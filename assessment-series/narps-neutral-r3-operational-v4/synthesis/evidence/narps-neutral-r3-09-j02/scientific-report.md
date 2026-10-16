# Independent assessment: NARPS equal-indifference gain analysis

## Verdict

**MUST:** 10 met / 3 partial / 4 unmet / 0 not-checked (17). **SHOULD:** 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable (9). **MAY:** 2 met / 1 partial / 1 unmet / 0 not-checked / 1 not-applicable (5). A partial does not satisfy a MUST. These are item counts, not an overall score.

## What to fix first

1. Track the worker's report, analysis scripts, requirements file and results in the repository. At stop, these five deliverable paths were untracked; the only commit contains supplied inputs. This closes the versioning gap (must/004, should/001).
2. Add a complete locked environment identity and link it from the result record; document how to update it and track those updates. Direct requirements pins and recorded package versions help, but do not identify the full resolved environment (must/006, must/013–015, should/006–008).
3. Publish a researcher-authorized route that covers the maps, metadata, analysis, environment, results, figures and report. No worker route or Git remote was captured (must/016).
4. Keep the current separation of `input/`, `analysis/`, `results/` and `figures/`, and clarify which are independently updateable components. The layout is useful, but it is one fixed script rather than independently maintained modules (should/003, may/002–004).

## What is already strong

- The analysis matches 54 participant maps to metadata, checks input hashes and image geometry, and excludes no participants. Its protocol states the estimand and the limits of the supplied first-level estimates (`content/workspace/analysis/run_group.py#L21-L58`; `content/workspace/analysis/protocol.md#L4-L7`).
- The primary test is a positive one-sample group test with 5,000 participant sign flips and whole-brain max-t FWE correction. The script and protocol expose the null assumptions, seed, support mask and vmPFC localization (`analysis/protocol.md#L9-L13`; `analysis/run_group.py#L69-L80`).
- The report distinguishes a lack of corrected vmPFC support from evidence of no effect, and the shipped independent check agrees with the ROI summary, corrected map maximum, threshold and significant voxel count (`REPORT.md#L27-L33`; `results/independent_validation.json`).

## Evidence boundary and attribution

All target citations below refer to the **canonical original capture, SHA-256 `794cdbd43e94970c2643887f261be89131d348e93c742f67f737491d9e2abfc1`**, and give capture-relative paths under `content/workspace/`. The full capture completed without manifest errors or omissions at `2026-10-16T16:55:12.565633Z`. Its original captured HEAD is `82443e43a1171f47c085c5e0fadc9e8132a12053`.

The worker stop receipt (`/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-09-j02/attempt-01/worker-end-state.json`, SHA-256 `304303180d8b2361a1e12a948d9102c1139ec9ab1d6386445f143a44f5988e7e`) records a successful exit and complete capture. At worker stop, that commit's only changes are the supplied maps and input metadata. The worker's report, code, figures, requirements and results are present in the capture but untracked. I therefore do not credit the supplied commit's annex arrangement as a worker action, nor count coordinator preservation as publication or worker versioning. The commit message includes a Codex co-author identifier; I record that as visible assistance exposure and did not use it to judge the scientific work.

The frozen runner and read-only Git inspection changed the operational copy's regular `.git/annex/keysdb/db` bytes (initial SHA-256 `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca`, current SHA-256 `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`); the allowed `db-shm` and `db-wal` files did not change. The complete operational comparison found no other differences from its initial manifest. This is inspection-induced operational metadata, not worker evidence; no claim of logical database equivalence is made. The runner verified the canonical capture before and after its replay action.

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion follows from the supplied group analysis: the one-sided whole-brain max-t test found 24 corrected voxels in three posterior occipital clusters (maximum t=6.62, pFWE=.0010; threshold=5.40), with none in the stated vmPFC envelope. The vmPFC mean is 0.0012 and its 95% interval [−0.0138, 0.0162] spans zero. The report does not claim equivalence.

**Reported hypothesis outcome (verbatim):** In the 54-person NARPS equal-indifference group, the supplied gain-effect estimates do **not support a positive vmPFC response to increasing potential gain** under whole-brain family-wise error correction.

The model uses participant effect estimates as independent observations and does not mistake outside-brain zero padding for measured zero: the primary test is over 198,029 voxels with finite, nonzero estimates in all participants. The MNI coordinate envelope is broad and explicitly approximate; the whole-brain correction, rather than an ROI-only test, determines support. The 5,000 sign flips assume independent participants and a symmetric null. The report gives the permutation resolution, effect interval and non-equivalence limitation. The independent validation recomputes the ROI summary and checks the reported max-t map, threshold and count.

The conclusion is conditional on the supplied AO86 estimates and upstream model. The supplied material lacks participant variance maps and the executable upstream pipeline, so first-level uncertainty, preprocessing and individual modeling cannot be re-evaluated. The common support is based on nonzero finite coverage rather than an independent anatomical mask, and the coordinate box does not resolve vmPFC subregions. The gain regressor was normalized upstream; these estimates are not BOLD change per monetary unit. The task states that the potential gain range was twice the loss range, but that does not imply a monetary-unit slope or a gain-versus-loss comparison under this model. These limitations do not invalidate the narrower conclusion of no corrected vmPFC support in these supplied estimates.

