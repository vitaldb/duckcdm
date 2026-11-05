"""Each viewer's definitions kept in their own drive (the snuh.ai app platform's Files, "내 드라이브").

The platform rule: what an app keeps for a user goes to that user's drive under apps/{APP_NAME}/. So every viewer
gets a store of their own (in memory), filled from their drive the first time they open the app in this process,
and every change is written back — one JSON file per entity:

  apps/{APP_NAME}/concept-sets/{id}.json        apps/{APP_NAME}/characterizations/{id}.json
  apps/{APP_NAME}/cohorts/{id}.json             apps/{APP_NAME}/pathways/{id}.json
  apps/{APP_NAME}/feature-analyses/{id}.json    apps/{APP_NAME}/incidence-rates/{id}.json

Files take only the viewer's own short-lived token (X-App-User-Token, ~5 min), never the app's: writes happen at the
end of a request, with that request's token. Work that finishes in the background (generations, analyses) is
written by the next request — the ATLAS page keeps polling while it waits, so that is seconds later. A write that
fails stays pending and is retried. Definitions are per viewer: users no longer see each other's — they share them
by ATLAS export/import. A file the user removed from the drive is simply gone at the next start.

What goes to the drive carries no small counts (Store.export_entity masks them; analysis results are stored masked).

Without APP_FILES_URL, or for a request without a viewer token, the viewer's store just lives in memory.
"""
import contextvars
import json
import logging
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid

from starlette.concurrency import run_in_threadpool

from .store import Store

log = logging.getLogger('duckcdm.drive')

FOLDERS = {'conceptset': 'concept-sets', 'cohort': 'cohorts', 'fa': 'feature-analyses', 'cc': 'characterizations',
           'pw': 'pathways', 'ir': 'incidence-rates'}
KINDS = {v: k for k, v in FOLDERS.items()}

current = contextvars.ContextVar('duckcdm_drive_store', default=None)


class DriveError(Exception):
    pass


class Files:
    """The four Files calls an app may make, as the viewer."""

    def __init__(self, url, app_name, timeout=30):
        self.url, self.root, self.timeout = url.rstrip('/'), f'apps/{app_name}', timeout

    def _call(self, method, path, token, query=None, body=None, ctype=None):
        url = self.url + path + ('?' + urllib.parse.urlencode(query) if query else '')
        hdr = {'X-App-User-Token': token}
        if ctype:
            hdr['Content-Type'] = ctype
        req = urllib.request.Request(url, data=body, method=method, headers=hdr)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except (urllib.error.URLError, OSError) as e:
            raise DriveError(f'{method} {path}: {e}')

    def list(self, folder, token):
        """Paths of the files in apps/{APP_NAME}/{folder}; [] if the folder does not exist."""
        out, offset = [], 0
        while True:
            code, raw = self._call('GET', '/api/v1/drive/files', token,
                                   {'path': f'{self.root}/{folder}', 'limit': 100, 'offset': offset})
            if code == 404:
                return out
            if code != 200:
                raise DriveError(f'list {folder}: HTTP {code} {raw[:200]!r}')
            d = json.loads(raw)
            files = d.get('files') or []
            for f in files:
                p = f.get('path') or f'{self.root}/{folder}/{f.get("name")}'
                if not f.get('is_dir') and not f.get('is_trashed') and p.endswith('.json'):
                    out.append(p.lstrip('/'))
            offset += len(files)
            if not files or offset >= (d.get('total') or 0):
                return out

    def get(self, path, token):
        code, raw = self._call('GET', '/api/v1/drive/files/download', token, {'path': path})
        if code == 404:
            return None
        if code != 200:
            raise DriveError(f'get {path}: HTTP {code} {raw[:200]!r}')
        return raw

    def put(self, path, data, token):
        b = uuid.uuid4().hex
        body = (f'--{b}\r\nContent-Disposition: form-data; name="path"\r\n\r\n{path}\r\n'
                f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{path.rsplit("/", 1)[-1]}"\r\n'
                f'Content-Type: application/json\r\n\r\n').encode() + data + f'\r\n--{b}--\r\n'.encode()
        code, raw = self._call('POST', '/api/v1/drive/files/upload', token, body=body,
                               ctype=f'multipart/form-data; boundary={b}')
        if code != 200:
            raise DriveError(f'put {path}: HTTP {code} {raw[:200]!r}')

    def delete(self, path, token):
        code, raw = self._call('DELETE', '/api/v1/drive/files', token, {'path': path})
        if code not in (200, 204, 404):
            raise DriveError(f'delete {path}: HTTP {code} {raw[:200]!r}')


