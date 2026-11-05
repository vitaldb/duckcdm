"""App store (equivalent to WebAPI's 'webapi' schema): concept sets, cohort definitions, generation history. A single DuckDB file.

Every change is noted in `changed` as (kind, id) — kind conceptset, cohort, or an analysis kind (fa, cc, pw, ir) —
so a caller can copy whole entities elsewhere (export_entity / import_entity; duckcdm.webapi.drive keeps them in
the viewer's drive). Exported entities carry no small counts: generation counts are masked the way the API shows them.
"""
import json
import threading
import time

import duckdb

from . import cells

DDL = """
CREATE SEQUENCE IF NOT EXISTS seq_concept_set START 1;
CREATE SEQUENCE IF NOT EXISTS seq_cohort START 1;
CREATE SEQUENCE IF NOT EXISTS seq_job START 1;
CREATE TABLE IF NOT EXISTS concept_set (
  id INTEGER PRIMARY KEY, name VARCHAR, description VARCHAR,
  created_by VARCHAR, created_date BIGINT, modified_by VARCHAR, modified_date BIGINT);
CREATE TABLE IF NOT EXISTS concept_set_item (
  concept_set_id INTEGER, concept_id BIGINT, is_excluded INTEGER, include_descendants INTEGER, include_mapped INTEGER,
  ord INTEGER);
CREATE TABLE IF NOT EXISTS cohort_definition (
  id INTEGER PRIMARY KEY, name VARCHAR, description VARCHAR, expression_type VARCHAR, expression VARCHAR,
  created_by VARCHAR, created_date BIGINT, modified_by VARCHAR, modified_date BIGINT);
CREATE TABLE IF NOT EXISTS cohort_generation_info (
  cohort_definition_id INTEGER, source_id INTEGER, start_time BIGINT, execution_duration INTEGER, status VARCHAR,
  is_valid BOOLEAN, is_canceled BOOLEAN, fail_message VARCHAR, person_count BIGINT, record_count BIGINT,
  report VARCHAR, PRIMARY KEY (cohort_definition_id, source_id));
ALTER TABLE cohort_generation_info ADD COLUMN IF NOT EXISTS report VARCHAR;
CREATE TABLE IF NOT EXISTS job_execution (
  execution_id INTEGER PRIMARY KEY, job_name VARCHAR, status VARCHAR, start_date BIGINT, end_date BIGINT,
  exit_status VARCHAR, parameters VARCHAR);
CREATE TABLE IF NOT EXISTS analysis (
  kind VARCHAR, id INTEGER, name VARCHAR, description VARCHAR, design VARCHAR,
  created_by VARCHAR, created_date BIGINT, modified_by VARCHAR, modified_date BIGINT, PRIMARY KEY (kind, id));
CREATE TABLE IF NOT EXISTS analysis_run (
  id INTEGER PRIMARY KEY, kind VARCHAR, analysis_id INTEGER, source_id INTEGER, source_key VARCHAR, status VARCHAR,
  start_time BIGINT, end_time BIGINT, message VARCHAR, design VARCHAR, result VARCHAR);
"""


def now_ms():
    return int(time.time() * 1000)


