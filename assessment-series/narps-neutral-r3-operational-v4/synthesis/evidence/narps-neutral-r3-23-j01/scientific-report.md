# Independent assessment: NARPS potential gain and vmPFC

**Assumption and scope.** The documented goal is a group-stage study of whether potential gain has a positive fMRI effect in vmPFC for the NARPS equal-indifference group. I assess this as a **study**. No human guidance was attached, so the goal and kind are not confirmed. The worker’s complete stopped delivery is the evidence boundary, including untracked files and annex content. All `content/workspace/...` citations below are relative to the canonical capture with SHA-256 `bdc6ab6e1a56690cadf0e17be607d358775058bec737d030a064492413234dae`; the original captured HEAD is `82443e43a1171f47c085c5e0fadc9e8132a12053`.

**STAMPED verdicts:** MUST: 4 met / 1 partial / 12 unmet / 0 not-checked (17 total). SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total). MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable (5 total). These are per-item verdicts, not an overall score.

## Scientific assessment

**Scientific adequacy: supported.** The delivered analysis supports the stated conclusion that these maps do not provide whole-brain-corrected evidence of a positive vmPFC effect. It includes all 54 equal-indifference participants, validates image dimensions/affines and finite values, defines common support as nonzero in at least 49/54 maps, and reports no exclusions. It tests a one-sided participant-level sign-flip maximum-*t* statistic over 210,968 voxels (9,999 permutations, plus-one Monte Carlo *p*), applying whole-brain FWE correction. The vmPFC proxy is explicitly coordinate-defined before effect inspection (|x|≤10, y=30–60, z=−20–0 mm); no voxels in it pass whole-brain correction. The ROI mean is −0.0061 cope (95% *t*-interval −0.0317 to 0.0195; one-sided sign-flip *p*=.6809), and the whole-brain peak is posterior occipital, outside vmPFC. The ROI interval spans both signs, so this is lack of evidence for a positive effect, not evidence of exact zero or equivalence. The code, report, summary, tables, maps and figures are at `content/workspace/analysis/analyze.py`, `content/workspace/analysis/report.md`, `content/workspace/analysis/results/summary.json`, `content/workspace/analysis/results/participant_qc.tsv`, `content/workspace/analysis/results/fwe_clusters.tsv`, `content/workspace/analysis/results/group_p_fwe_maxT.nii.gz`, `content/workspace/analysis/figures/wholebrain_mean_and_fwe.png`, and `content/workspace/analysis/figures/vmPFC_participant_effects.png`.

The approach is defensible for the fixed supplied inputs: participant copes are treated as independent observations and equally weighted; the sign-flip null assumes exchangeability under sign reversal. Participant variance maps are absent, so uncertainty from first-level estimates cannot be propagated in a precision-weighted model. The 90% nonzero-support rule and geometry checks are inspectable but do not validate the upstream models. The upstream gain regressor was centered and variance-normalized, so cope is not BOLD change per currency unit; separate gain/loss models and a gain range twice the loss range also limit cross-valence interpretation. The report states these boundaries. The ROI is one explicit, defensible vmPFC operationalization, not the only possible anatomical boundary. Its descriptive, uncorrected ROI statistic is not substituted for required whole-brain inference.

## Hypothesis outcome

> **The supplied gain-effect maps do not support a greater vmPFC response with increasing potential gain.**

This is the reported hypothesis outcome, separate from the adequacy label above. The corrected whole-brain analysis found 24 significant voxels in three small posterior occipital clusters (peak *t*=6.62, max-*t* FWE *p*=.0006); vmPFC had no corrected voxels. The figures and tables make the spatial and participant-level results inspectable.

## Worker stop, integrity, access and replay

The worker-stop receipt (`worker-end-state.json`, SHA-256 `ddac0b5e79d52c1fea0b027f7b9a105b0a1809d294a3105ea5ca5b23c4bc7d25`) records a complete capture with no omissions and HEAD `82443e43a1171f47c085c5e0fadc9e8132a12053`. The canonical and operational manifest capture hashes match. Comparison of all 1,137 workspace entries against the operational initial manifest found no scientific-file, link, Git, index, ref, object, or configuration mismatch. Only regular-file changes under the supplied operational-metadata carve-out were observed: `.git/annex/keysdb/db` retained its size and mode but its SHA-256 changed from `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca` to `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`; `db-shm` and `db-wal` were absent initially and appeared as regular files of 32,768 and 0 bytes. These are the only differences (1,137 captured entries, 1,139 observed). Logical database equivalence is not established. The target Git status still shows the same untracked `.task-skills/` and `content/workspace/analysis/` directories. The runner’s Git/annex environment settings were retained. The inspection is based on unchanged captured scientific files; the metadata-only change does not enter scientific interpretation.

