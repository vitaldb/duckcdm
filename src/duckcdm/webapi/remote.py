"""Remote source: the CDM lives behind a query API that runs one SELECT at a time (snuh.ai Data Foundation
"Tables", DuckDB engine) instead of a local DuckDB file.

A layer on top of the local Source — nothing else changes:
- Reads (vocabulary, data-source reports, concept counts) go to the API as they are.
- Cohort generation: the Circe script (temp tables, inserts) is folded into one SELECT (duckcdm.fold) and
  run remotely; the cohort counts and the inclusion statistics come back as JSON. The cohort result tables
  (cohort_*) live in a local in-memory DuckDB — they are recomputed by generating again.
- Optional year filter (DF_REQUIRE_YEAR=1): the API currently refuses partitioned tables without a filter on
  `year`, so every reference to such a table becomes (SELECT * FROM t WHERE year >= 0). Turn it off when the
  platform no longer requires it — no code change.
- The viewer's identity is passed through (the gateway's user token X-App-User-Token, else User-ID headers),
  so the API applies that user's permissions and audit.

Configuration (environment):
  DF_URL            query endpoint (default: in-cluster Data Foundation)
  DF_DATASET        dataset holding CDM, vocabulary and Achilles tables (default snuh_cdm)
  DF_REQUIRE_YEAR   1 = add the year filter (default 1)
  DF_FLAT_TABLES    comma-separated tables without a year partition (no filter added)
  DF_PURPOSE        purpose sent with each query (default RESEARCH)
  DF_REQUEST_TEXT   default request_text (what is looked up and why); cohort generation names the cohort
  DF_TIMEOUT_MS     per-query timeout (default 600000)
  SOURCE_DIALECT_LABEL  dialect ATLAS shows for the source (display only)
"""
import contextvars
import datetime
import json
import os
import re
import threading
import urllib.error
import urllib.request

import duckdb

from ..fold import fold
from ..sqlrender import render, split_sql, translate
from .sources import Source

DF_URL = os.environ.get('DF_URL', 'http://datafoundation.platform.svc.cluster.local:8787/datafoundation/v1/query')
FLAT_DEFAULT = ('care_site,concept_class,death,domain,location,provider,relationship,source_to_concept_map,vocabulary')
LOCAL_TABLES = ('cohort', 'cohort_inclusion', 'cohort_inclusion_result', 'cohort_inclusion_stats',
                'cohort_summary_stats', 'cohort_censor_stats')
STATS = ('cohort_inclusion_result', 'cohort_inclusion_stats', 'cohort_summary_stats', 'cohort_censor_stats')

identity = contextvars.ContextVar('duckcdm_identity', default=None)   # {'user_id': .., 'authorities': ..}
# what is being looked up and why — required by the API for research queries (request_text)
purpose_text = contextvars.ContextVar('duckcdm_request_text', default=None)
DEFAULT_TEXT = os.environ.get('DF_REQUEST_TEXT', 'CDM ATLAS(OHDSI) — OMOP CDM 개념 검색·데이터 소스 보고서·코호트 정의 실행')


class RemoteError(Exception):
    def __init__(self, msg):
        # messages reach the ATLAS screen (generation failure); they need not name the engine
        super().__init__(re.sub(r'(?i)duck\s*db', 'SQL engine', str(msg)))


_DATE = re.compile(r'\d{4}-\d{2}-\d{2}$')
_TS = re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?$')


def _value(v):
    """JSON gives dates as text; the WebAPI code expects what DuckDB returns locally (date / datetime)."""
    if isinstance(v, str) and len(v) >= 10 and v[4] == '-':
        try:
            if _DATE.match(v):
                return datetime.date.fromisoformat(v)
            if _TS.match(v):
                return datetime.datetime.fromisoformat(v.replace('T', ' '))
        except ValueError:
            pass
    return v


def install_identity(app):
    """ASGI middleware: remember the viewer's gateway identity for the remote queries of this request."""
    @app.middleware('http')
    async def _identity(request, call_next):
        h = request.headers
        uid = h.get('x-auth-user-id') or h.get('user-id') or h.get('x-auth-subject')
        # 2026-10-12~ the API takes the gateway's short-lived user token (X-App-User-Token, ~5 min) instead of bare User-ID
        tok = identity.set({'user_id': uid, 'authorities': h.get('x-auth-authorities') or '',
                            'token': h.get('x-app-user-token')} if uid else None)
        try:
            return await call_next(request)
        finally:
            identity.reset(tok)


