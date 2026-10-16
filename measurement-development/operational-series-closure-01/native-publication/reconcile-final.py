"""Reconcile all registered sessions and stage-specific final receipts."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,subprocess
R=Path(__file__).resolve().parent;B=R.parent
series_path=B/'repaired-series-registration-01/series.json';series=json.loads(series_path.read_text());plan=json.loads((R/'plan.json').read_text());boundary=json.loads((R/'coordinator-boundary.json').read_text())
old=B/'judge-native-publication-index-03/result.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def save(p,d):assert not p.exists();p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
assert sha(old)==next(row['sha256'] for row in plan['references'] if row['path']==str(old))
original=json.loads(old.read_text());old_sessions={r['session_id'] for r in original['records']}
old_checkpoints={r['checkpoint_id'] for r in original['records']}
rows=[];sessions=set();checkpoints=set();pending=[];bases={};checks=[]
for allocated in series['judgment_dispatch_order']:
 slot=allocated['judgment'];out=R/'judgments'/slot;pub=out/'native-publication-01';cap=out/'late-capture-01'
 path=out/'completion-index.json';full=path.exists()
 if not full:path=out/'git-completion-index.json'
 d=json.loads(path.read_text());a=json.loads((pub/'attachment.json').read_text());config=json.loads((pub/'publication-config.json').read_text())
 assert config['initial_study_base']==boundary['initial_bases'][allocated['run']]
 assert d['slot']==slot and d['series_id']==series['series_id'] and d['assessment_procedure_sha256']==series['assessment_procedure_sha256']
 assert d['session_id']==a['session_id'] and d['checkpoint_id']==a['checkpoint_id']
 assert d['session_id'] not in sessions|old_sessions and d['checkpoint_id'] not in checkpoints|old_checkpoints
 sessions.add(d['session_id']);checkpoints.add(d['checkpoint_id'])
 assert a['all_line_identity_fields_equal'] and a['historical_attachment']
 original_meta=json.loads((cap/'native/entire-session.json').read_text())
 assert original_meta['phase']=='ended' and original_meta['session_id']==d['session_id']
 assert json.loads((out/'late-capture-01.integrity-audit.json').read_text())['verified']
 assert {p:sha(Path(p)) for p in a['original_sources_unchanged']}==a['original_sources_unchanged']
 assert sha(cap/'native/native-transcript.jsonl')==a['raw_sha256']
 assert sha(pub/'processed-transcript.stdout')==a['processed_sha256']
 head=d['proof_commit'] if full else d['git_proof_commit'];repo=pub/'publisher'
 if allocated['run'] in bases:assert config['base_commit']==bases[allocated['run']]
 else:assert config['base_commit']==config['initial_study_base']
 bases[allocated['run']]=head
 p=subprocess.run(['git','merge-base','--is-ancestor',config['base_commit'],head],cwd=repo,capture_output=True);checks.append({'slot':slot,'command':['git','merge-base','--is-ancestor',config['base_commit'],head],'cwd':str(repo),'returncode':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()});p.check_returncode()
 if full:
  closed=path
  assert json.loads((pub/'fresh-verification.json').read_text())['verified']
 else:
  closed=R/'git-closures'/slot/'index.json';closure=json.loads(closed.read_text())
  assert closure['git_completion_index']==ref(path) and closure['git_proof_commit']==head and not closure['fully_verified_hub_publication']
  assert d['git_code_checkpoint_and_proof_verified'] and d['hosted_checkpoint_verified'] and not d['fully_verified_hub_publication']
  for payload in d['annex_payloads']:
   if payload['fresh_hub_retrieval_status']=='previously_verified':
    assert payload['path'] in a['annex_paths'] and json.loads((pub/'fresh-verification.json').read_text())['verified']
   if payload['hub_upload_status']=='previously_succeeded' and payload['path'] not in a['annex_paths']:
    receipts=json.loads((pub/'proof-publication-01/commands.json').read_text())
    assert any(r['label']=='upload-evidence' and r['returncode']==0 for r in receipts)
   pending.append(dict(payload,slot=slot,branch=d['branch'],git_proof_commit=head))
 rows.append({'slot':slot,'dispatch_order':allocated['dispatch_order'],'run':allocated['run'],'session_id':d['session_id'],'checkpoint_id':d['checkpoint_id'],'checkpoint_ref':a['checkpoint_ref'],'checkpoint_oid':a['checkpoint_oid'],'content_commit':a['commit'],'proof_commit':head,'base_commit':config['base_commit'],'branch':d['branch'],'fully_verified_hub_publication':full,'stage_index':ref(path),'closed_local_bundle':ref(closed),'capture_manifest':ref(cap/'manifest.json'),'source_to_captured_mapping':ref(cap/'source-captures.json'),'session_url':'https://entire.io/gh/leej3/stamped-in-practice/session/'+d['session_id'],'commit_url':'https://entire.io/gh/leej3/stamped-in-practice/commit/'+a['commit'],'raw_sha256':a['raw_sha256'],'attached_processed_sha256':a['processed_sha256']})
assert len(rows)==32 and len(sessions)==32 and len(checkpoints)==32
pending_only=[p for p in pending if p['fresh_hub_retrieval_status']!='previously_verified']
unique={}
for p in pending_only:
 identity=(p['sha256'],p['bytes'])
 if p['annex_key'] in unique:assert unique[p['annex_key']]==identity
 unique[p['annex_key']]=identity
result={'schema':'operational-native-stage-reconciliation-v1','reconciled_at':datetime.now(timezone.utc).isoformat(),'series_id':series['series_id'],'assessment_procedure_sha256':series['assessment_procedure_sha256'],'registered_slots':32,'ended_sessions_preserved':32,'unique_new_sessions':32,'unique_new_checkpoints':32,'git_and_hosted_verified_slots':32,'fully_verified_hub_slots':sum(r['fully_verified_hub_publication'] for r in rows),'hub_transfers_held':True,'original32_index_unchanged':ref(old),'registered_series':ref(series_path),'records':rows,'pending_payload_paths':len(pending_only),'pending_unique_annex_keys':len(unique),'pending_unique_payload_bytes':sum(v[1] for v in unique.values()),'scope':'Complete stopped local captures, independent GitHub code/checkpoint/proof verification and authenticated hosted session identity. Full Hub closure is claimed only for individual full completion indexes. All attachments were coordinator work after native session stop; no assessment, scoring, or scientific-validity conclusion.'}
save(R/'final-git-reconciliation-checks.json',checks)
save(R/'final-pending-hub-payloads.json',{'series_id':series['series_id'],'hub_transfers_held':True,'payloads':pending,'scope':'Exact path/key/bytes/hash and receipt status for Git-only slots. Previously verified entries remain explicit; not-attempted does not assert remote absence.'})
result['pending_hub_payloads']=ref(R/'final-pending-hub-payloads.json');result['reconciliation_checks']=ref(R/'final-git-reconciliation-checks.json');result['reconciliation_method']=ref(Path(__file__).resolve());result['hub_hold_record']=ref(R/'hub-hold-state.json')
save(R/'final-git-reconciliation.json',result)
print(json.dumps({'result':ref(R/'final-git-reconciliation.json'),'slots':32,'fully_verified_hub_slots':result['fully_verified_hub_slots'],'pending_unique_annex_keys':len(unique),'pending_unique_payload_bytes':result['pending_unique_payload_bytes']}))
