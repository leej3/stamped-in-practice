# STAMPED and scientific assessment

**MUST:** 7 met / 8 partial / 2 unmet / 0 not-checked / 0 not-applicable (17). **SHOULD:** 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9). **MAY:** 2 met / 2 partial / 1 unmet / 0 not-checked / 0 not-applicable (5). There is no overall score.

## What to fix first

1. Track the exact Pixi lock used for results, document how to update it, and link it from a run record. This closes the main environment/provenance gaps for this study (must/006, must/014, must/015, should/006, should/007, should/008).
2. Publish one exact reproduction command and explain how to install Pixi and obtain the environment. The report's duct-wrapped command differs from the worker run record's direct Pixi command, which makes the starting route ambiguous (must/007, must/008, must/011, must/012, must/017).
3. State a researcher-accessible annex route alongside the Git URL and verify the result payloads from a separate recipient clone. The code revision and all source maps are retrievable; the public GitHub clone cannot retrieve an annexed result file (must/016).
4. Add a CI or equivalent clean-environment check and retain a successful run against the exact locked environment (should/002, should/004, should/006).

## What the project already does well

- Keeps report, analysis, inputs, results, logs, and `pixi.toml` under one root. Large maps and binary results use git-annex; the probes found 57 annex pointers and no oversized Git text blobs (`.gitattributes`, `input`, `analysis`, `results`, `pixi.toml`; [probes](2026-10-16-probes.json)).
- Checks each input image against a byte count and SHA-256 manifest, validates participant identities and image grids, records the common support, and reports all 54 participants with no exclusions (`analysis/run_group_analysis.py`, `results/participant_qc.tsv`, `results/run_summary.json`).
- Gives an interpretable scientific report with participant-level effects, confidence intervals, corrected whole-brain maps, figures, and explicit caveats about upstream modeling and gain scaling (`REPORT.md`, `results/figures/`).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md`, `pixi.toml`, `analysis and input directories` | One repository root contains the report, code, inputs, results, logs, and environment spec. |
| must/002 | S.1 | met | judgement | `analysis/run_group_analysis.py`, `input/sources.json` | The required maps and metadata are within the root and the analysis resolves them by relative paths. |
| must/003 | S.1 | met | judgement | `analysis/run_group_analysis.py`, `pixi.toml` | All imported analysis software is declared in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/worker-end-state.json`, `git status --porcelain` | Git tracks the committed code, report and configuration; the worker receipt records a clean stop at this commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, ` .gitattributes` | Git-annex tracks large maps and binary results; 57 annex objects are represented at the target. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `logs/group-final-validated-2026.10.15T23.24.54-85960_info.json`, `results/run_summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/worker-end-state.json` | Run logs and software versions exist, but no exact environment lock is linked to the result run. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md#Reproducibility`, `logs/group-final-validated-2026.10.15T23.24.54-85960_info.json`, `pixi.toml` | REPORT.md shows a vague duct-wrapped command; the run record used pixi run python directly, and setup instructions are absent. |
| must/008 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md#Reproducibility`, `logs/group-final-validated-2026.10.15T23.24.54-85960_info.json`, `analysis/run_group_analysis.py` | The main script exists, but REPORT.md and the run record give different commands, leaving the reproducible starting route ambiguous. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths | `analysis/run_group_analysis.py`, `results/run_summary.json` | The analysis uses relative paths, but a shipped run summary records a worker-home Python path. |
| must/010 | P.1 | met | judgement | `analysis/run_group_analysis.py`, `pixi.toml` | The imports and invoked analysis tools are declared in pixi.toml; version pinning is a separate gap. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `REPORT.md#Reproducibility`, `pixi.toml`, `no Pixi installation requirement is stated` | Pixi must be installed on the host; platform targets are listed, but host setup assumptions are incomplete. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `REPORT.md` | Python dependencies and supported platforms are listed, but the host Pixi requirement and installation steps are not. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | The Pixi environment specification is versioned with the analysis. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log -- pixi.lock` | No reproducible environment update command or tracked lock-update process is documented. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/worker-end-state.json`, `.gitignore` | The exact package lock used for results is not tracked or preserved at worker stop. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/judgment/remote-verification/github`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/judgment/remote-verification/neurovault/retrieval-report.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/judgment/records/github-annex-output-get.stdout` | The exact Git revision and all 54 input maps are retrievable, but annexed result artifacts lack a verified researcher route. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:fresh-rerun+judgement | `REPORT.md#Reproducibility`, `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The report gives a run command, but does not explain how to install Pixi or obtain a frozen environment. |
| should/001 | T.2 | met | judgement | `git ls-files`, `.gitattributes` | Git and git-annex jointly version code, metadata, and large content in this one repository. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI configuration or scheduled workflow tests the reproduction instructions. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `analysis`, `results`, `pixi.toml` | Input data, analysis code, results, and environment spec occupy distinct paths. |
| should/004 | E.1 | not-checked | probe:fresh-rerun+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/judgment/2026-10-16-fresh-rerun.json`, `logs/group-final-validated-2026.10.15T23.24.54-85960_info.json` | The only clean-clone attempt stopped before analysis because the runner removed input/participants.tsv; a valid fresh-environment replay would settle this. |
| should/005 | E.1 | unmet | judgement | `REPORT.md#Reproducibility`, `Pixi project environment persists under .pixi` | Pixi uses a persistent local project environment rather than creating a disposable environment for each run. |
| should/006 | D.2 | unmet | probe:ci-present+probe:fresh-rerun | `probe:ci-present`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/judgment/2026-10-16-fresh-rerun.json` | There is no successful routine reconstruction test for the environment; the only clean-clone attempt was blocked before execution. |
| should/007 | D.2 | unmet | judgement | `.gitignore`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/worker-end-state.json` | No environment image or frozen package artifact is archived; pixi.lock is ignored and absent from the worker stop inventory. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log -- pixi.lock` | No environment update process is documented or tracked; this duplicates must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `pixi.toml` | N/A: documented public participant maps and ordinary open-source dependencies leave no restricted component to isolate. |
| may/001 | M.2 | unmet | judgement | `.gitmodules`, `input/data` | External maps are stored as annexed files, not linked as submodules or subdatasets. |
| may/002 | M.2 | partial | judgement | `REPORT.md`, `no architecture or module-composition guide` | The report points to code and results, but does not explain module relationships or how to recombine them. |
| may/003 | M.2 | partial | judgement | `input, analysis, results, pixi.toml`, `REPORT.md` | Input, code, results, and environment are separated, but interfaces and independent update rules are undocumented. |
| may/004 | M.2 | met | judgement | `analysis/run_group_analysis.py`, `pixi.toml` | The script composes input, analysis, environment, and result paths through a repository-root-relative workflow. |
| may/005 | M.2 | met | judgement | `REPORT.md` | The report links the analysis script and result figures, giving readers a map of the study outputs. |

## Flagged items

- **must/006:** The probes did not recognize the retained `logs/*_info.json` run record; inspection found the run command and host, but not an exact locked environment. The result is partial.
- **must/007 and must/008:** The entry-point probe only searched README/Makefile patterns and missed `REPORT.md` and the analysis script. The judgment still found a documentation/run-record disagreement: `REPORT.md` gives a vague `pixi run duct ... pixi run python ...` command, while the worker log records `pixi run python analysis/run_group_analysis.py`.
- **must/015:** The environment probe reported not-checked because it did not recognize the named environment; `pixi.toml` is present, but the worker-stop inventory and `.gitignore` show no tracked lock. The status is unmet.
- **must/017:** The fresh-rerun probe failed, but its runner removed `input/participants.tsv` before execution. The partial verdict here rests on missing environment setup documentation, not on that induced failure.
- **should/004:** The probe's unmet result was changed to not-checked. The replay did not reach the analysis because the runner removed an input table, so it cannot establish whether the project succeeds in a clean environment.
- **should/008:** This duplicates must/014 verbatim in the pinned checklist; it carries `upstream-duplicate` by design.

## Not checked

- **should/004:** A valid fresh-environment replay with `input/participants.tsv` preserved would settle whether the pipeline works in a clean environment. The single authorized attempt was used and retained; it was not repeated.

## Goals and kind

**Assumption (not confirmed with a human):** This is a **study** whose goal is to test the positive gain-effect hypothesis for vmPFC in the supplied equal-indifference cohort using the fixed 54 participant maps. The assumption comes from the retained coordinator brief, `input/study-task.md`, and `REPORT.md`. All seven STAMPED principles apply, with particular attention to complete provenance, environment pins, and data access. No treatment assignment was inferred or reported.

## Scientific adequacy: qualified

The analysis provides a defensible group-stage test of the supplied scientific question. It includes all 54 listed participants, verifies input checksums and geometry, tests the positive direction, and uses 10,000 one-sample permutations with voxelwise maximum-t family-wise correction over the common nonzero mask. The independently specified 10 mm MNI sphere centered at [0, 46, -6] localizes vmPFC; inference remains whole-brain corrected, as required by the NARPS instructions.

There is **no whole-brain-corrected positive support in vmPFC**: the sphere's largest statistic is t = 1.30 with max-t FWE p = 1.00; its mean effect is -0.011 (95% t interval [-0.041, 0.018]). Twenty-four corrected voxels form three small foci outside the vmPFC sphere. This supports the report's conclusion that these data do not provide corrected support for the predicted vmPFC response. It does not establish a zero effect or rule out a modest effect.

The report appropriately explains that map values are participant contrast estimates, not standardized statistics or currency-unit slopes: the gain regressor was normalized upstream, gain and loss were modeled separately, and the upstream choices are fixed. The group analysis weights participants equally because variance maps are absent. The permutation test assumes a symmetric null. The common nonzero intersection is a reasonable way to avoid using uncovered zeros as observations, but no separate coverage masks were supplied to distinguish all in-brain exact zeros from missing coverage. The evidence therefore answers the group question conditionally on those fixed maps and assumptions, not on a re-estimated first-level model. See `REPORT.md`, `analysis/run_group_analysis.py`, `results/run_summary.json`, and `results/whole_brain_fwe_peaks.tsv`. Source: [NARPS Hypothesis 1 instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

## Retrieval, replay, and worker-stop attribution

**Recipient and routes checked:** a researcher using the repository's GitHub route for code and metadata and the per-image NeuroVault URLs listed in `input/sources.json` for source maps. A no-checkout clone plus checkout retrieved GitHub commit `e2d266ea0ca7cc52e9ecab358e0f5a8c9085f6b9`. Independent HTTP downloads returned 200 and matched expected byte counts and SHA-256 values for all 54 maps (about 96.4 MB; [retrieval report](remote-verification/neurovault/retrieval-report.json)). Host scope was this assessment host. This establishes source-map access and exact Git revision retrieval, not portability.

The public GitHub clone could not retrieve `results/group_mean_effect.nii.gz`; git-annex reported no usable annex remote. The local-source replay did retrieve 57 annex objects via a same-host route recorded in the source checkout's Git configuration, but this does not establish that a researcher can discover and use that route from the published clone. Annexed result artifact coverage is therefore partial; see [retrieval attempt](records/github-annex-output-get.stdout) and the [fresh-rerun record](2026-10-16-fresh-rerun.json).

The only authorized replay used the documented analysis command `pixi run python analysis/run_group_analysis.py` in a separate clone at [replay workspace](replay-workdir/clone). The runner fetched inputs and removed six shipped output candidates, including `input/participants.tsv`, then the entry point exited 1 with `FileNotFoundError` for that missing input. This is a runner-induced limitation, not evidence that the project itself fails. The clone and outputs remain for coordinator preservation. Pixi generated a local `pixi.lock` in that clone; it was not present in the worker-stop inventory and earns no worker credit.

The external worker-end-state receipt records exit code 0, a clean tree, and HEAD at the assessed commit at 2026-10-16 03:30 UTC ([receipt](</Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-05/judgment-01/worker-end-state.json>)). Its supplied SHA-256 matched (`records/receipt-and-task-hashes.stdout`); the retained task brief hash also matched the coordinator digest. This supports credit for committing/tracking the delivered study state. It records 92 indexed paths and no `pixi.lock`. The current public GitHub branch is retrievable at the exact commit, but the receipt does not attribute the remote push or later annex preservation to the worker. Coordinator preservation or uploads after the stop are not counted as worker actions.

The licence probe found no `LICENSE`, `LICENSES/`, `REUSE.toml`, or BIDS License field; reuse terms are unstated. This is an extra finding, not a pinned checklist item.

## Checklist URL and provenance

[Open this assessment in the STAMPED checklist app](2026-10-16-url.txt). The machine-readable answers are in [2026-10-16-response.json](2026-10-16-response.json); scripted probe results are in [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on `https://github.com/leej3/stamped-in-practice/tree/codex/narps-r1-05` at commit `e2d266ea0ca7cc52e9ecab358e0f5a8c9085f6b9`, 2026-10-16, Codex (OpenAI API workspace; model not exposed by harness). Probe output: `2026-10-16-probes.json`.
