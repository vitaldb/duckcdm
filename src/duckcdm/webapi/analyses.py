"""ATLAS Analysis: feature analyses, characterizations, cohort pathways and incidence rates (WebAPI paths and shapes).

Each run is one SELECT. The cohorts it needs are rebuilt from their definitions (Circe, into a temp table), the
analysis is added on top, and the script is folded (duckcdm.fold) — so a remote source runs it where the CDM is,
and only aggregates come back: features by cohort and stratum, pathway counts, incidence summaries.
Counts below SMALL_CELL_MIN leave the server as cells.MASK or not at all (feature rows and pathways are dropped;
so are distributions whose non-zero values come from fewer people — their mean would give the count away).

Not WebAPI's engine (FeatureExtraction, its pathway and IR SQL), and simpler where noted:
- Preset features are a fixed set (demographics, domain concepts in the usual windows, a few distributions).
  Custom SQL features (CUSTOM_FE) are refused — the app does not run SQL its users write.
- Counts are over cohort entries (one per person in most cohorts).
- Pathways: event cohort entries that start within the target entry; an event that starts within
  `combinationWindow` days of the previous one joins its step (a combination). Repeated steps collapse; without
  allowRepeats only the first occurrence of each step is kept. Steps beyond maxDepth are cut.
- Incidence: time at risk ends at the end of the observation period at most and is cut to the study window;
  target entries with an outcome entry starting before the time at risk are left out (they already had it);
  a case is a first outcome entry starting within the time at risk; its time at risk ends there.
"""
import contextvars
import json
import re
import threading
import time
import traceback

from fastapi import HTTPException, Request
from fastapi.responses import Response

from ..circe import build_cohort_query
from ..circe._builders import template
from ..circe._jutil import jreplace
from ..circe._model import ConceptSet, CriteriaGroup, DemographicCriteria, WindowedCriteria
from ..circe._query import CohortExpressionQueryBuilder
from ..fold import fold
from ..sqlrender import render, split_sql, translate
from . import cells
from .store import now_ms

_builder = CohortExpressionQueryBuilder()


class AnalysisError(Exception):
    pass


def _min_count():
    return max(cells.MIN, 1)


# ---- one run: Circe (OHDSI SQL) and DuckDB statements, folded into one SELECT ------------------------------------
class Script:
    def __init__(self, s):
        self.s, self.stmts, self.n = s, [], 0

    def ohdsi(self, sql):
        sql = render(sql, cdm_database_schema=self.s.cdm_schema, vocabulary_database_schema=self.s.vocab_schema)
        self.stmts += [x for x in split_sql(translate(sql, 'duckdb')) if x.strip()]

    def duck(self, sql):
        sql = sql.replace('@cdm.', self.s.cdm_schema + '.').replace('@vocab.', self.s.vocab_schema + '.')
        self.stmts += [x for x in split_sql(sql) if x.strip()]

    def cohorts(self, store, cids):
        """an_cohort: the entries of the given cohorts, as their definitions generate them now."""
        self.duck('CREATE TEMP TABLE an_cohort (cohort_definition_id BIGINT, subject_id BIGINT, '
                  'cohort_start_date DATE, cohort_end_date DATE)')
        for cid in dict.fromkeys(int(c) for c in cids):
            c = store.get_cohort(cid)
            if c is None:
                raise AnalysisError(f'cohort definition {cid} not found')
            self.ohdsi(build_cohort_query(json.loads(c['expression']), cdm_schema=self.s.cdm_schema,
                                          vocabulary_schema=self.s.vocab_schema, result_schema=self.s.results_schema,
                                          target_table='#an_cohort', cohort_id=cid, generate_stats=False))

    def events(self, name, where='', extra=''):
        """Cohort entries as a Circe event table (event_id, person_id, start/end, observation period)."""
        self.duck(f"""CREATE TEMP TABLE {name} AS
SELECT row_number() OVER (ORDER BY c.cohort_definition_id, c.subject_id, c.cohort_start_date) AS event_id,
  c.cohort_definition_id AS cohort_id, c.subject_id AS person_id, c.cohort_start_date AS start_date,
  c.cohort_end_date AS end_date, op.observation_period_start_date AS op_start_date,
  op.observation_period_end_date AS op_end_date, CAST(NULL AS BIGINT) AS visit_occurrence_id{extra}
FROM an_cohort c JOIN @cdm.observation_period op ON op.person_id = c.subject_id
  AND c.cohort_start_date BETWEEN op.observation_period_start_date AND op.observation_period_end_date {where}""")

    def codesets(self, concept_sets):
        """A codeset table for one set of concept sets; returns its name (Circe's #Codesets renamed)."""
        self.n += 1
        name = f'an_cs_{self.n}'
        sets = [ConceptSet.parse(c) for c in concept_sets or []]
        self.ohdsi(re.sub(r'(?i)#Codesets\b', '#' + name, _builder.get_codeset_query(sets)))
        return name

    def group(self, group, codesets, event_table):
        """Events (person_id, event_id) of event_table that satisfy a Circe criteria group; returns the table name."""
        self.n += 1
        name = f'an_g_{self.n}'
        g = CriteriaGroup.parse(group) if isinstance(group, dict) else None
        if g is None or g.is_empty():
            self.duck(f'CREATE TEMP TABLE {name} AS SELECT person_id, event_id FROM {event_table}')
            return name
        q = jreplace(_builder.get_criteria_group_query(g, event_table), '@indexId', '0')
        q = re.sub(r'(?i)#Codesets\b', '#' + codesets, q)
        self.ohdsi(f'SELECT DISTINCT person_id, event_id INTO #{name} FROM (\n{q}\n) G;')
        return name

    def windowed(self, criteria, codesets, event_table):
        """Records matching a windowed criteria, one row per record (person_id, event_id); returns the table name."""
        self.n += 1
        name = f'an_w_{self.n}'
        q = _builder.get_windowed_criteria_query(template('windowedCriteria.sql'), WindowedCriteria.parse(criteria),
                                                 event_table, None)
        q = re.sub(r'(?i)#Codesets\b', '#' + codesets, q)
        self.ohdsi(f'SELECT person_id, event_id INTO #{name} FROM (\n{q}\n) W;')
        return name

    def demographic(self, criteria, codesets, event_table):
        self.n += 1
        name = f'an_d_{self.n}'
        q = jreplace(_builder.get_demographic_criteria_query(DemographicCriteria.parse(criteria), event_table),
                     '@indexId', '0')
        q = re.sub(r'(?i)#Codesets\b', '#' + codesets, q)
        self.ohdsi(f'SELECT DISTINCT person_id, event_id INTO #{name} FROM (\n{q}\n) D;')
        return name

    def run(self, outputs):
        """Fold and run; returns {output table: [row dict, ...]}."""
        s, res = self.s, None
        for mat in ('MATERIALIZED', 'NOT MATERIALIZED'):   # DuckDB 1.5 can lose some materialized CTEs (INTERNAL error)
            q = fold(self.stmts, outputs, materialize=mat)
            try:
                rows = s.remote(q)[1] if hasattr(s, 'remote') else s.con.cursor().execute(q).fetchall()
                res = {t: json.loads(d) for t, d in rows}
                break
            except Exception as e:
                if 'CTE definition' not in str(e) or mat != 'MATERIALIZED':
                    raise
        return res