At worker stop, Git had a commit, but the delivered analysis and main outputs were untracked. I therefore do not treat the commit as versioning those results. No worker Git remote or publication route for the complete analysis object was recorded. The declared upstream route is NeuroVault collection 4932, with direct map URLs in `content/workspace/input/sources.json`; that file also identifies participant and methods sources. A HEAD request to one map URL on `neurovault.org` returned HTTP 200. The tested scope is only that host and one representative map endpoint: the other 53 maps, metadata hosts, and complete analysis/code/results routes were not tested. For a researcher using these declared upstream routes, input maps are identifiable, but those routes do not cover the worker’s analysis code, report, figures, results, or environment. Coordinator delivery is not evidence that the worker published those artifacts. No license was found in the captured study tree; reuse terms are unstated.

**Replay declaration and result.** Before the attempt I declared the report’s exact entrypoint: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/analyze.py`. Prerequisites were the already-existing named interpreter and captured in-copy annex inputs; I installed no packages and made no source changes. The selected outputs were the ten explicitly named files in `content/workspace/analysis/results/` and two figures in `content/workspace/analysis/figures/`, as listed in `2026-10-16-fresh-rerun.json`; only those outputs were removed in the helper’s fresh complete replay copy. The helper used one attempt, 7,200 seconds, `rtol=1e-6`, no automatic scientific-input retrieval, and its 5 GB compatibility parameter with no prefetch. All 12 selected artifacts were byte-identical to the shipped outputs. Thus the delivered entrypoint reproduced these outputs in this host’s pre-existing environment. This does not establish worker-side environment capture, a fresh machine environment, or general portability; the documented interpreter path is host-specific and its dependency versions are not supplied. The replay helper disabled captured Git hooks through its execution overlay without changing the captured configuration.

## Assessor malfunction

One response-edit helper call stopped during `must/010` after the frozen runtime reported a locally changed `pixi.toml`; the failed draft and observed error are retained in `assessor-malfunction.json`, `assessor-malfunction.stdout`, and `assessor-malfunction.stderr`. This affected response formatting only, not target inspection or replay. The frozen runner subsequently validated the retained complete response and the final response after the item edits; scientific adequacy and item measurements were not replaced.

The target inventory exposed `.task-skills/jupyter-notebook/` and `.entire/` session-material paths. I record that exposure; I did not use those contents as grading evidence, and I do not infer any treatment assignment.

## Item verdicts and evidence

Evidence paths below refer to the canonical capture SHA-256 stated above. Probe results are retained in `2026-10-16-probes.json`; coordinator replay and retrieval evidence are separate from worker-stop evidence.

| Item | Status | Evidence and reason |
|---|---|---|
| must/001 | met | Capture manifest; all study material is under `content/workspace/`. |
| must/002 | met | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/input/sources.json`; all 54 maps are annex-backed within the captured root. |
| must/003 | unmet | `content/workspace/analysis/analyze.py`, `content/workspace/analysis/report.md`; Python dependencies are assumed from an external prepared environment, not included or linked as a component. |
| must/004 | unmet | Captured HEAD plus stop-state `git status`; `content/workspace/analysis/` was untracked, including code, report and results. |
| must/005 | met | `content/workspace/input/data/` pointers and annex inventory; 54 maps are stored with git-annex. |
| must/006 | unmet | `content/workspace/analysis/results/summary.json`, `content/workspace/analysis/report.md`; there is no worker run record tying results and actions to an exact environment. |
| must/007 | partial | `content/workspace/analysis/report.md`; usage command is documented, installation and dependency setup are not. Probe’s README/Makefile pattern alone missed the equivalent report instructions. |
| must/008 | met | `content/workspace/analysis/report.md`, `content/workspace/analysis/analyze.py`; clear start script and command are provided. |
| must/009 | unmet | `content/workspace/analysis/report.md`; reproduction command contains a host-specific absolute `/Users/...` interpreter path. |
| must/010 | unmet | `content/workspace/analysis/analyze.py`, `content/workspace/analysis/report.md`; required packages are not declared in an environment specification. |
| must/011 | unmet | `content/workspace/analysis/report.md`; external Python path is assumed, while host/system requirements are not documented. |
| must/012 | unmet | `content/workspace/analysis/report.md`, `content/workspace/analysis/analyze.py`; no complete dependency or system requirements list. |
| must/013 | unmet | Probe inventory and captured tree; no tracked environment specification. |
| must/014 | unmet | `content/workspace/analysis/report.md`, `content/workspace/analysis/analyze.py`; no environment specification or dependency update process. |
| must/015 | unmet | `content/workspace/analysis/report.md`; no lock, image digest, or frozen package manifest. |
| must/016 | unmet | `content/workspace/analysis/report.md`; only a local prepared environment path is named, not a shareable environment artifact. |
| must/017 | unmet | `content/workspace/analysis/report.md`; instructions assume the external environment already exists and do not say how to obtain it. |
| should/001 | partial | Git/annex evidence and worker-stop status; one repository is used, but analysis remained untracked. |
| should/002 | not-checked | Probe found no recognized CI; no equivalent recurring worker test record was found. CI absence alone does not settle this. |
| should/003 | partial | `content/workspace/input/` vs `content/workspace/analysis/`; inputs are separated, but code and derived outputs share a module and there is no environment module. |
| should/009 | not-applicable | `content/workspace/input/sources.json`; no restricted data or software subject is identified. |
| should/004 | not-checked | Worker stop contains no clean-container/VM test record. The later coordinator replay is not worker practice. |
| should/005 | unmet | `content/workspace/analysis/analyze.py`; script writes into the workspace and does not spawn disposable environments. |
| should/006 | unmet | No environment specification or worker reconstitution record in the captured tree. |
| should/007 | unmet | `content/workspace/analysis/report.md`; runtime is referenced externally and no environment artifact is archived. |
| should/008 | unmet | No declared environment update process; duplicates must/014. |
| may/001 | not-applicable | No independently maintained software/data component; annex-managed maps are inputs in this project. |
| may/002 | partial | `content/workspace/input/`, `content/workspace/analysis/report.md`; directory roles are visible, but module relationships are not documented. |
| may/003 | partial | `content/workspace/analysis/analyze.py`; input/output paths are distinct but interfaces are implicit and runtime is external. |
| may/004 | met | `content/workspace/analysis/analyze.py`; script composes inputs and outputs through workspace-relative paths. |
| may/005 | met | `content/workspace/analysis/report.md`, `content/workspace/input/study-task.md`, `content/workspace/input/upstream-methods.md`; report links major files and describes task context. |

