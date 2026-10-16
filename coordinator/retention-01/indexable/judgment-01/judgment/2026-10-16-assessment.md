# STAMPED and scientific assessment

Assessed the committed study at `32d9cabf7b5d041f9efb97830bf5279068809357` on 2026-10-16 UTC. The target HEAD was verified before inspection. The retained task brief hash matches the supplied SHA-256. No files in the assessed checkout were changed.

## STAMPED verdict

MUST: **10 met / 3 partial / 4 unmet / 0 not-checked** (17 items). SHOULD: **2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable** (9 items). MAY: **3 met / 1 partial / 1 unmet** (5 items). `partial` does not satisfy a MUST. No overall score is assigned.

## What to fix first

1. Commit a resolved `pixi.lock` and link its hash to each run record → the analysis results cannot currently be tied to an exact environment (must/006, must/015, should/006).
2. Add a root `README.md` with Pixi installation, supported host requirements, environment setup, and the existing run command → the report has a runnable command but not a complete setup route (must/007, must/011, must/012, must/017).
3. Document and track the command for updating dependencies and the lockfile → environment changes currently have no reproducible update process (must/014, should/008; these checklist items are duplicates).
4. Correct fresh-rerun cleanup so it does not remove required inputs → the sole replay stopped before analysis; a future assessment could verify successful fresh execution (should/004, currently not-checked).

## What the project already does well

- Git tracks the complete project tree and git-annex carries the 54 participant maps plus the unthresholded group map; an independent retrieval clone verified the annex content (`.gitattributes`, `input/data/`, retrieval record below).
- The report states the group model, positive direction, 9,999 sign flips, whole-brain max-T FWE correction, coverage rule, ROI coordinates, uncertainty, and limits (`results/report.md`, `results/analysis_results.json`).
- It supplies runnable analysis code, figures, unthresholded and corrected maps, source/checksum metadata, and command/resource logs (`scripts/group_analysis.py`, `results/`, `input/sources.json`, `logs/`).

## Per-item checklist

The table below is rendered by the frozen response helper; the complete machine-readable answers are in [`2026-10-16-response.json`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/2026-10-16-response.json).

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files` | All scientific inputs, code, environment specification, results and records are beneath one repository root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `scripts/group_analysis.py`, `input/data/` | The script reads repository-relative inputs; all 54 maps are annex pointers beneath input/data/. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `scripts/group_analysis.py` | The analysis libraries are declared in pixi.toml; no external code submodule is required. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git status --porcelain`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/worker-end-state.json` | Git tracks code, text, configuration and results; the worker-stop receipt records a clean checkout at this commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `.gitattributes`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/attempts/remote-retrieval-2.stdout` | Git-annex tracks 55 binary objects; a retrieval clone fetched and fsck verified all annex payloads. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/group-analysis-final-20261015c_info.json`, `pixi.toml` | Run logs record the command and host, but no exact lock or environment hash links the results to a frozen specification. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-files`, `results/report.md` | No README.md or Makefile gives installation and use instructions; the command appears only in results/report.md. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `scripts/group_analysis.py` | The report gives a concrete command and scripts/group_analysis.py is the runnable starting point. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths`, `scripts/group_analysis.py` | The analysis constructs paths relative to its repository root; the path probe found no host-specific absolute paths. |
| must/010 | P.1 | met | judgement | `scripts/group_analysis.py`, `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/replay-work/fresh-1/clone/pixi.lock` | Direct analysis imports are declared in pixi.toml or its resolved package dependencies; no omitted analysis library was found. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml`, `results/report.md` | pixi.toml names macOS 14 arm64 and linux-64, but the documented route assumes a host Pixi install without installation guidance. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml`, `results/report.md` | pixi.toml lists package dependencies and platforms, but the documentation omits the required Pixi installation step. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is tracked with the code and data. |
| must/014 | P.3 | unmet | judgement | `.gitignore`, `pixi.toml` | No runnable process for updating environment specifications is documented; pixi.lock is ignored and absent from the committed object. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml`, `.gitignore` | The committed pixi.toml uses wildcard or range versions, and no frozen pixi.lock is tracked. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/attempts/remote-ls-remote.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/attempts/remote-retrieval-2.stdout` | A researcher with Hub access can retrieve the exact commit and all 55 annex payloads; checksums passed in a same-host clone. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md`, `pixi.toml` | The report shows how to run pixi.toml, but does not explain how to install Pixi or obtain the environment tooling. |
| should/001 | T.2 | met | judgement | `git ls-files`, `.gitattributes` | Git tracks the project tree and git-annex stores its large binary content within that same repository. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI configuration regularly tests that the documented instructions remain accurate. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, analysis code, results and environment specification occupy distinct project paths. |
| should/004 | E.1 | not-checked | probe:fresh-rerun | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The only replay was invalidated when the runner removed input/participants.tsv; a fresh run preserving all declared inputs would settle this. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `.gitignore` | The documented pixi run route reuses a local environment; it does not create a disposable environment for each execution. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `.gitignore` | No exact locked environment was recorded or regularly rebuilt; the project has no CI configuration and omits pixi.lock. |
| should/007 | D.2 | unmet | judgement | `.gitignore`, `pixi.toml` | The object tracks a specification but no archived environment image or binaries; .pixi is excluded. |
| should/008 | D.2 | unmet | judgement | `must/014`, `.gitignore` | Same question as must/014: no runnable update process or tracked lockfile update is present. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `pixi.toml` | N/A: this study uses public source data and declares no restricted data or software component. |
| may/001 | M.2 | unmet | probe:subdatasets-resolvable+judgement | `git submodule status`, `input/data/`, `pixi.toml` | External maps and packages are not Git submodules; maps use git-annex and packages use pixi.toml. |
| may/002 | M.2 | met | judgement | `results/report.md`, `input/`, `scripts/`, `results/`, `pixi.toml` | The report describes fixed inputs, the analysis, outputs and reproduction command; the tree separates each component. |
| may/003 | M.2 | partial | judgement | `scripts/group_analysis.py`, `input/`, `results/` | Filesystem boundaries are clear, but the input and result interfaces are conventions in one script rather than independent module contracts. |
| may/004 | M.2 | met | judgement | `results/report.md`, `scripts/group_analysis.py` | The report's pixi run command composes the environment, script and repository inputs. |
| may/005 | M.2 | met | judgement | `results/report.md`, `input/upstream-methods.md` | The report links key outputs and describes upstream methods and the input, code and result layout. |

