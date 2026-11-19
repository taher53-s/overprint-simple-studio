import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {plan,select,cover,deterministicSelect,heapRank} from '../worker/planner.mjs';
import worker from '../dist/server/index.js';
const fixtures=JSON.parse(await readFile('results/java-parity.json','utf8'));
function compare(a,b,path=''){
  if(path.endsWith('.elapsedMs'))return;
  if(typeof b==='number'){assert.ok(Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(b)),`${path}: ${a} != ${b}`);return;}
  if(b===null||typeof b!=='object'){assert.equal(a,b,path);return;}
  if(Array.isArray(b))assert.equal(a.length,b.length,path);
  for(const key of Object.keys(b))compare(a[key],b[key],path+'.'+key);
}
for(const f of fixtures)compare(plan(f.form),f.expected);
const failures=[{}, {targets:'#000000',inks:'#000000:0'}, {targets:'#000000',inks:'#000000:1',tolerance:'NaN'}, {targets:'#000000',inks:'#000000:1',review:'1.2'}, {targets:'#000000',inks:'#000000:1,#000000:1'}, {targets:'#000000',inks:'#000000:1',seed:'9223372036854775808'}];
for(const f of failures)assert.throws(()=>plan(f));
for(let n=1;n<=200;n++){
  const a=Array.from({length:n},(_,i)=>((i*37+n)%53)-26),sorted=[...a].sort((a,b)=>a-b);
  for(const rank of [0,Math.floor(n/2),n-1])assert.equal(select(a,rank,n).value,sorted[rank]);
}
assert.deepEqual(cover(2,[[true,false]],[1]).uncovered,[1]);
const response=await worker.fetch(new Request('https://test.local/api/plan',{method:'POST',body:new URLSearchParams(fixtures[0].form)}));
assert.equal(response.status,200);compare(await response.json(),fixtures[0].expected);
for(const [url,mime] of [['/','text/html'],['/app.js','text/javascript'],['/api/benchmarks','application/json'],['/overprint-film.mp4','video/mp4']]){
  const response=await worker.fetch(new Request('https://test.local'+url));assert.equal(response.status,200);assert.ok(response.headers.get('Content-Type').startsWith(mime));assert.ok((await response.arrayBuffer()).byteLength>100);
}
assert.equal((await worker.fetch(new Request('https://test.local/api/plan'))).status,405);
assert.equal((await worker.fetch(new Request('https://test.local/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}))).status,415);
assert.equal((await worker.fetch(new Request('https://test.local/api/plan',{method:'POST',body:new URLSearchParams({x:'a'.repeat(65537)})}))).status,413);
assert.equal((await worker.fetch(new Request('https://test.local/missing'))).status,404);
const report=`PASS: ${fixtures.length} plans match the Java backend (numeric tolerance 1e-9 relative).\nPASS: 600 Quickselect order statistics match full sorting.\nPASS: 6 invalid input classes rejected.\nPASS: Worker plan, asset, download, method, content-type, size and missing-route checks.\n`;
console.log(report);await writeFile('results/sites-tests.txt',report);

for(let n=1;n<=100;n++){const a=Array.from({length:n},(_,i)=>(i*37+n)%29),sorted=[...a].sort((a,b)=>a-b);for(const rank of [0,Math.floor(n/2),n-1])assert.equal(deterministicSelect(a,rank),sorted[rank]);const ids=a.map((_,i)=>i);assert.deepEqual(heapRank(ids,a),[...ids].sort((i,j)=>a[j]-a[i]||i-j));}
for(const f of fixtures){const a=plan(f.form),b=plan({...f.form,method:'deterministic'});assert.equal(a.reviewThreshold,b.reviewThreshold);assert.deepEqual(a.rankedReview,b.rankedReview);}
console.log('PASS 300 deterministic-selection oracles, 100 heap ordering oracles, and 125 cross-mode comparisons.');
const html=await readFile('web/index.html','utf8');assert(!/Project notes|App ID pending|download-panel|hosting-note|ChatGPT|Codex/i.test(html));assert(html.includes('id="tour-dialog"'));assert(html.includes('id="film-dialog"'));console.log('PASS presentation copy and tour/video hooks.');
