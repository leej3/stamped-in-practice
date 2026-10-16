from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parent
commands=[]
for name,args in [('publish-and-verify.py',[]),('verify-hosted.py',['01']),('finalize-proof.py',[])]:
 if name=='finalize-proof.py':assert json.loads((root/'hosted-check-01/result.json').read_text())['hosted_verified']
 p=subprocess.run([sys.executable,str(root/name),*args],cwd=root,capture_output=True)
 (root/('recovery-'+name+'.stdout')).write_bytes(p.stdout)
 (root/('recovery-'+name+'.stderr')).write_bytes(p.stderr)
 commands.append({'argv':[sys.executable,str(root/name),*args],'returncode':p.returncode,'cwd':str(root)})
 (root/'recovery-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 p.check_returncode()
print((root/'proof-publication-01/result.json').read_text())
