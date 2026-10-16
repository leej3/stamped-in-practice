# Independent assessment — 2026-10-16

MUST: 11 met / 1 partial / 4 unmet / 1 not-checked (17). SHOULD: 1 met / 1 partial / 3 unmet / 3 not-checked / 1 not-applicable (9). MAY: 2 met / 2 unmet / 1 not-applicable (5). No overall score is assigned.

Assessment basis: canonical capture SHA-256 `ce0f53e7851a29789255c124bd60091355202305a3a359e6ccd080f2bf3640b0`, captured 2026-10-16 16:51:22 UTC, original HEAD `d4d11a9c1bd38a9c96b5a4cf0c5403c455f1f96c`. Unless otherwise stated, each evidence citation below means that capture SHA plus the capture-relative path. The worker-stop receipt is SHA-256 `f64892e020611b79834de40eed2802af473323e23ad4fddc25aa50d40772bfcf`. The delivery manifest reports no omissions or errors. The operational manifest had the same 22,612 entries and bytes as the canonical manifest after inspection; no mismatch was detected. Git/probe commands were directed to the operational copy. Their state observations are distinguished from worker actions.

## Scientific assessment

Scientific adequacy: supported — the bounded conclusion of no whole-brain-corrected vmPFC support is supported by the one-sided whole-brain max-t FWE analysis; all reported corrected clusters are posterior, and the descriptive vmPFC interval crosses zero. The report explicitly says this is not proof of no effect or an equivalence test.

Hypothesis conclusion (worker report, verbatim):
> In the 54-person NARPS equal-indifference group, the supplied gain-modulator maps do **not** support a greater response in vmPFC under whole-brain family-wise error (FWE) control.

The worker's `analysis/protocol.md` specifies 54 independent participant effects, one-sided sign-flip max-t FWE over common support and a vmPFC localization rule; `analysis/run_analysis.py` implements the model, image checks, correction and outputs. `results/summary.json` records all 54 participants, no exclusions, 198,029 voxels, 5,000 sign flips, 24 corrected voxels, a peak FWE p=.001, and a descriptive vmPFC proxy mean 0.00563 with 95% interval [−0.0126, 0.0239]. `results/fwe_clusters.tsv` places all three corrected clusters in posterior coordinates (peaks y=−94 to −102 mm), outside vmPFC. `report.md` correctly treats them as unexpected and states that the proxy is descriptive, not a confirmatory ROI test.

The group inference is appropriate conditional on supplied maps: all maps have matching geometry and finite values; participant IDs match the equal-indifference cohort; the common nonzero support avoids treating outside-mask zeros as measured zeros; participant-level sign flips preserve spatial dependence and max-t controls one-sided whole-brain family-wise error. The protocol acknowledges symmetry/exchangeability assumptions and absent participant variance maps. The contrast maps are normalized-modulator coefficients, not per-currency slopes; the report makes that limitation clear. The proxy's interval is descriptive and does not establish equivalence or rule out smaller effects. These limitations qualify interpretation but do not undermine the stated “no support” conclusion. Evidence: canonical capture SHA-256 `ce0f53e7851a29789255c124bd60091355202305a3a359e6ccd080f2bf3640b0` paths `input/upstream-methods.md`, `analysis/protocol.md`, `analysis/run_analysis.py`, `results/summary.json`, `results/fwe_clusters.tsv`, `results/participant_qc.tsv`, `report.md`, and `figures/wholebrain_fwe_peak.png`.

## What to improve first

1. Track the analysis, report, environment declarations and results in the worker's version-control history at stop. They were captured but untracked; this would establish an auditable worker revision (MUST 004/013; SHOULD 001).
2. Add the exact environment-lock identity to each run record. The summary has code/input checksums and package versions, but no lockfile digest or explicit environment identity (MUST 006).
3. Document and test a researcher retrieval route covering the complete workspace, data and environment. No worker-declared route or Git remote was present (MUST 016).
4. Document a dependency update/lock regeneration process and preserve its updates in version control (MUST 014; duplicate SHOULD 008).
5. Add recurring clean-environment checks and decide whether each run should use a disposable Pixi environment. The delivery has one run record and a persistent local environment, but does not establish recurring or fresh-host tests (SHOULD 002/004/005/006).

## What is already strong