class UserStores:
    """Stands in for a Store: every attribute is the current viewer's store (set per request by install())."""

    def __init__(self, files=None, user='atlas'):
        self._files, self._user = files, user
        self._stores, self._loaded, self._lock = {}, set(), threading.Lock()
        self._user_locks = {}

    def __getattr__(self, name):
        st = current.get()
        if st is None:
            st = self._store(None)
        return getattr(st, name)

    def _store(self, uid):
        with self._lock:
            st = self._stores.get(uid)
            if st is None:
                st = self._stores[uid] = Store(':memory:', user=uid or self._user)
                self._user_locks[uid] = threading.Lock()
            return st

    def open(self, uid, token):
        """The viewer's store; filled from the drive on first use (needs the token), pending writes flushed."""
        st = self._store(uid)
        if self._files and uid and token and uid not in self._loaded:
            with self._user_locks[uid]:
                if uid not in self._loaded:
                    self._load(st, token)
                    self._loaded.add(uid)
        return st

    def _load(self, st, token):
        n = 0
        for folder, kind in KINDS.items():
            for path in self._files.list(folder, token):
                raw = self._files.get(path, token)
                if raw is None:
                    continue
                try:
                    doc = json.loads(raw)
                    if doc.get('kind') != kind:
                        raise ValueError(f"kind {doc.get('kind')!r}")
                    if (kind, doc['row']['id']) in st.changed:
                        continue                # changed here while the drive was unreachable: ours is newer
                    st.import_entity(doc)
                    n += 1
                except Exception as e:          # one bad file must not stop the app
                    log.warning('drive: skipped %s: %s', path, e)
        log.info('drive: loaded %d entities for %s', n, st.user['login'])

    def flush(self, uid, token):
        """Write the viewer's changed entities to their drive. Failures stay pending for the next request."""
        if not (self._files and uid and token and uid in self._loaded):
            return
        st = self._stores[uid]
        with self._user_locks[uid]:
            for kind, eid in sorted(st.changed):
                st.changed.discard((kind, eid))
                path = f'{self._files.root}/{FOLDERS[kind]}/{eid}.json'
                try:
                    doc = st.export_entity(kind, eid)
                    if doc is None:
                        self._files.delete(path, token)
                    else:
                        self._files.put(path, json.dumps(doc, ensure_ascii=False, default=str).encode(), token)
                except Exception as e:
                    st.changed.add((kind, eid))
                    log.warning('drive: %s not saved (retried next request): %s', path, e)
                    break


def install(app, stores):
    """Middleware: pick the viewer's store for this request (and the work it starts), save changes afterwards."""
    @app.middleware('http')
    async def _drive(request, call_next):
        h = request.headers
        uid = h.get('x-auth-user-id') or h.get('user-id') or h.get('x-auth-subject')
        token = h.get('x-app-user-token')
        try:
            st = await run_in_threadpool(stores.open, uid, token)
        except DriveError as e:
            log.warning('drive: could not load %s: %s', uid, e)
            st = stores._store(uid)        # serve from memory; loading is tried again next request
        tok = current.set(st)
        try:
            return await call_next(request)
        finally:
            current.reset(tok)
            await run_in_threadpool(stores.flush, uid, token)


def from_env(user='atlas'):
    url, name = os.environ.get('APP_FILES_URL'), os.environ.get('APP_NAME')
    return UserStores(Files(url, name) if url and name else None, user=user)
