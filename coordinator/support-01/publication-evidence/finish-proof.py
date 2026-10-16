from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parent
row=json.loads((ROOT/'result.json').read_bytes())
assert row['verified']
repo=Path(row['publisher']);recipient=Path(row['fresh_recipient'])
commands=[]

def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def run(argv,cwd):
 argv=list(map(str,argv));p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
 commands.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 save(ROOT/'finish-commands.json',commands);p.check_returncode();return p.stdout.strip()

try:
 assert run(['git','rev-parse','HEAD'],repo)==row['commit']
 dest=repo/'coordinator/support-01/publication-evidence';dest.mkdir()
 files=[]
 for source in sorted(ROOT.iterdir()):
  if source.is_file() and source.name not in {'finish-commands.json','finish.stdout','finish.stderr','finish-proof.stdout','finish-proof.stderr'}:
   raw=source.read_bytes();shutil.copy2(source,dest/source.name);assert (dest/source.name).read_bytes()==raw
   files.append({'path':source.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 save(dest/'evidence-manifest.json',files)
 run(['git','add','coordinator/support-01/publication-evidence'],repo)
 run(['git','diff','--cached','--check'],repo)
 trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],repo)
 message=ROOT/'proof-commit-message.txt'
 message.write_text('chore(retention): retain independent support publication proof\n\n'
                    'Record exact preparation, upload and fresh-recipient verification.\n'
                    'Keep the original delivery and assessed evidence unchanged.\n\n'+trailers+'\n')
 run(['git','commit','-F',message],repo)
 head=run(['git','rev-parse','HEAD'],repo)
 assert run(['git','rev-parse','HEAD^'],repo)==row['commit']
 assert run(['git','remote','get-url','--push','origin'],repo)=='git@github.com:leej3/stamped-in-practice.git'
 run(['git','push','origin','HEAD:refs/heads/'+row['branch']],repo)
 run(['git','fetch','--no-tags','origin',head],recipient)
 run(['git','checkout','--detach','FETCH_HEAD'],recipient)
 assert run(['git','rev-parse','HEAD^'],recipient)==row['commit']
 changed=run(['git','diff','--name-only','HEAD^','HEAD'],recipient).splitlines()
 assert changed and all(p.startswith('coordinator/support-01/publication-evidence/') for p in changed)
 for f in files:
  raw=(recipient/'coordinator/support-01/publication-evidence'/f['path']).read_bytes()
  assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256']
 assert run(['git','status','--porcelain'],recipient)==''
 save(ROOT/'proof-verification.json',{'verified':True,'commit':head,'content_parent':row['commit'],
      'base':row['base'],'branch':row['branch'],'evidence_files':len(files),
      'archive_verification':'result.json; ancestor content unchanged','files':files})
 print(head)
except BaseException as exc:
 save(ROOT/'finish-failure.json',{'type':type(exc).__name__,'error':str(exc)})
 raise
