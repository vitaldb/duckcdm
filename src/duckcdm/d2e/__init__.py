"""D2E (Data2Evidence) portal on DuckCDM — the D2E UI with the WebAPI of this server, no trex.

install(app) adds, in front of the ATLAS routes of create_app():
  - the D2E portal and its Concepts plugin (static, from Data2Evidence 0.18),
  - the D2E service endpoints the portal calls (system-portal, usermgmt, jobplugins, terminology), answered
    from the WebAPI sources and their Achilles reports; /d2e/d2e-webapi/* is the WebAPI itself,
  - D2E's own cohort builder (the Cohorts tab, analytics-svc): counts, bar chart and attrition through
    duckcdm.d2e.pa, which turns the screen's filter tree into one SELECT; patient-level answers are refused,
  - a stand-in OIDC provider: the portal logs in through it and gets tokens for the viewer the gateway names
    (X-Auth-User-Id, as for the remote source). The tokens carry no authority — no endpoint reads them.
The app may run under a path prefix (an app platform's /apps/runtime/<name>/): the page works the prefix out
from its own URL (window.__D2E_BASE__) and the few absolute paths of the D2E build are rewritten to use it.
Patient-level views are not part of it; counts go through the same small-cell suppression as the WebAPI.
"""
import base64
import datetime
import functools
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import time
import urllib.parse
import zlib

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response

from ..webapi import cells
from . import pa
from .bookmarks import BookmarkError, Bookmarks
from ..webapi.app import STATIC as ATLAS_STATIC, concept_json, search_filters
from ..webapi.sources import q, sql_resource

STATIC = os.path.join(os.path.dirname(__file__), 'static')
PORTAL = os.path.join(STATIC, 'portal')
CONCEPT_SETS = os.path.join(STATIC, 'concept-sets')
MRI = os.path.join(STATIC, 'mri')
CLIENT_ID = 'd2e-portal'
_B = '(window.__D2E_BASE__||"")'

# absolute paths in the D2E build -> the same path under the page's prefix
REWRITES = {
    'portal': [('n.p="/d2e/portal/"', f'n.p={_B}+"/d2e/portal/"'),
               ('PUBLIC_URL:"/d2e/portal"', f'PUBLIC_URL:{_B}+"/d2e/portal"'),
               ('basename:"/d2e/portal"', f'basename:{_B}+"/d2e/portal"'),
               ('.concat(window.location.origin,"/d2e/portal")', f'.concat(window.location.origin+{_B},"/d2e/portal")'),
               ('.concat(window.location.origin,"/atlas/")', f'.concat(window.location.origin+{_B},"/atlas/")'),
               # no Account page (the platform signs the viewer in): drop the button and the header tab
               ('return(0,f.jsx)(ne.$n,{containerClassName:"account-button",variant:"outlined",text:a,onClick:s})',
                'return null'),
               ('return(0,i.jsx)("li",{className:"".concat(d," header__menu-item--pin-right"),children:(0,i.jsx)(s.Link,'
                '{to:c(),children:n(l.ACCOUNT_TAB__LINK)})})', 'return null')],
    'concept-sets': [('="/resources/concept-sets"', f'={_B}+"/resources/concept-sets"')],
    'css': [('url(/d2e/portal/static/', 'url(../')],  # the portal's stylesheets live in static/css/
}

# D2E feature flags: what the portal offers. Notebooks and analyses are not here.
FEATURES = [('atlas', 'Atlas', True), ('conceptRecordCounts', 'Concept record counts', True),
            ('conceptSets', 'Concept sets', True), ('cohort', 'Cohort', True), ('notebook', 'Notebook', False),
            ('strategus', 'Strategus', False), ('wizards', 'Wizards', False), ('shinyLive', 'Dashboards', False),
            ('pythia', 'Pythia', False), ('datasetFilter', 'Dataset filter', False),
            ('datasetSearch', 'Dataset search', False), ('fhirServer', 'Fhir server', False),
            ('mappingSuggestion', 'Data mapping AI suggestion', False), ('adminOnlySharing', 'Admin only sharing', False),
            ('aiAssistant', 'AI assistant', False), ('sibyl', 'Sibyl', False), ('dataExploration', 'Data exploration', False),
            ('d2eLogs', 'Logs', False)]

# the dataset card's "Entity Count Distribution" (labels as D2E writes them)
ENTITY_TABLES = [('Observation Period Count', 'observation_period'), ('Death Count', 'death'),
                 ('Visit Occurrence Count', 'visit_occurrence'), ('Visit Detail Count', 'visit_detail'),
                 ('Condition Occurrence Count', 'condition_occurrence'), ('Drug Exposure Count', 'drug_exposure'),
                 ('Procedure Occurrence Count', 'procedure_occurrence'), ('Device Exposure Count', 'device_exposure'),
                 ('Measurement Count', 'measurement'), ('Observation Count', 'observation'), ('Note Count', 'note'),
                 ('Specimen Count', 'specimen')]

