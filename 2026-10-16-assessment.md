# STAMPED assessment — NARPS gain-effect study

**MUST:** 11 met / 5 partial / 1 unmet / 0 not-checked (17). **SHOULD:** 2 met / 4 partial / 2 unmet / 0 not-checked / 1 not-applicable (9). **MAY:** 3 met / 2 partial / 0 unmet / 0 not-checked (5).

## What to fix first

1. Publish the exact Pixi lock at a stable, retrievable commit and record that commit with its hash in each run record → makes the recorded environment verifiable and repeatable → must/006, must/015, must/017, should/006, should/007.
2. Add installation and usage instructions in a README or Makefile, including how to obtain the locked environment → gives a new researcher a complete start-to-result route → must/007, must/017.
3. Document a lock regeneration/update command and keep updates in version control → lets dependency changes be reproduced rather than inferred → must/014, should/008.
4. Give replay runs a fresh output prefix or isolated output directory so existing duct logs do not block the documented task → lets a clean clone complete the documented analysis → must/006, must/008, should/004.
5. Verify and record annex publication at worker stop, including all 54 maps and the atlas → establishes retrieval for the intended researcher at the delivery point → must/016.

## What the project already does well

- A focused protocol names the participant-level estimand, exclusions, positive direction, whole-brain maximum-t correction and explicit vmPFC atlas labels (`protocol.md`).
- The report ties together a fixed input manifest, executable code, Pixi task, machine-readable outputs and uncertainty; the `summary.json` records the code commit and lock hash (`results/report.md`, `pixi.toml`, `results/final-v3/summary.json`).
- At worker stop, the supplied receipt records this exact HEAD, an empty Git status, and annex payloads locally present; the current fresh clone also retrieved 115 annex payloads via the hub route (receipt and replay record linked below).

## Scientific adequacy (separate from STAMPED)

**Classification: supported** for the narrow reported conclusion: these data do not support a positive vmPFC response under the specified whole-brain-corrected test. The protocol tests the positive group mean at the participant level (54 independent participants) across the common nonzero support using 5,000 sign flips and a one-sided maximum-t statistic. Support required a positive voxel inside a prespecified Harvard–Oxford vmPFC operationalization to pass whole-brain FWE p < .05. The report finds 0/6,174 vmPFC voxels passing; the descriptive ROI mean is −0.0103 (95% t interval −0.0290 to 0.0084; t(53)=−1.10; one-sided p=.862), with 21/54 positive participant averages. The strongest corrected positive voxel is outside the ROI (MNI [−26, −102, −3.6], mean 0.1121, t=6.62, max-t FWE p=.001). These findings support a lack-of-evidence conclusion at the prespecified threshold; they do not show that the true vmPFC effect is zero or rule out smaller effects.

