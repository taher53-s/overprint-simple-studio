// Hosted demonstration adapter. Assessed Java implementation is in the download.
// The port preserves Java's Random sequence and the Java API's response shape.
export function lab(value) {
  const h=hex(value), linear=c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4;
  const [r,g,b]=[1,3,5].map(i=>linear(parseInt(h.slice(i,i+2),16)/255));
  const d=6/29,f=t=>t>d*d*d?Math.cbrt(t):t/(3*d*d)+4/29;
  const x=f((.4124564*r+.3575761*g+.1804375*b)/.95047);
  const y=f(.2126729*r+.7151522*g+.0721750*b);
  const z=f((.0193339*r+.1191920*g+.9503041*b)/1.08883);
  return [116*y-16,500*(x-y),200*(y-z)];
}
function hex(value) {
  const h=String(value).trim().toUpperCase();
  if(!/^#[0-9A-F]{6}$/.test(h))throw new Error('Use six-digit colours such as #ED622F.');
  return h;
}
const distance=(a,b)=>Math.sqrt(a.reduce((v,x,i)=>v+(x-b[i])**2,0));
function numeric(value,name,min,max,integer=false) {
  const text=String(value).trim(), n=Number(text);
  if(!text||!Number.isFinite(n)||n<min||n>max||(integer&&!/^[+-]?\d+$/.test(text)))throw new Error(`Check ${name}: use ${integer?'an integer':'a number'} from ${min} to ${max}.`);
  return n;
}
class JavaRandom {
  constructor(seed){this.seed=(BigInt(seed)^0x5DEECE66Dn)&((1n<<48n)-1n);}
  next(bits){this.seed=(this.seed*0x5DEECE66Dn+11n)&((1n<<48n)-1n);return Number(this.seed>>BigInt(48-bits));}
  nextInt(bound){
    if((bound&-bound)===bound)return Number(BigInt(bound)*BigInt(this.next(31))>>31n);
    let bits,val;do{bits=this.next(31);val=bits%bound;}while(bits-val+(bound-1)>=2147483648);return val;
  }
}
export function select(input,rank,seed=2409540) {
  if(!input.length||rank<0||rank>=input.length||!Number.isInteger(rank)||input.some(x=>!Number.isFinite(x)))throw new Error('Invalid selection input.');
  const a=[...input],random=new JavaRandom(seed);let low=0,high=a.length-1,partitions=0,comparisons=0;
  const swap=(i,j)=>{const t=a[i];a[i]=a[j];a[j]=t;};
  while(low<high){
    const pivot=a[low+random.nextInt(high-low+1)];let lt=low,i=low,gt=high;partitions++;
    while(i<=gt){comparisons++;if(a[i]<pivot)swap(lt++,i++);else if(a[i]>pivot)swap(i,gt--);else i++;}
    if(rank<lt)high=lt-1;else if(rank>gt)low=gt+1;else return {value:pivot,partitions,comparisons};
  }
  return {value:a[low],partitions,comparisons};
}
export function cover(n,coverage,costs) {
  const covered=Array(n).fill(false),used=Array(costs.length).fill(false),selected=[],steps=[];let remaining=n,cost=0;
  while(remaining>0){
    let best=-1,bestGain=0,bestRatio=Infinity;
    for(let j=0;j<costs.length;j++){
      if(used[j])continue;let gain=0;
      for(let i=0;i<n;i++)if(!covered[i]&&coverage[j][i])gain++;
      if(gain>0&&costs[j]/gain<bestRatio){best=j;bestGain=gain;bestRatio=costs[j]/gain;}
    }
    if(best===-1)break;used[best]=true;selected.push(best);steps.push({ink:best,gain:bestGain,ratio:bestRatio});cost+=costs[best];
    for(let i=0;i<n;i++)if(!covered[i]&&coverage[best][i]){covered[i]=true;remaining--;}
  }
  return {selected,cost,steps,uncovered:covered.flatMap((v,i)=>v?[]:[i])};
}
export function plan(form) {
  const method=form.method||'randomized';if(!['randomized','deterministic'].includes(method))throw new Error('Unknown selection method.');
  const started=performance.now(),raw=(form.targets||'').trim();
  if(!raw)throw new Error('Add at least one artwork colour.');
  const input=raw.split(',');if(input.length>256)throw new Error('Use at most 256 artwork colours.');
  const targets=[...new Set(input.map(hex))], inkText=(form.inks||'').trim();
  if(!inkText)throw new Error('Enable at least one available ink.');
  const inks=inkText.split(',').map(s=>{
    const parts=s.split(':');if(parts.length!==2)throw new Error('Each ink needs hex:cost.');
    const cost=numeric(parts[1],'ink cost',0,1000);if(cost<=0)throw new Error('Ink setup costs must be greater than zero.');
    return {hex:hex(parts[0]),cost};
  });
  if(inks.length>64)throw new Error('Use at most 64 available inks.');
  if(new Set(inks.map(x=>x.hex)).size!==inks.length)throw new Error('Remove duplicate inks from the ink bank.');
  const tolerance=numeric(form.tolerance??18,'colour tolerance',0,100);
  const requestedReview=numeric(form.review??3,'review count',1,256,true),maxInks=numeric(form.maxInks??4,'press limit',1,64,true);
  const seedText=String(form.seed??2409540);if(!/^[+-]?\d+$/.test(seedText))throw new Error('Seed must be a signed 64-bit integer.');
  const seed=BigInt(seedText);if(seed<-(1n<<63n)||seed>=(1n<<63n))throw new Error('Seed must be a signed 64-bit integer.');
  const n=targets.length,m=inks.length,labs=targets.map(lab),costs=inks.map(x=>x.cost);
  const distances=inks.map(x=>{const inkLab=lab(x.hex);return labs.map(a=>distance(a,inkLab));});
  const coverage=distances.map(row=>row.map(x=>x<=tolerance)),r=cover(n,coverage,costs);
  const baseline=new Set();for(let i=0;i<n;i++){let best=-1;for(let j=0;j<m;j++)if(coverage[j][i]&&(best===-1||costs[j]<costs[best]))best=j;if(best>=0)baseline.add(best);}
  const mappings=targets.map((source,i)=>{
    let best=-1;for(const j of r.selected)if(best<0||distances[j][i]<distances[best][i])best=j;
    return {index:i,source,ink:best<0?null:inks[best].hex,deltaE:best<0?null:distances[best][i],covered:best>=0&&coverage[best][i]};
  });
  const errors=mappings.map(x=>x.deltaE??0),k=Math.min(requestedReview,n),review=[];
  let reviewThreshold=null,p90=null,partitions=0,comparisons=0;
  if(r.selected.length){
    const selection=method==='deterministic'?{value:deterministicSelect(errors,n-k),partitions:0,comparisons:0}:select(errors,n-k,seed);reviewThreshold=selection.value;partitions=selection.partitions;comparisons=selection.comparisons;
    for(let i=0;i<n;i++)if(errors[i]>reviewThreshold)review.push(i);
    for(let i=0;i<n&&review.length<k;i++)if(errors[i]===reviewThreshold)review.push(i);
    p90=select(errors,Math.ceil(.9*n)-1,seed).value;
  }
  return {targets,inputCount:input.length,duplicatesRemoved:input.length-n,selected:r.selected.map(index=>({index,hex:inks[index].hex,cost:costs[index]})),mappings,uncovered:r.uncovered,cost:r.cost,baselineCost:[...baseline].reduce((s,j)=>s+costs[j],0),baselineInks:baseline.size,feasible:!r.uncovered.length,withinPressLimit:r.selected.length<=maxInks,maxInks,tolerance,review,reviewThreshold,p90,partitions,comparisons,selectionMethod:method,rankedReview:heapRank(review,errors),seed:Number(seed),trace:r.steps.map(s=>({hex:inks[s.ink].hex,gain:s.gain,ratio:s.ratio})),elapsedMs:performance.now()-started,engine:'Sites JavaScript demo'};
}

export function deterministicSelect(input,k){
 if(!input.length||!Number.isInteger(k)||k<0||k>=input.length||input.some(x=>!Number.isFinite(x)))throw new Error('Invalid selection input.');
 const insertion=a=>{for(let i=1;i<a.length;i++){const v=a[i];let j=i-1;while(j>=0&&a[j]>v){a[j+1]=a[j];j--;}a[j+1]=v;}return a;};
 const pick=(a,k)=>{
  if(a.length<=5)return insertion(a)[k];
  const medians=[];for(let i=0;i<a.length;i+=5){const g=insertion(a.slice(i,i+5));medians.push(g[Math.floor(g.length/2)]);}
  const pivot=pick(medians,Math.floor(medians.length/2)),less=[],greater=[];let equal=0;
  for(const v of a){if(v<pivot)less.push(v);else if(v>pivot)greater.push(v);else equal++;}
  return k<less.length?pick(less,k):k<less.length+equal?pivot:pick(greater,k-less.length-equal);
 };return pick([...input],k);
}
export function heapRank(indices,errors){
 const h=[...indices],out=[];
 for(const i of h)if(!Number.isInteger(i)||i<0||i>=errors.length||!Number.isFinite(errors[i]))throw new Error('Invalid review error.');
 const above=(a,b)=>errors[a]>errors[b]||(errors[a]===errors[b]&&a<b);
 const down=(i,size)=>{while(2*i+1<size){let c=2*i+1;if(c+1<size&&above(h[c+1],h[c]))c++;if(!above(h[c],h[i]))return;[h[i],h[c]]=[h[c],h[i]];i=c;}};
 for(let i=Math.floor(h.length/2)-1;i>=0;i--)down(i,h.length);
 for(let size=h.length;size>0;){out.push(h[0]);h[0]=h[--size];down(0,size);}return out;
}
