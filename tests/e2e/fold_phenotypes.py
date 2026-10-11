"""Folded single-SELECT cohort generation == original multi-statement script, on all PhenotypeLibrary cohorts.

python3 fold_phenotypes.py <cdm.duckdb (a scratch copy)> <cohorts dir> [count]
For each cohort: run the original script (temp tables, inserts) on a scratch copy of the results tables,
run the folded query (one SELECT) read-only, and compare the cohort counts and the four stats tables.
"""
import glob, json, os, sys, threading, time

import duckdb

from duckcdm.circe import build_cohort_query
from duckcdm.fold import fold
from duckcdm.sqlrender import render, split_sql, translate

STATS = ['res.cohort_inclusion_result', 'res.cohort_inclusion_stats', 'res.cohort_summary_stats', 'res.cohort_censor_stats']
DDL = {
    'res.cohort': [('cohort_definition_id', 'INTEGER'), ('subject_id', 'BIGINT'), ('cohort_start_date', 'DATE'), ('cohort_end_date', 'DATE')],
    'res.cohort_inclusion_result': [('cohort_definition_id', 'INTEGER'), ('inclusion_rule_mask', 'BIGINT'), ('person_count', 'BIGINT'), ('mode_id', 'INTEGER')],
    'res.cohort_inclusion_stats': [('cohort_definition_id', 'INTEGER'), ('rule_sequence', 'INTEGER'), ('person_count', 'BIGINT'),
                                   ('gain_count', 'BIGINT'), ('person_total', 'BIGINT'), ('mode_id', 'INTEGER')],
    'res.cohort_summary_stats': [('cohort_definition_id', 'INTEGER'), ('base_count', 'BIGINT'), ('final_count', 'BIGINT'), ('mode_id', 'INTEGER')],
    'res.cohort_censor_stats': [('cohort_definition_id', 'INTEGER'), ('lost_count', 'BIGINT')],
}


def norm(rows):
    return sorted(json.dumps({k: (int(v) if isinstance(v, (int, float)) and v == int(v) else v) for k, v in r.items()}, sort_keys=True)
                  for r in rows)


def main():
    db, cdir = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    files = sorted(glob.glob(os.path.join(cdir, '*.json')), key=lambda f: int(os.path.basename(f).split('.')[0]))[:limit]
    ok, diff, err = 0, [], []
    t0 = time.time()
    for f in files:
        cid = int(os.path.basename(f).split('.')[0])
        sql = translate(render(build_cohort_query(open(f, encoding='utf-8').read(), cdm_schema='main', vocabulary_schema='main',
                                                  result_schema='res', target_table='res.cohort', cohort_id=cid, generate_stats=True)), 'duckdb')
        stmts = [s for s in split_sql(sql) if s.strip()]
        # original
        con = duckdb.connect(db)          # a scratch copy: the original script writes res.* tables
        con.execute('CREATE SCHEMA IF NOT EXISTS res')
        for t, cols in DDL.items():
            con.execute(f'CREATE OR REPLACE TABLE {t} (' + ', '.join(f'{c} {ty}' for c, ty in cols) + ')')
        timer = threading.Timer(60, con.interrupt); timer.start()
        try:
            for s in stmts:
                con.execute(s)
            want = {'res.cohort': {'rows': con.execute('select count(*) from res.cohort').fetchone()[0],
                                   'persons': con.execute('select count(distinct subject_id) from res.cohort').fetchone()[0]}}
            for t in STATS:
                cur = con.execute(f'select * from {t}')
                names = [d[0] for d in cur.description]
                want[t] = norm([dict(zip(names, r)) for r in cur.fetchall()])
        except Exception as e:
            err.append((cid, 'orig', str(e)[:150])); timer.cancel(); con.close(); continue
        timer.cancel(); con.close()
        # folded
        con = duckdb.connect(db)
        for t in DDL:
            con.execute(f'DELETE FROM {t}')      # the folded query must not depend on what the original wrote
        timer = threading.Timer(60, con.interrupt); timer.start()
        try:
            q = fold(stmts, ['res.cohort'] + STATS, known=DDL, count_only=('res.cohort',))
            got = {}
            for name, data in con.execute(q).fetchall():
                d = json.loads(data)
                got['res.' + name] = d if name == 'cohort' else norm(d)
        except Exception as e:
            err.append((cid, 'fold', str(e)[:200])); timer.cancel(); con.close(); continue
        timer.cancel(); con.close()
        if got == want:
            ok += 1
        else:
            diff.append((cid, {k: (want[k], got.get(k)) for k in want if want[k] != got.get(k)}))
    print(f'ok {ok} / {len(files)}  diff {len(diff)}  error {len(err)}  {time.time() - t0:.0f}s')
    for x in diff[:10]:
        print('DIFF', str(x)[:400])
    for x in err[:15]:
        print('ERR', x)


if __name__ == '__main__':
    main()
