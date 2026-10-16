"""Copy exact stopped receipts into a new coordinator-only extraction directory."""
from pathlib import Path
import hashlib,json,sys
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset'
out=Path(sys.argv[1]).absolute();out.mkdir(exist_ok=False)
def artifact(src,dest):
 src=Path(src);dst=out/dest;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes();dst.write_bytes(data)
 return {'path':str(dst.relative_to(out)),'sha256':hashlib.sha256(data).hexdigest()}
def usage_evidence(native, destination):
 source=native/'events.jsonl';raw=source.read_bytes();selected=[]
 for line,record in enumerate(raw.splitlines(),1):
  event=json.loads(record)
  if event.get('type')=='turn.completed':selected.append({'line':line,'event_sha256':hashlib.sha256(record).hexdigest(),'event':event})
 receipt={'kind':'native-completed-turn-token-usage','source_path':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),'completed_turns':selected,'scope':'Reported parent native session completed-turn usage; separate child sessions excluded. Cached input and reasoning output are subsets, not additional totals. No provider billing inference.'}
 dst=out/destination;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(receipt,indent=2)+'\n')
 ref={'path':str(dst.relative_to(out)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}
 if len(selected)!=1:return ref,[]
 usage=selected[0]['event'].get('usage',{});metrics=[]
 for name in ['input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens']:
  if name not in usage:continue
  value=usage[name];assert isinstance(value,int) and value>=0
  scope='parent native session completed-turn reported tokens; excludes separate child sessions; not billing'
  if name=='cached_input_tokens':scope+='; subset of input_tokens'
  if name=='reasoning_output_tokens':scope+='; subset of output_tokens'
  metrics.append({'name':name,'value':value,'unit':'tokens','scope':scope})
 if 'cached_input_tokens' in usage:assert usage['cached_input_tokens']<=usage['input_tokens']
 if 'reasoning_output_tokens' in usage:assert usage['reasoning_output_tokens']<=usage['output_tokens']
 return ref,metrics
seal=artifact(D/'procedure.json','evidence/procedure.json')
index={'schema_version':3,'comparison_provenance':{'assessment_seal':seal,'research_procedure_sha256':seal['sha256']},'runs':[]}
retained={}
for path in B.glob('publisher-wave-??-01/published-complete-*.json'):
 for row in json.loads(path.read_text()):retained[row['run_id']]=row['commit']
for run in sorted((B/'runs').iterdir()):
 n=run/'attempt-01/native';resultpath=n/'result.json';stoppath=n/'worker-end-state.json'
 if not resultpath.is_file() or not stoppath.is_file():continue
 dispatch=json.loads((run/'dispatch.json').read_text())
 if dispatch['status']!='launcher-finished':continue
 result=json.loads(resultpath.read_bytes());stop=json.loads(stoppath.read_bytes());seed=json.loads((run/'attempt-01/input-boundary.json').read_bytes())
 prefix='evidence/'+run.name
 resultref=artifact(resultpath,prefix+'/native-result.json')
 row={'run_id':run.name,'result_commit':stop.get('head_commit'),'worker_head':stop.get('head_commit'),'seed_commit':seed['seed_commit'],
      'worker_completion':'completed' if result['returncode']==0 else 'failed',
      'worker_end_state':artifact(stoppath,prefix+'/worker-end-state.json'),
      'delivery_capture':artifact(n/'original-delivery/manifest.json',prefix+'/capture-manifest.json'),
      'worker_input':artifact(run/'attempt-01/input-boundary.json',prefix+'/input-boundary.json'),
      'worker_native':{'procedure_status':artifact(n/'procedure-status.json',prefix+'/procedure-status.json'),'result':resultref},
      'operations':[{'operation_id':run.name+'-native-research','stage':'worker','actor':'worker',
                     'status':'succeeded' if result['returncode']==0 else 'failed',
                     'scope':'native research session elapsed wall time; process completion, not scientific adequacy or billing',
                     'evidence':[resultref],'duration_s':result['elapsed_seconds']} ]}
 if run.name in retained:row['retention_commit']=retained[run.name]
 usage_ref,metrics=usage_evidence(n,prefix+'/native-token-usage.json');row['operations'][0]['evidence'].append(usage_ref);row['operations'][0]['metrics']=metrics
 if seed['condition']=='stamped-explicit':row['skill_commit']='f2e74ea3ed372f966c95692cb0826d56ad5e6a6c'
 index['runs'].append(row)
# Coordinator publications remain distinct from original worker identities.
registry=json.loads(Path('/Users/johnlee/code/CON/stamped-in-practice/studies/narps/neutral-retention-publications.json').read_text())
by_run={row['run_id']:row for row in index['runs']}
for published in registry['runs']:
 if published['run_id'] in by_run:by_run[published['run_id']]['retention_commit']=published['commit']
judgment_count=0
for path in sorted((B/'judgment-extractions').glob('*/extraction.json')):
 record=json.loads(path.read_text());row=by_run[record['run_id']];judgment=dict(record['judgment']);prefix='evidence/'+record['run_id']+'/judgments/'+judgment['judgment_id']
 supplement_path=path.parent/'manual-extraction-supplement.json'
 if supplement_path.exists():
  supplement=json.loads(supplement_path.read_text())
  assert supplement['kind']=='manual-explicit-label-extraction'
  assert supplement['previous_extraction_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
  assert supplement['report_sha256']==judgment['report']['sha256']
  assert supplement['raw_response_modified'] is False and supplement['formal_admission_changed'] is False
  judgment['adequacy']=supplement['adequacy']
  artifact(supplement_path,prefix+'/manual-extraction-supplement.json')
 def exact(ref,name):
  source=Path(ref['path']);assert hashlib.sha256(source.read_bytes()).hexdigest()==ref['sha256'],str(source)
  return artifact(source,prefix+'/'+name)
 for key in ['response','report','scientific_report','output_binding']:
  if key in judgment:judgment[key]=exact(judgment[key],key+Path(judgment[key]['path']).suffix)
 judgment['native']={key:exact(ref,'native-'+key+'.json') for key,ref in judgment['native'].items()}
 row.setdefault('judgments',{})[record['role']]=judgment;judgment_count+=1
 for operation in record.get('operations',[]):
  operation=dict(operation);operation['evidence']=[exact(ref,operation['operation_id']+'-evidence-'+str(i)+Path(ref['path']).suffix) for i,ref in enumerate(operation['evidence'])];row['operations'].append(operation)
 native_source=Path(record['judgment']['native']['result']['path']).parent
 usage_ref,metrics=usage_evidence(native_source,prefix+'/native-token-usage.json')
 for operation in row['operations']:
  if operation['operation_id']==judgment['judgment_id']+'-native':operation['evidence'].append(usage_ref);operation['metrics']=metrics
 artifact(path,prefix+'/coordinator-extraction.json')
 artifact(path.parent/'source-binding-evidence.json',prefix+'/source-binding-evidence.json')
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
(out/'build-extraction.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'stopped_runs':len(index['runs']),'judgments':judgment_count,'output':str(out)}))
