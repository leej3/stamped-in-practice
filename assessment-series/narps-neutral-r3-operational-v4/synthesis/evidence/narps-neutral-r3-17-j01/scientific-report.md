# Independent assessment

**Verdict line:** MUST: 5 met / 1 partial / 9 unmet / 2 not-checked (17); SHOULD: 0 met / 2 partial / 2 unmet / 4 not-checked / 1 not-applicable (9); MAY: 2 met / 1 partial / 0 unmet / 0 not-checked / 2 not-applicable (5). No overall score is assigned.

## What to fix first

1. Commit the analysis script, report, notebook, figures, and result artifacts so the versioned state matches the delivered work (must/004).
2. Add a pinned environment file and concise install/use instructions, then link the environment used to the run record (must/006, 007, 010, 012–017; should/006–008).
3. Declare an authorized retrieval route covering the full workspace and verify that a researcher can retrieve it (must/016–017).

## What the project already does well

- It separates inputs, code, results, and figures into clear directories and provides a notebook starting point and a concise scientific report (`content/workspace/group_analysis.ipynb`, `content/workspace/report.md`).
- The large participant maps are tracked through annex pointers and identified with per-file checksums (`content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`).
- The analysis script uses workspace-relative paths and checks the roster, input checksums, and map geometry (`content/workspace/code/group_analysis.py`).


**Canonical capture:** SHA-256 `9caec40f60d64f664726edd255c87a99225f70fa81314a02c97ffcdea26d2fa9`  
**Captured HEAD:** `c5e927c2c46296ba59886bffc66dc165f9cf2c78`  
**Scientific adequacy: qualified.** The analysis gives a defensible, transparent test of the stated group question and supports the reported absence of corrected vmPFC evidence, subject to the stated model and coverage limitations.

**Reported hypothesis outcome:** “This analysis **does not support** the predicted positive vmPFC response to potential gain.”

## Scientific assessment

The worker analyzes all 54 supplied equal-indifference participant cope maps as one observation per participant, checks source checksums and image geometry, and uses a positive one-sample t statistic with whole-brain max-T sign-flip permutation correction. This is a scientifically defensible group analysis of the supplied fixed inputs. The task requires whole-brain correction; the code searches a 192,339 voxel mask and reports a one-sided corrected threshold, rather than relying on an uncorrected ROI result. The report and code explain that the maps are participant effect estimates in upstream model units, not currency-scaled BOLD responses, and that separate gain/loss models and missing first-level variance maps constrain interpretation. Evidence: `content/workspace/code/group_analysis.py`, `content/workspace/report.md`, `content/workspace/results/summary.json`, `content/workspace/input/upstream-methods.md`.

The reported outcome is appropriately bounded: no positive voxel survived whole-brain FWE in the AAL3 vmPFC ROI; the ROI mean is −0.00639 with 95% t interval [−0.02513, 0.01235], while the positive corrected voxels are three small posterior clusters outside that ROI. The confidence interval includes zero and modest positive values, so the result is a lack of corrected evidence, not evidence of equivalence or no neural response. The figures make that separation inspectable. The anatomical definition is reasonable but atlas dependent. The generic MNI152 mask is acknowledged as approximate to the supplied MNI152NLin2009cAsym maps. The sign-flip max-T test is defensible if participant errors are symmetric under the null; the report states this assumption. No material inference error was identified, but inference remains conditional on these supplied cope maps and one specified model. Evidence: `content/workspace/results/summary.json`, `content/workspace/figures/whole_brain_fwe_glass_brain.png`, `content/workspace/figures/vmPFC_subject_estimates.png`, `content/workspace/figures/participant_map_qc.png`.

The report states: “This analysis **does not support** the predicted positive vmPFC response to potential gain.” This is the worker's reported hypothesis outcome, distinct from this assessment's adequacy category.

## Delivery integrity and attribution

The canonical and operational manifests identify the same complete original capture and HEAD; the capture has no omissions or Git dependencies. The worker stop receipt records an exited, non-timed-out process and the same HEAD. The worker's analytical code, report, notebook, figures, and results are untracked at that stop; the commit therefore does not contain the complete delivered analysis. The frozen probe also reports a dirty tree. This weakens version tracking and prevents credit for a clean, committed research state. The 54 input map pointers are tracked through git-annex. No remotes are configured. I found no worker-declared publication or retrieval route; the coordinator's copy is not evidence of worker-side access. No access route was available to test.

