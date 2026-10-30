"""D2E cohort builder (Patient Analytics, the "Cohorts" tab) on a WebAPI source — population counts only.

The cohort screen sends a filter tree (BooleanContainer AND/OR/NOT of FilterCards; a card's attributes each carry an
OR of Expressions {operator, value}, a range or a date span being an AND of two). This module turns that tree into
one SELECT over the CDM — person level: the Basic Data card filters the person row (age = year of death or of today
minus year of birth, as D2E counts it), every other card is an EXISTS over its CDM table with all the card's
constraints on the same row, concept set constraints expand through the concept set SQL of circe.
It answers the patient count, the bar chart (axes on person attributes) and the attrition (inclusion) report.
Counts 1..MIN-1 go out as cells.MASK (shown as "<MIN"), chart bars and attrition groups below MIN are dropped.
Patient-level answers (patient lists, a patient's record, notes) are refused.
"""
import json
import os
import re

from ..circe import build_concept_set_query
from ..webapi import cells
from ..webapi.sources import q

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'static', 'pa_config.json')
CONFIG_ID = 'pa-omop'

# person attributes: config name -> SQL over the person row (p), its death (d) and concept names (gc, rc, ec)
PERSON = {
    'Age': ('num', 'YEAR(COALESCE(CAST(d.death_date AS DATE), GETDATE())) - p.year_of_birth'),
    'Gender_concept_name': ('text', "COALESCE(gc.concept_name, 'No matching concept')"),
    'raceName': ('text', "COALESCE(rc.concept_name, 'No matching concept')"),
    'ethnicityName': ('text', "COALESCE(ec.concept_name, 'No matching concept')"),
    'yearOfBirth': ('num', 'p.year_of_birth'),
    'monthOfBirth': ('num', 'p.month_of_birth'),
    'dateOfBirth': ('datetime', 'p.birth_datetime'),
    'genderconceptid': ('text', 'CAST(p.gender_concept_id AS VARCHAR(20))'),
    'raceconceptid': ('text', 'CAST(p.race_concept_id AS VARCHAR(20))'),
    'ethnicityconceptid': ('text', 'CAST(p.ethnicity_concept_id AS VARCHAR(20))'),
    'gendersourcevalue': ('text', 'p.gender_source_value'),
    'racesourcevalue': ('text', 'p.race_source_value'),
    'ethnicitysourcevalue': ('text', 'p.ethnicity_source_value'),
}

