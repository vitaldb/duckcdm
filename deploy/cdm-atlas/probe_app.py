"""Smoke test of CDM ATLAS inside the app pod: python3 /workspace/probe_app.py <user id>"""
import json, sys, time, urllib.request as u, urllib.error as E

B = 'http://127.0.0.1:8080/apps/runtime/dev/cdm-atlas'
H = {'X-Auth-User-ID': sys.argv[1], 'X-Auth-Method': 'parent_gateway', 'Content-Type': 'application/json'}


def call(m, p, body=None):
    t = time.time()
    r = u.Request(B + p, None if body is None else json.dumps(body).encode(), H, method=m)
    try:
        d = u.urlopen(r, timeout=55).read()
        return round(time.time() - t, 1), json.loads(d) if d[:1] in b'[{' else d[:80]
    except E.HTTPError as e:
        return round(time.time() - t, 1), f'HTTP {e.code} {e.read()[:300]}'


step = sys.argv[2] if len(sys.argv) > 2 else 'read'
if step == 'read':
    print('sources', call('GET', '/WebAPI/source/sources'))
    t, d = call('GET', '/WebAPI/cdmresults/SNUH/dashboard'); print('dashboard', t, str(d)[:200])
    t, d = call('GET', '/WebAPI/vocabulary/SNUH/search?query=diabetes'); print('search', t, len(d) if isinstance(d, list) else d)
    t, d = call('POST', '/WebAPI/cdmresults/SNUH/conceptRecordCount', [201826]); print('rc', t, d)
elif step == 'gen':
    f = sys.argv[3] if len(sys.argv) > 3 else 'probe_cohort.json'
    expr = json.load(open('/workspace/' + f))
    t, d = call('POST', '/WebAPI/cohortdefinition', {'name': 'probe ' + f, 'expressionType': 'SIMPLE_EXPRESSION', 'expression': expr})
    cid = d['id'] if isinstance(d, dict) else None; print('created', t, cid)
    print('generate', call('GET', f'/WebAPI/cohortdefinition/{cid}/generate/SNUH')[0])
    open('/tmp/probe_cid', 'w').write(str(cid))
elif step == 'info':
    cid = open('/tmp/probe_cid').read()
    print('info', call('GET', f'/WebAPI/cohortdefinition/{cid}/info'))
    print('report', str(call('GET', f'/WebAPI/cohortdefinition/{cid}/report/SNUH?mode=0'))[:400])
