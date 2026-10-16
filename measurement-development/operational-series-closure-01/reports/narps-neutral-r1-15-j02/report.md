# Independent assessment — NARPS gain effect

## Verdicts

MUST: 5 met / 2 partial / 10 unmet / 0 not-checked / 0 N/A (17 items). SHOULD: 1 met / 1 partial / 3 unmet / 3 not-checked / 1 N/A (9 items). MAY: 0 met / 2 partial / 1 unmet / 1 not-checked / 1 N/A (5 items). No overall score is assigned.

## Scientific judgment

**Scientific adequacy: supported.** The reported conclusion that this analysis did not find corrected positive vmPFC evidence is supported by the documented group inference and supplied outputs. It is a statement about lack of evidence in these data and this operational ROI, not proof of a zero effect.

**Hypothesis outcome (verbatim):** “This group analysis did not support the predicted positive gain effect in vmPFC.”

The analysis uses 54 participant-level gain-effect maps as independent units; checks their byte hashes, finite values, dimensions and affine consistency; defines common nonzero coverage; and applies a positive one-sided voxelwise one-sample t analysis with participant-level whole-map sign flips and max-T whole-brain correction. The saved summary reports zero FWE-significant vmPFC voxels, 24 corrected voxels in posterior occipital clusters, and a vmPFC participant-average effect near zero with an interval spanning positive and negative values. The report correctly distinguishes the null corrected result from evidence of absence.

The anatomical localization is explicit and inspectable: Harvard–Oxford medial frontal, subcallosal and medial orbital labels, resampled to the participant grid and intersected with coverage. The report acknowledges template and boundary uncertainty. The supplied methods describe maps as mean-centered, variance-normalized gain coefficients, not effects per currency unit; participant variance maps and the upstream individual-level pipeline are unavailable. Sign-flip inference assumes independent participants and symmetric effects under the null. These limits qualify scope, but I found no material inference error in the reported conclusion. [Capture f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9: `content/workspace/report.md`, `analysis/group_analysis.py`, `results/summary.json`, `results/fwe_clusters.csv`, `input/upstream-methods.md`]

**Scientific adequacy: supported — the absence of corrected positive vmPFC evidence is supported for this analysis, while the report appropriately avoids claiming that the true effect is zero.**

## Capture, attribution and scope

The canonical capture SHA-256 is `f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9`; the delivery and operational manifests have this same digest. The complete capture reports no omissions or errors. Its original HEAD is `d857ab1302d13cb660a7a044af07141f44bfa9ba`. Evidence citations below use this canonical digest and capture-relative paths. The worker stop receipt records a normal exit (return code 0); the stopped workspace contains `analysis/group_analysis.py`, `report.md`, two figures and eleven result artifacts. At worker stop these project outputs were untracked, so the HEAD alone does not contain the complete scientific delivery. The capture retains annex contents for the 54 relative data links. A valid post-inspection byte comparison matched all 1,143 captured entries except the regular file `.git/annex/keysdb/db`, which is permitted operational metadata. No logical database equivalence is established; the comparison found no other mismatch. Two earlier attempts of my supplemental checker failed due to a path-calculation/quoting error; those invalid outputs are retained and recorded separately in `assessor-malfunction.json`. The frozen runner did not malfunction.

The target contains `.codex` and `.entire` session-support directories, which identify AI-assisted tooling. I did not use their session content as grading evidence. Later coordinator preservation is not attributed to the worker. The worker-stop receipt and captured target were used to assess worker state.

## Replay and access

Replay was **not checked**. The candidate command is `python analysis/group_analysis.py`; the script explicitly selects its generated CSV, NIfTI, JSON, text and figure outputs. However, it imports packages for which the delivery has no environment declaration, and calls Nilearn’s Harvard–Oxford atlas fetch. That scientific prerequisite is not supplied or pinned in the delivery. No replay copy was executed or modified, and no atlas or other scientific input was retrieved. `replay.json` records the command, output selection, comparison rule and reason.

Intended recipient: a researcher using a worker-declared authorized route. No project retrieval route is declared in the captured report or Git configuration; no worker remote or publication route was available to test. `input/sources.json` identifies upstream source-data URLs, not a retrieval route for this complete project. Artifact coverage and host scope for worker access are therefore unavailable / not tested. The coordinator’s delivery of this capture is not evidence of worker access. See `access.json`.

## What to improve first

- Commit the analysis, report, figures and results at worker stop; they are currently outside the captured HEAD (must/004).
- Add a dependency lock and record the exact environment for this run, including how the atlas resource is obtained (must/006, 010, 013, 015).
- Add concise installation and execution instructions, with host requirements and an explicit atlas retrieval/cache route (must/007, 011, 012, 017).
- Publish a stable authorized route covering code, data, environment and results, then test it from the intended recipient’s host scope (must/016).

## What is already done well

