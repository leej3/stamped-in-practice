from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
MAIN=Path('/Users/johnlee/code/CON/stamped-in-practice')
PIXI=['pixi','run','--manifest-path',str(MAIN/'pixi.toml'),'--locked']
row=json.loads((ROOT/'prepared.json').read_bytes())
repo=Path(row['publisher'])
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_bytes())
commands=[]

def save(path, value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def run(argv,cwd,allow=False):
 argv=list(map(str,argv));p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
 commands.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 save(ROOT/'publish-verify-retry-02-commands.json',commands)
 if not allow:p.check_returncode()
 return p.stdout.strip() if not allow else p
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

try:
 assert run(['git','rev-parse','HEAD'],repo)==row['commit']
 assert run(['git','remote','get-url','--push','origin'],repo)=='git@github.com:leej3/stamped-in-practice.git'
 run(['git','push','origin','HEAD:refs/heads/'+row['branch']],repo)
 assert run(['git','ls-remote','origin','refs/heads/'+row['branch']],repo).split()[0]==row['commit']
 run(PIXI+['git','annex','copy','--to',host['annex_remote'],'--',row['archive_path']],repo)
 for attempt in range(3):
  run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],repo)
  run(PIXI+['git','annex','merge'],repo)
  p=run(['git','push','origin','git-annex:git-annex'],repo,True)
  if not p.returncode:break
  if 'non-fast-forward' not in p.stderr and 'fetch first' not in p.stderr:p.check_returncode()
 else:raise RuntimeError('Shared annex metadata push did not settle')
 recipient=ROOT/'fresh-recipient';recipient.mkdir()
 assert not list(recipient.iterdir())
 run(['git','init','--initial-branch','received'],recipient)
 run(['git','remote','add','origin','https://github.com/leej3/stamped-in-practice.git'],recipient)
 run(['git','config','remote.origin.annex-ignore','true'],recipient)
 run(['git','fetch','--no-tags','origin',row['commit']],recipient)
 run(['git','checkout','--detach','FETCH_HEAD'],recipient)
 assert not (recipient/'.git/objects/info/alternates').exists()
 archive=recipient/row['archive_path'];assert not archive.exists()
 run(PIXI+['git','annex','init',row['run_id']+' independent complete support receiver'],recipient)
 run(['git','remote','add',host['annex_remote'],host['annex_git_url']],recipient)
 run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']],recipient)
 run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],recipient)
 run(PIXI+['git','annex','merge'],recipient)
 assert run(PIXI+['git','annex','lookupkey',row['archive_path']],recipient)==row['archive_key']
 run(PIXI+['git','annex','get','--from',host['annex_remote'],'--',row['archive_path']],recipient)
 assert sha(archive)==row['archive_sha256'] and archive.stat().st_size==row['archive_bytes']
 package=recipient/'coordinator/support-01'
 assert sha(package/'publication-files.json')==row['publication_manifest_sha256']
 files=json.loads((package/'publication-files.json').read_bytes())
 for item in files:
  path=recipient/item['path'];assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes'],item['path']
 spec=importlib.util.spec_from_file_location('support_verifier',package/'prepare.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 verification=module.verify_archive(archive,json.loads((package/'support-archive-inventory.json').read_bytes()))
 assert verification['verified']
 changed=run(['git','diff','--name-only',row['base'],row['commit']],recipient).splitlines()
 assert changed and all(p=='.gitattributes' or p.startswith('coordinator/') for p in changed)
 assert run(['git','rev-parse','HEAD^'],recipient)==row['base']
 assert run(['git','rev-parse','HEAD:input'],recipient)==run(['git','rev-parse',row['base']+':input'],recipient)
 assert run(['git','status','--porcelain'],recipient)==''
 save(ROOT/'result.json',{**row,'verified':True,'fresh_recipient':str(recipient),
      'archive_absent_before_get':True,'alternate_object_store':False,
      'ordinary_files_verified':len(files)-1,'archive_verification':verification,
      'scientific_paths_unchanged':True,'input_tree_unchanged':True})
 print(json.dumps({'verified':True,'commit':row['commit'],'members':verification['members']}))
except BaseException as exc:
 save(ROOT/'publish-verify-retry-02-failure.json',{'type':type(exc).__name__,'error':str(exc)})
 raise
