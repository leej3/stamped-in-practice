# Independent assessment — NARPS Hypothesis 1

Assessment date: 2026-10-16 UTC. Object kind: **study** (assumed from `input/study-task.md`; no human confirmation was attached). Product: a group-level answer from 54 fixed participant gain-effect maps. The canonical delivery identity used throughout this report is the SHA-256 of its retained manifest: `21b5f53f9cbc01dce2bc961e06a436fa5fbeae8a6e8118d53866c2a0ccfb014d`. Capture-relative paths below are rooted at `content/workspace/`. The original captured HEAD is `c341bb810566ffec5a12747e921f38c28c618b4a`.

## Verdicts

MUST: **3 met / 2 partial / 11 unmet / 1 not-checked** (17 items). SHOULD: **0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable** (9 items). MAY: **2 met / 2 partial / 1 unmet** (5 items). These are item verdicts, not a composite score.

## What to address first

1. Commit the analysis script, report, figures, and result tables/maps as an attributable worker snapshot; this would make the delivered analysis state trackable (must/004; should/001).
2. Add a portable, frozen environment specification and instructions for obtaining it, including the template-data/network requirements; link the environment to the generated results (must/003, 006, 010, 013, 015, 017; should/006, 007).
3. Replace the machine-specific interpreter path with a root-relative documented invocation, and state host assumptions and installation steps (must/001, 007, 009, 011).
4. Declare how environment specifications are regenerated and track an update; the checklist repeats this item (must/014; should/008).
5. Publish a worker-declared authorized retrieval route that covers the complete study object, including inputs, code, report, results, and environment; no such route is present at worker stop (must/016).

## What is already strong

- The delivered input boundary is clear: `input/sources.json` identifies all 54 AO86 gain maps and their upstream collection; maps are present as annex-backed links under `input/data/`. The capture manifest retains payload identity, and the script uses the local input directory.
- The scientific method is inspectable in `scripts/group_analysis.py`: all 54 participant maps are checked for checksum, grid, and finite values; group inference is a one-sample positive-direction test with 9,999 participant sign flips and max-T familywise correction across a template brain mask.
- `output/report.md` explains the independent 10-mm vmPFC sphere, equal weighting, missing participant variance maps, arbitrary scale of the upstream normalized gain regressor, uncertainty, and the meaning of a null result. Figures, participant summaries, QC, and voxelwise maps are shipped.

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion is that the supplied analysis does not provide evidence for a positive gain effect in its vmPFC operationalization. It is supported by the reported whole-brain-corrected result: no vmPFC-sphere voxel survives positive one-sided max-T FWE, while the ROI mean is −0.010 model units (95% t interval −0.036 to 0.015; uncorrected descriptive one-sided p=.788; 27/54 participant ROI means positive). The ROI sphere is defined independently at MNI (4, 42, −8), radius 10 mm; it does not replace whole-brain correction. The 23 whole-brain corrected voxels are reported outside vmPFC and are not repurposed as support for the hypothesis. (Capture evidence: `content/workspace/output/report.md` SHA-256 `16a6b545838d376e1cac628bea3afce710ce2bf5b45e2e54f29ce5717998c71e`; `content/workspace/output/results/summary.json` SHA-256 `858c897f87e6c5064975a48663e8839367d3e94f3a28462723bc7c81c4e585e5`; `content/workspace/scripts/group_analysis.py` SHA-256 `a6e6dee319d4da34bedb13adcd4777c88e19af0afa80cadafe957203dcfa0ffe`.)

The analysis uses the intended complete cohort and equal participant weighting, checks image-grid compatibility and finite values, and corrects across the whole template brain mask. The sign-flip maximum-t procedure is a defensible group-level approach under the stated independent-participant and null-symmetry assumptions. The report properly limits inference because first-level variance maps are absent and the upstream gain regressor was variance-normalized: coefficients are not BOLD change per dollar. A nonsignificant ROI summary is correctly described as lack of support, not proof of a zero effect. QC and participant-level figures make the reported checks and uncertainty inspectable. These judgments assess the delivered scientific artifacts and reasoning, not whether a fresh replay succeeded.

**Reported hypothesis outcome (verbatim):** “The 54-participant group did **not** show evidence that potential gains produced a greater vmPFC response.” This is retained separately from the adequacy category.

