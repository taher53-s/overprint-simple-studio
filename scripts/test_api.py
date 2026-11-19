"""HTTP integration checks. Starts a temporary Java server, always terminates it."""
import json, os, pathlib, socket, subprocess, time, urllib.request, urllib.parse, urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
with socket.socket() as s:
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
base = f'http://127.0.0.1:{port}'
log = open('results/api-server.log', 'w')
process = subprocess.Popen(['java', '-cp', 'build/classes', 'studio.Server', '--port', str(port)], stdout=log, stderr=log)
checks = []

def request(path, fields=None, raw=None, content_type=None, method=None):
    data = urllib.parse.urlencode(fields).encode() if fields is not None else raw
    req = urllib.request.Request(base+path, data=data, method=method)
    if data is not None:
        req.add_header('Content-Type', content_type or 'application/x-www-form-urlencoded')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read(), response.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers

def fields(name):
    p = json.loads((ROOT/'data'/name).read_text())
    return dict(targets=','.join(p['targets']), inks=','.join(f"{i['hex']}:{i['cost']}" for i in p['inks']), tolerance=p['tolerance'], maxInks=p['maxInks'], review=p['review'], seed=p['seed'])

def check(name, condition):
    assert condition, name
    checks.append('PASS '+name)
    print(checks[-1])

try:
    for attempt in range(60):
        try:
            if request('/api/health')[0] == 200: break
        except (OSError, urllib.error.URLError): time.sleep(.1)
    else: raise RuntimeError('Java test server did not become ready')
    check('Health endpoint identifies Java backend', json.loads(request('/api/health')[1])['backend']=='Java')
    for path, mime in [('/', 'text/html'),('/style.css','text/css'),('/app.js','text/javascript'),('/artwork.js','text/javascript')]:
        status, body, headers=request(path)
        check('Static resource '+path, status==200 and headers['Content-Type'].startswith(mime) and len(body)>100)
    code, raw, _=request('/api/plan',fields('01-poster.json')); result=json.loads(raw)
    check('Poster reaches a feasible four-ink plan', code==200 and result['feasible'] and result['withinPressLimit'] and len(result['selected'])==4)
    check('Review has exactly three unique colors', len(set(result['review']))==3)
    check('Every reported covered assignment meets threshold', all(m['deltaE']<=result['tolerance'] for m in result['mappings'] if m['covered']))
    (ROOT/'results/demo-plan.json').write_text(json.dumps({'inputs':json.loads((ROOT/'data/01-poster.json').read_text()),'result':result},indent=2)+'\n')
    neon=json.loads(request('/api/plan',fields('03-infeasible-neon.json'))[1])
    check('Infeasible palette exposes every uncovered color and null quantile', not neon['feasible'] and len(neon['uncovered'])==4 and neon['p90'] is None)
    dup=json.loads(request('/api/plan',fields('05-duplicates.json'))[1])
    check('Duplicates consolidated without losing colors', dup['duplicatesRemoved']==1 and len(dup['targets'])==2)
    exact=json.loads(request('/api/plan',fields('04-exact-match.json'))[1])
    check('Zero tolerance exact matches all have zero error', exact['feasible'] and all(x['deltaE']==0 for x in exact['mappings']))
    limited=fields('01-poster.json'); limited['maxInks']=1
    check('Press budget warning is independent from coverage', not json.loads(request('/api/plan',limited)[1])['withinPressLimit'])
    invalids=[{}, {'targets':'#GGGGGG','inks':'#000000:1'}, {'targets':'#000000','inks':'#000000:-1'}, {'targets':'#000000','inks':'#000000:1','tolerance':'Infinity'}, {'targets':'#000000','inks':'#000000:1','review':0}, {'targets':'#000000','inks':'#000000:1,#000000:2'}]
    check('Six invalid request classes return structured 400 errors', all(request('/api/plan',x)[0]==400 and 'error' in json.loads(request('/api/plan',x)[1]) for x in invalids))
    check('Wrong method returns 405', request('/api/plan',method='GET')[0]==405)
    check('Wrong content type returns 415', request('/api/plan',raw=b'{}',content_type='application/json')[0]==415)
    check('Oversized body returns 413', request('/api/plan',raw=b'x'*65537)[0]==413)
    check('Repeated form keys rejected', request('/api/plan',raw=b'targets=a&targets=b')[0]==400)
    check('Missing files and directory traversal not served', request('/missing')[0]==404 and request('/%2e%2e/README.md')[0]==404)
    check('Benchmark endpoint contains three measured sizes', len(json.loads(request('/api/benchmarks')[1])['rows'])==3)
finally:
    process.terminate()
    process.wait(timeout=10)
    log.close()
(ROOT/'results/api-tests.txt').write_text('\n'.join(checks)+f'\n\n{len(checks)} HTTP integration checks passed.\n')
