"""Read-only final assignment/session coverage check on retained judge evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
BASE=Path(__file__).resolve().parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
root=BASE/'judge-retention-final-01';summary=read(root/'summary.json');manifest=read(root/'manifest.json');support=read(root/'supporting-files.json')
for record in manifest['files']+manifest['verified_external_references']+support['files']:
    data=Path(record['path']).read_bytes();assert len(data)==record['size'] and sha(data)==record['sha256'],record['path']
plan=read(BASE/'dataset/rounds/round-01/plan.json');expected=sorted(plan['assigned_judgments'],key=lambda r:r['dispatch_order']);assert [r['assignment'] for r in summary['judgments']]==expected and len(expected)==32
sessions=[];metadata_complete=[];target_deltas=[]
for row in summary['judgments']:
    r=Path(row['retention']);m=read(r/'late-capture-01/native/entire-session.json');n=read(r/'late-capture-01/native/verification.json')
    assert m['phase']=='ended' and m['session_id']==n['session_id'] and n['native_identity']['session_and_cwd_match']
    assert all(f['completed_event_identity_sequence_matches'] for shadow in n['shadow_checkpoints'] for f in shadow['session_files'] if 'identity' in f)
    sessions.append(m['session_id']);metadata_complete.append(m.get('subagent_inventory_complete'))
    if 'target_as_found' in row:
        d=read(Path(row['target_as_found']['delta']['path']));target_deltas.append({'judgment':row['assignment']['judgment'],'added':[r['path'] for r in d['added']],'missing':[r['path'] for r in d['missing']],'modified':[r['path'] for r in d['modified']]})
assert len(set(sessions))==32
result={'audited_at':datetime.now(timezone.utc).isoformat(),'verified':True,'fixed_assignments':32,'unique_ended_native_sessions':32,'completed_event_identity_sequence_verified_sessions':32,'metadata_inventory_complete_sessions':sum(v is True for v in metadata_complete),'final_summary_sha256':sha((root/'summary.json').read_bytes()),'final_manifest_sha256':sha((root/'manifest.json').read_bytes()),'supporting_files_verified':len(support['files']),'bound_external_references_verified':len(manifest['verified_external_references']),'target_delta_paths':target_deltas,'source_mutations':False,'scope':'Assignment/session identity, bound metadata hashes and preserved path deltas only. Scientific grade content was not read or evaluated.'}
out=BASE/'judge-retention-final-01.audit.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