# event cards: config key -> (CDM table, {attribute: (kind, column)}).
# kinds: cs = concept set on a concept id column, name = concept name of a concept id column,
# code = concept code of a concept id column, num, text, time (date), datetime
INTERACTIONS = {
    'visit': ('visit_occurrence', {
        'visitconceptset': ('cs', 'visit_concept_id'), 'visittypeconceptset': ('cs', 'visit_type_concept_id'),
        'visit_occ_concept_name': ('name', 'visit_concept_id'),
        'startdate': ('time', 'visit_start_date'), 'enddate': ('time', 'visit_end_date')}),
    'conditionoccurrence': ('condition_occurrence', {
        'conditionconceptset': ('cs', 'condition_concept_id'),
        'conditiontypeconceptset': ('cs', 'condition_type_concept_id'),
        'conditionsourceconceptset': ('cs', 'condition_source_concept_id'),
        'conditionstatusconceptset': ('cs', 'condition_status_concept_id'),
        'condition_occ_concept_name': ('name', 'condition_concept_id'),
        'condition_source_concept_code': ('code', 'condition_source_concept_id'),
        'startdate': ('time', 'condition_start_date'), 'enddate': ('time', 'condition_end_date')}),
    'conditionera': ('condition_era', {
        'Condition_era_concept_set': ('cs', 'condition_concept_id'),
        'count': ('num', 'condition_occurrence_count'),
        'startdate': ('time', 'condition_era_start_date'), 'enddate': ('time', 'condition_era_end_date')}),
    'drugexposure': ('drug_exposure', {
        'drugconceptset': ('cs', 'drug_concept_id'), 'routeconceptset': ('cs', 'route_concept_id'),
        'drugtypeconceptset': ('cs', 'drug_type_concept_id'), 'drug_concept_name': ('name', 'drug_concept_id'),
        'dayssupply': ('num', 'days_supply'), 'refills': ('num', 'refills'), 'stopreason': ('text', 'stop_reason'),
        'startdate': ('time', 'drug_exposure_start_date'), 'enddate': ('time', 'drug_exposure_end_date'),
        'startdatetime': ('datetime', 'drug_exposure_start_datetime'),
        'enddatetime': ('datetime', 'drug_exposure_end_datetime'), 'verbatimenddate': ('time', 'verbatim_end_date')}),
    'drugera': ('drug_era', {
        'drugconceptset': ('cs', 'drug_concept_id'), 'gapdays': ('num', 'gap_days'),
        'drugexpcount': ('num', 'drug_exposure_count'),
        'startdate': ('time', 'drug_era_start_date'), 'enddate': ('time', 'drug_era_end_date')}),
    'doseera': ('dose_era', {
        'drugconceptset': ('cs', 'drug_concept_id'), 'unitconceptset': ('cs', 'unit_concept_id'),
        'dosevalue': ('num', 'dose_value'),
        'startdate': ('time', 'dose_era_start_date'), 'enddate': ('time', 'dose_era_end_date')}),
    'proc': ('procedure_occurrence', {
        'procconceptset': ('cs', 'procedure_concept_id'), 'proctypeconceptset': ('cs', 'procedure_type_concept_id'),
        'modifierconceptset': ('cs', 'modifier_concept_id'), 'procconceptname': ('name', 'procedure_concept_id'),
        'qty': ('num', 'quantity'), 'procdatetime': ('datetime', 'procedure_datetime'),
        'startdate': ('time', 'procedure_date'), 'enddate': ('time', 'procedure_end_date')}),
    'measurement': ('measurement', {
        'measurementconceptset': ('cs', 'measurement_concept_id'),
        'measurementtypeconceptset': ('cs', 'measurement_type_concept_id'),
        'valueasconceptset': ('cs', 'value_as_concept_id'), 'unitconceptset': ('cs', 'unit_concept_id'),
        'meas_concept_name': ('name', 'measurement_concept_id'), 'numval': ('num', 'value_as_number'),
        'startdate': ('time', 'measurement_date'), 'enddate': ('time', 'measurement_date')}),
    'observation': ('observation', {
        'obsconceptset': ('cs', 'observation_concept_id'),
        'observationtypeconceptset': ('cs', 'observation_type_concept_id'),
        'valueasconceptset': ('cs', 'value_as_concept_id'), 'qualifierconceptset': ('cs', 'qualifier_concept_id'),
        'unitconceptset': ('cs', 'unit_concept_id'), 'obs_concept_name': ('name', 'observation_concept_id'),
        'numval': ('num', 'value_as_number'), 'verbatimtext': ('text', 'value_as_string'),
        'obsdate': ('time', 'observation_date'), 'startdate': ('time', 'observation_date'),
        'enddate': ('time', 'observation_date'), 'obsdatetime': ('datetime', 'observation_datetime')}),
    'deviceexposure': ('device_exposure', {
        'deviceconceptset': ('cs', 'device_concept_id'), 'devicetypeconceptset': ('cs', 'device_type_concept_id'),
        'device_concept_name': ('name', 'device_concept_id'),
        'startdate': ('time', 'device_exposure_start_date'), 'enddate': ('time', 'device_exposure_end_date')}),
    'death': ('death', {
        'deathtypeconceptset': ('cs', 'death_type_concept_id'),
        'death_type_concept_name': ('name', 'death_type_concept_id'), 'deathdatetime': ('datetime', 'death_datetime'),
        'deathdate': ('time', 'death_date'), 'startdate': ('time', 'death_date'), 'enddate': ('time', 'death_date')}),
    'obsperiod': ('observation_period', {
        'periodtypeconceptset': ('cs', 'period_type_concept_id'),
        'startdate': ('time', 'observation_period_start_date'), 'enddate': ('time', 'observation_period_end_date')}),
    'specimen': ('specimen', {
        'specimenconceptset': ('cs', 'specimen_concept_id'), 'specimentypeconceptset': ('cs', 'specimen_type_concept_id'),
        'anatomicsiteconceptset': ('cs', 'anatomic_site_concept_id'),
        'diseasestatusconceptset': ('cs', 'disease_status_concept_id'), 'unitconceptset': ('cs', 'unit_concept_id'),
        'specimen_concept_name': ('name', 'specimen_concept_id'), 'quantity': ('num', 'quantity'),
        'specimendate': ('time', 'specimen_date'), 'specimendatetime': ('datetime', 'specimen_datetime')}),
    'ppperiod': ('payer_plan_period', {
        'startdate': ('time', 'payer_plan_period_start_date'), 'enddate': ('time', 'payer_plan_period_end_date')}),
}

