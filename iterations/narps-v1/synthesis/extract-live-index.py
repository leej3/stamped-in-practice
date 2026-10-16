"""Coordinator extraction: exact stopped receipts and explicit report labels, no regrading."""
import argparse,datetime,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--repo',default='/Users/johnlee/code/CON/stamped-in-practice');a=p.parse_args();repo=Path(a.repo);base=Path.home()/'.local/state/stamped-in-practice/narps-v1';out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def native(folder):return {'procedure_status':ref(folder/'native/procedure-status.json'),'result':ref(folder/'native/result.json')}
def session_op(folder,identity,stage,actor,role=None):
 r=load(folder/'native/result.json');op={'operation_id':identity,'stage':stage,'actor':actor,'status':'succeeded' if r['returncode']==0 else 'failed','scope':'complete native session wall time','duration_s':r['elapsed_seconds'],'evidence':[ref(folder/'native/result.json')]};events=folder/'native/events.jsonl';usages=[]
 for line in events.read_text().splitlines():
  e=json.loads(line)
  if e.get('type')=='turn.completed' and 'usage' in e:usages.append(e['usage'])
 if usages:
  op['evidence'].append(ref(events));keys=set.intersection(*(set(x) for x in usages));op['metrics']=[{'name':k,'value':sum(u[k] for u in usages),'unit':'tokens','scope':'sum of native completed-turn usage; overlapping token categories are not summed together'} for k in sorted(keys)]
 if role=='supplementary':op['supplementary_attempt_id']=identity.removesuffix('-session')
 elif role:op['judgment_role']=role
 return op
