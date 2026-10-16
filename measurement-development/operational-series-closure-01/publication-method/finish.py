from pathlib import Path
import json,hashlib,shutil
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset';O=B/'round-01-operational-extraction-01'
S=D/'assessment-series/narps-neutral-r1-operational-v4/synthesis';E=D/'measurement-development/operational-series-closure-01'
mapfile=E/'source-copies.json';mapping=json.loads(mapfile.read_text())['copies']
def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes();dst.write_bytes(raw);assert src.read_bytes()==raw
 mapping.append({'source':str(src),'destination':str(dst.relative_to(D)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
for name in ['final-delivery-03.json','final-evidence-report-03.md','final-evidence-report-02.json','final-context-exposure-04-j01-01.json','final-figure-qa-01.json','disagreement-interpretation-01.json','replay-redirection-binding-21-j01-01.json']:
 cp(O/name,E/name)
for p in sorted((B/'operational-extraction-package-01').iterdir()):cp(p,E/'extraction-archive'/p.name)
# Each reviewer identity is explicitly recorded by the review itself.
R=B/'final-series-summary-review-01';receipt=json.loads((R/'receipt.json').read_text());sid=receipt['CODEX_THREAD_ID']
source=next(Path('/Users/johnlee/.codex/sessions/2026/10/16').glob('*'+sid+'.jsonl'));raw=source.read_bytes();records=[json.loads(x) for x in raw.splitlines()]
assert records[0]['payload']['id']==sid and records[-1]['payload']['type']=='task_complete'
local=B/'final-series-summary-review-session-01';local.mkdir(exist_ok=False);(local/'raw-session.jsonl').write_bytes(raw);assert source.read_bytes()==raw
(local/'receipt.json').write_text(json.dumps({'session_id':sid,'source':str(source),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'records':len(records),'task_complete_events':sum(x.get('payload',{}).get('type')=='task_complete' for x in records),'scope':'Closed coordinator review; not a formal assessment observation','source_before_copy_after_equal':True},indent=2)+'\n')
for root,label in [(R,'summary-review'),(local,'summary-review/native-session')]:
 for p in sorted(root.rglob('*')):
  if p.is_file():cp(p,E/label/p.relative_to(root))
# Exact script/metadata provenance for the publication transformation.
for name in ['prepare.py','finish.py','archive-extraction.py']:
 cp(B/'operational-synthesis-publication-01'/name,E/'publication-method'/name)
mapfile.write_text(json.dumps({'copies':mapping,'source_bytes_preserved':True},indent=2)+'\n')

p=S/'README.md';text=p.read_text();text=text.replace('Condition labels were omitted from the judging prompt, but complete blinding is not guaranteed on the shared host. Run04\'s report discloses displaying an external procedure with allocation records. Its assertion that it did not use them cannot prove absence of influence; the exact exposure is retained separately. No grade or admission was changed because of this disclosure.', 'Condition labels were omitted from the judging prompt, but the supplied `$STAMPED_PROCEDURE` path exposed the complete sealed allocation. Run04-j01 native event10 displayed it, including its own `discover-science` assignment, replicate2, wave8 and launch_position3, alongside other runs. Its report called the records unrelated and denied using them; the recorded bytes establish current-object assignment exposure, while influence remains unknown. This is a coordinator-supplied context defect, not proof of blinding. The [exact native/report receipt](../../../measurement-development/operational-series-closure-01/final-context-exposure-04-j01-01.json) is retained; no grade, admission or observation was changed or replaced.')
text=text.replace('Round-two research remains unlaunched pending the recorded continuation decision; no extra sample or replacement is selected from these scores.', 'All further formal launches are held pending a reviewed correction to supplied assessment context and a declared measurement boundary. Round-two research remains unlaunched; no extra sample or replacement is selected from these scores.')
p.write_text(text)
p=S/'viability.md';text=p.read_text();text=text.replace('The operational mechanism now supports the intended complete series:', 'Operational completion and identity binding improved:')
text=text.replace('Continuation must preserve these limits,', 'A newly verified supplied-context defect prevents declaring this a condition-blinded assessment: `$STAMPED_PROCEDURE` directly exposed the sealed current allocation, and04-j01 displayed its own assignment. Its no-use claim cannot establish absence of influence. Preserve all32 judgments unchanged; hold all further formal launches for an isolated, reviewed runtime-context projection and an explicit new measurement boundary. Do not silently treat a documentation disclaimer as the repair.\n\nAny later continuation must preserve these limits,')
p.write_text(text)
p=E/'README.md';text=p.read_text().replace('The complete extraction tree will be retained as an annexed archive with its member manifest and byte verification.', 'The complete extraction tree is retained in `extraction-archive/evidence.tar.gz`:13,801 members,857,879,921 uncompressed regular-file bytes,191,569,033 archive bytes; SHA-256 `904302d5f8a993438be73e210e30c68155c68b5a597c169213a263f27c68b315`. Every member hash/mode/link and source-before/after inventory was verified, with no exclusions. The member manifest and exact packaging sources are beside it.')
text+='\nThe [context exposure receipt](final-context-exposure-04-j01-01.json) establishes that supplied procedure metadata included the current allocation and run04’s own assistance condition. This defect holds future launches; the completed observations remain immutable.\n';p.write_text(text)
(D/'STATUS.md').write_text('''# Current comparison status

**Round one and its separately registered reassessment are complete; all further formal launches are held.** The original24 workers are unchanged. The original32 judgments admitted21 and lost11 to annex-metadata integrity failures. The separate operational v4 series admitted all32, with32 available scientific judgments and30 valid checklist responses.

Read the [separate reassessment synthesis and figures](assessment-series/narps-neutral-r1-operational-v4/synthesis/README.md), [measurement viability and current hold](assessment-series/narps-neutral-r1-operational-v4/synthesis/viability.md), and unchanged [original synthesis](rounds/round-01/synthesis/README.md). Duplicate judgments disagree on67/248 item comparisons and5/8 scientific categories; these results do not establish a skill benefit or grading reliability.

The supplied assessment procedure exposed allocation records. Exact native evidence shows04-j01 displayed its own condition. The completed32 observations remain unchanged; future launches await a reviewed context-projection correction and a declared measurement boundary. The remaining48 research attempts and64 judgments have not launched, and the formal research-skill pin has not changed.

All24 original deliveries and their original-series support are published and independently retrieved. For the new series, all32 stopped sessions are fully retained locally and have verified Git/Entire identities. Native Hub retrieval is complete for5 and pending for27; full-support archives have separate status. See [every immutable native proof and exact transport scope](assessment-series/narps-neutral-r1-operational-v4/synthesis/SESSIONS.md). No evidence was discarded; Hub recovery remains pending without further retries.

The [prospective research-guidance revision](skill-reflection/research-skill-revision-01/README.md) and [unlaunched round-two preparation](rounds/round-02/preparation-01/source-skill-binding.json) remain candidates. There is no preset spending, token or elapsed-time cap, no outcome-selected extension and no replacement of primary labels with favorable duplicate grades.

Read the [controller handoff](assessment-series/narps-neutral-r1-operational-v4/HANDOFF.md) and published control closure before any continuation. Historical PID/process snapshots do not establish current liveness. The completed queue must not be restarted. Detailed registration, frozen records and prior progress remain available in this subdataset.
''')
series=S.parent
p=series/'README.md';text=p.read_text();text=text.replace('The series is running; see the [control progress](progress.json) and [final preparation review](../../measurement-development/assessment-operational-followup-01/README.md).','The series is complete; see the [synthesis and figures](synthesis/README.md), [control progress](progress.json) and [final preparation review](../../measurement-development/assessment-operational-followup-01/README.md).');text=text.replace('All 32 assigned attempts will be retained regardless of grade, replay or admission.','All32 assigned attempts are retained regardless of grade, replay or admission.');text=text.replace('Later research remains held until this separate series supports a measurement-viability decision.','All further formal launches are held for the [supplied-context defect and measurement-boundary review](synthesis/viability.md).');p.write_text(text)
p=series/'HANDOFF.md';text=p.read_text();text='''## Closure update

The fixed32-attempt queue and extraction watcher04 have completed, each exit0. No formal assessment session remains active. Exact queue/batch/watcher receipts are retained in [closure evidence](../../measurement-development/operational-series-closure-01/README.md). Do not restart this queue or replace any attempt. The earlier process snapshots below are historical.

All further formal launches are held for the supplied-procedure allocation exposure described in the [viability record](synthesis/viability.md). Local full-support packaging may continue, but it does not launch agents or claim pending Hub payloads are retrievable.

'''+text;p.write_text(text)
progress={'series':'narps-neutral-r1-operational-v4','status':'completed-future-launches-held','research_workers':24,'assigned_judgments':32,'finalized':32,'admitted':32,'scientific_available':32,'checklist_valid':30,'checklist_invalid':2,'pending_current_slots':0,'native_entrypoint_executions':8,'duplicate_pairs':8,'item_disagreements':67,'item_comparisons':248,'science_pair_disagreements':5,'original_index_sha256':'2737380bb88b4ac609736fefc496e3ad1a98c1ecc72d434c7011b33b0622ad13','assessment_procedure_sha256':'6f25ebbec5310442e8fd3fd20bd20682ecb5653b350362119af3e825a2668084','future_launch_hold':'Supplied full procedure exposes current allocation; reviewed context projection and declared boundary required. Completed results unchanged.','publication':{'local_native_captures':32,'git_entire_verified':32,'native_hub_complete':5,'native_hub_partial':27,'native_pending_unique_keys':191,'native_pending_unique_bytes':145367830,'full_support_archives':'separate scope; locally packaging remaining slots; remote transport pending'}}
(series/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
print(json.dumps({'copies':len(mapping),'bytes':sum(x['bytes'] for x in mapping),'summary_review_session':sid,'extraction_archive_complete':True}))
