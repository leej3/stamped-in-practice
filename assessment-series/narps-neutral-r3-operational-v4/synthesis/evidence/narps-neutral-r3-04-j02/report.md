# Independent assessment — 2026-10-16

## Verdict

MUST: 4 met / 4 partial / 9 unmet / 0 not-checked (17 items). SHOULD: 0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 items). MAY: 3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable (5 items). No overall score is assigned.

## What to fix first

1. Add a tracked, installable and locked environment specification and document how to create it → readers cannot reconstruct the software needed for the analysis → must/003, must/010, must/013, must/015, should/006, should/007.
2. Record each analysis run with its exact environment and outputs → the shipped statistics cannot currently be traced to an execution state → must/006.
3. Track the worker-authored report, script, results and figures in version control → Git currently identifies only the supplied starting inputs → must/004, should/001.
4. Replace the absolute shared-interpreter command with a portable documented setup and state the atlas network prerequisite → the present entry command depends on a host path and undeclared connectivity → must/007, must/009, must/011, must/012, must/017.
5. Publish an authorized retrieval route covering inputs, code, report and results, then test it from a researcher context → coordinator delivery to the assessor does not establish worker publication → must/016.

## What the project already does well

- It includes all 54 gain-effect maps and cohort metadata beneath `input/`, and records upstream sources and retrieved-byte checksums (`input/sources.json`, capture SHA-256 `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`; source file SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`).
- The single analysis script checks cohort membership, checksums, image grids and finite values, documents the group model and generates inspectable tables, maps and figures (`scripts/group_analysis.py`, capture SHA-256 `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`; file SHA-256 `a801bee36ed5c95416d3da617ec17771a8ea6f5908e4c3926b6bfad83a5cd348`).
- The report distinguishes participant effect estimates from test statistics, uses a positive one-sample group test with whole-brain maximum-t FWE correction, and explains the ROI definition and limits (`report.md`, same capture SHA-256; file SHA-256 `1ea3e153e8b124308f628c609744a72b0a43819177c8a2b7d786b2c7121e8c58`).

## Scientific assessment

**Scientific adequacy: supported.** Conditional on the supplied AO86 participant maps, the reported conclusion is adequately supported: the analysis tested a positive group effect and applied one-sided maximum-t family-wise error correction across the stated whole-brain search mask. The report separately localized vmPFC with an atlas-defined ROI, found no overlap with corrected positive voxels, and did not treat the corrected occipital finding as support for the vmPFC hypothesis. Its effect-size interpretation, lack of participant variance maps, and non-detection limitations are appropriately qualified.

**Hypothesis outcome (reported conclusion):** “The supplied maps do not support a greater vmPFC response with increasing potential gain in the NARPS equal-indifference group.” The ROI mean was −0.0108 (95% CI −0.0304 to 0.0089); the most positive vmPFC voxel had whole-brain corrected p = .777. The whole-brain positive peak (left occipital pole, pFWE = .0008) is outside the hypothesized region. These findings support lack of detected positive vmPFC evidence at the chosen whole-brain FWE threshold, not proof of a zero effect.

The analysis uses 54 independent participants, checks matching IDs, map checksums, dimensions, affine and finite values, and excludes none. It appropriately treats maps as cope estimates rather than standardized statistics, uses a one-sample group model without precision weights unavailable from the inputs, and accounts for the twice-wide gain range and the upstream mean-centered, variance-normalized regressor. The atlas ROI is an explicit operational definition rather than a universal vmPFC boundary. The principal residual limitation is that nonzero map support is used as the coverage indicator; no separate participant coverage maps were supplied, so the common-support mask and corresponding search space cannot be independently verified as a pure coverage mask. Atlas resampling and sign-exchangeability assumptions also limit interpretation, and the report acknowledges them. None undermines the stated conditional, non-detection conclusion enough to change the adequacy category.

Evidence: canonical capture SHA-256 `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`, especially `report.md`, `results/summary.json` (file SHA-256 `fb2dd6927429851608dc0e3d7a26c1dc42437980f5735f555072f6fecd20fad3`), `results/participant_qc_and_roi.csv` (file SHA-256 `cb092a613fa779c800923b35764ab5d52d95b1baf20484082422e17ed86f35a5`), and `scripts/group_analysis.py`.

### Replay measurement

The one permitted frozen replay attempt is **not checked**. The helper failed before materializing a copy or executing the target because its destination existed; this was an assessor-side setup malfunction. The failed command, stdout and traceback are retained in `replay.command.txt`, `fresh-rerun.stdout.txt` and `fresh-rerun.stderr.txt`; `fresh-rerun.json` records the attempt. No target behavior was observed, no scientific output was regenerated, and no second attempt was made. Thus replay does not add to or detract from the scientific adequacy assessment.

## STAMPED item table

Evidence paths below are relative to the canonical captured workspace identified by SHA-256 `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`, except where the worker stop receipt or frozen probe record is named explicitly. The complete responses and evidence descriptions are in [response.json](response.json); the preserved scripted probe output is [probes.json](probes.json).

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `.git/HEAD`, `report.md` | All delivered paths are under the workspace root in the complete captured tree. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `scripts/group_analysis.py` | All 54 maps and metadata are within input/; the analysis resolves them from the workspace root. |
| must/003 | S.1 | unmet | probe:env-spec-tracked+judgement | `scripts/group_analysis.py`, `report.md` | Python analysis dependencies are listed but no installable environment or linked software module is delivered. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `report.md`, `scripts/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j02/attempt-01/worker-end-state.json` | Git versions the supplied inputs, but worker report, code, results and figures were uncommitted at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j02/attempt-01/worker-end-state.json` | The 54 large supplied maps are carried through git-annex in the captured state; this storage was inherited from supplied inputs. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/summary.json`, `report.md` | Shipped results lack a worker run record linking their generation to an exact environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md` | report.md gives a run command, but installation and environment acquisition instructions are absent and its interpreter path is host-specific. |
| must/008 | A.1 | met | probe:entry-point+judgement | `scripts/group_analysis.py` | The documented scripts/group_analysis.py has a main entry point that performs the full group analysis. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `report.md`, `scripts/group_analysis.py` | Analysis paths are relative, but the documented reproduction command hardcodes an absolute host interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `scripts/group_analysis.py`, `report.md` | No dependency specification includes the imported packages or atlas retrieval prerequisite. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `scripts/group_analysis.py`, `report.md` | The script needs network access to fetch the atlas, but that host assumption is not documented in the worker report. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `report.md`, `scripts/group_analysis.py` | Python and package versions are listed, but installation and the atlas network requirement are not specified. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `scripts/group_analysis.py`, `report.md` | No environment specification is included alongside the code and data. |
| must/014 | P.3 | unmet | judgement | `report.md`, `scripts/group_analysis.py` | No process for updating an environment specification is documented or tracked. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `report.md`, `scripts/group_analysis.py` | A package version list does not capture the exact environment; no frozen manifest or image is delivered. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j02/attempt-01/worker-end-state.json` | No worker-published route exposes the analysis artifacts and their required input coverage. |
| must/017 | D.1 | unmet | judgement | `report.md`, `scripts/group_analysis.py` | The report has a command but no instructions to obtain or install the absent environment specification. |
| should/001 | T.2 | partial | judgement | `report.md`, `scripts/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j02/attempt-01/worker-end-state.json` | Git tracks supplied inputs, while worker-authored code, results and figures were uncommitted at stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `scripts/group_analysis.py` | No CI, test suite or recurring workflow-check process is present in the complete delivery. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/`, `scripts/group_analysis.py`, `results/`, `report.md` | Inputs, code and results have separate directories, but no environment module exists and outputs remain untracked. |
| should/004 | E.1 | unmet | judgement | `report.md`, `scripts/group_analysis.py` | No fresh container, VM, batch or cloud execution is documented or configured. |
| should/005 | E.1 | unmet | judgement | `report.md` | The documented command uses a shared interpreter and does not create a disposable environment. |
| should/006 | D.2 | unmet | judgement | `report.md`, `scripts/group_analysis.py` | No exact environment specification exists to reconstitute or test regularly. |
| should/007 | D.2 | unmet | judgement | `report.md`, `scripts/group_analysis.py` | No environment artifacts are archived in the worker delivery. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment update process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software components are identified in this public-input study. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json`, `scripts/group_analysis.py` | N/A: the study has no independently maintained project components; datasets are included and Python packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `report.md` | The report identifies inputs, code, result files and figures and explains their roles. |
| may/003 | M.2 | partial | judgement | `scripts/group_analysis.py`, `report.md` | The directory boundaries are visible, but the single script hardcodes their paths and modules cannot be updated independently through a documented interface. |
| may/004 | M.2 | met | judgement | `report.md`, `scripts/group_analysis.py` | The documented command runs the entry point that composes supplied inputs into results and figures. |
| may/005 | M.2 | met | judgement | `report.md` | The report names and describes the input, script, results and figure files. |

## Flagged items

- **must/002, must/008, must/009, must/011, must/012, must/015, may/001:** the probe could not settle the complete untracked workspace, entry-point equivalence, report-level absolute path, host network requirement, or absence of project modules/environment. Direct reading of the captured files determines the recorded verdicts.
- **must/004 and must/007:** the probe treated only the Git tree and conventional README/Makefile as decisive; the complete capture includes untracked deliverables and `report.md` gives partial reproduction instructions.
- **must/006:** probe did not recognize untracked outputs or their absent worker run record; direct inspection shows shipped results without environment-linked provenance.
- **should/002:** no recognized CI config is present; the complete delivery also lacks a test harness or recurring workflow-check record.
- **should/008:** duplicate of must/014 in the pinned checklist; flagged as an upstream duplicate.

## Not checked

- **Replay measurement:** the frozen helper malfunction described above consumed the single permitted attempt. A replay measure would require a correctly configured fresh destination in a future authorized assessment.
- The worker declared no publication or retrieval route for this analysis product. Therefore no worker route was available to test; the coordinator's delivery of the capture to the assessor does not establish researcher access.

## Goals, kind and access

The stated goal is a group-stage test of whether potential gain has a positive fMRI response in vmPFC among the NARPS equal-indifference group, using 54 supplied gain-effect maps and metadata without repeating preprocessing or participant modeling (`input/study-task.md`, capture SHA-256 `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`; file SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`). I classify the object as a **study**: its product is a scientific answer with code and derived results. This classification follows the supplied task and is an assumption for this assessment; no human guidance was attached.

