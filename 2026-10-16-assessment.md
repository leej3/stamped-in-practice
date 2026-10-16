# STAMPED assessment — NARPS potential-gain study

**MUST:** 8 met / 2 partial / 6 unmet / 1 not-checked (17 total). **SHOULD:** 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 total). **MAY:** 1 met / 2 partial / 2 unmet / 0 not-checked / 0 not-applicable (5 total). No overall score is assigned.

Scientific adequacy is assessed separately in [the scientific assessment](./2026-10-16-scientific-assessment.md).

## What to fix first

1. Track a resolved environment lock and a command for updating it, and include that environment identity in each run record. This closes the main traceability and rebuild gaps (must/006, must/014, must/015; should/006, should/008).
2. Add concise setup and use instructions, including the Pixi bootstrap, supported host platforms and first-run network access for Nilearn atlases/templates (must/007, must/011, must/012, must/017).
3. Preserve a time-stamped worker release inventory for Git-annex availability. A same-host clone retrieved all current content, but the worker-stop receipt does not record annex availability (must/016).

## What the project already does well

- It keeps all 54 input maps inside the object, verifies each source hash, checks common image geometry and finite values, and uses the complete participant intersection mask (`analysis/run_group_analysis.py`, `input/sources.json`, `results/map_quality.tsv`).
- The analysis script and report are committed with interpretable tables, maps and figures (`analysis/run_group_analysis.py`, `results/report.md`, `results/group_results.json`).
- Git-annex carries 58 large objects. At assessment, a Datalad clone at the assessed commit retrieved all 54 maps and 4 annexed results; all map hashes matched the source manifest (`records/remote-get.stdout`, `records/remote-integrity.stdout`).

## Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/run_group_analysis.py` | Required Harvard-Oxford atlas and MNI template are fetched outside the root at runtime. |
| must/002 | S.1 | met | judgement | `input/data` | All 54 input maps, metadata and their source manifest are under input/ and read by root-relative paths. |
| must/003 | S.1 | met | judgement | `analysis/run_group_analysis.py` | All analysis software imports are declared in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-01/worker-end-state.json`, `git status at target` | Git tracks the committed code and records; worker receipt shows the stop tree was clean. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex` | Large maps and binary results use git-annex; the published clone retrieved all annex content. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/group-analysis-final-info.json` | Run records exist, but none names the exact environment; pixi.lock is ignored and absent. |
| must/007 | A.1 | unmet | probe:entry-point | `probe:entry-point` | No README or Makefile gives installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md#Reproducibility and files` | The report links the runnable main script and the recorded command invokes it. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | Tracked code uses root-relative paths and the probe found no host-specific paths. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `analysis/run_group_analysis.py` | Every Python import used by the analysis is declared in pixi.toml. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `analysis/run_group_analysis.py` | Runtime network access is required to fetch the atlas and template, but host requirements are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml` | pixi.toml lists packages and platforms, but omits Pixi bootstrap and runtime network requirements. |
| must/013 | P.3 | met | probe:env-spec-tracked | `probe:env-spec-tracked` | pixi.toml is tracked alongside the code and results. |
| must/014 | P.3 | unmet | judgement | `pixi.toml` | No dependency update or environment regeneration process is documented. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml` | The environment specification is mutable and no exact lock or archived environment is included. |
| must/016 | D.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-01/judgment/records/remote-get.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-01/worker-end-state.json` | Current same-host HTTPS retrieval succeeds, but the worker-stop receipt lacks annex locations; stop-time publication cannot be established. A time-stamped worker remote inventory would settle it. |
| must/017 | D.1 | unmet | judgement | `pixi.toml` | No documentation explains how to install or use the environment specification. |
| should/001 | T.2 | met | judgement | `git ls-files` | Git and git-annex version code, data, results and configuration under one repository boundary. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI configuration or recurring workflow tests the documented procedure. |
| should/003 | M.1 | met | probe:modules-separated | `probe:modules-separated` | Inputs, analysis code, outputs and environment are separated in the project layout. |
| should/004 | E.1 | not-checked | judgement | `2026-10-16-fresh-rerun.json` | Fresh replay could not reach analysis: the runner removed input/participants.tsv as an output; a clean successful test would settle this. |
| should/005 | E.1 | unmet | judgement | `logs/group-analysis-final-info.json` | pixi run reuses a project-local environment; no per-execution disposable environment is defined. |
| should/006 | D.2 | unmet | probe:ci-present | `probe:ci-present` | No recurring test reconstitutes the exact environment; no lock is tracked. |
| should/007 | D.2 | unmet | judgement | `pixi.toml` | The object tracks an environment recipe but archives no resolved environment or executable image. |
| should/008 | D.2 | unmet | judgement | `pixi.toml` | No dependency update process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the input maps and code have no restricted-access component. |
| may/001 | M.2 | unmet | judgement | `analysis/run_group_analysis.py` | External atlas data and software are fetched or installed, but no external component is linked as a submodule. |
| may/002 | M.2 | partial | judgement | `results/report.md#Reproducibility and files` | The report identifies code and result files, but does not explain how the components are recombined. |
| may/003 | M.2 | partial | judgement | `analysis/run_group_analysis.py` | Inputs, code and results are separated, but paths and source hashes tie them to the current root layout. |
| may/004 | M.2 | unmet | judgement | `pixi.toml` | No documented composition workflow joins inputs, environment and analysis. |
| may/005 | M.2 | met | judgement | `results/report.md#Reproducibility and files` | The scientific report lists and links the code, result tables, maps and figures. |

