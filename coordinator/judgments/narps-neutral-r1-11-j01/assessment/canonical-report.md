# Independent assessment: NARPS potential gains and brain activity

**STAMPED verdicts:** MUST: 4 met / 2 partial / 11 unmet / 0 not-checked (17). SHOULD: 1 met / 1 partial / 5 unmet / 1 not-checked / 1 not-applicable (9). MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable (5). No overall score is assigned.

## What to fix first

1. Track the worker-created analysis, report and results at the stop state. Their absence from the Git commit means the recorded revision does not contain the delivered scientific work (must/004).
2. Supply a pinned environment declaration with install/update instructions and tie it to the run record. The current report assumes an external interpreter and no exact environment can be recreated from this object (must/003, 006, 010–017; should/005–008).
3. Make the documented run route portable and publish the complete object through a declared authorized route. The report's interpreter path is host-specific, and no worker retrieval route was declared (must/007, 009, 016–017).
4. Record recurring workflow checks and environment reconstitution. One shipped result set does not establish regular testing (should/002, 006).

## What the project already does well

- The complete workspace includes all 54 supplied participant maps as annex payloads, plus cohort and source metadata; the analysis checks each map's SHA-256 before use ([sources.json](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-11-j01/content/workspace/input/sources.json>), [analysis script](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-11-j01/content/workspace/analysis/run_analysis.py>)).
- The analysis uses whole-brain one-sided max-*t* correction and defines its Harvard–Oxford vmPFC proxy independently of the activation results. It reports participant QC, permutation maxima, an ROI interval and figures ([report](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-11-j01/content/workspace/report.md>), [results](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-11-j01/content/workspace/results/results.json>)).
- The report correctly limits interpretation: supplied coefficients are normalized gain-modulator estimates, not slopes per currency unit; participant-level variance maps and an executable upstream model are absent.

## Scientific assessment

**Scientific adequacy: qualified.** The delivered group analysis is appropriate for a conditional group-stage test: it includes the 54 equal-indifference participants, checks map hashes and common geometry, retains participants without outcome-based exclusions, uses an equal-weight one-sample test on participant-level effects, and controls positive whole-brain family-wise error with a studentized sign-flip max statistic. The vmPFC proxy (Harvard–Oxford Frontal Medial and Subcallosal labels at 25%) is specified without using the observed activation, and the report separates the whole-brain corrected decision from the descriptive ROI interval.

The **reported hypothesis outcome** is *not supported*: the ROI mean is 0.0062 (95% CI −0.0204 to 0.0327), and no vmPFC voxel survives whole-brain FWE correction. This is defensible evidence of no corrected positive finding in these supplied estimates, not evidence that the true effect is zero. The gain regressor was normalized upstream and gain/loss were modeled separately, so the estimate is not a response slope per dollar and cannot establish a gain-versus-loss range-scaled contrast.

The qualification is coverage handling. The analysis includes voxels with nonzero support in at least 90% of participants and uses zero values as coefficients for the remaining participants ([coverage audit](scientific-coverage-audit.json)). In the delivered vmPFC ROI, 1,422/1,638 voxels are nonzero in all participants; 216 have at least one zero (no voxel has more than five). No separate missingness indicator or coverage sensitivity is reported. The corrected whole-brain peak has nonzero values for all participants. This leaves a bounded uncertainty about edge/coverage voxels, while the ROI estimate and corrected map still support the stated lack of positive corrected evidence. Participant variance maps are unavailable, so equal-weight group inference is a reasonable available choice but cannot account for first-level precision.

The inspected output is internally coherent, but the single permitted replay did **not** execute the target: the frozen adapter rejected the pre-created empty workdir before copying or invoking the entrypoint. This is recorded as an assessor-side helper precondition failure, not target behavior. It leaves computational repeatability not checked and does not replace inspection of the shipped scientific evidence.

## Delivery boundary, attribution and verification

The worker stop receipt identifies commit `eece8595d255a766517e32ff10b2e6574d3c4e6a`, a normal exit at 2026-10-16 06:31:42 UTC, and a complete captured workspace. The manifest SHA-256 is `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa`; the receipt SHA-256 is `326729607bc2dd9e90676b27d7204dd180cee4b3cdc2491383b6ec65728910b1`. Final frozen validation and independent byte/mode checks matched all 1,238 manifest entries. A first directory check briefly found two annex SQLite sidecars absent; both returned on later checks. This transient mismatch and its unknown cause are retained in [manifest records](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/manifest-validation-observation.json>); it did not persist.

