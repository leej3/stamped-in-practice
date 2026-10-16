from pathlib import Path
import csv, hashlib, json, shutil

B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
D=B/'dataset'; O=B/'round-01-operational-extraction-01'; N=B/'operational-native-publication-01'
S=D/'assessment-series/narps-neutral-r1-operational-v4/synthesis'
E=D/'measurement-development/operational-series-closure-01'
S.mkdir(exist_ok=False); E.mkdir(exist_ok=False)
mapping=[]
def cp(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    raw=src.read_bytes(); dst.write_bytes(raw)
    assert src.read_bytes()==raw
    mapping.append({'source':str(src),'destination':str(dst.relative_to(D)), 'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
def tree(src,dst):
    for p in sorted(src.rglob('*')):
        if p.is_file():
            assert not p.is_symlink(),str(p)
            cp(p,dst/p.relative_to(src))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value)

for p in sorted((O/'snapshot-batch-11/analysis').iterdir()):
    if p.suffix in {'.json','.jsonl','.tsv'}:cp(p,S/'tables'/p.name)
for p in sorted((O/'final-round-01-summary-v2').iterdir()):
    if p.suffix in {'.png','.svg','.json'}:cp(p,S/'figures'/p.name)
for slot in sorted((O/'snapshot-batch-11/evidence/judgments').iterdir()):
    for name in ['report.md','scientific-report.md','response.json','scientific-judgment.json','output-binding.json','native-result.json','native-procedure-status.json','completion.json']:
        p=slot/name
        if p.exists():cp(p,E/'reports'/slot.name/name)
for name in ['final-review-01','final-replay-audit-01']:
    tree(O/name,E/name)
cp(O/'final-relocation-01/result.json',E/'relocation/result.json')
tree(B/'final-series-root-review-01',E/'independent-raw-review')
tree(B/'coordinator-navigation-review-02',E/'navigation-review')
tree(B/'operational-publication-coordinator-session-01',E/'publisher-coordination-session')
for name in ['final-git-reconciliation.json','final-git-reconciliation-checks.json','final-pending-hub-payloads.json','reconcile-final.py','hub-hold-state.json']:
    cp(N/name,E/'native-publication'/name)
for name in ['queue-01']+[f'batch-{i:02d}' for i in range(1,12)]:
    p=B/'assessment-series/narps-neutral-r1-operational-v4'/name
    for f in sorted(p.iterdir()):
        if f.is_file(): cp(f,E/'control'/name/f.name)
for name in ['watcher-resumption-03.json','watcher-resumption-04.json','known-checklist-issues-02.json','checklist-assessor-metadata-issue-16-j01-01.json','checklist-identity-issue-23-j01-01.json','scientific-binding-23-j01-01.json']:
    cp(O/name,E/'extraction-control'/name)
for name in ['closed-batch-watcher-03','closed-batch-watcher-04']:
    tree(O/name,E/'extraction-control'/name)
for name in ['run_series.py','dispatch_series.py']:
    cp(B/'repaired-series-registration-01'/name,E/'control'/name)

pub=json.loads((N/'final-git-reconciliation.json').read_text())
lines=['# All 32 retained native assessments','',
       'These are new sessions in the separate operational v4 series. Git and hosted identity checks passed for all 32. Five native publication bundles also completed fresh Hub retrieval; the other 27 remain partial. These counts do not describe the separate full-support archive publication.','',
       '| Slot | Immutable Git proof | Hosted session | Native Hub closure |','|---|---|---|---|']
for row in pub['records']:
    lines.append(f"| {row['slot']} | [proof](https://github.com/leej3/stamped-in-practice/tree/{row['proof_commit']}/coordinator/assessment-series/narps-neutral-r1-operational-v4/judgments/{row['slot']}) | [session]({row['session_url']}) | {'verified' if row['fully_verified_hub_publication'] else 'pending'} |")
lines+=['','Exact receipts and payload inventories are in [the reconciliation record](../../../measurement-development/operational-series-closure-01/native-publication/final-git-reconciliation.json). The 259 pending paths represent 191 distinct native/proof keys and 145,367,830 bytes; complete-support archives are additional. Raw native, original live shadow and later attached processed transcripts remain distinct representations. Coordinator publication earns no worker credit.','']
write(S/'SESSIONS.md','\n'.join(lines))

write(S/'README.md', '''# Round one: separate reassessment

All 24 original research deliveries and the same eight preselected duplicate slots received fresh judgments under the registered operational-copy procedure. All 32 were admitted, with 32 available scientific judgments and 30 valid checklist responses. The two invalid checklist responses are measurement missingness; their independent scientific judgments remain available.

The procedure resolved the original series' widespread annex-metadata admission failures. It did not establish consistent grading: duplicate judges differed on 67 of 248 item comparisons and five of eight scientific categories. These results do not establish a skill benefit or a reduction in variability.

Read the [measurement assessment](viability.md), [all native sessions and publication status](SESSIONS.md), [reproduction scope](REPRODUCE.md), and unchanged [original assessment synthesis](../../../rounds/round-01/synthesis/README.md). No original judgment was replaced or pooled with this series.

## Scientific judgments

These are judgments of the adequacy of the analysis, not whether the positive vmPFC hypothesis was supported. Primary judgments determine the worker summaries; duplicates never replace them. Each condition has six original workers.

| Assistance condition | Supported | Qualified | Not supported | Science available | Checklist valid |
|---|---:|---:|---:|---:|---:|
| Baseline | 6 | 0 | 0 | 6/6 | 4/6 |
| General skill discovery | 5 | 1 | 0 | 6/6 | 6/6 |
| Reproducible-science skill discovery | 3 | 2 | 1 | 6/6 | 6/6 |
| Explicit pinned STAMPED | 4 | 2 | 0 | 6/6 | 6/6 |

![Primary scientific adequacy by assistance condition](figures/scientific-adequacy.png)

The one `not supported` primary judgment concerns treatment of zero-coded noncoverage in group inference and the absence of a sensitivity check. That delivery reproduced 13 selected outputs exactly in the judge's replay; reproducibility of selected bytes did not resolve the inferential concern. This is the retained judge's assessment, not a new coordinator grade. [Original report](../../../measurement-development/operational-series-closure-01/reports/narps-neutral-r1-04-j01/report.md).

## Checklist evidence and disagreement

Checklist availability is 22/24 primary and 8/8 duplicate responses. Both invalid responses are baseline primaries: run23 omits `object.capture` despite including the correct digest in its URL; run16 omits required assessor identity/dependency metadata. The frozen validator does not repair either artifact. These are not worker failures.

![Primary checklist item statuses](figures/item-statuses.png)

All eight preselected pairs are available. Scientific categories differ in five pairs, always `supported` versus `qualified`. Item statuses differ in 67/248 comparisons (27.0%). The 31 items are nested within each of eight objects; 248 is not an independent replication count. Both original categories and item reasons remain in the [pair table](tables/pairs.tsv) and [raw reports](../../../measurement-development/operational-series-closure-01/reports/).

![Duplicate judgment disagreements](figures/duplicate-disagreement.png)

Limited reading of paired rationales found overlapping concerns assigned different severity or verification requirements. It does not establish one cause for all disagreements. There is no adjudication, consensus category or overall STAMPED score.

![Recurring primary checklist outcomes, pooled descriptively](figures/recurring-outcomes.png)

Recurring outcomes use the 22 valid primary checklists. Unequal valid denominators, discretionary judgments and this small single-study sample limit condition comparisons. Assignment, discovery, installation and observed use remain separate; the [original worker evidence](../../../rounds/round-01/synthesis/README.md) is unchanged.

## Replay and effort

All 32 judges retained a replay-related record. Native evidence establishes 15 helper invocations across 12 slots: eight reached a scientific entrypoint, four failed setup before entry, and three later invocations were refused because the allowance was already consumed. Seven executions bind helper output in the same event; one additional redirected-output chain is independently bound. The eight successful records concern selected outputs, not universal workflow or scientific validity.

The four destination-exists setup failures occurred in01-j01,05-j02,12-j01 and20-j01. Three later refused calls are additional invocations, not additional workers. The other 20 slots have no observed helper invocation; their records retain the judge's stated reason or scope. Unavailable replay is not a worker-science failure. [Exact event audit](../../../measurement-development/operational-series-closure-01/final-replay-audit-01/result.json).

![Original research and new assessment elapsed time](figures/effort.png)

![Original research parent-session tokens](figures/research-token-usage.png)

Research effort belongs to the original 24 deliveries; reassessment does not repeat that work. Elapsed session time includes waiting and is not computation-only time. Token input/output totals remain separate from their cached/reasoning subsets. Parent-session coverage is explicit; these are neither provider billing nor all-in coordinator effort.

## Limits and next iteration

The original and new assessment series have distinct measurement procedures and remain separate. The new mechanism admits operational copies while preserving canonical deliveries and protected content; allowed changes to three annex database paths are retained, not proof of database semantic equivalence. Scientific criteria and the external assessor pin stayed fixed.

Condition labels were omitted from the judging prompt, but complete blinding is not guaranteed on the shared host. Run04's report discloses displaying an external procedure with allocation records. Its assertion that it did not use them cannot prove absence of influence; the exact exposure is retained separately. No grade or admission was changed because of this disclosure.

The [prospective research-guidance revision](../../../skill-reflection/research-skill-revision-01/README.md) addresses reference routing, complete delivered artifacts, and reconstruction evidence rather than tuning to a preferred scientific answer. Its tests and limitations are retained. Round-two research remains unlaunched pending the recorded continuation decision; no extra sample or replacement is selected from these scores.
''')
write(S/'viability.md','''# Measurement viability after the complete series

This review uses all 32 fixed assessments of 24 original deliveries. It has no new numerical pass threshold and authorizes no replacements or sample extension.

| Measure | Original assessment series | Separate operational v4 series |
|---|---|---|
| Assigned observations | 24 primary + 8 duplicate | Same 24 primary + same 8 duplicate |
| Admission | 21/32; 11 metadata-related failures | 32/32 |
| Scientific judgments available | Bound by original admission | 32/32 |
| Valid checklist responses | Bound by original admission | 30/32; two malformed baseline primaries |
| Complete comparable duplicate pairs | 4/8 | 8/8 |
| Item-status disagreements | 32/124 in four available pairs | 67/248 in all eight pairs |
| Science-category disagreements | 1/4 available pairs | 5/8, all supported/qualified |

The differing available pairs and measurement mechanisms prevent treating these rates as a clean improvement or deterioration in reliability. Original observations remain unchanged and are not selectively substituted.

The operational mechanism now supports the intended complete series: canonical/protected evidence checks pass, all scientific records bind exact original captures and reports, and every preselected pair can be inspected. Remaining checklist missingness is separate from science availability. Substantial grading disagreement limits small condition contrasts and claims about reduced variance; schema/integrity success alone is not measurement reliability.

Replay is an optional and incomplete instrument. Eight native entrypoint executions are evidenced; four setup failures and three allowance refusals are preserved. The practical instrument lesson is to check disposable destination preconditions before consuming an allowance. No helper, grade, allowance or criterion was changed during this series.

The same-host relocated reporting check reproduced all 36 table files exactly while denying 1,882 original paths and verifying 1,064 copied files unchanged. It preserves the two original checklist issues and return code2. It establishes relocation of retained reporting evidence, not cross-host scientific replay or complete remote payload access.

Continuation must preserve these limits, the fixed sample/stopping rule, all primary and duplicate labels, and the unchanged v4 measurement mechanism. A later seal may bind new original delivery identities without changing that mechanism. The prepared round-two source changes only the permitted research-skill input; it is not yet a launched round. The coordinator's continuation decision will be retained additively, outside original outcomes.

Full local retention and Git/Entire identity publication are complete for all32 sessions. Native Hub retrieval is complete for five and pending for27; full-support archives are separately scoped. Transport failure does not erase evidence, excuse incomplete preservation, or make a partial remote publication complete.
''')
write(S/'REPRODUCE.md','''# Reproduce and inspect this summary

The tables in `tables/` are byte-identical copies of the frozen final extraction. They retain the full registered72-worker/96-judgment allocation; the six human-facing figures filter round one only (24 workers/32 judgments). Future pending rounds are outside current missingness.

The source snapshot index is `2737380bb88b4ac609736fefc496e3ad1a98c1ecc72d434c7011b33b0622ad13`. The assessment seal is `6f25ebbec5310442e8fd3fd20bd20682ecb5653b350362119af3e825a2668084`; the original research seal remains `b011f6e68dc6838e736f1ae2ad70d52896dab9b848d6f33950b4d35dd86b1521`.

The [closure evidence](../../../measurement-development/operational-series-closure-01/README.md) includes original reports/responses, exact event audits, independent raw-output checks, native publication indexes and controller closure. Its full extraction archive preserves intermediate snapshots, failed checks, original figures, executable reporting sources, explicit source-path maps and final relocation commands. No raw receipt was rewritten to make a path portable.

The original frozen aggregator returned2 for exactly two invalid checklist artifacts. Additive reporting revision `2f641a9134b9740a3ee859d8f2bd2d7e487fe957` accepts an explicit hash-checked source-path map; its final relocation trial returned the same2 and all36 table files were identical. The [receipt](../../../measurement-development/operational-series-closure-01/relocation/result.json) records denied original-path access, retained-file integrity and changed provenance fields. This reporting-tool revision is separate from the sealed runtime used by judges.

All selected reports and summary tables are ordinary Git files for browsing. Bulk extraction, transcripts and support archives remain annex payloads. Their current upload/retrieval status is explicit; while Hub transport is held, do not claim a new recipient can obtain every new payload. Use the repository's retrieval guide when access is restored. Existing fully verified experiment gitlinks remain in place; [new native Git/Entire proofs](SESSIONS.md) are directly linked without falsely promoting partial support commits.
''')
write(E/'README.md','''# Complete operational-series closure evidence

These coordinator records support the [separate round-one synthesis](../../assessment-series/narps-neutral-r1-operational-v4/synthesis/README.md). Original scientific objects and judge outputs remain unchanged. Reports and responses below are exact byte copies; coordinator reviews, publication sessions and transport receipts are separately attributed.

- `reports/`: all32 original scientific reports, checklist responses, structured science records and native identity receipts.
- `final-review-01/`, `final-replay-audit-01/`, `relocation/`: separate availability, paired-observation and native-execution checks. The final native audit adds the failed-status12-j01 commands missed by an earlier candidate scan; earlier evidence stays retained.
- `independent-raw-review/`: independent verification of all32 categories/report hashes/excerpts and all248 duplicate item comparisons.
- `native-publication/`:32 Git/Entire verifications, five complete native Hub closures,27partial; exact259pendingpaths/191keys/145,367,830bytes exclude full-support archives.
- `control/` and `extraction-control/`: closed dispatcher/batch/watchers, including absence observations and failed watcher checks. No termination cause is inferred from an absent process.
- `navigation-review/`, `publisher-coordination-session/`: closed coordinator reviews/publication work, not formal assessment observations.

The complete extraction tree will be retained as an annexed archive with its member manifest and byte verification. New bulk payload upload/retrieval remains pending Hub recovery, while ordinary Git reports and indexes are available. Complete stopped attempts, canonical/operational copies, replay trees and all native representations remain in closed per-slot preservation inventories; full-support archive packaging and transfer are tracked separately. No evidence has been discarded.
''')
write(E/'source-copies.json',json.dumps({'copies':mapping,'source_bytes_preserved':True},indent=2)+'\n')
write(S/'.gitattributes','figures/* annex.largefiles=nothing\ntables/* annex.largefiles=nothing\n')
print(json.dumps({'summary':str(S),'evidence':str(E),'copies':len(mapping),'bytes':sum(x['bytes'] for x in mapping)}))
