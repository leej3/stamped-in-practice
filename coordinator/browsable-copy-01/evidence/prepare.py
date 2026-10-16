from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,stat,subprocess,traceback
root=Path(__file__).resolve().parent;base=root.parent
repo=root/'publisher';repo.mkdir()
main=Path('/Users/johnlee/code/CON/stamped-in-practice')
pixi=['pixi','run','--manifest-path',str(main/'pixi.toml'),'--locked']
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
plan_path=base/'browsable-delivery-plan-01/narps-neutral-r1-20.json'
plan=json.loads(plan_path.read_text());capture=Path(plan['capture_manifest']['path'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(capture)==plan['capture_manifest']['sha256']
commands=[]
def save(p,j):p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def run(argv):
 p=subprocess.run(list(map(str,argv)),cwd=repo,text=True,capture_output=True)
 commands.append({'argv':list(map(str,argv)),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 save(root/'commands-prepare.json',commands);p.check_returncode();return p.stdout.strip()
try:
 run(['git','init','--initial-branch','codex/narps-neutral-r1-20-browsable'])
 run(['git','remote','add','origin','git@github.com:leej3/stamped-in-practice.git'])
 run(['git','config','remote.origin.annex-ignore','true'])
 run(['git','fetch','--no-tags','origin','23c2cb0f0fe443d21bea4f8bb57101e5d89ae932'])
 run(['git','reset','--hard','FETCH_HEAD'])
 run(pixi+['git','annex','init','narps-neutral-r1-20 browsable coordinator copy'])
 run(['git','remote','add',host['annex_remote'],host['annex_git_url']])
 run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']])
 run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'])
 run(pixi+['git','annex','merge'])
 copied=[]
 for e in plan['entries']:
  path=e['path'];dest=repo/path;src=capture.parent/e['capture_path']
  assert not dest.exists() and not dest.is_symlink(),path
  if e['action']=='directory-no-placeholder':continue
  assert e['action'] in ['copy-to-git','copy-to-annex'] and e['kind']=='file'
  st=src.lstat();assert stat.S_ISREG(st.st_mode) and st.st_size==e['size'] and stat.S_IMODE(st.st_mode)==e['mode']
  assert sha(src)==e['sha256']
  dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as stream:stream.write(src.read_bytes())
  os.chmod(dest,e['mode'])
  assert sha(dest)==e['sha256']
  copied.append({'original_path':path,'published_path':path,'kind':e['kind'],'source_mode':e['mode'],'bytes':e['size'],'sha256':e['sha256'],'storage':'git' if e['action']=='copy-to-git' else 'annex'})
 annex_files=[e['published_path'] for e in copied if e['storage']=='annex']
 with (repo/'.gitattributes').open('a') as stream:
  stream.write('\n# Coordinator publication of unchanged original scientific files.\n')
  for p in annex_files:stream.write(p+' annex.largefiles=anything annex.backend=SHA256E\n')
 run(pixi+['git','annex','add','--force-large','--backend=SHA256E','--',*annex_files])
 for e in copied:
  dest=repo/e['published_path'];assert sha(dest)==e['sha256']
  if e['storage']=='annex':e['annex_key']=run(pixi+['git','annex','lookupkey',e['published_path']])
 assert sha(capture)==plan['capture_manifest']['sha256']
 save(root/'prepared.json',{'prepared_at':datetime.now(timezone.utc).isoformat(),'parent_commit':'23c2cb0f0fe443d21bea4f8bb57101e5d89ae932','plan_sha256':sha(plan_path),'capture_sha256':sha(capture),'source_worker_head':plan['original_worker_head'],'publisher':str(repo),'copied_files':copied,'scientific_execution':False,'source_files_unchanged':True,'command_log_sha256':sha(root/'commands-prepare.json')})
 print(json.dumps({'prepared':True,'files':len(copied),'annex_files':len(annex_files)}))
except Exception:
 (root/'failure-prepare.txt').write_text(traceback.format_exc());raise
