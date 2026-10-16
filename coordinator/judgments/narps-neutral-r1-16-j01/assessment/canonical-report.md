# Independent assessment — NARPS potential gains and vmPFC

**STAMPED verdict:** MUST: 4 met / 3 partial / 10 unmet / 0 not-checked (17 total). SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total). MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable (5 total). Partial MUST items do not satisfy the MUST requirement. No overall score is assigned.

**Scientific adequacy:** **Qualified.** The supplied analysis supports the reported conclusion that there is no whole-brain-corrected positive vmPFC evidence in this group: nine positive voxels survived correction elsewhere (peak t(53)=6.62 at MNI [-26, -102, -3.6] mm), none in the proxy; its 2,415-voxel mean was 0.0002 COPE (95% CI [-0.0221, 0.0225]). It does not establish a zero effect. The correction, data checks and uncertainty summary are defensible; the main qualification is that voxels present in at least 90% of maps are analyzed at N=54, so zero-valued out-of-coverage observations in the remaining maps are treated as estimates. This is most relevant near coverage boundaries; the anatomical vmPFC summary is far from the image edge. The absence of participant variance maps also limits group inference to unweighted COPE estimates.

**Reported hypothesis outcome:** No positive vmPFC effect survived whole-brain correction; the atlas-proxy mean is near zero and its 95% interval spans zero. Interpret this as failure to find corrected support for the prediction, not evidence that the true response is exactly zero.

## What to improve first

1. Add a pinned environment and atlas version, document the network requirement, and record the environment used for each result. This makes the analysis installable and links results to actions (`must/003`, `must/006`, `must/010`–`must/017`, `should/006`–`should/008`).
2. Track the worker-created analysis code, report, figures and results in version control, and end with a clean, documented stop state (`must/004`, `should/001`).
3. Add installation instructions and a researcher-facing route to the complete object. The report already supplies the two script commands (`must/007`, `must/016`, `must/017`).
4. Make spatial coverage explicit in the group calculation: exclude missing observations voxelwise or use a justified complete-coverage mask, and report voxelwise sample sizes (`must/006` scientific provenance; scientific adequacy).
5. State reuse terms for maps, code and derived outputs; no license or reuse terms were found (extra finding, outside the checklist).

## What is already strong