## Flagged items

- **must/006 — mapping questioned:** the probe reported no run record. Run records are present, but they do not name the exact environment; `pixi.lock` is ignored and absent.
- **must/008 — probe overridden:** the entry-point probe missed `analysis/run_group_analysis.py`, which has a main guard and is linked from the report; the run record gives its command.
- **must/010 — probe overridden:** the probe left dependency completeness unchecked; inspection confirmed all Python imports in the analysis are declared in `pixi.toml`.
- **must/011 and must/012 — judgement applied:** the command scan could not assess documented host requirements. The analysis downloads an atlas and template at runtime, while setup and network requirements are not documented.
- **must/015 — probe overridden:** although the probe found no recognized environment pin, direct inspection confirms `pixi.toml` is unlocked and `pixi.lock` is not tracked.
- **should/008 — upstream duplicate:** this repeats must/014 word for word; its answer is intentionally the same.

## Not checked

- **must/016:** complete content retrieval succeeded at assessment, but the worker-stop receipt does not record a time-stamped annex inventory. Stop-time publication cannot be attributed without that evidence.
- **should/004:** the single authorized replay did not reach analysis. The runner removed `input/participants.tsv` as a shipped output before launching the entry point. A successful fresh run with that input retained would settle this; no second attempt was made. See [the replay record](./2026-10-16-fresh-rerun.json).

## Extra finding

The license probe found no license declaration among tracked files (`2026-10-16-probes.json`, `license-declared`). The checklist has no licensing item; reuse terms are therefore unstated.

## Goals and kind

**Assumption (not confirmed by a human):** this is a **study** whose product is a group-level answer to the supplied NARPS Hypothesis 1 question, using the fixed 54 participant gain-effect maps (`input/study-task.md`, `input/upstream-methods.md`). The study emphasis is on linked inputs, recorded derivations, actionable instructions, explicit environments and retrieval of the complete object.

The retained task and participant metadata expose cohort labels and participant characteristics, so assessor blinding cannot be established. No treatment assignment was inferred or reported, and this limitation was not used as grading evidence.

## Access and worker-stop attribution

The intended recipient is a researcher using the Git-annex/Datalad route exposed by the configured HTTPS hub remote. A same-host fresh clone checked out `a424c3e8ae47f9208fa661fc4f974f6b187acb00`; `datalad get -r input/data results` retrieved 58 annex files (54 input maps and 4 result files), and all map hashes matched `input/sources.json`. Other committed files were available as Git blobs. This checks the current retrieval route on the same host; it does not establish cross-host portability. Access is verified now, but worker-stop publication is not established from the receipt.

The external worker-end-state receipt (SHA-256 `c412bb1e086138c7b6e914bff36d5f204221ca3d98a75e46b1e36fbf57d254f7`) records the same HEAD and an empty worktree at worker exit. It supports credit for the worker's committed, tracked state. Annex publication at the stop cannot be attributed from that receipt. Current remote retrieval and preservation are reported separately.

## Checklist URL and stamp

[Open the completed checklist](./2026-10-16-url.txt). The machine-readable answers are in [2026-10-16-response.json](./2026-10-16-response.json), validated with the supplied runner against checklist 0.3.1.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad237fa57b856417db8dba45a1b283a527`), on `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git` at commit `a424c3e8ae47f9208fa661fc4f974f6b187acb00`, 2026-10-16, Codex API / model identifier not exposed by the harness. Probe output: [2026-10-16-probes.json](./2026-10-16-probes.json). Replay output: [2026-10-16-fresh-rerun.json](./2026-10-16-fresh-rerun.json).
