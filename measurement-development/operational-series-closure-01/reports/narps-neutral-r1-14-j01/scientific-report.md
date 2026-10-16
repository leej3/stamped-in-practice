# Independent assessment

## Identity and integrity

Assessed the complete operational copy against canonical capture `5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153`, captured at 2026-10-16 07:07:52 UTC. The captured original HEAD is `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`. The canonical and operational manifest digests in `judge-target.json` match. The worker-stop receipt records exit code 0, a complete capture and the same HEAD. The corrected operational-tree comparison found no delivery-content changes outside the specifically exempt annex keys database metadata. During inspection, `.git/annex/keysdb/db` changed; `db-shm` and `db-wal` appeared transiently and were absent from the final comparison. These regular files are operational metadata and are not worker evidence. No claim is made about logical database equivalence. There is no identified mismatch affecting scientific conclusions.

All original evidence citations below use the canonical capture digest above and a capture-relative path. Example: `content/workspace/report.md` means the bytes in that path in the canonical capture, not an assessment copy. The assessor runner check passed before probes or response operations. The frozen probe suite was run against the operational copy. Its draft statuses were checked against untracked and ignored material and the full stopped workspace.

## STAMPED verdicts

MUST: 4 met / 1 partial / 12 unmet / 0 not-checked / 0 not-applicable (17 items). SHOULD: 1 met / 1 partial / 3 unmet / 3 not-checked / 1 not-applicable (9 items). MAY: 2 met / 1 partial / 1 unmet / 0 not-checked / 1 not-applicable (5 items). No overall score is assigned.

### Highest-leverage improvements

1. Add a tracked, installable, pinned environment specification and link each run to it. This would make the reported results reconstructible and would address MUST 006, 010, 013, 015–017.
2. Document installation and use through a portable entrypoint rather than an absolute external interpreter. This would make the group analysis actionable for another researcher and address MUST 007–009, 011–012.
3. Track the analysis code, report, figures, result tables and generated maps in the worker's versioned state. This would preserve the exact scientific product that was delivered and address MUST 004 and SHOULD 001.

### What is already working

- The analysis checks the delivered inputs and cohort, uses a common coverage mask, reports uncertainty and uses whole-brain max-statistic FWE inference; see `content/workspace/analysis/run_analysis.py` and `content/workspace/results/summary.json` in capture `5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153`.
- The 54 large input maps use tracked annex pointers and retained annex content; see `content/workspace/input/sources.json` and the canonical Git tree in the same capture.
- Inputs, analysis, results and figures are organized in separate directories, and the report points to the main script and supporting results.

### Per-item checklist

The response table below preserves each item verdict and capture-relative evidence citation.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/input/study-task.md`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/run_analysis.py` | All supplied inputs, analysis, outputs and documentation sit under one workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/data/sub-001_hypo1_cope.nii.gz` | Code reads the 54 included data/ maps relative to the workspace root. |
| must/003 | S.1 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | External Python packages are listed, but no environment, bundled software or software submodule is supplied. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/.git/index` | At worker stop, the main code, report, figures, results and analysis data were untracked in Git. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/.git/annex/objects/fW/JZ/MD5E-s1794522--2a6f64556ba73c42049c33979409bb66.nii.gz/MD5E-s1794522--2a6f64556ba73c42049c33979409bb66.nii.gz` | The captured Git tree tracks 54 annex pointers and retains the corresponding annex objects. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | Outputs are present, but no exact environment specification is linked to their run. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | report.md gives usage instructions, but no installation instructions or complete environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/run_analysis.py`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | analysis/run_analysis.py is the documented starting script for reproducing the group analysis. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | The documented reproduction command uses an absolute external interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | analysis/software.txt lists versions but does not specify an installable set of dependencies. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | The documented route assumes a prepared external Python environment without documenting host requirements. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No README or environment specification provides complete system and dependency requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No environment specification is present in the stopped object. |
| must/014 | P.3 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No process for updating and tracking environment specifications is documented. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No lockfile, environment capture or container digest supports exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | The worker supplied no environment specification to share. |
| must/017 | D.1 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | The report does not explain how to obtain or reconstruct the prepared external environment. |
| should/001 | T.2 | partial | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/.git/index` | Git/annex tracks inputs, while the analysis, report and results were untracked at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/run_analysis.py`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | No repeated workflow-testing record is present; test history would settle regularity. |
| should/003 | M.1 | met | probe:modules-separated+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/run_analysis.py`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/input/sources.json`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/results/summary.json` | Inputs, code, data, results and figures occupy distinct folders. |
| should/004 | E.1 | not-checked | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No fresh-container, clean-VM or comparable execution record is supplied; such a record would settle this. |
| should/005 | E.1 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No mechanism creates a disposable environment for each execution. |
| should/006 | D.2 | not-checked | probe:ci-present | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No exact environment specification exists to assess for repeated reconstitution testing. |
| should/007 | D.2 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No environment image, binaries or other environment artifact is archived in the project. |
| should/008 | D.2 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/software.txt` | No process for updating and tracking environment specifications is documented. |
| should/009 | M.4 | not-applicable | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/input/sources.json` | N/A: all delivered data and software components are public; no restricted subject is present. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/input/sources.json` | The external map source is identified in sources.json, bundled as an input, and its public retrieval route is reachable. |
| may/002 | M.2 | partial | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | Folders are separated, but the report does not fully document module interfaces or recombination. |
| may/003 | M.2 | unmet | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/analysis/run_analysis.py`, `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | The object does not define independently updateable module boundaries. |
| may/004 | M.2 | not-applicable | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | N/A: no independent project modules need to be composed. |
| may/005 | M.2 | met | judgement | `capture:5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153#content/workspace/report.md` | The report directs readers to the analysis script, inputs, result files and figures. |