- The complete stopped delivery contains 54 maps; per-map hashes, finite values, common image shape and affine are checked in the code and QC table. Git-annex is used for the large map payloads (`analysis/group_analysis.py`, `results/map_qc.csv`, `probe:large-in-annex`).
- The group test uses unthresholded participant COPEs and a positive one-sample t test, controls whole-brain FWE with Bonferroni across 210,968 voxels, and reports df, interval and corrected voxel results (`analysis/group_analysis.py`, `results/summary.json`, `results/fwe_positive_voxels.csv`).
- The report correctly explains that the gain COPE is not a currency-unit slope, describes the atlas proxy and unavailable first-level variance maps, and distinguishes no corrected support from a true null (`report.md`).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `report.md`, `input/sources.json` | The captured delivery places supplied maps, analysis, outputs and report under one workspace root. |
| must/002 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `input/data`, `input/sources.json`, `analysis/group_analysis.py` | The 54 maps are included and checksummed; the required Harvard–Oxford atlas is fetched at runtime and not pinned in the delivery. |
| must/003 | S.1 | unmet | judgement | `analysis/group_analysis.py`, `analysis/restore_maps.py` | Analysis imports NumPy, pandas, nibabel, SciPy, Nilearn, Matplotlib and Pillow, but no environment specification declares them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probe:tree-clean`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-16/judgments/narps-neutral-r1-16-j01/attempt-01/worker-end-state.json` | Git tracks supplied materials, but worker analysis, report, figures and results are untracked; 54 annex paths are type-changed at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `input/data`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-16/judgments/narps-neutral-r1-16-j01/attempt-01/worker-end-state.json` | Git-annex stores the 54 binary map payloads; the stop receipt and capture retain matching bytes and annex identities. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `report.md`, `analysis/group_analysis.py`, `results/summary.json` | Shipped results have a documented command but no run record linking them to an exact environment; no environment specification is supplied. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md`, `analysis/group_analysis.py` | report.md gives usage commands and links code, but does not explain how to obtain or install the claimed Python 3.13 environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analysis/restore_maps.py`, `analysis/group_analysis.py` | The report names the two-step entrypoint: restore_maps.py followed by group_analysis.py. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths`, `analysis/group_analysis.py` | Scripts resolve workspace paths relative to their own location; the tracked-text scan found no host-specific absolute paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked`, `analysis/group_analysis.py` | No environment specification declares the scientific Python packages imported by the analysis. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `analysis/group_analysis.py`, `report.md`, `.git/config` | The atlas fetch requires network access, and captured Git config names an undocumented host-specific hooks path; worker attribution for that config is unclear. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md`, `analysis/group_analysis.py` | No system requirements or complete software dependency list is documented; report.md only mentions a Python 3.13 environment. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | No environment specification is present in the captured workspace or worker stop inventory. |
| must/014 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-16/judgments/narps-neutral-r1-16-j01/attempt-01/worker-end-state.json` | No environment specification or dependency-update process is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | No frozen package manifest, container digest or other exact environment pin is supplied. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-16/judgments/narps-neutral-r1-16-j01/attempt-01/judgment/2026-10-16-access-record.json` | No environment specification is supplied or shared through a worker-declared route. |
| must/017 | D.1 | unmet | probe:entry-point+judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | The report says a Python 3.13 environment was provided but gives no route to obtain or install it. |
| should/001 | T.2 | partial | judgement | `probe:large-in-annex`, `probe:tree-clean`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-16/judgments/narps-neutral-r1-16-j01/attempt-01/worker-end-state.json` | Git and git-annex are present, but the worker analysis, report and generated outputs are untracked at stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `probe:ci-present`, `report.md` | No repeated testing record or CI is supplied; inspect worker test history to establish whether the workflow is checked regularly. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `probe:modules-separated`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | Input, analysis, results and figures occupy separate directories, but no environment module or documented independent module boundaries exist. |
| should/004 | E.1 | not-checked | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-16/judgments/narps-neutral-r1-16-j01/attempt-01/judgment/2026-10-16-replay-record.json` | No fresh-environment execution is recorded; a declared dependency environment and one bounded replay would settle this. |
| should/005 | E.1 | unmet | judgement | `report.md`, `analysis/group_analysis.py` | The documented scripts run in the caller’s existing Python environment; no disposable-environment workflow is defined. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | No exact environment specification exists to test for reconstitution. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json`, `report.md` | No environment artifacts or executable runtime are archived with the delivery. |
| should/008 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | No dependency-update process exists; this repeats the answer to must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/study-task.md`, `input/sources.json` | N/A: the supplied task and source metadata identify no restricted data or software component. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `probe:subdatasets-resolvable`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | N/A: there are no independently maintained project modules; package dependencies are runtime software, not project modules. |
| may/002 | M.2 | partial | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | The report links inputs, scripts and outputs, but does not explain modular boundaries or how components relate. |
| may/003 | M.2 | partial | judgement | `analysis/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/manifest.json` | Input and output directories are separated, but analysis code relies on a single workspace root and has no independent module interface. |
| may/004 | M.2 | met | judgement | `report.md` | The report provides an explicit composition sequence: restore maps, then run group analysis. |
| may/005 | M.2 | met | judgement | `report.md` | report.md links the analysis scripts, key result summary, tables and figures for navigation. |
## Flagged items