## Flagged items

- **must/002 — probe-overridden:** the probe only saw no submodules; the 54 required maps are git-annex files within the common root and resolve from the script's root-relative paths.
- **must/006 — mapping-questioned:** the run-record probe missed the committed command/stdout/stderr/resource records. The verdict remains unmet because those records do not identify an exact locked environment.
- **must/008 — probe-overridden:** the probe missed the entrypoint because it is described in `results/report.md`, not a README or Makefile; the report names `scripts/group_analysis.py` and its command.
- **must/011 and must/012 — probe-overridden:** the command scan could not assess host documentation. `pixi.toml` lists platforms, but Pixi installation is not documented.
- **must/014 and should/008 — upstream-duplicate:** both items ask the same environment-update question and are answered from the same evidence.
- **must/015 — probe-overridden:** the probe left environment pinning unchecked; `pixi.toml` uses ranges/wildcards and `.gitignore` excludes `pixi.lock`.
- **must/016 — probe-overridden:** the probe did not retrieve the exact revision. A separate clone fetched the exact commit and all 55 annex payloads, then passed `git annex fsck`.
- **may/001 — probe-overridden:** no submodules exist, but inspection shows external inputs are handled with git-annex and software with Pixi; the optional submodule property is absent.

## Not checked

- **should/004:** the sole replay attempt did not reach analysis. The wrapper removed `input/participants.tsv` as a shipped output before running the entrypoint. A fresh replay that preserves this required input would settle whether the pipeline completes in a fresh environment. The failed attempt and clone are retained under `replay-work/fresh-1/` and `2026-10-16-fresh-rerun.json`.

## Goals and kind

Assumption, not user-confirmed: this is a **study** whose product is an answer to the supplied NARPS Hypothesis 1 question using fixed participant gain-effect maps. The goal and upstream scope are described in `input/study-task.md` and `input/upstream-methods.md`. There was no human attached to confirm the kind. The study emphasis is on keeping inputs, code, environment and derived results linked and re-executable.

## Scientific adequacy and conclusion

**Scientific adequacy: qualified.** The supplied maps provide a defensible group-level test conditional on the fixed participant models. The reported scientific conclusion is **no whole-brain-corrected support for a positive vmPFC gain effect in this sample**. This is a defensible absence of a positive finding, not evidence that the effect is exactly zero.

