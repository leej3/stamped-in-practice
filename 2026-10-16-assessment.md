# STAMPED assessment — NARPS potential-gain study

Assessment date: 2026-10-16 (UTC). Assessed commit: `a424c3e8ae47f9208fa661fc4f974f6b187acb00`. Initial HEAD verification is recorded in [evidence/initial-commit-verification.stdout](evidence/initial-commit-verification.stdout). The object remained unchanged.

## Verdict

- **MUST:** 7/17 met, 4 partial, 6 unmet, 0 not-checked.
- **SHOULD:** 2/9 met, 1 partial, 5 unmet, 0 not-checked, 1 not-applicable.
- **MAY:** 3/5 met, 1 partial, 1 unmet.

No overall score is assigned.

## What to fix first

1. Commit a resolved environment lock, pin the Pixi bootstrap version, and include that identity in each run record → exact dependencies can be tied to the results → **must/003, must/006, must/010, must/014, must/015, should/006, should/008**.
2. Add a README or Makefile with environment installation, system/network prerequisites, execution steps, and the authorized annex retrieval route → a new researcher can obtain and run the object → **must/007, must/011, must/012, must/016, must/017**.
3. Publish and document a retrievable annex route for all inputs and derived annex payloads, then verify it from a researcher clone → Git history alone does not provide the complete object → **must/016**.
4. Make the documented entry point regenerate the report as well as numerical outputs, then retain a complete run record → the approved replay reproduced 13 outputs, while `results/report.md` was missing after rerun → **must/006, should/004**.
5. Add a regular clean-environment workflow that reconstitutes the pinned environment and results in a disposable run context → instructions and result production can be checked over time → **should/002, should/004, should/005, should/006, should/007**.

## What the project already does well

- The worker-stop receipt and retained checkout agree on the exact commit, clean status, and all 114 indexed paths; the worker snapshot also records all 58 annex payloads locally available. See [worker-stop-audit-2.json](worker-stop-audit-2.json).
- The input manifest records source URLs and checksums; all 54 NeuroVault maps were retrieved and matched their expected byte counts and SHA-256 values. See [source-map-retrieval.json](source-map-retrieval.json).
- The analysis checks hashes, finite voxel values, participant identity, and image grids. It uses an all-participant support intersection and saves code, quality tables, numerical results, and two figures. See `analysis/run_group_analysis.py`, `results/map_quality.tsv`, and `results/report.md`.

## Per-item table

