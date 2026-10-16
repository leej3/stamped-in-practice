from pathlib import Path
from datetime import datetime, timezone
import collections
import hashlib
import json
import os
import re
import subprocess
import tomllib
import tomlkit

ROOT=Path('/Users/johnlee/code/CON/stamped-in-practice')
STATE=Path.home()/'.local/state/stamped-in-practice'
OUT=STATE/'initial-launch-audit-01'
SHA='c6f01b00ee6a4469be70eb8c85cc8a2553e6ef616e3b7fb8bc46707acaae4bd4'
RUNS=['narps-r1-07','narps-r1-08','narps-r1-09']
report={'schema_version':1,'observed_at':datetime.now(timezone.utc).isoformat(),'scope':'Initial launch context only; no worker results assessed or worker files changed.','runs':[],'findings':[],'pending':[],'sources':[]}
def digest(data):return hashlib.sha256(data).hexdigest()
def source(path):
 data=path.read_bytes();report['sources'].append({'path':str(path),'bytes':len(data),'sha256':digest(data)});return data
def read(path):return json.loads(source(path))
def check(ok,message):
 if not ok:report['findings'].append(message)
def git(repo,*args,allowed=(0,)):
 env=os.environ.copy();env.update(GIT_OPTIONAL_LOCKS='0',GIT_TERMINAL_PROMPT='0')
 r=subprocess.run(['git','--no-optional-locks','-C',str(repo),*args],capture_output=True,env=env)
 if r.returncode not in allowed:raise RuntimeError('Read-only Git command failed: '+str(args))
 return r.stdout,r.returncode
