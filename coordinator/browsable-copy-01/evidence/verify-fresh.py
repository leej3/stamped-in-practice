from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,traceback
root=Path(__file__).resolve().parent;base=root.parent
check=root/'fresh-check-01';check.mkdir();repo=check/'recipient';repo.mkdir()
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked']
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
published=json.loads((root/'publication.json').read_text());original=json.loads((root/'prepared.json').read_text())
input_manifest=base/'dataset/input-manifest.json';inputs=json.loads(input_manifest.read_text());commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def run(argv):
 p=subprocess.run(argv,cwd=repo,text=True,capture_output=True)
 commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 save(check/'commands.json',commands);p.check_returncode();return p.stdout.strip()
try:
 run(['git','init','--initial-branch','received'])
 run(['git','remote','add','origin','https://github.com/leej3/stamped-in-practice.git'])
 run(['git','config','remote.origin.annex-ignore','true'])
 run(['git','fetch','--no-tags','origin',published['commit']])
 run(['git','checkout','--detach','FETCH_HEAD'])
 assert not (repo/'.git/objects/info/alternates').exists()
 assert run(['git','rev-parse','HEAD:input'])==inputs['input_tree']
 assert sha(repo/'coordinator/browsable-copy-01/manifest.json')==sha(root/'publisher/coordinator/browsable-copy-01/manifest.json')
 assert sha(repo/'coordinator/delivery-01/index.json')==sha(root/'publisher/coordinator/delivery-01/index.json')
 annex=[e for e in original['copied_files'] if e['storage']=='annex']
 absent={e['published_path']:not (repo/e['published_path']).exists() for e in annex}
 assert all(absent.values())
 run(pixi+['git','annex','init','independent browsable delivery receiver'])
 run(['git','remote','add',host['annex_remote'],host['annex_git_url']])
 run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']])
 run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'])
 run(pixi+['git','annex','merge'])
 for e in annex:assert run(pixi+['git','annex','lookupkey',e['published_path']])==e['annex_key']
 paths=[e['published_path'] for e in annex]+[e['path'] for e in inputs['files'] if e.get('annex_key')]
 run(pixi+['git','annex','get','--from',host['annex_remote'],'--',*paths])
 for e in original['copied_files']:
  assert sha(repo/e['published_path'])==e['sha256'] and (repo/e['published_path']).stat().st_size==e['bytes']
 for e in inputs['files']:
  assert sha(repo/e['path'])==e['sha256'] and (repo/e['path']).stat().st_size==e['bytes']
 assert run(['git','rev-parse','HEAD'])==published['commit']
 assert run(['git','status','--porcelain'])==''
 save(check/'result.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'verified':True,'commit':published['commit'],'scope':'Fresh empty Git store with network fetch and authenticated annex retrieval; same host, no scientific execution.','alternates':False,'original_delivery_archive_index_unchanged':True,'copied_files_verified':len(original['copied_files']),'copied_annex_files_absent_before_get':absent,'input_files_verified':len(inputs['files']),'input_manifest_sha256':sha(input_manifest),'command_log_sha256':sha(check/'commands.json')})
 print(json.dumps({'verified':True,'commit':published['commit'],'files':len(original['copied_files']),'inputs':len(inputs['files'])}))
except Exception:
 (check/'failure.txt').write_text(traceback.format_exc());raise
