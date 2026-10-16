"""Summarize all 32 closed stopped-judge evidence bundles without reading grades.
Only preservation metadata, bound hashes, and control files are read.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def ref(p):
    b=p.read_bytes();return {'path':str(p),'size':len(b),'sha256':sha(b)}
checked={}
def check(r):
    p=Path(r['path']);actual=checked.setdefault(str(p),ref(p))
    assert actual['sha256']==r['sha256'] and actual['size']==r['size'],str(p)
    return actual
planpath=BASE/'dataset/rounds/round-01/plan.json';assignments=sorted(read(planpath)['assigned_judgments'],key=lambda a:a['dispatch_order']);assert len(assignments)==32
batches=[];rows=[]
counts={'judgments':0,'main_retention_regular_files':0,'main_retention_regular_bytes':0,'attempt_source_regular_files':0,'attempt_source_regular_bytes':0,'raw_native_transcripts':0,'raw_native_bytes':0,'original_shadow_transcripts':0,'completed_events':0,'profile_entrypoint_occurrences':0,'workspace_entrypoint_occurrences':0,'supplied_skill_target_directories':0,'changed_targets_preserved':0,'changed_target_source_regular_files':0,'changed_target_source_regular_bytes':0,'target_added_paths':0,'target_missing_paths':0,'target_modified_paths':0,'payload_difference_events':0,'child_spawn_evidence_items':0,'literal_child_match_resolutions':0,'original_main_verification_failures_retained':0}
for n in range(1,12):
    p=BASE/f'round-01-judge-batch-{n:02d}'/'retention-closed.json';b=read(p);assert b['preservation_complete'] and b['batch']==n;batches.append(ref(p));check(b['registered_plan'])
    for item in b['helper_files_at_closure']:check(item)
    for j in b['judgments']:
        for key in ['main_capture_manifest','main_integrity_audit','main_verification','main_script']:check(j[key])
        for item in j['external_receipts']:check(item)
        v=read(Path(j['main_verification']['path']));a=read(Path(j['main_integrity_audit']['path']));assert a['verified'] and (v['verified'] or a.get('child_match_resolution'))
        row={'assignment':j['assignment'],'retention':j['retention'],'capture_finished_at':v['capture_finished_at'],'judge_finished_at':v['judge_finished_at'],'launcher_status':j['launcher_status'],'preservation_verified':True,'original_capture_verified':v['verified'],'main_capture_manifest':j['main_capture_manifest'],'main_audit':j['main_integrity_audit'],'completed_events':v['completed_events'],'raw_native_bytes':v['native_bytes'],'original_shadow_transcripts':v['shadow_transcripts'],'payload_difference_events':v['payload_difference_events'],'child_spawn_evidence':v['child_spawn_evidence'],'profile_entrypoints':v['profile_skill_entrypoints'],'workspace_entrypoints':v['workspace_skill_entrypoints'],'source_before_after_equal':v['source_before_after_equal']}
        counts['judgments']+=1;counts['main_retention_regular_files']+=a['entry_kinds']['file'];counts['main_retention_regular_bytes']+=a['regular_file_bytes'];counts['attempt_source_regular_files']+=v['source_attempt_files'];counts['attempt_source_regular_bytes']+=v['source_attempt_bytes'];counts['raw_native_transcripts']+=1;counts['raw_native_bytes']+=v['native_bytes'];counts['original_shadow_transcripts']+=v['shadow_transcripts'];counts['completed_events']+=v['completed_events'];counts['profile_entrypoint_occurrences']+=v['profile_skill_entrypoints'];counts['workspace_entrypoint_occurrences']+=v['workspace_skill_entrypoints'];counts['supplied_skill_target_directories']+=v['supplied_skill_target_directories'];counts['payload_difference_events']+=v['payload_difference_events'];counts['child_spawn_evidence_items']+=len(v['child_spawn_evidence'])
        if 'child_match_resolution' in j:
            for item in j['child_match_resolution'].values():check(item)
            row['child_match_resolution']=j['child_match_resolution'];counts['literal_child_match_resolutions']+=1
        counts['original_main_verification_failures_retained']+=int(not v['verified'])
        if 'target_as_found' in j:
            t=j['target_as_found']
            for item in t.values():check(item)
            tv=read(Path(t['verification']['path']));delta=read(Path(t['delta']['path']));assert tv['preservation_verified']
            row['target_as_found']={**t,'path_delta_counts':{k:len(delta[k]) for k in ['added','missing','modified']}}
            counts['changed_targets_preserved']+=1;counts['changed_target_source_regular_files']+=tv['source_regular_files'];counts['changed_target_source_regular_bytes']+=tv['source_regular_bytes']
            for key in ['added','missing','modified']:counts[f'target_{key}_paths']+=len(delta[key])
        rows.append(row)
assert [r['assignment'] for r in rows]==assignments
out=BASE/'judge-retention-final-01';out.mkdir(exist_ok=False)
summary={'schema':'complete-stopped-judge-preservation-index-v1','completed_at':datetime.now(timezone.utc).isoformat(),'registered_plan':ref(planpath),'fixed_assignment_count':32,'preserved_assignment_count':len(rows),'all_registered_judgments_covered':True,'all_preservation_audits_passed':True,'counts':counts,'batches':batches,'judgments':rows,'scope':'All 32 registered judgments preserved only after finalized launcher control receipts, using additive late snapshots. Exact raw native and original Entire processed shadows are separate, with completed-event identity proof; payload equality is not assumed. Full output trees include failures, probes and replay artifacts. Skill availability is not installation/use credit. Separate changed-target copies preserve prior path/content changes without repair. Scientific and STAMPED content was neither interpreted nor graded by preservation.','limitations':['Late bounded capture is not an atomic or launcher stop-time snapshot.','Launcher exit/target status and judgment validity remain separate from successful preservation.','Hosted publication is not verified by this local evidence index.'],'source_modified_by_preservation':False,'hosted_publication_verified':False}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
metadata=[]
for root in [HERE,BASE/'judge-retention-passes-01']:
    metadata.extend(ref(p) for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink())
(out/'supporting-files.json').write_text(json.dumps({'scope':'Exact observer scripts, command/output receipts and bounded control observations; no publication implied.','files':metadata},indent=2)+'\n')
(out/'manifest.json').write_text(json.dumps({'files':[ref(out/'summary.json'),ref(out/'supporting-files.json')],'verified_external_references':list(checked.values()),'script':ref(Path(__file__))},indent=2)+'\n')
print(json.dumps({'summary':ref(out/'summary.json'),'manifest':ref(out/'manifest.json'),'counts':counts},indent=2))
