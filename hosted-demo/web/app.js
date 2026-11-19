'use strict';
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const BANK = [
  ['Vermilion','#EC6033',1.9],['Cobalt','#2D488B',2.1],['Marigold','#E9BF44',1.5],['Carbon','#2D332B',1.1],
  ['Moss','#69704A',1.6],['Brick','#A94738',1.4],['Rose','#D88C9E',2.2],['Lilac','#8C86B5',1.9],
  ['Teal','#3B8583',1.8],['Warm grey','#ADA697',1],['Plum','#6E3D5F',1.9],['Ultramarine','#474AC5',2.4]
].map(([name,hex,cost]) => ({name,hex,cost,enabled:true}));
const PRESETS = {
  poster:{targets:['#EE653A','#DF704D','#2D488B','#3D5692','#E9BF44','#EFCA5A','#2D332B','#3A4036'],tolerance:18,maxInks:4,review:3},
  packaging:{targets:['#747B50','#69704A','#EDC44F','#DAB643','#A94738','#B95641','#383D33','#ADA697'],tolerance:20,maxInks:4,review:3},
  neon:{targets:['#00FF00','#FF00FF','#00FFFF','#0000FF'],tolerance:5,maxInks:2,review:2}
};
let palette=[...PRESETS.poster.targets], bank=structuredClone(BANK), result=null, planInput=null, dirty=false, mode='reduced', sequence=0;
let toastTimer;
function toast(message) { $('#toast').textContent=message; $('#toast').hidden=false; clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('#toast').hidden=true,5000); }
function esc(s) { return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function num(v,d=1) { return v==null?'—':Number(v).toFixed(d); }
function setDirty() {
  dirty=true; sequence++;
  $('#input-note').textContent='Colours changed. Try again to see the new result.';
  $('#input-note').classList.add('dirty');
  $('#export-svg').disabled=true; $('#export-json').disabled=true;
  $('#plan-button').disabled=false; $('#plan-button').innerHTML='Update my ink plan <span>↗</span>';
  $('#result-status').textContent='Showing the previous result'; $('#result-status').classList.add('issue');
  $('#proof-overlay').hidden=mode==='original';
  $('#proof-overlay').textContent='Colours changed. Click Find my ink plan to see the new result.';
  if(mode==='original') renderArtwork();
}
function renderPalette() {
  $('#palette-count').textContent=String(palette.length).padStart(2,'0');
  $('#palette-editor').innerHTML=palette.map((h,i)=>`<div class="palette-item"><input type="color" value="${h}" data-color="${i}" aria-label="Artwork colour ${i+1}"><div class="palette-hex">${h}</div><button class="remove-color" data-remove="${i}" aria-label="Remove colour ${i+1}">×</button></div>`).join('');
  $$('[data-color]').forEach(el=>el.addEventListener('input',()=>{palette[+el.dataset.color]=el.value.toUpperCase();el.nextElementSibling.textContent=el.value.toUpperCase();setDirty();}));
  $$('[data-remove]').forEach(el=>el.addEventListener('click',()=>{palette.splice(+el.dataset.remove,1);renderPalette();setDirty();}));
}
function renderBank() {
  $('#bank-count').textContent=String(bank.filter(x=>x.enabled).length).padStart(2,'0');
  $('#ink-bank').innerHTML=bank.map((ink,i)=>`<div class="ink-row"><input type="checkbox" id="ink-${i}" data-ink="${i}" ${ink.enabled?'checked':''} aria-label="Use ${esc(ink.name)}"><span class="ink-chip" style="background:${ink.hex}"></span><label for="ink-${i}">${esc(ink.name)}</label><input type="number" data-cost="${i}" value="${ink.cost}" min="0.1" max="1000" step="0.1" aria-label="Setup weight for ${esc(ink.name)}"></div>`).join('');
  $$('[data-ink]').forEach(el=>el.addEventListener('change',()=>{bank[+el.dataset.ink].enabled=el.checked;$('#bank-count').textContent=String(bank.filter(x=>x.enabled).length).padStart(2,'0');setDirty();}));
  $$('[data-cost]').forEach(el=>el.addEventListener('input',()=>{bank[+el.dataset.cost].cost=Number(el.value);setDirty();}));
}
function inputSnapshot() {
  return {targets:[...palette],inks:bank.filter(x=>x.enabled).map(({name,hex,cost})=>({name,hex,cost})),tolerance:Number($('#tolerance').value),maxInks:Number($('#max-inks').value),review:Number($('#review-count').value),method:$('#selection-method').value,seed:2409540};
}
async function plan() {
  const request=++sequence, snapshot=inputSnapshot();
  $('#plan-button').disabled=true; $('#plan-button').textContent='Finding your inks…';
  $('#input-note').textContent='Looking for close matches to your colours.';
  try {
    const body=new URLSearchParams({targets:snapshot.targets.join(','),inks:snapshot.inks.map(x=>`${x.hex}:${x.cost}`).join(','),tolerance:snapshot.tolerance,maxInks:snapshot.maxInks,review:snapshot.review,method:snapshot.method,seed:snapshot.seed});
    const response=await fetch('/api/plan',{method:'POST',body});
    const data=await response.json();
    if(request!==sequence)return;
    if(!response.ok)throw new Error(data.error||'The planner could not complete this plan.');
    result=data;planInput=snapshot;dirty=false;
    $('#input-note').classList.remove('dirty');
    $('#input-note').textContent=`Your colour suggestion is ready${data.duplicatesRemoved?` · ${data.duplicatesRemoved} repeated colours combined`:''}.`;
    $('#engine-status').textContent='Ready';$('#status-dot').classList.add('online');
    renderResult();renderArtwork();renderEvidence();return true;
  } catch(error) {
    if(request!==sequence)return;
    dirty=true;$('#input-note').textContent=error.message;$('#input-note').classList.add('dirty');
    $('#result-status').textContent='Input needs attention';$('#result-status').classList.add('issue');
    $('#export-svg').disabled=true;$('#export-json').disabled=true;
    $('#proof-overlay').hidden=false;$('#proof-overlay').textContent=error.message;toast(error.message);
  } finally {
    if(request===sequence){$('#plan-button').disabled=false;$('#plan-button').innerHTML='Find my ink plan <span>↗</span>';}
  }
}
function renderArtwork() {
  let colors=palette,label='ORIGINAL / SCREEN COLOURS';
  if(mode==='reduced'&&result){colors=result.mappings.map(x=>x.covered?x.ink:x.source);label=result.feasible?'REMAPPED / SCREEN STUDY':'INCOMPLETE / UNMATCHED COLOURS RETAINED';}
  $('#artboard').innerHTML=svgArtwork(colors,label);
  $('#proof-overlay').hidden=mode==='original'||(!dirty&&result&&result.selected.length>0);
  if(mode==='reduced'&&!dirty&&result&&!result.selected.length)$('#proof-overlay').textContent='These inks are not close enough to your colours. Try allowing more colour change.';
  $('#proof-caption').textContent=mode==='original'?`${palette.length} input colours · original colours`:result?`${result.selected.length} chosen inks · ${result.feasible?'suggested colour preview':'unmatched colours retained'}`:'Suggested colour preview';
}
function renderResult() {
  const r=result, ready=r.feasible&&r.withinPressLimit;
  $('#result-status').textContent=!r.feasible?'Some colours need a closer match':!r.withinPressLimit?'More inks than your limit':'Ready to compare';
  $('#result-status').classList.toggle('issue',!ready);
  $('#selected-count').textContent=r.selected.length;
  const saved=r.targets.length-r.selected.length;
  $('#reduction-copy').textContent=`${r.targets.length} artwork colours → ${r.selected.length} suggested inks.${saved>0?` ${saved} fewer than one ink per colour.`:''}`;
  $('#chosen-inks').innerHTML=r.selected.map(x=>`<span style="background:${x.hex}" title="${x.hex} · weight ${x.cost}" aria-label="${x.hex}, setup weight ${x.cost}"></span>`).join('');
  $('#coverage-value').textContent=`${r.targets.length-r.uncovered.length} / ${r.targets.length}`;
  $('#cost-value').textContent=`${num(r.cost)} units`;
  $('#baseline-value').textContent=`${num(r.baselineCost)} units`;
  $('#p90-value').textContent=r.p90==null?'No result':`${num(r.p90)} ΔE`;
  $('#review-colors').innerHTML=(r.rankedReview||r.review).map((i,rank)=>{const m=r.mappings[i];return `<div class="review-swatch" title="${m.source} → ${m.ink}; ΔE ${num(m.deltaE)}"><span style="background:${m.source}"></span><small>Check ${rank+1}</small></div>`;}).join('')||'<span class="hint">No matches to check yet.</span>';
  const warnings=[];
  if(!r.feasible)warnings.push(`${r.uncovered.length} colour(s) have no close match. Those colours stay unchanged in the preview. Allow more colour change or choose different inks.`);
  if(!r.withinPressLimit)warnings.push(`This suggestion uses ${r.selected.length} inks; your limit is ${r.maxInks}. Try changing the colours or allowing a bigger change. Another combination might use fewer inks.`);
  $('#plan-warning').hidden=!warnings.length;$('#plan-warning').textContent=warnings.join(' ');
  $('#color-mapping').style.gridTemplateColumns=`repeat(${Math.min(8,r.mappings.length)},1fr)`;
  $('#color-mapping').innerHTML=r.mappings.map(m=>`<div class="mapping-pair ${m.covered?'':'bad'}" title="${m.source} → ${m.ink||'No ink'}; ${m.covered?'covered':'outside tolerance'}"><span style="background:${m.source}"></span><span style="background:${m.ink||'repeating-linear-gradient(45deg,#aaa 0 2px,#eee 2px 4px)'}"></span><small>${m.deltaE==null?'×':num(m.deltaE)}</small></div>`).join('');
  $('#export-svg').disabled=!ready;$('#export-json').disabled=false;
}
function renderEvidence() {
  if(!result)return;
  const r=result;
  $('#trace-table').innerHTML=r.trace.length?`<table><thead><tr><th>PICK</th><th>INK</th><th>NEW COLOURS</th><th>COST / NEW</th></tr></thead><tbody>${r.trace.map((s,i)=>`<tr><td>0${i+1}</td><td><span class="table-swatch" style="background:${s.hex}"></span>${s.hex}</td><td>${s.gain}</td><td>${num(s.ratio,2)}</td></tr>`).join('')}</tbody></table>`:'<p>No ink covers any remaining colour at the current tolerance.</p>';
  const max=Math.max(1,...r.mappings.map(x=>x.deltaE||0));
  $('#error-chart').innerHTML=r.mappings.map((m,i)=>`<div class="error-row ${r.review.includes(i)?'review':''}"><span>${m.source}</span><div class="error-track"><i style="width:${100*(m.deltaE||0)/max}%"></i></div><span>${num(m.deltaE)}</span></div>`).join('');
  $('#selection-details').textContent=r.reviewThreshold==null?'No result exists, so no error quantile is reported.':`${r.selectionMethod==='deterministic'?'Median of Medians':'Randomized Quickselect'} cutoff: ΔE ${num(r.reviewThreshold,2)}. ${r.selectionMethod==='deterministic'?'Deterministic groups-of-five pivot.':`${r.partitions} partition(s), seed ${r.seed}.`} Orange bars mark the selected colours. The max-heap orders the review queue; p90 always uses randomized Quickselect.`;
}
async function loadBenchmarks() {
  try {
    const response=await fetch('/api/benchmarks'), b=await response.json();if(!response.ok)throw new Error(b.error);
    $('#benchmark-table').innerHTML=`<div class="table-scroll"><table><thead><tr><th>COLOURS</th><th>GREEDY (ms)</th><th>BASELINE (ms)</th><th>QUICKSELECT (ms)</th><th>FULL SORT (ms)</th><th>GREEDY / BASELINE COST</th></tr></thead><tbody>${b.rows.map(r=>`<tr><td>${r.n.toLocaleString()}</td><td>${num(r.greedyMs,3)}</td><td>${num(r.baselineMs,3)}</td><td>${num(r.quickselectMs,3)}</td><td>${num(r.sortMs,3)}</td><td>${num(r.greedyCost)} / ${num(r.baselineCost)}</td></tr>`).join('')}</tbody></table></div>`;
    const maximum=Math.max(...b.rows.flatMap(r=>[r.quickselectMs,r.sortMs]));
    $('#benchmark-bars').innerHTML=b.rows.map(r=>`<div class="bench-column"><span>${r.n.toLocaleString()} colours</span><div class="bench-bar"><span>Quickselect</span><i style="width:${r.quickselectMs/maximum*100}%"></i></div><div class="bench-bar sort"><span>Full sort</span><i style="width:${r.sortMs/maximum*100}%"></i></div></div>`).join('');
    $('#benchmark-method').textContent=`${b.method} Java ${b.java} · ${b.os} · ${b.processors} reported processors · seed ${b.seed}. Bars share one scale. These timings are not a guarantee for other machines.`;
  }catch(e){$('#benchmark-table').textContent=e.message;}
}
function download(name,content,type) {
  const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function applyPreset(key) {
  const p=PRESETS[key];palette=[...p.targets];bank=structuredClone(BANK);
  $('#tolerance').value=p.tolerance;$('#tolerance-value').value=p.tolerance;$('#max-inks').value=p.maxInks;$('#review-count').value=p.review;
  $('#study-label').textContent=key==='poster'?'01':key==='packaging'?'02':'03';
  renderPalette();renderBank();setDirty();plan();
}
$$('[data-view]').forEach(el=>el.addEventListener('click',()=>{
  const target=el.dataset.view;$$('.view').forEach(v=>v.hidden=v.id!==target);
  $$('.nav').forEach(b=>{b.classList.toggle('active',b.dataset.view===target);if(b.dataset.view===target)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  window.scrollTo({top:0,behavior:'instant'});
}));
$$('[data-proof]').forEach(el=>el.addEventListener('click',()=>{
  mode=el.dataset.proof;$$('[data-proof]').forEach(b=>{b.classList.toggle('selected',b===el);b.setAttribute('aria-pressed',String(b===el));});renderArtwork();
}));
$('#add-color').addEventListener('click',()=>{if(palette.length>=256){toast('The studio accepts up to 256 colours.');return;}palette.push('#EC6033');renderPalette();setDirty();});
$('#tolerance').addEventListener('input',()=>{$('#tolerance-value').value=$('#tolerance').value;setDirty();});
$('#max-inks').addEventListener('change',setDirty);$('#review-count').addEventListener('input',setDirty);$('#selection-method').addEventListener('change',setDirty);
$('#plan-button').addEventListener('click',plan);
$('#load-demo').addEventListener('click',()=>{$('#preset').value='poster';applyPreset('poster');});
$('#preset').addEventListener('change',()=>applyPreset($('#preset').value));
$('#palette-file').addEventListener('change',async event=>{
  const file=event.target.files[0];if(!file)return;
  try {
    if(file.size>65536)throw new Error('Use a palette JSON file smaller than 64 KB.');
    const data=JSON.parse(await file.text()), p=data.inputs||data;
    if(!Array.isArray(p.targets)||!p.targets.length||p.targets.length>256||p.targets.some(x=>typeof x!=='string'||!/^#[0-9a-f]{6}$/i.test(x)))throw new Error('JSON needs a targets array of 1–256 six-digit hex colours.');
    const nextBank=p.inks==null?structuredClone(BANK):p.inks;
    if(!Array.isArray(nextBank)||!nextBank.length||nextBank.length>64||nextBank.some(x=>!/^#[0-9a-f]{6}$/i.test(x.hex)||!Number.isFinite(x.cost)||x.cost<=0||x.cost>1000))throw new Error('Every ink needs a valid hex and a positive numeric cost (up to 1000).');
    const tolerance=p.tolerance??18, review=p.review??3,maxInks=p.maxInks??4;
    if(!Number.isFinite(tolerance)||tolerance<0||tolerance>60||!Number.isInteger(review)||review<1||review>256||!Number.isInteger(maxInks)||maxInks<1||maxInks>64)throw new Error('Use tolerance 0–60, review 1–256 and maxInks 1–64.');
    palette=p.targets.map(x=>x.toUpperCase());bank=nextBank.map(x=>({...x,hex:x.hex.toUpperCase(),name:String(x.name||x.hex),enabled:true}));
    $('#tolerance').value=tolerance;$('#tolerance-value').value=tolerance;$('#review-count').value=review;
    if(![...$('#max-inks').options].some(o=>Number(o.value)===maxInks))$('#max-inks').add(new Option(String(maxInks),String(maxInks)));
    $('#selection-method').value=p.method==='deterministic'?'deterministic':'randomized';$('#max-inks').value=maxInks;$('#study-label').textContent='CUSTOM';renderPalette();renderBank();setDirty();if(await plan())toast('Palette imported and checked.');
  }catch(e){toast(e.message);}finally{event.target.value='';}
});
$('#export-svg').addEventListener('click',()=>{if(!result||dirty||!result.feasible||!result.withinPressLimit)return;download('overprint-proof.svg',svgArtwork(result.mappings.map(x=>x.ink),'REMAPPED / SCREEN STUDY'),'image/svg+xml');toast('Poster saved. Check a real test print before production.');});
$('#export-json').addEventListener('click',()=>{if(!result||dirty)return;download('overprint-plan.json',JSON.stringify({project:'OVERPRINT',inputs:planInput,result},null,2),'application/json');toast('Colours and settings saved.');});
renderPalette();renderBank();renderArtwork();plan();loadBenchmarks();
