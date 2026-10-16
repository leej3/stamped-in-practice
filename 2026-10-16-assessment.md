# STAMPED assessment: NARPS gain effect in vmPFC

**MUST:** 12/17 met, 1 partial, 4 unmet, 0 not-checked. **SHOULD:** 2/9 met, 5 unmet, 1 not-checked, 1 not-applicable. **MAY:** 2/5 met, 2 partial, 1 unmet. A partial MUST does not satisfy the item. No overall score is assigned.

## What to fix first

1. **Commit a resolved Pixi lockfile and document how to regenerate and review it** → the shipped environment can change as package ranges resolve, and the result logs cannot identify the environment used → must/006, must/014, must/015, should/006, should/008.
2. **Add a root README with Pixi installation, clone/data retrieval, and run steps** → the report includes a run command, but a new researcher is not told how to obtain the execution tool and environment → must/007, must/017.
3. **Add a clean CI or fresh-environment run with retained inputs and recorded results** → no committed evidence shows the documented route succeeding in a disposable environment; the authorized replay was interrupted by runner cleanup → should/002, should/004, should/006.

## What the project does well

- The analysis checks cohort membership, all 54 map hashes, dimensions, affines and finite values; it uses the common nonzero coverage mask and retains all participants. See `scripts/group_analysis.py`, `results/quality_checks.json` and `results/participant_roi_effects.csv`.
- The report uses participant-level gain coefficients, whole-brain one-sided max-T FWE, and an explicit AAL3 medial-orbitofrontal operational label. It does not treat non-significance as proof of zero or claim a gain-versus-loss effect. See `results/report.md` and `results/analysis_results.json`.
- Inputs, code, results and environment are separated; binary content is tracked through git-annex. The worker-stop receipt matches the 149-entry committed tree exactly and records an exited worker with an empty index/worktree status; see `input/`, `scripts/`, `results/`, `pixi.toml`, and [the worker inventory check](2026-10-16-worker-inventory-check.stdout.txt).

## Per-item results

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-tree -r HEAD` | All tracked object content is within the single repository root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data` | The 54 maps and manifest are annexed under input/data; retrieval sources are recorded. |
| must/003 | S.1 | met | judgement | `pixi.toml` | The analysis dependencies are declared in the Pixi environment specification. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean+judgement | `git status --short`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-03/worker-end-state.json` | Git tracks code, text, documentation and configuration at the committed state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `probe:large-in-annex`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-03/judgment/2026-10-16-annex-whereis.jsonl` | git-annex carries the binary maps and outputs; no large binary blobs are stored directly in Git. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/group-analysis-releaseinfo.json`, `pixi.toml` | The run log records a command, but no exact environment is linked to results; no lockfile is tracked. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-tree -r --name-only HEAD` | The root has no README.md or Makefile with installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `scripts/group_analysis.py` | The report gives a reproduction command and names the analysis script. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/group_analysis.py`, `probe:no-abs-paths` | The analysis uses paths relative to its repository root. |
| must/010 | P.1 | met | judgement | `scripts/group_analysis.py`, `pixi.toml` | All nonstandard imports and analysis libraries are declared in Pixi. |
| must/011 | P.1 | met | judgement | `pixi.toml`, `results/report.md` | Pixi declares supported platforms; no additional host hardware, scheduler or system library is required. |
| must/012 | P.2 | met | judgement | `pixi.toml`, `results/report.md` | The environment specification lists Python, analysis packages and supported platforms; the report names the run command. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | The environment specification is committed with the analysis. |
| must/014 | P.3 | unmet | judgement | `pixi.toml` | No dependency-update or environment-regeneration process is documented. |
| must/015 | D.1 | unmet | judgement | `pixi.toml`, `git ls-tree -r HEAD` | The committed Pixi file has mutable ranges and wildcards; no exact lock snapshot is tracked. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `2026-10-16-hub-ls-remote.stdout.txt`, `2026-10-16-fresh-rerun.json`, `2026-10-16-replay-map-check-2.stdout.txt`, `pixi.toml` | Researcher retrieval of the exact commit and environment spec succeeded through the recorded Git/DataLad route. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:fresh-rerun+judgement | `results/report.md`, `pixi.toml` | The report provides `pixi run`, but omits Pixi installation and environment retrieval instructions. |
| should/001 | T.2 | met | judgement | `.gitattributes`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-03/judgment/2026-10-16-annex-whereis.jsonl` | Git and git-annex version text and large content within the same repository. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present`, `git ls-tree -r --name-only HEAD` | No CI or regular workflow test is defined. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, code, results and environment are kept in distinct paths. |
| should/004 | E.1 | not-checked | probe:fresh-rerun+judgement | `2026-10-16-fresh-rerun.json`, `logs/group-analysis-releaseinfo.json` | Replay stopped before analysis because the runner deleted input/participants.tsv; a clean fresh-run test that preserves inputs would settle this. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `pixi.toml` | The documented command reuses Pixi's environment; no per-run disposable environment is configured. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `pixi.toml`, `logs/group-analysis-releaseinfo.json` | There is no exact locked environment to reconstitute or regularly test; run logs do not record one. |
| should/007 | D.2 | unmet | judgement | `pixi.toml` | The environment is described by a spec but installed artifacts are not archived with the object. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log --oneline -- pixi.toml` | No update-and-track process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `pixi.toml` | N/A: the object contains no restricted data or software; sources identify public inputs and dependencies. |
| may/001 | M.2 | unmet | judgement | `input/data` | External source data are annexed as files rather than included or linked as submodules. |
| may/002 | M.2 | partial | judgement | `results/report.md`, `input`, `scripts`, `results`, `pixi.toml` | The input/code/results/environment layout is apparent and the report links files, but module relationships are not described as a structure. |
| may/003 | M.2 | partial | judgement | `scripts/group_analysis.py`, `input/sources.json` | Input, analysis and result boundaries are distinct, though there is no documented contract for updating them independently. |
| may/004 | M.2 | met | judgement | `results/report.md`, `scripts/group_analysis.py` | The documented Pixi command composes the environment, inputs and analysis script into result generation. |
| may/005 | M.2 | met | judgement | `results/report.md` | The report links the analysis script and key machine-readable results, supporting navigation. |

