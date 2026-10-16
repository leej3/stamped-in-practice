# STAMPED and scientific assessment

**STAMPED verdict:** 10/17 MUST met, 5 partial, 2 unmet; 2/9 SHOULD met, 5 unmet, 1 not-checked, 1 not-applicable; 0/5 MAY met, 2 partial, 2 unmet, 1 not-applicable. A partial MUST does not satisfy the item. These are item counts, not an overall score.

**Object:** `f30190d8144a9e15acfa1c0d973eadf0d655c83c` (`study`)
**Assessment date:** 2026-10-16 UTC
**Scientific adequacy:** **qualified**

## Assumption, goal and scope

**Assumption (not user-confirmed):** this is a single-study research object whose goal is to answer the supplied NARPS Hypothesis 1 question at the group-analysis stage, conditional on the supplied 54 participant gain-effect maps and metadata. The upstream participant models are fixed. No human was attached to confirm the object kind or goal.

The requested commit was verified with `git -C "$STAMPED_JUDGE_TARGET" rev-parse HEAD` before inspection. The retained `input/study-task.md` SHA-256 is `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`, matching the supplied brief (`task-brief-sha256.txt`). The assessment covers that committed state, the recorded Git/annex retrieval routes, and one authorized fresh-clone replay. No source files were changed, no raw time-series data were downloaded, and the fixed upstream analyses were not rerun. The replay clone and its outputs remain in `replay-workdir/` for preservation. Coordinator guidance folders and other judgments were not read.

The target reveals the equal-indifference cohort label and participant IDs. This is a blinding limitation for those fields; it was not used to infer or report any treatment assignment.

## Scientific finding

The analysis provides **no whole-brain-corrected evidence for a positive vmPFC gain effect** in the supplied equal-indifference maps. Its one-sided participant sign-flip max-t test reports 24 positive voxels surviving whole-brain FWE, all in posterior locations, with no surviving voxel in the operational vmPFC ROI (0/1,297). The whole-brain peak is posterior (MNI −26, −102, −3.6 mm; t=6.62; max-t pFWE=0.0008). The descriptive bilateral AAL3 medial-orbitofrontal mean is −0.0079 model units (95% t interval −0.0346 to 0.0188). See `results/report.md`, `results/analysis_results.json`, `results/group_summary.csv`, `results/whole_brain_fwe_clusters.csv`, and the saved maps/figures.

**Conclusion about the hypothesis:** not supported by these supplied group-stage maps under the reported model and whole-brain FWE procedure. That is a defensible absence of positive evidence, not evidence that the true effect is zero. The interval spans zero and no equivalence bound was set.

**Why adequacy is qualified:** the analysis uses all 54 mapped participants, checks IDs, hashes, common geometry and finite values, treats maps as first-level coefficients rather than test statistics, and uses a directional whole-brain max-t correction. Equal participant weighting is reasonable because participant variance maps were not supplied. The report also states the sign-flip symmetry assumption, retains the single flagged participant, gives a leave-one-out sensitivity summary, and does not interpret the coefficient as change per dollar. However, the vmPFC label is an operational proxy (bilateral AAL3 `Frontal_Med_Orb` parcels) resampled to the supplied MNI152NLin2009cAsym grid; no explicit atlas-to-template registration check is recorded. This limits anatomical precision. The common nonzero intersection is a defensible way to exclude zero padding, but defines the tested search space by shared nonzero coverage. These qualifications do not turn posterior corrected peaks into evidence for vmPFC.

The separate gain model and standardized gain modulator do not support a gain-versus-loss comparison or a per-currency response claim. Results are conditional on upstream AO86 choices; alternative first-level models and inverse-variance group modeling cannot be assessed from the supplied data.

## Replay and retrieval

The single authorized command was `pixi run python scripts/group_analysis.py --permutations 5000 --seed 20261015`. The runner cloned the exact local result commit on the **same host**, retrieved 0.1 GiB through the configured Git-annex transport, and all 54 map payloads matched the SHA-256 values in `input/sources.json`. It then removed nine files it identified as shipped outputs. This list included `input/participants.tsv`, which the documented script requires as an input. The runner committed this cleanup in the replay workspace (post-cleanup HEAD `b4a0572`); its parent is the requested source commit, as recorded in `replay-clone-history.txt`. The entry consequently exited 1 with `FileNotFoundError` before analysis; no existing result was accepted as replay evidence. The command, runner receipt, stdout/stderr, exit status and retained clone are in `replay-attempt-01.*`, `2026-10-16-fresh-rerun.json`, and `replay-workdir/`.

