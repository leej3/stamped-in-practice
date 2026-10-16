from pathlib import Path
import hashlib,json,subprocess
base=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');source=base/'dataset';root=base/'preparation-fresh-check-01';root.mkdir();recipient=root/'recipient';rows=[]
def run(argv,cwd):
 r=subprocess.run(list(map(str,argv)),cwd=cwd,capture_output=True,text=True);rows.append({'argv':list(map(str,argv)),'cwd':str(cwd),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(root/'commands.json').write_text(json.dumps(rows,indent=2)+'\n');r.check_returncode();return r.stdout.strip()
main='/Users/johnlee/code/CON/stamped-in-practice';manifest=main+'/pixi.toml';pixi=['pixi','run','--locked','--manifest-path',manifest]
head=run(['git','rev-parse','HEAD'],source)
run(['git','clone','--depth','1','--branch','codex/iteration-narps-neutral-v1','https://github.com/leej3/stamped-in-practice.git',recipient],main)
assert run(['git','rev-parse','HEAD'],recipient)==head
modules=run(['git','submodule','status'],recipient).splitlines();assert len(modules)==3 and all(x.startswith('-') for x in modules)
run(['git','config','remote.origin.annex-ignore','true'],recipient)
run(pixi+['git','annex','init','neutral-registration-independent-receiver'],recipient)
run(['git','remote','add','con-hub','https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git'],recipient)
run(['git','config','remote.con-hub.annexurl','annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp'],recipient)
run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],recipient)
run(pixi+['git','annex','merge'],recipient)
lock='resources/common-environment/validated-environment.lock'
run(pixi+['git','annex','get','--from','con-hub','--',lock],recipient)
expected=hashlib.sha256((source/lock).read_bytes()).hexdigest();actual=hashlib.sha256((recipient/lock).read_bytes()).hexdigest();assert expected==actual
allocation=json.loads((recipient/'allocation.json').read_text());assert allocation['total_workers']==72 and allocation['total_judgments']==96
report={'success':True,'commit':head,'gitlinks_uninitialized':modules,'lock_sha256':actual,'lock_bytes':(recipient/lock).stat().st_size,'allocation_sha256':hashlib.sha256((recipient/'allocation.json').read_bytes()).hexdigest(),'status':'preparation, not sealed and no formal worker launched','scope':'Fresh public Git read and independent authenticated annex payload retrieval; no source dataset initialization or science run'}
(root/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
