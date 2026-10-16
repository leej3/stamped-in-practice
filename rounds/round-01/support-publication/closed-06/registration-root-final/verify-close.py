from pathlib import Path
import hashlib,json,subprocess,shutil
root=Path(__file__).resolve().parent
base=root.parent
study=Path('/Users/johnlee/code/CON/stamped-in-practice/studies/narps')
result=json.loads((root/'result.json').read_bytes())
commands=[]
def run(argv):
 p=subprocess.run(argv,cwd=study,capture_output=True,text=True)
 commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 p.check_returncode();return p.stdout.strip()
assert run(['git','rev-parse','HEAD'])==result['study_commit']
assert run(['git','ls-remote','origin','refs/heads/codex/study-narps']).split()[0]==result['study_commit']
changed=run(['git','diff','--name-only',result['previous_study_commit'],result['study_commit']]).splitlines()
assert set(changed)=={'neutral-retention-publications.json','results/narps-neutral-r1-03','results/narps-neutral-r1-19'}
registry=json.loads((study/'neutral-retention-publications.json').read_bytes())
assert len(registry['runs'])==24
assert all(r.get('support_publication') for r in registry['runs'])
assert sum(len(r['support_publication']['native_publications']) for r in registry['runs'])==32
for row in result['runs']:
 assert run(['git','ls-remote','origin','refs/heads/codex/'+row['run_id']+'-retained']).split()[0]==row['commit']
 assert run(['git','rev-parse','HEAD:results/'+row['run_id']])==row['commit']
final={'verified':True,'study_commit':result['study_commit'],'support_publications':24,
       'assigned_native_publications':32,'runs':result['runs'],'changed_paths':changed,
       'iteration_commit_created':False,'main_commit_created':False,'commands':commands}
with (root/'final-verification.json').open('x') as f:f.write(json.dumps(final,indent=2,sort_keys=True)+'\n')
dest=base/'dataset/rounds/round-01/support-publication/closed-06/registration-root-final'
dest.mkdir()
files=[]
for source in sorted(root.iterdir()):
 if source.is_file():
  raw=source.read_bytes();target=dest/source.name;shutil.copy2(source,target);assert target.read_bytes()==raw
  files.append({'path':source.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(dest/'receipt-index.json').write_text(json.dumps({'scope':'Exact final registration root receipts; earlier snapshots at closed-06 root retained separately.','files':files},indent=2,sort_keys=True)+'\n')
print(json.dumps({'verified':True,'study_commit':result['study_commit'],'final_receipts':str(dest),'receipt_index_sha256':hashlib.sha256((dest/'receipt-index.json').read_bytes()).hexdigest()}))