Key scientific evidence: `REPORT.md#L5-L17`, `REPORT.md#L27-L33`, `analysis/protocol.md#L4-L16`, `input/upstream-methods.md#L1-L17`, `results/group_results.json`, `results/independent_validation.json`, and the delivered figures `figures/whole_brain_fwe.png`, `figures/vmPFC_participant_estimates.png`, `figures/coverage_qc.png` (all under the canonical capture identity above).

## Replay and access

The predeclared replay plan is in [`2026-10-16-replay-plan.md`](2026-10-16-replay-plan.md). The single frozen-runner attempt used the documented install prerequisite and confirmatory command on a separate writable copy of the complete canonical delivery, with inputs and code protected. It selected the participant QC table and the group-t and corrected-p maps. The attempt stopped in `python -m pip install` because the frozen assessment runtime has no `pip` (`No module named pip`); the scientific entrypoint never started. The runner's retained record labels the command failure `unmet`, but this is an **assessor-runtime malfunction**, not target behavior. Fresh replay remains not checked; I did not retry or substitute another environment. See [`fresh-rerun.json`](fresh-rerun.json), `replay/workdir/replay.stderr` and `inspection-replay-stderr.txt`.

The intended recipient is a researcher using the worker-declared authorized route. No such route was recorded, the worker Git remote list is empty, and the report has no retrieval instructions. Therefore no route could be tested from this host and no artifact coverage is established. Coordinator delivery to the assessor is not worker access evidence. The separate [`access-record.json`](access-record.json) records recipient, route, required coverage and tested host scope.

## Per-item checklist

The response below uses the pinned STAMPED checklist 0.3.1. Evidence citations in the machine-readable response include the canonical capture SHA-256 and capture-relative path.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/analysis/README.md#L3-L11` | All inputs, analysis code, environment file, results and figures are nested in one workspace root. |
| must/002 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The 54 maps and metadata are under input/; each map resolves through the captured annex object within the same workspace. |
| must/003 | S.1 | met | judgement | `content/workspace/requirements.txt`, `content/workspace/analysis/README.md#L3-L8` | The Python analysis dependencies are declared in requirements.txt and the documented route installs that file. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `content/workspace/REPORT.md`, `content/workspace/analysis/run_group.py`, `probe:tree-clean` | Git tracks supplied inputs, but the worker's report, code, requirements and results are untracked at stop. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/results/group_t.nii.gz` | Large supplied maps use annex pointers; worker-generated NIfTI results are untracked, and the input annex commit is coordinator-supplied. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `content/workspace/results/group_results.json`, `content/workspace/requirements.txt` | Results record package/runtime versions and parameters, but no exact environment spec identity is linked to the run. |
| must/007 | A.1 | met | probe:entry-point+judgement | `content/workspace/analysis/README.md#L1-L11` | analysis/README.md gives Python setup and the run commands; the probe missed this nested README. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/analysis/run_group.py#L88-L108` | analysis/run_group.py is the documented starting script for pilot and confirmatory group inference. |
| must/009 | P.1 | met | judgement | `content/workspace/analysis/run_group.py#L14-L17` | The delivered scripts resolve inputs and outputs relative to their own project root. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `content/workspace/requirements.txt`, `content/workspace/REPORT.md#L37-L43` | requirements.txt covers the third-party imports, including nibabel, nilearn and scientific/plotting libraries. |
| must/011 | P.1 | met | judgement | `content/workspace/analysis/README.md#L3-L8`, `content/workspace/analysis/run_group.py#L14-L17` | The route documents Python 3.13; the code declares no other host, scheduler, mount, hardware or service assumption. |
| must/012 | P.2 | met | judgement | `content/workspace/analysis/README.md#L3-L8`, `content/workspace/requirements.txt` | The instructions name Python 3.13 and requirements.txt lists the direct package dependencies. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `content/workspace/requirements.txt`, `probe:tree-clean` | requirements.txt is present in the stop capture but was untracked, so the environment specification is not in version control. |
| must/014 | P.3 | unmet | judgement | `content/workspace/requirements.txt`, `content/workspace/analysis/README.md#L3-L8` | The delivered docs pin dependencies but give no process or command for updating the specification. |
| must/015 | D.1 | unmet | judgement | `content/workspace/requirements.txt`, `content/workspace/results/group_results.json` | Direct requirements pins and reported package versions omit a complete transitive lock or environment digest for exact recreation. |
| must/016 | D.1 | unmet | judgement | `content/workspace/.git/config`, `content/workspace/REPORT.md#L35-L48` | No worker-declared route or remote publishes the complete study and environment for an authorized researcher. |
| must/017 | D.1 | met | judgement | `content/workspace/analysis/README.md#L3-L11` | The analysis README explains Python setup, dependency installation and the run commands. |
| should/001 | T.2 | partial | judgement | `content/workspace/input/sources.json`, `probe:tree-clean` | Git/annex covers supplied inputs, while worker-authored code, report, environment file and outputs remain untracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `content/workspace/results/independent_validation.json`, `probe:ci-present` | A validation result is shipped, but the capture does not establish regular workflow testing; recurring run records would settle it. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/analysis/README.md#L3-L11`, `content/workspace/analysis/run_group.py#L14-L17` | Inputs, analysis, results and figures are separated by directory, but not independent modules with separate update boundaries. |
| should/004 | E.1 | not-checked | judgement | `fresh-rerun.json`, `replay/workdir/replay.stderr` | The only replay stopped before analysis because the frozen runtime lacks pip; a fresh-environment result is unavailable. |
| should/005 | E.1 | unmet | judgement | `content/workspace/analysis/README.md#L3-L8` | The documented workflow installs into the active Python environment and does not create a disposable environment per run. |
| should/006 | D.2 | not-checked | judgement | `content/workspace/requirements.txt`, `replay/workdir/replay.stderr` | No environment reconstitution history is captured; the failed replay never reached the supplied setup route. |
| should/007 | D.2 | unmet | judgement | `content/workspace/requirements.txt` | The project supplies a text requirements file, but no archived Python environment, package binaries or container image. |
| should/008 | D.2 | unmet | judgement | `content/workspace/requirements.txt` | No dependency-update process is documented or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/upstream-methods.md#L3-L4` | N/A: no restricted data or software component is identified in the delivered study; the source maps are the public NARPS cohort. |
| may/001 | M.2 | not-applicable | judgement | `content/workspace/analysis/README.md#L3-L11` | N/A: no independently maintained project components; maps, code and results are within one workspace, while Python packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `content/workspace/REPORT.md#L35-L48`, `content/workspace/analysis/README.md#L3-L11` | The report and analysis README explain the inputs, scripts, result directories and how to run the analysis from the root. |
| may/003 | M.2 | partial | judgement | `content/workspace/analysis/run_group.py#L14-L17`, `content/workspace/analysis/README.md#L11` | Directory boundaries aid updates, but code and outputs are fixed to one script and are not independently maintained components. |
| may/004 | M.2 | unmet | judgement | `content/workspace/analysis/run_group.py#L14-L17` | The directories are joined by one script; no module composition or orchestration mechanism is provided. |
| may/005 | M.2 | met | judgement | `content/workspace/REPORT.md#L48`, `content/workspace/analysis/README.md#L11` | The report lists key artifacts and the analysis README links to the protocol and output locations. |

