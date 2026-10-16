# Independent assessment — 2026-10-16

## Verdict

**MUST: 4 met / 1 partial / 11 unmet / 1 not-checked**  
**SHOULD: 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable**  
**MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable**

These are per-item findings, not an overall score. The primary scientific concern is the invalid permutation statistic. The principal reproducibility concerns are that the worker’s script/report/results were untracked and the documented environment cannot be reconstructed from the delivery.

## What to fix first

1. Correct the signed-permutation *t* calculation and regenerate the correction maps, summary and report. In `analysis/run_analysis.py` lines 88–90, the signed participant sum is divided by a standard error for the **mean** without first dividing the numerator by *n*. This inflates every permutation statistic by approximately *n* and invalidates the reported permutation FWE *p* values.
2. Track the analysis script, report and derived results at the worker stop so the delivered scientific state is versioned, not just the supplied inputs (must/004; should/001).
3. Add a pinned, obtainable environment specification and installation instructions for the imports and Nilearn atlas/template resources (must/003, must/007, must/010–017; should/006–008).
4. Declare a recipient-facing retrieval route and verify that it covers the complete input, code, report, result and environment artifacts. No worker route was observed (must/016).

## What is already strong

- The full set of 54 participant maps and cohort metadata is included under `input/`; the analysis checks IDs, affine/dimensions and finite values, uses a common coverage mask, and excludes nobody (`input/participants.tsv`, `input/upstream-methods.md`, `analysis/run_analysis.py`).
- The report correctly explains the supplied cope scaling and upstream conditioning, the absence of first-level variance maps, equal participant weighting, the broad atlas proxy and why a corrected null does not prove a zero effect (`REPORT.md`, `input/upstream-methods.md`).
- The package-version summary, participant QC, whole-brain maps, ROI estimates and figures make many analytic choices inspectable (`results/analysis_summary.json`, `results/participant_qc.tsv`, `results/figures/`).

## Scientific assessment

**Scientific adequacy: qualified.** The report's no-support conclusion is defensible from its one-sided whole-brain Bonferroni sensitivity analysis (11 corrected voxels, all reported posterior and outside the vmPFC proxy) and the descriptive parcel estimate (mean cope −0.009; 95% CI −0.040 to 0.022; one-sided unadjusted *p*=.723). But the report's primary permutation correction is invalid: `t_obs` uses the mean as numerator (`analysis/run_analysis.py` line 76), while `t_perm = signs @ chunk` is a signed sum and lines 89–90 divide that sum by the standard error of a mean. The resulting null maximum near 200–290, including the reported critical value 290.20, is therefore inflated by roughly *n*=54. The permutation FWE result (*p*=1.00/no survivors) cannot be treated as valid whole-brain inference. The Bonferroni test is an independent, whole-brain corrected sensitivity under the stated one-sample-*t* assumptions and supports the same absence of positive vmPFC evidence, so I classify the overall adequacy as **qualified**, rather than treating the faulty primary permutation as the only evidence. The null still does not establish zero response. Scientific artifacts cited here are from canonical capture 82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b: `content/workspace/analysis/run_analysis.py` (SHA-256 dbd9ed4fff89b4cbae153d6fe890f280d9941d1630137b13f4a521fff7bbae43), `content/workspace/results/analysis_summary.json` (SHA-256 433330e4eac95c89e1279569e1b7e00c69ebac4f0103d9973eb7e56b0d327715), `content/workspace/results/vmPFC_roi_summary.json` (SHA-256 c9882dfde22ee08719f6f352b69262e70dd6637d9f6e8b609c5be4a4350f50fc), `content/workspace/REPORT.md` (SHA-256 f55f8f5578dc6c195365b688613db97a284a428d7444d8faadf9ff3bf40ffbc4), and `content/workspace/input/upstream-methods.md` (SHA-256 508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b).