A post-inspection comparison against the initial operational manifest found one byte change: `.git/annex/keysdb/db`, classified as operational metadata. This is inspection-copy metadata, not worker evidence; no logical database equivalence is claimed. No other file, link, mode, or Git metadata mismatch was found. The operational copy was used for inspection. The captured participant map symlink text points to relative paths in the workspace annex object store; the map links were not dereferenced. `judge-target.json` lists no reference limits. No original absolute/external link or external Git pointer was followed. Git configuration records an external hooks path, but no hook was run. The worker-installed `.workspace-skills/jupyter-notebook/` directory and `.entire/` session metadata indicate assistance-related material was present; these contents were not used as grading evidence, and no treatment assignment was inferred. Probe findings were limited to the tracked commit where applicable; untracked scientific files were inspected directly.

## Reproducibility measurement

The notebook documents `python code/group_analysis.py` from the workspace root. That script generates `results/group_mask.nii.gz`, `results/participant_qc.csv`, `results/max_positive_t_null_10000_seed20261016_brainmask.npy`, `results/t_statistic.nii.gz`, `results/mean_cope.nii.gz`, `results/p_fwe_positive.nii.gz`, `results/t_fwe_p05_positive.nii.gz`, `results/aal3_vmPFC_roi.nii.gz`, `results/summary.json`, and the four PNGs under `figures/`. These are the declared output candidates; supplied inputs, metadata, source code, and the notebook would be protected. The script requires NumPy, SciPy, NiBabel, pandas, Nilearn, threadpoolctl, and Matplotlib, plus Nilearn atlas/template resources. The worker supplied software version observations in `results/summary.json`, but no environment specification or installation instructions. Since the required environment cannot be reconstructed from worker-supplied declarations, replay is **not checked**; no output was deleted and no replay attempt was made. The frozen one-attempt, 7,200-second limit therefore was not consumed.

## STAMPED evidence and item decisions

The frozen probes are preserved in `probes/probes.json`. They recognize annex-backed inputs, no host-specific paths in tracked text, an incomplete module split, no committed reproducibility entry point/environment specification, and uncommitted deliverables. I also inspected the untracked script, notebook, report, figures, and result summary; absence from the commit does not erase their scientific evidence but does affect tracking. The response JSON records a verdict, reason, and capture-relative evidence for every checklist item. The checklist link and item table are in `checklist-link.txt` and `checklist-table.md`.

Automated probe limitations: these probes inspect tracked repository state and do not establish all relevant practice. In particular, the `entry-point` probe did not recognize the worker's notebook and Python script; the human review found a usable documented start command. Conversely, its annex result pertains to the tracked pointers and does not by itself establish a worker sharing route.

## Flagged items

- must/006, must/007, and must/008: the automated probes did not recognize the run record or notebook/script evidence; human review found software versions and a documented entry point, while exact environment provenance remains unmet.
- may/001: the subdataset probe was not checked, but the captured workspace contains no independently maintained submodule component; this item is not applicable.
- should/008 repeats must/014 by design.

## Not checked

- must/011: host assumptions require explicit system requirements or an execution environment description.
- must/014 and should/008: an environment specification and its update history would settle the update-process question.
- should/002: repeated testing or CI records would settle regular testing.
- should/004 and should/005: a fresh-environment execution record and disposable-environment workflow would settle these items.

## Goals and kind

The stated goal is a group-stage analysis of whether potential gain increases vmPFC response for the NARPS equal-indifference group, using the supplied participant gain-effect maps (`content/workspace/input/study-task.md`). This is a study analysis workspace; the assessment emphasizes transparent statistical inference, input provenance, reproducibility, and complete delivery tracking.

## Checklist and provenance

The checklist table is [checklist-table.md](checklist-table.md), and the generated app link is [checklist-link.txt](checklist-link.txt). The machine-readable item record is [response.json](response.json).

Produced using the frozen assessment runner identified in `assessment-version.json` (source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`), checklist 0.3.1, on the complete original capture, HEAD `c5e927c2c46296ba59886bffc66dc165f9cf2c78`, 2026-10-16, Codex/GPT-6. Probe output: [probes/probes.json](probes/probes.json).

The response helper sequence produced one retained external-runner error (`Recorded environment was changed locally` for the pinned runtime lock) while setting item answers. The failed command and output are preserved under `commands/`; the remaining answers were set using the same pinned `encode_response.py` helper, and the final frozen-runner validation passed all 31 items. This was an assessor-side transient and did not affect target files. The worker stop receipt is preserved at `evidence/worker-end-state.json` (SHA-256 `dfdb5389ccd0c8c34d7c305ea4127fb79503efb5865196be09a45012eb91c8c4`).

## Scope and evidence key

Unless otherwise noted, cited original evidence is from canonical capture SHA-256 `9caec40f60d64f664726edd255c87a99225f70fa81314a02c97ffcdea26d2fa9`, using paths relative to the capture root (`content/workspace/...`). Operational-copy observations are identified as such above; coordinator-created assessment records are not worker evidence. Full replay and access dispositions are in `replay-record.json` and `access-record.json`.
