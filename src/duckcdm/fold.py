"""Fold a multi-statement DuckDB script (temp tables, INSERT, DELETE) into one read-only SELECT.

For engines that accept a single SELECT only (e.g. a query API in front of shared Parquet tables).
Every write becomes a new version of a common table expression, so each statement reads exactly the
rows the original script would have seen at that point:

    CREATE TEMP TABLE t (a int, b int)       -> t__1 AS (SELECT NULL::int a, NULL::int b WHERE false)
    INSERT INTO t (a, b) SELECT ...          -> t__2 AS (SELECT * FROM t__1 UNION ALL BY NAME SELECT ...)
    CREATE TEMP TABLE t AS SELECT ...        -> t__1 AS (SELECT ...)
    DELETE FROM t   /  TRUNCATE TABLE t      -> t__2 AS (SELECT * FROM t__1 WHERE false)
    DELETE FROM t WHERE <cond>               -> t__2 AS (SELECT * FROM t__1 WHERE NOT coalesce(<cond>, false))
    DROP TABLE / ANALYZE                     -> ignored

The result is one row per output table: (table_name without schema, json) where json is the list of that table's
final rows (or, for `count_only` tables, {"rows": n, "persons": distinct subject_id}).
"""
import re

_IDENT = r'[A-Za-z_][A-Za-z0-9_]*'
_NAME = rf'{_IDENT}(?:\.{_IDENT})?'


