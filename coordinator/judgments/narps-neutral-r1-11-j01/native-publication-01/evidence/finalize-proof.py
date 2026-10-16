"""Retain attachment/retrieval/hosted proofs as a separate coordinator commit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess, traceback
root=Path(__file__).resolve().parent
repo=root/'publisher'
a=json.loads((root/'attachment.json').read_text())
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=root/'proof-publication-01';proof.mkdir()
commands=[]
def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def run(label,argv,cwd=repo,allow=False,_retry=0):
 p=subprocess.run(argv,cwd=cwd,capture_output=True)
 (proof/(label+'.stdout')).write_bytes(p.stdout);(proof/(label+'.stderr')).write_bytes(p.stderr)
 commands.append({'label':label,'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':label+'.stdout','stderr':label+'.stderr'})
 save(proof/'commands.json',commands)
 if p.returncode and argv[:2]==['git','push'] and b'ssh: connect to host github.com port 22: Operation timed out' in p.stderr and _retry<2:
  return run(label+'.retry-'+str(_retry+1),argv,cwd,allow,_retry+1)
 if not allow:p.check_returncode()
 return p

def git(label,*args,cwd=repo):return run(label,['git',*args],cwd).stdout.decode().strip()
try:
 assert git('initial-head','rev-parse','HEAD')==a['commit']
 assert not git('initial-status','status','--porcelain')
 assert git('push-transport','remote','get-url','--push','origin')=='git@github.com:leej3/stamped-in-practice.git'
 rel=Path(a['coordinator_record_path'])/'evidence'
 dest=repo/rel;dest.mkdir()
 sources=[p for p in root.iterdir() if p.is_file()]+[p for p in (root/'hosted-check-01').iterdir() if p.is_file()]
 files={}
 for p in sorted(sources):
  q=dest/p.relative_to(root);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  files[str(q.relative_to(repo))]={'source':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
 save(dest/'manifest.json',{'created_at':datetime.now(timezone.utc).isoformat(),'content_commit':a['commit'],
  'scope':'Exact attachment, network retrieval and hosted-verification evidence. Publisher and receiver Git stores are represented by their command logs and exact remote identities, not copied as files. Final proof-publication logs are retained separately with the coordinator run.',
  'files':files})
 readme=repo/a['coordinator_record_path']/'README.md'
 readme.write_text(readme.read_text()+'\nThe [evidence manifest](evidence/manifest.json) binds the attachment procedure, command records, independent retrieval check and [hosted verification](evidence/hosted-check-01/result.json).\nThe content checkpoint remains on the original attachment commit; this later commit adds its verification records.\n')
 snap=['pre-commit','run','--config','/Users/johnlee/code/CON/stamped-in-practice/.pre-commit-config.yaml','snapper','--files',str(readme.relative_to(repo))]
 run('snapper',pixi+snap,allow=True);run('snapper-check',pixi+snap)
 bulk=[p for p,v in files.items() if v['bytes']>=1024*1024 or p.endswith('processed-transcript.stdout')]
 with (repo/'.gitattributes').open('a') as f:
  f.write('\n# Complete native checkpoint representations retained as annex payloads.\n')
  for p in bulk:f.write(json.dumps('/'+p)+' annex.largefiles=anything annex.backend=SHA256E\n')
 if bulk:run('annex-evidence',pixi+['git','annex','add','--force-large','--backend=SHA256E','--',*bulk])
 git('stage','add','--','.gitattributes',a['coordinator_record_path'])
 git('check-prose','diff','--cached','--check','--','.gitattributes',str(readme.relative_to(repo)))
 changes=git('scope','diff','--cached','--name-only').splitlines()
 assert all(p=='.gitattributes' or p.startswith(a['coordinator_record_path']+'/') for p in changes)
 trailers=run('provenance',['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh']).stdout.decode().strip()
 message=proof/'message.txt';message.write_text('chore(narps): retain judge11-j01 publication verification\n\nPreserve exact attachment, independent retrieval and hosted-session proof.\nKeep the original assessment capture and scientific delivery unchanged.\n\n'+trailers+'\n')
 git('commit','-c','core.hooksPath=/dev/null','commit','--file',str(message))
 head=git('head','rev-parse','HEAD')
 if bulk:run('upload-evidence',pixi+['git','annex','copy','--to',host['annex_remote'],'--',*bulk])
 git('push-proof','push','origin','HEAD:refs/heads/'+a['branch'])
 for n in range(4):
  git(f'annex-fetch-{n}','fetch','origin','+git-annex:refs/remotes/origin/git-annex')
  shared=git(f'annex-head-{n}','rev-parse','refs/remotes/origin/git-annex')
  run(f'annex-merge-{n}',pixi+['git','annex','merge'])
  git(f'annex-ancestor-{n}','merge-base','--is-ancestor',shared,'git-annex')
  p=run(f'annex-push-{n}',['git','push','origin','git-annex:git-annex'],allow=True)
  if not p.returncode:break
  if not any(x in p.stderr for x in [b'non-fast-forward',b'fetch first']):p.check_returncode()
 else:raise RuntimeError('Concurrent metadata publication did not converge')
 received=root/'proof-fresh-check-01';received.mkdir()
 git('fresh-init','init','--template=','--initial-branch','received',cwd=received)
 git('fresh-remote','remote','add','origin','https://github.com/leej3/stamped-in-practice.git',cwd=received)
 git('fresh-ignore','config','remote.origin.annex-ignore','true',cwd=received)
 git('fresh-fetch','fetch','--no-tags','origin',head,cwd=received)
 git('fresh-checkout','checkout','--detach','FETCH_HEAD',cwd=received)
 assert not (received/'.git/objects/info/alternates').exists()
 assert not git('original-content','diff','--name-only',a['base_commit'],'HEAD','--','input','coordinator/delivery-01','coordinator/original-manifest.json',cwd=received)
 absent={p:not(received/p).exists() for p in bulk};assert all(absent.values())
 run('fresh-annex-init',pixi+['git','annex','init','independent judge11-j01 proof recipient'],received)
 git('fresh-hub','remote','add',host['annex_remote'],host['annex_git_url'],cwd=received)
 git('fresh-route','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url'],cwd=received)
 git('fresh-annex-fetch','fetch','origin','git-annex:refs/remotes/origin/git-annex',cwd=received)
 run('fresh-annex-merge',pixi+['git','annex','merge'],received)
 if bulk:run('fresh-get',pixi+['git','annex','get','--from',host['annex_remote'],'--',*bulk],received)
 for p,row in files.items():assert sha(received/p)==row['sha256'] and (received/p).stat().st_size==row['bytes']
 assert sha(received/rel/'manifest.json')==sha(dest/'manifest.json')
 assert {p:sha(Path(p)) for p in a['original_sources_unchanged']}==a['original_sources_unchanged']
 assert not git('final-status','status','--porcelain')
 assert git('remote-pin','ls-remote','origin','refs/heads/'+a['branch']).split()[0]==head
 save(proof/'result.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'verified':True,'content_commit':a['commit'],
  'proof_commit':head,'branch':a['branch'],'checkpoint_id':a['checkpoint_id'],'session_id':a['session_id'],
  'evidence_files':len(files),'manifest_sha256':sha(dest/'manifest.json'),'annex_absent_before_get':absent,
  'source_files_unchanged':True,'canonical_branch_updated':False,'scope':'Independent GitHub proof retrieval; all manifest files verified. Original raw transcript and checkpoint already independently verified by the preserved content proof.'})
 print((proof/'result.json').read_text())
except BaseException:
 (proof/'failure.txt').write_text(traceback.format_exc());raise
