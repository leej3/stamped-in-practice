# Independent assessment: NARPS potential gains and vmPFC

**Assessment boundary.** The original complete stopped workspace was checked against the delivery manifest and worker-stop receipt. The frozen delivery capture validates as complete, with no listed omissions or errors. The task file hash matches the coordinator brief (`e92bf2e0…10cc8`), and the stop receipt hash matches the supplied hash (`48129fa8…541fa`). The Git HEAD at stop is `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`; the manifest also retains the worker's untracked and ignored workspace state. The report, analysis, figures and results were untracked at stop. No discrepancy between the manifest and stop inventory was found. No Git command was run against an external pointer and no external absolute target was followed. The capture contains an absolute `core.hooksPath`; its target was not followed. Later coordinator capture/preservation is not worker publication or worker version-control credit.

The visible `.task-skills/jupyter-notebook/` directory and `.entire/` session metadata were treated as workspace context only, not as evidence for scientific grading. No other worker outputs, prior judgments or assignment records were consulted, and no treatment assignment was inferred.

## Scientific assessment

**Adequacy: qualified. Hypothesis outcome: no whole-brain-corrected vmPFC support in the supplied maps.** The delivered conclusion is appropriately bounded: it does not claim equivalence or that the true response is zero.

The script and report support the conclusion with all 54 equal-indifference participant COPE maps, matched metadata, a geometry check, finite-value check, and a participant-support mask requiring nonzero coverage in at least 90% of participants. The group test is a one-sample positive sign-flip max-T test over the analysis mask, with 4,999 sign assignments and whole-brain voxelwise FWE correction. The report identifies vmPFC with Harvard–Oxford medial frontal/subcallosal labels restricted to an anterior ventral midline; the ROI is used for localization, not as a substitute for the required whole-brain correction. Reported output has zero corrected vmPFC voxels, a near-zero descriptive vmPFC mean (0.006; 95% t interval −0.066 to 0.078), and 24 corrected voxels in posterior clusters outside the hypothesis region. Those posterior clusters do not support the vmPFC hypothesis. See [REPORT.md](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/REPORT.md), [group_analysis.py](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/analysis/group_analysis.py), [analysis_summary.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/results/analysis_summary.json), and [quality_checks.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/results/quality_checks.json).

The analysis is conditional on upstream AO86 gain COPEs, which reflect a mean-centered, variance-normalized gain modulator and separate gain/loss models; they are not currency-unit slopes. Equal participant weighting is defensible because participant variance maps are unavailable. The sign-flip correction depends on exchangeability and approximate symmetry under the null. Coverage is inferred from nonzero map support, and the report notes but does not sensitivity-test the flagged extreme values. These limit the strength and scope of the conclusion but do not invalidate the reported absence of corrected vmPFC evidence. The result does not rule out smaller or more variable effects and cannot establish a zero effect.
A structured summary of adequacy, outcome and qualifications is in [scientific-assessment.json](2026-10-16-scientific-assessment.json).

The images and result tables are scientific deliverables, not replay evidence. No replay was run: the worker supplied no complete environment declaration or setup instructions, and the script also fetches atlas/template assets without documenting the needed setup. The recorded [replay assessment](2026-10-16-replay.json) explains the not-checked result.

## STAMPED findings

### Verdict counts

- **MUST:** 4 met / 4 partial / 9 unmet / 0 not-checked (17 total; a partial MUST is not satisfied).
- **SHOULD:** 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total).
- **MAY:** 1 met / 2 partial / 1 unmet / 0 not-checked / 1 not-applicable (5 total).

### What to fix first

1. Add a complete, retrievable environment specification and setup instructions, including every imported package and atlas/template retrieval requirements → makes the analysis actionable and portable → must/003, must/010–017, should/006–008.
2. Track the delivered script, report, figures and results at worker stop → makes the delivered scientific product part of the versioned record → must/004, should/001.
3. Add a run record linking the exact inputs, command, full environment and outputs → ties the reported results to their production conditions → must/006.
4. Declare and test a researcher-accessible route covering the code, inputs and scientific outputs → enables independent retrieval → must/016.

### What is already good

- The report distinguishes participant effect estimates from test statistics and money-unit slopes, and explains the missing variance maps and upstream limits ([REPORT.md](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/REPORT.md>)).
- Group inference uses a positive whole-brain max-T FWE procedure and separates the anatomical vmPFC interpretation from whole-brain inference ([group_analysis.py](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/analysis/group_analysis.py>)).
- The delivery includes code, a notebook, machine-readable results, a cluster table and three informative figures ([analysis](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/analysis/group_analysis.py>), [results](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/results/analysis_summary.json>), [figures](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-10-j01/content/workspace/figures/whole_brain_fwe.png>)).