def g(repo,*args):return git(repo,*args)[0].decode().strip()
proc=read(ROOT/'iterations/narps-v1/procedure.json');check(digest((ROOT/'iterations/narps-v1/procedure.json').read_bytes())==SHA,'Coordinator procedure digest')
allocation=read(ROOT/'iterations/narps-v1/allocation.json');check([x['run'] for x in allocation['rounds'][0]['launch_order'][:3]]==RUNS,'Requested first three allocation identities')
conditions=read(ROOT/'conditions.json');expectedassignment=conditions['conditions']['discover-science']
source_config=tomllib.loads((Path.home()/'.local/state/stamped-ai-research-next/codex-public-v3-20261015/config.toml').read_text())
approved=Path('/Users/johnlee/code/CON/stamped-ai-research-next/.codex/hooks.json')
common=[]
for run in RUNS:
 e=STATE/'narps-v1'/run/'launch';native=e/'native'
 required=['checkout.json','input-boundary.json','procedure-status.json','procedure.json','resource-readiness.json','research-prompt.md','preparation.json','native/launch.json','native/prompt-preflight.json','native/condition-assignment.json','native/procedure-status.json','native/prompt.txt','native/events.jsonl']
 missing=[x for x in required if not (e/x).is_file()]
 if missing:
  report['pending'].append({'run':run,'missing_setup_files':missing});continue
 checkout=read(e/'checkout.json');seed=read(e/'input-boundary.json');status=read(e/'procedure-status.json');launchproc=read(e/'procedure.json');ready=read(e/'resource-readiness.json');prep=read(e/'preparation.json');launch=read(native/'launch.json');preflight=read(native/'prompt-preflight.json');assignment=read(native/'condition-assignment.json');native_status=read(native/'procedure-status.json')
 repo=Path(checkout['checkout']);start=checkout['worker_commit'];profile=Path(launch['codex_home'])
 for section in (status,native_status,launch['procedure']):check(section.get('status')=='formal-verified' and section.get('procedure_sha256')==SHA,run+' formal procedure receipt')
 check(digest((e/'procedure.json').read_bytes())==SHA and launchproc==proc,run+' exact frozen procedure')
 check(ready.get('ready') is True and ready.get('complete') is True and ready['requirements_sha256']==proc['resources']['sha256'],run+' resource readiness gate')
 check(seed['condition']==assignment['condition']==launch['condition']==preflight['condition']=='discover-science',run+' assigned condition')
 check(seed['assignment']['supplied_skills']==assignment['supplied_skills']==[] and assignment['supplied_skills_commit'] is None,run+' no supplied skills')
 check(seed['assignment']['additional_prompt']==expectedassignment['additional_prompt'],run+' discovery prompt')
 check(seed['study_commit']==proc['study']['commit'] and seed['study_input_tree']==proc['study']['input_tree'],run+' study pin')
 check(seed['source_manifest_sha256']==proc['starting_environment']['sha256']['pixi.toml'],run+' source environment manifest')
 check(seed['coordinator_commit']==checkout['base_commit']==assignment['coordinator_commit'],run+' coordinator source receipt')
 for name,sha in proc['fixed_files'].items():check(digest(git(ROOT,'show',seed['coordinator_commit']+':'+name)[0])==sha,run+' frozen executing source '+name)
 roots=g(repo,'rev-list','--parents','-n','1',start).split();check(roots==[start],run+' parentless seed')
 committed_seed=json.loads(git(repo,'show',start+':worker-input.json')[0]);check(committed_seed==seed,run+' committed seed receipt')
 tree=g(repo,'ls-tree','-r','--name-only',start).splitlines();allowed={x['path'] for x in seed['inputs']}|{'pixi.toml','.gitignore','.gitattributes','worker-input.json'};check(set(tree)==allowed,run+' exact initial file allowlist')
 check(not (repo/'.git/objects/info/alternates').exists() and not (repo/'.git/objects/info/http-alternates').exists(),run+' no object alternates')
 missing_objects={}
 for label,oid in [('selected_coordinator',seed['coordinator_commit']),('sealed_coordinator',proc['coordinator_commit']),('study_history',seed['study_commit']),('starting_snapshot',proc['starting_environment']['commit']),('assessor_source',proc['assessment']['source_commit'])]:
  _,rc=git(repo,'cat-file','-e',oid+'^{commit}',allowed=(0,1,128));missing_objects[label]=rc!=0;check(rc!=0,run+' excluded '+label+' object')
 common_input=digest(json.dumps(seed['inputs'],sort_keys=True,separators=(',',':')).encode())
 source_manifest=git(ROOT,'show',seed['coordinator_commit']+':pixi.toml')[0];doc=tomlkit.parse(source_manifest.decode());doc.pop('tasks',None)
 for feature in doc.get('feature',{}).values():feature.pop('tasks',None)
 worker_manifest=git(repo,'show',start+':pixi.toml')[0];check(worker_manifest==tomlkit.dumps(doc).encode(),run+' initial worker manifest projection')
 current_lock=repo/'pixi.lock';locksha=digest(current_lock.read_bytes()) if current_lock.is_file() else None
 # Record only current lock identity: workers may legitimately change it later.
 lock_matches=locksha==proc['starting_environment']['sha256']['pixi.lock']
 prompt=source(e/'research-prompt.md');nativeprompt=source(native/'prompt.txt');check(prompt==nativeprompt and digest(prompt)==assignment['prompt_sha256']==launch['prompt_sha256'],run+' submitted prompt identity')
 check(assignment['capture_execution'] is True and b'with duct under `logs/`' in prompt,run+' requested execution capture')
 check(preflight['private_marker_count']==0 and preflight['project_instructions_present'] is False and not preflight['unexpected_skill_catalog'] and preflight['visible_study_skills']==[],run+' clean effective prompt preflight')
 catalog=preflight['advertised_skill_catalog'];check(all(Path(x['path']).is_relative_to(profile/'skills/.system') for x in catalog),run+' only built-in initial skill catalog')
 check(all(digest(Path(x['path']).read_bytes())==x['sha256'] for x in catalog),run+' built-in catalog hashes')
 cmd=launch['command'];check(cmd[cmd.index('-m')+1]=='gpt-6-luna' and 'model_reasoning_effort="high"' in cmd,run+' model and effort');check(launch['timeout_seconds']==0 and launch['review_seconds']==5400,run+' no hard deadline and review timing');check(launch['cwd']==str(repo) and launch['starting_commit']==start,run+' exact native launch checkout')
 skill_arg=next(x for x in cmd if x.startswith('skills.config='));overrides=tomllib.loads(skill_arg)['skills']['config'];check(all(x['enabled'] is False for x in overrides),run+' no host skills enabled by launch overrides')
 check('project_doc_max_bytes=0' in cmd,run+' inherited project document exclusion')
 cfgbytes=source(profile/'config.toml');cfg=tomllib.loads(cfgbytes.decode());check(digest(cfgbytes)==preflight['profile_config_sha256'],run+' unchanged launch profile config')
 hookpath=repo/'.codex/hooks.json';hooks=source(hookpath);check(digest(hooks)==prep['native_hooks_sha256']==proc['host_identity']['approved_hooks_sha256'] and hooks==approved.read_bytes(),run+' exact approved hook bytes')
 hookkeys=[]
 for event,groups in json.loads(hooks)['hooks'].items():
  name=re.sub(r'(?<!^)(?=[A-Z])','_',event).lower()
  for i,group in enumerate(groups):
   for j,hook in enumerate(group.get('hooks',[])):
    suffix=f'{name}:{i}:{j}';hookkeys.append(suffix);target=cfg.get('hooks',{}).get('state',{}).get(str(hookpath)+':'+suffix,{});original=source_config.get('hooks',{}).get('state',{}).get(str(approved)+':'+suffix,{})
    check(bool(target.get('trusted_hash')) and target.get('trusted_hash')==original.get('trusted_hash') and not target.get('disabled') and not hook.get('disabled'),run+' native hook approval '+suffix)
 check(cfg['projects'].get(str(repo),{}).get('trust_level')=='trusted',run+' project trust')
 eventbytes=(native/'events.jsonl').read_bytes();events=[]
 for line in eventbytes.splitlines():
  try:events.append(json.loads(line))
  except json.JSONDecodeError:pass
 ids=[x.get('thread_id') for x in events if x.get('type')=='thread.started'];check(len(ids)==1,run+' unique real native session')
 state_path=repo/'.git/entire-sessions'/(ids[0]+'.json');session_bytes=state_path.read_bytes();session=json.loads(session_bytes)
 check(session.get('session_id')==ids[0] and session.get('agent_type')=='Codex' and session.get('worktree_path')==str(repo) and session.get('model_name')=='gpt-6-luna',run+' live Entire session identity')
 summary={'run':run,'checkout':str(repo),'coordinator_commit':seed['coordinator_commit'],'seed_commit':start,'seed_parentless':roots==[start],'initial_paths':len(tree),'input_inventory_sha256':common_input,'inputs':len(seed['inputs']),'annex_inputs':sum('annex_key' in x for x in seed['inputs']),'study_commit':seed['study_commit'],'study_input_tree':seed['study_input_tree'],'initial_worker_manifest_sha256':digest(worker_manifest),'current_working_lock_sha256':locksha,'current_lock_matches_registered_start':lock_matches,'starting_environment_commit':proc['starting_environment']['commit'],'starting_environment_lock_sha256':proc['starting_environment']['sha256']['pixi.lock'],'condition':assignment['condition'],'supplied_skills':assignment['supplied_skills'],'prompt_sha256':digest(prompt),'capture_execution_requested':True,'excluded_history_objects':missing_objects,'profile':str(profile),'effective_catalog':[{'name':x['name'],'sha256':x['sha256']} for x in catalog],'host_skill_overrides_disabled':len(overrides),'native_hooks_approved':len(hookkeys),'started_at':launch['started_at'],'session_id':ids[0],'entire_phase':session.get('phase'),'entire_checkpoint_count_at_audit':session.get('checkpoint_count'),'entire_session_state_sha256_at_audit':digest(session_bytes),'events_read_bytes':len(eventbytes),'events_read_sha256':digest(eventbytes),'event_type_counts':dict(collections.Counter(x.get('type') for x in events)),'native_session_and_live_entire_state_match':True,'publication_enabled_at_setup':prep['publication_enabled']}
 report['runs'].append(summary);common.append((seed['coordinator_commit'],common_input,digest(worker_manifest),digest(prompt),[(x['name'],x['sha256']) for x in catalog]))
