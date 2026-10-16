"""Publish one reviewed presentation branch and its new annex payloads."""
from pathlib import Path
import json, subprocess, sys, traceback
root=Path(sys.argv[1]).resolve();repo=root/'publisher'
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked']
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
prepared=json.loads((root/'prepared.json').read_text());commit=json.loads((root/'commit.json').read_text());commands=[]
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv,allow=False,_retry=False):
    p=subprocess.run(argv,cwd=repo,capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    save(root/'commands-publish.json',commands)
    if not _retry and p.returncode == 128 and 'ssh: connect to host github.com port 22: Operation timed out' in p.stderr and argv[:2] in [['git','fetch'],['git','ls-remote'],['git','push']]: return run(argv,allow,True)
    if not allow:p.check_returncode()
    return p
try:
    assert not (root/'publication.json').exists()
    assert run(['git','rev-parse','HEAD']).stdout.strip()==commit['commit']
    assert run(['git','status','--porcelain']).stdout.strip()==''
    assert run(['git','remote','get-url','--push','origin']).stdout.strip()=='git@github.com:leej3/stamped-in-practice.git'
    assert run(['git','ls-remote','origin','refs/heads/'+commit['branch']]).stdout.strip()==''
    if prepared['annex_files']:run(pixi+['git','annex','copy','--to',host['annex_remote'],'--',*prepared['annex_files']])
    run(['git','push','-u','origin','HEAD:refs/heads/'+commit['branch']])
    for attempt in range(3):
        run(['git','fetch','origin','+git-annex:refs/remotes/origin/git-annex'])
        shared=run(['git','rev-parse','refs/remotes/origin/git-annex']).stdout.strip()
        run(pixi+['git','annex','merge'])
        assert run(['git','rev-parse','HEAD']).stdout.strip()==commit['commit']
        run(['git','merge-base','--is-ancestor',shared,'git-annex'])
        pushed=run(['git','push','origin','git-annex:git-annex'],allow=True)
        if pushed.returncode==0:break
        if not any(s in pushed.stderr for s in ['non-fast-forward','fetch first']):pushed.check_returncode()
    else:raise RuntimeError('Shared metadata did not converge in three attempts')
    metadata=run(['git','rev-parse','git-annex']).stdout.strip()
    actual={x.split()[1]:x.split()[0] for x in run(['git','ls-remote','origin','refs/heads/'+commit['branch'],'refs/heads/git-annex']).stdout.splitlines()}
    assert actual=={'refs/heads/'+commit['branch']:commit['commit'],'refs/heads/git-annex':metadata}
    save(root/'publication.json',dict(commit,annex_metadata_commit=metadata,annex_files_uploaded=prepared['annex_files'],independent_retrieval='pending'))
    print(json.dumps({'published':True,**commit}))
except BaseException:
    (root/'failure-publish.txt').write_text(traceback.format_exc());raise
