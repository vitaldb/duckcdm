"""CDM ATLAS — duckcdm (OHDSI ATLAS 3.0 + WebAPI) on the snuh.ai app platform (python-web, ASGI).

The CDM is read from the Data Foundation Tables dataset (DF_DATASET, default snuh_cdm) as the viewing user:
the gateway identity headers are passed through, so the dataset grants decide who sees what.
Cohort generation is folded into one SELECT and run there (duckcdm.webapi.remote). The app keeps no data
of its own: concept sets and cohort definitions live in /tmp (lost when the pod restarts — export them as
JSON from ATLAS), cohort results are recomputed by generating again.
"""
import os

from fastapi.responses import PlainTextResponse

from duckcdm.webapi.app import create_app
from duckcdm.webapi.remote import RemoteSource, install_identity
from duckcdm.webapi.store import Store

source = RemoteSource(1, os.environ.get('SOURCE_KEY', 'SNUH'), os.environ.get('SOURCE_NAME', 'SNUH CDM'))
store = Store(os.environ.get('STORE_PATH', '/tmp/cdm-atlas-store.duckdb'), user='atlas')
app = create_app([source], store, title='CDM ATLAS')
install_identity(app)


@app.get('/healthz')
def healthz():
    return PlainTextResponse('ok')
