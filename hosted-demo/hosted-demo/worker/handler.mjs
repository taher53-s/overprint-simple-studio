const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
async function boundedText(request){
  if(!request.body)return '';const reader=request.body.getReader(),parts=[];let size=0;
  while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>65536){await reader.cancel();return null;}parts.push(value);}
  const bytes=new Uint8Array(size);let pos=0;for(const p of parts){bytes.set(p,pos);pos+=p.length;}return new TextDecoder().decode(bytes);
}
export default {
  async fetch(request){
    const path=new URL(request.url).pathname;
    if(path==='/api/health'&&request.method==='GET')return json({status:'ok',backend:'Sites JavaScript demo',submissionBackend:'Java'});
    if(path==='/api/plan'){
      if(request.method!=='POST')return json({error:'Use POST for planning.'},405);
      if(request.headers.get('Content-Type')?.split(';')[0].trim()!=='application/x-www-form-urlencoded')return json({error:'Send a URL-encoded form.'},415);
      const text=await boundedText(request);if(text===null)return json({error:'Request exceeds 64 KB.'},413);
      try{
        const form={};for(const [k,v] of new URLSearchParams(text)){if(Object.hasOwn(form,k))throw new Error('Repeated parameter: '+k);Object.defineProperty(form,k,{value:v,enumerable:true});}
        return json(plan(form));
      }catch(error){return json({error:error.message},400);}
    }
    if(request.method!=='GET'&&request.method!=='HEAD')return json({error:'Use GET for files.'},405);
    const asset=ASSETS[path==='/'?'/index.html':path];
    if(!asset)return json({error:'File not found.'},404);
    const headers={'Content-Type':asset.type,'X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'};
    if(path.startsWith('/downloads/'))headers['Content-Disposition']='attachment; filename="'+path.split('/').pop()+'"';
    const body=asset.binary?Uint8Array.from(atob(asset.body),x=>x.charCodeAt(0)):asset.body;
    return new Response(request.method==='HEAD'?null:body,{headers});
  }
};