- The 54 participant maps are carried in annex and checked against source checksums; quality results retain one row per participant (`input/sources.json`, `results/input_qc.csv`).
- The report, analysis code, figures, and derived outputs are separated into recognizable directories. The report documents the operational vmPFC mask and uncertainty (`report.md`, `results/vmPFC_mask_definition.txt`).
- The analysis applies whole-brain max-T correction to participant-level maps and reports the corrected discoveries separately from the vmPFC estimate (`analysis/group_analysis.py`, `results/summary.json`, `results/fwe_clusters.csv`).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | Required code, inputs, figures and results are inside the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/input/data/` | All 54 maps are reachable through relative annex links inside the root. |
| must/003 | S.1 | unmet | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | Python packages and the atlas dependency are not supplied as an installable environment or linked module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md`, `probes.json#tree-clean` | Git tracks starter inputs, but the analysis, report, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/input/data/` | The 54 large participant maps are stored in git-annex. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/results/summary.json` | No run record links these shipped results to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | No install and usage instructions give a reader a supported setup route. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py` | The report identifies the executable analysis script, whose main block runs the group workflow. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py` | The analysis derives paths from its own file location and uses relative project paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py` | Reported package versions are not an environment specification; no dependency file captures them. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py` | The documented materials omit host, system-library, cache and atlas-retrieval requirements. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | The report names Python and package versions, but gives no system requirements or installation route. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No environment specification is present in the captured repository. |
| must/014 | P.3 | unmet | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No environment specification or reproducible update process is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | No immutable environment specification is supplied for reproducing the reported run. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No environment artifact or specification is available to share. |
| must/017 | D.1 | unmet | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | The report does not explain how to obtain and use a reproducible environment. |
| should/001 | T.2 | met | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/input/data/`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py` | Git versions the project materials and git-annex carries the large maps within the same repository. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No repeated testing history or schedule is present; a retained run series would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/input/`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/results/`, `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/figures/` | Inputs, code, results and figures are separated, but environment files are absent. |
| should/004 | E.1 | not-checked | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | No fresh-environment run record exists; a retained clean-environment execution would settle it. |
| should/005 | E.1 | not-checked | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/analysis/group_analysis.py` | No execution wrapper documents environment lifetime; its run configuration would settle this. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | There is no environment specification to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No environment artifacts or binaries are archived with the delivery. |
| should/008 | D.2 | unmet | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No environment specification or tracked update process exists. |
| should/009 | M.4 | not-applicable | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/input/sources.json` | N/A: no restricted data or software is identified; the inputs are public-source maps. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | N/A: no independently maintained project components; annex data and Python packages are not components. |
| may/002 | M.2 | partial | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | The report links the code, inputs and outputs, but does not explain how the modules relate. |
| may/003 | M.2 | not-checked | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | Independent module update boundaries are not described; module history would settle this. |
| may/004 | M.2 | unmet | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/` | No composition mechanism is supplied for independently managed modules. |
| may/005 | M.2 | partial | judgement | `capture://f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9/content/workspace/report.md` | The report links key artifacts, but gives no overall navigation or module guide. |

## Probe overrides and limitations

- **must/002:** the probe could not infer data links from submodule structure. Manual inspection of all 54 relative annex links and retained annex objects establishes the dataset is inside the common root; this is an override.
- **must/008:** the entry-point probe did not recognize the untracked script in the complete stopped workspace. The report identifies it and its `__main__` block invokes the workflow; this is an override.
- **must/009:** the probe scanned tracked paths only; the untracked analysis script was separately inspected and uses paths rooted at its own location. This answers the property for the complete delivery.
- **must/004:** the probe’s unmet tracking result is retained as partial because Git tracks starter inputs while the main work products were untracked.

## Not checked

- **should/002:** no repeated testing schedule or run series is captured; a retained series would settle it.
- **should/004:** no worker fresh-environment execution is recorded; a worker run record would settle it.
- **should/005:** no environment lifecycle wrapper is documented; an execution configuration would settle it.
- **may/003:** module update independence is not documented; a module boundary/history record would settle it.
- **Replay:** the supplied code requires an atlas retrieval and an undeclared package environment. A worker-supplied atlas resource and reproducible environment specification would permit the one scoped replay.

## Goals, kind and emphasis

Assumption (no human guidance was attached): the object is a **study** whose product is a group-level NARPS Hypothesis 1 assessment from fixed participant maps. This follows `input/study-task.md` and the supplied scientific brief. The STAMPED review emphasizes tracked complete delivery, actionable reproduction, environment portability, and distributable access.

Flagged verdicts are listed above. Checklist URL: [`checklist-url.txt`](checklist-url.txt). Machine-readable answers: [`response.json`](response.json). Probe details: [`probes.json`](probes.json). Target integrity: [`target-integrity.json`](target-integrity.json). Scientific record: [`scientific-judgment.json`](scientific-judgment.json).

Assessment stamp: `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), 2026-10-16, frozen external assessment runner; model identity not exposed by runtime. Original captured HEAD `d857ab1302d13cb660a7a044af07141f44bfa9ba`; canonical capture `f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9`. Probe output: `probes.json`.
