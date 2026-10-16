# Independent assessment — NARPS potential gains and vmPFC

**MUST:** 4 met / 2 partial / 11 unmet / 0 not-checked. **SHOULD:** 0 met / 1 partial / 5 unmet / 2 not-checked / 1 not-applicable. **MAY:** 0 met / 2 partial / 0 unmet / 1 not-checked / 2 not-applicable. No overall score is assigned.

## What to fix first

1. Add a reproducible environment specification and link it to the results. This addresses the missing dependency installation, host requirements, environment identity and sharing (must/003, 006, 010–017).
2. Track the analysis script, scientific report and generated results at the worker stop. This makes the delivered study state reviewable and links code to results (must/004, should/001).
3. Add installation and usage instructions that start from a clean environment and identify any network resources the script may fetch (must/007, 011–012, 017).
4. Add a worker-controlled retrieval route covering the complete study object. The current coordinator handoff does not establish recipient access (access record).

## What the project already does well

- It includes all 54 input maps and metadata under `input/`, and the analysis uses paths relative to its own location (`analyze.py`, `input/sources.json`).
- The report explains the gain-map scale, model assumptions, sample and mask, uncertainty, anatomical choice, correction, and limits (`REPORT.md`, `input/upstream-methods.md`).
- The analysis script is a clear entrypoint and writes named outputs under `results/` and `figures/` (`analyze.py`, `REPORT.md`).

## Scientific judgment

**Scientific adequacy: supported.** The report supports its conclusion that the supplied analysis does not demonstrate a positive vmPFC effect under required whole-brain correction. It analyzes all 54 equal-indifference participants, checks map checksums and geometry, uses a positive one-sample group test with whole-map participant sign flips and a whole-brain maximum-statistic FWE correction, and separately reports a broad anatomical vmPFC summary. The corrected foci are occipital, not vmPFC; the ROI mean is 0.0019 model units with 95% CI [−0.0200, 0.0238]. The report appropriately treats the ROI result as descriptive and does not claim a null effect. Evidence: canonical capture SHA-256 `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77e`, `REPORT.md`, `analyze.py`, `results/summary.json`, `results/vmPFC_roi_summary.json`, and `results/corrected_clusters.csv`.

**Reported hypothesis outcome:** “The supplied data do **not support a positive vmPFC gain effect** at the required whole-brain corrected level.” This outcome is retained separately from the adequacy category.

The sign-flip inference relies on independent participants and a symmetric zero-centered null, as stated in the report. The maps are upstream participant-level parameter estimates of a standardized gain modulator, not currency-unit slopes or test statistics; first-level variance maps are absent. These limits are stated. The supplied results and code support the reported conclusion conditional on those fixed upstream inputs. The p-value NIfTI fills voxels outside the analysis mask with zero (`analyze.py`), so those outside-mask values must not be read as corrected evidence; the report's inference is based on the explicitly defined mask and cluster table.

## Capture, worker stop and access

The canonical original capture is `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77e`; original HEAD is `bfe069501c140673f38778116f34bc8a5c36366f`. The operational manifest initially has the same digest. The external worker stop receipt `worker-end-state.json` (SHA-256 `a5b81c7f265e90323f156ce5d1f98b3ac849e44f4b268959765f47ba0572eeb1`) records a complete capture and exit code 0. It shows the analysis script, report, figures and results as untracked at stop; the captured HEAD is a supplied-input baseline, so it does not establish worker versioning of those deliverables. Annex-backed input pointers and coordinator preservation do not earn worker-practice credit.

The delivery includes `.entire` session metadata, which reveals possible assistance exposure. I did not inspect its contents or use it as grading evidence. No treatment assignment is inferred or reported.

No worker-declared access route was found. The recipient considered is a researcher using an authorized retrieval route. Required coverage includes the study description, code, all input maps and metadata, results/figures, and the environment needed to rerun. No host scope could be tested because no worker route was declared. Coordinator handoff is not proof of worker accessibility; see `access-record.json`.

A complete-delivery replay was not checked. The only documented command is `python analyze.py`, but dependencies are not pinned or installable from the captured stop state. Replay details and the exact candidate output list are in `replay-record.json`.

