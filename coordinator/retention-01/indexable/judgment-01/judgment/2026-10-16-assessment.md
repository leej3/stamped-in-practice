# STAMPED and scientific assessment

> Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1, on the research object at commit `e0a8fb1ae78b457a38ff7102825b1d8bc63119b4`, 2026-10-16 UTC. Harness/model: Codex API / GPT-6; exact runtime versions unavailable. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).

## Verdict

MUST: **9 met / 5 partial / 3 unmet / 0 not-checked** (17 total; partial does not satisfy a MUST). SHOULD: **2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable** (9 total). MAY: **0 met / 1 partial / 4 unmet / 0 not-checked / 0 not-applicable** (5 total). No overall score is assigned.

## What to fix first

1. Add and track a Pixi lockfile plus an update command, and name the lock used by each result run → readers cannot recreate the exact software state from wildcard dependencies → must/006, must/014, must/015, should/006, should/008.
2. Add concise setup instructions covering Pixi installation, supported host platforms, and TemplateFlow network access → the run command currently assumes an installed launcher and online template assets → must/007, must/011, must/012, must/017.
3. Preserve the replay runner's input/output distinction and repeat a clean replay after that harness defect is fixed → the one authorized run removed `input/participants.tsv` before starting, so replay remains unverified → should/004.
4. Record annex publication state alongside the worker-stop receipt → all required content retrieves from the hub now, but the receipt does not establish when annex copies became available → must/016.

## What the project already does well

- All 54 input maps and cohort metadata are within the repository boundary; large images are Git-annex managed. The remote clone retrieved the exact commit and all 56 annex payloads, and each passed `git annex fsck` (see [remote-get.stdout](remote-get.stdout), [remote-fsck-full.stdout](remote-fsck-full.stdout)).
- The analysis is rooted in repository-relative paths, checks participant IDs, image geometry, byte counts and SHA-256 values, and retains all 54 participants (see `scripts/analyze.py`, `results/participant_qc.tsv`, `input/sources.json`).
- The report gives a careful interpretation of model units and uncertainty, uses whole-brain Bonferroni correction for its primary test, and includes figures and participant-level vmPFC estimates (`results/report.md`, `results/results.json`).

## Per-item results

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/judgment/remote-get.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/judgment/remote-fsck-full.stdout` | All required files are under the repository root; annex payloads resolve through the documented remote. |
| must/002 | S.1 | met | judgement | `scripts/analyze.py`, `input/sources.json` | All 54 maps and cohort metadata are included under input/; sources.json preserves original provenance links. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `scripts/analyze.py` | Analysis libraries and TemplateFlow are declared in pixi.toml; nibabel is a Nilearn dependency. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/worker-end-state.json` | Git tracks the committed analysis and the worker-stop receipt records a clean tree at this commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `.datalad/config` | Large maps use Git-annex pointers rather than Git blobs. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `logs/final-analysis-releaseinfo.json`, `pixi.toml` | Run logs record command and exit status, but no exact lock or environment hash links results to a pinned environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `git ls-files` | No README or Makefile provides installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md#Reproducibility`, `scripts/analyze.py` | The report names the runnable script and exact pixi command; scripts/analyze.py is the analysis entry point. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/analyze.py` | The analysis resolves inputs and outputs relative to its own repository root. |
| must/010 | P.1 | met | judgement | `scripts/analyze.py`, `pixi.toml` | Imports are covered by pixi.toml directly or through declared Nilearn dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md#Reproducibility` | Pixi platform targets are stated, but Pixi installation and TemplateFlow network access are undocumented host prerequisites. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `scripts/analyze.py` | Package requirements are listed, but the host Pixi bootstrap and required network access are not documented. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is version-controlled with the analysis. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No environment lock/update command or dependency-update history establishes a repeatable update process. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `git ls-files pixi.lock` | pixi.toml is shared, but wildcard versions and the absence of pixi.lock do not freeze the environment. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/judgment/remote-fsck-full.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/worker-end-state.json` | The hub currently serves the exact commit and all annex payloads, but the receipt cannot attribute annex publication to the worker stop. |
| must/017 | D.1 | unmet | judgement | `results/report.md#Reproducibility`, `pixi.toml` | The report gives a command but does not explain how to install or obtain the environment specification. |
| should/001 | T.2 | met | judgement | `git ls-files`, `results/group_mean_gain_effect.nii.gz` | Git versions text and code while Git-annex tracks large binary content within the same repository. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | There is no CI configuration that checks the documented workflow. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, analysis code, results and environment specification occupy distinct paths. |
| should/004 | E.1 | not-checked | probe:fresh-rerun+judgement | `2026-10-16-fresh-rerun.json` | The only replay attempt was invalidated when the runner deleted input/participants.tsv before execution; no retry was authorized. |
| should/005 | E.1 | unmet | judgement | `results/report.md#Reproducibility` | pixi run reuses the project environment; no disposable environment is created per execution. |
| should/006 | D.2 | unmet | probe:ci-present | `pixi.toml` | No locked environment or CI job regularly tests environment reconstitution. |
| should/007 | D.2 | unmet | judgement | `git ls-files`, `pixi.toml` | The environment is described by package declarations only; no environment artifacts are archived. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No environment update command is declared and no update instance appears in history. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the object contains no restricted data or software component; the supplied maps are publicly retrievable. |
| may/001 | M.2 | unmet | judgement | `.gitmodules`, `input/data and pixi.toml` | No external data or software is included through submodules; maps use annex and packages use Pixi. |
| may/002 | M.2 | unmet | judgement | `results/report.md` | Directories separate inputs, code and results, but no document explains modular composition. |
| may/003 | M.2 | unmet | judgement | `scripts/analyze.py` | All components share one repository and the script assumes fixed paths; boundaries are not independently versioned. |
| may/004 | M.2 | unmet | judgement | `scripts/analyze.py` | No module composition mechanism is provided beyond the single analysis script. |
| may/005 | M.2 | partial | judgement | `results/report.md`, `git ls-files` | The results report links figures and names the analysis command, but gives no guide to the input/code/environment boundaries. |