class Store:
    def __init__(self, path, user='admin'):
        self.con = duckdb.connect(path)
        self.lock = threading.RLock()
        self.user = {'id': 1, 'login': user, 'name': user}
        self.changed = set()
        for stmt in DDL.strip().split(';'):
            if stmt.strip():
                self.con.execute(stmt)

    def _rows(self, sql, params=()):
        with self.lock:
            cur = self.con.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

    def _exec(self, sql, params=()):
        with self.lock:
            self.con.execute(sql, params)

    _SEQ_TABLE = {'seq_concept_set': ('concept_set', 'id'), 'seq_cohort': ('cohort_definition', 'id'),
                  'seq_job': ('job_execution', 'execution_id'), 'seq_run': ('analysis_run', 'id')}

    def _next(self, seq):
        # max+1 instead of a sequence: ids never go backwards even if the process dies abnormally
        table, col = self._SEQ_TABLE[seq]
        with self.lock:
            return self.con.execute(f'SELECT coalesce(max({col}), 0) + 1 FROM {table}').fetchone()[0]

    def _common(self, r):
        # the UI zod schema is optional, not nullable — missing values must omit the key
        d = {'createdBy': {'id': 1, 'login': r['created_by'], 'name': r['created_by']},
             'createdDate': r['created_date'], 'tags': [], 'hasWriteAccess': True, 'hasReadAccess': True,
             'writeAccess': True, 'readAccess': True}
        if r['modified_by']:
            d['modifiedBy'] = {'id': 1, 'login': r['modified_by'], 'name': r['modified_by']}
            d['modifiedDate'] = r['modified_date']
        return d

    # ---- concept sets
    def list_concept_sets(self):
        return [dict(id=r['id'], name=r['name'], description=r['description'], **self._common(r))
                for r in self._rows('SELECT * FROM concept_set ORDER BY id')]

    def get_concept_set(self, cid):
        rows = self._rows('SELECT * FROM concept_set WHERE id = ?', [cid])
        if not rows:
            return None
        r = rows[0]
        return dict(id=r['id'], name=r['name'], description=r['description'], **self._common(r))

    def create_concept_set(self, name, description):
        cid = self._next('seq_concept_set')
        t = now_ms()
        self._exec('INSERT INTO concept_set VALUES (?,?,?,?,?,?,?)',
                   [cid, name, description, self.user['login'], t, None, None])
        self.changed.add(('conceptset', cid))
        return self.get_concept_set(cid)

    def update_concept_set(self, cid, name, description):
        self._exec('UPDATE concept_set SET name = ?, description = ?, modified_by = ?, modified_date = ? WHERE id = ?',
                   [name, description, self.user['login'], now_ms(), cid])
        self.changed.add(('conceptset', cid))
        return self.get_concept_set(cid)

    def delete_concept_set(self, cid):
        self._exec('DELETE FROM concept_set_item WHERE concept_set_id = ?', [cid])
        self._exec('DELETE FROM concept_set WHERE id = ?', [cid])
        self.changed.add(('conceptset', cid))

    def get_items(self, cid):
        return [{'id': i, 'conceptSetId': cid, 'conceptId': r['concept_id'], 'isExcluded': r['is_excluded'],
                 'includeDescendants': r['include_descendants'], 'includeMapped': r['include_mapped']}
                for i, r in enumerate(self._rows(
                    'SELECT * FROM concept_set_item WHERE concept_set_id = ? ORDER BY ord', [cid]), 1)]

    def set_items(self, cid, items):
        with self.lock:
            self._exec('DELETE FROM concept_set_item WHERE concept_set_id = ?', [cid])
            for i, it in enumerate(items):
                self._exec('INSERT INTO concept_set_item VALUES (?,?,?,?,?,?)',
                           [cid, int(it['conceptId']), int(bool(it.get('isExcluded'))),
                            int(bool(it.get('includeDescendants'))), int(bool(it.get('includeMapped'))), i])
            self._exec('UPDATE concept_set SET modified_by = ?, modified_date = ? WHERE id = ?',
                       [self.user['login'], now_ms(), cid])
            self.changed.add(('conceptset', cid))

    # ---- cohort definitions
    def list_cohorts(self):
        return [dict(id=r['id'], name=r['name'], description=r['description'], expressionType=r['expression_type'],
                     **self._common(r))
                for r in self._rows('SELECT * FROM cohort_definition ORDER BY id')]

    def get_cohort(self, cid):
        rows = self._rows('SELECT * FROM cohort_definition WHERE id = ?', [cid])
        if not rows:
            return None
        r = rows[0]
        return dict(id=r['id'], name=r['name'], description=r['description'], expressionType=r['expression_type'],
                    expression=r['expression'], **self._common(r))

    def create_cohort(self, name, description, expression_type, expression_json):
        cid = self._next('seq_cohort')
        self._exec('INSERT INTO cohort_definition VALUES (?,?,?,?,?,?,?,?,?)',
                   [cid, name, description, expression_type or 'SIMPLE_EXPRESSION', expression_json,
                    self.user['login'], now_ms(), None, None])
        self.changed.add(('cohort', cid))
        return self.get_cohort(cid)

    def update_cohort(self, cid, name, description, expression_type, expression_json):
        self._exec('UPDATE cohort_definition SET name=?, description=?, expression_type=?, expression=?, '
                   'modified_by=?, modified_date=? WHERE id=?',
                   [name, description, expression_type or 'SIMPLE_EXPRESSION', expression_json, self.user['login'],
                    now_ms(), cid])
        self.changed.add(('cohort', cid))
        return self.get_cohort(cid)

    def delete_cohort(self, cid):
        self._exec('DELETE FROM cohort_generation_info WHERE cohort_definition_id = ?', [cid])
        self._exec('DELETE FROM cohort_definition WHERE id = ?', [cid])
        self.changed.add(('cohort', cid))

    # ---- generation history
    def set_generation(self, cid, source_id, **fields):
        with self.lock:
            rows = self._rows('SELECT * FROM cohort_generation_info WHERE cohort_definition_id=? AND source_id=?',
                              [cid, source_id])
            cur = rows[0] if rows else {'cohort_definition_id': cid, 'source_id': source_id, 'start_time': now_ms(),
                                        'execution_duration': None, 'status': 'PENDING', 'is_valid': False,
                                        'is_canceled': False, 'fail_message': None, 'person_count': None,
                                        'record_count': None, 'report': None}
            cur.update(fields)
            self._exec('DELETE FROM cohort_generation_info WHERE cohort_definition_id=? AND source_id=?',
                       [cid, source_id])
            self._exec('INSERT INTO cohort_generation_info VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                       [cid, source_id, cur['start_time'], cur['execution_duration'], cur['status'], cur['is_valid'],
                        cur['is_canceled'], cur['fail_message'], cur['person_count'], cur['record_count'],
                        cur['report']])
            self.changed.add(('cohort', cid))

    def generation_report(self, cid, source_id, mode):
        """The inclusion report kept with the generation (already masked), or None."""
        rows = self._rows('SELECT report FROM cohort_generation_info WHERE cohort_definition_id=? AND source_id=?',
                          [cid, source_id])
        rep = json.loads(rows[0]['report']) if rows and rows[0]['report'] else {}
        return rep.get(str(mode))

    def generation_info(self, cid):
        return [{'id': {'cohortDefinitionId': r['cohort_definition_id'], 'sourceId': r['source_id']},
                 'startTime': r['start_time'], 'executionDuration': r['execution_duration'], 'status': r['status'],
                 'isValid': r['is_valid'], 'isCanceled': r['is_canceled'], 'failMessage': r['fail_message'],
                 'personCount': r['person_count'], 'recordCount': r['record_count'], 'createdBy': self.user}
                for r in self._rows('SELECT * FROM cohort_generation_info WHERE cohort_definition_id=?', [cid])]

    # ---- analyses (characterizations, pathways, incidence rates, custom feature analyses): the design is JSON
    def list_analyses(self, kind):
        return self._rows('SELECT * FROM analysis WHERE kind = ? ORDER BY id', [kind])

    def get_analysis(self, kind, aid):
        rows = self._rows('SELECT * FROM analysis WHERE kind = ? AND id = ?', [kind, aid])
        return rows[0] if rows else None

    def save_analysis(self, kind, aid, name, description, design, first_id=1):
        """aid None creates one. Returns the id."""
        with self.lock:
            if aid is None:
                aid = self.con.execute('SELECT greatest(coalesce(max(id), 0) + 1, ?) FROM analysis WHERE kind = ?',
                                       [first_id, kind]).fetchone()[0]
                self._exec('INSERT INTO analysis VALUES (?,?,?,?,?,?,?,?,?)',
                           [kind, aid, name, description, design, self.user['login'], now_ms(), None, None])
            else:
                self._exec('UPDATE analysis SET name=?, description=?, design=?, modified_by=?, modified_date=? '
                           'WHERE kind=? AND id=?', [name, description, design, self.user['login'], now_ms(), kind, aid])
            self.changed.add((kind, aid))
            return aid

    def delete_analysis(self, kind, aid):
        self._exec('DELETE FROM analysis_run WHERE kind = ? AND analysis_id = ?', [kind, aid])
        self._exec('DELETE FROM analysis WHERE kind = ? AND id = ?', [kind, aid])
        self.changed.add((kind, aid))

    def start_run(self, kind, aid, source, design):
        rid = self._next('seq_run')
        self._exec('INSERT INTO analysis_run VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                   [rid, kind, aid, source.source_id, source.key, 'RUNNING', now_ms(), None, None, design, None])
        self.changed.add((kind, aid))
        return rid

    def finish_run(self, rid, status, message=None, result=None):
        self._exec('UPDATE analysis_run SET status=?, end_time=?, message=?, result=? WHERE id=?',
                   [status, now_ms(), message, result, rid])
        for r in self._rows('SELECT kind, analysis_id FROM analysis_run WHERE id = ?', [rid]):
            self.changed.add((r['kind'], r['analysis_id']))

    def runs(self, kind, aid=None, rid=None):
        sql, p = 'SELECT * FROM analysis_run WHERE kind = ?', [kind]
        if aid is not None:
            sql, p = sql + ' AND analysis_id = ?', p + [aid]
        if rid is not None:
            sql, p = sql + ' AND id = ?', p + [rid]
        return self._rows(sql + ' ORDER BY id DESC', p)

    def delete_runs(self, kind, aid, source_id):
        self._exec('DELETE FROM analysis_run WHERE kind = ? AND analysis_id = ? AND source_id = ?', [kind, aid, source_id])
        self.changed.add((kind, aid))

    # ---- whole entities (for copies kept outside the store)
    def export_entity(self, kind, eid):
        """The entity as a JSON-able dict, or None if it does not exist (any more)."""
        if kind == 'conceptset':
            rows = self._rows('SELECT * FROM concept_set WHERE id = ?', [eid])
            items = self._rows('SELECT * FROM concept_set_item WHERE concept_set_id = ? ORDER BY ord', [eid])
            return rows and {'v': 1, 'kind': kind, 'row': rows[0], 'items': items} or None
        if kind == 'cohort':
            rows = self._rows('SELECT * FROM cohort_definition WHERE id = ?', [eid])
            if not rows:
                return None
            gens = [dict(g, person_count=cells.mask(g['person_count']), record_count=cells.mask(g['record_count']))
                    for g in self._rows('SELECT * FROM cohort_generation_info WHERE cohort_definition_id = ?', [eid])]
            row = dict(rows[0])
            try:
                row['expression'] = json.loads(row['expression'])      # readable in the file
            except (TypeError, ValueError):
                pass
            return {'v': 1, 'kind': kind, 'row': row, 'generations': gens}
        rows = self._rows('SELECT * FROM analysis WHERE kind = ? AND id = ?', [kind, eid])
        runs = self._rows('SELECT * FROM analysis_run WHERE kind = ? AND analysis_id = ? ORDER BY id', [kind, eid])
        return rows and {'v': 1, 'kind': kind, 'row': rows[0], 'runs': runs} or None

    def import_entity(self, doc):
        """Put back an exported entity (replacing one with the same id). Work that was running when it was saved
        cannot finish any more: it comes back FAILED."""
        kind, row = doc['kind'], dict(doc['row'])
        stopped = 'interrupted (the app restarted)'
        with self.lock:
            if kind == 'conceptset':
                self._exec('DELETE FROM concept_set_item WHERE concept_set_id = ?', [row['id']])
                self._exec('DELETE FROM concept_set WHERE id = ?', [row['id']])
                self._insert('concept_set', row)
                for it in doc.get('items') or []:
                    self._insert('concept_set_item', it)
            elif kind == 'cohort':
                if not isinstance(row.get('expression'), str):
                    row['expression'] = json.dumps(row.get('expression'))
                self._exec('DELETE FROM cohort_generation_info WHERE cohort_definition_id = ?', [row['id']])
                self._exec('DELETE FROM cohort_definition WHERE id = ?', [row['id']])
                self._insert('cohort_definition', row)
                for g in doc.get('generations') or []:
                    if g.get('status') in ('PENDING', 'RUNNING'):
                        g = dict(g, status='FAILED', is_valid=False, fail_message=stopped)
                    self._insert('cohort_generation_info', g)
            else:
                self._exec('DELETE FROM analysis_run WHERE kind = ? AND analysis_id = ?', [kind, row['id']])
                self._exec('DELETE FROM analysis WHERE kind = ? AND id = ?', [kind, row['id']])
                self._insert('analysis', row)
                for r in doc.get('runs') or []:
                    if r.get('status') in ('RUNNING', 'STARTED', 'PENDING'):
                        r = dict(r, status='FAILED', message=stopped, end_time=r.get('end_time') or now_ms())
                    self._insert('analysis_run', r)

    def _insert(self, table, row):
        with self.lock:
            cols = [c[0] for c in self.con.execute(f'DESCRIBE {table}').fetchall()]
            self._exec(f'INSERT INTO {table} ({", ".join(cols)}) VALUES ({", ".join("?" * len(cols))})',
                       [row.get(c) for c in cols])

    # ---- jobs
    def start_job(self, job_name, parameters):
        jid = self._next('seq_job')
        self._exec('INSERT INTO job_execution VALUES (?,?,?,?,?,?,?)',
                   [jid, job_name, 'STARTED', now_ms(), None, None, json.dumps(parameters)])
        return jid

    def finish_job(self, jid, status, exit_status=None):
        self._exec('UPDATE job_execution SET status=?, end_date=?, exit_status=? WHERE execution_id=?',
                   [status, now_ms(), exit_status, jid])

    def job(self, jid):
        rows = self._rows('SELECT * FROM job_execution WHERE execution_id=?', [jid])
        return self._job_dict(rows[0]) if rows else None

    def jobs(self):
        return [self._job_dict(r) for r in self._rows('SELECT * FROM job_execution ORDER BY execution_id DESC')]

    def _job_dict(self, r):
        return {'executionId': r['execution_id'], 'status': r['status'], 'startDate': r['start_date'],
                'endDate': r['end_date'], 'exitStatus': r['exit_status'],
                'jobInstance': {'instanceId': r['execution_id'], 'name': r['job_name']},
                'jobParameters': json.loads(r['parameters'] or '{}'), 'ownerType': 'user'}