**Access record.** Intended recipient: a researcher using the worker's declared authorized route. Worker-declared route: none for the report, code and results. Required coverage for a reproducible handoff: report, analysis script, all 54 maps, cohort/source metadata, derived tables, maps and figures, plus environment specifications. Tested host scope: none, because there was no worker route to test. `input/sources.json` contains upstream source URLs for inputs; those are not publication of this analysis product. The captured `.git/config` has no worker remote. The coordinator's retained capture is not counted as worker access or publication. Access details are also in [access-record.json](access-record.json).

## Attribution, exposure and integrity

The worker stop receipt (SHA-256 `1b8872c1194f929b734c3561f01244142f875c42247976f605fc3983cf497fea`) records HEAD `c5e927c2c46296ba59886bffc66dc165f9cf2c78` and a complete stop capture with no omissions. That commit contains the supplied starting material; `report.md`, `scripts/`, `results/` and `figures/` appear as worker-stop artifacts outside that HEAD. The coordinator's later retention or delivery does not earn worker tracking, publication or environment credit. Original evidence paths and hashes in this report refer to the canonical capture, not inspection-generated state.

The captured `.entire/logs/entire.log` includes a `codex` agent identifier and checkpoint entry, which reveals assistant use. I record this exposure but did not use those session identifiers or logs as grading evidence. I did not inspect other workers' outputs, prior judgments or assignment records, and did not infer a treatment assignment.

The post-inspection integrity comparison found a changed regular file `.git/annex/keysdb/db` and added regular `.git/annex/keysdb/db-shm` and `db-wal`, all within the separately classified operational-metadata exception. This is inspection-induced metadata, not worker evidence. No other content, link, index, ref, object, configuration or ignored-file change was found. This byte-level allowance does not establish logical database equivalence. See [integrity-check.stdout.txt](integrity-check.stdout.txt).

## Checklist link and provenance

Checklist URL: [open the completed STAMPED checklist](2026-10-16-url.txt). Machine-readable responses: [response.json](response.json). Probe receipt: [probes.json](probes.json). Replay attempt: [fresh-rerun.json](fresh-rerun.json).

Produced using the frozen external assessment runner and runtime identified by the supplied assessment pin, with the STAMPED checklist 0.3.1 and assessment conventions 0.1.0, on the canonical capture SHA-256 `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`, original HEAD `c5e927c2c46296ba59886bffc66dc165f9cf2c78`, 2026-10-16. Model identity was not exposed by the assessment harness. Probe output: [probes.json](probes.json).