- `must/004`: the tree-clean probe measures committed-state cleanliness. The full worker-stop state includes untracked analysis/report/results and 54 type-changed annex paths, so Git is used but does not track the complete worker product (`probe-overridden`).
- `must/006`: the run-env probe could not identify a provenance record; direct review found no environment declaration in the complete delivery, so the exact result environment is absent (`probe-overridden`).
- `must/007`: the filename probe missed the delivered `report.md`; it gives usage commands but not environment installation steps, so the answer is partial (`probe-overridden`).
- `must/008`: the filename probe missed the report's documented script sequence, which is a clear start point (`probe-overridden`).
- `must/011`, `must/012`: direct review found undocumented network access for atlas retrieval and no system/dependency list; captured `.git/config` also names an external absolute hooks path. Attribution for that Git config cannot be established (`probe-overridden`).
- `must/014` and `should/008`: the checklist repeats the environment-update question; both answers repeat by design (`upstream-duplicate`).

The frozen probe's `derived-have-records` result was not applicable because it examines tracked products only. The complete delivery contains untracked result files, so it does not establish absence of derived outputs or provenance.

## Extra finding

The frozen license probe found no license or reuse terms. This is recorded as `license-declared: unmet` in the response JSON; it is not a checklist item.

## Not checked

- `should/002`: no repeated test history was used to establish regular workflow testing; worker test history or a recurring CI record would settle it.
- `should/004`: no fresh-environment run is recorded. A replay after a worker-supplied environment declaration would settle it.
- Scientific replay: not checked because the worker mentions a Python 3.13 environment but supplies no dependency declaration or installation route. The assessor environment was not substituted. The exact proposed command, prerequisites, output selection, comparison rule and reason are in [the replay record](2026-10-16-replay-record.json); no replay process or target code was launched.

## Goals, kind and scope

**Assumption (not confirmed with a human):** this is a **study** whose product is a group-level answer about gain-related vmPFC activity. The goal comes from `input/study-task.md`; no human guidance was attached.

I inspected the complete target at `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-16-j01/content/workspace`, verified it against the capture manifest, read the stop receipt, inspected report/code/results/figures and ran the frozen probes. The initial manifest comparison matched all 1,141 entries. A subsequent Git-based assessment inspection coincided with one mismatch in `.git/annex/keysdb/db`; I preserved it and bounded conclusions to the original manifest and stop receipt for worker-state claims. See [the delivery verification note](2026-10-16-delivery-mismatch.md) and [verification output](2026-10-16-delivery-verification.stdout). No original external pointer was followed, and reference limits were empty. `.entire` session-log and prompt paths were present in the inventory; I did not open or use them as grading evidence.

The worker stop receipt records a normal exit and a complete capture. At stop, Git-annex input payloads were present, but analysis scripts, report, figures and results were untracked; later coordinator capture or delivery does not change that attribution. The captured `.git/config` has an absolute `core.hooksPath` outside the workspace; who supplied or set that value is unclear. Replay hooks were not run.

**Access.** The intended recipient is a researcher using the declared authorized route. The only worker-declared route is the NeuroVault input URLs in `input/sources.json`; HEAD checks for all 54 map URLs returned 200 with expected content lengths. That route covers inputs only. No worker-declared route for code, report, outputs or environment was found; the coordinator-provided target path is not evidence of worker publication. The tested host scope and limitations are in [the access record](2026-10-16-access-record.json) and [check output](2026-10-16-access-check.stdout).

## Checklist link and provenance

Checklist: [open the STAMPED checklist app](2026-10-16-url.txt). The validated per-item record is [2026-10-16-response.json](2026-10-16-response.json); unedited frozen probe output is [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on target commit `675620fed8a134102b1b07226fe39d67630ee6f7`, assessment date 2026-10-16, Codex API / GPT-6 (exact build and model ID unavailable). Capture SHA-256: `1bc0f46ef4ad58e9f70bb654d761eb330f15d1c87929ad165d414907dd7d0f68`; worker stop receipt SHA-256: `17bbce762c9dc4b3e7c27f16479e30072174e2fd5dac626ab71bf147ee863588`. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). The capture and stop receipt are coordinator-retained records and do not earn worker-practice credit.
