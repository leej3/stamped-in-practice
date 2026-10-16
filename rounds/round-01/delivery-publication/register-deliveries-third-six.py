from pathlib import Path
import hashlib,json,subprocess
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');study=Path('/Users/johnlee/code/CON/stamped-in-practice/studies/narps')
proofs=[B/'publisher-wave-05-01/fresh-check-01/result.json',B/'publisher-wave-06-01/fresh-check-01/result.json']
rows=[]
for p in proofs:
 x=json.loads(p.read_text());assert x['success'];rows.extend(x['runs'])
assert len(rows)==6 and len({r['run_id'] for r in rows})==6
assert subprocess.check_output(['git','status','--porcelain'],cwd=study,text=True)==' M README.md\n'
assert subprocess.check_output(['git','rev-parse','HEAD:input'],cwd=study,text=True).strip()=='a484f41db2095ef116f08d359f9b95ad41981698'
for row in rows:
 assert row['success'] and row['verification']['verified']
 name=row['run_id'];path='results/'+name;(study/path).mkdir(exist_ok=False)
 for key,value in [('path',path),('url','https://github.com/leej3/stamped-in-practice.git'),('branch',row['branch']),('datalad-id',row['dataset_id'])]:
  subprocess.run(['git','config','-f','.gitmodules','submodule.'+path+'.'+key,value],cwd=study,check=True)
 subprocess.run(['git','update-index','--add','--cacheinfo','160000',row['commit'],path],cwd=study,check=True)
registry=[]
for wave in range(1,7):
 folder='root-fresh-check-01' if wave==1 else 'fresh-check-01'
 proof=B/f'publisher-wave-{wave:02d}-01'/folder/'result.json';verified=json.loads(proof.read_text());assert verified['success']
 for item in verified['runs']:
  registry.append({**{k:item[k] for k in ['run_id','commit','dataset_id','branch','worker_head_commit','capture_sha256','archive_sha256','archive_bytes','archive_key']},'archive_path':'coordinator/delivery-01/delivery.tar.gz','independent_check':{'comparison_evidence_path':f'rounds/round-01/delivery-publication/wave-{wave:02d}/{folder}/result.json','sha256':hashlib.sha256(proof.read_bytes()).hexdigest()}})
(study/'neutral-retention-publications.json').write_text(json.dumps({'comparison':'narps-neutral-v1','scope':'Published original deliveries, independently retrieved; later judgments and supplementary evidence are separate','runs':registry},indent=2)+'\n')
subprocess.run(['git','add','.gitmodules','README.md','neutral-retention-publications.json'],cwd=study,check=True)
resolver=subprocess.run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],cwd=study,capture_output=True,text=True,check=True)
msg='data: register six deliveries and clarify retention identities\n\nLink complete original-delivery archives after independent retrieval and\nmember verification. Coordinator preservation remains separate from the\nactual worker Git identities and later judgment records.\n\n'+resolver.stdout
subprocess.run(['git','commit','-F','-'],cwd=study,input=msg,text=True,check=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=study,text=True).strip()
assert subprocess.check_output(['git','rev-parse','HEAD:input'],cwd=study,text=True).strip()=='a484f41db2095ef116f08d359f9b95ad41981698'
subprocess.run(['git','push','origin','HEAD:refs/heads/codex/study-narps'],cwd=study,check=True)
record={'study_commit':commit,'input_tree':'a484f41db2095ef116f08d359f9b95ad41981698','scope':'Six complete original deliveries; later judgments and supplementary coordinator evidence still pending','proofs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in proofs],'runs':[{k:r[k] for k in ['run_id','commit','dataset_id','branch','worker_head_commit','capture_sha256','archive_sha256','archive_bytes']} for r in rows]}
(B/'third-six-study-registration.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
