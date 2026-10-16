"""Repin published browsing descendants; original capture/worker identities stay fixed."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;study=Path('/Users/johnlee/code/CON/stamped-in-practice/studies/narps')
proof=B/'browsable-publication-complete-01/result.json';raw=proof.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='001c9286080a7366cb95578c7152514071a5278141735e558bf50d909610fb6c'
v=json.loads(raw);assert v['success'] and len(v['runs'])==23
assert subprocess.check_output(['git','status','--porcelain'],cwd=study,text=True)==''
assert subprocess.check_output(['git','rev-parse','HEAD:input'],cwd=study,text=True).strip()==v['input_tree']
p=study/'neutral-retention-publications.json';registry=json.loads(p.read_text());by_run={r['run_id']:r for r in registry['runs']}
for r in v['runs']:
 old=by_run[r['run_id']];assert old['commit']==r['canonical_parent'];assert old['dataset_id']==r['dataset_id'] and old['capture_sha256']==r['capture_sha256']
 assert r['canonical_fast_forward_verified'] and r['original_archive_unchanged'] and r['original_critical_git_metadata_unchanged'] and r['original_stop_receipt_unchanged']
 old['original_archive_publication_commit']=old['commit'];old['commit']=r['commit'];old['browsable_copy']={'scope':'Exact original scientific bytes exposed at delivered paths; coordinator copying and navigation earn no worker-practice credit.','verification_path':'rounds/round-01/delivery-publication/browsable-complete-01/result.json','verification_sha256':hashlib.sha256(raw).hexdigest(),'run_receipt_path':f"rounds/round-01/delivery-publication/browsable-complete-01/{r['run_id']}/final.json",'run_receipt_sha256':r['final_receipt_sha256']}
 subprocess.run(['git','update-index','--cacheinfo','160000',r['commit'],'results/'+r['run_id']],cwd=study,check=True)
p.write_text(json.dumps(registry,indent=2)+'\n');subprocess.run(['git','add',p.name],cwd=study,check=True)
subprocess.run(['git','diff','--cached','--check'],cwd=study,check=True)
resolved=subprocess.run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],cwd=study,capture_output=True,text=True,check=True)
message='data: expose all first-round original scientific deliveries\n\nRepin 23 verified coordinator presentation descendants. Original delivery\narchives, scientific file bytes, capture identities and worker Git HEADs\nremain unchanged; later assessment support remains separately attributed.\n\n'+resolved.stdout
subprocess.run(['git','commit','-F','-'],input=message,text=True,cwd=study,check=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=study,text=True).strip();assert subprocess.check_output(['git','rev-parse','HEAD:input'],cwd=study,text=True).strip()==v['input_tree']
subprocess.run(['git','push','origin','HEAD:refs/heads/codex/study-narps'],cwd=study,check=True)
(B/'browsable-study-registration.json').write_text(json.dumps({'study_commit':commit,'input_tree':v['input_tree'],'proof_sha256':hashlib.sha256(raw).hexdigest(),'registered_browsable_runs':24,'updated_runs':23,'original_worker_identity_changed':False},indent=2)+'\n')
print(commit)