At the worker stop, `analysis/`, `report.md`, `results/` and `.codex/` were untracked; they are assessed as delivered scientific artifacts but do not earn Git tracking credit. The input maps are annexed. The capture has a workspace-resident `.git` directory and no Git dependencies or reference limits. No coordinator commit, upload or route is credited to the worker. See the [worker stop receipt](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/worker-end-state.json>) and [manifest verification](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/manifest-verification.json>).

## Assistance exposure

The captured commit message includes a Codex co-author/runtime identifier. This is recorded as evidence of assistance exposure only; it was not used to judge the scientific result or checklist items.

## Access record

The intended recipient is a researcher using the worker-declared authorized route; anonymous access is not required. No project remote or publication route was declared in the captured Git configuration or report, so there was no worker route to test. The URLs in `input/sources.json` retrieve upstream inputs, not this worker's code, report or results. The coordinator's local delivery to the assessor is not evidence of worker-side access. Required coverage for a usable route is the complete object, including all map payloads, code, report, results and a usable environment specification. Host scope was this local captured workspace only. See [access record](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/access-record.json>).

## Replay record

One formal attempt was registered with the documented command, explicit output selection (`results/results.json`, `results/participant_qc.tsv`, `results/permutation_max_t.tsv`), 7,200-second limit, 5 GB retrieval limit and 10⁻⁶ relative tolerance for numeric tables. The adapter failed before materialization because the assessment invocation created the workdir directory, while the frozen materializer requires a new destination. No code ran and no supplied output was removed. The one-attempt allowance is consumed; there was no second attempt. The failure stdout/stderr and formal argument record are retained in [replay records](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/replay-record.json>), [formal attempt](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/formal-replay-attempt.json>), [stdout](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/replay-helper.stdout>) and [stderr](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j01/attempt-01/judgment/replay-helper.stderr>). Replay status is not-checked due to the assessor helper failure.

## Per-item STAMPED checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/data`, `analysis/run_analysis.py` | All supplied maps, metadata, analysis, results and atlas assets are inside the captured workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data` | The 54 maps and cohort/method metadata are present under input/; source URLs and pins are recorded. |
| must/003 | S.1 | unmet | judgement | `report.md#Reproduction and artifacts`, `analysis/run_analysis.py` | No software environment specification or linked software module accompanies the Python analysis. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `git status --short at stop`, `worker-end-state.json` | At worker stop, all analysis code, report and results were untracked; Git contains only the supplied starting materials. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `.git/annex/objects`, `probes.json#large-in-annex` | The 54 participant input maps are stored as git-annex payloads under the Git-controlled workspace. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/results.json` | Shipped results identify package versions but do not link the execution to an exact environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md#Reproduction and artifacts` | report.md explains reproduction, but its command depends on an external host-specific interpreter and gives no environment installation route. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/run_analysis.py`, `report.md#Reproduction and artifacts` | analysis/run_analysis.py is a clear group-analysis entrypoint and report.md names the command. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `analysis/run_analysis.py`, `report.md#Reproduction and artifacts` | The script uses paths relative to itself, while the documented interpreter command hardcodes a worker-host absolute path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/run_analysis.py`, `probes.json#env-spec-tracked` | The analysis imports NumPy, SciPy, nibabel, pandas, Nilearn and Matplotlib, but no environment declaration is delivered. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `report.md#Reproduction and artifacts`, `analysis/run_analysis.py` | The documented route assumes an absolute interpreter path and installed packages; host and system requirements are not specified. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md#Reproduction and artifacts`, `probes.json#platform-assumptions` | No README or environment specification lists installation, system requirements or dependency setup. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json#env-spec-tracked`, `worker-end-state.json` | No environment specification is present in the worker delivery or versioned tree. |
| must/014 | P.3 | unmet | judgement | `report.md`, `analysis/run_analysis.py` | No environment specification or dependency-update process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/results.json` | No frozen environment specification or exact lock snapshot is retained for reproducing these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `report.md#Reproduction and artifacts`, `git config` | No worker-published or archived software environment specification is identified. |
| must/017 | D.1 | unmet | judgement | `report.md#Reproduction and artifacts` | The report gives an interpreter path but no instructions for obtaining or installing the environment. |
| should/001 | T.2 | met | judgement | `git status --short at stop`, `.git/annex/objects` | Git versions text and code while git-annex stores the input maps within the same repository boundary. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probes.json#ci-present`, `results/results.json` | Only one completed result set is evidenced; no CI or recurring manual test record is present. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/, analysis/, results/`, `report.md#Reproduction and artifacts` | input/, analysis/ and results/ separate data, code and outputs; no environment module or specification is supplied. |
| should/004 | E.1 | not-checked | judgement | `report.md#Reproduction and artifacts` | No run record establishes execution in a fresh container, VM, batch job or cloud instance; a captured run environment would settle this. |
| should/005 | E.1 | unmet | judgement | `report.md#Reproduction and artifacts` | The documented entrypoint invokes a pre-existing shared environment and does not create a disposable environment per run. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probes.json#env-spec-tracked`, `probes.json#ci-present` | No exact environment specification exists to reconstitute or test. |
| should/007 | D.2 | unmet | judgement | `results/atlas/`, `worker-end-state.json` | The atlas is archived, but no Python environment artifact or executable environment is included. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment update process is declared or tracked; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the supplied public inputs and software are not access-restricted. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json` | N/A: no independently maintained project component is a subject; source datasets and package dependencies are inputs, not modules. |
| may/002 | M.2 | partial | judgement | `input/, analysis/, results/`, `report.md#Reproduction and artifacts` | Directories distinguish inputs, analysis code and outputs, but the report does not document their modular relationships. |
| may/003 | M.2 | partial | judgement | `analysis/run_analysis.py` | The script consumes input/ and writes results/, but the fixed filename and absent environment contract limit independent module updates. |
| may/004 | M.2 | met | judgement | `analysis/run_analysis.py` | analysis/run_analysis.py composes the delivered input maps and metadata into results/. |
| may/005 | M.2 | met | judgement | `report.md#Reproduction and artifacts`, `results/atlas/README.md` | The report identifies the entrypoint, principal outputs and their locations; results/atlas/README.md describes cached atlas data. |

