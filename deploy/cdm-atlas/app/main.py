"""CDM ATLAS — OHDSI ATLAS 3.0 + WebAPI on the snuh.ai app platform (python-web, ASGI).

The CDM is read from the Data Foundation Tables dataset (DF_DATASET, default snuh_cdm) with the app's own
permissions (DF_AUTH=app, the platform app token): viewers see counts without a grant on snuh_cdm of their own,
and each query is logged with the viewer's ID.
Cohort generation is folded into one SELECT and run there (duckcdm.webapi.remote). Concept sets, cohort
definitions and analyses, with their (masked) results, are each viewer's own: kept in that viewer's drive under
apps/cdm-atlas/ (duckcdm.webapi.drive — the platform rule for what an app keeps for a user), loaded into memory
the first time they open the app.
The engine is not named to users: WebAPI build name, source dialect label, no API docs pages.
"""
import os

os.environ.setdefault('WEBAPI_BUILD_NAME', 'WebAPI 3.0')
os.environ.setdefault('SOURCE_DIALECT_LABEL', 'postgresql')
os.environ.setdefault('SMALL_CELL_MIN', '10')         # counts 1..9 are shown as "<10" (사용자 결정 2026-10-23)
os.environ.setdefault('DF_AUTH', 'app')               # 앱 권한으로 조회 (사용자 결정 2026-10-23)
# 앱 권한 + RESEARCH 는 scope-gate LLM 이 막는다(llm_unavailable, 2026-10-23) — purpose 없이 데이터셋 바인딩에 맡긴다
os.environ.setdefault('DF_PURPOSE', '')

from fastapi.responses import PlainTextResponse

from duckcdm.webapi import drive
from duckcdm.webapi.app import create_app
from duckcdm.webapi.remote import RemoteSource, install_identity

source = RemoteSource(1, os.environ.get('SOURCE_KEY', 'SNUH'), os.environ.get('SOURCE_NAME', 'SNUH CDM'))
store = drive.from_env(user='atlas')
app = create_app([source], store, title='CDM ATLAS')
install_identity(app)
drive.install(app, store)
# no FastAPI documentation pages (they list the server internals)
app.router.routes = [r for r in app.router.routes if getattr(r, 'path', '') not in ('/docs', '/redoc', '/openapi.json', '/docs/oauth2-redirect')]
app.openapi_url = app.docs_url = app.redoc_url = None


@app.get('/healthz')
def healthz():
    return PlainTextResponse('ok')
