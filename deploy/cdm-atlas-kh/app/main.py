"""CDM ATLAS (koreahealth.ai) — OHDSI ATLAS 3.0 + WebAPI over the public synthetic CDM, on the koreahealth.ai app platform.

The CDM is the public Synthetic-SNUH dataset (synthetic_snuh_cdm, 143 synthetic patients — no real records) bundled
with the code as one DuckDB (data/synthetic_snuh.duckdb, built by build_db.py: the synthetic tables, the vocabulary
for their concepts and ancestors, Achilles results). It is copied to /tmp at start so cohort results can be written;
concept sets and cohort definitions live in /tmp too (lost when the pod restarts — export them as JSON from ATLAS).
The engine is not named to users: WebAPI build name, source dialect label, no API docs pages.
"""
import os
import shutil

os.environ.setdefault('WEBAPI_BUILD_NAME', 'WebAPI 3.0')
os.environ.setdefault('SOURCE_DIALECT_LABEL', 'postgresql')

from fastapi.responses import PlainTextResponse

from duckcdm.webapi.app import create_app
from duckcdm.webapi.sources import Source
from duckcdm.webapi.store import Store

DB = '/tmp/synthetic_snuh.duckdb'
if not os.path.exists(DB):
    shutil.copy(os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic_snuh.duckdb'), DB)
source = Source(1, 'SYNSNUH', 'Synthetic-SNUH CDM', DB, memory_limit='1GB', threads=2)
store = Store('/tmp/cdm-atlas-store.duckdb', user='atlas')
app = create_app([source], store, title='CDM ATLAS')
# no FastAPI documentation pages (they list the server internals)
app.router.routes = [r for r in app.router.routes if getattr(r, 'path', '') not in ('/docs', '/redoc', '/openapi.json', '/docs/oauth2-redirect')]
app.openapi_url = app.docs_url = app.redoc_url = None


@app.get('/healthz')
def healthz():
    return PlainTextResponse('ok')
