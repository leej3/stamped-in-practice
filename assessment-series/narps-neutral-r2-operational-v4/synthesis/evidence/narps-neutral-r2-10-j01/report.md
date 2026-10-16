# Independent assessment — NARPS potential gain and vmPFC

**Capture:** `385fba6acdfe780cb3054269259f625ee5fd7bec671e5103a75609ca48607f2a` (canonical original; HEAD `8c6a78dcf33d4e58f7f2b9e276b5c42bccb797fa`). Target paths below use `content/workspace/<path>` within this capture (so `report.md` denotes `content/workspace/report.md`); the canonical capture digest governs each path. Worker stop was complete with no capture errors or omissions. The assessment uses the unchanged operational copy; its workspace entries and file/link identities match the initial operational manifest. No differences were found in the three separately classified annex database files. Inspection-induced state is not worker evidence.

**Assumption — goals and kind:** This is a study analysis deliverable. Its goal is to evaluate the positive potential-gain effect in vmPFC for the 54-person equal-indifference group from fixed participant maps, and provide a concise report, figures, code and results. The coordinator supplied this goal; there was no human confirmation. The report and input task state the same analysis goal (`report.md` lines 1–16; `input/study-task.md` lines 3–17).

**Finding:** Scientific adequacy: **qualified**. The supplied analyses do not support a positive vmPFC response to increasing potential gain in this group. The reported vmPFC mean is −0.0143 with a 95% interval of −0.0439 to 0.0152 and one-sided p=.832; the 11 whole-brain Bonferroni-significant voxels are reported outside vmPFC. The report correctly treats this as lack of evidence for the predicted increase, not proof of a zero effect (`report.md` lines 5, 17–25; `results/summary.json`). The primary limitations are that the whole-brain mask comes from Nilearn’s MNI152 template release a, whereas the supplied effects are labeled MNI152NLin2009cAsym (release c), and the full-delivery replay comparison covered the JSON summary and two participant tables only; NIfTI maps and figures were not replay-compared. The mask-template version difference could affect boundary coverage and deserves a space-matched sensitivity check; it does not appear to undermine the independently specified vmPFC sphere result. The ROI mean is based on participant maps without participant variance maps, so equal-weight inference cannot reflect first-level precision. Whole-brain Bonferroni inference is one-sided and appropriately conservative for the positive hypothesis. The estimated coefficients are normalized gain-modulator effects, not BOLD change per currency unit; separate gain and loss models do not test a gain-versus-loss contrast (`input/upstream-methods.md` lines 3–15; `report.md` lines 11–13, 23–25). Nilearn documents its `load_mni152_brain_mask` template as asymmetrical ICBM152 2009 release a, while noting fMRIPrep’s default is release c ([Nilearn reference](https://nilearn.github.io/stable/modules/generated/nilearn.datasets.load_mni152_brain_mask.html)).

## STAMPED attainment

The complete stopped workspace includes the worker’s uncommitted and ignored files. The primary `codex/...` branch HEAD is the supplied input commit, so `analysis/`, `figures/`, `report.md` and `results/` appear untracked from that checkout. However, the retained Entire session log records a worker-session checkpoint branch, `entire/8c6a78d-e3b0c4`, at commit `4d1dbd1ca594fa4f88a37b6a909dae2fe3ed76ab`. Its tree includes the analysis, report, all result files and figures; SHA-256 comparisons confirm those bytes match the current workspace. The worker’s checkpoint earns Git versioning credit, while the primary branch remains input-only. The session log also records the documented script invocation and its result generation. The report lists software versions, but no exact environment lock is present, so the run is only partly linked to a reproducible environment. The worker stop state shows no publication route for the complete project. No coordinator preservation action is credited to the worker.

| Item | Verdict | Evidence and reason |
|---|---|---|
| must/001 | met | `input/`, `analysis/`, `results/`, `figures/`, and `report.md` are within the workspace root; complete capture contains 1,191 entries. |
| must/002 | met | The 54 maps are internal annex-backed links under `input/data/`; metadata and methods are under `input/`. No external pointer is needed to analyze the captured data. |
| must/003 | unmet | The script imports NumPy, SciPy, pandas, NiBabel, Nilearn and Matplotlib, but no environment spec or software module is delivered. |
| must/004 | met | Worker checkpoint branch `entire/8c6a78d-e3b0c4` at `4d1dbd1` tracks the analysis, report, figures and results; its artifact hashes match the stopped workspace. |
| must/005 | met | The 54 supplied maps are annex-backed; their content is present in the captured annex store. No large worker output is tracked. |
| must/006 | partial | The Entire session records the script invocation and generated outputs; the report lists package versions, but no exact frozen environment specification links the run to a reproducible environment. |
| must/007 | partial | `report.md` gives a usage command and lists packages/outputs, but no installation or environment retrieval instructions; its interpreter path is host-specific. |
| must/008 | met | `analysis/run_group_analysis.py` is a clear start point and `report.md` lines 41–47 document its command and outputs. |
| must/009 | partial | Script input/output paths are rooted relative to `__file__`, but the documented execution command hardcodes a `/Users/johnlee/...` interpreter (`report.md` line 44). |
| must/010 | unmet | No dependency/environment specification is delivered; listing package names and versions in the report is not an installable environment. |
| must/011 | unmet | The documented route assumes a host-local interpreter path and provides no host/system requirements. |
| must/012 | partial | The report names Python and package versions, but omits an installable dependency list and host/system requirements. |
| must/013 | unmet | No environment specification is included in the captured Git state or complete workspace. |
| must/014 | unmet | No runnable environment-update process is documented. |
| must/015 | unmet | No frozen environment specification or lock is supplied. |
| must/016 | unmet | No worker-published project/environment route is recorded. Source URLs cover inputs, not the code, results or environment. |
| must/017 | unmet | No instructions explain how to obtain/recreate the environment; the only command refers to a user-specific external path. |
| should/001 | met | Git is the common repository; the worker’s Entire checkpoint commit includes code, report, figures, results and annex pointers. |
| should/002 | not-checked | Probe found no CI; no equivalent regular-test record was established. A worker test/run history would settle this. |
| should/003 | partial | Input, analysis, results and figures have distinct directories, but no environment component is present and boundaries are not fully documented. |
| should/009 | not-applicable | N/A: no restricted data or software component is identified; the supplied inputs have public source URLs. |
| should/004 | unmet | The only recorded worker execution and the replay used the prepared host Python environment; no fresh container, batch job or clean VM was used. |
| should/005 | unmet | The documented command invokes a persistent host-local interpreter; no disposable environment is created. |
| should/006 | not-checked | No exact environment exists to reconstitute or test; no worker reconstitution record is supplied. |
| should/007 | unmet | No environment artifacts (lock, container or archived binaries) are delivered. |
| should/008 | unmet | No environment update process or tracked update instance exists; duplicate of must/014. |
| may/001 | partial | Source collection, cohort and methods are identified in `input/sources.json`, but the independent upstream dataset is copied into the workspace rather than represented as a separately retrievable module. |
| may/002 | partial | Directory separation is visible and the report names outputs, but it does not document component relationships or recomposition. |
| may/003 | partial | The script separates input reads from output writes, but no module contracts or independent-update checks are documented. |
| may/004 | partial | One script composes the analysis, but there is no documented composition mechanism for independent modules. |
| may/005 | partial | The report points to the script, result files and figures, but the absolute interpreter path limits navigation into a working execution. |

**Checklist summary:** 5/17 MUST met, 4 partial, 8 unmet; 4/9 SHOULD unmet, 1 partial, 1 met, 2 not-checked and 1 not-applicable; all 5 MAY items partial. Partial does not satisfy a MUST. This is an item-by-item report, not an overall score.

## Probe interpretation and flags

The frozen probes were run against the operational workspace after the mandatory runner check. I overrode the tracked-only `derived-have-records` probe for must/006 because scientific results are present in the complete delivery and an Entire session log records their execution; absence of a derivative on the primary branch is not N/A. I also corrected `tree-clean` for must/004 because the worker checkpoint branch tracks the delivered analysis artifacts, and corrected the entrypoint and absolute-path findings using `report.md` and the code. `must/004` is met from the worker-created checkpoint branch even though the primary checkout is dirty. `must/006` is partial because the execution is recorded but its exact environment is not pinned. `must/007` is partial because the report contains usage but not environment installation; `must/008` is met because the script is a real start point. `must/009` is partial because the full stopped delivery’s documented command contains a host path, missed by the tracked-text scan. Probe outputs remain unedited in `2026-10-16-probes.json`; item reasons and flags are in the response.

The response marks `must/014` and `should/008` as an upstream duplicate, as both ask the same environment-update question. No overall score is calculated.

## Retrieval/access record

Intended recipient: a researcher authorized to retrieve the public NARPS source materials. The worker-declared route in `input/sources.json` is the NeuroVault collection and per-map URLs, plus pinned raw GitHub URLs for the cohort and methods metadata. From this assessment host, HTTP HEAD checks returned 200 for the collection, one sample map, and the pinned cohort table. This verifies those tested URLs on this host only; it does not test all 54 payload checksums or any other host. Required complete-project coverage would include source maps, code, report, results, figures and environment. The declared routes cover source materials only; no worker route for the complete project or environment was found. Coordinator delivery is not evidence of worker publication. Full details are in `access-record.json`.

## Replay record

**One replay attempt completed successfully** using the documented interpreter in a new writable copy of the canonical complete delivery. The exact worker command was run with no code or environment repair. `results/summary.json`, `results/participant_qc.tsv`, and `results/vmPFC_participant_values.tsv` were reproduced byte-for-byte. The two TSVs were configured for 1e-6 relative numeric tolerance; the JSON was byte-compared. The worker-listed Python and package versions matched in the supplied common environment. The helper initiated no prefetch; the script’s Nilearn template-loader calls were not byte-metered by the frozen adapter. NIfTI maps and figures were not selected, so replay equivalence for those outputs remains unavailable. The run is same-host evidence and does not demonstrate cross-host portability.

## Scope, integrity and provenance

The mandatory frozen assessor check passed before probe/response actions. Probe commands and outputs, access checks, the worker checkpoint comparison, the single replay, and the target integrity comparison are retained under this assessment directory. No Git/annex commands were run outside the operational copy. The initial operational manifest matches the canonical capture digest; all 1,100 workspace entries checked with no file, mode or link mismatch, no extra path, and no annex metadata difference. The worker-stop receipt is complete and has no capture omissions; supplied inputs are distinguished from the worker’s analysis artifacts, which are tracked on the worker checkpoint branch. Any coordinator-preserved copies or later commits are not credited as worker versioning or publication.

The probe found no Git remote; `input/sources.json` does declare public upstream URLs for the input data and metadata, which were checked only as described above. The link targets remain internal annex pointers. No external `.git` pointer was followed. Assistance exposure: the captured `.codex/` hooks and `.entire/` session metadata identify a Codex session (model `gpt-6-luna`) and a `jupyter-notebook` skill installation. This records agent/tool exposure only; I did not use that content as scientific or STAMPED grading evidence.

## Assessor record

Frozen assessment pin: see `assessment-version.json` outside the target. Checklist 0.3.1; assess-alignment-with-stamped-principles 0.1.0; stamped-conventions 0.1.0. Harness/model identifiers were not exposed by the runtime, so the machine-readable stamp records that limitation rather than guessing. No prior judgment, other worker output, or coordinator assignment record was used as grading evidence. A retained system skills directory is present in the capture; its content was not used as scientific or STAMPED evidence.