# ---- preset features ----------------------------------------------------------------------------------------------
DOMAINS = {   # domain -> (FeatureExtraction-style label, table, concept column, date column, first analysis id)
    'CONDITION': ('condition_occurrence', 'condition_occurrence', 'condition_concept_id', 'condition_start_date', 101),
    'DRUG': ('drug_exposure', 'drug_exposure', 'drug_concept_id', 'drug_exposure_start_date', 301),
    'PROCEDURE': ('procedure_occurrence', 'procedure_occurrence', 'procedure_concept_id', 'procedure_date', 501),
    'DEVICE': ('device_exposure', 'device_exposure', 'device_concept_id', 'device_exposure_start_date', 601),
    'MEASUREMENT': ('measurement', 'measurement', 'measurement_concept_id', 'measurement_date', 701),
    'OBSERVATION': ('observation', 'observation', 'observation_concept_id', 'observation_date', 801),
    'VISIT': ('visit_occurrence', 'visit_occurrence', 'visit_concept_id', 'visit_start_date', 931),
}
WINDOWS = [('AnyTimePrior', None), ('LongTerm', 365), ('MediumTerm', 180), ('ShortTerm', 30)]


def _camel(design):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', design)


def _presets():
    out = {}

    def add(aid, design, domain, stat, description, sql):
        out[aid] = {'id': aid, 'name': _camel(design), 'design': design, 'domain': domain, 'statType': stat,
                    'description': description, 'sql': sql}

    person = 'FROM an_events e JOIN @cdm.person p ON p.person_id = e.person_id'
    for aid, design, col in ((1, 'DemographicsGender', 'gender_concept_id'), (4, 'DemographicsRace', 'race_concept_id'),
                             (5, 'DemographicsEthnicity', 'ethnicity_concept_id')):
        add(aid, design, 'DEMOGRAPHICS', 'PREVALENCE', f'{_camel(design)[13:]} of the person.',
            f'SELECT e.event_id, CAST(p.{col} AS BIGINT) * 1000 + {aid} AS covariate_id, p.{col} AS concept_id, NULL AS label '
            f'{person} WHERE p.{col} <> 0')
    age = 'year(e.start_date) - p.year_of_birth'
    add(2, 'DemographicsAge', 'DEMOGRAPHICS', 'DISTRIBUTION', 'Age in years at index.',
        f"SELECT e.event_id, 1002 AS covariate_id, 0 AS concept_id, 'age in years' AS label, {age} AS value {person}")
    add(3, 'DemographicsAgeGroup', 'DEMOGRAPHICS', 'PREVALENCE', 'Age in 5-year groups at index.',
        f"SELECT e.event_id, CAST(floor(({age}) / 5) AS BIGINT) * 1000 + 3 AS covariate_id, 0 AS concept_id, "
        f"'age group: ' || lpad(CAST(CAST(floor(({age}) / 5) * 5 AS INTEGER) AS VARCHAR), 3, ' ') || ' - ' || "
        f"lpad(CAST(CAST(floor(({age}) / 5) * 5 + 4 AS INTEGER) AS VARCHAR), 3, ' ') AS label {person}")
    add(6, 'DemographicsIndexYear', 'DEMOGRAPHICS', 'PREVALENCE', 'Year of the index date.',
        "SELECT event_id, CAST(year(start_date) AS BIGINT) * 1000 + 6 AS covariate_id, 0 AS concept_id, "
        "'index year: ' || year(start_date) AS label FROM an_events")
    add(7, 'DemographicsIndexMonth', 'DEMOGRAPHICS', 'PREVALENCE', 'Month of the index date.',
        "SELECT event_id, CAST(month(start_date) AS BIGINT) * 1000 + 7 AS covariate_id, 0 AS concept_id, "
        "'index month: ' || month(start_date) AS label FROM an_events")
    for aid, design, label, expr in ((8, 'DemographicsPriorObservationTime', 'observation time (days) prior to index',
                                      'start_date - op_start_date'),
                                     (9, 'DemographicsPostObservationTime', 'observation time (days) after index',
                                      'op_end_date - start_date'),
                                     (10, 'DemographicsTimeInCohort', 'time (days) between cohort start and end',
                                      'end_date - start_date')):
        add(aid, design, 'DEMOGRAPHICS', 'DISTRIBUTION', label[0].upper() + label[1:] + '.',
            f"SELECT event_id, {1000 + aid} AS covariate_id, 0 AS concept_id, '{label}' AS label, {expr} AS value "
            f"FROM an_events")
    for domain, (label, table, col, date, first) in DOMAINS.items():
        for k, (wname, days) in enumerate(WINDOWS):
            aid = first + k
            if domain == 'VISIT':
                design = 'VisitConcept' + wname
            else:
                design = ''.join(w.capitalize() for w in label.split('_')) + wname
            text = f'during day -{days} through 0 days' if days else 'any time prior through 0 days'
            # The CDM table is cut first by a per-person table (an_persons: earliest index - window .. latest index),
            # which the engine sizes well, then matched to the entries; without that it can misjudge the size of
            # the entries (built through the cohort's own joins) and hash the large side (out of memory on measurement).
            # Any time prior: the first date of each concept per person is enough. Rows carry integers only (the label
            # is added to the aggregate).
            if days:
                x = (f"SELECT m.person_id, m.{col} AS c, m.{date} AS d FROM @cdm.{table} m JOIN an_persons b "
                     f"ON b.person_id = m.person_id AND m.{date} BETWEEN b.first_index - {days} AND b.last_index "
                     f"WHERE m.{col} <> 0")
                win = f'AND x.d >= e.start_date - {days}'
            else:
                x = (f"SELECT m.person_id, m.{col} AS c, min(m.{date}) AS d FROM @cdm.{table} m JOIN an_persons b "
                     f"ON b.person_id = m.person_id AND m.{date} <= b.last_index WHERE m.{col} <> 0 GROUP BY ALL")
                win = ''
            add(aid, design, domain, 'PREVALENCE',
                f'One covariate per {label} concept {text} relative to index.',
                f"SELECT event_id, CAST(concept_id AS BIGINT) * 1000 + {aid} AS covariate_id, concept_id, "
                f"CAST(NULL AS VARCHAR) AS label FROM (SELECT DISTINCT e.event_id, x.c AS concept_id FROM an_events e "
                f"JOIN ({x}) x ON x.person_id = e.person_id AND x.d <= e.start_date {win}) d")
            out[aid]['prefix'] = f'{label} {text} relative to index: '
    for aid, (wname, days) in ((921, ('LongTerm', 365)), (922, ('ShortTerm', 30))):
        add(aid, 'VisitCount' + wname, 'VISIT', 'DISTRIBUTION',
            f'Number of visits during day -{days} through 0 days relative to index.',
            f"SELECT e.event_id, {1000 + aid} AS covariate_id, 0 AS concept_id, "
            f"'visit count during day -{days} through 0 days relative to index' AS label, count(x.person_id) AS value "
            f"FROM an_events e LEFT JOIN (SELECT m.person_id, m.visit_start_date FROM @cdm.visit_occurrence m JOIN an_persons b "
            f"ON b.person_id = m.person_id AND m.visit_start_date BETWEEN b.first_index - {days} AND b.last_index) x "
            f"ON x.person_id = e.person_id "
            f"AND x.visit_start_date <= e.start_date AND x.visit_start_date >= e.start_date - {days} GROUP BY e.event_id")
    return out