All 54 expected participants were analyzed with no exclusions. The script checks finite values and matching dimensions/affines, aligns the TemplateFlow brain mask to the maps, and limits inference to shared nonzero support inside that mask. It reports 186,192 whole-brain voxels and 5,754 voxels in its broad bilateral MNI vmPFC search zone. The positive one-sample voxelwise t test uses 9,999 participant sign flips and the whole-brain maximum statistic for one-sided FWE correction, as required by the supplied task and the [original NARPS instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). No vmPFC voxel passed FWE p ≤ .05. The zone's largest statistic was t(53)=4.19 at MNI [-2, 24, -18], with whole-brain FWE p=.7778. The descriptive zone-mean estimate was -0.000096 upstream coefficient units (95% t interval [-0.01434, 0.01414]). The whole-brain positive peak was outside vmPFC (t=6.62, FWE p=.0007); it does not answer the target hypothesis.

The decision is qualified by three limits. First, the broad coordinate box is transparent and fixed before examining effects, but is not tied to an independently named anatomical atlas; boundaries could include or omit relevant vmPFC subregions. Second, the mask treats nonzero support in all 54 maps as coverage; the report quantifies exclusions but does not show a sensitivity analysis using the stated 90% support mask. The inference therefore assumes zeros outside a participant's coverage are missing rather than valid estimates. Third, participant variance maps are unavailable, so estimates are unweighted and sign-flip inference depends on a symmetric null distribution. The upstream gain regressor was centered and variance-normalized, so its coefficient is not a per-currency-unit effect and, given the unequal gain/loss ranges, does not directly compare gain and loss slopes. These limits are acknowledged in the report; no time-series data or upstream participant models were rerun.

The figures are informative: the whole-brain map marks corrected positive clusters and states none lie in the vmPFC zone, while the participant plot shows the zone-mean estimates and interval. The supported finding is restricted to the supplied maps, their upstream model and this stated group procedure; it does not generalize to all possible first-level models or populations.

## Retrieval, replay and worker-stop attribution

**Access check.** Intended recipient: a researcher with authorized CON Hub access. Route: HTTPS Git clone/fetch from `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git` at `refs/heads/codex/narps-r1-06`, with annex content fetched through the Hub's Git-annex P2P HTTP route. Required coverage checked: exact Git commit and tracked code, environment specification, methods, report and metadata; all 54 input maps; and the annexed group map. The retrieval-only clone resolved to the requested commit and all 55 annex payloads passed `git annex fsck`. Host scope was the same workstation as the target, so this establishes retrieval through that route, not cross-host portability. Commands and output are in `attempts/remote-retrieval-2.*` and `attempts/remote-ls-remote.*`.

**Replay.** The one authorized replay used the documented command `pixi run python scripts/group_analysis.py --permutations 9999 --seed 20261015` in a separate clone on the same host. The wrapper fetched input files, then removed `input/participants.tsv` before execution as though it were a shipped output; the script consequently exited before analysis. The wrapper result is `unmet`, but that failure does not establish a project-code defect. Because no second replay is allowed, should/004 is `not-checked`. The full runner receipt, stdout/stderr and workspace are preserved; the original target remains unchanged.

**Worker stop.** The supplied end-state receipt (SHA-256 `c269f48fe77e0c9f39b921fad6e6759fb8f7d02016b93ef435c43bff7b52ea41`) records worker exit code 0, the requested HEAD, and an empty status at stop. Its index and worktree inventories contain 99 entries; the assessed checkout is that exact commit and is clean. This supports worker credit for delivering a committed, tracked state. The receipt also records `con-hub` and `origin` remote-tracking refs at the same commit, but does not record a push operation or remote URL. Exact-revision publication and annex retrieval are verified now; the receipt does not establish who performed that publication. Coordinator-side commits, annex uploads, or environment snapshots added after stop are not credited to the worker. The receipt is retained as `worker-end-state.json`.

Blinding note: retained identifiers expose study and cohort context. No hidden worker-condition field was inferred or used as grading evidence.

Additional probe findings outside the 31-item checklist: no license declaration was found; no Git text blob exceeded the probe's 10 MiB threshold. These are reported separately because the pinned checklist has no license item.

## Checklist link and provenance stamp

[Open the completed STAMPED checklist](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/2026-10-16-url.txt). The validated response JSON is [`2026-10-16-response.json`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/2026-10-16-response.json); unedited probe results are [`2026-10-16-probes.json`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/2026-10-16-probes.json), and the replay receipt is [`2026-10-16-fresh-rerun.json`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-06/judgment-01/judgment/2026-10-16-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on `git@github.com:leej3/stamped-in-practice.git` at commit `32d9cabf7b5d041f9efb97830bf5279068809357`, 2026-10-16, OpenAI Codex API / GPT-6 (exact runtime variants unavailable). Frozen runner environment commit: `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: `2026-10-16-probes.json`.
