"""CDM D2E (koreahealth.ai) — the Data2Evidence (D2E) portal over the public synthetic CDM, backed by DuckCDM (no trex).

The CDM is the public Synthetic-SNUH dataset (143 synthetic patients — no real records) bundled as one DuckDB
(data/synthetic_snuh.duckdb, built by deploy/cdm-atlas-kh/build_db.py), copied to /tmp at start so cohort results
can be written. duckcdm.d2e serves the D2E portal (dataset, data characterization, concept search and concept
sets, an ATLAS tab); its login is the platform's. Concept sets and cohort definitions live in /tmp.
"""
import os
import shutil

os.environ.setdefault('WEBAPI_BUILD_NAME', 'WebAPI 3.0')
os.environ.setdefault('SOURCE_DIALECT_LABEL', 'postgresql')
os.environ.setdefault('D2E_LOCAL_USER', 'user')

from duckcdm import d2e
from duckcdm.webapi.app import create_app
from duckcdm.webapi.sources import Source
from duckcdm.webapi.store import Store

DB = '/tmp/synthetic_snuh.duckdb'
if not os.path.exists(DB):
    shutil.copy(os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic_snuh.duckdb'), DB)
source = Source(1, 'SYNSNUH', 'Synthetic-SNUH CDM', DB, memory_limit='1GB', threads=2)
store = Store('/tmp/cdm-d2e-store.duckdb', user='d2e')
app = create_app([source], store, title='CDM D2E')
d2e.install(app, title='CDM D2E', description='Synthetic-SNUH CDM — 가상 환자 143명의 합성 데이터(실제 환자 기록 없음)')
# no FastAPI documentation pages (they list the server internals)
app.router.routes = [r for r in app.router.routes if getattr(r, 'path', '') not in (
    '/docs', '/redoc', '/openapi.json', '/docs/oauth2-redirect', '/WebAPI/docs', '/WebAPI/openapi.json')]
app.openapi_url = app.docs_url = app.redoc_url = None
