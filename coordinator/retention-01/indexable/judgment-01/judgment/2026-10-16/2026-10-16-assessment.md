# STAMPED and scientific assessment

## Verdict

MUST: **14 met / 0 unmet / 3 partial / 0 not-checked** (17). SHOULD: **2 met / 1 unmet / 5 partial / 1 not-checked** (9). MAY: **4 met / 0 unmet / 1 partial / 0 not-checked** (5). Partial does not satisfy a MUST. No overall score is assigned.

## What to fix first

1. Document the online Nilearn template dependency or ship a pinned mask with checksum. This closes the remaining host/network gap for reruns (must/011, must/012).
2. Add a recurring clean-environment rebuild and validation, and retain the logs. This keeps instructions and the pinned environment current (should/002, should/006).
3. Record an actual dependency update after the documented `pixi lock` process, and retain that update in history (must/014, should/008).
4. Run tasks in a disposable environment per execution (should/005).
5. Declare data and software reuse terms so restriction status can be decided (should/009; extra finding `license-declared`).

## What the object already does well

- The analysis plan defines the estimand, participant-level model, whole-brain correction, anatomical search box, checks, exclusions and interpretation limits (`protocol/analysis-plan.md`).
- The repository tracks code and documentation in Git and large inputs/results with git-annex; a remote DataLad checkout retrieved all 54 maps and annexed result payloads, and annex fsck passed.
- It retains a lock snapshot and a replay record, plus Duct records and an independent validator for the reported statistics (`results/replay.json`, `logs/`, `scripts/validate_results.py`).

## Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-tree -r --name-only HEAD`, `.gitmodules` | All study inputs, code, configuration, protocol, results and logs are nested under one repository root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable | `.gitmodules`, `input/sources.json` | Study maps are annexed under input/data; the only linked module has a resolvable URL. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `scripts/group_analysis.py`, `README.md#Install` | Pixi declares analysis libraries and the access tooling; scripts import only declared packages. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/worker-end-state.json`, `git ls-tree -r --name-only HEAD` | Worker-stop receipt records the requested commit and a clean worktree; code and documentation are Git tracked. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/object-datalad-annex-fsck.log` | git-annex stores the maps and binary outputs; remote retrieval and fsck verified all task inputs. |
| must/006 | T.1,T.3,T.5 | met | probe:derived-have-records+probe:run-env-linked+judgement | `results/replay.json`, `logs/20261016T-published-replay-groupinfo.json` | Run records name commands and results/replay.json pins the source commit and exact lock hash. |
| must/007 | A.1 | met | probe:entry-point | `README.md#Install`, `README.md#Run` | README.md documents setup, environment retrieval and use. |
| must/008 | A.1 | met | probe:entry-point | `scripts/group_analysis.py`, `pixi.toml` | README names the present group-analysis script and Pixi task. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | The probe found no host-specific absolute paths in tracked text. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-pixi-toml.txt`, `scripts/group_analysis.py`, `scripts/validate_results.py` | The environment declares Python, Git, scientific libraries, DataLad and git-annex used by the scripts. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md#Install`, `scripts/group_analysis.py` | README documents supported OS families, but the analysis fetches a Nilearn brain mask online without documenting that host network requirement. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md#Install`, `scripts/group_analysis.py` | README lists Git, git-annex, Pixi and supported platforms; it omits the online template fetch and tool versions. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-snapshot-head.txt` | pixi.toml is tracked with the task code and the lock snapshot is tracked on the companion environment branch. |
| must/014 | P.3 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md#Install`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-history.log` | README gives a pixi lock update procedure; history shows the initial lock snapshot, but no later dependency update following it. |
| must/015 | D.1 | met | probe:run-env-linked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-pixi-lock-sha256.txt`, `results/replay.json` | The exact pixi.lock is retrievable at the companion branch and its SHA-256 matches results/replay.json. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/object-datalad-target-branch-head.txt`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/object-datalad-target-branch-get.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/object-datalad-annex-fsck.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-pixi-lock-sha256.txt` | A researcher can retrieve the exact task branch, all 54 input maps, archived result payloads and the locked environment. |
| must/017 | D.1 | met | judgement | `README.md#Install` | README explains where to get the lock snapshot, how to install it and how to retrieve maps. |
| should/001 | T.2 | met | judgement | `.gitmodules`, `input/data`, `pixi.toml` | Git tracks code, environment and text; git-annex tracks large maps and results; skills is a Git submodule. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `logs/20261016T-published-replay-groupinfo.json`, `probe:ci-present` | Duct records show repeated manual analysis and validation runs, but no CI or scheduled checks keep instructions current. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, scripts, results and environment manifest occupy separate directories/files. |
| should/004 | E.1 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/2026-10-16-fresh-rerun.json` | A fresh clone replayed on the same host; scientific outputs matched, but no separate VM, container or cloud host was used. |
| should/005 | E.1 | unmet | judgement | `README.md#Install`, `pixi.toml` | Pixi reuses a project environment; each execution does not create and discard an isolated environment. |
| should/006 | D.2 | partial | probe:ci-present+judgement | `results/replay.json`, `probe:ci-present` | The pinned environment was replayed and checked manually, but no recurring CI rebuild verifies it. |
| should/007 | D.2 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-snapshot-clone/pixi.lock`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-pixi-toml.txt` | The exact lock is archived in the retrievable companion branch, but executable package artifacts come from external channels. |
| should/008 | D.2 | partial | judgement | `README.md#Install`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-history.log` | Same documented update process as must/014; the initial lock is tracked, with no later update instance. |
| should/009 | M.4 | not-checked | judgement | `input/sources.json`, `probe:license-declared` | No license or access terms establish whether any software or data are restricted; declarations would settle this. |
| may/001 | M.2 | partial | probe:subdatasets-resolvable+judgement | `.gitmodules`, `input/sources.json`, `pixi.toml` | The skills module is linked, but study maps use annex and Pixi packages use manifests rather than separate modules. |
| may/002 | M.2 | met | judgement | `README.md`, `protocol/analysis-plan.md` | README explains the relationship among fixed inputs, group-analysis code, results and environment tasks. |
| may/003 | M.2 | met | judgement | `input/data`, `scripts`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-01/judgment/2026-10-16/environment-snapshot-head.txt` | The map inputs, analysis scripts and environment snapshot can be updated independently within tracked boundaries. |
| may/004 | M.2 | met | judgement | `pixi.toml`, `README.md#Run` | Pixi tasks compose analysis, validation and figure generation; git-annex retrieves inputs and results. |
| may/005 | M.2 | met | judgement | `README.md`, `input/upstream-methods.md` | README links the protocol and input methods and names all reproduction tasks. |

