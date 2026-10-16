# STAMPED assessment — NARPS gain-effect study

**Object:** `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/targets/judgment-01` at `f30190d8144a9e15acfa1c0d973eadf0d655c83c`, verified with `git -C "$STAMPED_JUDGE_TARGET" rev-parse HEAD`. The worker-end-state receipt records the same commit and a clean worktree.

**Assumption (unconfirmed):** From the supplied scientific brief and retained report, this is a study research object whose goal is group inference for NARPS Hypothesis 1. No human is attached to confirm the purpose or kind; the recorded kind is `study`.

**Scope:** committed state only; frozen probes with remote checks; source retrieval checks; one authorized fresh clone on the assessor host using the documented entrypoint. The replay clone did not retrieve annex payloads, so the entrypoint was not run. The clone and generated output are retained under `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/replay-work-1`. This tests its recorded local retrieval route, not cross-host portability. The supplied NARPS PDF URL timed out when opened; I relied on the task brief, coordinator rubric and retained artifacts. No target files were modified.

## STAMPED verdict

**MUST:** 8/17 met, 6 partial (do not satisfy MUST), 3 unmet, 0 not-checked. **SHOULD:** 2/9 met, 5 unmet, 1 not-checked, 1 not-applicable. **MAY:** 0/5 met, 3 partial, 2 unmet. Across all 31 items: 10 met, 9 partial, 10 unmet, 1 not-checked, 1 not-applicable. There is no overall score.

The highest-leverage issue is that a fresh clone cannot retrieve 64 annex payloads, including shipped result and atlas files. The code branch itself is available at the assessed commit, and all 54 participant maps are retrievable from the declared NeuroVault source URLs with exact manifest hashes. Make the annex content available through the existing authorized route. Next, pin the Pixi environment and document environment setup and dependency updates.

**Already in good shape:** the analysis, methods, figures, machine-readable outputs, quality checks, run logs and source manifest are committed; code and annex data share Git-based tracking; map identities and image geometry are checked; the report explains the coefficient scale, exclusions, uncertainty and correction method.

## Scientific assessment (separate from STAMPED)

**Scientific adequacy: qualified. Reported conclusion: the supplied maps do not support a positive, whole-brain-corrected vmPFC gain effect in this group.** The code uses all 54 equal-indifference participants, checks IDs, map hashes, 3D shape and affine alignment, and analyzes participant gain-effect estimates with an equal-weight one-sample random-effects t model. Participant variance maps were not supplied, so inverse-variance weighting is unavailable. The one-sided participant sign-flip max-t test uses 5,000 permutations over 198,029 common nonzero voxels, with whole-brain FWE control at .05. This directly addresses the required correction and avoids using an uncorrected ROI result as the confirmatory finding.

**Supported findings:** under the stated model and supplied maps, no positive vmPFC voxel survives whole-brain correction; a positive effect occurs in posterior brain locations elsewhere. The retained results support a defensible absence of corrected support for the vmPFC hypothesis, not an equivalence or zero-effect claim.

The result is 24 positive whole-brain FWE voxels, all in posterior locations. None of 1,297 bilateral AAL3 medial orbitofrontal voxels operationalized as vmPFC passes max-t FWE; the ROI peak has t=2.34 and max-t pFWE=1.0. The descriptive participant-average coefficient is −0.0079 model units (95% t interval −0.0346 to 0.0188). The interval spans zero. The outlier screen flagged sub-025, but the participant was retained and the reported leave-one-out interval remains across zero.

The no-support conclusion is appropriately limited: it does not establish a zero effect or exclude a smaller effect. The estimates are first-level coefficients for a mean-centered, variance-normalized gain modulator, not BOLD change per currency unit. Separate gain/loss models and the unequal gain/loss ranges preclude a gain-versus-loss comparison. The anatomical label is a defensible broad operationalization, though AAL3 medial orbitofrontal parcels are not a uniquely defined vmPFC boundary. Sign-flip inference also relies on participant-level symmetry under the null. These considerations qualify interpretation without overturning the reported absence of corrected vmPFC support.

Scientific evidence: `input/upstream-methods.md`, `scripts/group_analysis.py`, `results/report.md`, `results/analysis_results.json`, `results/quality_checks.json`, `results/group_summary.csv`, `results/whole_brain_fwe_clusters.csv`, `results/participant_roi_effects.csv`, and the three figures under `results/figures/`. The single fresh-clone replay could not execute because annex content was unavailable; it does not independently confirm the retained outputs.

## Access and worker-stop attribution

- **Intended recipient:** a researcher using the declared authorized access route; anonymous access is not required.
- **Routes checked:** GitHub origin recorded by the worker receipt and individual NeuroVault media URLs in `input/sources.json`.
- **Coverage:** the worker receipt records `refs/remotes/origin/codex/narps-r1-07` at the worker commit; a bare clone of the current origin also contains branch `codex/narps-r1-07` at that commit. All 54 required participant gain maps fetched and matched the recorded byte counts and SHA-256 values. The fresh clone could not retrieve the 64 annex payloads (including outputs and cached atlas files), so full-object access remains **partial**.
- **Host scope:** Git clone and direct source retrieval were checked from the assessor's Darwin host. No separate-host retrieval test was made. The NeuroVault retrieval manifest and downloaded map files are under `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/neurovault-all-maps-attempt-2/`; the replay receipt is `2026-10-16-fresh-rerun.json`.