PRESETS = _presets()
FIRST_CUSTOM_FA = 1001
AGGREGATES = [{'id': 1, 'name': 'Events count', 'domain': None, 'function': 'COUNT', 'expression': None,
               'joinTable': None, 'joinType': None, 'joinCondition': None, 'isDefault': True, 'missingMeansZero': True,
               'additionalColumns': None}]


# ---- characterization ---------------------------------------------------------------------------------------------
def features(sc, fas):
    """Feature queries for some feature analyses: ([(analysis id, binary query)], [(analysis id, continuous query)]).
    Binary queries give one row per entry and covariate (event_id, covariate_id, concept_id, label); continuous ones
    one value per entry and covariate."""
    binary, cont = [], []
    for fa in fas:
        aid = fa['id']
        if fa['type'] == 'PRESET':
            p = PRESETS[aid]
            (binary if p['statType'] == 'PREVALENCE' else cont).append((aid, p['sql']))
        elif fa['type'] == 'CRITERIA_SET':
            cs = sc.codesets(fa.get('conceptSets'))
            for i, item in enumerate(fa.get('design') or []):
                cov = int(item.get('id') or i + 1)
                label = (item.get('name') or f'criteria {i + 1}').replace("'", "''")
                expr = item.get('expression')
                if fa.get('statType') == 'DISTRIBUTION':
                    if item.get('criteriaType') == 'DemographicCriteria':
                        t = sc.demographic(expr, cs, 'an_events')
                        val = f'CASE WHEN EXISTS (SELECT 1 FROM {t} m WHERE m.event_id = e.event_id) THEN 1 ELSE 0 END'
                        cont.append((aid, f"SELECT e.event_id, {cov} AS covariate_id, 0 AS concept_id, '{label}' AS label, "
                                          f"{val} AS value FROM an_events e"))
                    else:
                        t = sc.windowed(expr, cs, 'an_events')
                        cont.append((aid, f"SELECT e.event_id, {cov} AS covariate_id, 0 AS concept_id, '{label}' AS label, "
                                          f"count(m.event_id) AS value FROM an_events e LEFT JOIN {t} m "
                                          f"ON m.event_id = e.event_id GROUP BY e.event_id"))
                else:
                    t = sc.group(expr, cs, 'an_events')
                    binary.append((aid, f"SELECT event_id, {cov} AS covariate_id, 0 AS concept_id, '{label}' AS label "
                                        f"FROM {t}"))
        else:
            raise AnalysisError(f"feature analysis '{fa['name']}': custom SQL features are not run by this server")
    return binary, cont


def _binary_sql(binary):
    """Prevalence by cohort and stratum, aggregated as the rows stream (no table of entry-level rows)."""
    m = _min_count()
    prefix = {aid: PRESETS[aid]['prefix'] for aid, _ in binary if aid in PRESETS and 'prefix' in PRESETS[aid]}
    label = ('CASE b.analysis_id ' + ' '.join(f"WHEN {aid} THEN '{p}'" for aid, p in prefix.items()) + ' END'
             if prefix else 'NULL')
    rows = ' UNION ALL '.join(f'SELECT {aid} AS analysis_id, event_id, covariate_id, concept_id, label FROM ({q}) b'
                              for aid, q in binary)
    return f"""CREATE TEMP TABLE an_bin AS
SELECT f.analysis_id, f.covariate_id, any_value(f.concept_id) AS concept_id, any_value(f.label) AS label, e.cohort_id,
  st.strata_id, count(*) AS n
FROM ({rows}) f JOIN an_events e ON e.event_id = f.event_id JOIN an_strata st ON st.event_id = f.event_id
GROUP BY f.analysis_id, f.covariate_id, e.cohort_id, st.strata_id HAVING count(*) >= {m};
CREATE TEMP TABLE an_out_bin AS
SELECT b.analysis_id AS "analysisId", b.covariate_id AS "covariateId", b.concept_id AS "conceptId",
  coalesce(b.label, {label} || coalesce(c.concept_name, ''), c.concept_name) AS "covariateName", c.concept_name AS "conceptName", c.domain_id AS "domainId", b.cohort_id AS "cohortId",
  b.strata_id AS "strataId", b.n AS "count", round(100.0 * b.n / d.n, 4) AS "pct"
FROM an_bin b JOIN an_denom d ON d.cohort_id = b.cohort_id AND d.strata_id = b.strata_id AND d.n >= {m}
LEFT JOIN @vocab.concept c ON c.concept_id = b.concept_id AND b.concept_id <> 0"""


def _continuous_sql(cont):
    m = _min_count()
    rows = ' UNION ALL '.join(f'SELECT {aid} AS analysis_id, event_id, covariate_id, concept_id, label, '
                              f'CAST(value AS DOUBLE) AS value FROM ({q}) c' for aid, q in cont)
    return f"""CREATE TEMP TABLE an_out_cont AS
SELECT f.analysis_id AS "analysisId", f.covariate_id AS "covariateId", any_value(f.concept_id) AS "conceptId",
  any_value(f.label) AS "covariateName", e.cohort_id AS "cohortId", st.strata_id AS "strataId", count(*) AS "count",
  round(avg(f.value), 4) AS "avg", round(coalesce(stddev_samp(f.value), 0), 4) AS "stdDev", min(f.value) AS "min",
  quantile_disc(f.value, 0.1) AS "p10", quantile_disc(f.value, 0.25) AS "p25", quantile_disc(f.value, 0.5) AS "median",
  quantile_disc(f.value, 0.75) AS "p75", quantile_disc(f.value, 0.9) AS "p90", max(f.value) AS "max"
FROM ({rows}) f JOIN an_events e ON e.event_id = f.event_id JOIN an_strata st ON st.event_id = f.event_id
WHERE f.value IS NOT NULL GROUP BY f.analysis_id, f.covariate_id, e.cohort_id, st.strata_id
HAVING count(*) >= {m} AND count(*) FILTER (WHERE f.value <> 0) NOT BETWEEN 1 AND {m - 1}"""