## Flagged items

- **must/006** — The derived-file probe did not recognize the recorded Duct runs and replay record; the run command, code commit and lock hash are present.
- **must/015** — The probe examined only the task branch; the companion environment branch contains the retrieved lock whose hash matches `results/replay.json`.
- **must/016** — The probe tested the SSH GitHub `origin`; the object also has a Center for Open Neuroscience route, which I checked by retrieving the exact branch and annex content.
- **should/002, should/006** — The CI probe found no CI configuration. Duct records show manual runs, supporting partial rather than no testing.
- **must/014, should/008** — These checklist items duplicate the same environment-update question; both answers repeat by design.
- **may/001** — The module probe found a linked skills submodule; this item also asks about the study maps and software dependencies, which instead use annex and Pixi manifests.

## Not checked

- **should/009:** Project files do not establish data/software licensing or whether any component is restricted. Add reuse and access terms to settle this.

## Goals and kind

**Assumption (not user-confirmed; no human was attached):** this is a study whose product is a group-level answer to the supplied NARPS Hypothesis 1 question, using the fixed participant maps. The primary kind is **study**, so all seven principles apply, with emphasis on the tracked inputs, reproducible group inference and retrieval of the complete object.

## Scientific assessment

**Scientific adequacy: supported.** **Scientific conclusion: the positive vmPFC hypothesis is not supported by this analysis.** The report reaches the defensible absence-of-support conclusion that the task requires; this does not establish a zero effect or equivalence.