## Flagged items

- `must/002`: the resolver probe did not establish this, but manual inventory confirmed the input maps and metadata are inside the boundary.
- `must/006`, `must/015`: run/environment probes could not resolve exact environment identity; package version strings are insufficient, and no environment spec is supplied.
- `must/007`, `must/008`, `must/009`: filename/track-only probes missed equivalent `report.md` instructions and the untracked entrypoint; the documented absolute interpreter path remains nonportable.
- `must/011`, `must/012`: the command scan did not settle host assumptions or requirements; the documented route assumes an existing host interpreter and packages.
- `must/014`, `should/008`: duplicated checklist wording; both repeat the absent environment-update process.
- `should/002`, `should/006`: the CI probe was only a heuristic; inspection of shipped records found no recurring test or exact environment reconstitution record.
- `should/003`: the directory-only probe missed the `analysis/` and `results/` separation; environment separation remains absent.

## Not checked

- `should/004`: no execution record establishes a fresh container, VM, batch or cloud run. A worker run record with its environment and isolation context would settle it.
- Replay: no target execution occurred because the frozen replay adapter failed before copy/entrypoint; the failed attempt is retained and the one-attempt allowance is consumed.

## Goals and kind

Assumption, not user-confirmed: the product is a group-level scientific answer to NARPS Hypothesis 1 plus code and results; the primary kind is a **study**. The goal comes from `input/study-task.md` and `report.md`. Accordingly, the assessment emphasizes the scientific inputs, provenance, actionability and environment for this result.

## Checklist, stamp and retained files

[Open the checklist response](2026-10-16-url.txt). The canonical machine-readable answers are in [response JSON](2026-10-16-response.json); unmodified frozen probe output is in [probes.json](2026-10-16-probes.json). The report, response, probes, URL, access and replay records are outside the assessed delivery.

Produced using `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad`), on the complete delivery at commit `eece8595d255a766517e32ff10b2e6574d3c4e6a`, 2026-10-16. Harness: OpenAI Codex API; exact harness version and deployment model ID are not exposed. Frozen assessor source commit: `9852d8360f9519d21d11099b45f5deb8ba80cb28`. Probe output: [probes.json](2026-10-16-probes.json).