The analysis uses the supplied gain contrast estimates rather than treating them as standardized statistics or currency-unit slopes. It correctly notes the upstream centered, variance-normalized gain regressor, the separate gain/loss model, and the absence of participant variance maps. The main inferential assumptions are sign-flip exchangeability and approximately symmetric participant errors. The vmPFC mask is a broad, defensible but non-unique set of Harvard–Oxford labels. Nearest-neighbor resampling from MNI152 2-mm atlas geometry to the supplied MNI152NLin2009cAsym maps may move ROI boundaries; the report discloses this limitation. All 54 maps are reported to pass checksums, geometry and finite-value checks, with no exclusions. The 5,000 permutations give minimum Monte Carlo p=.0002. These details make the non-support conclusion defensible, with the stated limits.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-tree -r --name-only HEAD` | All code, data pointers, methods, results, logs, and environment files are nested under the repository root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable | `.gitmodules`, `input/sources.json` | The linked skills module resolves from the root; inputs and outputs are also under the same root. |
| must/003 | S.1 | met | judgement | `pixi.toml` | Python, neuroimaging and execution dependencies are specified in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean+judgement | `git ls-tree -r HEAD`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-10/judgment-01/worker-end-state.json` | Code, text and configuration are Git-tracked; the worker-stop receipt records this exact commit and a clean state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `git ls-tree -r -l HEAD`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-10/judgment-01/worker-end-state.json`, `2026-10-16-fresh-rerun.json` | Git-annex tracks the large binaries; the stop receipt records 107 payload-bearing entries available locally, and the later clone fetched 115 payloads. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `results/final-v3/summary.json`, `results/report.md`, `git ls-tree -r --name-only HEAD` | The run summary links code commit and lock hash, but the exact lock artifact is absent from the worker-delivered tree and cannot be verified here. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `results/report.md#Reproduction record`, `git ls-tree -r --name-only HEAD` | The report gives `pixi run analysis`, but the item’s README or Makefile with installation and usage instructions is absent. |
| must/008 | A.1 | met | probe:entry-point+judgement | `pixi.toml`, `code/analyze.py`, `results/report.md#Reproduction record` | A runnable `analysis` task in Pixi invokes the group analysis script, and the report documents that command. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `code/analyze.py`, `2026-10-16-probes.json` | The analysis resolves project files relative to its repository root; the path probe found no host-specific absolute paths. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `code/analyze.py` | The environment lists the analysis imports and invoked tools, including Nilearn, NiBabel, SciPy and con-duct. |
| must/011 | P.1 | met | judgement | `pixi.toml`, `results/report.md#Interpretation and limits` | The environment declares supported macOS and Linux platforms; the report states replay was same-host and does not claim cross-platform portability. |
| must/012 | P.2 | met | judgement | `pixi.toml` | Pixi specifies Python and package dependencies plus supported platforms for the analysis environment. |
| must/013 | P.3 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `git ls-tree -r --name-only HEAD` | The Pixi environment specification is tracked in Git alongside the analysis code and data pointers. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No documented lock regeneration/update procedure is present; pixi.toml history shows edits but not a stated update process. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `pixi.toml`, `results/final-v3/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-10/judgment-01/worker-end-state.json` | Pixi declarations and a run lock hash are recorded, but the exact lockfile is absent from the delivered object and the referenced snapshot was not independently retrieved. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-10/judgment-01/worker-end-state.json`, `2026-10-16-fresh-rerun.json#local_source_transports`, `input/sources.json` | The current same-host clone fetched all required payloads through the hub, but the worker-stop receipt proves local availability only, not remote annex publication at that time. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:fresh-rerun+judgement | `results/report.md#Reproduction record`, `pixi.toml`, `2026-10-16-fresh-rerun.json` | The report gives the analysis command, but does not document how to obtain the exact locked environment referenced by its run record. |
| should/001 | T.2 | met | judgement | `.gitmodules`, `git ls-tree -r HEAD` | Git is used for the research object and Git-annex and the linked skills submodule also use Git. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `results/replay-validation.json`, `2026-10-16-probes.json` | A successful same-host replay is recorded, but no recurring CI or other regular workflow check is configured. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `code`, `results`, `pixi.toml` | Inputs, code, derived results and environment are kept in distinct directories or files. |
| should/004 | E.1 | partial | probe:fresh-rerun+judgement | `results/replay-validation.json`, `2026-10-16-fresh-rerun.json` | The report records a successful replay in a fresh clone on the same host; no fresh container, VM or batch environment is evidenced. |
| should/005 | E.1 | unmet | judgement | `pixi.toml` | The Pixi task runs in the configured environment; each execution does not create a disposable environment. |
| should/006 | D.2 | partial | probe:ci-present+judgement | `results/replay-validation.json`, `2026-10-16-probes.json`, `2026-10-16-fresh-rerun.json` | A same-host replay of the locked environment is recorded, but the lock is not in the delivered tree and no recurring reconstitution check is configured. |
| should/007 | D.2 | partial | judgement | `pixi.toml`, `git ls-tree -r --name-only HEAD` | The Pixi manifest is tracked, but no exact lock or archived environment artifact is present in the delivered tree. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No dependency-change/lock regeneration process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software is identified; the supplied inputs are retrievable through the declared researcher route. |
| may/001 | M.2 | met | probe:subdatasets-resolvable | `.gitmodules` | The external skills component is linked as a Git submodule. |
| may/002 | M.2 | met | judgement | `protocol.md`, `results/report.md#Reproduction record` | The protocol and report explain the input, analysis and results components and how the analysis connects them. |
| may/003 | M.2 | partial | judgement | `git ls-tree -r --name-only HEAD`, `.gitmodules` | Input, code, environment and output paths are distinct, but they share one repository root and are not independently versioned modules. |
| may/004 | M.2 | partial | judgement | `pixi.toml`, `code/analyze.py`, `.gitmodules` | The Pixi task composes code and project-relative inputs, but there is no module orchestration for the study data or results. |
| may/005 | M.2 | met | judgement | `protocol.md`, `results/report.md`, `input/sources.json` | The protocol, report and source manifest guide users through the data, analysis and outputs. |