def characterize(s, store, design, fa_lookup):
    cohorts = design.get('cohorts') or []
    fas = [fa_lookup(int(f['id'])) for f in design.get('featureAnalyses') or []]
    if not cohorts or not fas:
        raise AnalysisError('a characterization needs at least one cohort and one feature analysis')
    strata = design.get('stratas') or []

    def base():
        """cohorts, their entries (an_events) and persons (an_persons), strata (an_strata), denominators (an_denom)"""
        sc = Script(s)
        sc.cohorts(store, [c['id'] for c in cohorts])
        sc.events('an_events')
        parts = [] if design.get('strataOnly') and strata else ['SELECT 0 AS strata_id, event_id FROM an_events']
        if strata:
            cs = sc.codesets(design.get('strataConceptSets'))
            for k, st in enumerate(strata):
                crit = st.get('criteria')
                if isinstance(crit, str):
                    crit = json.loads(crit) if crit.strip() else None
                sid = int(st['id']) if str(st.get('id', '')).isdigit() else k + 1
                parts.append(f'SELECT {sid} AS strata_id, event_id FROM {sc.group(crit, cs, "an_events")}')
        sc.duck('CREATE TEMP TABLE an_persons AS SELECT person_id, min(start_date) AS first_index, '
                'max(start_date) AS last_index FROM an_events GROUP BY person_id')
        sc.duck('CREATE TEMP TABLE an_strata AS ' + ' UNION ALL '.join(parts))
        sc.duck('CREATE TEMP TABLE an_denom AS SELECT e.cohort_id, s.strata_id, count(*) AS n '
                'FROM an_events e JOIN an_strata s ON s.event_id = e.event_id GROUP BY ALL')
        return sc

    # one query per feature analysis that reads a large CDM table, the demographics together: the engine's memory
    # is shared, and the cohorts are cheap to rebuild next to a scan of drug_exposure or measurement
    light = [f for f in fas if f['type'] == 'PRESET' and PRESETS[f['id']]['domain'] == 'DEMOGRAPHICS']
    batches = ([light] if light else []) + [[f] for f in fas if f not in light]
    res = {'an_out_bin': [], 'an_out_cont': []}
    for batch in batches:
        sc = base()
        binary, cont = features(sc, batch)
        outs = []
        if binary:
            sc.duck(_binary_sql(binary))
            outs.append('an_out_bin')
        if cont:
            sc.duck(_continuous_sql(cont))
            outs.append('an_out_cont')
        for t, rows in sc.run(outs).items():
            res[t] += rows

    names = {int(c['id']): c.get('name') for c in cohorts}
    snames = {0: None}
    for k, st in enumerate(strata):
        snames[int(st['id']) if str(st.get('id', '')).isdigit() else k + 1] = st.get('name')
    fa_meta = {f['id']: f for f in fas}
    rows = []
    for t, kind in (('an_out_bin', 'PREVALENCE'), ('an_out_cont', 'DISTRIBUTION')):
        for r in res.get(t) or []:
            fa = fa_meta[r['analysisId']]
            r.update(resultType=kind, analysisName=fa['name'], faType=fa['type'], cohortName=names.get(r['cohortId']))
            if r['strataId']:
                r['strataName'] = snames.get(r['strataId'])
            else:
                del r['strataId']                  # the page treats a missing stratum as "overall"
            rows.append({k: v for k, v in r.items() if v is not None})
    return rows


# ---- pathways -----------------------------------------------------------------------------------------------------
def pathways(s, store, design):
    targets = [int(c['id']) for c in design.get('targetCohorts') or []]
    events = [int(c['id']) for c in design.get('eventCohorts') or []]
    if not targets or not events:
        raise AnalysisError('a pathway analysis needs target and event cohorts')
    window = int(design.get('combinationWindow') or 0)
    depth = int(design.get('maxDepth') or 5)
    minc = max(int(design.get('minCellCount') or 0), _min_count())
    codes = {cid: 1 << i for i, cid in enumerate(events)}
    sc = Script(s)
    sc.cohorts(store, targets + events)
    case = ' '.join(f'WHEN {cid} THEN {code}' for cid, code in codes.items())
    sc.duck(f"""CREATE TEMP TABLE an_pw_t AS
SELECT row_number() OVER (ORDER BY cohort_definition_id, subject_id, cohort_start_date) AS entry_id,
  cohort_definition_id AS target_id, subject_id AS person_id, cohort_start_date AS t_start, cohort_end_date AS t_end
FROM an_cohort WHERE cohort_definition_id IN ({','.join(map(str, targets))})""")
    sc.duck(f"""CREATE TEMP TABLE an_pw_e AS
SELECT t.target_id, t.entry_id, CASE c.cohort_definition_id {case} END AS code, c.cohort_start_date AS e_start
FROM an_pw_t t JOIN an_cohort c ON c.subject_id = t.person_id AND c.cohort_definition_id IN ({','.join(map(str, events))})
  AND c.cohort_start_date BETWEEN t.t_start AND t.t_end""")
    sc.duck(f"""CREATE TEMP TABLE an_pw_g AS
SELECT target_id, entry_id, code, e_start, sum(CASE WHEN prev IS NULL OR e_start - prev > {window} THEN 1 ELSE 0 END)
  OVER (PARTITION BY entry_id ORDER BY e_start, code ROWS UNBOUNDED PRECEDING) AS grp
FROM (SELECT *, lag(e_start) OVER (PARTITION BY entry_id ORDER BY e_start, code) AS prev FROM an_pw_e) x""")
    keep = ('prev_code IS NULL OR prev_code <> code' if design.get('allowRepeats')
            else 'row_number() OVER (PARTITION BY entry_id, code ORDER BY grp) = 1')
    sc.duck(f"""CREATE TEMP TABLE an_pw_s AS
SELECT target_id, entry_id, grp, code FROM (
  SELECT *, lag(code) OVER (PARTITION BY entry_id ORDER BY grp) AS prev_code
  FROM (SELECT target_id, entry_id, grp, bit_or(code) AS code FROM an_pw_g GROUP BY ALL) s0) s1
QUALIFY {keep}""")
    sc.duck(f"""CREATE TEMP TABLE an_pw_p AS
SELECT target_id, entry_id, string_agg(CAST(code AS VARCHAR), '-' ORDER BY rn) AS path FROM (
  SELECT *, row_number() OVER (PARTITION BY entry_id ORDER BY grp) AS rn FROM an_pw_s) x
WHERE rn <= {depth} GROUP BY target_id, entry_id""")
    sc.duck(f"""CREATE TEMP TABLE an_pw_paths AS
SELECT target_id, path, count(*) AS n FROM an_pw_p GROUP BY ALL HAVING count(*) >= {minc}""")
    sc.duck("""CREATE TEMP TABLE an_pw_counts AS
SELECT t.target_id, count(*) AS total, count(p.entry_id) AS with_path
FROM an_pw_t t LEFT JOIN an_pw_p p ON p.entry_id = t.entry_id GROUP BY t.target_id""")
    res = sc.run(['an_pw_counts', 'an_pw_paths'])
    counts = {r['target_id']: r for r in res['an_pw_counts']}
    names = {int(c['id']): c.get('name') or f'Cohort {c["id"]}' for c in design.get('eventCohorts') or []}
    seen = set(codes.values())
    groups = []
    for t in targets:
        c = counts.get(t, {'total': 0, 'with_path': 0})
        paths = [{'path': r['path'], 'personCount': r['n']} for r in res['an_pw_paths'] if r['target_id'] == t]
        paths.sort(key=lambda p: -p['personCount'])
        for p in paths:
            seen.update(int(x) for x in p['path'].split('-'))
        groups.append({'targetCohortId': t, 'targetCohortCount': cells.mask(c['total']),
                       'totalPathwaysCount': cells.mask(c['with_path']), 'pathways': paths})
    by_code = {code: names.get(cid, f'Cohort {cid}') for cid, code in codes.items()}
    event_codes = []
    for code in sorted(seen):
        parts = [by_code[b] for b in sorted(by_code) if code & b]
        event_codes.append({'code': code, 'name': ' + '.join(parts), 'isCombo': len(parts) > 1})
    return {'pathwayGroups': groups, 'eventCodes': event_codes}