The failure establishes that this one replay did not reproduce results, but the immediate missing-file cause was the runner’s output-removal step. It does not establish that the script fails when its required tracked input remains in place. No second replay was attempted under the one-attempt limit.

**Access evidence (must/016):** intended recipient is a researcher using the declared Git/DataLad authorized route; anonymous access is not required. The Git route is `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git` (also `git@github.com:leej3/stamped-in-practice.git`); the annex route is `annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp`. Required coverage is the code, `pixi.toml`, cohort/method metadata, all 54 participant maps, and the atlas assets used by the script. Both Git endpoints advertised the exact commit; the replay clone retrieved all 54 maps and their manifest checksums matched. The retrieval was same-host and does not establish cross-host portability. The successful content retrieval is recorded separately from the unsuccessful analysis replay.

## Worker-stop attribution

The supplied external receipt records worker HEAD `f30190d8144a9e15acfa1c0d973eadf0d655c83c`, worker exit 0, and an empty worktree status. Its 149-entry inventory matches the retained target paths, file hashes and annex pointer targets. It also records remote-tracking refs at the worker stop; current GitHub and con-hub listings still advertise the exact commit. Thus versioning and tracking at the recorded stop are attributable to the worker. Later coordinator preservation is not credited as worker action. Annex payload bytes were independently checked against the source manifest for all 54 participant maps; inaccessible local annex objects were not treated as hash-verified from the retained checkout itself. Receipt copy and hash: `worker-end-state-receipt.json` (SHA-256 `97caecab5ddac2f1b7bfa033e1b20470c263523c6cf88bb1fc34482c0ab55e25`).

## What to address first

1. Pin the execution environment (commit a lockfile or equivalent) and link the exact environment to the run record; include Pixi setup/version instructions.
2. Add a README or equivalent installation and usage guide, and ensure the clean replay procedure preserves required inputs such as `input/participants.tsv` while removing generated outputs.
3. Record repeated successful fresh-environment runs if claiming regular workflow testing.

## Existing strengths