The analysis uses 54 participant COPE-like maps as independent observations in a one-sample intercept model, tests the positive direction, and controls whole-brain familywise error with a one-sided max-t sign-flip procedure (9,999 flips; 196,120 voxels). It checks participant IDs, hashes, geometry and finite values; all 54 maps pass and none are excluded. The analysis plan and report correctly state that these are normalized-modulator effect estimates, not currency-unit slopes, and that absent participant variance maps prevent precision weighting. The separate-gain upstream model also limits interpretation.

No positive max-t FWE voxel lies in the descriptive vmPFC coordinate box. The selected vmPFC-box peak has FWE p = .791 despite its post-selection uncorrected p = 5.3e-5. The 23 FWE-positive voxels lie posteriorly; the peak at MNI (−26, −102, −3.6) has t = 6.62 and FWE p = .0007 and does not support the vmPFC hypothesis. The box is explicitly descriptive, not a validated atlas ROI or a reduced correction family. The 95% interval for its mean (−0.0215, 0.0172) includes zero. These details, plus the unthresholded/corrected maps and localization figures, support the conclusion without treating a nonsignificant result as proof of no effect. The inference remains conditional on independent participants, sign-symmetric null errors and the supplied upstream model.

The retained report includes informative participant and whole-brain figures. I inspected them; the coordinate figure places all corrected points posterior to the vmPFC box. The source task requires whole-brain-corrected decisions; the [NARPS team instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) identify the positive vmPFC hypothesis for the equal-indifference group and request whole-brain-corrected decisions and group statistical maps.

## Access and replay evidence

**Intended recipient:** a researcher following the object's documented access and installation route. **Route tested:** HTTPS/DataLad clone of `codex/narps-r1-11` from `hub.centerforopenneuroscience.org`, followed by `datalad get input/data/` and `datalad get results/`; the companion `codex/env-narps-r1-11` branch supplies the exact lock, installed with `pixi install --locked`. **Coverage:** the exact assessed Git commit, code/documentation, 54 input maps and the annexed result payloads under `results/`; all 67 retrieved annex payloads passed `git annex fsck --fast`. The companion lock SHA-256 (`de895db6…ac20bd7`) matches `results/replay.json`. **Host scope:** same macOS host; this retrieval and replay do not establish cross-host portability. A shallow single-branch retrieval attempt had no annex-location records; the full DataLad clone at the documented task branch retrieved the payloads successfully.

The authorized runner replay used a separate fresh clone and the documented command `pixi run group-analysis`. It completed on the same host. Fourteen of 15 selected outputs matched exactly. The only differing output was `results/summary.json`; removing `runtime_seconds` leaves no diff (18.333 s versus 19.071 s). This verifies the recorded route and computational repeatability for the inferential outputs; it does not test the full validation/figure task sequence or another host. The runner's replay record and workspace are retained under `2026-10-16/`.

## Worker-stop attribution

The supplied worker-end-state receipt (SHA-256 `1f87c35600472021177124e6da4b93f2b2161975a2376d85e0f07d60265a72a6`) records return code 0, `HEAD` at the requested commit, branch `codex/narps-r1-11`, and an empty worktree at stop. The committed logs include a successful published-branch replay before that stop, and the receipt lists remote-tracking refs at the same commit. This supports credit for worker-tracked code, results and recorded retrieval/replay practice. Current retrieval checks independently show that the route still works; they are not used to infer who uploaded the files. No later coordinator preservation is counted as worker work.

## Other probe findings

- `license-declared` is **unmet** as an extra finding: no reuse terms are declared.
- `clone-weight` is **met**: no large text blob is in Git.
- `inputs-untouched` is **not-checked** for the uninitialized `skills` module; this does not concern the NARPS input maps.

## Checklist and provenance

[Open the checklist response URL](2026-10-16-url.txt). The full per-item record is [2026-10-16-response.json](2026-10-16-response.json); raw probe results are [2026-10-16-probes.json](2026-10-16-probes.json), and the formal replay record is [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on `git@github.com:leej3/stamped-in-practice.git` at commit `284c8768140cbd816d983f8bd2697bd9b541eb25`, 2026-10-16, Codex/GPT-6. The frozen assessment runtime was runner source `b86e37ff9115e37541fd47aca73f49e13b5110bb` in environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).
