from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,traceback
root=Path(__file__).resolve().parent;repo=root/'publisher'
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked']
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
prepared=json.loads((root/'prepared.json').read_text());commands=[]
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv,required=True):
 p=subprocess.run(argv,cwd=repo,capture_output=True,text=True)
 commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 save(root/'commands-publish.json',commands)
 if required:p.check_returncode()
 return p
try:
 files=[e['published_path'] for e in prepared['copied_files'] if e['storage']=='annex']
 run(pixi+['git','annex','copy','--to',host['annex_remote'],'--',*files])
 run(['git','push','-u','origin','codex/narps-neutral-r1-20-browsable'])
 for attempt in range(3):
  run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'])
  run(pixi+['git','annex','merge'])
  pushed=run(['git','push','origin','git-annex:git-annex'],required=False)
  if pushed.returncode==0:break
  if not any(s in pushed.stderr for s in ['non-fast-forward','fetch first']):pushed.check_returncode()
 else:raise RuntimeError('Concurrent annex metadata push did not converge after3attempts')
 head=run(['git','rev-parse','HEAD']).stdout.strip()
 assert head==json.loads((root/'commit.json').read_text())['commit']
 save(root/'publication.json',{'at':datetime.now(timezone.utc).isoformat(),'commit':head,'branch':'codex/narps-neutral-r1-20-browsable','annex_files_uploaded':files,'independent_retrieval':'pending'})
 print(json.dumps({'published':True,'commit':head,'annex_files':len(files)}))
except Exception:
 (root/'failure-publish.txt').write_text(traceback.format_exc());raise