### Flagged items

- MUST 002, 006–009 and 015: probe results were corrected after full stopped-workspace review found bundled maps, an executable script/report entrypoint, a documented absolute interpreter path, or supplied result artifacts without an environment-linked run record.
- SHOULD 003: the probe counted only Git-tracked modules; the full stopped delivery separates inputs, code, data, results and figures.
- MAY 001: the probe did not recognize the independently identified, retrievable external map source bundled as an input.
- MUST 014 and SHOULD 008 carry `upstream-duplicate`; the checklist repeats the same environment-update-process question.

### Not checked

- SHOULD 002: regular workflow testing is not established; repeated test records would settle it.
- SHOULD 004: a fresh container/VM/cloud execution is not established; a corresponding completed-run record would settle it. The assessment replay was not checked for the separate reason below.
- SHOULD 006: repeated environment reconstitution is not established; an exact environment specification and reconstitution records would settle it.

### Goals and kind

Assumption, not confirmed by human guidance: this is a **study** whose goal is to answer the supplied NARPS equal-indifference group-analysis question using the fixed participant maps. The goal comes from `content/workspace/input/study-task.md` and the reported analysis in `content/workspace/report.md`. All seven STAMPED principles apply, with traceability of the study outputs and retrievability of its inputs especially relevant.

Checklist URL: [2026-10-16-url.txt](2026-10-16-url.txt). Machine-readable verdicts: [response.json](response.json); frozen probe output: [probes.json](probes.json).

Stamp: assess-alignment-with-stamped-principles 0.1.0 and stamped-conventions 0.1.0; checklist 0.3.1; Codex independent assessor / GPT-6; 2026-10-16. Canonical capture manifest SHA-256 `5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153`; original captured HEAD `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`. Probe output: `probes.json`.

## Scientific adequacy

**Scientific adequacy: supported.** This category evaluates the report's stated absence of support for a positive vmPFC gain effect; it does not imply proof of a zero effect.

The report states: “This group analysis does not support a greater vmPFC response with increasing potential gain.” (worker report, `content/workspace/report.md`). The analysis uses all 54 supplied equal-indifference participant maps, treats each participant as one independent observation, and tests the positive group mean with a one-sample *t* statistic. A participant-level sign-flip maximum-positive-*t* procedure controls whole-brain FWE over 198,029 voxels (9,999 flips, α=.05). The report and code make the null symmetry assumption explicit. The coordinate-defined 10-mm sphere at MNI (0, 40, −10) is a reproducible vmPFC operationalization; it is used to localize the hypothesis, while corrected whole-brain inference remains primary. No corrected positive voxel overlaps the 428-voxel sphere. The descriptive ROI mean is −0.0061 with a 95% CI of [−0.0342, 0.0221], which spans zero and both signs. These results support “not established” and do not establish absence of an effect.