## Flagged items

- **must/006 — probe-overridden:** the derived-output probe missed committed con-duct run records. Those logs record the command and exit status, but no exact lock/hash links the run to a frozen environment; the verdict is partial.
- **must/008 — probe-overridden:** the entry-point probe missed `scripts/analyze.py` and the command in `results/report.md`; a documented starting point exists even though a README/Makefile setup guide does not.
- **must/016 — unverified-claim:** exact-commit retrieval and payload verification succeeded now. The worker receipt records remote Git refs but not the timing of annex copies, so worker publication credit is partial.
- **should/004 — probe-overridden:** the fresh-rerun action classified the command failure as a pipeline failure, but the runner itself removed the required `input/participants.tsv` before execution. The sole allowed attempt was consumed; a clean replay is not checked.
- **should/008 — upstream-duplicate:** this repeats must/014 and is answered from the same absence of an environment update process.

## Not checked

- **should/004:** a replay from a fresh clone after the runner stops deleting `input/participants.tsv` as a shipped output would settle this. The failed attempt and retained workspace are in [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json) and [replay-workdir](replay-workdir/).
- No cross-host portability claim is made. The fresh replay and remote retrieval ran on the same Darwin host.

## Goals and kind

**Assumption (not confirmed with a human):** this is a **study** whose product is a group-level analysis and report testing the positive gain-effect hypothesis in vmPFC for the supplied 54 equal-indifference participants. This goal comes from the retained `input/study-task.md` and the coordinator-supplied brief. Study emphasis therefore falls on traceable analysis, usable instructions, environment reproducibility and access to the inputs and results.

## Scientific adequacy (separate from STAMPED)

**Classification: qualified.** The results support the narrower conclusion that these supplied participant maps do not show corrected evidence for a positive vmPFC group effect. All 54 maps are included; the one-sample, equal-participant-weight model and the full-mask one-sided Bonferroni test are defensible conditional on the supplied first-level estimates. The vmPFC sphere mean is -0.0057 model units (95% CI [-0.0323, 0.0210]), *t*(53) = -0.43, one-sided *p* = .664; no voxel in the sphere survives whole-brain correction. The 11 Bonferroni-significant voxels are posterior and outside the sphere. This follows the original NARPS instruction to use whole-brain corrected inference ([Hypothesis 1 instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). This is a lack of support for the positive hypothesis, not evidence of a true zero effect or absence of individual responses.

Qualification is warranted because the 12 mm sphere at MNI (0, 40, -12) is an operational anatomical choice without a cited independent atlas or prespecified external definition in the retained artifacts. Participant variance maps are absent, so the group analysis weights participant estimates equally and cannot propagate first-level uncertainty. The supplied gain maps reflect a variance-normalized regressor from separate gain/loss models, so effects are not currency-unit slopes. The sign-flip max-T sensitivity produced extreme null maxima and no discoveries; the report acknowledges this instability. Primary Bonferroni inference still depends on approximately Gaussian participant effects. These limits narrow the interpretation to the fixed upstream model and provided maps.

## Retrieval, replay and worker-stop attribution

- **Recipient:** a researcher using the declared authorized hub route (anonymous access was not required). **Route:** DataLad clone `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git`, checkout `e0a8fb1ae78b457a38ff7102825b1d8bc63119b4`, then `datalad get` for `input/data` and the two annexed group maps. **Coverage:** Git-tracked code, report, metadata and environment declaration, plus all 54 participant maps and both annexed result maps; all 56 annex objects passed fsck. **Host scope:** same Darwin host only; this does not demonstrate cross-host portability. See [remote-ls-remote.stdout](remote-ls-remote.stdout), [remote-clone.stdout](remote-clone.stdout), [remote-get.stdout](remote-get.stdout), and [remote-fsck-full.stdout](remote-fsck-full.stdout).
- One authorized fresh replay ran from a fresh clone of the local source, after the runner removed its detected outputs. It mistakenly included the required input table among those outputs, then the documented entry command failed with `FileNotFoundError` for `input/participants.tsv`. The retained record identifies this cause. No second attempt was made.
- The external worker-stop receipt (SHA-256 `a894ffb989c1f46af6a4c26a7259973fb6a9d2672ed974db0574c50d03823271`) records this commit, a clean worktree, and remote-tracking Git refs. It does not record annex-copy timing. Current retrieval is verified, but a coordinator-side annex upload after worker stop cannot be credited to worker publication practice. The source object's scientific artifacts are assessed as retained.

The separate probe extra `license-declared` is **unmet**: no license declaration was found in the tracked object. This extra has no checklist item and does not change the denominators above.

## Checklist and record

Checklist link: [2026-10-16-url.txt](2026-10-16-url.txt). Canonical per-item response: [2026-10-16-response.json](2026-10-16-response.json). Replay record: [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json). The response validates against pinned checklist 0.3.1.

Assessor stamp: `assess-alignment-with-stamped-principles@0.1.0`; `stamped-conventions@0.1.0`; Codex API / GPT-6 (exact runtime versions unavailable); date 2026-10-16 UTC. The target kind and goals above are explicit assumptions because no human was attached.
