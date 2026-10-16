# Independent assessment — NARPS gain effect in vmPFC

**STAMPED verdicts:** MUST: 3 met / 4 partial / 10 unmet / 0 not-checked; SHOULD: 0 met / 2 partial / 5 unmet / 1 not-checked / 1 not-applicable; MAY: 2 met / 3 partial / 0 unmet / 0 not-checked. Partial MUST items do not count as satisfied. No overall score is assigned.

## What to fix first

1. **Commit the analysis, report, figures, and result files and record each run with its exact environment** → makes the scientific delivery and result provenance traceable (**must/004, must/006**).
2. **Add an installable, locked environment and setup/use instructions, including the atlas retrieval requirement** → lets another researcher reconstruct the group analysis (**must/003, must/007, must/010–017**).
3. **Pin and make the Harvard–Oxford atlas retrieval durable within the declared study boundary** → protects the vmPFC mask definition from external changes (**must/001, must/002, may/001**).
4. **Publish an authorized, durable route to the complete study object and its environment** → makes the code, data, results, and setup retrievable by an intended researcher (**must/016; access record**).
5. **Add repeat and clean-environment execution records** → shows the documented workflow remains usable (**should/002, should/004, should/006**).

## What is already good

- The captured delivery contains all 54 supplied participant maps, matching metadata and source checksums, plus input QC, group outputs, code, and figures. The QC table has 54 rows and every row matches input/sources.json; no participants were excluded ([QC](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-15-j02/content/workspace/results/input_qc.csv), [sources](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-15-j02/content/workspace/input/sources.json)).
- The analysis uses independent participant-level maps and one-sided whole-brain max-T sign-flip correction, and it gives an explicit, operational vmPFC definition ([analysis](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-15-j02/content/workspace/analysis/group_analysis.py), [mask definition](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-15-j02/content/workspace/results/vmPFC_mask_definition.txt)).
- The scientific report describes the normalized gain coefficient, limits the inference to the fixed upstream maps, reports uncertainty, and explains why a nonsignificant result is not proof of no effect ([report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-15-j02/content/workspace/report.md)).

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion is that these data and this group analysis do not support a positive vmPFC gain effect after whole-brain correction. That bounded conclusion is supported by the method and supplied results. The reported outcome is separate from the checklist verdicts: no vmPFC voxel survived positive one-sided max-T FWE correction across the common-coverage mask (198,029 voxels; 10,000 participant-level whole-image sign flips; α=.05). The operational vmPFC summary was −0.00051 estimate units, with an uncorrected 95% t interval [−0.0222, 0.0212] and one-sided p=.519. The interval includes positive and negative effects, so the result does not establish a zero effect or exclude a smaller increase. Twenty-four corrected positive voxels occurred in three small posterior occipital clusters outside the operational vmPFC mask.

This is a defensible group-stage analysis of the supplied estimates. It checks input hashes, dimensions, affines and finite values; retains all 54 participants; applies the same whole-brain sign to each participant map per permutation; and corrects the maximum statistic over common coverage. The report appropriately says the maps are participant contrast estimates whose gain modulator was normalized upstream, not a response-per-currency-unit estimate. It also acknowledges that participant variance maps and an executable upstream pipeline are unavailable.

The conclusion is qualified by the symmetry assumption for sign-flip inference, the atlas/template mismatch and non-unique vmPFC boundary, and the fixed upstream model. The supplied figures are interpretable: one shows the mean map with FWE discoveries and one shows participant-level vmPFC summaries. No replay was performed, so shipped outputs are evidence from the stopped delivery, not evidence of a fresh rerun. See [scientific-assessment.json](2026-10-16-scientific-assessment.json) for the structured result and [replay record](2026-10-16-replay-record.json) for the replay decision.

## Delivery boundary, attribution, and scope

