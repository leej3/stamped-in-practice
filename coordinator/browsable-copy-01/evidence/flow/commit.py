"""Commit one already reviewed staged presentation copy with fresh attribution."""
from pathlib import Path
import json, subprocess, sys, traceback
root=Path(sys.argv[1]).resolve(); repo=root/'publisher'
prepared=json.loads((root/'prepared.json').read_text()); commands=[]
def save(p,v): p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv):
    p=subprocess.run(list(map(str,argv)),cwd=repo,capture_output=True,text=True)
    commands.append({'argv':list(map(str,argv)),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    save(root/'commands-commit.json',commands);p.check_returncode();return p.stdout.strip()
try:
    assert not (root/'commit.json').exists()
    assert run(['git','rev-parse','HEAD'])==prepared['parent_commit']
    run(['git','diff','--cached','--check','--','.gitattributes','coordinator'])
    trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'])
    message=('feat(retention): expose original files for '+prepared['run_id']+'\n\n'
      'Preserve exact scientific paths and bytes from the stopped capture.\n'
      'Keep readable files in Git and bulk payloads in annex. Record source\n'
      'hashes, original modes and the identical-input retrieval proof.\n\n'
      'This coordinator presentation leaves the complete archive authoritative\n'
      'and performs no scientific execution or original source changes.\n\n'+trailers+'\n')
    (root/'commit-message.txt').write_text(message)
    run(['git','commit','-F',root/'commit-message.txt'])
    head=run(['git','rev-parse','HEAD'])
    assert run(['git','rev-parse','HEAD:input'])==prepared['input_tree']
    assert run(['git','status','--porcelain'])==''
    save(root/'commit.json',{'commit':head,'parent_commit':prepared['parent_commit'],'branch':prepared['branch']})
    print(head)
except BaseException:
    (root/'failure-commit.txt').write_text(traceback.format_exc());raise