check(len({json.dumps(x) for x in common})<=1,'Matched launches have identical source/input/manifest/prompt/catalog')
check(len({r['profile'] for r in report['runs']})==len(report['runs']),'Independent session profiles')
check([r['run'] for r in sorted(report['runs'],key=lambda x:x['started_at'])]==RUNS[:len(report['runs'])],'Native launch order matches first allocation entries')
report['initial_context_passed']=not report['findings'] and not report['pending']
report['limitations']=['Audits initial supplied context and independent Git stores, not filesystem confinement: native workers have authorized danger-full-access and network access.','The exact registered starting environment is checked by the launcher before launch; this audit separately records the current lock hash, which workers may legitimately evolve.','Live native session and Entire recognition are verified; final condensed checkpoints, publication and hosted worker-session proof are future completion/retention checks, not claimed here.','Execution capture is requested in the assigned prompt and receipt; actual analysis logs/results are outside this initial-context audit.','No private reasoning or scientific outputs were printed or retained by this audit; live event bytes were hashed and event types/identity inspected only.']
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'report':str(OUT/'report.json'),'passed':report['initial_context_passed'],'findings':report['findings'],'pending':report['pending'],'runs':[{k:r[k] for k in ('run','started_at','session_id','current_lock_matches_registered_start','native_hooks_approved')} for r in report['runs']]},indent=2))
