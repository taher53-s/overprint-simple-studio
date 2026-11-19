import {readFile,writeFile,mkdir,readdir,copyFile} from 'node:fs/promises';
const types={html:'text/html; charset=utf-8',css:'text/css',js:'text/javascript',svg:'image/svg+xml',json:'application/json',pdf:'application/pdf',zip:'application/zip',mp4:'video/mp4',jpg:'image/jpeg',vtt:'text/vtt; charset=utf-8'};
const assets={};
for(const folder of ['web','data'])for(const name of await readdir(folder)){
  const extension=name.split('.').pop(),binary=['pdf','zip','mp4','jpg'].includes(extension),bytes=await readFile(`${folder}/${name}`);
  assets[folder==='web'?'/'+name:`/${folder}/${name}`]={type:types[extension]||'application/octet-stream',body:bytes.toString(binary?'base64':'utf8'),binary};
}
assets['/api/benchmarks']={type:'application/json',body:await readFile('results/benchmarks.json','utf8'),binary:false};
const config=JSON.parse(await readFile('.openai/hosting.json','utf8'));
if(!config.project_id)throw new Error('Missing registered Site identity.');
const worker=(await readFile('worker/planner.mjs','utf8'))+'\nconst ASSETS='+JSON.stringify(assets)+';\n'+await readFile('worker/handler.mjs','utf8');
await mkdir('dist/server',{recursive:true});await mkdir('dist/.openai',{recursive:true});
await writeFile('dist/server/index.js',worker);await copyFile('.openai/hosting.json','dist/.openai/hosting.json');
console.log(`Built ${Object.keys(assets).length} embedded resources; Worker ${(Buffer.byteLength(worker)/1024).toFixed(0)} KiB.`);
