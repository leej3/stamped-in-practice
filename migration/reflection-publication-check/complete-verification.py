from pathlib import Path
import subprocess,json,hashlib,tarfile,shutil
out=Path(__file__).parent/'reflection-fresh-check-01';shutil.copyfile(__file__,out/'complete-verification.py');r=out/'recipient';px=['pixi','run','--locked','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
argv=px+['git','-C',str(r),'annex','find','--anything','--json','--','migration/verification','skill-reflection'];p=subprocess.run(argv,capture_output=True,text=True);(out/'final-inventory-command.json').write_text(json.dumps(dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2)+'\n');p.check_returncode();inventory=[json.loads(x) for x in p.stdout.splitlines()]
for x in inventory:assert sha(r/x['file'])==x['key'].split('--')[1].split('.')[0]
m=json.loads((r/'migration/verification/retention-manifest.json').read_text())['files']
for x in m:assert sha(r/x['path'])==x['sha256']
trials=[]
for name,prefix,key in [('assessment-neutrality-trial-01','trial','records'),('research-guidance-trial-01','research-guidance-trial-01','files')]:
 d=r/'skill-reflection'/name;rows=json.loads((d/'manifest.json').read_text())[key]
 with tarfile.open(d/'trial.tar.gz') as tar:
  for x in rows:
   member=tar.getmember(prefix+'/'+x['path'])
   if x['kind']=='symlink':assert member.issym() and member.linkname==x['target']
   elif x['kind']=='file':assert hashlib.sha256(tar.extractfile(member).read()).hexdigest()==x['sha256'],x['path']
 trials.append(dict(name=name,files=len(rows),archive_sha256=sha(d/'trial.tar.gz'),manifest_sha256=sha(d/'manifest.json')))
old=json.loads((out/'result.json').read_text());assert old['error']=="KeyError: 'assessment-neutrality-trial-01/README.md'"
result=dict(success=True,commit=old['commit'],annex_paths=len(inventory),proof_files_verified=len(m),trials=trials,original_attempt='result.json',original_error='Verifier assumed the assessor archive prefix matched its directory; its actual preserved prefix is trial/. Corrected member lookup verified all unchanged archived bytes.',fresh_retrieval_commands='commands.json')
(out/'result-complete.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