# ---- incidence rates ----------------------------------------------------------------------------------------------
def _tar_date(point):
    col = 'c.cohort_end_date' if (point or {}).get('DateField') == 'EndDate' else 'c.cohort_start_date'
    return f'({col} + {int((point or {}).get("Offset") or 0)})'


def _date_literal(v):
    return "DATE '%s'" % re.sub(r'[^0-9-]', '', str(v))[:10] if v else None


def incidence(s, store, expr):
    targets = [int(x) for x in expr.get('targetIds') or []]
    outcomes = [int(x) for x in expr.get('outcomeIds') or []]
    if not targets or not outcomes:
        raise AnalysisError('an incidence rate analysis needs target and outcome cohorts')
    tar = expr.get('timeAtRisk') or {}
    start, end = _tar_date(tar.get('start')), _tar_date(tar.get('end'))
    end = f'least({end}, op.observation_period_end_date)'
    sw = expr.get('studyWindow') or {}
    if _date_literal(sw.get('startDate')):
        start = f"greatest({start}, {_date_literal(sw['startDate'])})"
    if _date_literal(sw.get('endDate')):
        end = f"least({end}, {_date_literal(sw['endDate'])})"
    sc = Script(s)
    sc.cohorts(store, targets + outcomes)
    sc.events('an_ir_t', where=f'WHERE c.cohort_definition_id IN ({",".join(map(str, targets))})',
              extra=f', {start} AS tar_start, {end} AS tar_end')
    strata = expr.get('strata') or []
    mask = '0'
    if strata:
        cs = sc.codesets(expr.get('ConceptSets'))
        joins = []
        for k, st in enumerate(strata):
            g = st.get('expression')
            if isinstance(g, str):
                g = json.loads(g) if g.strip() else None
            joins.append(f'(CASE WHEN EXISTS (SELECT 1 FROM {sc.group(g, cs, "an_ir_t")} m '
                         f'WHERE m.event_id = e.event_id) THEN {1 << k} ELSE 0 END)')
        mask = ' + '.join(joins)
    sc.duck(f'CREATE TEMP TABLE an_ir_e AS SELECT e.*, {mask} AS mask FROM an_ir_t e WHERE e.tar_end >= e.tar_start')
    sc.duck(f"""CREATE TEMP TABLE an_ir_prior AS
SELECT DISTINCT e.event_id, o.cohort_definition_id AS outcome_id
FROM an_ir_e e JOIN an_cohort o ON o.subject_id = e.person_id AND o.cohort_definition_id IN ({",".join(map(str, outcomes))})
  AND o.cohort_start_date < e.tar_start""")
    sc.duck(f"""CREATE TEMP TABLE an_ir_o AS
SELECT e.event_id, o.cohort_definition_id AS outcome_id, min(o.cohort_start_date) AS o_date
FROM an_ir_e e JOIN an_cohort o ON o.subject_id = e.person_id AND o.cohort_definition_id IN ({",".join(map(str, outcomes))})
  AND o.cohort_start_date BETWEEN e.tar_start AND e.tar_end GROUP BY ALL""")
    sc.duck(f"""CREATE TEMP TABLE an_ir_eo AS
SELECT e.cohort_id AS target_id, oc.outcome_id, e.person_id, e.mask, x.o_date IS NOT NULL AS is_case,
  CASE WHEN x.o_date IS NOT NULL THEN x.o_date - e.tar_start ELSE e.tar_end - e.tar_start END AS tar
FROM an_ir_e e CROSS JOIN (SELECT unnest([{",".join(map(str, outcomes))}]) AS outcome_id) oc
LEFT JOIN an_ir_o x ON x.event_id = e.event_id AND x.outcome_id = oc.outcome_id
WHERE NOT EXISTS (SELECT 1 FROM an_ir_prior p WHERE p.event_id = e.event_id AND p.outcome_id = oc.outcome_id)""")
    agg = ('count(DISTINCT person_id) AS persons, count(DISTINCT CASE WHEN is_case THEN person_id END) AS cases, '
           'coalesce(sum(tar), 0) AS tar')
    sc.duck(f'CREATE TEMP TABLE an_ir_sum AS SELECT target_id, outcome_id, {agg} FROM an_ir_eo GROUP BY ALL')
    sc.duck(f'CREATE TEMP TABLE an_ir_mask AS SELECT target_id, outcome_id, mask, {agg} FROM an_ir_eo GROUP BY ALL')
    outs = ['an_ir_sum', 'an_ir_mask']
    if strata:
        sc.duck('CREATE TEMP TABLE an_ir_strata AS ' + ' UNION ALL '.join(
            f'SELECT target_id, outcome_id, {k} AS k, {agg} FROM an_ir_eo WHERE mask & {1 << k} <> 0 GROUP BY ALL'
            for k in range(len(strata))))
        outs.append('an_ir_strata')
    res = sc.run(outs)
    summary = {(r['target_id'], r['outcome_id']): r for r in res['an_ir_sum']}
    out = []
    for t in targets:
        for o in outcomes:
            r = summary.get((t, o), {'persons': 0, 'cases': 0, 'tar': 0})
            leaves = [x for x in res['an_ir_mask'] if x['target_id'] == t and x['outcome_id'] == o]
            stats = []
            for k, st in enumerate(strata):
                x = next((y for y in res.get('an_ir_strata') or [] if y['target_id'] == t and y['outcome_id'] == o
                          and y['k'] == k), {'persons': 0, 'cases': 0, 'tar': 0})
                stats.append(dict(_rates(x), id=k, name=st.get('name') or f'Stratum {k + 1}'))
            out.append({'targetId': t, 'outcomeId': o, 'summary': dict(_rates(r), targetId=t, outcomeId=o),
                        'stratifyStats': stats, 'treemapData': json.dumps(_ir_treemap(leaves, len(strata)))})
    return out


def _rates(r):
    persons, cases, tar = r['persons'], r['cases'], r['tar'] or 0
    if cells.small(persons):
        return {'totalPersons': cells.MASK, 'cases': cells.MASK, 'timeAtRisk': tar, 'proportion': cells.MASK,
                'rate': cells.MASK}
    if cells.small(cases):
        return {'totalPersons': persons, 'cases': cells.MASK, 'timeAtRisk': tar, 'proportion': cells.MASK,
                'rate': cells.MASK}
    return {'totalPersons': persons, 'cases': cases, 'timeAtRisk': tar,
            'proportion': cases / persons if persons else 0, 'rate': cases / (tar / 365.25) if tar else 0}