Input checks are appropriate for this fixed group-stage task: the 54 map files under `data/` all match their recorded SHA-256 and byte counts in `input/sources.json`; the worker reports matching dimensions and affines, finite values, unique cohort IDs, and complete map coverage in the strict common nonzero mask. No participants were excluded. The analysis does not mistake contrast estimates for *t*/*z* statistics or currency-unit slopes. It explains that the upstream gain modulator was normalized, variance maps are unavailable, and participant-level estimates are conditional on the fixed upstream model. The one-sample equal-weight group model and stated symmetry assumption are defensible with these inputs.

The supplied results in `results/summary.json`, `results/fwe_clusters.csv`, `results/map_qc.csv`, `results/permutation_max_t.csv`, `results/vmPFC_participant_values.csv`, NIfTI maps and four figures make the key results inspectable. Visual review found the participant ROI and coverage/null figures legible. The corrected-result figure is difficult to inspect at the very posterior boundary and does not clearly show the small clusters; the cluster table and peak coordinates provide the needed numerical evidence. The ROI estimate and interval are explicitly descriptive, avoiding a second uncorrected positive claim. The corrected posterior clusters are not relabeled as vmPFC.

The worker reports 24 corrected positive voxels in three small posterior clusters, maximum *t*(53)=6.62 at (−26, −102, −3.6), max-statistic FWE *p*=.0006. These are anatomically remote from the stated target. The reported outcome is therefore a defensible absence of positive support for the hypothesis, not confirmation of a positive effect and not evidence that the vmPFC effect equals zero. Alternative vmPFC boundaries and the modest sample size limit localization and precision. No exact atlas, package or numerical replication was required.

**Hypothesis outcome, verbatim:** “This group analysis does not support a greater vmPFC response with increasing potential gain.” This is the reported hypothesis outcome and is retained separately from the adequacy category above.

Scientific evidence cited: `content/workspace/report.md`; `content/workspace/analysis/run_analysis.py`; `content/workspace/input/upstream-methods.md`; `content/workspace/input/sources.json`; `content/workspace/input/participants.tsv`; `content/workspace/results/summary.json`; `content/workspace/results/fwe_clusters.csv`; `content/workspace/results/map_qc.csv`; `content/workspace/results/permutation_max_t.csv`; `content/workspace/results/vmPFC_participant_values.csv`; `content/workspace/figures/whole_brain_fwe.png`; `content/workspace/figures/vmPFC_unthresholded.png`; `content/workspace/figures/vmPFC_participant_values.png`; `content/workspace/figures/quality_and_null.png`.

## Replay and measurement availability

Replay status: **not checked**; no scientific replay was attempted. The exact documented command is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py`, run from the workspace root. The report's interpreter points outside the captured object, and the worker supplied no environment lock/specification or retained dependency mapping for it. The only dependency record is `analysis/software.txt`, which lists versions without an installable specification. Following or reconstructing the external interpreter would exceed the supplied scope; substituting the assessor environment or an inferred Python command would not be a replay of the documented entrypoint.

Had the declared prerequisite been available, the script identifies these generated outputs: `results/group_mean_cope.nii.gz`, `results/group_t_positive.nii.gz`, `results/group_p_fwe_positive.nii.gz`, `results/group_sig_fwe_p05.nii.gz`, `results/fwe_clusters.csv`, `results/map_qc.csv`, `results/vmPFC_participant_values.csv`, `results/permutation_max_t.csv`, `results/summary.json`, and the four PNGs under `figures/`. The declared comparison rule would use relative tolerance 1e-6 for scientifically relevant numeric map, table and summary quantities, while separating timestamp/log/prose/format differences; fixed-seed permutation outputs would be compared numerically. No outputs were removed and no replay copy was created. Shipped results are worker-delivery evidence only, not replay evidence. The frozen runner passed its check and response validation; no frozen-assessor malfunction was observed. Assessment-side diagnostic errors and their corrections are recorded in `commands/assessor-diagnostics.md`.

## STAMPED evidence and item attainment

The response JSON contains the individual checklist verdicts and evidence paths. Attainment is assessed at the worker stop state, not by coordinator preservation. The captured HEAD includes annex pointers for 54 input maps and the annex objects are retained, so large-data annex use is credited. The main analysis script, report, software list, figures, result tables and top-level analysis data are present in the stopped delivery but untracked in Git. Thus Git did not track the complete scientific product at stop; the coordinator's later capture/retention does not remedy this. The project is organized into input, analysis, data, results and figures folders, but the environment is absent. The report gives a starting script but no README/Makefile install instructions; its reproduce command names an absolute external interpreter.

The worker-declared retrieval routes in `input/sources.json` cover all 54 maps on NeuroVault, the pinned participant table on raw GitHub, and the NeuroVault collection metadata API. A researcher using those public routes is the intended recipient; anonymous access is not a requirement. HEAD checks returned HTTP 200 for the collection page, a representative map, the pinned participant table and the metadata API. The test therefore covers the declared hosts and representative routes, not a byte-for-byte retrieval of all 54 files during this assessment. The worker reports those 54 files were retrieved and checksum-verified before analysis, and the delivered top-level map set independently matches all 54 recorded sizes and SHA-256 values. The worker's report/source index is not itself a public project publication route; coordinator delivery to the assessor is not credited as worker publication. No worker-hosted route for the complete report/code/results bundle was evidenced, so access to that bundle through a worker-declared route is not established.

Worker-stop attribution: `worker-end-state.json` says the worker exited normally and identifies the captured stopped state. The presence of `.codex/` skills and `.entire/` session-trace metadata indicates AI-assistance material was retained in the delivery; this exposure is recorded without using it as grading evidence. No treatment assignment is inferred or reported. Coordinator-side commits, annex conversion, uploads or preservation are not used to award worker-practice credit.

## Evidence and records

Canonical capture SHA-256: `5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153`. Original captured HEAD: `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`.

See `response.json` for item-level attainment, `probes.json` for frozen probe outputs, `access.json` for route coverage and host test outcomes, and `replay.json` for replay declaration and the reason it was not checked. The scientific record is `scientific-judgment.json`. No overall score is assigned.
