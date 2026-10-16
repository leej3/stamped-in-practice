"""Use the project verifier's empty-store hosted checkpoint check."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent
source=Path('/Users/johnlee/code/CON/stamped-in-practice/scripts/verify_native_capture.py')
copied=root/'hosted-verifier-source.py'
if not copied.exists():shutil.copy2(source,copied)
spec=importlib.util.spec_from_file_location('hosted_verifier',copied)
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
out=root/('hosted-check-'+sys.argv[1]);out.mkdir()
a=json.loads((root/'attachment.json').read_text());commands=[]
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv,cwd,env=None):
    p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True)
    label=f'command-{len(commands)+1:02d}'
    (out/(label+'.stdout')).write_bytes(p.stdout);(out/(label+'.stderr')).write_bytes(p.stderr)
    commands.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':label+'.stdout','stderr':label+'.stderr'})
    save(out/'commands.json',commands);p.check_returncode();return p.stdout
verifier.run=run
result={'checked_at':datetime.now(timezone.utc).isoformat(),'checkpoint_id':a['checkpoint_id'],'session_id':a['session_id'],
        'helper_sha256':hashlib.sha256(copied.read_bytes()).hexdigest(),'empty_independent_git_store':True,'hosted_verified':False}
try:
    metadata,digest=verifier.hosted_metadata('gh/leej3/stamped-in-practice',a['checkpoint_id'])
    assert metadata['checkpoint_id']==a['checkpoint_id']
    assert a['session_id'] in [s['session_id'] for s in metadata['sessions']]
    result.update(hosted_verified=True,metadata_sha256=digest)
except BaseException as exc:result.update(error_type=type(exc).__name__,error=str(exc))
save(out/'result.json',result)
print(json.dumps(result))
