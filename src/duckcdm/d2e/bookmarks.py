"""Saved cohorts of the D2E cohort builder ("bookmarks"), kept in the viewer's own drive.

On an app platform with a user drive (APP_FILES_URL, the gateway's X-App-User-Token on each request) a saved cohort is
one JSON file in the viewer's drive: apps/<APP_NAME>/cohorts/<id>.json. Each viewer sees only their own; the
"share" flag is kept but not acted on (another viewer cannot read someone's drive). Without a drive (local runs) the
files go to D2E_BOOKMARK_DIR/<viewer>/ instead. The records have the shape D2E's bookmark service returns.
"""
import datetime
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid

FILES_URL = os.environ.get('APP_FILES_URL', '').rstrip('/')
APP_NAME = os.environ.get('APP_NAME', 'cdm-d2e')
LOCAL_DIR = os.environ.get('D2E_BOOKMARK_DIR', '/tmp/d2e-bookmarks')


class BookmarkError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class _Drive:
    """The viewer's drive through the platform's Files API (the viewer's own token, never the app's)."""

    def __init__(self, token):
        self.token = token
        self.folder = f'apps/{APP_NAME}/cohorts'

    def _call(self, method, path, body=None, headers=None):
        h = {'X-App-User-Token': self.token}
        h.update(headers or {})
        req = urllib.request.Request(FILES_URL + path, data=body, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def list(self):
        out, offset = [], 0
        while True:
            q = urllib.parse.urlencode({'path': self.folder, 'limit': 100, 'offset': offset})
            code, raw = self._call('GET', f'/api/v1/drive/files?{q}')
            if code == 404:
                return out
            if code != 200:
                raise BookmarkError(502, f'drive list failed ({code})')
            j = json.loads(raw)
            files = j.get('files') or []
            out += [f for f in files if str(f.get('path') or f.get('name') or '').endswith('.json')]
            offset += len(files)
            if not files or offset >= int(j.get('total') or 0):
                return out

    def read(self, f):
        path = str(f.get('path') or f'{self.folder}/{f.get("name")}').lstrip('/')
        code, raw = self._call('GET', '/api/v1/drive/files/download?' + urllib.parse.urlencode({'path': path}))
        return json.loads(raw) if code == 200 else None

    def write(self, rec):
        b = uuid.uuid4().hex
        path = f'{self.folder}/{rec["bmkId"]}.json'
        body = (f'--{b}\r\nContent-Disposition: form-data; name="path"\r\n\r\n{path}\r\n'
                f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{rec["bmkId"]}.json"\r\n'
                'Content-Type: application/json\r\n\r\n').encode() + json.dumps(rec, ensure_ascii=False).encode() + \
            f'\r\n--{b}--\r\n'.encode()
        code, raw = self._call('POST', '/api/v1/drive/files/upload', body,
                               {'Content-Type': f'multipart/form-data; boundary={b}'})
        if code == 413:
            raise BookmarkError(413, 'your drive is full')
        if code != 200:
            raise BookmarkError(502, f'drive upload failed ({code})')

    def delete(self, bid):
        q = urllib.parse.urlencode({'path': f'{self.folder}/{bid}.json'})
        code, _ = self._call('DELETE', f'/api/v1/drive/files?{q}')
        if code not in (200, 404):
            raise BookmarkError(502, f'drive delete failed ({code})')


class _Local:
    def __init__(self, user):
        self.dir = os.path.join(LOCAL_DIR, re.sub(r'[^\w.-]', '_', user))

    def list(self):
        if not os.path.isdir(self.dir):
            return []
        return [{'name': n} for n in sorted(os.listdir(self.dir)) if n.endswith('.json')]

    def read(self, f):
        try:
            with open(os.path.join(self.dir, f['name']), encoding='utf-8') as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return None

    def write(self, rec):
        os.makedirs(self.dir, exist_ok=True)
        with open(os.path.join(self.dir, rec['bmkId'] + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, ensure_ascii=False)

    def delete(self, bid):
        try:
            os.remove(os.path.join(self.dir, re.sub(r'[^\w.-]', '_', bid) + '.json'))
        except FileNotFoundError:
            pass


class Bookmarks:
    """D2E's bookmark commands (insert, update, rename, delete, duplicate, loadAll, loadByIDs) over one viewer's files."""

    def __init__(self, user, token):
        self.user = user
        self.box = _Drive(token) if FILES_URL and token else _Local(user)

    def _all(self, pa_config_id=None):
        recs = [r for r in (self.box.read(f) for f in self.box.list()) if r and r.get('bmkId')]
        if pa_config_id:
            recs = [r for r in recs if r.get('paConfigId') in (None, '', pa_config_id)]
        return sorted(recs, key=lambda r: (r.get('bookmarkname') or '').lower())

    def _one(self, bid):
        for r in self._all():
            if r['bmkId'] == bid:
                return r
        raise BookmarkError(404, 'saved cohort not found')

    def load_all(self, pa_config_id=None):
        return {'schemaName': '', 'bookmarks': self._all(pa_config_id)}

    def load_ids(self, ids, pa_config_id=None):
        want = set(ids)
        return {'schemaName': '', 'bookmarks': [r for r in self._all(pa_config_id) if r['bmkId'] in want]}

    def _name_free(self, name, but=None):
        if not name:
            raise BookmarkError(400, 'Bookmark name cannot be empty')
        if any(r['bookmarkname'] == name and r['bmkId'] != but for r in self._all()):
            raise BookmarkError(400, f'a saved cohort named {name} exists')

    def insert(self, p):
        name = (p.get('bookmarkname') or '').strip()
        self._name_free(name)
        rec = {'bmkId': uuid.uuid4().hex, 'bookmarkname': name, 'bookmark': p.get('bookmark') or '',
               'viewname': None, 'modified': _now(), 'version': 1, 'user_id': self.user,
               'shared': bool(p.get('shareBookmark')), 'paConfigId': p.get('paConfigId') or ''}
        self.box.write(rec)
        return {'status': 'success', 'bmkId': rec['bmkId']}

    def update(self, bid, p):
        rec = self._one(bid)
        cmd = p.get('cmd') or 'update'
        if cmd == 'rename':
            name = (p.get('newName') or p.get('bookmarkname') or '').strip()
            self._name_free(name, bid)
            rec['bookmarkname'] = name
        else:
            if p.get('bookmark') is not None:
                rec['bookmark'] = p['bookmark']
            if 'shareBookmark' in p:
                rec['shared'] = bool(p['shareBookmark'])
        rec['modified'] = _now()
        rec['version'] = int(rec.get('version') or 1) + 1
        self.box.write(rec)
        return 'success'

    def delete(self, bid):
        self.box.delete(bid)
        return 'success'

    def duplicate(self, bid, p):
        rec = dict(self._one(bid))
        name = (p.get('bookmarkname') or p.get('newName') or '').strip()
        self._name_free(name)
        rec.update(bmkId=uuid.uuid4().hex, bookmarkname=name, modified=_now(), version=1)
        self.box.write(rec)
        return {'status': 'success', 'bmkId': rec['bmkId']}
