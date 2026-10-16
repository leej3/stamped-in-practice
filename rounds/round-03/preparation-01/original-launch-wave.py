"""Dispatch one preregistered research wave through the native Pixi task."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,time
ROOT=Path('/Users/johnlee/.local/share/wt-utils/worktrees/4af0/stamped-in-practice')
SKILLS=Path('/Users/johnlee/code/CON/stamped-in-practice/skills')
STATE=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
DATASET=STATE/'dataset'
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
parser=argparse.ArgumentParser();parser.add_argument('--round',type=int,required=True);parser.add_argument('--wave',type=int,required=True);args=parser.parse_args()
registration=json.loads((DATASET/'registration.json').read_text());assert registration['status']=='sealed'
assert hashlib.sha256((DATASET/'procedure.json').read_bytes()).hexdigest()==registration['procedure_sha256']
assert hashlib.sha256((DATASET/'allocation.json').read_bytes()).hexdigest()==registration['allocation_sha256']
assert args.round==2 and args.wave in range(1,9)
allocation=json.loads((DATASET/'allocation.json').read_bytes());registered=allocation['rounds'][args.round-1]
binding_path=DATASET/'rounds/round-02/preparation-01/source-skill-binding.json'
assert hashlib.sha256(binding_path.read_bytes()).hexdigest()=='9524612ab6efa04443928c77171c156f6f2139df06f6253da972c9087de3b817'
binding=json.loads(binding_path.read_bytes())
plan=json.loads((DATASET/f'rounds/round-{args.round:02d}/plan.json').read_text());assert plan['status']=='sealed-before-launch'
assert plan['round']==args.round==registered['round']==binding['round']
assert plan['worker_assignments']==registered['launch_order']==binding['worker_assignments']
assert plan['assigned_judgments']==registered['judgment_dispatch_order']==binding['assigned_judgments']
assert plan['coordinator_source_commit']==binding['coordinator_source_commit']=='9068886f91615b2c69578bdaa6042a858f4d9011'
assert plan['research_guidance_commit']==binding['research_guidance_commit']=='d83d7d66a9060be6afae57336124afdcfc1743e9'
assert registration['procedure_sha256']==binding['research_procedure_sha256']=='b011f6e68dc6838e736f1ae2ad70d52896dab9b848d6f33950b4d35dd86b1521'
assert registration['allocation_sha256']==binding['original_allocation_sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==plan['coordinator_source_commit']
assert subprocess.check_output(['git','rev-parse',plan['coordinator_source_commit']+':skills'],cwd=ROOT,text=True).strip()==plan['research_guidance_commit']
workers=sorted([w for w in plan['worker_assignments'] if w['wave']==args.wave],key=lambda w:w['launch_position']);assert len(workers)==3
out=STATE/f'round-{args.round:02d}-wave-{args.wave:02d}';out.mkdir(exist_ok=False)
records=[];processes=[]
for worker in workers:
 run=STATE/'runs'/worker['run'];run.mkdir(parents=True,exist_ok=False)
 command=['pixi','run','--locked','launch','--host-config',str(Path.home()/'.config/stamped-in-practice/launch-neutral.json'),'--protocol','neutral-v1','--repo',str(ROOT),'--branch','codex/'+worker['run'],'--base',plan['coordinator_source_commit'],'--study',str(ROOT/'studies/narps'),'--condition',worker['condition'],'--common-resources',str(DATASET/'resources/common-resources.md'),'--skills-source',str(SKILLS),'--clone-path',str(STATE/'workspaces'/worker['run']),'--evidence',str(run/'attempt-01'),'--run-mode','formal','--procedure',str(DATASET/'procedure.json'),'--procedure-sha256',registration['procedure_sha256'],'--resource-readiness',str(STATE/'readiness-01/result.json'),'--capture-execution']
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
