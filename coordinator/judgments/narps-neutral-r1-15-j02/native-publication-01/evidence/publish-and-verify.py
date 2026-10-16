"""Publish captured judge15-j02 evidence and independently retrieve exact bytes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import traceback

root=Path(__file__).resolve().parent
repo=root/'publisher'
a=json.loads((root/'attachment.json').read_text())
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
commands=[]

def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def run(label,argv,cwd=repo,allow=False,_retry=0):
    p=subprocess.run(argv,cwd=cwd,capture_output=True)
    (root/(label+'.stdout')).write_bytes(p.stdout)
    (root/(label+'.stderr')).write_bytes(p.stderr)
    commands.append({'label':label,'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':label+'.stdout','stderr':label+'.stderr'})
    save(root/'publish-commands.json',commands)
    if p.returncode and argv[:2]==['git','push'] and b'ssh: connect to host github.com port 22: Operation timed out' in p.stderr and _retry<2:
     return run(label+'.retry-'+str(_retry+1),argv,cwd,allow,_retry+1)
    if not allow:p.check_returncode()
    return p

def git(label,*args,cwd=repo):return run(label,['git',*args],cwd).stdout.decode().strip()

try:
    assert git('publish-head','rev-parse','HEAD')==a['commit']
    assert not git('publish-status','status','--porcelain')
    assert git('publish-remote','remote','get-url','--push','origin')=='git@github.com:leej3/stamped-in-practice.git'
    assert not git('branch-absent','ls-remote','origin','refs/heads/'+a['branch'])
    run('upload-transcripts',pixi+['git','annex','copy','--to',host['annex_remote'],'--',*a['annex_paths']])
    git('push-code-and-checkpoint','push','origin','HEAD:refs/heads/'+a['branch'],a['checkpoint_ref']+':'+a['checkpoint_ref'])
    for n in range(3):
        git(f'annex-fetch-{n}','fetch','origin','+git-annex:refs/remotes/origin/git-annex')
        shared=git(f'annex-remote-head-{n}','rev-parse','refs/remotes/origin/git-annex')
        run(f'annex-merge-{n}',pixi+['git','annex','merge'])
        git(f'annex-ancestor-{n}','merge-base','--is-ancestor',shared,'git-annex')
        p=run(f'annex-push-{n}',['git','push','origin','git-annex:git-annex'],allow=True)
        if not p.returncode:break
        if not any(x in p.stderr for x in [b'non-fast-forward',b'fetch first']):p.check_returncode()
    else:raise RuntimeError('Concurrent annex metadata did not converge')
    actual={line.split()[1]:line.split()[0] for line in git('published-refs','ls-remote','origin','refs/heads/'+a['branch'],a['checkpoint_ref']).splitlines()}
    assert actual=={'refs/heads/'+a['branch']:a['commit'],a['checkpoint_ref']:a['checkpoint_oid']}
    save(root/'publication.json',dict(a,published_refs=actual,published_at=datetime.now(timezone.utc).isoformat()))
    recipient=root/'fresh-check-01';recipient.mkdir()
    git('receiver-init','init','--template=','--initial-branch','received',cwd=recipient)
    git('receiver-remote','remote','add','origin','https://github.com/leej3/stamped-in-practice.git',cwd=recipient)
    git('receiver-ignore-origin','config','remote.origin.annex-ignore','true',cwd=recipient)
    git('receiver-fetch','fetch','--no-tags','origin',a['commit'],cwd=recipient)
    git('receiver-checkout','checkout','--detach','FETCH_HEAD',cwd=recipient)
    assert not (recipient/'.git/objects/info/alternates').exists()
    assert git('receiver-head','rev-parse','HEAD',cwd=recipient)==a['commit']
    assert not git('receiver-originals','diff','--name-only',a['base_commit'],'HEAD','--','input','coordinator/delivery-01','coordinator/original-manifest.json',cwd=recipient)
    absent={p:not (recipient/p).exists() for p in a['annex_paths']};assert all(absent.values())
    run('receiver-annex-init',pixi+['git','annex','init','independent judge15-j02 native receiver'],recipient)
    git('receiver-hub','remote','add',host['annex_remote'],host['annex_git_url'],cwd=recipient)
    git('receiver-route','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url'],cwd=recipient)
    git('receiver-annex-fetch','fetch','origin','git-annex:refs/remotes/origin/git-annex',cwd=recipient)
    run('receiver-annex-merge',pixi+['git','annex','merge'],recipient)
    run('receiver-transcript-get',pixi+['git','annex','get','--from',host['annex_remote'],'--',*a['annex_paths']],recipient)
    files=json.loads((root/'payloads.json').read_text())
    dest=recipient/a['coordinator_record_path']
    for name,row in files.items():
        assert sha(dest/name)==row['sha256'] and (dest/name).stat().st_size==row['bytes']
    git('receiver-checkpoint-fetch','fetch','origin',a['checkpoint_ref']+':'+a['checkpoint_ref'],cwd=recipient)
    assert git('receiver-checkpoint-id','rev-parse',a['checkpoint_ref'],cwd=recipient)==a['checkpoint_oid']
    metadata=json.loads(git('receiver-checkpoint-metadata','show',a['checkpoint_ref']+':0/metadata.json',cwd=recipient))
    assert metadata['checkpoint_id']==a['checkpoint_id'] and metadata['session_id']==a['session_id']
    processed=run('receiver-processed-transcript',['git','show',a['checkpoint_ref']+':0/full.jsonl'],recipient).stdout
    assert hashlib.sha256(processed).hexdigest()==a['processed_sha256']
    assert not git('receiver-final-status','status','--porcelain',cwd=recipient)
    assert {p:sha(Path(p)) for p in a['original_sources_unchanged']}==a['original_sources_unchanged']
    save(root/'fresh-verification.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'verified':True,
       'commit':a['commit'],'checkpoint_id':a['checkpoint_id'],'session_id':a['session_id'],
       'checkpoint_ref':a['checkpoint_ref'],'checkpoint_oid':a['checkpoint_oid'],
       'annex_absent_before_get':absent,'source_files_verified':len(files),'processed_sha256':a['processed_sha256'],
       'scope':'Empty independent Git store, exact GitHub commit and checkpoint refs, authorized Hub retrieval. No original-source changes or scientific execution. Hosted service visibility is checked separately.'})
    print(json.dumps({'published':True,'independent_retrieval_verified':True,'commit':a['commit'],'checkpoint_id':a['checkpoint_id']}))
except BaseException:
    (root/'publish-failure.txt').write_text(traceback.format_exc());raise