policy=load(repo/'iterations/narps-v1/measurement-disposition-01.json');index={'schema_version':2,'comparison_provenance':{'assessment_seal':ref(repo/'iterations/narps-v1/amendment-01/procedure.json'),'research_procedure_sha256':policy['research_procedure_sha256']},'runs':[]};notes=[]
alloc=load(repo/'iterations/narps-v1/allocation.json')
for assignment in alloc['rounds'][0]['launch_order']:
 run=assignment['run'];folder=base/run;native_result=folder/'launch/native/result.json'
 if not native_result.exists():continue
 result=load(native_result);w=Path(result['cwd']);row={'run_id':run,'result_commit':result['worker_end_state']['head_commit'],'worker_head':result['worker_end_state']['head_commit'],'seed_commit':result['starting_commit'],'worker_end_state':ref(folder/'launch/native/worker-end-state.json'),'worker_native':native(folder/'launch'),'worker_input':ref(w/'worker-input.json'),'worker_completion':'completed' if result['returncode']==0 else 'failed','skill_commit':'c90252a7b9072a4828e9c0b1fa6e5f48409a9cfa','judgments':{},'operations':[session_op(folder/'launch',run+'-worker','worker','worker')]}
 receipt=folder/('retention/recipient-check-02/result.json' if run in {'narps-r1-10','narps-r1-12'} else 'retention/recipient-check-01/result-complete.json')
 if not receipt.exists():receipt=folder/'retention/recipient-check-01/result.json'
 if receipt.exists():
  proof=load(receipt);passed=proof.get('success',proof.get('passed',False));stop=load(folder/'launch/native/worker-end-state.json');annex_count=proof.get('annex_paths',proof.get('annex_paths_verified',proof.get('annex_files')))
  op={'operation_id':run+'-coordinator-independent-retrieval','stage':'output-retrieval','actor':'coordinator','status':'succeeded' if passed else 'failed','scope':'independent full stopped-object retrieval; coordinator preservation','evidence':[ref(receipt)],'recipient':'researcher with authorized configured Git and annex access','route':'SSH Git publication plus configured con-hub annex transport; see retained command receipts','artifact_class':'complete stopped research object: regular files and annex payloads','required_coverage':str(len(stop['worktree']))+' stop-inventory paths','verified_coverage':('all stop paths; '+str(annex_count)+' annex paths' if passed else 'see failed receipt'),'host_scope':'independent recipient checkout on the same host; not cross-host portability'}
  byte_count=proof.get('unique_annex_bytes',proof.get('annex_bytes_verified',proof.get('annex_bytes')))
  if byte_count is not None:op['metrics']=[{'name':'verified_annex_bytes','value':byte_count,'unit':'bytes','scope':'annex payload coverage reported by independent receipt; alias convention follows receipt'}]
  row['operations'].append(op)
 for disposition in policy['judgments']:
  if disposition['run_id']!=run:continue
  jid=disposition['judgment_id'];attempt=jid.removeprefix(run+'-');role=disposition['role'];j=folder/attempt;binding=folder/'retention'/f'{attempt}-output-binding.json'
  if not (j/'native/result.json').exists() or not binding.exists():continue
  bd=load(binding);report=Path(bd['outputs']['report']['path']);response=Path(bd['outputs']['response']['path']);record={'judgment_id':jid,'native':native(j),'output_binding':ref(binding),'response':ref(response),'report':ref(report)};candidates=[]
  if 'scientific_report' in bd['outputs']:
   report=Path(bd['outputs']['scientific_report']['path']);record['scientific_report']=ref(report)
  for n,line in enumerate(report.read_text().splitlines(),1):
   m=re.search(r'Scientific adequacy\s*:\s*(?:\*\*)?\s*(not supported|unable to assess|supported|qualified)\b',line,re.I)
   if m:candidates.append((n,line,m.group(1).lower()))
  if (run,attempt)==('narps-r1-01','judgment-01'):
   candidates=[(n,line,'qualified') for n,line in enumerate(report.read_text().splitlines(),1) if line.startswith('**Adequacy: qualified.**')]
  if (run,attempt)==('narps-r1-10','judgment-01'):
   line=report.read_text().splitlines()[20];assert '**Classification: supported**' in line;candidates=[(21,line,'supported')]
  special={('narps-r1-03','judgment-02'):(82,'**Classification: supported.**'),('narps-r1-04','judgment-02'):(98,'**Classification: supported**'),('narps-r1-11','judgment-02'):(78,'**Scientific adequacy for the reported conclusion: supported.**')}.get((run,attempt))
  if special:
   n,expected=special;line=report.read_text().splitlines()[n-1];assert expected in line;candidates=[(n,line,'supported')]
  if (run,attempt)==('narps-r1-02','judgment-01'):
   line=report.read_text().splitlines()[76];assert '**Classification: qualified.**' in line;candidates=[(77,line,'qualified')]
  if len(candidates)==1:
   n,line,cat=candidates[0];record['adequacy']={'extraction_status':'explicit','category':cat,'excerpt':{'quote':line,'start_line':n,'end_line':n}}
  else:record['adequacy']={'extraction_status':'missing' if not candidates else 'ambiguous','category':None}
  conclusion_line={('narps-r1-03','judgment-02'):84,('narps-r1-04','judgment-02'):98,('narps-r1-11','judgment-02'):78,('narps-r1-10','judgment-01'):21,('narps-r1-11','judgment-01'):76,('narps-r1-07','judgment-03'):78,('narps-r1-03','judgment-01'):7,('narps-r1-04','judgment-01'):3,('narps-r1-12','judgment-01'):81,('narps-r1-05','judgment-01'):75,('narps-r1-06','judgment-01'):81,('narps-r1-01','judgment-01'):70,('narps-r1-02','judgment-01'):77,('narps-r1-07','judgment-01'):19,('narps-r1-08','judgment-01'):81,('narps-r1-07','judgment-02'):21,('narps-r1-09','judgment-01'):75}.get((run,attempt))
  if conclusion_line:
   quote=report.read_text().splitlines()[conclusion_line-1]
   record['conclusion']={'quote':quote,'start_line':conclusion_line,'end_line':conclusion_line}
  if role=='supplementary':
   record['reason']='Repair attempt retained separately; does not replace first-assigned primary or preselected duplicate.';row.setdefault('supplementary_attempts',[]).append(record)
  else:row['judgments'][role]=record
  row['operations'].append(session_op(j,jid+'-session','judging','judge',role))
  replay=report.parent/'2026-10-16-fresh-rerun.json'
  if replay.exists():
   rr=load(replay);entries=[s for s in rr.get('steps',[]) if s.get('step','').startswith('entry:')];op={'operation_id':jid+'-replay','stage':'replay','actor':'judge','status':{'met':'succeeded','partial':'partial','unmet':'failed','not-checked':'not-checked'}.get(rr.get('status'),'unknown'),'scope':'single authorized same-host fresh-clone replay','evidence':[ref(replay)],'replay_attempt_observed':True,'helper_completed':bool(rr.get('finished_at')),'entrypoint_executed':bool(entries),'replay_status':rr.get('status')}
   if role=='supplementary':op['supplementary_attempt_id']=jid
   else:op['judgment_role']=role
   if entries:op['entrypoint_returncode']=entries[-1]['returncode']
   comp=rr.get('comparison')
   if comp:
    mapping={'identical_outputs':'identical','within_tolerance_outputs':'within_tolerance','differing_outputs':'differing','missing_outputs':'missing_after_rerun'}
    for key,src in mapping.items():op[key]=len(comp.get(src,[]))
    op['compared_outputs']=sum(op[k] for k in mapping)
   try:op['duration_s']=(datetime.datetime.fromisoformat(rr['finished_at'])-datetime.datetime.fromisoformat(rr['started_at'])).total_seconds()
   except (KeyError,ValueError):pass
   row['operations'].append(op)
 index['runs'].append(row)
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n');(out/'extract_index.py').write_bytes(Path(__file__).read_bytes());(out/'extraction-record.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'index_sha256':sha(out/'index.json'),'disposition':ref(repo/'iterations/narps-v1/measurement-disposition-01.json'),'limitations':['Exact report labels extracted, not independently regraded.','Only finalized session bindings included; missing slots stay pending.','Token categories overlap and are retained separately.','This live-path index must be remapped to retained experiment paths before final publication.']},indent=2)+'\n');print(out/'index.json')
