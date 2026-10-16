# Independent assessment — NARPS potential gain and vmPFC

**Scientific adequacy: supported. Reported hypothesis outcome: no whole-brain-corrected vmPFC support.** This supports the restrained conclusion that the supplied group maps do not provide corrected evidence for a positive vmPFC response under the fixed upstream model. It does not establish a zero effect.

## Scientific assessment

The delivery analyzes all 54 equal-indifference participant gain-effect maps and their matching metadata. The code checks participant IDs, input hashes, finiteness, shape and affine; the report states no exclusions. The common finite, nonzero support mask addresses zero-filled voxels outside individual analysis coverage. It uses a participant-level one-sample positive t model and sign-flip maximum-t correction across the whole mask (198,029 voxels), then checks whether corrected positive voxels intersect an independently specified 5 mm vmPFC sphere centered at MNI [2, 46, −8]. That is a defensible whole-brain family-wise inference for the directional hypothesis required by the [NARPS instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). The literature citation for the chosen valuation focus is consistent with [Bartra et al. (2013)](https://doi.org/10.1016/j.neuroimage.2013.02.063).

No positive corrected voxel intersects the vmPFC sphere. The reported sphere mean is −0.012 upstream normalized-regressor units (95% t interval −0.052 to 0.028; t(53)=−0.60; uncorrected one-sided p=.726). The whole-brain test found 24 positive corrected voxels elsewhere (minimum FWE p=.0006), which do not support the vmPFC hypothesis. The report correctly says that non-significance is not proof of zero, and the normalized gain coefficient is not an effect per currency unit. The participant variance maps are absent, so the group analysis cannot propagate first-level uncertainty; sign-flip inference also assumes independent participants and sign-exchangeability under the null. These limitations qualify scope but do not invalidate the stated absence-of-support conclusion.

Evidence inspected: [target analysis report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-17-j01/content/workspace/report/analysis-report.md), `protocol.md`, `analysis/group_analysis.py`, `results/summary.json`, `results/participant_qc.tsv`, `results/analysis_log.txt`, both figures and `input/upstream-methods.md`. Figures clearly show participant variation/uncertainty and the corrected whole-brain findings.

## Delivery integrity and worker attribution

The complete capture manifest reports `capture_status=complete`. Independent verification matched all 1,174 manifest entries and all 58 worker-stop input hashes; there are no delivery mismatches. See [manifest verification](manifest-verification.json). The worker stop receipt records commit `e929d623d8de313d2ecdd97911ea8487077af580`, a normal exit, and no capture omissions. The full stopped workspace includes uncommitted/untracked analysis, report, protocol, figures and results; these are valid scientific artifacts for this assessment, but they were not version-controlled at worker stop. The 54 source maps were present as annex-backed supplied inputs; this records their delivered organization, not authorship or publication by the worker.

No worker remote is configured in captured `.git/config`, and the documentation declares no route for retrieving the complete analysis object. `input/sources.json` names upstream input URLs only. Browser checks of the NeuroVault collection/image and pinned GitHub metadata URLs returned fetcher errors/cache miss; these do not establish remote unavailability. No recipient-side route covering the full code, report, figures, results, inputs and environment was verified. See [access record](access-record.json). Coordinator delivery is not counted as worker publication or sharing.

## Replay and measurement limits

Replay status is **not checked**. The documented command uses a coordinator-side absolute Python path outside the delivery, and the worker supplied no lockfile, package manifest or container definition from which to reconstruct the environment. I did not substitute the assessor or coordinator environment. No replay attempt was made and shipped results are not replay evidence. The intended generated-output selection and comparison rule are recorded in [replay record](replay-record.json).

An initial manifest-check script used the wrong relative root and reported false missing paths. The corrected check used the manifest directory as its base and verified the full capture with zero mismatches. The failed attempt is retained in [assessment-attempts](assessment-attempts.json); it did not alter the target or affect the final integrity result.

## STAMPED checklist

Verdicts assess the frozen checklist 0.3.1 against the worker stop state. The scripted probes inspect recognized Git-tracked paths and miss some complete-delivery material; items 004, 007, 008, 009 and SHOULD 001 were judged against the full capture and flagged where probe output was overridden. `not-checked` remains distinct from `unmet`.

- **MUST:** 4 met / 4 partial / 9 unmet / 0 not-checked (17 items).
- **SHOULD:** 0 met / 2 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 items).
- **MAY:** 3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable (5 items).

The principal gaps are the absent worker-supplied environment specification and dependency update process, untracked analysis/report/results at stop, and no complete-object retrieval route. The response contains an evidence citation for every item verdict.

