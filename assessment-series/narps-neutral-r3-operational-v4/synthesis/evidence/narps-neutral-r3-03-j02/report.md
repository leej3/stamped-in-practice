# Independent assessment: NARPS gain effect in vmPFC

## Identity and scope

This assessment concerns the complete worker stop delivery, canonical capture SHA-256 `accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd`, captured HEAD `82443e43a1171f47c085c5e0fadc9e8132a12053`. The supplied worker-stop receipt records a complete capture with no omissions or errors (receipt SHA-256 `f0e216cddf471b52448636819a8483a4c1f5103967c0f3900711b587ad6cef91`). Evidence key `C` means canonical capture SHA-256 `accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd`; every `content/workspace/...` artifact citation below is relative to that capture.

I assessed the operational copy as the worker delivery. The frozen runner’s probe sweep and one replay were performed in the permitted scope. The replay helper reports no capture issues, and its outputs matched all ten selected shipped outputs exactly. Inspection commands and outputs, probe results, replay plan and record, and access check are retained in this assessment directory. The replay result is assessor evidence only; it does not change worker-stop attribution.

## Scientific assessment

**Scientific adequacy: supported.** The report’s bounded conclusion that the supplied maps do not provide sufficient evidence for the hypothesized positive whole-brain response is supported by an appropriate group analysis and is stated without claiming a true zero effect. The reported hypothesis outcome is: “In the 54-person equal-indifference group, the supplied gain-modulator estimates did **not** support a positive group response in vmPFC.”

The analysis includes all 54 intended participants and checks participant identity, image checksums, finite values, common shape and affine. It uses participant-level cope estimates in a one-sided one-sample t analysis, defines common nonzero coverage to avoid treating outside-coverage zero padding as observations, and controls positive whole-brain familywise error with participant sign-flip max-T permutations. It reports no voxels below FWE p < .05 (maximum t = 0.90; FWE p = 1.00). The independently specified 10-mm vmPFC sphere summary is descriptive, not a confirmatory uncorrected rescue: mean cope −0.0061, 95% t CI [−0.0342, 0.0221]. The report and code explain that copes are not per-currency BOLD slopes, gain and loss were modeled separately, and absent participant variance maps prevent precision weighting. No evidence is offered that the true effect is exactly zero.

The inference is conditional on the supplied upstream model and on independent participants and a symmetric one-sample null for sign flips. The intersection of nonzero support is a pragmatic coverage rule, not an explicit anatomical mask; the report states which voxels were tested and the figure and QC records make the main decisions inspectable. These are limitations, not material inference errors for the bounded conclusion. Replay regenerated all selected results byte-for-byte. Supporting artifacts: `content/workspace/report.md`, `content/workspace/analysis/group_analysis.py`, `content/workspace/input/upstream-methods.md`, `content/workspace/input/participants.tsv`, `content/workspace/input/sources.json`, `content/workspace/results/summary.json`, `content/workspace/results/input_qc.tsv`, `content/workspace/results/participant_summary.tsv`, and both `content/workspace/figures/*.png`.

## STAMPED item attainment

Verdicts refer to the worker’s recorded stop state, not the coordinator’s later preservation. The complete report, script, figures and results are present in the stopped delivery, but Git status at that state shows `analysis/`, `figures/`, `report.md` and `results/` untracked; the captured HEAD tracks the input metadata and 54 annex pointers. Thus Git-annex earns the large-binary item, while the central report and analysis products were not versioned. See the worker state receipt above and captured `content/workspace/.git/config`, `content/workspace/input/sources.json`, and `content/workspace/report.md`.

The key attainment decisions are:

| Item | Verdict | Evidence and reason |
|---|---|---|
| must/001 | met | All project materials are under the workspace root; `content/workspace/input/sources.json`, report and script. |
| must/002 | met | Relative input links point to annex objects within the root; source/checksum mapping is in `content/workspace/input/sources.json`. |
| must/003 | unmet | No environment specification or included external software; the documented Python executable is outside the object in `content/workspace/report.md`. |
| must/004 | unmet | At worker stop, report, code, figures and results were untracked; stop receipt and `content/workspace/.git/config`. |
| must/005 | met | 54 large input maps use Git-annex pointers; `content/workspace/input/sources.json`. |
| must/006 | unmet | Results identify package versions but no exact environment specification links the run to a reconstructable environment; `content/workspace/results/summary.json`, report. |
| must/007 | unmet | No README or Makefile; the report gives a command but no installation instructions. |
| must/008 | met | `content/workspace/report.md` names the analysis script and an invocation that reproduces all outputs. |
| must/009 | met | The script locates inputs and outputs relative to its own path; `content/workspace/analysis/group_analysis.py`. |
| must/010, 013–017 | unmet | No dependency lock, container, environment capture, update process, shared specification or instructions for obtaining one; captured workspace inventory and report. |
| must/011–012 | unmet | Host and dependency requirements are not listed; report relies on a machine-specific absolute interpreter path. |
| should/001 | partial | Git and annex are used for the input module, but worker analysis and generated products were untracked. |
| should/002, 004–008 | unmet or not-checked | No worker CI, recurring reconstitution record, disposable environment or archived environment artifact is documented. The independent replay is not worker practice. |
| should/003 | partial | Inputs, analysis, results and figures have distinct directories, but there is no environment module; report/code and results remain untracked. |
| should/009 | not-applicable | The supplied public, de-identified cohort materials do not identify a restricted-data or restricted-software component. |
| may/001–005 | not-applicable / partial | No separately maintained project modules are declared. The directory layout offers some navigation, but module relationships and composition are not documented. |

The full per-item response and probe evidence are in `response.json` and `probes.json`; the pinned checklist version is 0.3.1. No overall score is assigned.

## Retrieval and access

The intended recipient is a researcher with access to the worker-declared NeuroVault route. The route in `content/workspace/input/sources.json` resolves gain-map URLs under `https://neurovault.org/media/images/4932/`; a HEAD request for the first map returned HTTP 200 from host `neurovault.org`. That tests one representative object and that host at assessment time, not every map or the worker’s historical access. The route covers participant gain maps only. It does not cover the worker’s analysis code, metadata table, figures, results or environment specification. The captured `.git/config` has no publication remote, and no worker-declared complete-project access route was found. Delivery of the stopped workspace by the coordinator is not evidence that the worker published it.

## Replay and integrity

Before replay, `replay-plan.md` recorded the exact entrypoint, prerequisites, ten outputs and comparison rules. The frozen helper made one fresh copy of the complete canonical delivery, removed only those exact generated output files in that copy, disabled original Git hooks through its documented overlay, and ran the worker-documented command with captured inputs. `replay/replay.json` reports return code 0 and all ten outputs identical; no scientific-input retrieval occurred. The maximum-time and 5 GB helper parameters were 7,200 seconds and 5 GB; the adapter performed no prefetch. The helper reports no capture issues. The assessment was limited to the supplied worker delivery and one route check; it did not rerun preprocessing or participant models.

No mismatch was reported by the frozen replay helper. The final operational-copy integrity check is performed by the launcher after this assessment; any inspection-induced annex database metadata is distinguished there from worker evidence.