## Flagged items

- **must/006 — probe overridden.** The derived-file probe did not recognize the summary and run logs as provenance. They record the analysis and link code commit/lock hash, but the exact lock artifact is unavailable in the delivered tree, so the verdict is partial.
- **must/007 — probe overridden.** The entry-point probe searched for a README or Makefile and missed the Pixi task and report command. The report documents `pixi run analysis`, but the required README/Makefile installation and usage route is absent.
- **must/008 — probe overridden.** The Pixi `analysis` task and `code/analyze.py` provide a reproducible starting point despite the probe’s README/Makefile search.
- **must/010 — probe overridden.** The environment probe’s partial result is driven by the uninitialized skills module; that module is not used by the analysis, and the analysis imports and invoked tools are listed in `pixi.toml`.
- **must/016 — unverified at worker stop.** The current replay retrieved through the hub route, but the worker-stop receipt records local annex availability, not remote payload locations. Later retrieval is not credited as worker-stop publication.
- **must/015 — unverified claim.** The report references a published environment snapshot and the summary gives a lock hash; the referenced exact lock was not independently retrieved from the worker-stop evidence.
- **should/002 and should/006 — probe overridden.** The CI probe found no CI configuration. A successful same-host replay is recorded, supporting partial rather than unmet; it does not establish recurring checks.
- **should/008 — upstream duplicate.** It repeats must/014 by design; both are unmet because no lock-update procedure is documented.

## Not checked

No checklist items remain `not-checked`. The extra `inputs-untouched` probe is not-checkable because the linked skills submodule was not initialized in the assessed checkout. The probe also reports no declared reuse licence (`license-declared`, outside the 31-item checklist); `clone-weight` is met. These extras are recorded in the response JSON.

## Goals and kind

**Assumption (not confirmed; no human attached):** the goal is the coordinator-retained brief supplied in the request (SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`): assess the group analysis from fixed AO86 gain-effect maps for a positive vmPFC response in the equal-indifference cohort. The primary object kind is **study**: it combines data, code, environment, results and scientific interpretation. The supplied brief sets the assessment emphasis; no worker-edited task replacement was used.

## Worker-stop attribution and scope

The external [worker-end-state receipt](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-10/judgment-01/worker-end-state.json) (SHA-256 `e755347d326d37950589af4e25a4ef5c582c7f3b2db8e4ce5455e05ca2c493fe`) records stop at 2026-10-16 04:16:59 UTC, return code 0, HEAD `62d247e48e69978d294dc39175d53f9aa638ce0d`, and an empty status. The requested target HEAD matches; the receipt’s index matches the committed paths. It records 107 of 107 payload-bearing annex entries available locally at stop, with 113 annex pointer paths in the Git tree. The retained target checkout now lacks 101 of those annex payloads locally; its links match the receipt, and the later fresh clone fetched the content. This is the basis for worker version-control assessment. The one formal replay was run afterward in a separate clone on the same host, from the exact local result commit. It fetched 115 payloads (105,288,812 bytes) using the recorded hub Git and annex HTTPS routes, then removed shipped output candidates as required. `pixi run analysis` exited 1 because `con-duct` refused to overwrite four tracked `logs/group-analysis-final-v3-*` files. This verifies current retrieval through that route, not cross-host portability or worker-stop remote annex publication. The clone and all failed replay artifacts remain under `replay-work/`; the assessed checkout was not modified.

The target’s retained report also records an earlier successful same-host replay and output comparison. The worker-stop receipt includes that report and its committed record; later coordinator preservation, publication or environment snapshots were not used to award worker credit. No coordinator guidance beyond the scientific rubric supplied in this task, other workers’ outputs, prior judgments or round summaries were used.

## Checklist URL and provenance stamp

[Open the checklist response URL](2026-10-16-url.txt). The canonical response is [2026-10-16-response.json](2026-10-16-response.json); scripted probes are [2026-10-16-probes.json](2026-10-16-probes.json), and the one-attempt replay record is [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json). Attempt commands, stdout/stderr and response-helper artifacts are under [assessment-attempts/](assessment-attempts/).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-10/targets/judgment-01` at commit `62d247e48e69978d294dc39175d53f9aa638ce0d`, 2026-10-16, Codex API / GPT-6 family (exact runtime variant not exposed). The report and evidence are outside the assessed checkout. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).