OPS = {'=': '=', '!=': '<>', '<>': '<>', '<': '<', '<=': '<=', '>': '>', '>=': '>='}
REFUSED = 'Patient-level data is not available here: counts and charts only.'


class PAError(ValueError):
    pass


def frontend_config(tables=None):
    """The cohort screen's configuration (D2E's OMOP default) cut to what this module answers: no identifiers,
    only the event cards mapped above (and, given tables, only those whose CDM table has rows)."""
    with open(CONFIG_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    patient = cfg['patient']
    patient['attributes'] = {k: v for k, v in patient['attributes'].items() if k in PERSON or k == 'pcount'}
    inter = {}
    for k, v in patient['interactions'].items():
        if k not in INTERACTIONS or (tables is not None and INTERACTIONS[k][0] not in tables):
            continue
        v['attributes'] = {a: b for a, b in v['attributes'].items() if a in INTERACTIONS[k][1]}
        inter[k] = v
    patient['interactions'] = inter
    return [{'meta': {'configId': CONFIG_ID, 'configVersion': 'A', 'configStatus': 'A', 'configName': 'OMOP CDM',
                      'configType': 'HC/MRI/PA', 'dependentConfig': {'configId': CONFIG_ID, 'configVersion': 'A'}},
             'config': cfg}]


class Translator:
    def __init__(self, source, concept_set_items):
        """concept_set_items(id) -> the concept set's items (WebAPI shape) or None."""
        self.s = source
        self.items = concept_set_items
        self.cards = None

    # ---- SQL pieces -------------------------------------------------------------------------------------------
    def base(self):
        """One row per person with its Basic Data attributes."""
        cols = ',\n  '.join(f'{expr} AS "{name}"' for name, (_, expr) in PERSON.items())
        return (f'SELECT p.person_id,\n  {cols}\nFROM @cdm.person p\n'
                'LEFT JOIN (SELECT person_id, MAX(death_date) AS death_date FROM @cdm.death GROUP BY person_id) d '
                'ON d.person_id = p.person_id\n'
                'LEFT JOIN @vocab.concept gc ON gc.concept_id = p.gender_concept_id\n'
                'LEFT JOIN @vocab.concept rc ON rc.concept_id = p.race_concept_id\n'
                'LEFT JOIN @vocab.concept ec ON ec.concept_id = p.ethnicity_concept_id')

    def concept_set_sql(self, value):
        try:
            cid = int(str(value).split(':')[-1])
        except ValueError:
            raise PAError(f'unknown concept set {value}')
        items = self.items(cid)
        if items is None:
            raise PAError(f'unknown concept set {value}')
        expr = {'items': [{'concept': {'CONCEPT_ID': int(i['conceptId'])}, 'isExcluded': bool(i['isExcluded']),
                           'includeDescendants': bool(i['includeDescendants']),
                           'includeMapped': bool(i['includeMapped'])} for i in items]}
        return build_concept_set_query(expr).replace('@vocabulary_database_schema', '@vocab')

    def value_sql(self, kind, v):
        if kind == 'num':
            try:
                return repr(float(v)) if not float(v).is_integer() else str(int(float(v)))
            except (TypeError, ValueError):
                raise PAError(f'not a number: {v!r}')
        if kind in ('time', 'datetime'):
            s = str(v)[:19].replace('T', ' ')
            if not re.match(r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$', s):
                raise PAError(f'not a date: {v!r}')
            y, m, d = (int(x) for x in s[:10].split('-'))
            return f'DATEFROMPARTS({y}, {m}, {d})'     # date precision also for datetime attributes
        return q(v)

    def expression(self, kind, col, e):
        """One constraint {operator, value} on column col (an event row column or a person attribute)."""
        if e.get('type') == 'BooleanContainer':
            parts = [self.expression(kind, col, x) for x in e.get('content') or []]
            if not parts:
                return '1 = 1'
            return '(' + f' {"OR" if e.get("op") == "OR" else "AND"} '.join(parts) + ')'
        op = OPS.get(str(e.get('operator', '=')).strip())
        if op is None:
            raise PAError(f'unsupported operator {e.get("operator")!r}')
        v = e.get('value')
        if kind == 'cs':
            sub = self.concept_set_sql(v)
            return f'{col} {"NOT IN" if op == "<>" else "IN"} ({sub})'
        if kind in ('name', 'code'):
            field = 'concept_name' if kind == 'name' else 'concept_code'
            return (f'{col} {"NOT IN" if op == "<>" else "IN"} '
                    f'(SELECT concept_id FROM @vocab.concept WHERE UPPER({field}) = UPPER({q(v)}))')
        if kind == 'text' and op in ('=', '<>'):
            return f'UPPER({col}) {op} UPPER({q(v)})'          # D2E compares text case-insensitively
        return f'{col} {op} {self.value_sql(kind, v)}'

    def constraints(self, kind, col, cons):
        content = (cons or {}).get('content') or []
        if not content:
            return None
        return '(' + ' OR '.join(self.expression(kind, col, e) for e in content) + ')'

    def card(self, c, root=None):
        """A FilterCard -> a condition on the person row (pt)."""
        if c.get('inactive'):
            return '1 = 1'
        path = c.get('configPath') or ''
        attrs = ((c.get('attributes') or {}).get('content')) or []
        if path == 'patient':
            parts = []
            for a in attrs:
                name = a.get('configPath', '').rsplit('.', 1)[-1]
                if name not in PERSON:
                    if (a.get('constraints') or {}).get('content'):
                        raise PAError(f'unsupported attribute {name}')
                    continue
                w = self.constraints(PERSON[name][0], f'pt."{name}"', a.get('constraints'))
                if w:
                    parts.append(w)
            return ' AND '.join(parts) if parts else '1 = 1'
        table, parts = self.event(c, 'e')
        if c.get('advanceTimeFilter'):
            parts.append(self.time_filter(c, 'e', root or c))
        where = ''.join(f'\n    AND {w}' for w in parts)
        return f'EXISTS (SELECT 1 FROM @cdm.{table} e WHERE e.person_id = pt.person_id{where})'

    def dates(self, card):
        """An event card's start and end date columns."""
        amap = INTERACTIONS[card['configPath'].rsplit('.', 1)[-1]][1]
        start = (amap.get('startdate') or amap.get('deathdate') or amap.get('specimendate') or (None, None))[1]
        end = (amap.get('enddate') or (None, start))[1]
        if not start:
            raise PAError(f'{card.get("name")} has no dates for a time relation')
        return {'startdate': start, 'enddate': end or start}

    def time_filter(self, c, alias, root):
        """advanceTimeFilter.request -> a condition on this card's row (alias): for each related card, one of its
        rows (another row when it is the same table) with DAYS(this date -> that date) meeting the operators."""
        mine = self.dates(c)
        table = INTERACTIONS[c['configPath'].rsplit('.', 1)[-1]][0]

        def related(item, n):
            other = self.find_card(self.cards, item.get('value') or '')
            if other is None:
                raise PAError(f'time relation to a missing card {item.get("value")}')
            o = f'{alias}t{n}'
            otab, oparts = self.event(other, o)
            theirs = self.dates(other)
            conds = [f'{o}.person_id = {alias}.person_id'] + oparts
            if otab == table and otab != 'death':
                conds.append(f'{o}.{otab}_id <> {alias}.{table}_id')
            for f in item.get('filter') or []:
                d = f'DATEDIFF(day, {alias}.{mine[f.get("this", "startdate")]}, {o}.{theirs[f.get("other", "startdate")]})'
                for x in f.get('and') or []:
                    op = OPS.get(str(x.get('op')))
                    if op is None:
                        raise PAError(f'unsupported operator {x.get("op")!r}')
                    conds.append(f'{d} {op} {int(x.get("value", 0))}')
            return f'EXISTS (SELECT 1 FROM @cdm.{otab} {o} WHERE ' + ' AND '.join(conds) + ')'

        n = [0]

        def item_sql(item):
            n[0] += 1
            if 'or' in item:
                return '(' + ' OR '.join(item_sql(x) for x in item['or']) + ')'
            if 'and' in item:
                return '(' + ' AND '.join(item_sql(x) for x in item['and']) + ')'
            return related(item, n[0])
        req = (c.get('advanceTimeFilter') or {}).get('request') or []
        parts = [item_sql(x) for x in req]
        return '(' + ' AND '.join(parts) + ')' if parts else '1 = 1'

    def event(self, c, alias):
        """An event card -> its CDM table and its constraints on one row of it (as alias)."""
        m = re.match(r'^patient\.interactions\.([^.]+)$', c.get('configPath') or '')
        if not m or m.group(1) not in INTERACTIONS:
            raise PAError(f'unsupported filter card {c.get("configPath")}')
        table, amap = INTERACTIONS[m.group(1)]
        parts = []
        for a in ((c.get('attributes') or {}).get('content')) or []:
            name = a.get('configPath', '').rsplit('.', 1)[-1]
            if name not in amap:
                if (a.get('constraints') or {}).get('content'):
                    raise PAError(f'unsupported attribute {name}')
                continue
            kind, col = amap[name]
            w = self.constraints(kind, f'{alias}.{col}', a.get('constraints'))
            if w:
                parts.append(w)
        return table, parts

    @staticmethod
    def find_card(node, instance_id):
        if node.get('type') == 'FilterCard':
            return node if node.get('instanceID') == instance_id else None
        for x in node.get('content') or []:
            f = Translator.find_card(x, instance_id)
            if f:
                return f
        return None

    def tree(self, node):
        t = node.get('type')
        if t == 'FilterCard':
            return self.card(node)
        if t != 'BooleanContainer' and 'content' not in node:
            raise PAError(f'unexpected node {t}')
        parts = [self.tree(x) for x in node.get('content') or []]
        op = node.get('op', 'AND')
        if op == 'NOT':
            return 'NOT (' + (' AND '.join(parts) if parts else '1 = 0') + ')'
        if not parts:
            return '1 = 1'
        return '(' + f' {"OR" if op == "OR" else "AND"} '.join(parts) + ')'

    def run(self, sql):
        return self.s.query_dicts(sql, cdm=self.s.cdm_schema, vocab=self.s.vocab_schema)

    # ---- answers ----------------------------------------------------------------------------------------------
    def patient_count(self, cards):
        self.cards = cards                        # the whole request, for cards that refer to other cards
        n = self.run(f'WITH pt AS (\n{self.base()}\n)\nSELECT COUNT(*) AS n FROM pt WHERE {self.tree(cards)}')[0]['n']
        return {'data': [{'patient.attributes.pcount': cells.mask(int(n))}]}

    def axis(self, cards, aid, binsize, config, joins):
        """A chart axis -> (SQL expression, category). Event attributes join their card's table (all the card's
        constraints on that row), so a person counts once under every value their matching events have."""
        name = aid.rsplit('.', 1)[-1]
        if aid.startswith('patient.attributes.'):
            if name not in PERSON:
                raise PAError(f'unsupported chart axis {aid}')
            kind, label = PERSON[name][0], (config['patient']['attributes'].get(name) or {}).get('name', name)
            col = f'pt."{name}"'
        else:
            m = re.match(r'^(patient\.interactions\.([^.]+)\.\d+)\.attributes\.([^.]+)$', aid)
            if not m or m.group(2) not in INTERACTIONS or m.group(3) not in INTERACTIONS[m.group(2)][1]:
                raise PAError(f'unsupported chart axis {aid}')
            card = self.find_card(cards, m.group(1))
            if card is None:
                raise PAError(f'the chart axis {aid} has no filter card')
            alias = joins.setdefault(m.group(1), (f'x{len(joins)}', card))[0]
            kind, c = INTERACTIONS[m.group(2)][1][m.group(3)]
            label = ((config['patient']['interactions'].get(m.group(2)) or {}).get('attributes', {})
                     .get(m.group(3)) or {}).get('name', m.group(3))
            if kind == 'cs':
                raise PAError('a concept set cannot be a chart axis')
            if kind in ('name', 'code'):
                field = 'concept_name' if kind == 'name' else 'concept_code'
                col = (f"COALESCE((SELECT k.{field} FROM @vocab.concept k WHERE k.concept_id = {alias}.{c}), "
                       f"'No matching concept')")
                kind = 'text'
            else:
                col = f'{alias}.{c}'
        cat = {'id': aid, 'value': '{%s}' % aid, 'name': label, 'type': kind, 'axis': 1, 'order': 'ASC'}
        if kind == 'num' and binsize not in (None, 'n/a', ''):
            col = f'FLOOR({col} / {float(binsize)}) * {float(binsize)}'
            cat['binsize'] = binsize
        elif kind in ('time', 'datetime'):
            col = f'YEAR({col})'                      # dates are charted by year
            cat['type'] = 'num'
        return col, cat

    def chart_from(self, joins):
        """FROM clause of a chart: the person rows and, for event axes, their cards' matching event rows."""
        sql = 'pt'
        for alias, card in joins.values():
            table, parts = self.event(card, alias)
            sql += (f'\nJOIN @cdm.{table} {alias} ON {alias}.person_id = pt.person_id'
                    + ''.join(f' AND {w}' for w in parts))
        return sql

    def bar_chart(self, cards, axes, config):
        self.cards = cards
        cats, dims, joins = [], [], {}
        for ax in axes:
            aid = ax.get('attributeId')
            if not aid or aid == 'n/a' or not str(ax.get('categoryId', '')).startswith('x'):
                continue
            col, cat = self.axis(cards, aid, ax.get('binsize'), config, joins)
            cats.append(cat)
            dims.append((aid, col))
        where = self.tree(cards)
        sel = ''.join(f'{col} AS "{aid}", ' for aid, col in dims)
        group = (' GROUP BY ' + ', '.join(col for _, col in dims)) if dims else ''
        src = self.chart_from(joins)
        rows = self.run(f'WITH pt AS (\n{self.base()}\n)\nSELECT {sel}COUNT(DISTINCT pt.person_id) AS n '
                        f'FROM {src} WHERE {where}{group}')
        if joins:      # a person may sit under several values: the total is counted on its own
            total = int(self.run(f'WITH pt AS (\n{self.base()}\n)\nSELECT COUNT(DISTINCT pt.person_id) AS n '
                                 f'FROM {src} WHERE {where}')[0]['n'])
        else:
            total = sum(int(r['n']) for r in rows)
        data = []
        for r in sorted(rows, key=lambda r: tuple('' if r[a] is None else r[a] for a, _ in dims)):
            n = int(r['n'])
            if cells.small(n):
                continue
            row = {'totalpcount': cells.mask(total), 'patient.attributes.pcount': n}
            for aid, _ in dims:
                v = r[aid]
                row[aid] = int(v) if isinstance(v, float) and v.is_integer() else v
            data.append(row)
        if not dims and not data:
            data = [{'totalpcount': cells.mask(total), 'patient.attributes.pcount': cells.mask(total)}]
        return {'data': data,
                'measures': [{'id': 'patient.attributes.pcount', 'value': '{patient.attributes.pcount}',
                              'name': 'Patient Count', 'group': 1, 'type': 'num'}],
                'categories': cats or [{'id': 'dummy_category', 'value': '{dummy_category}', 'axis': 1}],
                'totalPatientCount': cells.mask(total),
                'postProcessingConfig': {'fillMissingValuesEnabled': True, 'NOVALUE': 'NoValue',
                                         'shouldFormatBinningLabels': True}}

    def rules(self, cards):
        """The attrition rules, in order: each constrained Basic Data attribute, then every other card
        (an excluded card counts as satisfied by those who do not have it)."""
        out = []

        def walk(node, excluded):
            if node.get('type') == 'FilterCard':
                if node.get('inactive'):
                    return
                if node.get('configPath') == 'patient':
                    for a in (node.get('attributes') or {}).get('content') or []:
                        if (a.get('constraints') or {}).get('content'):
                            name = a['configPath'].rsplit('.', 1)[-1]
                            one = dict(node, attributes={'content': [a], 'type': 'BooleanContainer', 'op': 'AND'})
                            out.append((name, False, self.card(one)))
                    return
                w = self.card(node)
                out.append((node.get('name') or node.get('configPath'), excluded,
                            f'NOT ({w})' if excluded else w))
                return
            for x in node.get('content') or []:
                walk(x, excluded or node.get('op') == 'NOT')
        walk(cards, False)
        return out

    def inclusion_report(self, cards):
        self.cards = cards
        rules = self.rules(cards)
        flags = ''.join(f', CASE WHEN {w} THEN 1 ELSE 0 END AS r{i}' for i, (_, _, w) in enumerate(rules))
        names = ''.join(f', r{i}' for i in range(len(rules)))
        sql = (f'WITH pt AS (\n{self.base()}\n), f AS (SELECT CASE WHEN {self.tree(cards)} THEN 1 ELSE 0 END AS fin'
               f'{flags} FROM pt)\nSELECT fin{names}, COUNT(*) AS n FROM f GROUP BY fin{names}')
        rows = self.run(sql)
        base = sum(int(r['n']) for r in rows)
        final = sum(int(r['n']) for r in rows if int(r['fin']) == 1)

        def pct(n, d):
            if cells.small(n):
                return f'{cells.MASK}%'
            return f'{100.0 * n / d:.2f}%' if d else '0.00%'
        stats = []
        for i, (name, excl, _) in enumerate(rules):
            sat = sum(int(r['n']) for r in rows if int(r[f'r{i}']) == 1)
            # excluded by this rule alone: fails it, meets every other rule
            only = sum(int(r['n']) for r in rows if int(r[f'r{i}']) == 0
                       and all(int(r[f'r{j}']) == 1 for j in range(len(rules)) if j != i))
            stats.append({'id': i, 'name': name, 'isExclude': excl, 'percentExcluded': pct(only, base),
                          'percentSatisfying': pct(sat, base), 'countSatisfying': cells.mask(sat)})
        # the attrition plot: persons left after rules 0..i, in order
        attrition = []
        for i, (name, excl, _) in enumerate(rules):
            cum = sum(int(r['n']) for r in rows if all(int(r[f'r{j}']) == 1 for j in range(i + 1)))
            attrition.append({'id': i, 'name': name, 'isExclude': excl, 'cumulativeCountSatisfying': cells.mask(cum)})
        groups = {}
        for r in rows:
            bits = ''.join(str(int(r[f'r{i}'])) for i in range(len(rules)))
            groups[bits] = groups.get(bits, 0) + int(r['n'])
        tree = {'name': 'Everyone', 'children': []}
        for k in range(len(rules) + 1):
            kids = [{'name': b, 'size': n} for b, n in sorted(groups.items()) if b.count('1') == k and not cells.small(n)]
            if kids:
                tree['children'].append({'name': f'Group {k}', 'children': kids})
        return {'summary': {'baseCount': cells.mask(base), 'finalCount': cells.mask(final), 'lostCount': 0,
                            'percentMatched': pct(final, base)},
                'inclusionRuleStats': stats, 'attritionStats': attrition, 'treemapData': tree}
