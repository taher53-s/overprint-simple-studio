// Fallback for the unavailable Sites source helper. Credentials remain in memory.
import {spawnSync} from 'node:child_process';
import {readFileSync,existsSync} from 'node:fs';
const config=JSON.parse(readFileSync('.openai/hosting.json','utf8'));
process.stdin.setRawMode(true);process.stdin.resume();
process.stdout.write('Ready for Site credential JSON on stdin (input is hidden).\n');
let input='';
process.stdin.on('data',chunk=>{
  input+=chunk.toString();if(!input.includes('\n'))return;
  process.stdin.pause();process.stdin.setRawMode(false);
  try{
    const credential=JSON.parse(input.trim());input='';
    if(!credential.remote_url?.includes(config.project_id)||new URL(credential.remote_url).username)throw new Error('Source repository does not match the registered Site.');
    const env={...process.env,GIT_TERMINAL_PROMPT:'0'};
    delete env.GIT_TRACE;delete env.GIT_CURL_VERBOSE;delete env.GIT_TRACE_CURL;
    if(credential.auth_mode==='http_extra_header'){
      env.GIT_CONFIG_COUNT='1';env.GIT_CONFIG_KEY_0='http.extraHeader';env.GIT_CONFIG_VALUE_0='Authorization: Bearer '+credential.token;
    }else if(credential.auth_mode!=='work_proxy')throw new Error('Unsupported Git authentication mode.');
    const run=(args,auth=false)=>{
      const result=spawnSync('git',args,{env:auth?env:process.env,encoding:'utf8'});
      if(result.status!==0){let message=result.stderr||result.stdout;if(credential.token)message=message.split(credential.token).join('[REDACTED]');throw new Error(message);}
      return result.stdout.trim();
    };
    if(!existsSync('.git'))run(['init','-b',credential.branch]);
    run(['add','.']);
    if(run(['status','--porcelain']))run(['-c','user.name=Project build','-c','user.email=project@localhost','commit','-m','Publish interactive OVERPRINT studio with Java reference download']);
    const remotes=run(['remote']).split('\n');
    run(remotes.includes('origin')?['remote','set-url','origin',credential.remote_url]:['remote','add','origin',credential.remote_url]);
    run(['push','-u','origin','HEAD:refs/heads/'+credential.branch],true);
    const sha=run(['rev-parse','HEAD']);
    const remoteSha=run(['ls-remote','origin','refs/heads/'+credential.branch],true).split(/\s/)[0];
    if(remoteSha!==sha)throw new Error('Remote source SHA does not match local source.');
    console.log(JSON.stringify({project_id:config.project_id,commit_sha:sha,source_pushed:true}));process.exit(0);
  }catch(error){console.error(error.message);process.exit(1);}
});