- The stopped delivery is complete and self-contained: it includes the 54 maps, cohort metadata, analysis source, Pixi recipe/lock, a local Pixi environment, outputs and figures. The README maps these components and documents the run route (`README.md`, `input/data`, `.pixi/envs/default`, `results/`, `figures/`).
- The scientific protocol is unusually inspectable: it states the estimand, participant-level unit, correction, common-support rule, anatomical interpretation, QC, assumptions and missing upstream variance maps (`analysis/protocol.md`, `input/upstream-methods.md`).
- The report presents corrected whole-brain results and uncertainty while avoiding an equivalence claim (`report.md`, `results/summary.json`, `figures/wholebrain_fwe_peak.png`).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md`, `input/data` | All scientific inputs, code, environment and outputs are under one captured workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `analysis/run_analysis.py`, `input/sources.json` | All supplied maps and metadata are inside the root and the documented script resolves them relative to itself. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `pixi.lock` | Runtime packages are declared in the delivered Pixi environment; their completeness is assessed under must/010. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `analysis/run_analysis.py`, `report.md`, `.git/index` | At worker stop the analysis, documentation, environment spec and results remained untracked in Git. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `input/data`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-02-j01/attempt-01/worker-end-state.json` | The 54 maps are annex-backed, but the stop receipt attributes them as supplied inputs; worker tracking practice is not established. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `results/summary.json`, `analysis/attempts.md` | The run summary records code/input hashes and package versions, but not the exact lockfile or environment identity used. |
| must/007 | A.1 | met | probe:entry-point+judgement | `README.md` | README gives the Pixi installation and run commands plus a contents guide. |
| must/008 | A.1 | met | probe:entry-point+judgement | `pixi.toml`, `analysis/run_analysis.py` | The README names pixi run analyze, which dispatches the analyze task to the group-analysis script. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis/run_analysis.py` | The analysis derives input and output locations from its own path; no machine-specific paths are required. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `pixi.lock` | All imported third-party libraries are declared in pixi.toml and resolved in pixi.lock. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `README.md`, `pixi.toml` | The only declared host prerequisite is Pixi; supported platforms are listed, with no extra mounts, services, variables or hardware assumed. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `README.md`, `pixi.toml` | README names Pixi and the environment spec lists the software dependencies and supported platforms. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `pixi.toml`, `pixi.lock`, `.git/index` | pixi.toml and pixi.lock are captured but were untracked at worker stop, so they were not under version control. |
| must/014 | P.3 | unmet | judgement | `README.md`, `pixi.toml` | No dependency-update or lockfile-regeneration process is documented. |
| must/015 | D.1 | met | probe:run-env-linked+judgement | `pixi.lock`, `pixi.toml` | A complete Pixi lockfile and environment recipe are included in the stopped delivery. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `README.md`, `.git/config` | No worker-declared authorized retrieval route or Git remote is present; coordinator delivery does not establish worker sharing. |
| must/017 | D.1 | met | judgement | `README.md`, `pixi.toml` | README explains how to use the supplied environment specification to install and run the workflow. |
| should/001 | T.2 | unmet | judgement | `analysis/run_analysis.py`, `input/data` | Inputs are annex-backed, but worker analysis, documentation, environment and results were untracked at stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `analysis/attempts.md`, `probe:ci-present` | One accepted run and failed development attempts are recorded, but regular testing is not established. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `README.md`, `analysis/run_analysis.py` | README and directories separate inputs, analysis, results/figures and environment, but these are not independently updateable modules. |
| should/004 | E.1 | not-checked | judgement | `analysis/attempts.md`, `fresh-rerun.json` | The recorded accepted run does not identify a fresh environment; the sole assessor replay did not reach the entrypoint. |
| should/005 | E.1 | unmet | judgement | `.pixi/envs/default`, `README.md` | The delivered Pixi environment is persistent under .pixi/envs/default; each run does not create a disposable environment. |
| should/006 | D.2 | not-checked | probe:ci-present+judgement | `analysis/attempts.md`, `pixi.lock` | The captured run and lock are present, but recurring environment reconstitution tests are not demonstrated. |
| should/007 | D.2 | met | judgement | `.pixi/envs/default`, `pixi.lock` | The complete local Pixi environment binaries are archived inside the captured workspace. |
| should/008 | D.2 | unmet | judgement | `README.md`, `pixi.toml` | No process for updating dependencies or tracking lockfile changes is stated. |
| should/009 | M.4 | not-applicable | judgement | `input/upstream-methods.md`, `pixi.toml` | N/A: supplied NARPS materials and declared software show no restricted component requiring a separate module. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `README.md`, `.git/config` | N/A: the workspace has no independently maintained project components; runtime packages are dependencies, not project modules. |
| may/002 | M.2 | met | judgement | `README.md` | README explains the roles of input, code, results, environment and report/figures. |
| may/003 | M.2 | unmet | judgement | `analysis/run_analysis.py`, `README.md` | Directory roles are clear, but components share one repository and the script couples input, analysis and output paths. |
| may/004 | M.2 | unmet | judgement | `pixi.toml`, `README.md` | There is no module composition mechanism; one Pixi task launches one script over the workspace. |
| may/005 | M.2 | met | judgement | `README.md` | README provides a contents guide linking the report, protocol, analysis code, results and figures. |

## Flagged items

- **MUST 002:** the probe's “no submodules” route missed that the maps and metadata are captured inside `input/`; the item concerns whether data are reachable within the boundary.
- **MUST 005:** the annex probe correctly identifies the 54 pointers, but the worker-stop receipt attributes them as supplied inputs. This does not establish worker tracking practice, so attainment remains not-checked.
- **MUST 006:** the run-record probe did not recognize `results/summary.json` and `analysis/attempts.md`; those records provide partial runtime provenance but omit the lock identity.
- **MUST 007/008:** the tracked-path probes missed the README and entrypoint because they were untracked at stop; the complete captured workspace includes both.
- **MUST 010:** the environment probe only accepted tracked specifications; the complete stopped delivery contains a lock/recipe, and the declared imports are present there.
- **MUST 015:** the probe mapped recognized run records to whether an exact environment spec exists. The Pixi lock and recipe are included in the complete delivery.
- **MUST 016:** the probe mapped a tracked environment file to sharing. Sharing was judged from the README and captured Git config; neither declares an authorized route.
- **SHOULD 003:** the folder probe sees only a separate input area. The README also separates analysis, results/figures and environment by directory, but these do not form independently updateable modules.
- **SHOULD 008:** duplicates MUST 014 by checklist design; its answer repeats that finding.

## Not checked and replay

- **MUST 005:** Annex-backed map storage is present in the object, but the supplied-input attribution prevents worker-practice credit; worker-originated data versioning would settle this.
- **SHOULD 002/004/006:** the capture does not establish regular workflow tests, a fresh-host run, or repeated environment reconstitution. The sole permitted assessor replay did not start the target entrypoint.
- **Replay record:** `fresh-rerun.json` records the sole attempt. The assessor setup precreated the workdir; the frozen helper then failed with “Materialization requires a new destination.” No target command ran, no outputs were removed from a replay copy, and no scientific replay result is claimed. The attempt log is `commands/replay-attempt.txt`; the predeclared command and comparison are in `replay-plan.md`. The one-attempt limit was observed.

## Attribution, access and scope

The README describes a study analysis; I assume the project kind is **study**, with the goal of group-stage inference on the supplied 54 participant maps. This assumption follows `README.md`, `analysis/protocol.md` and `report.md`; no human clarification was attached. The receipt identifies the worker as exited normally and the capture as complete. The captured HEAD contains the supplied input commit, while the worker analysis, documentation, Pixi files, results and figures are untracked in the stop state. Coordinator preservation and assessor delivery do not earn worker versioning or publication credit. The maps were already annex-backed as supplied resources. The captured local `.pixi/envs/default` environment is present in the stop state; the receipt's supplied-file list does not attribute it as a supplied input.

For access, the intended recipient is a researcher using the worker's declared authorized route. No such route is declared in the README and the captured `.git/config` has no remote. Required coverage is the complete workspace, including map payloads, metadata, code, environment recipe/lock and environment binaries, report, results and figures. No host scope could be tested. Coordinator delivery to the assessor is not evidence of worker-side availability. Details are in `access-record.json`.

The capture's reference limits prohibit following the retained external skill links; they were not followed. The committed metadata includes a Codex Desktop co-author attribution, which reveals assistance; I record this exposure without using it as grading evidence. No treatment assignment was inferred or reported.

One extra item has no STAMPED id: reuse/license terms are not declared in the complete workspace. The frozen probe also reported no license declaration. Probe output is preserved in [`2026-10-16-probes.json`](2026-10-16-probes.json).

Checklist URL: [`2026-10-16-url.txt`](2026-10-16-url.txt). Machine-readable checklist: [`2026-10-16-response.json`](2026-10-16-response.json). Scientific judgment record: [`scientific-judgment.json`](scientific-judgment.json). Replay plan and record: [`replay-plan.md`](replay-plan.md), [`fresh-rerun.json`](fresh-rerun.json).

Stamp: frozen assessor 0.1.0 / `stamped-conventions` 0.1.0, checklist 0.3.1, Codex API / GPT-6 (runtime variant not exposed), 2026-10-16. Original capture SHA-256 `ce0f53e7851a29789255c124bd60091355202305a3a359e6ccd080f2bf3640b0`; original HEAD `d4d11a9c1bd38a9c96b5a4cf0c5403c455f1f96c`. Probe output: `2026-10-16-probes.json`.