### Per-item results

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md` | Code, inputs, results and figures sit under the workspace root. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz` | All 54 maps resolve to retained annex payloads inside the common root. |
| must/003 | S.1 | unmet | judgement | `REPORT.md` | Python packages are named in the report but no dependency environment or linked software module is supplied. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probe:tree-clean` | Git holds supplied inputs, but worker code, report and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+judgement | `probe:large-in-annex`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-10/judgments/narps-neutral-r1-10-j01/attempt-01/worker-end-state.json` | Annex stores the coordinator-supplied maps; stop HEAD equals seed HEAD, and worker-produced image outputs were untracked. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+probe:run-env-linked+judgement | `results/analysis_summary.json` | Results are present, but no execution record links them to a complete exact environment specification. |
| must/007 | A.1 | unmet | judgement | `REPORT.md` | REPORT.md explains methods and lists files, but gives no installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/group_analysis.py` | The executable group-analysis script is a clear starting point for reproducing results. |
| must/009 | P.1 | met | judgement | `analysis/group_analysis.py` | The analysis script builds input and output paths relative to its own project root. |
| must/010 | P.1 | unmet | judgement | `analysis/group_analysis.py` | The delivery has no complete dependency specification; the report's version list omits imported packages. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `analysis/group_analysis.py` | Python is named, but host assumptions and runtime needs such as network-backed atlas/template fetches are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `REPORT.md` | Some package versions are listed, but pandas and matplotlib and system/runtime requirements are omitted. |
| must/013 | P.3 | unmet | judgement | `REPORT.md` | No environment specification is included in the worker stop state. |
| must/014 | P.3 | unmet | judgement | `REPORT.md` | No environment specification or dependency-update procedure is supplied. |
| must/015 | D.1 | unmet | judgement | `REPORT.md` | No complete pinned environment specification is supplied. |
| must/016 | D.1 | unmet | judgement | `.git/config` | No worker-declared route publishes the environment specification or complete project for retrieval. |
| must/017 | D.1 | unmet | judgement | `REPORT.md` | No instructions explain how to obtain and install the analysis environment. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `probe:tree-clean` | Git is present and annex tracks inputs, while the delivered analysis, report and results are untracked. |
| should/002 | A.2 | not-checked | probe:ci-present | `probe:ci-present` | No evidence establishes that the workflow is tested regularly; a test/CI history would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `REPORT.md` | Inputs, analysis, results and figures have separate folders, but no environment module is provided. |
| should/004 | E.1 | not-checked | judgement | `results/analysis_summary.json` | The delivered outputs show work was produced, but no evidence establishes testing in a fresh environment. |
| should/005 | E.1 | unmet | judgement | `analysis/group_analysis.py` | The script runs in the caller's Python process and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `REPORT.md` | No exact environment specification exists to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `REPORT.md` | No environment artifact, executable image or complete package snapshot is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `REPORT.md` | No environment-update process exists; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: supplied data and software are public; no restricted component exists in this study. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json` | N/A: no independently maintained project modules; source data are included and Python packages are runtime dependencies. |
| may/002 | M.2 | partial | judgement | `REPORT.md` | The report links input, analysis and output areas, but does not document a component composition diagram or module interface. |
| may/003 | M.2 | partial | judgement | `analysis/group_analysis.py` | Folders separate data and outputs, but one script couples the complete analysis and no independent module boundaries are described. |
| may/004 | M.2 | unmet | judgement | `analysis/group_analysis.py` | No mechanism composes separately maintained modules; execution is a single script. |
| may/005 | M.2 | met | judgement | `REPORT.md` | The report links readers to the script, methods, machine-readable results and figures. |

### Flagged items

- **must/004, should/001 — `mapping-questioned`:** the tree-clean probe measured uncommitted paths; this assessment used the complete stop state to judge whether Git tracked the worker's delivered code, report and results.
- **must/005 — `probe-overridden`:** annex pointers were real, but the stop receipt shows annex setup and input maps were inherited from the seed commit; no worker-produced image output was tracked.
- **must/006, must/008, must/011, must/012, should/006, may/001 — `probe-overridden`:** tracked-path/format probes missed untracked scientific outputs and/or deferred to manual inspection; these verdicts use the complete delivery and read the supplied code/docs.
- **should/003 — `mapping-questioned`:** the module probe measured tracked directory names and missed untracked analysis, result and figure folders; no environment module exists.
- **should/008 — `upstream-duplicate`:** this checklist item repeats must/014 by design.

### Not checked and access

- **should/002:** regular testing is not established; a repeated test/CI or equivalent execution history would settle it.
- **should/004:** no evidence establishes a fresh-environment run; a recorded run in a clean environment with the exact worker specification would settle it.
- **Access:** intended recipient is a researcher using the worker's declared authorized route. No route was declared in the report or captured Git config; upstream source URLs are not a route to this analysis delivery. Required coverage is code, all 54 maps and metadata, results, figures, report and environment specification. No route host was tested. Coordinator access to the retained capture does not show worker publication. Details are in [access.json](2026-10-16-access.json).
- **Replay:** one attempt was allowed, but none was launched because complete prerequisites could not be established from worker-supplied instructions/declarations. No outputs were removed. The candidate script outputs and comparison plan are in [replay.json](2026-10-16-replay.json).

### Goals and kind

The stated goal is a group-level assessment of whether potential gain has a positive fMRI response in vmPFC in the equal-indifference NARPS group, using fixed participant maps and whole-brain correction; the retained task brief is the source. This is a **study**: the deliverable is a scientific answer with its code, inputs and results. No human clarification was attached; this goal and kind are treated as supplied assumptions.

Checklist link: [2026-10-16-url.txt](2026-10-16-url.txt). Canonical per-item record: [2026-10-16-response.json](2026-10-16-response.json). Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).

**Stamp:** Produced with `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0; checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on 2026-10-16 using Codex API / gpt-6-luna and the pinned neutral-v1 runner. Worker stop commit: `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`. Complete delivery manifest SHA-256: `30c1789617c94c9281de732c088ff1cb50ca8c42114be533237ab3e53e76d06f`; worker-stop receipt SHA-256: `48129fa8fe6dbcf60b02077ede0587888bc760ebd714bffd490c9a5c11f541fa`. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).