def _split_cols(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [c.strip() for c in out]


class Folder:
    def __init__(self, known=None, rewrite_source=None):
        """known: {table: [(column, type), ...]} for tables that exist before the script (result tables
        that start empty). rewrite_source(sql) is applied to every statement body (e.g. CDM table names)."""
        self.ver = {}            # lower name -> current version number
        self.cols = {}           # lower name -> [column, ...] (when known)
        self.ctes = []           # [(cte name, body)]
        self.empty = set()       # CTE names that are empty table definitions (never materialized —
                                 # DuckDB 1.5 loses materialized CTEs whose plan folds to empty)
        self.rewrite_source = rewrite_source or (lambda s: s)
        self.materialize = 'MATERIALIZED'   # or 'NOT MATERIALIZED' / '' (engine decides)
        for t, cols in (known or {}).items():
            self._define_empty(t, cols)

    # -- naming
    @staticmethod
    def _key(name):
        return name.lower()

    def _cte(self, key, v=None):
        return re.sub(r'\W', '_', key) + '__' + str(self.ver[key] if v is None else v)

    def _define(self, name, body, cols=None):
        k = self._key(name)
        self.ver[k] = self.ver.get(k, 0) + 1
        if cols is not None:
            self.cols[k] = cols
        self.ctes.append((self._cte(k), body))

    def _define_empty(self, name, cols):
        self._define(name, 'SELECT ' + ', '.join(f'CAST(NULL AS {ty}) AS {c}' for c, ty in cols) + ' WHERE false',
                     [c for c, _ in cols])
        self.empty.add(self._cte(self._key(name)))
        self.types = getattr(self, 'types', {}); self.types[self._key(name)] = dict(cols)

    def _refs(self, sql):
        """Replace references to folded tables by their current CTE."""
        if not self.ver:
            return sql
        names = sorted(self.ver, key=len, reverse=True)
        pat = re.compile(r'(?<![\w.])(' + '|'.join(re.escape(n) for n in names) + r')(?![\w])', re.I)
        return pat.sub(lambda m: self._cte(m.group(1).lower()), sql)

    # -- statements
    def add(self, stmt):
        s = stmt.strip().rstrip(';').strip()
        if not s:
            return
        low = s.lower()
        if re.match(r'(drop\s+table|analyze)\b', low):
            return
        m = re.match(rf'create\s+(?:temp(?:orary)?\s+)?table\s+(?:if\s+not\s+exists\s+)?({_NAME})\s+as\s+(.*)$', s, re.I | re.S)
        if m:
            self._define(m.group(1), self._refs(self.rewrite_source(m.group(2))))
            return
        m = re.match(rf'create\s+(?:temp(?:orary)?\s+)?table\s+(?:if\s+not\s+exists\s+)?({_NAME})\s*\((.*)\)\s*$', s, re.I | re.S)
        if m:
            cols = []
            for c in _split_cols(m.group(2)):
                parts = c.split()
                ty = re.sub(r'(?i)\s+not\s+null.*$|\s+null\s*$', '', ' '.join(parts[1:])) or 'VARCHAR'
                cols.append((parts[0], ty))
            self._define_empty(m.group(1), cols)
            return
        m = re.match(rf'insert\s+into\s+({_NAME})\s*(?:\(([^)]*)\))?\s*(.*)$', s, re.I | re.S)
        if m:
            name, collist, body = m.group(1), m.group(2), m.group(3)
            k = self._key(name)
            if k not in self.ver:
                raise ValueError(f'INSERT into unknown table {name}')
            body = self._refs(self.rewrite_source(body))
            cols = [c.strip() for c in collist.split(',')] if collist else self.cols.get(k)
            prev = self._cte(k)
            if cols:
                aliased = f'SELECT * FROM ({body}\n) AS _ins({", ".join(cols)})'
                tcols = self.cols.get(k) or cols
                sel = ', '.join(c if c.lower() in {x.lower() for x in cols} else f'NULL AS {c}' for c in tcols)
                if prev in self.empty:       # first rows into an empty table: no union with the empty definition
                    ty = getattr(self, 'types', {}).get(k, {})
                    sel = ', '.join((f'CAST({c} AS {ty[c]}) AS {c}' if c in ty else c) if c.lower() in {x.lower() for x in cols}
                                    else f'CAST(NULL AS {ty.get(c, "VARCHAR")}) AS {c}' for c in tcols)
                    new = f'SELECT {sel} FROM ({aliased}\n) AS _i'
                else:
                    new = f'SELECT * FROM {prev} UNION ALL SELECT {sel} FROM ({aliased}\n) AS _i'
            else:
                new = f'SELECT * FROM {prev} UNION ALL ({body}\n)'
            self._define(name, new)
            return
        m = re.match(rf'(?:delete\s+from|truncate\s+table)\s+({_NAME})\s*(?:where\s+(.*))?$', s, re.I | re.S)
        if m:
            k = self._key(m.group(1))
            if k not in self.ver:
                return               # deleting from a table we never saw (pre-existing results) — nothing to keep
            prev = self._cte(k)
            cond = m.group(2)
            if prev in self.empty:
                return               # deleting from an empty table changes nothing
            body = f'SELECT * FROM {prev} WHERE ' + (f'NOT coalesce(({self._refs(cond)}\n), false)' if cond else 'false')
            self._define(m.group(1), body)
            if not cond:
                self.empty.add(self._cte(k))
            return
        raise ValueError('cannot fold statement: ' + s[:120])

    def query(self, outputs, count_only=()):
        """outputs: table names to return. count_only: tables returned as {"rows", "persons"}."""
        sel = []
        for t in outputs:
            k = self._key(t)
            label = t.split('.')[-1]          # no schema in the label: some query gateways scan literals for table names
            if k not in self.ver:
                sel.append(f"SELECT '{label}' AS table_name, '[]' AS data")
            elif t in count_only or k in {c.lower() for c in count_only}:
                sel.append(f"SELECT '{label}' AS table_name, CAST(json_object('rows', count(*), 'persons', count(DISTINCT subject_id)) AS VARCHAR) AS data FROM {self._cte(k)}")
            else:
                sel.append(f"SELECT '{label}' AS table_name, CAST(coalesce(to_json(list(_r)), '[]') AS VARCHAR) AS data FROM {self._cte(k)} AS _r")
        tail = '\nUNION ALL\n'.join(sel)
        # keep only the CTEs the outputs depend on (cleanup DELETEs at the end leave unreferenced versions;
        # DuckDB 1.5 fails on some unreferenced MATERIALIZED CTEs, and they would cost time anyway)
        names = [n for n, _ in self.ctes]
        word = re.compile(r'\b(' + '|'.join(map(re.escape, names)) + r')\b') if names else None
        need, todo = set(), set(word.findall(tail)) if word else set()
        body = dict(self.ctes)
        while todo:
            n = todo.pop()
            if n not in need:
                need.add(n); todo |= set(word.findall(body[n])) - need
        withs = ',\n'.join(f'{n} AS {"NOT MATERIALIZED" if n in self.empty else self.materialize} (\n{b}\n)'
                            for n, b in self.ctes if n in need)
        return ('WITH ' + withs + '\n' if withs else '') + tail


def fold(statements, outputs, known=None, count_only=(), rewrite_source=None, materialize='MATERIALIZED'):
    f = Folder(known, rewrite_source)
    f.materialize = materialize
    for s in statements:
        f.add(s)
    return f.query(outputs, count_only)
