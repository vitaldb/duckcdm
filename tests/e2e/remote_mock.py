"""RemoteSource against a mock of the Data Foundation query API, compared with the local Source.

python3 remote_mock.py <eunomia with Achilles results .duckdb> <a second copy of it> <cohorts dir> [count]

The mock behaves like the API where it matters: one SELECT per request, no parameters, viewer identity
headers required, at most 50,000 rows, and (MOCK_REQUIRE_YEAR=1) partitioned tables refused unless read as
(SELECT * FROM t WHERE year >= 0). It serves dataset `snuh_cdm` = the CDM tables (+ a constant year column on
partitioned tables) and the Achilles tables of the given database.
"""
import glob, json, os, re, socket, sys, threading, time

import duckdb
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from duckcdm.circe import build_cohort_query
from duckcdm.sqlrender import render
from duckcdm.webapi import remote as R
from duckcdm.webapi.reports import Reports
from duckcdm.webapi.sources import Source

FLAT = set(R.FLAT_DEFAULT.split(','))
ACH = ('achilles_results', 'achilles_results_dist', 'achilles_result_concept_count', 'achilles_analysis', 'concept_hierarchy')


def mock_app(db):
    con = duckdb.connect()
    con.execute(f"ATTACH '{db}' AS e (READ_ONLY)")
    con.execute('CREATE SCHEMA snuh_cdm')
    tabs = [r[0] for r in con.execute("select table_name from duckdb_tables() where database_name='e' and schema_name='main'").fetchall()]
    for t in tabs:
        con.execute(f'CREATE VIEW snuh_cdm.{t} AS SELECT *' + ('' if t in FLAT else ', 9999 AS year') + f' FROM e.main.{t}')
    for t in ACH:
        con.execute(f'CREATE VIEW snuh_cdm.{t} AS SELECT *, 9999 AS year FROM e.results.{t}')
    lock = threading.Lock()
    app = FastAPI()
    need_year = os.environ.get('MOCK_REQUIRE_YEAR', '1') == '1'

    @app.post('/v1/query')
    async def query(req: Request):
        if not req.headers.get('user-id'):
            return JSONResponse({'detail': 'no identity'}, 403)
        b = await req.json()
        sql = b['sql']
        if ';' in sql.strip().rstrip(';').strip() or not re.match(r'\s*\(*\s*(select|with)\b', sql, re.I):
            return {'state': 'failed', 'error': 'safety: single SELECT only'}
        if need_year:
            for m in re.finditer(r'(?i)snuh_cdm\.(\w+)', sql):
                t = m.group(1).lower()
                if t not in FLAT and not re.match(r'\s+WHERE year >= 0\)', sql[m.end():]):
                    return {'state': 'failed', 'error': f'safety: {t} requires a filter on one of: year'}
        with lock:
            try:
                cur = con.cursor().execute(sql)
                cols = [d[0] for d in cur.description]
                rows = cur.fetchmany(int(b.get('limit') or 1000) + 1)
            except Exception as e:
                return {'state': 'failed', 'error': str(e)[:300]}
        trunc = len(rows) > int(b.get('limit') or 1000)
        data = [dict(zip(cols, [v if isinstance(v, (int, float, str, type(None))) else str(v) for v in r])) for r in rows[:int(b.get('limit') or 1000)]]
        return {'state': 'succeeded', 'columns': [{'name': c} for c in cols], 'data': data, 'truncated': trunc}
    return app


def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


def main():
    db, db2, cdir = sys.argv[1], sys.argv[2], sys.argv[3]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 50
    port = free_port()
    srv = uvicorn.Server(uvicorn.Config(mock_app(db), host='127.0.0.1', port=port, log_level='warning'))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.1)
    rs = R.RemoteSource(1, 'R', 'remote', url=f'http://127.0.0.1:{port}/v1/query')
    R.identity.set({'user_id': 'tester', 'authorities': ''})
    ls = Source(2, 'L', 'local', db2, 'main', 'main', 'res')
    ls_rep = Source(3, 'L2', 'local', db2, 'main', 'main', 'results', read_only=False) if False else None
    # data-source report and a vocabulary-style query, both sides
    rl = Reports(Source(3, 'L2', 'local', db2.replace('.duckdb', '_rep.duckdb'), 'main', 'main', 'results')).dashboard()
    rr = Reports(rs).dashboard()
    print('dashboard same:', json.dumps(rl, sort_keys=True, default=str) == json.dumps(rr, sort_keys=True, default=str))
    files = sorted(glob.glob(os.path.join(cdir, '*.json')), key=lambda f: int(os.path.basename(f).split('.')[0]))[:limit]
    ok, bad = 0, []
    t0 = time.time()
    for f in files:
        cid = int(os.path.basename(f).split('.')[0])
        expr = open(f, encoding='utf-8').read()
        want = got = None
        try:
            sql = build_cohort_query(expr, cdm_schema='main', vocabulary_schema='main', result_schema='res',
                                     target_table='res.cohort', cohort_id=cid, generate_stats=True)
            cur = ls.cursor()
            ls.execute_script(render(sql), cur)
            want = (cur.execute('select count(distinct subject_id), count(*) from res.cohort where cohort_definition_id=?', [cid]).fetchone(),
                    sorted(cur.execute('select rule_sequence, person_count, gain_count, person_total, mode_id from res.cohort_inclusion_stats where cohort_definition_id=?', [cid]).fetchall()),
                    sorted(cur.execute('select base_count, final_count, mode_id from res.cohort_summary_stats where cohort_definition_id=?', [cid]).fetchall()))
            sql = build_cohort_query(expr, cdm_schema='snuh_cdm', vocabulary_schema='snuh_cdm', result_schema='snuh_cdm',
                                     target_table='snuh_cdm.cohort', cohort_id=cid, generate_stats=True)
            rs.execute_script(render(sql))
            c = rs.con.cursor()
            got = (tuple(rs.generated_counts(cid)),
                   sorted(c.execute('select rule_sequence, person_count, gain_count, person_total, mode_id from snuh_cdm.cohort_inclusion_stats where cohort_definition_id=?', [cid]).fetchall()),
                   sorted(c.execute('select base_count, final_count, mode_id from snuh_cdm.cohort_summary_stats where cohort_definition_id=?', [cid]).fetchall()))
        except Exception as e:
            bad.append((cid, 'error', str(e)[:200])); continue
        if want == got:
            ok += 1
        else:
            bad.append((cid, want, got))
    print(f'cohorts ok {ok} / {len(files)}  {time.time() - t0:.0f}s')
    for x in bad[:10]:
        print('BAD', str(x)[:300])


if __name__ == '__main__':
    main()
