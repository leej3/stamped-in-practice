from pathlib import Path
import hashlib,json,subprocess,shutil
B=Path(__file__).resolve().parent.parent
ROOT=Path(__file__).resolve().parent
MAIN=Path('/Users/johnlee/code/CON/stamped-in-practice');STUDY=MAIN/'studies/narps'
DATASET=B/'dataset';OUT=DATASET/'rounds/round-01/support-publication/closed-05'
OUT.mkdir(parents=True)
commands=[]
def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def run(argv,cwd):
 argv=list(map(str,argv));p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
 commands.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 save(ROOT/'commands.json',commands);p.check_returncode();return p.stdout.strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
registry=json.loads((STUDY/'neutral-retention-publications.json').read_bytes())
old=run(['git','rev-parse','HEAD'],STUDY);registered=[]
for suffix in ['08','14','21']:
 name='narps-neutral-r1-'+suffix;pub=B/f'support-publication-r1-{suffix}-01'
 proof=json.loads((pub/'proof-verification.json').read_bytes());support=json.loads((pub/'result.json').read_bytes())
 assert proof['verified'] and support['verified']
 native=B/'runs'/name/'judgments'/(name+'-j01')/'retention/native-publication-01/proof-publication-01/result.json'
 np=json.loads(native.read_bytes());assert np['verified'] and np['source_files_unchanged']
 head=proof['commit']
 repo=pub/'publisher';row=next(x for x in registry['runs'] if x['run_id']==name)
 run(['git','fetch','--no-tags','origin',head],repo)
 run(['git','merge-base','--is-ancestor',row['commit'],head],repo)
 paths=run(['git','diff','--name-only',row['commit'],head],repo).splitlines()
 assert paths and all(p=='.gitattributes' or p.startswith('coordinator/') for p in paths)
 assert run(['git','rev-parse',head+':input'],repo)=='a484f41db2095ef116f08d359f9b95ad41981698'
 run(['git','push','origin',head+':refs/heads/'+row['branch']],repo)
 assert run(['git','ls-remote','origin','refs/heads/'+row['branch']],repo).split()[0]==head
 previous=row['commit'];row['commit']=head
 dest=OUT/name;dest.mkdir()
 for source in sorted(pub.iterdir()):
  if source.is_file():shutil.copy2(source,dest/source.name)
 shutil.copy2(native,dest/'native-proof-publication.json')
 native_rows=[]
 for additional in sorted((B/'runs'/name/'judgments').glob('*/retention/native-publication-01/proof-publication-01/result.json')):
  value=json.loads(additional.read_bytes());assert value['verified'] and value['source_files_unchanged']
  label=additional.parents[3].name+'-native-proof.json';shutil.copy2(additional,dest/label)
  native_rows.append({'commit':value['proof_commit'],'path':str((dest/label).relative_to(DATASET)),'sha256':sha(dest/label)})
 row['support_publication']={'scope':'Complete closed run support plus exact assigned judgment copies and native publication; coordinator evidence receives no worker credit.',
    'previous_browsable_commit':previous,'support_content_commit':support['commit'],
    'support_archive_key':support['archive_key'],'support_archive_sha256':support['archive_sha256'],
    'support_archive_bytes':support['archive_bytes'],'support_archive_path':support['archive_path'],
    'independent_check':{'path':str((dest/'result.json').relative_to(DATASET)),'sha256':sha(dest/'result.json')},
    'proof_check':{'path':str((dest/'proof-verification.json').relative_to(DATASET)),'sha256':sha(dest/'proof-verification.json')},
    'native_publications':native_rows,
    'native_publication':{'commit':np['proof_commit'],'path':str((dest/'native-proof-publication.json').relative_to(DATASET)),'sha256':sha(dest/'native-proof-publication.json')}}
 run(['git','update-index','--add','--cacheinfo','160000,'+head+',results/'+name],STUDY)
 registered.append({'run_id':name,'previous':previous,'commit':head})
save(STUDY/'neutral-retention-publications.json',registry)
run(['git','add','neutral-retention-publications.json'],STUDY)
run(['git','diff','--cached','--check'],STUDY)
trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],STUDY)
message=ROOT/'message.txt';message.write_text('data(narps): register three more support publications\n\n'
 'Retain exact original scientific paths and capture identities while\n'
 'linking complete support archives, assigned judgments and native proofs.\n\n'+trailers+'\n')
run(['git','commit','-F',message],STUDY)
head=run(['git','rev-parse','HEAD'],STUDY)
assert run(['git','rev-parse','HEAD:input'],STUDY)==run(['git','rev-parse',old+':input'],STUDY)
run(['git','push','origin','HEAD:refs/heads/codex/study-narps'],STUDY)
save(ROOT/'result.json',{'verified':True,'study_commit':head,'previous_study_commit':old,'runs':registered,'input_tree_unchanged':True})
shutil.copy2(ROOT/'result.json',OUT/'registration-result.json')
print(head)