The reported outcome is: “In the 54-person NARPS equal-indifference group, these data do **not support a positive gain-related response in vmPFC**.” This is the worker report’s stated hypothesis conclusion; it is recorded separately from adequacy. The group design uses all 54 intended participants, common nonzero coverage intersected with an MNI brain mask and a transparent Harvard–Oxford Frontal Medial Cortex proxy. The broad parcel and unadjusted ROI *p* are descriptive; only the whole-brain-corrected sensitivity is relevant to hypothesis support. Effect estimates are not per-currency slopes and remain conditional on the supplied upstream participant model. The analysis assumes independent participants and, for the parametric sensitivity, an adequate one-sample *t* model; no participant variance maps were supplied.

## Delivery identity, attribution and integrity

- Canonical original capture SHA-256: `82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b`; captured HEAD: `d4d11a9c1bd38a9c96b5a4cf0c5403c455f1f96c`. The canonical and initial operational manifest digests match. `reference_limits` is empty.
- The worker stop receipt (SHA-256 `c0e31095b57c285aac338da6216ce53c196d5699cc6a23847eb3ca3da510bab2`) records the full stop-state inventory. Git status showed `REPORT.md`, `analysis/` and `results/` untracked. The captured commit `chore(study): supply materialized scientific inputs` is not credit for worker tracking or publication. The report, code and outputs were nevertheless assessed as scientific evidence from the complete stopped workspace.
- The capture comparison found no integrity-invalidating change. Read-only inspection/probes caused changes only to `.git/annex/keysdb/db`, `db-shm` and `db-wal`, the separately classified operational metadata files. Their logical database equivalence is not established; all original participant-map links matched their retained link targets. Details: [operational-integrity.json](operational-integrity.json).
- Captured `.entire` session artifacts and a `.codex/skills` directory expose assisted-workflow material. This exposure is recorded only; it was not used as grading evidence. No treatment assignment was inferred or reported.

## Replay and measurement limits

One replay was attempted from a fresh full-delivery copy using the documented `python analysis/run_analysis.py` command and the 12 explicit generated outputs listed in [replay-plan.md](replay-plan.md). It stopped before analysis because the frozen interpreter lacked `nibabel`; no environment could be reconstructed from worker-supplied declarations without inventing one. This failed attempt is retained and leaves fresh-environment testing unavailable; it is not evidence that the worker’s script fails in its unspecified prepared environment. No second attempt or repair was made. The entrypoint could not reach its Nilearn atlas/template calls.

## Access and reuse

The intended recipient is a researcher using the declared authorized route. No worker-declared route or Git remote was found, so there was no host scope to test. Required coverage is the complete input set, metadata, code, report, generated results and an obtainable environment. The coordinator’s delivery to the assessor is not evidence that the worker had published or shared these bytes. See [access-record.json](access-record.json). A reuse/license declaration was not found (probe extra item `license-declared`).

## Checklist responses