## Flagged items

- **must/008 — probe-overridden:** the entry-point probe did not recognize a starting script, but `results/report.md` gives the exact command and `scripts/group_analysis.py` is the main entrypoint.
- **must/016 — probe-overridden:** the initial probe did not establish remote retrieval. The branch resolved to the requested commit; the same-host clone fetched annex content and all 54 map hashes matched `input/sources.json`.
- **should/004 — probe-overridden:** the rerun probe reported failure, but its cleanup removed the tracked input `input/participants.tsv` before the command began. This does not establish that the project command itself failed.
- **must/014 and should/008 — upstream-duplicate:** these ask the same environment-update question and receive the same verdict.

## Not checked

- **should/004:** no fresh-environment success or failure can be attributed to the object because the runner removed a required input before execution. A valid clean run that preserves `input/participants.tsv` would settle it. No second replay was attempted under the one-attempt scope.

## Access and worker-stop attribution

The intended recipient is a researcher using the repository’s authorized Git/DataLad route. At assessment time, the `con-hub` route (`https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git`, branch `codex/narps-r1-07`) resolved to the exact assessed commit. The fresh clone retrieved 64 annex objects, including the 54 participant maps; an independent check found all 54 map byte counts and SHA-256 values matched `input/sources.json`. Required object coverage included code, environment specification, cohort metadata, all 54 maps and retained results; the Git tree supplied the tracked files. The clone and retrieval were performed on the same Darwin host; this verifies that route on that host, not cross-host portability. The replay runner then deleted `input/participants.tsv` during shipped-output cleanup, so it stopped before scientific analysis.

The supplied worker-end-state receipt is complete and matches SHA-256 `97caecab5ddac2f1b7bfa033e1b20470c263523c6cf88bb1fc34482c0ab55e25`; it records worker return code 0 and an empty index/worktree status, and its inventory matches all 149 entries of commit `f30190d8144a9e15acfa1c0d973eadf0d655c83c`. This establishes the worker’s committed, clean delivery. The receipt does not inventory annex payload locations at worker stop; current remote retrievability is verified above but is not attributed to the worker. The committed `logs/group-analysis-releaseinfo.json` records a successful same-host execution, but it does not pin the exact resolved environment.

Probe extras: no text blob exceeds 10 MiB (clone-weight met); no linked modules were present for the input-change comparison (inputs-untouched not-applicable); no reuse license was declared (license-declared unmet).

## Goals and kind

**Assumption (not confirmed by a human):** this is a study-level research object whose product is the group-analysis report and supporting code, tables, figures and maps. The goal is the supplied NARPS Hypothesis 1 group inference, conditional on the fixed participant maps and methods in `input/study-task.md` and `input/upstream-methods.md`. The study kind emphasizes complete inputs, traceable execution, portable environment and inspectable outputs. No treatment assignment was inferred or reported.

## Scientific assessment (separate from STAMPED)

**Scientific adequacy: supported. Scientific conclusion: the positive vmPFC gain-effect hypothesis is not supported by these supplied estimates under the reported group model.** Those labels are separate: the analysis and evidence support a defensible absence-of-positive-finding conclusion, not the hypothesized positive effect.

The script verified 54 unique equal-indifference participants, map hashes and common image geometry. It fit a one-sample participant-level random-effects model, used 5,000 participant-wise sign flips with the maximum positive t across 198,029 common finite, nonzero voxels for whole-brain FWE correction, and labeled vmPFC with bilateral AAL3 medial-orbitofrontal parcels. No participant was excluded. The participant-average ROI coefficient was −0.0079 model units (95% t interval −0.0346 to 0.0188); 0 of 1,297 ROI voxels survived max-T FWE. Twenty-four corrected positive voxels occurred in posterior locations outside the hypothesized ROI. These results support “no corrected positive vmPFC finding,” not a true zero effect.

The interpretation is appropriately bounded. The supplied maps are gain parameter estimates, not t/z maps; the upstream gain regressor was normalized, so coefficients are not per-currency-unit BOLD changes. The equal-weight group analysis is reasonable because participant variance maps are absent, but it does not provide a two-level variance model or inverse-variance weighting. Sign-flip inference assumes participant-level symmetry under the null. The AAL3 medial-orbitofrontal parcel is an explicit broad proxy for vmPFC. The descriptive ROI interval spans zero and no equivalence bound was tested. Separate gain/loss upstream models and the unequal gain/loss ranges prevent a gain-versus-loss conclusion. The positive posterior findings do not support the vmPFC hypothesis.

## Checklist link and stamp

[Open the completed checklist](2026-10-16-url.txt) · [Response JSON](2026-10-16-response.json) · [Unedited probe output](2026-10-16-probes.json) · [Replay receipt](2026-10-16-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on `git@github.com:leej3/stamped-in-practice.git` at commit `f30190d8144a9e15acfa1c0d973eadf0d655c83c`, 2026-10-16, OpenAI Codex assessment runner / model identity unavailable from harness. Probe output: `2026-10-16-probes.json`. The response passed the supplied runner’s `validate` action.
