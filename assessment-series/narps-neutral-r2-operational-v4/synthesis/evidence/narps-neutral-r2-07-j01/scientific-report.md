# Independent assessment — NARPS potential gains and brain activity

Assessment date: 2026-10-16 (UTC). Object kind: **study**. Goal assumption (not human-confirmed): answer the supplied group-level NARPS question using the complete participant gain maps and report a reproducible, scientifically interpretable conclusion. No treatment assignment was inferred or reported.

Canonical delivery: SHA-256 `7f0de9d39bc3997e976a3d16bea8531a5902fd34a34d71338c9ebc2e591de2e0`; captured HEAD `8c6a78dcf33d4e58f7f2b9e276b5c42bccb797fa`; worker-stop receipt SHA-256 `01406b359dcfb08516352b5de09832bea4a6f2afe412c8e2771645a1c63b2309`. Unless marked as an operational observation or external receipt, citations below use paths relative to the canonical capture with this SHA-256.

## Verdicts

MUST: **4 met / 2 partial / 11 unmet / 0 not-checked / 0 not-applicable** (17 items).
SHOULD: **1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable** (9 items).
MAY: **3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable** (5 items).

These are item judgments, not an overall score.

## What to fix first

1. Track `analysis.py`, `report.md`, and `results/` in the delivered Git state. They were untracked at stop, so the worker commit does not version the scientific product (must/004).
2. Add a pinned, installable dependency/environment specification and document its setup. The only run command points to a host-specific external Python environment; package version strings in a result summary do not recreate it (must/003, 007, 009–017; should/005–008).
3. Record each run with its input identities, exact environment, command, and generated outputs. `results/summary.json` has a seed and package versions, but no exact environment identity or linked run record (must/006, 015).
4. Publish or declare an authorized route covering the complete study product, not just the NeuroVault input maps, and state reuse terms. A researcher needs the code, report, results, metadata, and usable environment as well (must/016; extra item: licence-declared).
5. Add recurring workflow and environment reconstitution evidence. The coordinator replay is reported separately and does not count as worker practice (should/002, 004, 006).

## What is already good

- The delivery contains all 54 participant maps, metadata, and input checksums; maps are Git-annex managed and their retained payloads sit inside the workspace (`input/sources.json`, `input/participants.tsv`, `input/data/`).
- The group analysis is inspectable and scientifically well targeted: it uses all 54 participants, a common-support mask, an explicit atlas-derived vmPFC definition, and one-sided whole-brain max-T correction (`analysis.py`, `results/summary.json`, `results/tables/participant_qc.tsv`).
- The report distinguishes non-detection from evidence of no effect, describes the upstream gain scaling and missing participant variance maps, and makes the anatomical approximation and sensitivity check visible (`report.md`).

## Scientific assessment

Hypothesis outcome: In the 54-person NARPS equal-indifference group, where the potential-gain range was twice the potential-loss range, the participant gain-effect estimates provide no support for a positive vmPFC response to increasing potential gain under whole-brain familywise-error (FWE) correction.

Scientific adequacy: supported — the conclusion of no whole-brain-corrected vmPFC support follows from a defensible group model and correction, and is appropriately bounded by the supplied first-level estimates, common-support restriction, equal weighting, and approximate anatomical ROI.

The analysis reads the 54 supplied participant contrast maps rather than time-series data, checks file checksums, geometry, and finite values, and analyzes the intersection of nonzero coverage. The one-sample participant-level model is appropriate given independent participants and no supplied variance maps. The 20,000 one-sided sign flips use the voxelwise maximum statistic over the common brain mask, which addresses the task’s whole-brain correction requirement. The report gives the vmPFC ROI definition (Harvard–Oxford cortical 25% “Subcallosal Cortex” plus “Frontal Orbital Cortex”), the ROI estimate and interval, the strongest ROI voxel’s whole-brain-corrected p-value, and the outside-ROI corrected clusters (`analysis.py`, `results/summary.json`, `results/tables/corrected_clusters.csv`).

The reported mean vmPFC estimate is −0.0037 model units (unadjusted 95% t interval [−0.0222, 0.0147]); the best vmPFC voxel has max-T FWE p=.780 and no vmPFC voxels survive FWE correction. The corrected posterior clusters do not support the vmPFC hypothesis. The report correctly says that non-detection does not prove a zero effect or equivalence. It also notes that AO86 mean-centered and variance-normalized the gain modulator, that gain and loss were modeled separately, and that the available maps omit first-level uncertainty. The atlas labels are a reasonable, explicit approximation, though not a uniquely defined vmPFC boundary. I found no material inference error that undermines the stated negative finding.