def year_filter(sql, dataset, flat):
    """dataset.t -> (SELECT * FROM dataset.t WHERE year >= 0) for partitioned tables."""
    pat = re.compile(rf'(?<![\w.]){re.escape(dataset)}\.(\w+)(?![\w.])', re.I)

    def sub(m):
        t = m.group(1)
        if t.lower() in flat or t.lower() in LOCAL_TABLES:
            return m.group(0)
        return f'(SELECT * FROM {dataset}.{t} WHERE year >= 0)'
    return pat.sub(sub, sql)


def literal(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def inline(sql, params):
    """Replace ? placeholders (outside string literals) with SQL literals — the API takes no parameters."""
    if not params:
        return sql
    out, it, i, n = [], iter(params), 0, len(sql)
    while i < n:
        ch = sql[i]
        if ch == "'":
            j = i + 1
            while j < n and not (sql[j] == "'" and (j + 1 >= n or sql[j + 1] != "'")):
                j += 2 if sql[j] == "'" else 1
            out.append(sql[i:j + 1]); i = j + 1
        elif ch == '?':
            out.append(literal(next(it))); i += 1
        else:
            out.append(ch); i += 1
    return ''.join(out)


class RemoteSource(Source):
    def __init__(self, source_id, key, name, dataset=None, url=None):
        # no local CDM file: an in-memory DuckDB holds only the cohort result tables
        self.dataset = dataset or os.environ.get('DF_DATASET', 'snuh_cdm')
        self.url = url or DF_URL
        self.require_year = os.environ.get('DF_REQUIRE_YEAR', '1') == '1'
        self.flat = {t.strip().lower() for t in os.environ.get('DF_FLAT_TABLES', FLAT_DEFAULT).split(',') if t.strip()}
        self.purpose = os.environ.get('DF_PURPOSE', 'RESEARCH')
        self.timeout_ms = int(os.environ.get('DF_TIMEOUT_MS', '600000'))
        self.counts = {}            # cohort_definition_id -> (persons, records) of the last remote generation
        super().__init__(source_id, key, name, ':memory:', self.dataset, self.dataset, self.dataset)
        self.path = self.url

    # -- remote calls
    def remote(self, sql):
        """Run one SELECT remotely as the current viewer. Returns (columns, rows)."""
        who = identity.get()
        if not who:
            raise RemoteError('no viewer identity — remote queries run with the gateway user headers')
        sql = sql.strip().rstrip(';').strip()      # one statement, no terminator
        if sql.startswith('('):                    # "(SELECT .. UNION ..) ORDER BY .." — the API's parser rejects it
            sql = f'SELECT * FROM (\n{sql}\n) AS _q'
        if self.require_year:
            sql = year_filter(sql, self.dataset, self.flat)
        body = {'sql': sql, 'limit': 50000, 'timeout_ms': self.timeout_ms, 'purpose': self.purpose,
                'request_text': purpose_text.get() or DEFAULT_TEXT}
        hdr = {'Content-Type': 'application/json'}
        if who.get('token'):
            hdr['X-App-User-Token'] = who['token']
        else:
            hdr.update({'User-ID': who['user_id'], 'User-Authorities': who['authorities']})
        req = urllib.request.Request(self.url, json.dumps(body).encode(), hdr)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_ms / 1000 + 60) as r:
                j = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise RemoteError(f'{e.code} {e.read().decode("utf-8", "replace")[:500]}')
        if j.get('state') != 'succeeded':
            raise RemoteError(f"{j.get('state')}: {j.get('error') or j.get('rationale') or j.get('decision')}")
        data = j.get('data') or []
        cols = [c['name'] if isinstance(c, dict) else c for c in (j.get('columns') or [])] or (list(data[0]) if data else [])
        return cols, [tuple(_value(r.get(c)) for c in cols) for r in data]

    def _is_local(self, sql):
        low = sql.lower()
        if re.match(r'\s*(insert|delete|create|drop|update|truncate|alter)\b', low):
            return True
        refs = re.findall(rf'{re.escape(self.dataset.lower())}\.(\w+)', low)
        return bool(refs) and all(t in LOCAL_TABLES for t in refs)

    # -- Source interface
    def cursor(self):
        return _Cursor(self)

    def query(self, sql, **params):
        duck = translate(render(sql, **params), self.dialect)
        parts = [s for s in split_sql(duck) if s.strip()]
        cur = self.cursor()
        for stmt in parts:
            cur.execute(stmt)
        return [d[0] for d in cur.description], cur.fetchall()

    def execute_script(self, sql, cur=None):
        """Cohort generation scripts are folded and run remotely; anything purely local runs locally."""
        stmts = [s for s in split_sql(translate(sql, self.dialect)) if s.strip()]
        cdm_ref = re.compile(rf'(?i)(?<![\w.]){re.escape(self.dataset)}\.(?!(?:{"|".join(LOCAL_TABLES)})\b)\w+')
        if not any(cdm_ref.search(s) for s in stmts):
            c = cur or self.cursor()
            for s in stmts:
                c.execute(s)
            return c
        return self._generate(stmts)

    def _generate(self, stmts):
        ds = self.dataset
        known = {}
        local = self.con.cursor()
        for t in ('cohort',) + STATS:
            known[f'{ds}.{t}'] = [(r[0], r[1]) for r in local.execute(f'DESCRIBE {ds}.{t}').fetchall()]
        outs = [f'{ds}.cohort'] + [f'{ds}.{t}' for t in STATS]
        ids = {int(x) for x in re.findall(rf'(?i)insert\s+into\s+{re.escape(ds)}\.cohort\s*\([^)]*\)\s*select\s+(\d+)\s+as\s+cohort_definition_id', '\n'.join(stmts))}
        cid = ids.pop() if len(ids) == 1 else None
        res = None
        for mat in ('MATERIALIZED', 'NOT MATERIALIZED'):   # DuckDB 1.5 can lose some materialized CTEs (INTERNAL error)
            q = fold(stmts, outs, known=known, count_only=(f'{ds}.cohort',), materialize=mat)
            try:
                res = dict(self.remote(q)[1]); break
            except RemoteError as e:
                if 'CTE definition' not in str(e) or mat != 'MATERIALIZED':
                    raise
        with self.lock:
            for t in STATS:
                rows = json.loads(res.get(t) or '[]')
                if cid is not None:
                    local.execute(f'DELETE FROM {ds}.{t} WHERE cohort_definition_id = ?', [cid])
                cols = [c for c, _ in known[f'{ds}.{t}']]
                for r in rows:
                    local.execute(f'INSERT INTO {ds}.{t} ({", ".join(cols)}) VALUES ({", ".join("?" * len(cols))})',
                                  [r.get(c) for c in cols])
        c = json.loads(res.get('cohort') or '{}')
        if cid is not None:
            self.counts[cid] = (c.get('persons', 0), c.get('rows', 0))
        return local

    def generated_counts(self, cid):
        return self.counts.get(cid, (0, 0))

    def info(self):
        d = super().info()
        label = os.environ.get('SOURCE_DIALECT_LABEL')   # what ATLAS shows as the source dialect (queries still run as duckdb)
        if label:
            d['sourceDialect'] = label
        return d

    def details(self):
        d = self.info()
        d.update({'connectionString': self.url + '#' + self.dataset, 'username': None, 'password': None,
                  'krbAuthMethod': 'password', 'krbAdminServer': None, 'keytabName': None})
        return d


class _Cursor:
    """DB-API-ish cursor that sends each statement where it belongs."""

    def __init__(self, src):
        self.s = src
        self.description, self._rows = None, []

    def execute(self, sql, params=None):
        s = self.s
        if 'information_schema' in sql.lower():
            # the API does not expose the catalog; the only caller asks whether Achilles results exist
            self.description, self._rows = [('n',)], [(1,)]
            return self
        if s._is_local(sql):
            c = s.con.cursor().execute(sql, params or [])
            self.description = c.description
            self._rows = c.fetchall() if c.description else []
            return self
        cols, rows = s.remote(inline(sql, params))
        self.description, self._rows = [(c,) for c in cols], rows
        return self

    def fetchall(self):
        r, self._rows = self._rows, []
        return r

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None