# Data characterization report -> Achilles report of the WebAPI (Reports method or treemap domain)
DC_REPORTS = {'dashboard': 'dashboard', 'person': 'person', 'datadensity': 'data_density', 'death': 'death',
              'observationPeriod': 'observation_period'}

def _b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def _unb64(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def _iso(ts=None):
    return datetime.datetime.fromtimestamp(ts or time.time(), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def _upper(v):
    """WebAPI report JSON -> D2E data characterization JSON: the same report, row fields in upper case
    (conceptPath -> CONCEPTPATH); the report's own section names (summary, gender, ...) stay."""
    def rows(x):
        if isinstance(x, list):
            return [{k.upper(): r for k, r in row.items()} if isinstance(row, dict) else row for row in x]
        return x
    if isinstance(v, dict):
        return {k: rows(x) for k, x in v.items()}
    return rows(v)


@functools.lru_cache(maxsize=None)
def _static_text(path, kind):
    with open(path, encoding='utf-8') as f:
        t = f.read()
    for old, new in REWRITES.get(kind, ()):
        t = t.replace(old, new)
    return t


def _serve(root, rel, kind):
    path = os.path.normpath(os.path.join(root, rel))
    if not path.startswith(root + os.sep) or not os.path.isfile(path):
        return None
    if path.endswith('.js'):
        return Response(_static_text(path, kind), media_type='application/javascript')
    if path.endswith('.css'):
        return Response(_static_text(path, 'css'), media_type='text/css')
    return FileResponse(path, media_type=mimetypes.guess_type(path)[0])


def install(app, title='CDM D2E', description=None, small_cell_label=None):
    sources = app.state.sources
    reports = app.state.reports
    secret = secrets.token_bytes(32)
    local_user = os.environ.get('D2E_LOCAL_USER', 'local')
    n_before = len(app.router.routes)

    def viewer(request):
        h = request.headers
        return h.get('x-auth-user-id') or h.get('user-id') or h.get('x-auth-subject') or local_user

    def roles():
        return (['role.viewer', 'cohort reader', 'cohort creator', 'concept set creator']
                + [f'role.researcher.{k}' for k in sources])

    def jwt(claims):
        head = _b64(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
        body = _b64(json.dumps(claims).encode())
        sig = _b64(hmac.new(secret, f'{head}.{body}'.encode(), hashlib.sha256).digest())
        return f'{head}.{body}.{sig}'

    def src(key):
        if key not in sources:
            raise HTTPException(404, f'dataset {key} not found')
        return sources[key]

    @functools.lru_cache(maxsize=None)
    def person_count(key):
        r = reports[key]
        if not r.ready():
            return None
        for row in r.dashboard().get('summary', []):
            if (row.get('attributeName') or '').lower() == 'number of persons':
                return row.get('attributeValue')
        return None

    @functools.lru_cache(maxsize=None)
    def release_date(key):
        s = sources[key]
        try:
            rows = s.query_dicts('SELECT MAX(cdm_release_date) AS d FROM @cdm.cdm_source', cdm=s.cdm_schema)
            d = rows[0]['d'] if rows else None
        except Exception:
            return None
        return str(d)[:10] if d else None

    @functools.lru_cache(maxsize=None)
    def table_counts(key):
        """Rows per CDM table (one COUNT(*) per table, once): the dataset card's chart, and which cohort
        builder cards are offered (a table that is missing or empty gives 0)."""
        s = sources[key]
        out = {}
        for table in sorted({t for _, t in ENTITY_TABLES} | {t for t, _ in pa.INTERACTIONS.values()}):
            try:
                out[table] = int(s.query_dicts(f'SELECT COUNT(*) AS n FROM @cdm.{table}', cdm=s.cdm_schema)[0]['n'])
            except Exception:
                out[table] = 0
        return out

    def entity_counts(key):
        n = table_counts(key)
        return {label: str(n.get(table, 0)) for label, table in ENTITY_TABLES}

    def dataset(key):
        s = src(key)
        n = person_count(key)
        d = release_date(key)
        ec = entity_counts(key)
        attrs = [('version', 'Version', 'STRING', '5.4', True),
                 ('patient_count', 'Patient Count', 'NUMBER', n, n is not None),
                 ('created_date', 'Created date', 'TIMESTAMP', d, d is not None),
                 ('updated_date', 'Updated date', 'TIMESTAMP', d, d is not None),
                 ('entity_count', 'Entity Count', 'NUMBER', sum(int(v) for v in ec.values()), False),
                 ('entity_count_distribution', 'Entity Count Distribution', 'STRING', json.dumps(ec), False)]
        return {
            'id': key, 'tokenStudyCode': key, 'databaseCode': key, 'databaseName': s.name, 'dialect': 'postgres',
            'cacheId': key, 'schemaName': s.cdm_schema, 'vocabSchemaName': s.vocab_schema,
            'resultsSchemaName': s.results_schema, 'type': 'webapi', 'dataModel': 'omop5-4',
            'plugin': 'omop_cdm_plugin', 'paConfigId': pa.CONFIG_ID, 'sourceStudyId': None, 'flowParameters': None,
            'tags': [], 'dashboards': [],
            'attributes': [{'attributeId': a, 'value': None if v is None else str(v),
                            'attributeConfig': {'name': nm, 'dataType': dt, 'isDisplayed': shown}}
                           for a, nm, dt, v, shown in attrs],
            'tenant': {'id': 'tenant', 'name': 'Tenant', 'system': 'Research System'},
            'studyDetail': {'name': s.name, 'description': description or s.name, 'summary': description or s.name,
                            'showRequestAccess': False},
        }

    # ---- page --------------------------------------------------------------------
    @app.get('/healthz')
    def healthz():
        return Response('ok', media_type='text/plain')

    @app.get('/')
    def root():
        return RedirectResponse('d2e/portal/', status_code=302)

    @app.get('/d2e/portal/env.js')
    def env_js():
        plugins = {'researcher': [
            {'type': 'app', 'visible': True, 'autoMount': True, 'featureFlag': 'conceptSets', 'defaultEnabled': True,
             'name': 'Concepts', 'nameI18nKey': 'UI_PLUGIN_CONCEPTS', 'route': 'concepts',
             'pluginPath': '@BASE@/resources/concept-sets/lifecycles.js', 'requiredRoles': ['RESEARCHER']},
            {'type': 'app', 'visible': True, 'autoMount': False, 'featureFlag': 'cohort', 'defaultEnabled': True,
             'name': 'Cohorts', 'nameI18nKey': 'UI_PLUGIN_COHORTS', 'route': 'cohort',
             'pluginPath': '@BASE@/mri/lifecycles.js', 'requiredRoles': ['RESEARCHER']}],
            'etl': [], 'setup': [], 'systemadmin': []}
        js = """(function(){
var L=location.pathname,I=L.lastIndexOf('/d2e/portal'),B=(I>=0?L.slice(0,I):L).replace(/\\/$/,''),O=location.origin;
window.__D2E_BASE__=B;
var P=['/d2e/','/resources/','/atlas','/oidc','/WebAPI'];
function fix(u){if(typeof u==='string'&&B&&u.charAt(0)==='/'&&u.indexOf(B+'/')!==0){for(var i=0;i<P.length;i++)if(u.indexOf(P[i])===0)return B+u;}return u;}
var f=window.fetch;window.fetch=function(u,o){return f.call(this,typeof u==='string'?fix(u):u,o);};
var x=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){arguments[1]=fix(u);return x.apply(this,arguments);};
var oidc={client_id:%(client)s,redirect_uri:O+B+'/d2e/portal/login-callback',authority:O+B+'/',
 authority_configuration:{issuer:O+B+'/oidc',authorization_endpoint:O+B+'/oidc/auth',token_endpoint:O+B+'/d2e/oauth/token',
 end_session_endpoint:O+B+'/oidc/session/end?redirect='+encodeURIComponent(O+B+'/d2e/portal')},
 scope:'openid offline_access profile email',refresh_time_before_tokens_expiration_in_second:180};
window.ENV_DATA={PUBLIC_URL:B+'/d2e/portal',REACT_APP_LOCALE:'',GIT_COMMIT:'',REACT_APP_IDP_RELYING_PARTY:'',
 REACT_APP_IDP_REQUIRED_CLAIM:'thirdPartyToken',REACT_APP_DN_BASE_URL:O+B+'/',REACT_APP_CURRENT_SYSTEM:%(title)s,
 REACT_APP_IDP_SUBJECT_PROP:'sub',REACT_APP_IDP_NAME_PROP:'username',REACT_APP_IDP_OIDC_CONFIG:JSON.stringify(oidc),
 REACT_APP_DB_CREDENTIALS_PUBLIC_KEYS:'{}',REACT_APP_PLUGINS:%(plugins)s.split('@BASE@').join(B),
 REACT_APP_MRI_CONFIG_NAME:'',REACT_APP_LOG_DISCLAIMER:'',REACT_APP_USE_PUBLIC_WEBAPI_PROXY:'false',
 REACT_APP_PUBLIC_WEBAPI_PROXY_URL:'',REACT_APP_PUBLIC_WEBAPI_DATASOURCE:''};
})();""" % {'client': json.dumps(CLIENT_ID), 'title': json.dumps(title), 'plugins': json.dumps(json.dumps(plugins))}
        return Response(js, media_type='application/javascript', headers={'Cache-Control': 'no-cache'})

    @functools.lru_cache(maxsize=1)
    def index_html():
        with open(os.path.join(PORTAL, 'index.html'), encoding='utf-8') as f:
            t = f.read()
        scripts = re.findall(r'<script defer="defer" src="([^"]+)"></script>', t)
        styles = re.findall(r'<link href="([^"]+\.css)" rel="stylesheet">', t)
        css = ''.join(f"document.write('<link rel=\"stylesheet\" href=\"'+B+'{s}\">');" for s in styles)
        js = ''.join(f"document.write('<script src=\"'+B+'{s}\"><\\/script>');" for s in scripts)
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8"/>'
                '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
                f'<title>{title}</title><script>var L=location.pathname,I=L.lastIndexOf("/d2e/portal"),B=(I>=0?L.slice(0,I):L).replace(/\\/$/,"");'
                "document.write('<base href=\"'+B+'/d2e/portal\"/><link rel=\"icon\" href=\"'+B+'/d2e/portal/assets/favicon.ico\"/>');"
                "document.write('<script src=\"'+B+'/d2e/portal/env.js\"><\\/script><script src=\"'+B+'/d2e/portal/cells.js\"><\\/script>');"
                f'{css}</script></head><body><noscript>You need to enable JavaScript to run this app.</noscript>'
                f'<div id="root"></div><script>{js}</script></body></html>')

    @app.get('/d2e/portal/cells.js')
    def portal_cells():
        return Response(cells.page_js(), media_type='application/javascript', headers={'Cache-Control': 'no-cache'})

    @app.get('/d2e/portal')
    @app.get('/d2e/portal/')
    def portal_index():
        return Response(index_html(), media_type='text/html', headers={'Cache-Control': 'no-cache'})

    @app.get('/d2e/portal/{rel:path}')
    def portal_file(rel: str):
        r = _serve(PORTAL, rel, 'portal')
        if r is not None:
            return r
        if re.search(r'\.\w{1,5}$', rel):
            raise HTTPException(404)
        return Response(index_html(), media_type='text/html', headers={'Cache-Control': 'no-cache'})

    @app.get('/resources/concept-sets/{rel:path}')
    def concept_sets_file(rel: str):
        r = _serve(CONCEPT_SETS, rel, 'concept-sets')
        if r is None:
            raise HTTPException(404)
        return r

    @app.get('/mri/{rel:path}')
    def mri_file(rel: str):
        r = _serve(MRI, rel, 'mri')
        if r is None:
            raise HTTPException(404)
        return r

    @app.get('/atlas')
    def atlas_root():
        return RedirectResponse('atlas/', status_code=302)

    @app.get('/atlas/config-local.json')
    def atlas_config():
        return {'api': {'url': '../WebAPI'}, 'userAuthenticationEnabled': False, 'enableSkipLogin': True,
                'enablePermissionManagement': False, 'enablePersonCount': False, 'enableTaggingSection': False,
                'authProviders': []}

    @app.get('/atlas/cells.js')
    def atlas_cells():
        return Response(cells.page_js(), media_type='application/javascript', headers={'Cache-Control': 'no-cache'})

    @app.get('/atlas/{rel:path}')
    def atlas_file(rel: str):
        path = os.path.normpath(os.path.join(ATLAS_STATIC, rel or 'index.html'))
        if not path.startswith(ATLAS_STATIC) or not os.path.isfile(path):
            path = os.path.join(ATLAS_STATIC, 'index.html')
        return FileResponse(path)

    # ---- stand-in OIDC -----------------------------------------------------------
    @app.get('/oidc/auth')
    def oidc_auth(request: Request, redirect_uri: str, state: str = '', nonce: str = ''):
        code = _b64(json.dumps({'n': nonce, 'u': viewer(request)}).encode())
        sep = '&' if '?' in redirect_uri else '?'
        return RedirectResponse(f'{redirect_uri}{sep}' + urllib.parse.urlencode({'code': code, 'state': state}),
                                status_code=302)

    @app.post('/d2e/oauth/token')
    async def oidc_token(request: Request):
        form = {k: v[0] for k, v in urllib.parse.parse_qs((await request.body()).decode()).items()}
        nonce = ''
        if form.get('grant_type') == 'authorization_code':
            try:
                nonce = json.loads(_unb64(form.get('code', ''))).get('n', '')
            except ValueError:
                nonce = ''
        user = viewer(request)
        base = str(request.base_url).rstrip('/')
        issuer = form.get('redirect_uri', base).split('/d2e/portal')[0] + '/oidc'
        now = int(time.time())
        common = {'sub': user, 'username': user, 'name': user, 'preferred_username': user, 'iss': issuer,
                  'iat': now, 'exp': now + 3600}
        id_token = jwt(dict(common, aud=form.get('client_id') or CLIENT_ID, nonce=nonce, email=None,
                            email_verified=False))
        access = jwt(dict(common, aud='https://alp-default', client_id=CLIENT_ID, roles=roles(), scope=''))
        return {'access_token': access, 'id_token': id_token, 'refresh_token': _b64(secrets.token_bytes(24)),
                'token_type': 'Bearer', 'expires_in': 3600, 'scope': 'openid offline_access profile email'}

    @app.get('/oidc/session/end')
    def oidc_end(redirect: str = '../d2e/portal'):
        return RedirectResponse(redirect, status_code=302)

    # ---- system-portal -----------------------------------------------------------
    @app.get('/d2e/system-portal/feature/list')
    def features():
        return [{'feature': f, 'name': n, 'nameI18nKey': 'FEATURE__' + re.sub(r'(?<!^)([A-Z])', r'_\1', f).upper(),
                 'isEnabled': on} for f, n, on in FEATURES]

    @app.get('/d2e/system-portal/dataset/public/list')
    def public_datasets():
        return []

    @app.get('/d2e/system-portal/config/public/overview-description')
    def overview():
        return {'type': 'overview-description', 'value': description or title}

    @app.get('/d2e/system-portal/config/public/header-image')
    def header_image():
        return {'type': 'header-image', 'value': None}

    @app.get('/d2e/system-portal/config/types')
    def config_types():
        return {}

    @app.get('/d2e/system-portal/dataset/list')
    def datasets():
        return [dataset(k) for k in sources]

    @app.get('/d2e/system-portal/dataset')
    def dataset_one(datasetId: str = '', tokenDatasetCode: str = ''):
        key = datasetId or tokenDatasetCode
        if not key:
            raise HTTPException(400, '400 - datasetId or tokenDatasetCode is required')
        return dataset(key)

    @app.get('/d2e/system-portal/dataset/release/list')
    def releases(datasetId: str = ''):
        return []

    @app.get('/d2e/system-portal/dataset/resource/list')
    def resources(datasetId: str = ''):
        return {'id': datasetId, 'resources': []}

    # ---- usermgmt ----------------------------------------------------------------
    @app.post('/d2e/usermgmt/api/user-group/list')
    def user_groups(request: Request):
        keys = list(sources)
        return {'userId': viewer(request), 'groups': roles(),
                'alpRoleMap': {'STUDY_RESEARCHER': keys, 'TENANT_VIEWER': ['tenant']},
                'alp_role_study_researcher': keys, 'alp_role_tenant_viewer': ['tenant'], 'alp_tenant_id': ['tenant'],
                'alp_role_study_admin': [], 'alp_role_tenant_admin': []}

    @app.post('/d2e/usermgmt/api/me/sync-webapi-roles')
    def sync_roles():
        return {'ok': True}

    @app.get('/d2e/usermgmt/api/study/access-request/me')
    def access_requests():
        return []

    # ---- jobplugins: data characterization from the Achilles reports -------------
    def flow_run(key, kind):
        t = _iso()
        return {'id': key, 'name': f'{kind}_{key}', 'created': t, 'updated': t, 'flow_id': kind, 'state_id': key,
                'state_type': 'COMPLETED', 'state_name': 'Completed', 'start_time': t, 'end_time': t,
                'tags': ['data_characterization'], 'parameters': {'options': {'datasetId': key}},
                'state': {'id': key, 'type': 'COMPLETED', 'name': 'Completed', 'timestamp': t, 'message': None}}

    @app.get('/d2e/jobplugins/dqd/data-characterization/flow-run/latest')
    def dc_latest(datasetId: str):
        src(datasetId)
        return flow_run(datasetId, 'DC') if reports[datasetId].ready() else None

    @app.get('/d2e/jobplugins/dqd/data-characterization/flow-run/{run}/results/{report}')
    def dc_results(run: str, report: str, datasetId: str = ''):
        key = datasetId or run
        src(key)
        r = reports[key]
        if not r.ready():
            raise HTTPException(404, 'no data characterization results')
        if report in DC_REPORTS:
            return _upper(getattr(r, DC_REPORTS[report])())
        if r.has_domain(report):
            return _upper(r.treemap(report))
        raise HTTPException(404, f'unknown report {report}')

    @app.get('/d2e/jobplugins/dqd/data-characterization/flow-run/{run}/results/{report}/{cid}')
    def dc_drilldown(run: str, report: str, cid: int, datasetId: str = ''):
        key = datasetId or run
        src(key)
        r = reports[key]
        if not r.ready() or not r.has_domain(report):
            raise HTTPException(404, f'unknown report {report}')
        return _upper(r.drilldown(report, cid))

    @app.get('/d2e/jobplugins/dqd/data-quality/flow-run/latest')
    def dq_latest(datasetId: str = ''):
        return None

    @app.get('/d2e/jobplugins/analysisflow/list')
    def analysis_flows():
        return []

    # ---- terminology (concept search facets and counts) --------------------------
    def concept_filter(text, flt):
        try:
            flt = json.loads(flt or '{}')
        except ValueError:
            flt = {}
        body = {'QUERY': text, 'DOMAIN_ID': flt.get('domainId') or [], 'VOCABULARY_ID': flt.get('vocabularyId') or [],
                'CONCEPT_CLASS_ID': flt.get('conceptClassId') or []}
        f = search_filters(body)
        std = [x for x in flt.get('standardConcept') or [] if x in ('S', 'C')]
        if std:
            f += ' AND STANDARD_CONCEPT IN (%s)' % ','.join(q(x) for x in std)
        valid = flt.get('validity') or []
        if valid == ['Valid']:
            f += ' AND INVALID_REASON IS NULL'
        elif valid == ['Invalid']:
            f += ' AND INVALID_REASON IS NOT NULL'
        return f

    @app.get('/d2e/terminology/concept/count')
    def concept_count(datasetId: str, code: str = '', filter: str = ''):
        s = src(datasetId)
        rows = s.query_dicts('SELECT COUNT(*) AS n FROM @CDM_schema.concept WHERE 1 = 1 '
                             + concept_filter(code, filter), CDM_schema=s.vocab_schema)
        return int(rows[0]['n']) if rows else 0

    @app.get('/d2e/terminology/concept/filter-options')
    def concept_filter_options(datasetId: str, searchText: str = '', filter: str = ''):
        s = src(datasetId)
        out = {'conceptClassId': {}, 'domainId': {}, 'standardConcept': {}, 'vocabularyId': {}, 'validity': {},
               'concept': {}}
        rows = s.query_dicts(
            'SELECT CONCEPT_CLASS_ID AS c, DOMAIN_ID AS d, COALESCE(STANDARD_CONCEPT, \'\') AS s, VOCABULARY_ID AS v, '
            'CASE WHEN INVALID_REASON IS NULL THEN \'Valid\' ELSE \'Invalid\' END AS i, COUNT(*) AS n '
            'FROM @CDM_schema.concept WHERE 1 = 1 ' + concept_filter(searchText, filter) + ' GROUP BY 1, 2, 3, 4, 5',
            CDM_schema=s.vocab_schema)
        for r in rows:
            n = int(r['n'])
            for k, col in (('conceptClassId', 'c'), ('domainId', 'd'), ('standardConcept', 's'),
                           ('vocabularyId', 'v'), ('validity', 'i')):
                out[k][r[col]] = out[k].get(r[col], 0) + n
            kind = 'Standard' if r['s'] == 'S' else 'Non-standard'
            out['concept'][kind] = out['concept'].get(kind, 0) + n
        return {'filterOptions': out}

    @app.post('/d2e/d2e-webapi/vocabulary/{key}/search')
    async def d2e_search(key: str, request: Request, page: int = None, rowsPerPage: int = None):
        s = src(key)
        body = await request.json()
        sql = sql_resource('vocabulary', 'search.sql').replace('@filters', search_filters(body))
        if rowsPerPage:
            sql += f'\nLIMIT {int(rowsPerPage)} OFFSET {int(page or 0) * int(rowsPerPage)}'
        else:
            sql += '\nLIMIT 20000'
        return [concept_json(r) for r in s.query_dicts(sql, CDM_schema=s.vocab_schema)]

    # ---- analytics-svc: D2E's cohort builder -------------------------------------
    store = app.state.store
    A = '/d2e/analytics-svc'

    def translator(key):
        return pa.Translator(src(key), lambda cid: store.get_items(cid) if store.get_concept_set(cid) else None)

    def pa_config(key):
        n = table_counts(key)
        return pa.frontend_config({t for t, c in n.items() if c})

    def mriquery(request, body=None):
        raw = request.query_params.get('mriquery')
        if raw:
            b = base64.b64decode(raw)
            try:
                b = zlib.decompress(b)
            except zlib.error:
                pass
            return json.loads(b)
        return body or {}

    def pa_answer(kind, qy):
        key = qy.get('datasetId') or next(iter(sources))
        cards = ((qy.get('filter') or {}).get('cards')) or {'type': 'BooleanContainer', 'op': 'AND', 'content': []}
        t = translator(key)
        try:
            if kind == 'patientcount':
                return t.patient_count(cards)
            if kind == 'barchart':
                return t.bar_chart(cards, qy.get('axisSelection') or [], pa_config(key)[0]['config'])
            if kind in ('inclusionreport', 'selectiveinclusionreport'):
                return t.inclusion_report(cards)
        except pa.PAError as e:
            return JSONResponse({'message': str(e), 'errorMessage': str(e)}, status_code=400)
        if kind == 'patientlist':
            return JSONResponse({'message': pa.REFUSED, 'errorMessage': pa.REFUSED}, status_code=403)
        msg = f'{kind} is not available yet'
        return JSONResponse({'message': msg, 'errorMessage': msg}, status_code=400)

    @app.get(A + '/pa/services/analytics.xsjs')
    def pa_my_config(datasetId: str = '', action: str = ''):
        if action and action != 'getMyConfig':
            return []
        return pa_config(datasetId or next(iter(sources)))

    @app.get(A + '/api/services/population/json/{kind}')
    def pa_population(kind: str, request: Request):
        return pa_answer(kind, mriquery(request))

    @app.post(A + '/api/services/population/json/{kind}')
    async def pa_population_post(kind: str, request: Request):
        body = await request.body()
        return pa_answer(kind, mriquery(request, json.loads(body) if body else None))

    @app.get(A + '/api/services/values')
    def pa_values(attributePath: str = '', datasetId: str = '', searchQuery: str = '', attributeType: str = ''):
        if attributePath == 'conceptSets' or attributeType == 'conceptSet':
            sets = store.list_concept_sets()
            s = (searchQuery or '').lower()
            return {'data': [{'value': str(c['id']), 'text': c['name'], 'score': 1} for c in sets
                             if not s or s in c['name'].lower()]}
        key = datasetId or next(iter(sources))
        name = attributePath.rsplit('.', 1)[-1]
        m = re.match(r'^patient\.interactions\.([^.]+)\.attributes\.([^.]+)$', attributePath)
        domain_col = col = None
        if m and m.group(1) in pa.INTERACTIONS:
            kind, col = pa.INTERACTIONS[m.group(1)][1].get(m.group(2), (None, None))
            if kind in ('name', 'code'):
                domain_col = 'concept_name' if kind == 'name' else 'concept_code'
                dom = {'condition': 'Condition', 'drug': 'Drug', 'procedure': 'Procedure', 'measurement': 'Measurement',
                       'observation': 'Observation', 'visit': 'Visit', 'device': 'Device', 'specimen': 'Specimen',
                       'death': 'Type Concept'}
                domain = next((v for k, v in dom.items() if col.startswith(k)), None)
        elif name in ('Gender_concept_name', 'raceName', 'ethnicityName'):
            domain_col, domain = 'concept_name', {'Gender_concept_name': 'Gender', 'raceName': 'Race',
                                                  'ethnicityName': 'Ethnicity'}[name]
        if not domain_col:
            return {'data': []}
        s = src(key)
        where = f"domain_id = {pa.q(domain)}" if domain else '1 = 1'
        if searchQuery:
            where += f" AND LOWER({domain_col}) LIKE {pa.q('%' + searchQuery.lower() + '%')}"
        if domain not in ('Gender', 'Race', 'Ethnicity') and domain_col == 'concept_name' and '_source_' not in (col or ''):
            where += " AND standard_concept = 'S'"
        rows = s.query_dicts(f'SELECT DISTINCT {domain_col} AS v FROM @vocab.concept WHERE {where} ORDER BY 1 LIMIT 100',
                             vocab=s.vocab_schema)
        return {'data': [{'value': r['v'], 'text': r['v'], 'score': 1} for r in rows]}

    # saved cohorts: the viewer's own drive (duckcdm.d2e.bookmarks)
    def bookmarks(request):
        return Bookmarks(viewer(request), request.headers.get('x-app-user-token'))

    def bm_call(fn):
        try:
            return fn()
        except BookmarkError as e:
            return JSONResponse({'error': str(e), 'message': str(e)}, status_code=e.status)

    async def bm_body(request):
        b = await request.body()
        return json.loads(b) if b else {}

    @app.get(A + '/api/services/bookmark')
    @app.get(A + '/api/services/bookmark/')
    def bm_list(request: Request, paConfigId: str = '', datasetId: str = ''):
        return bm_call(lambda: bookmarks(request).load_all(paConfigId or None))

    @app.get(A + '/api/services/bookmark/bookmarkIds')
    def bm_ids(request: Request, ids: str = '', paConfigId: str = ''):
        return bm_call(lambda: bookmarks(request).load_ids([i for i in ids.split(',') if i], paConfigId or None))

    @app.post(A + '/api/services/bookmark')
    @app.post(A + '/api/services/bookmark/')
    async def bm_post(request: Request):
        p = await bm_body(request)
        b = bookmarks(request)
        if p.get('cmd', 'insert') == 'loadAll':
            return bm_call(lambda: b.load_all(p.get('paConfigId') or None))
        return bm_call(lambda: b.insert(p))

    @app.put(A + '/api/services/bookmark/{bid}')
    async def bm_put(bid: str, request: Request):
        p = await bm_body(request)
        return bm_call(lambda: bookmarks(request).update(bid, p))

    @app.delete(A + '/api/services/bookmark/{bid}')
    def bm_delete(bid: str, request: Request):
        return bm_call(lambda: bookmarks(request).delete(bid))

    @app.post(A + '/api/services/bookmark/{bid}/duplicate')
    async def bm_duplicate(bid: str, request: Request):
        p = await bm_body(request)
        return bm_call(lambda: bookmarks(request).duplicate(bid, p))

    @app.get('/d2e/d2e-webapi/cohortdefinition-pa')
    def pa_cohort_list(request: Request):
        """The cohort builder's list (cohortdefinition?source=pa): the viewer's saved cohorts and the ATLAS definitions."""
        def atlas(c):
            d = {k: c[k] for k in ('id', 'name', 'createdDate', 'hasWriteAccess', 'hasReadAccess', 'tags')}
            d['description'] = c.get('description')
            d['createdBy'] = (c.get('createdBy') or {}).get('name')
            if c.get('modifiedDate'):
                d['modifiedDate'] = c['modifiedDate']
            return d
        out = bm_call(lambda: bookmarks(request).load_all()['bookmarks'])
        if isinstance(out, Response):
            return out
        return out + [atlas(c) for c in store.list_cohorts()]

    @app.get(A + '/api/services/cohort/can-materialize-cohort')
    def pa_can_materialize(datasetId: str = ''):
        return False

    @app.get(A + '/api/services/patient/cohorts/compare/{chart}')
    def pa_compare(chart: str, request: Request, ids: str = '', xaxis: str = '', yaxis: str = '', datasetId: str = ''):
        if chart != 'barchart':
            return JSONResponse({'message': f'comparing cohorts as {chart} is not available',
                                 'errorMessage': f'comparing cohorts as {chart} is not available'}, status_code=400)
        key = datasetId or next(iter(sources))
        saved = bm_call(lambda: bookmarks(request).load_ids([i for i in ids.split(',') if i])['bookmarks'])
        if isinstance(saved, Response):
            return saved
        order = {i: n for n, i in enumerate(ids.split(','))}
        cohorts = []
        for b in sorted(saved, key=lambda b: order.get(b['bmkId'], 0)):
            try:
                cards = ((json.loads(b['bookmark']).get('filter') or {}).get('cards'))
            except ValueError:
                continue
            cohorts.append((b['bmkId'], b['bookmarkname'], cards or {'type': 'BooleanContainer', 'op': 'AND', 'content': []}))
        xs = [x for x in xaxis.split(',') if x and x not in ('undefined', 'n/a')]
        try:
            return translator(key).compare_bar(cohorts, xs, pa_config(key)[0]['config'])
        except pa.PAError as e:
            return JSONResponse({'message': str(e), 'errorMessage': str(e)}, status_code=400)

    def refused():
        return JSONResponse({'message': pa.REFUSED, 'errorMessage': pa.REFUSED}, status_code=403)

    for path in ('/api/services/patient', '/api/services/patient/{rest:path}', '/api/services/datastream/{rest:path}',
                 '/api/services/population/csv/{rest:path}', '/api/services/search-notes',
                 '/api/services/calcview/{rest:path}'):
        app.add_api_route(A + path, refused, methods=['GET', 'POST'])

    # ---- /d2e/d2e-webapi/* is the WebAPI ------------------------------------------
    @app.middleware('http')
    async def _d2e_webapi(request, call_next):
        scope = request.scope
        root = scope.get('root_path') or ''      # some servers keep the mount prefix in path and say so in root_path
        p = scope['path'][len(root):] if root and scope['path'].startswith(root) else scope['path']
        if p == '/d2e/d2e-webapi/cohortdefinition' and b'source=pa' in scope.get('query_string', b''):
            new = '/d2e/d2e-webapi/cohortdefinition-pa'     # the cohort builder's list, not the WebAPI's
            scope['path'] = (root + new) if scope['path'] != p else new
            scope['raw_path'] = scope['path'].encode()
        elif p.startswith('/d2e/d2e-webapi/') and not re.match(r'^/d2e/d2e-webapi/vocabulary/[^/]+/search$', p):
            new = '/WebAPI/' + p[len('/d2e/d2e-webapi/'):]
            scope['path'] = (root + new) if scope['path'] != p else new
            scope['raw_path'] = scope['path'].encode()
        return await call_next(request)

    # these routes go before the ones create_app() made (its "/" and the catch-all ATLAS mount)
    new = app.router.routes[n_before:]
    del app.router.routes[n_before:]
    app.router.routes[0:0] = new
    return app
