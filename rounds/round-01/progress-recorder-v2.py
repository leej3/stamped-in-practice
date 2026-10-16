"""Record launch/stop identities outside worker inputs without reading science."""
from pathlib import Path
import datetime,hashlib,json,shutil
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_once(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),str(dst)
 else:shutil.copy2(src,dst)
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
allocation=json.loads((D/'allocation.json').read_text());rows=[]
for dispatch in sorted(B.glob('round-??-wave-??/dispatch.json')):
 batch=json.loads(dispatch.read_text());rn=batch['round'];wn=batch['wave'];out=D/f'rounds/round-{rn:02d}/launches/wave-{wn:02d}';out.mkdir(parents=True,exist_ok=True)
 copy_once(dispatch,out/'dispatch.json');copy_once(B/'launch-wave.py',out/'dispatcher.py')
 for r in batch['records']:
  run=r['assignment']['run'];src=B/'runs'/run/'attempt-01';n=src/'native';dst=out/run
  if not (n/'launch.json').exists() or not (n/'events.jsonl').exists():continue
  first=(n/'events.jsonl').open().readline()
  if not first:continue
  event=json.loads(first);assert event['type']=='thread.started'
  for name in ['native/launch.json','native/procedure-status.json','native/prompt-preflight.json','native/condition-assignment.json','procedure-status.json','input-boundary.json','checkout.json','environment.json']:
   copy_once(src/name,dst/name)
  initial=dst/'native/thread-started.jsonl'
  if initial.exists():assert initial.read_text()==first
  else:initial.write_text(first)
  launch=json.loads((n/'launch.json').read_text());row={'run':run,'round':rn,'wave':wn,'condition':launch['condition'],'native_session_id':event['thread_id'],'started_at':launch['started_at'],'status':'running','starting_commit':launch['starting_commit'],'procedure_sha256':launch['procedure']['procedure_sha256'],'evidence':str(dst.relative_to(D))}
  final_dispatch=json.loads((B/'runs'/run/'dispatch.json').read_text())
  if final_dispatch['status']=='launcher-finished':
   result=json.loads((n/'result.json').read_text());copy_once(n/'result.json',dst/'native/result.json')
   row.update(status='stopped',finished_at=result['finished_at'],returncode=result['returncode'],elapsed_seconds=result['elapsed_seconds'],native_result_sha256=digest(n/'result.json'))
   if (n/'worker-end-state.json').exists():
    stop=json.loads((n/'worker-end-state.json').read_text());copy_once(n/'worker-end-state.json',dst/'native/worker-end-state.json')
    row.update(worker_head=stop.get('head_commit'),stop_sha256=digest(n/'worker-end-state.json'),capture=stop.get('capture'),capture_status=stop.get('capture_status'))
  rows.append(row)
 for name in ['result.json','stop-validation.json']:
  if (dispatch.parent/name).exists():copy_once(dispatch.parent/name,out/('wave-'+name))
 files=[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json']
 write(out/'manifest.json',{'scope':'Launch identities and finalized native/stop receipts when available; no scientific grading','files':files})
judges=[]
for dispatch in sorted(B.glob('round-??-judge-batch-??/dispatch.json')):
 batch=json.loads(dispatch.read_text());rn=batch['round'];bn=batch['batch'];out=D/f'rounds/round-{rn:02d}/judging/batch-{bn:02d}';out.mkdir(parents=True,exist_ok=True)
 copy_once(dispatch,out/'dispatch.json');copy_once(B/'launch-judgments.py',out/'dispatcher.py')
 for r in batch['records']:
  assignment=r['assignment'];run=assignment['run'];identifier=assignment['judgment'];source=B/'runs'/run/'judgments'/identifier;src=source/'attempt-01';n=src/'native';dst=out/identifier
  final=json.loads((source/'dispatch.json').read_text());row={'judgment':identifier,'run':run,'role':assignment['role'],'round':rn,'batch':bn,'status':final['status'],'native_started':False,'evidence':str(dst.relative_to(D))}
  for name in ['procedure-status.json','checkout.json','environment.json','native/launch.json','native/procedure-status.json','native/prompt-preflight.json','native/target.json']:
   if (src/name).is_file():copy_once(src/name,dst/name)
  events=n/'events.jsonl'
  if events.is_file():
   first=events.open().readline()
   if first:
    event=json.loads(first);assert event['type']=='thread.started';row.update(native_started=True,native_session_id=event['thread_id'])
    initial=dst/'native/thread-started.jsonl';initial.parent.mkdir(parents=True,exist_ok=True)
    if initial.exists():assert initial.read_text()==first
    else:initial.write_text(first)
  if final['status']=='launcher-finished':
   copy_once(source/'dispatch.json',dst/'dispatch-final.json');row.update(returncode=final['returncode'],finished_utc=final['finished_utc'])
   if (n/'result.json').exists():
    copy_once(n/'result.json',dst/'native/result.json');row['native_result_sha256']=digest(n/'result.json')
  judges.append(row)
 if (dispatch.parent/'result.json').exists():copy_once(dispatch.parent/'result.json',out/'batch-result.json')
 files=[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json']
 write(out/'manifest.json',{'scope':'Judgment dispatch/start/completion identities; no grades or response extraction','files':files})
jstarted=sum(r['native_started'] for r in judges);jstopped=sum(r['status']=='launcher-finished' for r in judges)
started=len(rows);stopped=sum(r['status']=='stopped' for r in rows);active=[r for r in rows if r['status']=='running']
write(D/'progress.json',{'comparison_id':'narps-neutral-v1','as_of_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sealed_registration_commit':'5056bebf6eb33c2b9b02262efc39d084259424ce','research_assigned':72,'research_started':started,'research_stopped':stopped,'judgments_assigned':96,'judgments_dispatched':len(judges),'judgments_started':jstarted,'judgments_finished_dispatches':jstopped,'judgments':judges,'current_round':max((r['round'] for r in rows),default=1),'current_wave':max((r['wave'] for r in rows),default=0),'runs':rows})
table='\n'.join(f"| {r['run']} | {r['condition']} | {r['status']} |" for r in rows)
(D/'STATUS.md').write_text(f'''# Current comparison status

The sealed tool-neutral comparison is underway: **{started} of 72 research workers have started**, **{stopped} have stopped**, and **{jstarted} of 96 assigned judgments have started** at this update.
The first round contains 24 workers and 32 judgments.
Judgment availability and scientific outcomes are reported separately from process completion.

| Run | Assigned assistance | State |
| --- | --- | --- |
{table}

See the [live ledger](progress.json), [launch and stop receipts](rounds/round-01/launches/), [sealed registration](registration.md) and [allocation](allocation.json).
The registration's zero-start count records its state before launch; it is not the live count.
The original registration and its hash manifest remain unchanged.

Each wave has three native sessions, and the next research wave starts after all three stop naturally.
All eight research waves finish before the round's independently randomized judging queue begins.
There is no preset spending, token or elapsed-time cap and no replacement selected for a favorable result.

Stopped deliveries include uncommitted and ignored files; their capture identities remain separate from actual worker Git HEADs and later coordinator preservation.
Separate workspaces and native profiles reduce shared context; the same-user host is not an operating-system containment boundary.
Coordinator retention and outer-session Duct capture earn no worker-practice credit.
''')
copy_once(Path(__file__),D/'rounds/round-01/progress-recorder-v2.py')
print(json.dumps({'started':started,'stopped':stopped,'running':[r['run'] for r in active]}))