The external receipt at `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/worker-end-state.json` (SHA-256 `97caecab5ddac2f1b7bfa033e1b20470c263523c6cf88bb1fc34482c0ab55e25`) records worker exit 0, the exact assessed commit, an empty porcelain status, 149 tracked paths, and remote-tracking refs at the worker commit. The current origin branch at the same hash corroborates code publication. It does not make unavailable annex payloads accessible. The scientific review uses retained committed artifacts; coordinator-preserved artifacts are not credited as worker actions.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files` | The study inputs, code, environment, run logs, and results sit under one repository root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/neurovault-all-maps-attempt-2/retrieval-manifest.json` | All 54 source map URLs returned manifest-matching bytes and SHA-256; code reads the in-root input/data paths. |
| must/003 | S.1 | met | judgement | `pixi.toml` | Analysis libraries are declared in pixi.toml; the atlas cache is included in results/. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git status --short --branch` | Git tracks the code and documentation, and the assessed worker stop was clean. |
| must/005 | T.1,T.3,T.5 | met | probe:large-annex | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-probes.json` | Git-annex tracks the large map and atlas payloads; no large binary is a Git blob. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `logs/group-analysis-releaseinfo.json` | The release log records command and host, but no lock or exact environment pin links outputs to a full environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `results/report.md` | No README or Makefile gives installation and usage; results/report.md has only a reproduction command. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md` | The documented Pixi command starts scripts/group_analysis.py and is recorded in the release log. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/group_analysis.py` | Tracked analysis code uses paths relative to its repository root. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Analysis imports are declared in pixi.toml, but the documented pixi run also assumes Pixi is installed on the host. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Pixi lists macOS and Linux targets, but host Pixi installation and network access for atlas retrieval are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Package dependencies and target platforms are listed, but Pixi setup and host requirements are not. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is tracked with the analysis code and data. |
| must/014 | P.3 | unmet | judgement | `pixi.toml` | No dependency update or lock regeneration process is declared in the environment specification or report. |
| must/015 | D.1 | unmet | judgement | `pixi.toml` | pixi.toml uses broad version ranges and no pixi.lock pins the resolved environment. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/target-ref-verification.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/neurovault-all-maps-attempt-2/retrieval-manifest.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The worker stop and remote branch share this commit; all 54 maps fetch, but annexed results and atlas payloads failed fresh-clone retrieval. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md` | The report gives a Pixi command, but omits how to install Pixi and obtain a pinned environment. |
| should/001 | T.2 | met | judgement | `.gitattributes` | Git and git-annex track the code, maps, cached atlas, and results within one dataset. |
| should/002 | A.2 | unmet | probe:ci-present | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-probes.json` | No CI configuration checks the workflow or keeps its instructions accurate. |
| should/003 | M.1 | met | probe:modules-separated | `input` | Inputs, analysis code, results, and environment specification occupy distinct paths. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The fresh clone could not retrieve annex payloads, so the analysis entrypoint never ran. |
| should/005 | E.1 | unmet | judgement | `results/report.md` | The documented Pixi environment is reused on the host; no disposable container or job environment is declared. |
| should/006 | D.2 | unmet | probe:ci-present | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-probes.json` | No CI rebuilds and tests the environment used for the results. |
| should/007 | D.2 | unmet | judgement | `pixi.toml` | The object contains specifications and atlas cache files, but no archived executable environment or package image. |
| should/008 | D.2 | unmet | judgement | `pixi.toml` | No process for updating dependencies is declared or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: supplied data and declared software are public; no restricted component is present. |
| may/001 | M.2 | unmet | judgement | `input/data` | The external dataset is annexed within this repository, not linked as a submodule. |
| may/002 | M.2 | partial | judgement | `results/report.md` | Directories separate inputs, code, results, and environment, but recombination is not documented. |
| may/003 | M.2 | partial | judgement | `scripts/group_analysis.py` | Inputs and code are separable by path, but the script expects fixed filenames and results layout. |
| may/004 | M.2 | unmet | judgement | `results/report.md` | The object has no module composition mechanism; the workflow is a single repository command. |
| may/005 | M.2 | partial | judgement | `results/report.md` | The report links the analysis and key outputs, but no root README explains repository navigation. |

## Flagged items

- `must/006`: the probe looked for a formal run-record mechanism; `logs/group-analysis-releaseinfo.json` does record the command and host. The verdict remains partial because no exact lock/pinned environment is linked to results.
- `must/007`: no root README or Makefile supplies installation and use instructions; `results/report.md` supplies only the run command.
- `must/008`: the probe missed the documented script and command in `results/report.md`; `scripts/group_analysis.py` is the entrypoint.
- `should/008` duplicates `must/014`; both are unmet because no dependency update process is declared.
- Probe extras outside the pinned checklist: `license-declared` is unmet (no reuse license is declared), `clone-weight` is met, and `inputs-untouched` is not-applicable because there are no linked modules.

## Not-checked

- `should/004`: the fresh clone failed annex retrieval before the entrypoint ran. A successful fresh execution with content access would settle it.

## Checklist, provenance and records

Checklist pin: STAMPED checklist 0.3.1. Assessment skill: `assess-alignment-with-stamped-principles@0.1.0`; conventions: `stamped-conventions@0.1.0`. Harness: Codex API. Model: GPT-6 (runtime build identifier unavailable). Assessment date: 2026-10-16 UTC.

- Checklist response: `2026-10-16-response.json`
- Checklist app URL: `2026-10-16-url.txt`
- Frozen probe output: `2026-10-16-probes.json`
- Fresh-clone record: `2026-10-16-fresh-rerun.json`
- Runner validation: `runner-validate.stdout`
- Commands and attempt outputs: `command-log.md` and the attempt artifacts under this assessment directory.