### Per-item verdicts

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md` | Complete delivery is under one workspace root, including code, inputs, reports, results and retained annex objects. |
| must/002 | S.1 | met | judgement | `input/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/manifest-verification.json` | All 54 maps and metadata are supplied under input/; their retained annex targets resolve within the delivery. |
| must/003 | S.1 | unmet | judgement | `analysis/group_analysis.py`, `README.md` | group_analysis.py imports external Python packages, but the delivery has no environment specification or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `analysis/group_analysis.py`, `report/analysis-report.md` | Git tracks supplied inputs, but the analysis code, protocol, report, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/manifest-verification.json` | All 54 large maps are annex-backed, and captured annex payloads match the worker-stop hashes. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/run_history.md`, `results/summary.json`, `README.md` | Run notes name a command and package versions, but do not identify a supplied exact environment specification for these outputs. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | README documents use and links the report, but offers no way to obtain or install its externally located runtime. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `analysis/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | README gives a starting command for the delivered analysis/group_analysis.py entry point. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `README.md`, `analysis/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | The documented command hardcodes a host-specific absolute interpreter path, although script data paths are relative. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | The script imports NumPy, NiBabel, pandas, SciPy, Nilearn and Matplotlib; no delivered environment declares these dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md`, `results/summary.json` | The external interpreter path is host-specific; the delivery does not document a portable host setup or its system requirements. |
| must/012 | P.2 | unmet | probe:env-spec-tracked+judgement | `README.md`, `analysis/group_analysis.py` | No installable dependency or system-requirement list accompanies the documented execution route. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `README.md` | No environment specification is present in the complete stopped workspace. |
| must/014 | P.3 | unmet | judgement | `README.md`, `analysis/group_analysis.py` | No environment specification or dependency-update command/process is supplied. |
| must/015 | D.1 | unmet | probe:env-spec-tracked+judgement | `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | Package versions are listed, but no lockfile or frozen environment specification is delivered. |
| must/016 | D.1 | unmet | judgement | `.git/config`, `README.md` | No worker publication route or environment artifact is recorded; .git/config has no remote, and coordinator delivery is not worker access. |
| must/017 | D.1 | unmet | judgement | `README.md`, `results/summary.json` | README names an external absolute interpreter path but gives no route to obtain the environment specification. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `analysis/group_analysis.py`, `report/analysis-report.md` | One Git repository contains source inputs, while the analysis code and remaining scientific deliverables were untracked at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `results/run_history.md` | Run history records a replay, but regular testing frequency or an ongoing repeated-test process is not established. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `protocol.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | Inputs, analysis, results, figures and report are in separate directories; no environment component is supplied. |
| should/004 | E.1 | unmet | judgement | `results/run_history.md`, `README.md` | Run history describes replay in the same environment; no fresh container, VM, batch job or cloud run is recorded. |
| should/005 | E.1 | unmet | judgement | `README.md`, `results/run_history.md` | The documented workflow reuses a long-lived default environment path and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `results/run_history.md`, `README.md` | No exact environment specification exists to test for reconstitution; the recorded replay reused the same external environment. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json`, `README.md` | The delivery contains no archived environment, executable package set or container image. |
| should/008 | D.2 | unmet | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | No dependency-update process is declared or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivery identifies no restricted data or software component; its source maps are public NARPS derivatives. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-17/judgments/narps-neutral-r1-17-j01/attempt-01/judgment/2026-10-16-probes.json` | N/A: there are no independently maintained project components; runtime packages are dependencies, and input maps are internal annex content. |
| may/002 | M.2 | met | judgement | `README.md`, `protocol.md` | Protocol and README explain the input, analysis, result and figure relationship and link the main report. |
| may/003 | M.2 | partial | judgement | `protocol.md`, `analysis/group_analysis.py`, `README.md` | Input/code/output directories are separated, but the missing environment and untracked code weaken independent updates. |
| may/004 | M.2 | met | judgement | `analysis/group_analysis.py`, `README.md` | The analysis script composes the workflow by reading input/ and writing named files under results/ and figures/. |
| may/005 | M.2 | met | judgement | `README.md`, `protocol.md` | README links the report and protocol and identifies the directories holding code, results and figures. |


### Flagged items

- `must/004`, `should/001`: the tree-clean probe sees untracked paths; complete capture proves analysis and results exist, so Git use is partial rather than absent.
- `must/007`: the entry-point probe missed the untracked README; instructions exist but lack environment acquisition/installation.
- `must/008`: the entry-point probe missed the untracked script and README; a documented main script exists.
- `must/009`: the probe scanned only tracked text and missed the README's host-specific absolute interpreter path.
- `must/014` and `should/008`: duplicated checklist question; both use the same evidence by design.

### Not checked

- `should/002`: the worker history records a rerun, but does not establish regular testing or an ongoing cadence. A scheduled/manual testing record would settle it.
- Access to the full object: no worker-declared authorized route exists to test. A route with the stated artifact coverage would settle this.
- Scientific replay: not attempted because no worker-supplied environment specification supports the documented external interpreter command.

## Assessment files

- [Response JSON](2026-10-16-response.json)
- [Probe output](2026-10-16-probes.json)
- [Checklist URL](2026-10-16-url.txt)
- [Scientific assessment JSON](scientific-assessment.json)
- [Access record](access-record.json)
- [Replay record](replay-record.json)

Assessment stamp: frozen `assess-alignment-with-stamped-principles` 0.1.0 / `stamped-conventions` 0.2.0, checklist 0.3.1; pinned external assessment runner/runtime passed its version check. Object commit `e929d623d8de313d2ecdd97911ea8487077af580`, captured 2026-10-16T06:38:30.918918+00:00; capture manifest SHA-256 `5dd86ac67e52dd77cb1d69b913060eb4c644b88d9dcf50d577a18967fee0fc22`. Report is based on the complete captured stop state, not the commit alone.