The study goal is to assess the supplied participant gain-effect maps at the group stage and report uncertainty, correction and limits. This is a **study**: its product is a scientific answer supported by data and computation. Assumption: no human confirmation of this classification was attached.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/input/participants.tsv` | Study inputs, code and outputs are nested under the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/input/participants.tsv`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | All 54 maps and metadata are included in the project boundary. |
| must/003 | S.1 | unmet | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | Required Python packages are named but no environment includes them or links them as a project component. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/worker-end-state.json`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | At worker stop, the analysis, report and result files were untracked; the captured commit covers supplied inputs. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/worker-end-state.json` | Annexed maps are present, but the stop record does not establish worker annex practice versus coordinator-supplied input preparation. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/results/analysis_summary.json`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | Summary records software versions and seed, but no exact environment specification is linked to the recorded analysis. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | REPORT.md gives a run command but no installation instructions for its prepared Python environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | REPORT.md identifies analysis/run_analysis.py and gives its exact invocation. |
| must/009 | P.1 | met | probe:no-abs-paths | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | The script builds paths relative to its own project root. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | No environment specification captures the imports required by the analysis. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/.git/config`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | The prepared environment is unspecified, and captured Git config points hooks to an external host path. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | The report names Python packages but gives no system requirements or usable environment setup. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | No tracked environment file or container definition is present. |
| must/014 | P.3 | unmet | probe:env-spec-tracked | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | No environment specification or update process is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/results/analysis_summary.json` | No frozen environment manifest or container digest is included. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/worker-end-state.json` | No worker-declared route provides the environment specification to another researcher. |
| must/017 | D.1 | unmet | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | Documentation does not explain how to obtain or recreate the prepared Python environment. |
| should/001 | T.2 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/worker-end-state.json` | Input files are committed, but the worker’s code, report and derived outputs are outside Git history. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/judgment/probes.json` | No CI or repeated-test record is present; a manual or scheduled test history would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | Inputs, code and derived outputs have separate directories, but no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/judgment/fresh-rerun.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/judgment/replay-workdir/replay.stderr` | The single replay could not start: the frozen interpreter lacks NiBabel; a replay in the specified worker environment would settle this. |
| should/005 | E.1 | unmet | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | The documented command assumes a prepared long-lived Python environment and does not create an isolated one. |
| should/006 | D.2 | not-checked | probe:run-env-linked+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/results/analysis_summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-12-j01/attempt-01/judgment/fresh-rerun.json` | No frozen environment or repeated reconstruction records are supplied; a tested rebuild would settle this. |
| should/007 | D.2 | unmet | probe:env-spec-tracked | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | No environment image, binary package archive or other environment artifact is shipped. |
| should/008 | D.2 | unmet | probe:env-spec-tracked | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | No environment specification or tracked update process is supplied. |
| should/009 | M.4 | not-applicable | probe:subdatasets-resolvable+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/input/sources.json` | N/A: supplied public data and analysis dependencies have no restricted component to isolate. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/input/sources.json` | N/A: no independently maintained project components are linked; runtime packages are dependencies. |
| may/002 | M.2 | met | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | Report and script explain how fixed inputs, analysis code and generated results relate. |
| may/003 | M.2 | partial | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py` | Inputs and results are separated, but their data contract and versioned boundaries are not documented as independent modules. |
| may/004 | M.2 | met | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/analysis/run_analysis.py`, `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | The documented script composes the included input maps and metadata into results using project-relative paths. |
| may/005 | M.2 | partial | judgement | `capture:82cb872b11c624381c7a999a410c4e657ec5f0d1488285c491760d752160fd2b:content/workspace/REPORT.md` | Report links core outputs but does not document the full input/environment layout or setup. |

## Flagged items

- `must/002`, `must/005`, `must/006`, `must/007`, `must/008`, `must/011`, `must/012`, `should/003`, `should/009`, and `may/001` override or qualify a probe result after reading the complete stopped delivery. The probe’s filename/tracked-path heuristics did not settle those items; worker attribution is explicitly bounded for annex use.
- `should/008` carries `upstream-duplicate`: it repeats the wording of `must/014`.

## Not checked

- `must/005`: annex pointers are present, but worker practice cannot be separated from coordinator-supplied input preparation; stop-state attribution would settle it.
- `should/002`: no CI or repeated-test record was found; a manual/scheduled run history would settle it.
- `should/004`: the single replay was blocked by missing NiBabel in the frozen assessor interpreter; a fresh run in a worker-declared matching environment would settle it.
- `should/006`: no frozen environment or repeated reconstruction record exists; a tested environment rebuild would settle it.

## Record links and stamp

- Checklist-app URL: [2026-10-16-url.txt](2026-10-16-url.txt)
- Machine-readable responses: [response.json](response.json)
- Probe output: [probes.json](probes.json)
- Scientific judgment: [scientific-judgment.json](scientific-judgment.json)
- Replay record: [fresh-rerun.json](fresh-rerun.json)

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0 and checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on the study at captured HEAD `d4d11a9c1bd38a9c96b5a4cf0c5403c455f1f96c`, 2026-10-16; harness `Codex API (runtime build not exposed)`, model `GPT-6 (exact variant not exposed)`. Frozen assessor/runtime: see `assessment-version.json` in the supplied attempt inputs.
