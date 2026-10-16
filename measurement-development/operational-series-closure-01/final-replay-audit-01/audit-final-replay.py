"""Additive final native replay audit; never executes or edits research evidence."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parent
SNAP=ROOT/'snapshot-batch-11'
OUT=ROOT/'final-replay-audit-01'
OUT.mkdir(exist_ok=False)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def ref(p): return {'path':str(p),'sha256':sha(p.read_bytes())}
def read(p): return json.loads(p.read_bytes())
def write(name,value): (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
meta=read(SNAP/'snapshot.json')
assert meta['closed_current_series_launchers']==32 and meta['pending_current_series_slots']==0
review=read(ROOT/'final-review-01/review.json')
replay=read(SNAP/'replay-native-observations.json')
old=read(ROOT/'replay-invocation-audit-01.json')
supp=read(ROOT/'replay-redirection-binding-21-j01-01.json')
manifest=read(SNAP/'source-manifest.json')
expected={v['copy']['path']:v['sha256'] for v in manifest}

sources={}; events={}; candidates=[]
for path in sorted((SNAP/'evidence/judgments').glob('*/native-events.jsonl')):
    assert sha(path.read_bytes())==expected[str(path.relative_to(SNAP))]
    sid=path.parent.name;sources[sid]=ref(path)
    for number,raw in enumerate(path.read_bytes().splitlines(),1):
        event=json.loads(raw); item=event.get('item',{})
        record={'judgment_id':sid,'native_events':sources[sid],'line':number,'raw_event_sha256':sha(raw),'event':event}
        events[(sid,number)]=record
        if event.get('type')=='item.completed' and item.get('type')=='command_execution' and 'fresh-rerun' in item.get('command',''):
            candidates.append(record)
assert len(sources)==32
# Preserve and revalidate the earlier reviewed failure observations.
classified=[]
for old_event in old['reviewed_events']:
    key=(old_event['judgment_id'],old_event['line']);new=events[key]
    assert new['raw_event_sha256']==old_event['raw_event_sha256']
    assert new['native_events']['sha256']==old_event['events']['sha256']
    classified.append({**new,'classification':old_event['reviewed_event_classification'],'entrypoint_execution_observed':False})
# Final audit correction: completed events with a failed command status were
# absent from the earlier narrow candidate inventory, though retained in raw logs.
for line,classification,needle in ((26,'setup-failed-before-entrypoint','Materialization requires a new destination'),(29,'later-invocation-refused','Formal replay allowance already consumed; retain this attempt')):
    event=events[('narps-neutral-r1-12-j01',line)]
    item=event['event']['item']
    assert event['event']['type']=='item.completed' and item['status']=='failed'
    assert 'fresh-rerun --path' in item['command'] and needle in item['aggregated_output']
    classified.append({**event,'classification':classification,'entrypoint_execution_observed':False})
# Same-event matches remain exactly the frozen postprocessing observations.
bound=[]
for row in replay['rows']:
    if not row['native_helper_completion_observed']: continue
    evidence_path=SNAP/row['evidence']['path']; assert sha(evidence_path.read_bytes())==row['evidence']['sha256']
    evidence=read(evidence_path)
    event=events[(row['judgment_id'],evidence['line'])]
    assert event['raw_event_sha256']==evidence['raw_event_sha256']
    assert row['entrypoint_execution_observed'] and row['entrypoint_returncode']==0
    artifact=SNAP/row['supporting_record']['artifact']['path'];assert sha(artifact.read_bytes())==row['supporting_record']['artifact']['sha256']
    bound.append({'judgment_id':row['judgment_id'],'native_binding':'same-event','helper_record':ref(artifact),'binding_receipt':ref(evidence_path),'capture_sha256':row['supporting_record']['reported_capture_sha256'],'entrypoint_returncode':row['entrypoint_returncode'],'reported_comparison':row['literal_comparison']})
    classified.append({**event,'classification':'helper-completed-entrypoint-executed','native_binding':'same-event','entrypoint_execution_observed':True})
assert len(bound)==7
# Supplementary redirection chain must still have exactly the retained native bytes.
sid=supp['judgment_id'];assert sources[sid]['sha256']==supp['native_events']['sha256']
for previous in supp['events']:
    event=events[(sid,previous['line'])]
    assert event['raw_event_sha256']==previous['raw_event_sha256'] and event['event']==previous['event']
previous_path=Path(supp['saved_report']['path'])
artifact=SNAP/previous_path.relative_to(Path(supp['source_snapshot']))
assert sha(artifact.read_bytes())==supp['saved_report']['sha256']
assert read(artifact)==supp['literal_helper_report']
assert supp['entrypoint_returncode']==0 and supp['entrypoint_execution_observed']
bound.append({'judgment_id':sid,'native_binding':'separately-validated-redirected-output-chain','helper_record':ref(artifact),'binding_receipt':ref(ROOT/'replay-redirection-binding-21-j01-01.json'),'capture_sha256':supp['literal_helper_report']['capture']['sha256'],'entrypoint_returncode':0,'reported_comparison':supp['reported_comparison']})
classified.append({**events[(sid,70)],'classification':'helper-completed-entrypoint-executed','native_binding':'separately-validated-redirected-output-chain','entrypoint_execution_observed':True})
assert len({(e['judgment_id'],e['line']) for e in classified})==len(classified)==15
counts=Counter(e['classification'] for e in classified)
assert counts=={'setup-failed-before-entrypoint':4,'later-invocation-refused':3,'helper-completed-entrypoint-executed':8}
ids={x['judgment_id'] for x in classified};assert len(ids)==12
item='stamped-checklist:should/004'
response=SNAP/'evidence/judgments/narps-neutral-r1-12-j01/response.json'
dependency={'judgment_id':'narps-neutral-r1-12-j01','response':ref(response),'item':item,'literal_response':read(response)['responses'][item],'decision':'Retain not-checked unchanged. Literal reason and evidence cite no worker fresh-environment testing record; failed assessor setup does not establish target behavior.'}
classification_by_key={(e['judgment_id'],e['line']):e['classification'] for e in classified}
for c in candidates:
    c['review_classification']=classification_by_key.get((c['judgment_id'],c['line']),'mention-only: help/source inspection, report/ledger writing, or retained-artifact reading; no execution counted')
write('candidate-inventory.json',candidates)
write('reviewed-invocations.json',classified)
write('helper-completions.json',bound)
write('checklist-dependency-12-j01.json',dependency)
groups=[]
availability=read(SNAP/'round-01-availability.json')['rows']
for condition in (None,'baseline','discover-general','discover-science','stamped-explicit'):
 for role in (None,'primary','duplicate'):
    rows=[x for x in availability if (condition is None or x['condition']==condition) and (role is None or x['role']==role)]
    selected={x['judgment_id'] for x in rows}
    group={'condition':condition,'role':role,'assigned_slots':len(rows),'same_event_entrypoints':sum(x['judgment_id'] in selected and x['native_binding']=='same-event' for x in bound),'redirected_chain_entrypoints':sum(x['judgment_id'] in selected and x['native_binding']!='same-event' for x in bound)}
    for typ in ('setup-failed-before-entrypoint','later-invocation-refused'):group[typ]=sum(x['judgment_id'] in selected and x['classification']==typ for x in classified)
    groups.append(group)
result={'kind':'final-native-replay-evidence-audit','interim':False,'script':ref(Path(__file__)),'snapshot_index':ref(SNAP/'index.json'),'native_sources':list(sources.values()),'source_replay_observations':ref(SNAP/'replay-native-observations.json'),'prior_audit':ref(ROOT/'replay-invocation-audit-01.json'),'supplementary_redirection':ref(ROOT/'replay-redirection-binding-21-j01-01.json'),'method_correction':'Earlier candidate enumeration required command status completed. Final additive inventory includes every item.completed command, including failed command statuses. This adds12-j01 events26/29; raw frozen source and earlier outputs remain unchanged.','counts':{'assigned_slots':32,'slots_with_observed_invocation':12,'native_invocation_events':15,'same_event_bound_entrypoints':7,'separately_bound_redirection_entrypoints':1,'total_observed_entrypoint_executions':8,'setup_failed_before_entrypoint':4,'later_invocations_refused':3,'retained_declared_replay_records':32,'declared_met_records':8,'declared_not_checked_records':24,'candidate_mentions':len(candidates)},'groups':groups,'setup_failure_slots':[e['judgment_id'] for e in classified if e['classification']=='setup-failed-before-entrypoint'],'refused_invocation_slots':[e['judgment_id'] for e in classified if e['classification']=='later-invocation-refused'],'helper_completions':bound,'scope':'Observed commands and explicit helper entrypoint returncodes only. Help/report mentions are not replay attempts. Selected outputs only; retained same-host environment/cache and documented external interpreters do not establish independent environment reconstruction or cross-host portability. Optional replay unavailability is not scientific failure. No rerun, repair, regrading or substitution.','artifacts':[ref(OUT/name) for name in ('candidate-inventory.json','reviewed-invocations.json','helper-completions.json','checklist-dependency-12-j01.json')]}
write('result.json',result)
print(json.dumps({'result':ref(OUT/'result.json'),'counts':result['counts'],'groups':groups}))
