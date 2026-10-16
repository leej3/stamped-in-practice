from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
root=Path(__file__).resolve().parent;b=root.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
rows=[];receipts=[]
for batch in range(1,5):
 receipt=b/f'round-01-judge-batch-{batch:02d}/retention-closed.json'
 data=json.loads(receipt.read_text());receipts.append(ref(receipt))
 for judgment in data['judgments']:
  assignment=judgment['assignment'];p=Path(judgment['retention'])/'native-publication-01'
  final=json.loads((p/'proof-publication-01/result.json').read_text())
  attachment=json.loads((p/'attachment.json').read_text())
  fresh=json.loads((p/'fresh-verification.json').read_text())
  hosted=json.loads((p/'hosted-check-01/result.json').read_text())
  native=json.loads((p.parent.parent/'attempt-01/native/result.json').read_text())
  assert final['verified'] and final['source_files_unchanged'] and not final['canonical_branch_updated']
  assert fresh['verified'] and hosted['hosted_verified']
  assert final['session_id']==attachment['session_id']==fresh['session_id']==hosted['session_id']==native['native_session_ids'][0]
  assert final['checkpoint_id']==attachment['checkpoint_id']==fresh['checkpoint_id']==hosted['checkpoint_id']
  assert final['content_commit']==attachment['commit']==fresh['commit']
  evidence=[ref(p/n) for n in ['attachment.json','publication.json','fresh-verification.json','hosted-check-01/result.json','proof-publication-01/result.json']]
  failures=[ref(p/n) for n in ['failure.txt','publish-failure.txt'] if (p/n).is_file()]
  rows.append({'judgment':assignment['judgment'],'run':assignment['run'],'dispatch_order':assignment['dispatch_order'],
   'scientific_validity_assessed':False,'historical_attachment':True,'session_id':final['session_id'],'checkpoint_id':final['checkpoint_id'],
   'base_commit':attachment['base_commit'],'content_commit':final['content_commit'],'proof_commit':final['proof_commit'],'branch':final['branch'],
   'record_path':attachment['coordinator_record_path'],'publication_directory':str(p),'evidence':evidence,'initial_failures_retained':failures,
   'github_proof_url':'https://github.com/leej3/stamped-in-practice/tree/'+final['proof_commit']+'/'+attachment['coordinator_record_path']})
assert len(rows)==12 and len({r['session_id'] for r in rows})==12 and len({r['checkpoint_id'] for r in rows})==12
result={'created_at':datetime.now(timezone.utc).isoformat(),'scope':'First twelve stopped first-round judgments: historical Entire publication and independent retrieval only. Original assessments, admission and source bytes unchanged. Later support packaging owns canonical experiment/study integration.','verified':True,'judgments':len(rows),'batch_receipts':receipts,'records':rows}
(root/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'verified':True,'judgments':len(rows),'sha256':sha(root/'result.json'),'path':str(root/'result.json')}))
