"""Retain coordinator observations from exact stopped native event citations."""
from pathlib import Path
import datetime,hashlib,json
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
sha=lambda x:hashlib.sha256(x).hexdigest()
records={
'23':({'discovery':False,'installation':False,'loaded':False,'application':'no successful skill use observed','notes':['One command attempted the path skills/.system/../x with stderr suppressed and an unconditional true fallback. The combined exit0 is not evidence that this path existed or executed.','No catalog listing, installed skill, entrypoint load or subsequent application was observed. The path probe remains recorded as ambiguous attempted activity.']},{'skill_path_probe':[15]}),
'18':({'discovery':True,'installation':True,'loaded':True,'application':'notebook scaffold and executions observed; intermediate execution failure retained','source_repository':'https://github.com/openai/skills','source_revision':None,'catalog_count':39,'notes':['Installed jupyter-notebook in .skills, read entrypoint and experiment/quality references, checked helper usage and scaffolded a notebook.','Notebook execution to workspace tmp/ first succeeded; a later modified execution failed, then a corrected command succeeded. All variants remain in native evidence.','Source commit unresolved in observed installation; exact installed bytes and workspace outputs are retained.']},{'installer_loaded':[11],'catalog':[15],'installation':[18],'skill_loaded':[20],'references_loaded':[36],'helper_usage':[38],'scaffold':[47],'execution_success':[80,85],'execution_failure':[82]}),
'05':({'discovery':False,'installation':False,'loaded':True,'application':'supplied loop, conventions and validation instructions loaded','source_repository':'https://github.com/con/skills','source_revision':'f2e74ea3ed372f966c95692cb0826d56ad5e6a6c','notes':['Loaded do-full-research-loop, stamped-conventions and validation guidance, then re-read validation and enumerated its reference directory.','No worker skill installation was observed; supplied link targets are preserved separately by the availability supplement. Procedural reads are not evidence of causal benefit.']},{'loop_loaded':[6],'conventions_validation_loaded':[8],'validation_reread_and_reference_listing':[11]})}
for num,(observations,selections) in records.items():
 name='narps-neutral-r1-'+num;n=B/'runs'/name/'attempt-01/native';path=B/'runs'/name/'retention/skill-use-observations.json';assert not path.exists()
 source=n/'events.jsonl';raw=source.read_bytes();lines=raw.splitlines(keepends=True);events=[json.loads(x) for x in lines]
 assert any(e['type']=='turn.completed' for e in events)
 ev={k:[{'line':i,'item_id':events[i-1].get('item',{}).get('id'),'event_sha256':sha(lines[i-1].rstrip(b'\n')),'event':events[i-1]} for i in values] for k,values in selections.items()}
 sources=[]
 for filename in ['events.jsonl','launch.json','result.json','worker-end-state.json','skill-observations.json','condition-assignment.json','prompt-preflight.json']:
  p=n/filename;d=p.read_bytes();sources.append({'path':str(p),'sha256':sha(d),'bytes':len(d)})
 o={'schema_version':1,'kind':'coordinator-skill-use-observations','run_id':name,'extracted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assigned_condition':json.loads((n/'launch.json').read_text())['condition'],'scope':{'scientific_adequacy_assessed':False,'causal_effect_assessed':False,'worker_files_modified':False,'native_stream_line_count':len(lines),'complete_turn_observed':True,'limitation':'Availability is not use; observed procedural action is not causal benefit. Per-install duration is not inferred from reduced events.'},'observations':observations,'evidence':ev,'sources':sources}
 path.write_text(json.dumps(o,indent=2)+'\n');assert source.read_bytes()==raw
 print(name,sha(path.read_bytes()))