## Delivery, worker attribution, and limits

The worker stop receipt (`worker-end-state.json`, SHA-256 `1ff473a16216ea3229d1001335f3f94204af1ca37678075671cf9787648b8b53`) records a completed stop. The canonical manifest identifies the complete workspace, including untracked `scripts/` and `output/`; at worker stop the tracked Git HEAD was `c341bb810566ffec5a12747e921f38c28c618b4a`, and the script and scientific deliverables were outside that commit. Thus the artifacts can be judged scientifically, but they do not establish worker version-control practice. The captured Git configuration has no remote. Later coordinator preservation or delivery to this assessor is not worker publication or access evidence.

Access assessment: intended recipient is a researcher using the worker-declared authorized route. No such route is declared for the complete study object. `sources.json` records upstream data provenance URLs, not a route for retrieving the worker's code, report, results, and environment together. No host route was available to test; the coordinator-provided assessment copy is excluded as evidence of worker access. Required coverage for a usable route is inputs, code, report, generated results, and environment. Anonymous access is not required.

Replay: **not checked; zero attempts.** The documented entrypoint is the absolute-path Python command in `output/report.md`, invoking `scripts/group_analysis.py`. Its prerequisite is an existing external “prepared” interpreter with named package versions, but the complete stopped delivery has no environment specification or reconstruction instructions. The external interpreter is outside the capture and cannot be used to reconstruct the environment. No replay copy was made and no shipped output is claimed as replay evidence. If the prerequisite were supplied, the explicit generated-output selection would be `output/results/{group_mean_effect.nii.gz,group_t_positive.nii.gz,group_p_fwe_positive.nii.gz,vmPFC_sphere_mask.nii.gz,image_qc.csv,vmPFC_participant_effects.csv,summary.json}` and `output/figures/{whole_brain_t_map.png,vmPFC_participant_estimates.png}`; inputs, participant metadata, and code would be protected. The declared comparison would inspect numeric map/table values at rtol `1e-6`, with images compared visually/scientifically and timestamps, logs, and presentation differences separated. Because the prerequisite cannot be established from worker-supplied declarations, no helper replay was launched.

Capture limitation: `judge-target.json` was not present beside the supplied canonical/operational manifests, so no `reference_limits` field was available. I did not follow original external targets or rely on an external `.git` pointer. The task launcher is responsible for exact before/after capture verification; no content mismatch was reported to this assessment. The coordinator manifest lists the retained complete workspace and its file/link hashes.

Assistance exposure: the captured `.entire` session material at `content/workspace/.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl` (SHA-256 `83cffc2f028734d767175e6c3f8694da32a4a3a86ed7f6943c472474116b2f34`) includes assistant-originated content. This exposure is recorded only; it was not used as evidence for any checklist verdict or scientific judgment.