The result commit is clean and the worker-stop receipt matches its retained inventory. Source maps have per-file checksums and traceable source metadata; data/code/results/environment are separated in the root. The report is explicit about the effect estimate scale, one-sided correction, exclusions, outlier sensitivity, uncertainty and limits of the fixed upstream model. It supplies reproducible analysis code, machine-readable results and informative figures.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `pixi.toml`, `input/study-task.md` | All source, code, environment and results files sit beneath this study root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `scripts/group_analysis.py` | The 54 maps and cohort metadata are in-root Git-annex/Git files; the script resolves them from the project root. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `results/reference-atlas-cache/README.md` | Python analysis packages are declared in pixi.toml; atlas files are cached in the object. |
| must/004 | T.1,T.3,T.5 | met | judgement | `scripts/group_analysis.py`, `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/worker-end-state.json` | Git tracks code, text, documentation and configuration; the worker-stop receipt records a clean tree at this commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/2026-10-16-fresh-rerun.json` | Git-annex tracks the large maps; the fresh clone retrieved all 54 with manifest SHA-256 matches. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `logs/group-analysis-releaseinfo.json`, `pixi.toml` | Run logs record the command and host, but no locked environment was attached to these results. |
| must/007 | A.1 | unmet | probe:entry-point | `results/report.md` | No README.md or Makefile gives installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `scripts/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/2026-10-16-fresh-rerun.json` | The report names the main analysis script and exact command; the replay wrapper removed a required input before execution. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/group_analysis.py` | The analysis resolves inputs and outputs relative to its own project root. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `pixi.toml`, `results/report.md` | Analysis imports are declared, but running the documented route also assumes an installed Pixi CLI whose version is unspecified. |
| must/011 | P.1 | met | judgement | `pixi.toml` | The manifest documents supported macOS 14 arm64 and linux-64 platforms and Python bounds. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md` | pixi.toml lists package dependencies and platforms, but does not document installing or pinning the required Pixi CLI. |
| must/013 | P.3 | met | probe:env-spec-tracked+judgement | `pixi.toml` | pixi.toml is tracked alongside the analysis and inputs. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log: pixi.toml` | No dependency-update or lockfile regeneration process is documented or recorded. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `pixi.toml`, `logs/group-analysis-releaseinfo.json` | pixi.toml allows ranges and wildcards; no lockfile or exact environment capture pins the result environment. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/remote-hub-ls-remote.txt`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/remote-github-ls-remote.txt`, `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/2026-10-16-fresh-rerun.json` | For a researcher using the configured Git/annex route, both remotes expose this commit and the fresh clone retrieved all 54 map payloads with matching hashes. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md`, `pixi.toml` | The report gives a Pixi reproduction command, but omits setup instructions for obtaining Pixi and the environment. |
| should/001 | T.2 | met | judgement | `.gitattributes`, `git log -1` | Git tracks the study, with git-annex extending the same repository for large binary files. |
| should/002 | A.2 | unmet | probe:ci-present | `logs/group-analysis-releaseinfo.json` | No CI or recurring workflow tests the documented instructions; the history shows a single manual release run. |
| should/003 | M.1 | met | probe:modules-separated | `input/`, `scripts/`, `results/`, `pixi.toml` | Inputs, analysis code, outputs and environment specification occupy distinct top-level paths. |
| should/004 | E.1 | unmet | probe:fresh-rerun+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/2026-10-16-fresh-rerun.json` | The sole fresh-clone attempt failed before analysis because the runner removed required input/participants.tsv; no successful clean-environment test exists. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `pixi.toml` | The documented pixi run uses a persistent project environment; no workflow creates a disposable environment per run. |
| should/006 | D.2 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-02/judgment/2026-10-16-fresh-rerun.json`, `pixi.toml` | The only fresh reconstitution failed before analysis, so successful reconstitution of the result environment remains unverified. |
| should/007 | D.2 | unmet | judgement | `pixi.toml`, `git ls-files` | No executable environment, package archive or container image is archived in the study. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | The study has no documented dependency update or environment regeneration process. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the object declares public NeuroVault/OpenNeuro inputs and ordinary public software; no restricted component is in scope. |
| may/001 | M.2 | unmet | probe:subdatasets-resolvable+judgement | `.gitmodules`, `pixi.toml`, `input/data/` | The external inputs and software are not submodules; maps use git-annex and packages use Pixi. |
| may/002 | M.2 | partial | judgement | `results/report.md`, `input/upstream-methods.md` | The report links the main script and key results, but does not document the component relationships or recombination. |
| may/003 | M.2 | unmet | judgement | `git ls-files`, `scripts/group_analysis.py` | Input, code and results are folders in one workflow, not independently versioned boundaries. |
| may/004 | M.2 | not-applicable | judgement | `.gitmodules`, `scripts/group_analysis.py` | N/A: this study has one in-repository group-analysis workflow and no modules to compose. |
| may/005 | M.2 | partial | judgement | `results/report.md`, `input/study-task.md` | The report helps locate code and results, but no project guide explains the structure or how components relate. |

## Flagged items

- **must/008:** the entry-point probe found no README/Makefile route, but `results/report.md` documents the script and command. The failed replay was due to runner deletion of a required input, so the probe verdict was overridden.
- **must/013:** the probe treated the missing lockfile as partial despite the committed `pixi.toml`; this item asks whether an environment specification is tracked. The no-lock limitation is assessed under must/015.
- **must/016:** the probe did not independently verify retrieval. Direct Git remote listings and the fresh clone’s successful retrieval of all 54 manifest-matched maps establish current access for the declared route.

## Not checked

- **should/006:** the single fresh environment reconstruction failed before the script could use its inputs; successful recurring reconstruction of the result environment remains unverified.

## Checklist link and provenance stamp

Checklist app URL: see [`2026-10-16-url.txt`](2026-10-16-url.txt). The validated machine-readable response is [`2026-10-16-response.json`](2026-10-16-response.json); probe results are [`2026-10-16-probes.json`](2026-10-16-probes.json), and the replay receipt is [`2026-10-16-fresh-rerun.json`](2026-10-16-fresh-rerun.json).

STAMPED checklist 0.3.1; skill `assess-alignment-with-stamped-principles` 0.1.0; conventions 0.1.0; harness OpenAI Codex API; model GPT-6. Coordinator runner source commit `b86e37ff9115e37541fd47aca73f49e13b5110bb`, runtime environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Runtime check and every checklist response helper action were run through the coordinator-supplied runner.
