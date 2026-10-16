# Independent assessment: NARPS potential gain and vmPFC

## Evidence identity and scope

The canonical original delivery capture is SHA-256 `8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb`; the captured HEAD is `bfe069501c140673f38778116f34bc8a5c36366f`. Unless otherwise noted, artifact citations use capture-relative paths under `content/workspace/`. The worker stop receipt is SHA-256 `d99f296419a1ebc7f2467baf3d086d16ab0bce2f376fbee8179aae4feec1eded`. The delivery is complete and has no capture omissions. The operational manifest matched the canonical digest at assessment start. Operational-copy Git/probe observations are identified as such; the replay used a separate copy of the canonical complete delivery.

The documented goal is a group-level analysis of the supplied 54 equal-indifference participant gain-effect maps, with whole-brain-corrected inference and an anatomically justified vmPFC interpretation (`input/study-task.md`, SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`). Assumption, not confirmed by a human: this is a **study**, with the scientific conclusion as its product.

## STAMPED verdicts

**MUST:** 3 met / 5 partial / 9 unmet / 0 not-checked (17 items). **SHOULD:** 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 items). **MAY:** 0 met / 2 partial / 2 unmet / 0 not-checked / 1 not-applicable (5 items). No overall score is assigned.

### What to address first

1. Track the analysis script, report, results, and a run record together at worker stop. They are in the complete capture but were outside the captured HEAD; without them Git did not identify the submitted scientific state (`code/analyze.py`, `report.md`, `results/`; operational-copy `probes.json#tree-clean`). This closes the key T.1/T.3/T.5 gap (must/004).
2. Include a pinned dependency/environment specification and link it from result provenance. The recorded command relies on a pre-existing absolute-path environment and result records do not identify it (must/003, 006, 010, 013, 015–017; should/006–007).
3. Replace the host-specific interpreter path with an obtainable, documented invocation and record required host assumptions (must/001, 009, 011–012, 017).
4. Declare and test a retrieval route for the complete research object. The captured source URLs cover input data and cohort metadata only; the worker stop state has no project remote or environment publication route (must/016; access record).

### What is already strong

- The 54 maps and metadata are under one project root, with large map payloads represented by annex-backed links; the worker code checks source checksums and common image geometry (`input/sources.json`, SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`; `code/analyze.py`, SHA-256 `6c853f514b8fff58123d317c95da4249248601e6c61082987f2750dade1212ff`).
- The report states a runnable group-analysis entrypoint, explains the one-sided whole-brain max-T procedure, and limits interpretation of normalized cope estimates and absent participant variance maps (`report.md`, SHA-256 `e1545efc76abf52ce79d0b979b9cc87db697efe6afda651426b827677d4832b7`; `input/upstream-methods.md`, SHA-256 `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`).
- The supplied inputs, analysis code, figures, tables, and JSON summary were all retained in the stopped delivery. A single bounded fresh-copy replay reproduced all 11 selected generated outputs byte-for-byte (`replay-record.json`). This is assessor-side repeatability evidence, not worker-side versioning or environment capture.

## Scientific assessment

**Scientific adequacy: supported.** Conditional on the supplied first-level maps and the stated symmetric-error assumption for sign flipping, the analysis supports the reported conclusion of no whole-brain-corrected positive vmPFC effect. It uses all 54 independent participant maps, checks checksums and shared image geometry, and defines the analysis domain by finite nonzero coverage in every map. A one-sided participant-level sign-flip max-T test controls whole-brain family-wise error over that common-coverage domain. The vmPFC sphere is independently located from a cited subjective-value meta-analysis and is used descriptively alongside whole-brain-corrected voxel inference. The supplied summary reports no corrected voxels in the sphere, a descriptive sphere mean of −0.014 cope units (95% participant-level t interval −0.044 to 0.015), and whole-brain adjusted minimum p of 1.00 in the sphere (`code/analyze.py`; `results/results.json`, SHA-256 `45d5e17c1132085564b583c2bb10fd61be0f41134f3aedc4258c5e3be110c54f`; `results/p_fwe_maxT.nii.gz`).

The direction and multiplicity handling fit the supplied task. The strict intersection is conservative at coverage boundaries; it avoids treating padded zeros as measured effects, though no external anatomical mask is used. The null result is not evidence that the effect is exactly zero. The report correctly limits the inference to these gain ranges and fixed upstream model. The cope coefficients reflect a mean-centered, variance-normalized gain regressor, not BOLD change per currency unit; absent first-level variance maps preclude precision-weighted inference, and the ROI interval covers between-participant variability rather than first-level uncertainty (`input/upstream-methods.md`; `report.md`). Small effects remain uncertain. The positive corrected posterior clusters reported outside vmPFC do not support the target hypothesis (`results/results.json`; `results/top_voxels.csv`, SHA-256 `661b9982bec8f2fb0d20229ffb8f5a6525c7c245111b012f3c7ee52aab1e6f57`).

**Hypothesis conclusion (verbatim statement):** We therefore find no corrected support for a positive vmPFC gain effect in this group.

This is the reported outcome, separate from the adequacy category above. The scientific category and its artifact reasoning are also recorded in `scientific-judgment.json`.

## Worker state, tracking, and availability

At worker stop, Git HEAD was the original captured commit, while `code/`, `report.md`, and `results/` were untracked in the operational copy; the complete capture and stop receipt confirm these are part of the delivered workspace, not a HEAD-only reconstruction. The operational-copy `git status`/probe is an observation of the verified copy, not evidence generated by the worker. Later coordinator capture, preservation, or delivery does not earn worker versioning or publication credit. The worker-side Git config has no remote URL; the coordinator-provided copy is not proof the worker had published it.

**Recipient and route:** the intended recipient is a researcher using the worker-declared authorized route; anonymous access is not required. `input/sources.json` declares NeuroVault map/collection URLs and a pinned GitHub cohort-table URL. From the assessment host, HTTP HEAD checks on the collection, one representative map, and the pinned cohort table returned 200. These routes cover source maps and cohort metadata only. They do not retrieve `code/analyze.py`, the report, generated results, or the Python environment. No complete-project Git or annex route was declared or found in the captured worker config. See `access-record.json` for exact route, coverage, and host scope.

**Replay:** before execution, `replay-plan.md` records the exact worker-documented command, prerequisites, 11 explicit generated outputs, comparison rule, and tolerances. The frozen helper copied the canonical complete delivery to `replay-work/`, removed only those selected output files in the replay copy, used the worker-documented external interpreter, and performed no input prefetch. It completed in 21.97 seconds with return code 0; all selected NIfTI maps, figures, JSON, and CSV outputs were byte-identical. The comparison therefore exceeded the planned CSV relative tolerance of 1e-6 without needing it. This does not supply the missing environment specification or establish worker-side environment practices. The exact command result and logs are retained in `replay-record.json`, `replay-helper.stdout`, `replay-helper.stderr`, `replay-work/replay.stdout`, and `replay-work/replay.stderr`.

**Exposure note:** a coordinator procedure output exposed assignment-related metadata during setup. I did not use it as grading evidence and do not infer or report any treatment assignment.

## Per-item table
| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md`, `input/sources.json` | Core inputs, code and products share the workspace root, but the documented interpreter lives outside it and its environment is not captured. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | All 54 maps and metadata are reachable under the root through relative links into the retained annex object store. |
| must/003 | S.1 | unmet | judgement | `report.md`, `code/analyze.py` | The documented runtime relies on external Python packages; no environment spec or linked software module supplies them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `.git/index`, `code/analyze.py` | Git tracks the input baseline, but the submitted analysis code, report and results remained uncommitted at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json`, `probes.json#large-in-annex` | The 54 large participant maps use git-annex pointers with payloads retained in the captured object store. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/results.json`, `results/run.log`, `results/gain_effect_group_analysis.ipynb` | Shipped results identify the test and inputs but do not record the exact software environment that produced them. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md` | The report gives a usage command but no installation instructions for its external prepared environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `code/analyze.py` | The report identifies code/analyze.py as the starting point and supplies a runnable command. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `code/analyze.py`, `report.md` | The script uses paths relative to its own location, but the documented command hardcodes a host-specific absolute interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `code/analyze.py`, `.` | No dependency declaration includes the script's scientific Python packages; replay depended on the host's preinstalled environment. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md`, `.git/config` | The command discloses two thread variables and an absolute interpreter path, but does not document the required host or system setup. |
| must/012 | P.2 | unmet | judgement | `report.md`, `code/analyze.py` | There is no reader-facing list of software and system requirements; the report only points to a prepared host environment. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `.` | No environment specification is included alongside the code and data in the captured workspace. |
| must/014 | P.3 | unmet | probe:env-spec-tracked+judgement | `.` | No process for updating and tracking dependency specifications is documented because no specification is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/results.json`, `report.md` | There is no pinned environment specification linked to these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `report.md`, `.git/config` | No environment specification is included or shared; the worker record has no project remote, and input URLs cover data only. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report gives an absolute runtime path but no instructions to obtain the environment specification or recreate it. |
| should/001 | T.2 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `.git/config` | One Git repository covers the project root, with git-annex handling the large input maps. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `report.md`, `results/gain_effect_group_analysis.ipynb` | No CI configuration or repeated worker-side test history is captured; a coordinator replay cannot establish regular worker testing. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/sources.json`, `code/analyze.py`, `report.md` | Inputs, analysis code and results occupy distinct directories; there is no separate environment module. |
| should/004 | E.1 | not-checked | judgement | `results/gain_effect_group_analysis.ipynb`, `report.md` | Worker-stop evidence shows no fresh-environment run record; the successful replay is assessor-side, so it cannot establish worker practice. |
| should/005 | E.1 | unmet | judgement | `report.md` | The documented entrypoint reuses a long-lived external environment; no disposable environment is created per execution. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `results/results.json`, `.` | No exact environment specification exists to reconstitute and test against the shipped results. |
| should/007 | D.2 | unmet | judgement | `.`, `report.md` | The project does not archive the external Python environment or another environment artifact. |
| should/008 | D.2 | unmet | judgement | `.` | No update process or dependency specification is documented. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the captured object contains public inputs and software dependencies, with no restricted component to isolate. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json` | N/A: the 54 source maps are included in the annex store; no independently maintained project component is external to the object. |
| may/002 | M.2 | partial | judgement | `report.md` | The report names input, code and result paths, but does not explain module boundaries or recombination. |
| may/003 | M.2 | unmet | judgement | `code/analyze.py` | The directory layout is clear, but no independently updateable module interfaces or boundary rules are defined. |
| may/004 | M.2 | unmet | judgement | `code/analyze.py` | No module composition mechanism is documented; one script directly couples inputs and results. |
| may/005 | M.2 | partial | judgement | `report.md` | The report gives a useful file map, but there is no module overview explaining how components relate. |

## Flagged items

- **must/004 (`probe-overridden`):** the tree-clean probe reports uncommitted paths, while the item asks whether version control is used. Git/annex is present for the input baseline, so the answer is partial because the submitted code and results are outside HEAD.
- **must/006 (`probe-overridden`, `mapping-questioned`):** the probe did not recognize the untracked outputs; the complete capture contains results, but their records omit the exact runtime identity.
- **must/007 (`probe-overridden`):** the filename probe missed the equivalent report, which documents usage; installation of its external environment remains undocumented, so the answer is partial.
- **must/008 (`probe-overridden`):** the filename probe missed the report's documented `code/analyze.py` starting point.
- **must/009 (`probe-overridden`):** the probe scanned tracked text only; the full report documents a host-specific absolute interpreter path, although code I/O paths are relative.
- **should/003 (`mapping-questioned`):** the probe saw only tracked inputs; the full delivery separates input, code, and result directories, but has no environment module.
- **must/014 and should/008 (`upstream-duplicate`):** the checklist repeats the same environment-update question in both items.

## Not checked

- **should/002:** no worker-side recurring test record is in the stop-state capture. A documented CI history or repeated test log would settle regular testing; the assessor replay does not count as worker practice.
- **should/004:** no worker-side clean-environment run is recorded. A worker run from a fresh container, VM, batch job, or cloud instance with retained results would settle it; the assessor replay does not count as worker practice.

## Additional finding outside the 31-item checklist

The complete captured workspace has no licence or reuse statement. This is reported as an unscored extra finding; the frozen checklist has no licence item. The scripted `license-declared` probe also reported absence.

## Scientific judgment and attribution limits

The scientific adequacy label is **supported** for the specific reported conclusion, not for a claim that vmPFC has no gain response. The result is conditional on the supplied cope maps, strict common-coverage mask, and symmetric sign-flip null; it does not estimate response per currency unit or account for unavailable first-level variance maps. Hypothesis outcome and adequacy are stored separately.

The assessment inventory identifies worker supplied inputs and the worker's stopped workspace. Initial coordinator guidance and the native profile skill directory are supplied resources; they do not establish worker environment practice. Later coordinator preservation and this assessment's replay are excluded from worker credit. One coordinator procedure output exposed assignment-related metadata during setup; it was not used as grading evidence, and no assignment is inferred or disclosed.

## Checklist link and provenance stamp

[Open the filled checklist](checklist-url.txt). The canonical machine-readable assessment is [response.json](response.json); probe results are [probes.json](probes.json), the captured-delivery replay record is [replay-record.json](replay-record.json), and the detailed route test is [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on canonical capture SHA-256 `8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb`, original HEAD `bfe069501c140673f38778116f34bc8a5c36366f`, 2026-10-16, Codex (API) / GPT-6 (exact runtime variant unavailable). Probe output: `probes.json`.

## Post-assessment integrity check

A byte/mode/path comparison against the canonical manifest found no mismatch outside the separately classified operational metadata. The regular-file `.git/annex/keysdb/db` changed; it is treated as inspection-time operational metadata and is not worker evidence. This comparison does not establish logical database equivalence. The check output and script are retained as `integrity-check.stdout`, `integrity-check.stderr`, and `integrity-check.py`.
