"""Independently verify published migration evidence and closed skill trials."""
from pathlib import Path
import subprocess,json,hashlib,tarfile,shutil,os
out=Path(__file__).parent/'reflection-fresh-check-01';out.mkdir(exist_ok=False)
shutil.copyfile(__file__,out/'verification.py');repo=out/'recipient';commands=[]
px=['pixi','run','--locked','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml']
def run(argv):
 p=subprocess.run(argv,cwd=out,capture_output=True,text=True,env=dict(os.environ,GIT_TERMINAL_PROMPT='0'),timeout=1200);n=len(commands)+1
 for suffix,value in [('stdout',p.stdout),('stderr',p.stderr)]:(out/f'{n:03d}.{suffix}').write_text(value)
 commands.append(dict(argv=argv,returncode=p.returncode,stdout=f'{n:03d}.stdout',stderr=f'{n:03d}.stderr'));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');p.check_returncode();return p.stdout
def git(*args):return run(['git','-C',str(repo),*args])
def annex(*args):return run(px+['git','-C',str(repo),'annex',*args])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(success=False,commit='4e2bb98adf6e75446d33ce6a105faab54f6b1fe0')
try:
 run(['git','clone','--depth','1','--single-branch','--branch','codex/iteration-narps-v1','https://github.com/leej3/stamped-in-practice.git',str(repo)])
 assert git('rev-parse','HEAD').strip()==result['commit']
 assert not (repo/'.git/objects/info/alternates').exists()
 git('fetch','--no-tags','origin','git-annex:refs/remotes/origin/git-annex');git('config','remote.origin.annex-ignore','true');annex('init','independent reflection preservation proof')
 git('remote','add','con-hub','https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git');git('config','remote.con-hub.annexurl','annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp');annex('merge')
 inventory=[json.loads(x) for x in annex('find','--anything','--json','--','migration/verification','skill-reflection').splitlines()]
 assert all(not (repo/x['file']).exists() for x in inventory)
 annex('get','--from','con-hub','--jobs','3','--','migration/verification','skill-reflection')
 for x in inventory:assert sha(repo/x['file'])==x['key'].split('--')[1].split('.')[0],x['file']
 copied=json.loads((repo/'migration/verification/retention-manifest.json').read_text())['files']
 for row in copied:assert sha(repo/row['path'])==row['sha256'],row['path']
 trials=[]
 for name,prefix,key in [('assessment-neutrality-trial-01','assessment-neutrality-trial-01','records'),('research-guidance-trial-01','research-guidance-trial-01','files')]:
  root=repo/'skill-reflection'/name;m=json.loads((root/'manifest.json').read_text());rows=m[key]
  with tarfile.open(root/'trial.tar.gz') as tar:
   members={x.name.rstrip('/'):x for x in tar.getmembers()}
   # Archives may retain the source root or put its contents at archive root.
   for row in rows:
    target=row['path'] if row['path'] in members else prefix+'/'+row['path'];member=members[target]
    if row['kind']=='symlink':assert member.issym() and member.linkname==row['target']
    elif row['kind']=='file':assert hashlib.sha256(tar.extractfile(member).read()).hexdigest()==row['sha256'],target
  trials.append(dict(name=name,files=len(rows),archive_sha256=sha(root/'trial.tar.gz'),manifest_sha256=sha(root/'manifest.json')))
 result.update(success=True,new_annex_paths=len(inventory),all_new_payloads_initially_absent=True,proof_files_verified=len(copied),trials=trials)
except Exception as e:result['error']=f'{type(e).__name__}: {e}'
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
raise SystemExit(0 if result['success'] else 1)