**Probe overrides and duplicate pin.** `must/002` is met after reading the internal annex-backed inputs; the subdataset probe did not inspect that mechanism. `must/007` is partial and `must/008` met because the delivered report provides usage instructions and a runnable script despite the entry-point probe’s README/Makefile heuristic. `must/009` is unmet because the probe scanned only tracked text; the untracked report contains an absolute environment path. `may/001` is not-applicable after inspection found no independent component, where the probe did not settle the item. `must/014` and `should/008` are the duplicated environment-update question and carry the `upstream-duplicate` flag.

**Not-checked items.** `should/002` lacks recurring worker test evidence; `should/004` lacks worker evidence of testing in a clean container, VM, batch job, or cloud instance. These are unavailable measurements, not failures inferred from coordinator replay.

## Highest-priority improvements and strengths

The most consequential reproducibility gap is the missing environment specification and result-to-environment provenance. The report already has a useful script, output inventory, scientific limitations, and maps handled in annex; committing the analysis deliverables and documenting an installable, pinned environment with a reusable retrieval route would make the stopped study materially easier to reproduce and share.

## Checklist link and provenance

Checklist app URL is stored in `2026-10-16-url.txt`. Response and evidence are in `2026-10-16-response.json`.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0; checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on the captured study workspace at original HEAD `82443e43a1171f47c085c5e0fadc9e8132a12053`, 2026-10-16. Frozen runner source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; the exact interactive harness/model variant was not independently supplied. Probe output: `2026-10-16-probes.json`. Capture identity: canonical delivery manifest SHA-256 `bdc6ab6e1a56690cadf0e17be607d358775058bec737d030a064492413234dae`.
