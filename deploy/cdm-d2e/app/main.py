"""CDM D2E — the Data2Evidence (D2E) portal on the snuh.ai app platform, backed by DuckCDM over Tables (no trex).

Same backend as CDM ATLAS (deploy/cdm-atlas): the CDM is read from the Data Foundation Tables dataset
(DF_DATASET, default snuh_cdm) with the app's own permissions (DF_AUTH=app), each query logged with the viewer's
ID, counts 1..9 shown as "<10". On top, duckcdm.d2e serves the D2E portal (dataset, data characterization,
concept search and concept sets, an ATLAS tab); its login is the platform's (the viewer the gateway names).
Patient-level views are not offered. Concept sets and cohort definitions live in /tmp (lost when the pod restarts).
"""
import os

os.environ.setdefault('WEBAPI_BUILD_NAME', 'WebAPI 3.0')
os.environ.setdefault('SOURCE_DIALECT_LABEL', 'postgresql')
os.environ.setdefault('SMALL_CELL_MIN', '10')         # counts 1..9 are shown as "<10" (사용자 결정 2026-10-23, D2E 2026-10-30)
os.environ.setdefault('DF_AUTH', 'app')               # 앱 권한으로 조회 (사용자 결정 2026-10-23)
# 앱 권한 + RESEARCH 는 scope-gate LLM 이 막는다(llm_unavailable, 2026-10-23) — purpose 없이 데이터셋 바인딩에 맡긴다
os.environ.setdefault('DF_PURPOSE', '')

from duckcdm import d2e
from duckcdm.webapi.app import create_app
from duckcdm.webapi.remote import RemoteSource, install_identity
from duckcdm.webapi.store import Store

source = RemoteSource(1, os.environ.get('SOURCE_KEY', 'SNUH'), os.environ.get('SOURCE_NAME', 'SNUH CDM'))
store = Store(os.environ.get('STORE_PATH', '/tmp/cdm-d2e-store.duckdb'), user='d2e')
app = create_app([source], store, title='CDM D2E')
install_identity(app)
d2e.install(app, title='CDM D2E', description=os.environ.get(
    'D2E_DESCRIPTION', '서울대병원 OMOP CDM — 앱 권한으로 집계 수만 보입니다(1~9명은 <10). 환자 단위 화면은 없습니다.'))
# no FastAPI documentation pages (they list the server internals)
app.router.routes = [r for r in app.router.routes if getattr(r, 'path', '') not in (
    '/docs', '/redoc', '/openapi.json', '/docs/oauth2-redirect', '/WebAPI/docs', '/WebAPI/openapi.json')]
app.openapi_url = app.docs_url = app.redoc_url = None
