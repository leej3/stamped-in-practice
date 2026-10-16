"""Add an immutable publication handoff for a fully preserved stopped batch.
Uses only control receipts and preservation records; never reads judge prose.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(path):
    data=path.read_bytes()
    return {'path':str(path),'size':len(data),'sha256':sha(data)}
def read(path):return json.loads(path.read_bytes())
batch=int(sys.argv[1]);directory=BASE/f'round-01-judge-batch-{batch:02d}';out=directory/'retention-closed.json'
assert not out.exists(),str(out)
planpath=BASE/'dataset/rounds/round-01/plan.json'
assignments=sorted(read(planpath)['assigned_judgments'],key=lambda a:a['dispatch_order'])[(batch-1)*3:batch*3]
assert len(assignments)==(2 if batch==11 else 3)
records=[];counts={'judgments':0,'main_retention_regular_files':0,'main_retention_regular_bytes':0,'completed_events':0,'native_transcripts':0,'shadow_transcripts':0,'profile_skill_entrypoints':0,'target_as_found_captures':0,'target_as_found_regular_files':0}
for a in assignments:
    d=BASE/'runs'/a['run']/'judgments'/a['judgment'];control=read(d/'dispatch.json')
    assert control.get('status')=='launcher-finished',a['judgment']
    r=d/'retention';v=read(r/'late-capture-01/verification.json');audit=read(r/'late-capture-01.integrity-audit.json')
    assert v['verified'] and audit['verified'] and v['source_before_after_equal']
    assert audit['capture_manifest_sha256']==ref(r/'late-capture-01/manifest.json')['sha256']
    result=read(r/'late-capture-01/control/native-result.json') if (r/'late-capture-01/control/native-result.json').exists() else None
    addendum=read(r/'late-capture-01.scope-addendum.json') if (r/'late-capture-01.scope-addendum.json').exists() else {}
    native_status={key:v.get(key,addendum.get(key)) for key in ['launcher_returncode','native_returncode','launcher_target_unchanged','launcher_target_validation_error']}
    external=[ref(p) for p in sorted(r.iterdir()) if p.is_file() and not p.is_symlink()]
    e={'assignment':a,'retention':str(r),'preservation_verified':True,'scientific_validity_assessed':False,'launcher_status':native_status,'main_capture_manifest':ref(r/'late-capture-01/manifest.json'),'main_integrity_audit':ref(r/'late-capture-01.integrity-audit.json'),'main_verification':ref(r/'late-capture-01/verification.json'),'external_receipts':external}
    execution=read(r/'late-capture-01.execution.json');script=Path(execution['argv'][2]);assert ref(script)['sha256']==execution['script_sha256'];e['main_script']=ref(script)
    counts['judgments']+=1;counts['main_retention_regular_files']+=audit['entry_kinds']['file'];counts['main_retention_regular_bytes']+=audit['regular_file_bytes'];counts['completed_events']+=v['completed_events'];counts['native_transcripts']+=1;counts['shadow_transcripts']+=v['shadow_transcripts'];counts['profile_skill_entrypoints']+=v['profile_skill_entrypoints']
    target=r/'target-as-found-01'
    if native_status['launcher_target_unchanged'] is False:assert target.exists(),'Changed target must have its own preserved evidence'
    if target.exists():
        tv=read(target/'verification.json');ta=read(r/'target-as-found-01.integrity-audit.json');assert tv['preservation_verified'] and ta['verified']
        e['target_as_found']={'manifest':ref(target/'manifest.json'),'verification':ref(target/'verification.json'),'audit':ref(r/'target-as-found-01.integrity-audit.json'),'delta':ref(target/'manifest-to-as-found-delta.json')}
        counts['target_as_found_captures']+=1;counts['target_as_found_regular_files']+=tv['source_regular_files']
    records.append(e)
helpers=[ref(p) for p in sorted(HERE.iterdir()) if p.is_file() and not p.is_symlink()]
receipt={'schema':'stopped-judge-batch-retention-handoff-v1','created_at':datetime.now(timezone.utc).isoformat(),'round':1,'batch':batch,'registered_plan':ref(planpath),'preservation_complete':True,'counts':counts,'judgments':records,'helper_files_at_closure':helpers,'scope':'Additive late preservation of stopped output trees, raw native and original Entire processed shadow, skill availability, and any changed assessed target. Capture integrity is separate from launcher status and scientific validity. Original captures and receipts are unchanged; publication is not established by this local handoff.','no_grade_content_interpreted':True,'source_mutations_performed':False}
with out.open('x') as stream:stream.write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'handoff':ref(out),'counts':counts},indent=2))