## Replay and measurement limits

Before execution, `replay-plan.txt` declared the exact documented command, inputs, prerequisites, selected outputs, and comparison rule. The frozen helper made a fresh writable copy from the canonical complete delivery; the operational inspection copy was not replayed. It removed only eight explicitly selected generated numerical outputs and protected inputs, code, metadata, and the supplied atlas. One attempt completed in 31 seconds with exit code 0. Seven selected outputs (four maps, the vmPFC mask, and two tables) were byte-identical. The summary JSON differed only in `roi_max_positive_t` (4.1918478012 vs 4.1918477636) and `roi_best_voxel_p_fwe_maxT` (0.77996098995 vs 0.77996100195), both relative changes below 1e-6. However, the frozen comparison helper applies numeric tolerance only to CSV/TSV tables, not nested JSON. Its result is therefore retained as `partial`; I do not substitute a custom comparator or claim the summary passed. This is a helper-comparison limitation, not evidence of target failure. Figures were excluded from comparison because rendering differences do not by themselves change scientific quantities.

The worker’s documented interpreter was the external common-environment Python path in `report.md`; it existed on this host, and its Nilearn cache was present. The replay therefore measures same-host repeatability using that pre-existing environment. The environment was not supplied in the workspace and was not reconstructed, so replay does not establish portability or independent environment reproduction. Replay stdout/stderr and all helper outputs are retained under `replay-work/`.

## Worker state, capture integrity, and attribution

The worker-stop receipt records a normal exit and HEAD `8c6a78dcf33d4e58f7f2b9e276b5c42bccb797fa`. An operational-copy `git status --short --ignored` observation showed `analysis.py`, `report.md`, and `results/` untracked, while `.codex/` and `.entire/` were ignored. The initial operational manifest matches the canonical capture, whose complete stop inventory includes these files; compared with the captured HEAD, they were therefore outside the worker commit. They are used for scientific assessment but do not earn worker version-control credit. The source maps are annex-managed at the worker stop. No repository remote is recorded in `.git/config`. Coordinator capture/preservation and this assessment’s replay do not establish worker publication or worker testing practices.

`judge-target.json` gives no reference limits. The input symlinks are relative links into `.git/annex/objects` within the captured workspace; no external Git pointer was followed. The worker’s source route in `input/sources.json` names NeuroVault. A HEAD request to one representative map on `neurovault.org` returned HTTP 200 (retained in `access-route.stdout`), so that host and one map were reachable from this assessment host. The route lists 54 input maps, but was not individually tested for every map and does not cover the analysis code, report, derived results, or runtime. No complete worker-declared retrieval route was found. The intended recipient is a researcher using an authorized route; anonymous access is not required.

The initial operational manifest matched the canonical capture identity. Final comparison found no changes outside the allowed regular-file annex keys database metadata (`db`, `db-shm`, `db-wal`); inspection created/changed those files. Their logical database equivalence is not established, and this inspection metadata is not worker evidence. The frozen replay helper independently validated the canonical capture before and after its attempt. No scientific-input mismatch was observed. The captured `.entire/` session metadata indicates assistance/session logging was present; this exposure is recorded without using that content as grading evidence.

## Not checked

- `should/002`: recurring workflow testing cannot be established from one stopped workspace; a worker-side repeated test or CI history would settle it.
- `should/004`: the assessment-time replay cannot establish that the worker tested a fresh environment; a worker-side clean-environment run record would settle it.
- `should/009` is not applicable because no restricted data or software component is identified.
- `may/001` is not applicable because there are no independently maintained project modules; annex-managed inputs are inside the same repository boundary.

## Flagged items and probe interpretation

- `must/002`: the probe looked for subdatasets; inspection found the 54 maps in internal annex storage.
- `must/006`: tracked-path heuristics missed untracked generated outputs; the full capture contains outputs, but no exact-environment run record.
- `must/007` and `must/008`: the probe did not recognize `report.md` and the untracked `analysis.py`; the report provides a usage command and the script is a clear starting point, while installation instructions remain incomplete.
- `must/009`: the path probe scanned tracked text only; the untracked report contains a host-specific absolute interpreter path.
- `must/011` and `must/012`: the command scan did not settle host setup; the documented external interpreter path is an undocumented host assumption and no system requirements are listed.
- `must/015`: version strings in the untracked summary do not constitute a complete environment pin.
- `should/006`: the CI probe could not establish reconstitution testing; inspection found no environment specification to test.
- `may/001`: the no-subdataset probe could not determine component structure; review found no independently maintained external module.
- `should/008`: this duplicates must/014 in the pinned checklist; the same missing environment-update process applies.