The frozen runner's version check passed and the delivery manifest validates against the worker-stop receipt: capture SHA-256 f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9, 1,143 entries, complete status, zero errors and omissions. The worker-stop HEAD is d857ab1302d13cb660a7a044af07141f44bfa9ba. The stop log records an Entire session-checkpoint commit; however, the scientific deliverable paths remained untracked, so that checkpoint does not establish their versioning. The manifest preserves the full stopped workspace, including untracked analysis/, report.md, figures/, and results/; the probe correctly reports those deliverables were not committed. The data's annex structure is present in the stopped delivery, while the stop receipt identifies the participant maps and metadata as supplied inputs; this assessment does not attribute their original annexing to the worker.

The worker report identifies a main script and package versions but provides no installable environment, environment update procedure, or exact execution command. The code retrieves the Harvard–Oxford atlas at runtime. The no-replay decision was made before execution: the supplied package versions do not include a setup recipe, and the captured replay adapter cannot enforce the 5 GB cap on that outbound atlas retrieval. No copy was run, no shipped output was removed, and no source files were changed. This limitation does not lower the scientific conclusion based on the unchanged delivered evidence.

No worker-declared retrieval route was found in the report or stop-state Git configuration; that configuration has no remote. The intended recipient is a researcher using an authorized route, but there was no route to test. The coordinator's delivery of the complete capture to this assessment is preservation evidence only, not proof of worker sharing. judge-target.json was absent, so its reference_limits could not be consulted; no original absolute/external pointer or Git pointer was followed. A standalone help call to the encoder with system Python failed because jsonschema was unavailable; this assessor-side invocation error did not affect any measure. The pinned runner's response action and validation succeeded.

The captured .entire history/metadata paths reveal an assistance-related record. This exposure is noted only; those files were not used as grading evidence, and no treatment assignment is inferred or reported. The supplied task and scientific guidance are treated as the applicable brief; goal/kind confirmation was unavailable, so the kind is a labelled assumption.

## Per-item STAMPED checklist


| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/group_analysis.py` | Atlas data needed for the vmPFC mask is fetched at runtime; it is not bundled under the study root. |
| must/002 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/group_analysis.py` | Participant maps are local, but the vmPFC atlas is retrieved outside the root through Nilearn. |
| must/003 | S.1 | unmet | judgement | `report.md` | Python dependencies are named in the report but no environment specification installs or links them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `probe:tree-clean` | The analysis, report, figures, and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex` | Git-annex pointers and payloads preserve all 54 input maps in the captured repository. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked` | No provenance record links the generated results to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point | `report.md` | The report describes files but gives no installation or usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md` | The report identifies analysis/group_analysis.py as the complete group-analysis entry point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis/group_analysis.py` | The delivered analysis script builds paths relative to its own root. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `report.md` | Required Python packages have no installable environment specification. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/group_analysis.py` | The script fetches its atlas at runtime, requiring network access that the report does not state as a host requirement. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md` | The report lists package versions, but does not give install instructions or document the runtime network requirement. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment specification is included in the worker-stop workspace or its Git history. |
| must/014 | P.3 | unmet | judgement | `report.md` | No environment specification or update process is declared. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `report.md` | No exact environment lock or container pin is supplied. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config` | No worker-declared route shares a frozen environment specification. |
| must/017 | D.1 | unmet | judgement | `report.md` | No instructions explain how to obtain and install the analysis environment. |
| should/001 | T.2 | partial | judgement | `probe:tree-clean` | Git and annex cover the inputs, but the generated code, report, figures, and results were untracked at stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present` | No CI or repeated workflow-testing record is supplied; the report describes one analysis run. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `report.md` | Input, analysis, results, and figures have separate directories; no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-15/judgments/narps-neutral-r1-15-j02/attempt-01/judgment/2026-10-16-replay-record.json` | No worker record establishes a fresh-container or clean-machine test; replay prerequisites are not reconstructable as supplied. |
| should/005 | E.1 | unmet | judgement | `analysis/group_analysis.py` | The script runs in the caller environment and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked` | No frozen environment specification or reconstitution test is present. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-15/judgments/narps-neutral-r1-15-j02/attempt-01/judgment/2026-10-16-delivery-manifest-verification.json` | No environment artifacts or package lock are archived with the study. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment specification or tracked update process is declared. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the captured public participant derivatives and analysis dependencies are not identified as access-restricted. |
| may/001 | M.2 | partial | probe:subdatasets-resolvable+judgement | `analysis/group_analysis.py` | The Harvard-Oxford atlas is independently maintained and named in code, but its retrieval link and version are not pinned in the object. |
| may/002 | M.2 | partial | judgement | `report.md` | The report maps key inputs, script, and outputs, but does not document an environment module or composition diagram. |
| may/003 | M.2 | partial | judgement | `report.md` | Input, analysis, and output folders are separated, but no environment boundary or independent update instructions exist. |
| may/004 | M.2 | met | judgement | `analysis/group_analysis.py` | The analysis script composes participant maps and metadata into group results and figures. |
| may/005 | M.2 | met | judgement | `report.md` | The report links the main analysis, source methods, QC table, mask recipe, and output figures. |
## Flagged items

- **must/006:** The automated run-environment probe found no recognized run record; inspection of the full stop state established that no exact environment specification is supplied, so the item is unmet.
- **must/008:** The tracked-tree probe missed the untracked entry script; the complete report names that script, so the entry-point verdict is met.
- **should/002:** No CI was recognized; the complete delivery also contains no repeated workflow-testing record.
- **should/003:** The path probe missed the untracked analysis and result directories; inspection shows those folders, but no environment module.
- **should/006:** The environment-specification probe shows no specification to reconstitute; no testing setup or record is present.
- **should/008:** Duplicates must/014 by checklist design; both are answered from the same absence of a declared environment-update process.
- **may/001:** The submodule probe could not assess the independently maintained atlas data; code inspection found a runtime fetch but no pinned retrieval identity.

## Extra observation

The probe-only extras are clone-weight=met, inputs-untouched=not-applicable, and license-declared=unmet. These are outside the pinned 31-item checklist; the complete workspace contains no license file. No worker Git remote is configured, so there is no project issue-tracker route to inspect.

## Not checked

- **should/004:** No worker record establishes testing in a fresh container, batch job, VM, or cloud instance. A completed-run record tied to a clean environment would settle this.
- **Access:** No worker-declared authorized retrieval route exists in the stop state, so recipient access could not be tested. A route and a check from the intended recipient context would settle this.
- **Replay:** Not checked because the worker supplied no installable environment/setup route and the adapter cannot bound the atlas fetch to the retrieval limit. A worker-supplied, reconstructable environment and bounded atlas source would settle this.

## Goals and kind

The goal, from the supplied scientific task and report, is to assess the positive gain effect in vmPFC for the equal-indifference group from fixed participant maps, then provide the code, outputs, figures, uncertainty, and limitations. **Assumed kind: study** (not confirmed by a human). The assessment emphasizes result provenance and input/environment completeness for this study.

Checklist link: [2026-10-16-url.txt](2026-10-16-url.txt). Canonical response: [2026-10-16-response.json](2026-10-16-response.json). Probe receipt: [2026-10-16-probes.json](2026-10-16-probes.json). Delivery verification: [2026-10-16-delivery-manifest-verification.json](2026-10-16-delivery-manifest-verification.json). Access record: [2026-10-16-access-record.json](2026-10-16-access-record.json).

Produced by assess-alignment-with-stamped-principles 0.1.0 with stamped-conventions 0.1.0, checklist 0.3.1 (stamped-checklist-schema@v0.3.1, af259ba), on the captured NARPS study at worker-stop commit d857ab1302d13cb660a7a044af07141f44bfa9ba, 2026-10-16, Codex via frozen assessment runner / gpt-6-luna. Capture manifest SHA-256: f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9. Probe output: 2026-10-16-probes.json.

