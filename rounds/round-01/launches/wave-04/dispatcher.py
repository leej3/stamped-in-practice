"""Dispatch one preregistered research wave through the native Pixi task."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,time
ROOT=Path('/Users/johnlee/code/CON/stamped-in-practice')
STATE=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
DATASET=STATE/'dataset'
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
parser=argparse.ArgumentParser();parser.add_argument('--round',type=int,required=True);parser.add_argument('--wave',type=int,required=True);args=parser.parse_args()
registration=json.loads((DATASET/'registration.json').read_text());assert registration['status']=='sealed'
assert hashlib.sha256((DATASET/'procedure.json').read_bytes()).hexdigest()==registration['procedure_sha256']
assert hashlib.sha256((DATASET/'allocation.json').read_bytes()).hexdigest()==registration['allocation_sha256']
plan=json.loads((DATASET/f'rounds/round-{args.round:02d}/plan.json').read_text());assert plan['status']=='sealed-before-launch'
workers=sorted([w for w in plan['worker_assignments'] if w['wave']==args.wave],key=lambda w:w['launch_position']);assert len(workers)==3
out=STATE/f'round-{args.round:02d}-wave-{args.wave:02d}';out.mkdir(exist_ok=False)
records=[];processes=[]
for worker in workers:
 run=STATE/'runs'/worker['run'];run.mkdir(parents=True,exist_ok=False)
 command=['pixi','run','--locked','launch','--host-config',str(Path.home()/'.config/stamped-in-practice/launch-neutral.json'),'--protocol','neutral-v1','--repo',str(ROOT),'--branch','codex/'+worker['run'],'--base',plan['coordinator_source_commit'],'--study',str(ROOT/'studies/narps'),'--condition',worker['condition'],'--common-resources',str(DATASET/'resources/common-resources.md'),'--skills-source',str(ROOT/'skills'),'--clone-path',str(STATE/'workspaces'/worker['run']),'--evidence',str(run/'attempt-01'),'--run-mode','formal','--procedure',str(DATASET/'procedure.json'),'--procedure-sha256',registration['procedure_sha256'],'--resource-readiness',str(STATE/'readiness-01/result.json'),'--capture-execution']
 stdout=(run/'launcher.stdout').open('wb');stderr=(run/'launcher.stderr').open('wb')
 process=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
 record={'assignment':worker,'argv':command,'pid':process.pid,'dispatched_utc':utc(),'status':'launcher-dispatched','note':'Task delivery/native start must be confirmed from native events, not this dispatch receipt.'}
 records.append(record);processes.append((process,stdout,stderr,record))
 (run/'dispatch.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'run':worker['run'],'pid':process.pid,'status':'launcher-dispatched'}),flush=True)
(out/'dispatch.json').write_text(json.dumps({'round':args.round,'wave':args.wave,'records':records},indent=2)+'\n')
while processes:
 for process,stdout,stderr,record in list(processes):
  code=process.poll()
  if code is not None:
   stdout.close();stderr.close();record.update(status='launcher-finished',returncode=code,finished_utc=utc())
   (STATE/'runs'/record['assignment']['run']/'dispatch.json').write_text(json.dumps(record,indent=2)+'\n')
   processes.remove((process,stdout,stderr,record));print(json.dumps({'run':record['assignment']['run'],'returncode':code,'status':'launcher-finished'}),flush=True)
 if processes: time.sleep(2)
(out/'result.json').write_text(json.dumps({'round':args.round,'wave':args.wave,'records':records,'all_launcher_returncodes_zero':all(r['returncode']==0 for r in records)},indent=2)+'\n')