## Checklist table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `.git/HEAD` | Workspace and its contents share one captured root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | All 54 maps resolve within the workspace through retained annex objects. |
| must/003 | S.1 | unmet | judgement | `analysis.py`, `report.md` | Python software dependencies are imported but no dependency environment is delivered. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `analysis.py`, `report.md`, `results/summary.json` | Git has a commit, but the analysis, report, and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | All 54 large input maps are retained through Git-annex. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+probe:run-env-linked+judgement | `results/summary.json`, `analysis.py` | Shipped results lack a run record linking execution to an exact environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md`, `analysis.py` | The report gives a usage command, but no installable environment or installation instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analysis.py` | The report names analysis.py as the starting point for rerunning the group analysis. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `analysis.py`, `report.md` | Code uses relative paths, but the documented run command hardcodes a host-specific absolute interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analysis.py`, `report.md` | Analysis dependencies have no delivered specification for installation or resolution. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `report.md` | The documented route assumes a specific external host path without documenting host setup. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md`, `analysis.py` | No system requirements or dependency installation steps are documented. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `.git/HEAD` | No environment specification is present in version control or the delivered workspace. |
| must/014 | P.3 | unmet | judgement | `report.md` | No environment update process or dependency specification is delivered. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/summary.json` | Reported package versions do not identify a complete reproducible environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `.git/config`, `input/sources.json` | No environment specification or complete project publication route is provided. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report does not explain how to obtain or reconstruct its external prepared environment. |
| should/001 | T.2 | met | judgement | `.git/HEAD`, `input/data/sub-001_hypo1_cope.nii.gz` | One Git repository contains project files and Git-annex manages the large maps. |
| should/002 | A.2 | not-checked | probe:ci-present | `probes.json` | No worker evidence establishes that the workflow was tested regularly; a single run does not settle frequency. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/participants.tsv`, `analysis.py` | Inputs and results are separated, but analysis code and environment are not separate modules. |
| should/004 | E.1 | not-checked | judgement | `fresh-rerun.json`, `worker-end-state.json` | The coordinator replay is not worker practice; no worker fresh-environment run is recorded. |
| should/005 | E.1 | unmet | judgement | `report.md` | The documented command reuses a pre-existing shared environment rather than creating a disposable one. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `report.md`, `probes.json` | There is no exact environment specification to reconstitute and regularly test. |
| should/007 | D.2 | unmet | judgement | `analysis.py`, `results/atlas/README.md` | The workspace does not archive the Python environment or its executable artifacts. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment-update process or tracked update is present; duplicates must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: supplied maps and software are public; no restricted component is identified. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `analysis.py` | N/A: no independently maintained project components; the maps are data inputs inside this workspace. |
| may/002 | M.2 | met | judgement | `report.md` | The report explains the input, analysis, and results relationship and links the outputs. |
| may/003 | M.2 | partial | judgement | `input/participants.tsv` | Input and result directories are separable, but code/environment boundaries are not independently updateable. |
| may/004 | M.2 | met | judgement | `analysis.py` | analysis.py composes the supplied input directory with generated result paths in a single reproducible entrypoint. |
| may/005 | M.2 | met | judgement | `report.md` | The report links and describes inputs, code, figures, tables, and numerical outputs. |

## Goals and kind

The supplied task asks for a group-level assessment of whether potential gain increases vmPFC response in the equal-indifference group, using the supplied 54 maps and metadata. I treat this as a **study** whose product is the scientific conclusion plus its analysis and results. This is an explicit assumption because no human confirmation was attached; it follows `input/study-task.md` and the retained coordinator scientific guidance.

## Checklist and provenance

[Open the STAMPED checklist response](2026-10-16-url.txt). The machine-readable record is [response.json](response.json); the frozen probe output is [probes.json](probes.json), and the single replay report is [fresh-rerun.json](fresh-rerun.json). Access details are in [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study at commit `8c6a78dcf33d4e58f7f2b9e276b5c42bccb797fa`, 2026-10-16, Codex API/GPT-6. Probe output: `probes.json`. Capture: `manifest.json`, SHA-256 `7f0de9d39bc3997e976a3d16bea8531a5902fd34a34d71338c9ebc2e591de2e0`.