The following table was rendered from the canonical response using the frozen runner.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files`, `input/sources.json` | All project artifacts reside under this repository root, with annex payloads stored beneath its Git metadata and input sources linked in the tracked manifest. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/source-map-retrieval.json`, `input/study-task.md` | All 54 fixed maps are in the annex and their declared NeuroVault URLs retrieved with matching sizes and SHA-256 values; task and metadata are inside the root. |
| must/003 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `logs/group-analysis-final-info.json`, `input/data/sub-001_hypo1_cope.nii.gz` | Analysis libraries are in pixi.toml, but run logs invoke Pixi and annex inputs require git-annex; neither host tool has a pinned in-object installation route. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `probe:tree-clean`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/worker-stop-audit-2.json` | Git tracks code, text and configuration; the worker-stop receipt records a clean tree at this commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `results/mean_gain_cope.nii.gz` | Large binary content is stored in git-annex; 58 pointers are tracked and no binary blob over 10 MiB is in Git. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/group-analysis-final-info.json`, `pixi.toml`, `git ls-files pixi.lock` | Run logs name the command, but no frozen lock or environment identity links the generated outputs to exact dependencies. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-files README.md Makefile`, `results/report.md` | No README.md or Makefile provides installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `logs/group-analysis-final-info.json` | The report links the analysis script, and the recorded command is pixi run python analysis/run_group_analysis.py. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | No host-specific absolute paths were found in tracked text files. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/run_group_analysis.py`, `pixi.toml`, `logs/group-analysis-final-info.json` | The script imports are supplied by pixi.toml, but Pixi is required by the recorded command and is not declared or pinned within the environment. |
| must/011 | P.1 | unmet | judgement | `pixi.toml`, `analysis/run_group_analysis.py`, `results/report.md` | pixi.toml lists macOS and Linux targets, but Pixi installation and network access for atlas retrieval are not documented for a new host. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md` | pixi.toml lists Python packages and target platforms; no install instructions identify Pixi, git-annex or network access as system prerequisites. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | The tracked pixi.toml defines the analysis environment alongside code and data. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `.gitignore`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/evidence/environment-history.stdout` | No dependency update process is documented; pixi.lock is ignored and no tracked lock update process appears in project history. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml`, `.gitignore`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/evidence/environment-absent-files.stdout` | pixi.toml uses mutable ranges and wildcards; pixi.lock is ignored and absent from the committed object. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/worker-stop-audit-2.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/evidence/retrieval.stderr` | At worker stop the receipt confirms local annex bytes and matching Git refs, but not recipient retrieval; the public GitHub route could not fetch annex payloads. |
| must/017 | D.1 | unmet | probe:entry-point+judgement | `pixi.toml`, `results/report.md` | No documentation explains how to obtain and use the environment specification on a new machine. |
| should/001 | T.2 | met | judgement | `git ls-files`, `input/data/sub-001_hypo1_cope.nii.gz` | Git tracks code, text and configuration; git-annex tracks large content in the same Git repository model. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No tracked CI workflow regularly checks that the documented analysis remains executable. |
| should/003 | M.1 | met | probe:modules-separated | `probe:modules-separated` | Inputs, code, results and environment are separated under input/, analysis/, results/ and pixi.toml. |
| should/004 | E.1 | partial | probe:fresh-rerun+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/2026-10-16-fresh-rerun.json` | A same-host clone reproduced 13 outputs exactly; report.md was absent, and replay did not use a container, batch job, clean VM or cloud host. |
| should/005 | E.1 | unmet | judgement | `logs/group-analysis-final-info.json`, `analysis/run_group_analysis.py` | The recorded pixi run uses a reusable project environment; no workflow creates and discards a separate environment per execution. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/judgment/2026-10-16-fresh-rerun.json`, `pixi.toml` | No recurring check rebuilds the exact environment used for these results; no exact lock exists, though one current-spec replay matched 13 outputs. |
| should/007 | D.2 | unmet | judgement | `pixi.toml`, `git ls-files` | The object archives the pixi.toml specification but no installed package binaries or environment image. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `.gitignore` | No dependency update process is documented or tracked; this item duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: all input and software sources are public; this object contains no restricted component. |
| may/001 | M.2 | unmet | judgement | `git ls-files .gitmodules`, `input/sources.json` | External maps are managed through git-annex and source URLs; the project has no Git submodules. |
| may/002 | M.2 | partial | judgement | `results/report.md` | The report describes inputs, code and results, but does not explain independent module relationships or how to recombine them. |
| may/003 | M.2 | met | judgement | `analysis/run_group_analysis.py`, `input/sources.json`, `pixi.toml` | Input, analysis, result and environment boundaries have distinct paths and interfaces; the script reads the manifest and writes under results/. |
| may/004 | M.2 | met | judgement | `analysis/run_group_analysis.py`, `results/report.md` | The group-analysis script combines the fixed inputs with the environment and writes the listed results. |
| may/005 | M.2 | met | judgement | `results/report.md`, `input/sources.json` | The report and source manifest help readers locate methods, inputs, code, quality checks, results and figures. |


## Flagged items

- **must/006 — mapping-questioned:** the probe treated the absence of a DataLad run record or tracked workflow as absence of any run record. The committed `logs/group-analysis-final-info.json` does record a successful command; the item remains unmet because no exact lock/environment identity is linked to the outputs.
- **must/008 — probe-overridden:** the entry-point probe missed the script reference in `results/report.md` and the completed command in the run log. Those provide a clear reproduction starting point; setup instructions remain absent under must/007.
- **must/014 and should/008 — upstream-duplicate:** the pinned checklist repeats the same environment-update question.

## Probe-only extras

- **License declaration — unmet:** no tracked license file or dataset license field was found. The checklist has no license item; see the `license-declared` extra in `2026-10-16-probes.json`.
- **Clone weight — met:** no text blob exceeded 10 MiB.
- **Inputs untouched — not-applicable:** there are no linked submodules/subdatasets for that probe to compare.

## Not checked

None of the 31 checklist items remains not-checked. The same-host replay does not establish portability to another host.

## Goals and kind

**Assumption (not confirmed with a human):** the goal is to report a group-level test of the positive potential-gain effect in vmPFC for the supplied NARPS equal-indifference cohort, conditional on the fixed AO86 participant maps. This follows `input/study-task.md` and `input/upstream-methods.md`. The primary kind is **study**, so the assessment emphasizes a self-contained, tracked, actionable and distributable answer, including its exact run provenance.

## Access and worker-stop attribution

**Intended recipient:** a researcher authorized to access the project’s annex-capable hub for the binary artifacts, and researchers with public internet access for the documented NeuroVault source maps. No anonymous access is required for the hub route.

**Routes and checks:** the public HTTPS GitHub route returned the exact commit. The 54 input-map URLs in `input/sources.json` each returned bytes matching the manifest. A fresh public GitHub clone could not retrieve the 58 annex payloads with `git annex get`. The assessment replay cloned the local source on the same host and fetched all 58 payloads through the checkout-configured `con-hub` route (`https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git`; annex P2P HTTP at `https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp`) before deleting shipped outputs and rerunning. This route was available to the authorized assessment host, but its URL is only in local Git configuration and is absent from committed instructions. The worker receipt does not establish the route was used by an intended recipient at worker stop. Required coverage is the 54 participant maps plus four annexed result files, along with the tracked code, metadata, environment description, report, tables, figures and remaining Git results. Retrieval and replay were on the same host; no cross-host portability claim follows.

**Worker state:** the external receipt at `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-04/judgment-02/worker-end-state.json` (SHA-256 `c412bb1e086138c7b6e914bff36d5f204221ca3d98a75e46b1e36fbf57d254f7`) records the worker exiting cleanly at the assessed commit. Its index matches all 114 retained paths, and it records 58/58 annex payloads available in the worker worktree. Git refs for the commit existed at worker stop. The receipt does not establish a recipient’s retrieval of annex bytes. The public GitHub check retrieved only Git content. The later same-host replay verified the retained object’s current configured retrieval route; that later preservation evidence is not credited as worker publication.

The first receipt-summary attempt counted annex fields in the Git index rather than the receipt’s worktree inventory. It is retained as `worker-stop-audit.json`; the corrected [worker-stop-audit-2.json](worker-stop-audit-2.json) reports 58 available payloads. All command transcripts, stdout/stderr, failed retrieval output, generated artifacts, and the replay workspace are retained under `evidence/`, `retrieval/`, and `replay/`.

## Scientific adequacy

**Classification: supported**, for the report’s stated conclusion that the supplied data give no whole-brain-corrected support for a positive vmPFC effect under this group model. This classification evaluates the reported conclusion, separately from STAMPED object quality. The NARPS instructions call for whole-brain-corrected hypothesis decisions and whole-brain statistical maps ([original instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The analysis includes the complete 54-person cohort, checks each image hash, shape, affine and finite values, and uses the intersection of nonzero support across participants (198,029 voxels). This avoids treating missing estimates outside a participant’s estimation mask as zero. No participants were excluded. The one-sample positive t test uses participant-level sign flips and the maximum positive t across the analysis mask for one-sided whole-brain family-wise error correction at 0.05 (5,000 flips; seed 20261015). The observed threshold is t=5.36. Twenty-four corrected voxels occur in three small posterior clusters; the peak is at MNI (−26, −102, −3.6), FWE p=0.0008, and no corrected voxel overlaps the operational vmPFC approximation.

The vmPFC definition combines four Harvard-Oxford labels with explicit coordinate limits and is described as an approximation. Its descriptive participant-average coefficient is −0.0011 (95% t interval −0.0228 to 0.0207); the strongest ROI voxel has whole-brain FWE p=0.788. The interval includes small positive and negative values, so it does not establish an exact zero effect. The supplied coefficients are mean-centered, variance-normalized gain-regressor estimates, not BOLD change per currency unit. Gain and loss came from separate upstream models. Participant variance maps are absent, so precision weighting and first-level uncertainty propagation were unavailable. Sign-flip inference assumes exchangeable, approximately symmetric participant effects under the null; the report discloses this assumption.

Both figures are informative: one shows the uncorrected display threshold and prints the whole-brain corrected threshold; the other shows participant-level ROI means and a confidence interval. The group-map figure does not draw the vmPFC outline mentioned in the analysis-script comment, so the ROI is located through the separate participant plot and textual definition. This does not alter the corrected whole-brain inference.

The scientific conclusion is a defensible absence of corrected positive evidence in this analysis. It does not establish that vmPFC is unresponsive, that the true effect is zero, or that a different defensible vmPFC boundary or upstream model would yield the same result.

## Checklist URL and provenance stamp

The checklist app link is stored in [2026-10-16-url.txt](2026-10-16-url.txt); the canonical record is [2026-10-16-response.json](2026-10-16-response.json). The response passed both the frozen response validator and the runner’s `validate` shortcut.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1, on `git@github.com:leej3/stamped-in-practice.git` at commit `a424c3e8ae47f9208fa661fc4f974f6b187acb00`, 2026-10-16, Codex API / GPT-6 (specific runtime versions not exposed). The coordinator runner checked source commit `b86e37ff9115e37541fd47aca73f49e13b5110bb`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`, and lock SHA-256 `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`. Probe output: `2026-10-16-probes.json`. Fresh replay record: `2026-10-16-fresh-rerun.json`.
