"""Dispatch one ordered group of assigned judgments after all round research stops."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,time
ROOT=Path('/Users/johnlee/code/CON/stamped-in-practice')
STATE=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');DATASET=STATE/'dataset'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text())
parser=argparse.ArgumentParser();parser.add_argument('--round',type=int,required=True);parser.add_argument('--batch',type=int,required=True);parser.add_argument('--describe',action='store_true');args=parser.parse_args()
registration=read(DATASET/'registration.json');assert registration['status']=='sealed'
assert hashlib.sha256((DATASET/'procedure.json').read_bytes()).hexdigest()==registration['procedure_sha256']
assert hashlib.sha256((DATASET/'allocation.json').read_bytes()).hexdigest()==registration['allocation_sha256']
plan=read(DATASET/f'rounds/round-{args.round:02d}/plan.json');assert plan['status']=='sealed-before-launch'
allocation=read(DATASET/'allocation.json');procedure=read(DATASET/'procedure.json')
registered_round=next(r for r in allocation['rounds'] if r['round']==args.round)
assert plan['round']==args.round and plan['procedure_sha256']==registration['procedure_sha256']
assert plan['coordinator_source_commit']==procedure['coordinator_commit']
assert plan['worker_assignments']==registered_round['launch_order']
assert plan['assigned_judgments']==registered_round['judgment_dispatch_order']
assert len(plan['worker_assignments'])==24 and len(plan['assigned_judgments'])==32
assert plan['maximum_simultaneous_native_sessions']==3 and plan['research_before_judgment'] is True
ordered=sorted(plan['assigned_judgments'],key=lambda j:j['dispatch_order']);selected=ordered[3*(args.batch-1):3*args.batch];assert args.batch>0 and selected
commands=[]
for assignment in selected:
 run=assignment['run'];identifier=assignment['judgment'];source=STATE/'runs'/run/'attempt-01';output=STATE/'runs'/run/'judgments'/identifier
 command=['pixi','run','--locked','launch','--host-config',str(Path.home()/'.config/stamped-in-practice/launch-neutral.json'),'--protocol','neutral-v1','--role','judge','--repo',str(ROOT),'--branch','codex/'+identifier,'--base',plan['coordinator_source_commit'],'--study',str(ROOT/'studies/narps'),'--seed-receipt',str(source/'input-boundary.json'),'--delivery-capture',str(source/'native/original-delivery/manifest.json'),'--worker-end-state',str(source/'native/worker-end-state.json'),'--clone-path',str(STATE/'judge-targets'/identifier),'--evidence',str(output/'attempt-01'),'--run-mode','formal','--procedure',str(DATASET/'procedure.json'),'--procedure-sha256',registration['procedure_sha256'],'--resource-readiness',str(STATE/'readiness-01/result.json'),'--capture-execution']
 commands.append((assignment,output,command))
if args.describe:
 print(json.dumps({'description_only':True,'round':args.round,'batch':args.batch,'commands':[{'assignment':a,'argv':c} for a,o,c in commands]},indent=2));raise SystemExit(0)
# Completion, not favorable outcomes, unlocks judging. Capture failures remain
# explicit missing measurements; no replacement judgment is selected here.
for worker in plan['worker_assignments']:
 dispatch=STATE/'runs'/worker['run']/'dispatch.json';assert dispatch.exists() and read(dispatch)['status']=='launcher-finished','Research still active or not dispatched: '+worker['run']
for previous in range(1,args.batch):
 receipt=STATE/f'round-{args.round:02d}-judge-batch-{previous:02d}/result.json';assert receipt.exists(),'Prior judgment group remains unfinished'
out=STATE/f'round-{args.round:02d}-judge-batch-{args.batch:02d}';out.mkdir(exist_ok=False)
records=[];processes=[]
for assignment,output,command in commands:
 output.mkdir(parents=True,exist_ok=False)
 stdout=(output/'launcher.stdout').open('wb');stderr=(output/'launcher.stderr').open('wb')
 process=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
 record={'assignment':assignment,'argv':command,'pid':process.pid,'dispatched_utc':utc(),'status':'launcher-dispatched','note':'Native start and target binding require native receipts; no outcome is inferred from dispatch.'};records.append(record);processes.append((process,stdout,stderr,record,output))
 (output/'dispatch.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'judgment':assignment['judgment'],'pid':process.pid,'status':'launcher-dispatched'}),flush=True)
(out/'dispatch.json').write_text(json.dumps({'round':args.round,'batch':args.batch,'records':records},indent=2)+'\n')
while processes:
 for process,stdout,stderr,record,output in list(processes):
  code=process.poll()
  if code is not None:
   stdout.close();stderr.close();record.update(status='launcher-finished',returncode=code,finished_utc=utc());(output/'dispatch.json').write_text(json.dumps(record,indent=2)+'\n');processes.remove((process,stdout,stderr,record,output));print(json.dumps({'judgment':record['assignment']['judgment'],'returncode':code,'status':'launcher-finished'}),flush=True)
 if processes:time.sleep(2)
(out/'result.json').write_text(json.dumps({'round':args.round,'batch':args.batch,'records':records},indent=2)+'\n')