## Probe disagreements and flags

- **must/004, must/005, must/006:** the probes only saw tracked paths or recognized annex pointers. The complete stop capture contains worker outputs, and the annexed-input commit is supplied rather than worker action; judgments account for that attribution.
- **must/007 and must/008:** the entry-point probe missed `analysis/README.md` and `analysis/run_group.py`, which document the route.
- **must/010:** the probe missed untracked `requirements.txt`; it still declares the direct third-party dependencies in the complete delivery.
- **should/003:** `modules-separated` inspected tracked paths only. The full layout has separate directories, while the update boundaries remain coupled.
- **should/008:** this repeats must/014 by design (`upstream-duplicate`).

## Not checked

- **should/002:** a validation record exists, but recurring manual or scheduled testing is not established. A run history would settle it.
- **should/004:** the replay did not reach the analysis because the frozen assessor runtime lacks `pip`. A successful fresh-environment run would settle it.
- **should/006:** no environment reconstitution history is captured; a successful reconstitution test and record would settle it.

The probe's extra finding `license-declared` is unmet: reuse terms are not stated. It is not a checklist item. No `AGENTS.md`, `CLAUDE.md`, or TODO/FIXME/known-gap matches were found in the project files; no issue tracker or remote was declared.

## Goals, kind and assumptions

The documented goal is to test whether potential gain has a positive group-level vmPFC response in the equal-indifference cohort, using the supplied 54 gain-effect maps and metadata (`input/study-task.md`; `REPORT.md`). I assess this as a **study**: its product is a scientific inference supported by input data, code, environment instructions and results. No human guidance was attached to confirm these assumptions.

## Checklist link and provenance

[Open the filled checklist](2026-10-16-url.txt). The complete response is [`2026-10-16-response.json`](2026-10-16-response.json); scripted probe output is [`2026-10-16-probes.json`](2026-10-16-probes.json).

Produced with `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1, by Codex / GPT-6 (specific variant not exposed), on 2026-10-16. Target: canonical capture SHA-256 `794cdbd43e94970c2643887f261be89131d348e93c742f67f737491d9e2abfc1`, original HEAD `82443e43a1171f47c085c5e0fadc9e8132a12053`. Probe output: [`2026-10-16-probes.json`](2026-10-16-probes.json). Replay measurement is incomplete due to the frozen runner runtime failure described above.
