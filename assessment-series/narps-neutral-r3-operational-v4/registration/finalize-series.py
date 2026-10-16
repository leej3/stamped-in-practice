"""Bind the existing round-three slots to their completed original deliveries."""
from pathlib import Path
import json,hashlib,datetime
G=Path(__file__).resolve().parent;B=G.parent;OLD=B/'round-02-assessment-registration-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
seal=read(G/'assessment-procedure.json');previous=read(OLD/'assessment-procedure.json')
left=json.loads(json.dumps(previous));right=json.loads(json.dumps(seal))
left['assessment_amendment'].pop('retained_objects');right['assessment_amendment'].pop('retained_objects')
assert left==right,'Only original object identities may differ'
allocation=read(G/'original-allocation.json');group=next(r for r in allocation['rounds'] if r['round']==3)
r=read(OLD/'series.json');r.update(round=3,series_id='narps-neutral-r3-operational-v4',assessment_procedure_sha256=sha(G/'assessment-procedure.json'),retained_objects_sha256=sha(G/'retained-objects.json'),original_object_sources_sha256=sha(G/'original-object-sources.json'))
r['judgment_dispatch_order']=[dict(s,original_judgment=s['judgment'],attempt_id=s['judgment']+'-operational-v4-01') for s in sorted(group['judgment_dispatch_order'],key=lambda x:x['dispatch_order'])]
r['outcome_policy']=r['outcome_policy'].replace('round-two','round-three')
r['research_scope']=r['research_scope'].replace('round-two','round-three')
with (G/'series.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
q=(OLD/'run_series.py').read_text().replace(sha(OLD/'series.json'),sha(G/'series.json'))
assert sha(G/'dispatch_series.py')==sha(OLD/'dispatch_series.py')
(G/'run_series.py').write_text(q)
check={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'old_seal_sha256':sha(OLD/'assessment-procedure.json'),'new_seal_sha256':sha(G/'assessment-procedure.json'),'only_changed_seal_paths':['/assessment_amendment/retained_objects'],'same_source_settings_assessor_environment_prompts_runtime':True,'assigned_workers':24,'assigned_judgments':32,'duplicates':8,'series_sha256':sha(G/'series.json'),'dispatcher_sha256':sha(G/'dispatch_series.py'),'queue_sha256':sha(G/'run_series.py'),'known_reporting_limitation':'Frozen source provenance gate remains unchanged; no repaired or substitute measures.'}
with (G/'static-binding-check.json').open('x') as f:json.dump(check,f,indent=2);f.write('\n')
print(json.dumps(check))