The integrity check found only classified annex database metadata differences: `.git/annex/keysdb/db` changed and `.git/annex/keysdb/db-shm` and `db-wal` appeared during inspection. No other manifest path was missing, extra, or changed. These are inspection-induced operational metadata, not worker evidence; logical database equivalence was not established.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md` | Study workspace, inputs, script and outputs share the captured root. |
| must/002 | S.1 | met | judgement | `analyze.py`, `input/sources.json` | All maps and metadata are inside input/ and code resolves them relative to the script. |
| must/003 | S.1 | unmet | judgement | `REPORT.md` | Runtime packages are named but no environment installs or includes external software. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `analyze.py`, `REPORT.md`, `worker-end-state.json` | Worker analysis code, report and outputs were untracked at stop; the captured commit is the supplied input baseline. |
| must/005 | T.1,T.3,T.5 | unmet | probe:large-in-annex+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `worker-end-state.json` | Annex pointers reflect supplied input handling; the stop record does not show worker versioning of large data. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/summary.json`, `REPORT.md` | Shipped results have no worker run record linking actions to an exact environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md` | REPORT.md gives usage but no installation steps or environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analyze.py`, `REPORT.md` | analyze.py is a clear documented group-analysis entrypoint, though untracked at stop. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analyze.py` | The inspected worker script uses paths relative to its own location. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analyze.py`, `REPORT.md` | The script imports NumPy, pandas, NiBabel, SciPy, Matplotlib and Nilearn, but no dependency specification is delivered. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `REPORT.md`, `analyze.py` | The documented route assumes a prepared Python environment and network-fetched Nilearn atlas/template resources without documenting host prerequisites. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `REPORT.md` | REPORT.md names Python packages but omits installable versions and system/network requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `worker-end-state.json` | No tracked or untracked environment specification is in the complete stop inventory. |
| must/014 | P.3 | unmet | judgement | `REPORT.md` | No command or process for updating environment specifications is documented. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/summary.json` | No frozen environment identity is linked to the result artifacts. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `worker-end-state.json` | No worker-published environment artifact or retrieval route is recorded. |
| must/017 | D.1 | unmet | judgement | `REPORT.md` | Readers are told to use a prepared Python environment, but not how to obtain or build it. |
| should/001 | T.2 | unmet | judgement | `worker-end-state.json`, `REPORT.md` | At worker stop, the study code and derived results were outside the supplied Git baseline and untracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `REPORT.md` | No repeated test record is present; a single worker run or a future CI check would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/` | Inputs, code and derived outputs occupy separate directories, but code and outputs are not tracked and no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `replay-record.json` | No fresh-environment run was performed; a successful isolated execution would settle this. |
| should/005 | E.1 | unmet | judgement | `REPORT.md` | The documented command uses a prepared Python environment; no per-run disposable environment is created. |
| should/006 | D.2 | unmet | probe:env-spec-tracked+judgement | `worker-end-state.json` | There is no environment specification to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `worker-end-state.json` | No environment artifact is archived in the worker stop state. |
| should/008 | D.2 | unmet | judgement | `REPORT.md` | No environment update process is stated; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivered inputs and listed software are public; there is no restricted component to isolate. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json` | N/A: this study has no independently maintained linked project components; runtime libraries are package dependencies. |
| may/002 | M.2 | partial | judgement | `REPORT.md` | The report names inputs, code and result locations but does not explain modular boundaries or their relationships. |
| may/003 | M.2 | unmet | judgement | `REPORT.md` | The delivered project has no documented modular boundaries designed for independent updates. |
| may/004 | M.2 | not-applicable | judgement | `input/sources.json` | N/A: no independently maintained modules are composed by this study. |
| may/005 | M.2 | partial | judgement | `REPORT.md` | The report lists key files, but offers no broader navigation guide or README. |

Every artifact path in the table is relative to `content/workspace` in canonical capture SHA-256 `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77e`. The retained canonical manifest and worker stop receipt are referenced in `response.json` and the access/replay records.

## Flagged items

- **must/004, must/005, must/006, must/007, must/008:** probes inspect repository structure, annex use, and entrypoint files; the verdicts also account for the worker stop receipt and complete untracked delivery. Coordinator-supplied Git/annex state does not establish worker practices.
- **must/009:** the probe scanned tracked paths; direct reading confirmed the untracked `analyze.py` also uses a relative project root.
- **should/008:** duplicates must/014 in the frozen checklist.

## Not checked

- **should/002:** no repeated test record is present; a repeated run or equivalent regular testing record would settle it.
- **should/004:** no fresh-environment replay was attempted because the worker supplied no environment specification.
- **should/005:** no evidence establishes whether the worker used disposable environments; a stop-state execution record would settle it.
- **may/003:** independently updateable module boundaries are not identified; module documentation would settle it.

## Goals and kind

The task is a group-level NARPS Hypothesis 1 analysis of potential gain effects in vmPFC, using the supplied 54 participant effect maps and metadata. This is a **study**: its product is a scientific answer with code, results and figures. This kind is an explicit assessment assumption based on `input/study-task.md`; no human guidance was attached to confirm it.

## Checklist and provenance

[Open the completed STAMPED checklist](2026-10-16-url.txt). The full per-item record is [response.json](response.json); probes are in [probes.json](probes.json). Replay and access records are [replay-record.json](replay-record.json) and [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study at original HEAD `bfe069501c140673f38778116f34bc8a5c36366f`, 2026-10-16, frozen external assessment runner source `9852d8360f9519d21d11099b45f5deb8ba80cb28`; model identity was not provided by the runtime. Probe output: `probes.json`.