## Per-item response

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | unmet | judgement | `content/workspace/output/report.md` | The documented interpreter is outside the captured root; the full reproducibility boundary is not self-contained. |
| must/002 | S.1 | met | judgement | `content/workspace/input/sources.json` | All 54 input maps are included as annex-backed links under input/ and the script resolves them relative to the root. |
| must/003 | S.1 | unmet | judgement | `content/workspace/output/report.md` | Scientific Python packages are named but no environment file or linked software module installs them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `content/workspace/scripts/group_analysis.py` | At worker stop, the analysis script and scientific report/results were untracked in the Git workspace. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `content/workspace/input/data/` | All 54 supplied participant maps use git-annex content links; the capture retains their payloads. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/output/report.md` | The report names package versions but gives no exact captured environment or run record linking these outputs to it. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/output/report.md` | The report gives a run command and usage context, but no installation instructions or reproducible environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/output/report.md` | The report identifies scripts/group_analysis.py as the executable analysis entry point and describes its generated results. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `content/workspace/output/report.md` | The documented invocation hard-codes a machine-specific absolute interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/scripts/group_analysis.py` | The script imports NumPy, SciPy, pandas, NiBabel, Nilearn and Matplotlib, but no delivered environment declares or installs them. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/output/report.md` | The route assumes a host-specific interpreter and template downloads, without documenting OS, network or system-library requirements. |
| must/012 | P.2 | partial | probe:platform-assumptions+judgement | `content/workspace/output/report.md` | The report lists direct package versions, but omits host, network and system-library requirements and supplies no installable declaration. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/` | No environment specification is included alongside the code and data. |
| must/014 | P.3 | unmet | judgement | `content/workspace/` | No declared process for updating or tracking environment specifications exists because none is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/output/report.md` | Package versions in prose are not a frozen, retrievable environment specification. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config` | No worker-declared route publishes an environment specification or the stopped research object. |
| must/017 | D.1 | unmet | judgement | `content/workspace/output/report.md` | The report says to use a prepared environment but does not explain how to obtain it. |
| should/001 | T.2 | partial | judgement | `content/workspace/.git/HEAD` | Inputs are versioned with Git and annex; the worker script and analysis outputs were not committed or otherwise versioned. |
| should/002 | A.2 | not-checked | probe:ci-present | `content/workspace/output/report.md` | No evidence establishes repeated workflow testing; a run history or CI record would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input/; content/workspace/scripts/; content/workspace/output/` | input/, scripts/ and output/ are separated; no independent environment module is present. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/output/report.md` | No fresh-environment test is evidenced; a successful isolated run with captured dependencies would settle this. |
| should/005 | E.1 | unmet | judgement | `content/workspace/output/report.md` | The documented command invokes an existing prepared environment and creates no disposable environment per run. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `content/workspace/` | No frozen environment specification or reconstitution test is supplied. |
| should/007 | D.2 | unmet | judgement | `content/workspace/` | No environment artifact is archived in the research object. |
| should/008 | D.2 | unmet | judgement | `content/workspace/` | No environment specification update process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: no restricted data or software is identified in the delivered study. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json` | The upstream AO86 input collection is identified and retrievable in sources.json, with all selected maps included under input/. |
| may/002 | M.2 | partial | judgement | `content/workspace/output/report.md` | The input, code and results directories are evident, but no module map explains their boundaries or recombination. |
| may/003 | M.2 | partial | judgement | `content/workspace/scripts/group_analysis.py` | Input, code and outputs have separate directories, but the script binds them to one fixed layout and no environment boundary exists. |
| may/004 | M.2 | unmet | judgement | `content/workspace/scripts/group_analysis.py` | There is one direct script invocation, not a mechanism for composing independently versioned modules. |
| may/005 | M.2 | met | judgement | `content/workspace/output/report.md` | The report links the script, summary, participant table and figures, making the delivered layout navigable. |

## Probe overrides and flagged items

- **must/006, 007, 008, 009, 011, 012, 015; should/003, 006; may/001:** Probe findings were reconciled with the complete stopped delivery. The probe reads tracked paths; the documented entrypoint and delivered untracked script/report change the answers for 007/008, while the documented absolute interpreter changes must/009. `should/003` reflects the actual `input/`, `scripts/`, and `output/` layout. `may/001` uses the identified and included upstream data component.
- **must/014 and should/008:** `upstream-duplicate` records the checklist's repeated environment-update question.

- **should/002:** no evidence of recurring workflow tests; a CI or repeated-run history would settle this.
- **should/004:** no fresh-environment test was completed; a safe replay with a supplied environment would settle this.
- **Scientific replay:** prerequisite not supplied, as detailed above. The 7,200-second limit and rtol `1e-6` remain the frozen scope for any eligible attempt.

## Goals, kind, checklist, and provenance

The goal, taken from `input/study-task.md`, is a group-stage test of whether increasing potential monetary gain increases vmPFC response in the equal-indifference NARPS group. This is a **study** because its product is a scientific answer from supplied inputs and computation. The assumption was not confirmed by a human.

The [filled STAMPED checklist](checklist-url.txt) opens the 0.3.1 checklist. Machine response: [response.json](response.json). Probe record: [probes.json](probes.json). Access record: [access-record.json](access-record.json). Replay record: [replay-record.json](replay-record.json). Scientific judgment record: [scientific-judgment.json](scientific-judgment.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on the complete study delivery. Canonical capture manifest: `canonical/manifest.json`, SHA-256 `21b5f53f9cbc01dce2bc961e06a436fa5fbeae8a6e8118d53866c2a0ccfb014d`; captured HEAD `c341bb810566ffec5a12747e921f38c28c618b4a`; assessor `Codex` / `GPT-6 (variant unavailable)`, 2026-10-16. Probe output: [probes.json](probes.json).