def _ir_treemap(leaves, nstrata):
    if not nstrata or any(cells.small(x['persons']) or cells.small(x['cases']) for x in leaves):
        return {'name': 'Everyone', 'children': []}      # leaf sizes would show small counts
    groups = {}
    for x in leaves:
        bits = ''.join('1' if x['mask'] >> i & 1 else '0' for i in range(nstrata))
        groups.setdefault(bits.count('1'), []).append({'name': bits, 'size': x['persons'], 'cases': x['cases'],
                                                       'timeAtRisk': x['tar']})
    for g in groups.values():
        g.sort(key=lambda x: x['name'], reverse=True)
    return {'name': 'Everyone', 'children': [{'name': f'Group {k}', 'children': groups[k]}
                                             for k in sorted(groups, reverse=True)]}


# ---- WebAPI endpoints ---------------------------------------------------------------------------------------------
def install(app, store, src):
    def user():
        return {'id': 1, 'login': store.user['login'], 'name': store.user['login']}

    def common(r):
        d = {'createdBy': user(), 'createdDate': r['created_date'], 'tags': [], 'hasWriteAccess': True,
             'hasReadAccess': True}
        if r['modified_by']:
            d['modifiedBy'], d['modifiedDate'] = user(), r['modified_date']
        return d

    def stored(kind, aid):
        r = store.get_analysis(kind, aid)
        if r is None:
            raise HTTPException(404, f'{kind} {aid} not found')
        return r

    def background(job_name, params, fn):
        jid = store.start_job(job_name, dict(params, jobAuthor=store.user['login']))

        def go():
            try:
                fn()
                store.finish_job(jid, 'COMPLETED', 'COMPLETED')
            except Exception as e:
                store.finish_job(jid, 'FAILED', f'FAILED: {e}'[:1000])
        # copy_context: the run keeps this request's viewer identity (remote sources query as the viewer)
        threading.Thread(target=contextvars.copy_context().run, args=(go,), daemon=True).start()

    def execute(kind, aid, s, design, fn, label):
        rid = store.start_run(kind, aid, s, json.dumps(design))

        def work():
            try:
                try:
                    from .remote import purpose_text
                    purpose_text.set(f"CDM ATLAS {label} — '{design.get('name') or aid}' ({kind} {aid})")
                except ImportError:
                    pass
                result = fn()
                store.finish_run(rid, 'COMPLETED', None, json.dumps(result))
            except Exception as e:
                if not isinstance(e, AnalysisError):
                    traceback.print_exc()
                store.finish_run(rid, 'FAILED', f'{type(e).__name__}: {e}'[:4000])
                raise
        return rid, work

    def run_result(kind, rid):
        rows = store.runs(kind, rid=rid)
        if not rows:
            raise HTTPException(404, 'generation not found')
        if rows[0]['status'] != 'COMPLETED':
            raise HTTPException(409, f"generation {rid} is {rows[0]['status']}")
        return json.loads(rows[0]['result'])

    # -- feature analyses (presets come from the code, the rest from the store)
    def fa_custom(r):
        d = json.loads(r['design'] or '{}')
        d.update(id=r['id'], name=r['name'], description=r['description'] or '', **common(r))
        return d

    def fa_preset(p):
        return {'id': p['id'], 'name': p['name'], 'description': p['description'], 'type': 'PRESET',
                'domain': p['domain'], 'statType': p['statType'], 'design': p['design'], 'supportsAnnual': False,
                'supportsTemporal': False, 'createdBy': user(), 'createdDate': 0}

    def fa_lookup(fid):
        if fid in PRESETS:
            return fa_preset(PRESETS[fid])
        return fa_custom(stored('fa', fid))

    @app.get('/WebAPI/feature-analysis')
    def fa_list():
        out = [fa_preset(p) for p in PRESETS.values()]
        for r in store.list_analyses('fa'):
            d = fa_custom(r)
            out.append({k: v for k, v in d.items() if k not in ('design', 'conceptSets')})
        return {'content': out, 'totalElements': len(out), 'totalPages': 1, 'size': len(out), 'number': 0}

    @app.get('/WebAPI/feature-analysis/domains')
    def fa_domains():
        return [{'id': d, 'name': d.title()} for d in ('CONDITION', 'DEVICE', 'DRUG', 'MEASUREMENT', 'OBSERVATION',
                                                        'PROCEDURE', 'VISIT', 'DEMOGRAPHICS')]

    @app.get('/WebAPI/feature-analysis/aggregates')
    def fa_aggregates():
        return AGGREGATES

    @app.get('/WebAPI/feature-analysis/{fid}')
    def fa_get(fid: int):
        return fa_lookup(fid)

    def fa_body(b):
        if b.get('type') == 'CUSTOM_FE':
            raise HTTPException(400, 'custom SQL feature analyses are not supported on this server')
        if b.get('type') == 'PRESET':
            raise HTTPException(400, 'preset feature analyses cannot be created or changed')
        keep = {k: b.get(k) for k in ('type', 'domain', 'statType', 'design', 'conceptSets', 'supportsAnnual',
                                      'supportsTemporal') if b.get(k) is not None}
        return json.dumps(keep)

    @app.post('/WebAPI/feature-analysis')
    async def fa_create(request: Request):
        b = await request.json()
        fid = store.save_analysis('fa', None, b.get('name') or 'New feature analysis', b.get('description'),
                                  fa_body(b), first_id=FIRST_CUSTOM_FA)
        return fa_lookup(fid)

    @app.put('/WebAPI/feature-analysis/{fid}')
    async def fa_update(fid: int, request: Request):
        b = await request.json()
        r = stored('fa', fid)
        store.save_analysis('fa', fid, b.get('name') or r['name'], b.get('description'), fa_body(b))
        return fa_lookup(fid)

    @app.delete('/WebAPI/feature-analysis/{fid}')
    def fa_delete(fid: int):
        stored('fa', fid)
        store.delete_analysis('fa', fid)
        return Response(status_code=204)

    @app.get('/WebAPI/feature-analysis/{fid}/copy')
    def fa_copy(fid: int):
        r = stored('fa', fid)
        return fa_lookup(store.save_analysis('fa', None, 'COPY OF: ' + r['name'], r['description'], r['design'],
                                             first_id=FIRST_CUSTOM_FA))

    # -- characterizations
    def cc_dto(r):
        d = json.loads(r['design'] or '{}')
        d.update(id=r['id'], name=r['name'], description=r['description'] or '', **common(r))
        for k in ('cohorts', 'featureAnalyses', 'stratas', 'parameters'):
            d.setdefault(k, [])
        return d

    def cc_save(cid, b):
        design = {k: b.get(k) for k in ('cohorts', 'featureAnalyses', 'stratas', 'strataConceptSets', 'stratifiedBy',
                                        'strataOnly', 'parameters') if b.get(k) is not None}
        for i, st in enumerate(design.get('stratas') or []):
            st.setdefault('id', i + 1)
            if isinstance(st.get('criteria'), str):
                st['criteria'] = json.loads(st['criteria']) if st['criteria'].strip() else None
        design['cohorts'] = [{'id': c['id'], 'name': c.get('name') or f"Cohort {c['id']}"} for c in design.get('cohorts') or []]
        return store.save_analysis('cc', cid, b.get('name') or 'New characterization', b.get('description'),
                                   json.dumps(design))

    def cc_run(r):
        return {'id': r['id'], 'ccGenerationId': r['id'], 'status': r['status'], 'executionStatus': r['status'],
                'startTime': r['start_time'], 'endTime': r['end_time'],
                'duration': (r['end_time'] or now_ms()) - r['start_time'], 'sourceKey': r['source_key'],
                **({'exitMessage': r['message']} if r['message'] else {})}

    @app.get('/WebAPI/cohort-characterization')
    def cc_list():
        out = [cc_dto(r) for r in store.list_analyses('cc')]
        return {'content': out, 'totalElements': len(out), 'totalPages': 1, 'size': len(out), 'number': 0}

    @app.post('/WebAPI/cohort-characterization')
    async def cc_create(request: Request):
        return cc_dto(stored('cc', cc_save(None, await request.json())))

    @app.post('/WebAPI/cohort-characterization/import')
    async def cc_import(request: Request):
        return await cc_create(request)

    @app.get('/WebAPI/cohort-characterization/{cid}')
    @app.get('/WebAPI/cohort-characterization/{cid}/design')
    @app.get('/WebAPI/cohort-characterization/{cid}/export')
    def cc_get(cid: int):
        return cc_dto(stored('cc', cid))

    @app.put('/WebAPI/cohort-characterization/{cid}')
    async def cc_update(cid: int, request: Request):
        stored('cc', cid)
        return cc_dto(stored('cc', cc_save(cid, await request.json())))

    @app.post('/WebAPI/cohort-characterization/{cid}')
    def cc_copy(cid: int):
        r = stored('cc', cid)
        return cc_dto(stored('cc', store.save_analysis('cc', None, 'COPY OF: ' + r['name'], r['description'],
                                                       r['design'])))

    @app.delete('/WebAPI/cohort-characterization/{cid}')
    def cc_delete(cid: int):
        store.delete_analysis('cc', cid)
        return Response(status_code=204)

    @app.get('/WebAPI/cohort-characterization/{cid}/generation')
    def cc_generations(cid: int):
        return [cc_run(r) for r in store.runs('cc', cid)]

    @app.post('/WebAPI/cohort-characterization/{cid}/generation/{key}')
    def cc_generate(cid: int, key):
        s = src(key)
        design = cc_dto(stored('cc', cid))
        rid, work = execute('cc', cid, s, design, lambda: characterize(s, store, design, fa_lookup), '특성 분석')
        background('generateCohortCharacterization', {'cohort_characterization_id': cid, 'source_key': key,
                                                      'jobName': f'Generating characterization {cid} : {key}'}, work)
        return cc_run(store.runs('cc', rid=rid)[0])

    @app.delete('/WebAPI/cohort-characterization/{cid}/generation/{key}')
    def cc_cancel(cid: int, key):
        return Response(status_code=204)

    @app.get('/WebAPI/cohort-characterization/generation/{rid}')
    def cc_generation(rid: int):
        rows = store.runs('cc', rid=rid)
        if not rows:
            raise HTTPException(404, 'generation not found')
        return cc_run(rows[0])

    @app.get('/WebAPI/cohort-characterization/generation/{rid}/design')
    def cc_generation_design(rid: int):
        rows = store.runs('cc', rid=rid)
        if not rows:
            raise HTTPException(404, 'generation not found')
        return json.loads(rows[0]['design'])

    @app.get('/WebAPI/cohort-characterization/generation/{rid}/result/count')
    def cc_result_count(rid: int):
        return len(run_result('cc', rid))

    @app.post('/WebAPI/cohort-characterization/generation/{rid}/result')
    async def cc_result(rid: int, request: Request):
        rows = run_result('cc', rid)
        try:
            f = await request.json()
        except Exception:
            f = None
        if isinstance(f, dict):
            for key, col in (('analysisIds', 'analysisId'), ('cohortIds', 'cohortId')):
                if f.get(key):
                    want = {int(x) for x in f[key]}
                    rows = [r for r in rows if r.get(col) in want]
        return rows

    # -- pathways
    def pw_dto(r):
        d = json.loads(r['design'] or '{}')
        d.update(id=r['id'], name=r['name'], description=r['description'] or '', **common(r))
        for k, v in (('targetCohorts', []), ('eventCohorts', []), ('combinationWindow', 30), ('minCellCount', 5),
                     ('maxDepth', 5), ('allowRepeats', False)):
            d.setdefault(k, v)
        return d

    def pw_save(pid, b):
        design = {k: b.get(k) for k in ('targetCohorts', 'eventCohorts', 'combinationWindow', 'minCellCount',
                                        'maxDepth', 'allowRepeats') if b.get(k) is not None}
        for k in ('targetCohorts', 'eventCohorts'):
            design[k] = [{'id': c['id'], 'name': c.get('name') or f"Cohort {c['id']}", **({'code': c['code']} if 'code' in c else {})}
                         for c in design.get(k) or []]
        return store.save_analysis('pw', pid, b.get('name') or 'New pathway analysis', b.get('description'),
                                   json.dumps(design))

    def pw_run(r):
        status = 'STARTED' if r['status'] == 'RUNNING' else r['status']      # the page's pathway states
        return {'id': r['id'], 'status': status, 'sourceKey': r['source_key'], 'startTime': r['start_time'],
                'executionDate': r['start_time'], 'endTime': r['end_time'],
                'duration': (r['end_time'] or now_ms()) - r['start_time'],
                **({'exitMessage': r['message']} if r['message'] else {})}

    @app.get('/WebAPI/pathway-analysis')
    def pw_list():
        out = [pw_dto(r) for r in store.list_analyses('pw')]
        return {'content': out, 'totalElements': len(out), 'totalPages': 1, 'size': len(out), 'number': 0}

    @app.post('/WebAPI/pathway-analysis')
    async def pw_create(request: Request):
        return pw_dto(stored('pw', pw_save(None, await request.json())))

    @app.post('/WebAPI/pathway-analysis/import')
    async def pw_import(request: Request):
        return await pw_create(request)

    @app.post('/WebAPI/pathway-analysis/check')
    async def pw_check(request: Request):
        return []

    @app.get('/WebAPI/pathway-analysis/{pid}')
    @app.get('/WebAPI/pathway-analysis/{pid}/export')
    def pw_get(pid: int):
        return pw_dto(stored('pw', pid))

    @app.put('/WebAPI/pathway-analysis/{pid}')
    async def pw_update(pid: int, request: Request):
        stored('pw', pid)
        return pw_dto(stored('pw', pw_save(pid, await request.json())))

    @app.post('/WebAPI/pathway-analysis/{pid}')
    def pw_copy(pid: int):
        r = stored('pw', pid)
        return pw_dto(stored('pw', store.save_analysis('pw', None, 'COPY OF: ' + r['name'], r['description'],
                                                       r['design'])))

    @app.delete('/WebAPI/pathway-analysis/{pid}')
    def pw_delete(pid: int):
        store.delete_analysis('pw', pid)
        return Response(status_code=204)

    @app.get('/WebAPI/pathway-analysis/{pid}/exists')
    def pw_exists(pid: int, name: str = ''):
        return sum(1 for r in store.list_analyses('pw') if r['name'] == name and r['id'] != pid)

    @app.get('/WebAPI/pathway-analysis/{pid}/generation')
    def pw_generations(pid: int):
        return [pw_run(r) for r in store.runs('pw', pid)]

    @app.post('/WebAPI/pathway-analysis/{pid}/generation/{key}')
    def pw_generate(pid: int, key):
        s = src(key)
        design = pw_dto(stored('pw', pid))
        rid, work = execute('pw', pid, s, design, lambda: pathways(s, store, design), '코호트 경로 분석')
        background('generatePathwayAnalysis', {'pathway_analysis_id': pid, 'source_key': key,
                                               'jobName': f'Generating pathway analysis {pid} : {key}'}, work)
        return pw_run(store.runs('pw', rid=rid)[0])

    @app.delete('/WebAPI/pathway-analysis/{pid}/generation/{key}')
    def pw_cancel(pid: int, key):
        return Response(status_code=204)

    @app.get('/WebAPI/pathway-analysis/generation/{rid}')
    def pw_generation(rid: int):
        rows = store.runs('pw', rid=rid)
        if not rows:
            raise HTTPException(404, 'generation not found')
        return pw_run(rows[0])

    @app.get('/WebAPI/pathway-analysis/generation/{rid}/design')
    def pw_generation_design(rid: int):
        rows = store.runs('pw', rid=rid)
        if not rows:
            raise HTTPException(404, 'generation not found')
        return json.loads(rows[0]['design'])

    @app.get('/WebAPI/pathway-analysis/generation/{rid}/result')
    def pw_result(rid: int):
        return run_result('pw', rid)

    # -- incidence rates (WebAPI keeps the expression as a JSON string)
    def ir_dto(r):
        d = {'id': r['id'], 'name': r['name'], 'description': r['description'] or '', 'expression': r['design'],
             **common(r)}
        if r['modified_by']:
            d['modifiedBy'] = user()
        return d

    def ir_save(iid, b):
        e = b.get('expression')
        e = json.loads(e) if isinstance(e, str) else (e or {})
        return store.save_analysis('ir', iid, b.get('name') or 'New incidence rate analysis', b.get('description'),
                                   json.dumps(e))

    def ir_info(r, s_key=None):
        st = {'COMPLETED': 'COMPLETE', 'RUNNING': 'RUNNING'}.get(r['status'], r['status'])
        summaries = [x['summary'] for x in json.loads(r['result'])] if r['status'] == 'COMPLETED' else []
        return {'executionInfo': {'id': {'analysisId': r['analysis_id'], 'sourceId': r['source_id']}, 'status': st,
                                  'startTime': r['start_time'],
                                  'executionDuration': (r['end_time'] or now_ms()) - r['start_time'],
                                  'isValid': r['status'] == 'COMPLETED', 'isCanceled': False, 'message': r['message']},
                'summaryList': summaries}

    def ir_latest(iid):
        latest = {}
        for r in store.runs('ir', iid):          # newest first
            latest.setdefault(r['source_key'], r)
        return latest

    @app.get('/WebAPI/ir/')
    @app.get('/WebAPI/ir')
    def ir_list():
        return [{k: v for k, v in ir_dto(r).items() if k != 'expression'} for r in store.list_analyses('ir')]

    @app.post('/WebAPI/ir/')
    @app.post('/WebAPI/ir')
    @app.post('/WebAPI/ir/design')
    async def ir_create(request: Request):
        return ir_dto(stored('ir', ir_save(None, await request.json())))

    @app.get('/WebAPI/ir/{iid}')
    @app.get('/WebAPI/ir/{iid}/design')
    def ir_get(iid: int):
        return ir_dto(stored('ir', iid))

    @app.put('/WebAPI/ir/{iid}')
    async def ir_update(iid: int, request: Request):
        stored('ir', iid)
        return ir_dto(stored('ir', ir_save(iid, await request.json())))

    @app.delete('/WebAPI/ir/{iid}')
    def ir_delete(iid: int):
        store.delete_analysis('ir', iid)
        return Response(status_code=204)

    @app.get('/WebAPI/ir/{iid}/copy')
    def ir_copy(iid: int):
        r = stored('ir', iid)
        return ir_dto(stored('ir', store.save_analysis('ir', None, 'COPY OF: ' + r['name'], r['description'],
                                                       r['design'])))

    @app.get('/WebAPI/ir/{iid}/exists')
    def ir_exists(iid: int, name: str = ''):
        return sum(1 for r in store.list_analyses('ir') if r['name'] == name and r['id'] != iid)

    @app.get('/WebAPI/ir/{iid}/execute/{key}')
    def ir_execute(iid: int, key):
        s = src(key)
        r = stored('ir', iid)
        expr = json.loads(r['design'] or '{}')
        design = dict(expr, name=r['name'])
        rid, work = execute('ir', iid, s, design, lambda: incidence(s, store, expr), '발생률 분석')
        background('irAnalysis', {'analysis_id': iid, 'source_key': key,
                                  'jobName': f'IR Analysis: {iid} : {key}'}, work)
        return None

    @app.delete('/WebAPI/ir/{iid}/execute/{key}')
    def ir_cancel(iid: int, key):
        return Response(status_code=204)

    @app.get('/WebAPI/ir/{iid}/info')
    def ir_infos(iid: int):
        stored('ir', iid)
        return [ir_info(r) for r in ir_latest(iid).values()]

    @app.get('/WebAPI/ir/{iid}/info/{key}')
    def ir_info_source(iid: int, key):
        r = ir_latest(iid).get(key)
        if r is None:
            raise HTTPException(404, 'no execution for this source')
        return ir_info(r)

    @app.delete('/WebAPI/ir/{iid}/info/{key}')
    def ir_info_delete(iid: int, key):
        store.delete_runs('ir', iid, src(key).source_id)
        return Response(status_code=204)

    @app.get('/WebAPI/ir/{iid}/report/{key}')
    def ir_report(iid: int, key, targetId: int = 0, outcomeId: int = 0):
        r = ir_latest(iid).get(key)
        if r is None or r['status'] != 'COMPLETED':
            raise HTTPException(404, 'no completed execution for this source')
        for x in json.loads(r['result']):
            if x['targetId'] == targetId and x['outcomeId'] == outcomeId:
                return {'summary': x['summary'], 'stratifyStats': x['stratifyStats'], 'treemapData': x['treemapData']}
        raise HTTPException(404, 'target/outcome not in this analysis')

    # -- tags, versions: not kept
    @app.post('/WebAPI/ir/{iid}/tag/{tag}')
    @app.delete('/WebAPI/ir/{iid}/tag/{tag}')
    @app.post('/WebAPI/pathway-analysis/{iid}/tag/{tag}')
    @app.delete('/WebAPI/pathway-analysis/{iid}/tag/{tag}')
    def analysis_tag(iid: int, tag: int):
        return {}

    @app.get('/WebAPI/ir/{iid}/version')
    @app.get('/WebAPI/ir/{iid}/version/')
    @app.get('/WebAPI/pathway-analysis/{iid}/version')
    @app.get('/WebAPI/pathway-analysis/{iid}/version/')
    def analysis_versions(iid: int):
        return []
