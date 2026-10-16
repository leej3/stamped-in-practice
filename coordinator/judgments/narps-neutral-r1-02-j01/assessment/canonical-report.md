# Independent assessment — NARPS gain effect in vmPFC

**STAMPED verdicts:** MUST: 5 met / 2 partial / 10 unmet / 0 not-checked / 0 not-applicable (17). SHOULD: 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable (9). MAY: 0 met / 3 partial / 2 unmet / 0 not-checked / 0 not-applicable (5). Partial does not satisfy a MUST; no overall score is calculated.

**Scientific adequacy: supported. Reported hypothesis outcome: not supported** at the required whole-brain-corrected level. This does not establish no vmPFC response.

## What to improve first

1. Track the analysis, report, figures and results in Git so the worker's commit identifies the scientific delivery (**must/004**).
2. Add a pinned, tracked environment specification, a usable install/setup route and host requirements; link results to that environment (**must/003, 006, 007, 010–017**).
3. Publish a researcher-authorized route to the complete object, including the annex payloads and environment materials (**must/016–017**).
4. Add repeatable workflow and environment testing records, and document how the input, analysis and atlas components relate (**should/002–008; may/002–005**).

## What is already done well

- The analysis verifies SHA-256 hashes for all 54 maps and checks geometry and finite values before inference ([group script](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-02-j01/content/workspace/analysis/group_analysis.py), [summary](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-02-j01/content/workspace/results/summary.json)).
- Whole-brain Bonferroni FWE controls the hypothesis test, while the anatomical ROI is specified independently of the observed effect ([report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-02-j01/content/workspace/report.md)).
- The report distinguishes lack of support from proof of no effect and explains upstream scale and variance limitations ([report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-02-j01/content/workspace/report.md)).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/judge-target.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/delivery-verification.json` | All delivered files, including the annex object store, sit under the workspace root. |
| must/002 | S.1 | met | judgement | `input/data/`, `analysis/group_analysis.py`, `.git/annex/` | All 54 supplied maps are reachable through relative links into the in-root annex store; code and inputs share the workspace root. |
| must/003 | S.1 | unmet | judgement | `analysis/group_analysis.py`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | The analysis imports scientific software, but no dependency specification or linked software module is delivered. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/delivery-tree-comparison.json` | Git tracks the seed, but the analysis, report, figures and results are untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | judgement | `.git/annex/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json` | git-annex stores all 54 binary map payloads inside the captured .git/annex object store. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/run.log`, `report.md` | The run log and report do not link the generated results to an exact environment specification. |
| must/007 | A.1 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | The report gives a run command but no installation instructions or usable dependency setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analysis/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json` | The report identifies analysis/group_analysis.py and gives its invocation as the results entry point. |
| must/009 | P.1 | met | judgement | `analysis/group_analysis.py` | The analysis script builds paths from its own root and uses relative project paths. |
| must/010 | P.1 | unmet | judgement | `analysis/group_analysis.py`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | No environment specification declares the imported Python dependencies. |
| must/011 | P.1 | unmet | judgement | `report.md` | The documented command assumes a host-specific prepared interpreter path; host setup requirements are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md` | The report names Python and package versions, but does not give a complete system/dependency setup. |
| must/013 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | No environment specification is included in the tracked project. |
| must/014 | P.3 | unmet | judgement | `report.md`, `analysis/group_analysis.py` | No process for updating and tracking dependency specifications is declared. |
| must/015 | D.1 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | No exact environment specification is supplied for reconstructing the analysis environment. |
| must/016 | D.1 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/access-record.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | No worker-declared route shares an environment specification. |
| must/017 | D.1 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | The report points to a prepared interpreter but gives no route to obtain or recreate that environment. |
| should/001 | T.2 | met | judgement | `.git/HEAD`, `.git/annex/` | One Git repository is used for the tracked project material; binary inputs use the in-repository annex store. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json`, `.codex/`, `results/run.log` | No repeated or scheduled workflow-test record was found; the probe only ruled out recognized CI configuration. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/`, `analysis/`, `results/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json` | Inputs, code and results have separate directories in the complete delivery; environment definitions are absent and worker-produced modules are untracked. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/replay-record.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/replay-record.json` | No clean-container or fresh-host run record is supplied; the bounded captured-delivery replay adapter is unavailable for this frozen runner. |
| should/005 | E.1 | unmet | judgement | `analysis/group_analysis.py`, `report.md` | No workflow creates a disposable environment for each run. |
| should/006 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | There is no exact environment specification or record of regularly testing its reconstruction. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/judgment/workspace-files.json` | No environment artifact is archived with the project. |
| should/008 | D.2 | unmet | judgement | `report.md`, `analysis/group_analysis.py` | No dependency update process is declared or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `report.md` | N/A: inspected contents show public study inputs and no restricted data or software component. |
| may/001 | M.2 | unmet | judgement | `analysis/atlases/README.md`, `analysis/atlases/` | Atlas resources are copied into the workspace without independently retrievable component links or module boundaries. |
| may/002 | M.2 | partial | judgement | `report.md` | The report names input, analysis and result paths, but does not document a modular composition model. |
| may/003 | M.2 | partial | judgement | `input/`, `analysis/group_analysis.py`, `report.md` | Inputs and analysis have directory boundaries, but their independent update contract is not documented. |
| may/004 | M.2 | unmet | judgement | `report.md`, `analysis/group_analysis.py` | Separate input, code, atlas and result directories exist, but no mechanism is documented for composing them as modules. |
| may/005 | M.2 | partial | judgement | `report.md` | The report links the script and result locations, but offers no broader navigation guide for the workspace. |

## Additional finding outside the pinned checklist

The frozen probe found no project-wide license declaration. The retained `COPYING` file is nested with an upstream atlas and does not establish terms for the worker-authored analysis and report. This is recorded as an extra finding in the response JSON; it does not change checklist counts.

## Flagged items

- **must/004 (`probe-overridden`):** `tree-clean` marked the repository unmet because four worker-produced directories/files were untracked. The item is partial: Git is used for the seed code and inputs, but omits substantive delivered analysis and outputs.
- **must/008 (`probe-overridden`):** `entry-point` did not recognize the untracked `report.md` and its named script. Manual review found a clear documented invocation and analysis entry point, so this item is met. Installation instructions remain unmet under must/007.
- **should/003 (`probe-overridden`):** the probe counted tracked paths and therefore missed the untracked `analysis/` and `results/` directories present in the complete delivery. The item remains partial because no environment module is supplied.
- **should/008 (`upstream-duplicate`):** repeats must/014's dependency-specification update process.

## Not checked

- **should/002:** no evidence establishes whether the workflow is tested regularly. A CI filename scan is not enough; repeated manual or scheduled run records would settle it.
- **should/004:** the replay used the documented interpreter on the assessment host, not a fresh container, batch environment, VM or cloud host. A worker-recorded run in one of those environments would settle it.
- **Access route:** no worker-declared complete-object route was available to test. A route for an authorized researcher that covers the full object, including annex content, would settle it.

## Scientific assessment

The delivered analysis supports its stated conclusion that these supplied maps do not provide evidence for a positive gain effect in vmPFC. It treats the 54 inputs as participant effect estimates, not test statistics, and applies a one-sample positive-direction test across participants. It intersects participant coverage with a resampled ICBM brain mask, reports image geometry and finite-value checks, excludes no participants, and applies Bonferroni familywise correction over 186,611 voxels. Its anatomically specified AAL proxy combines bilateral medial orbital frontal and rectus labels; this is a defensible vmPFC approximation, and the report acknowledges its limits. The displayed ROI estimate is descriptive and its uncorrected ROI p-value is not used to claim support.

The vmPFC proxy mean is −0.00363 map units (95% CI −0.02847 to 0.02120; one-sided *p* = .615; *n* = 54). None of the 11 positive voxels surviving whole-brain correction overlaps the proxy. The three reported foci are small posterior occipital foci. The report appropriately avoids interpreting these map units per currency unit, since the upstream gain regressor was variance-normalized. It also notes that participant variance maps are unavailable, gain and loss were modeled separately, and a nonsignificant result is not an equivalence test.

I reviewed the group script, report, numerical summary, cluster and participant tables, and all three figures. The figures make the target ROI, participant spread and corrected whole-brain findings inspectable. The delivered summary is internally consistent with the report and tables. A one-sample model is defensible for the independent participant maps; limitations include the absent within-participant variance estimates, assumptions about between-participant effects, use of nonzero values as a coverage proxy, and use of the symmetric 2009a mask as an approximation to the maps' 2009c space. These are disclosed or bounded and do not materially undermine the conclusion.

The frozen complete-delivery helper copied the verified workspace, used the report's documented command, and removed only the two explicitly selected generated TSVs in the copy. The tables were byte-identical after rerun (`rtol=1e-6`; no tolerance-only differences occurred). The helper retained stdout/stderr and reported no capture omissions. Replay corroborates these selected outputs only; it does not independently validate unselected maps or confer worker-practice credit. See [replay record](replay-record.json), [replay declaration](replay-declaration.json), and [captured command stdout](replay.stdout).

## Capture, worker stop and access

The manifest file digest matches the capture digest in the worker-stop receipt; the receipt itself has SHA-256 `82f54530325e3ea11b0ac50513a18c3dbf514b94ba460933d28b4efd6744267d`. I compared every one of 1,139 manifest entries, including content hashes, link targets and modes, and the full filesystem tree: there are no missing, altered or unmanifested entries, and the capture reports no omissions or errors. The retained relative annex links resolve inside the captured workspace to the 54 stored map payloads. I did not follow external targets or use an external Git pointer.

The [worker-stop receipt](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-02/judgments/narps-neutral-r1-02-j01/attempt-01/worker-end-state.json) records a clean worker exit at 2026-10-16 07:04:26 UTC and commit `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`. At that stop, `analysis/`, `figures/`, `report.md` and `results/` were untracked. They are included in the verified complete delivery and count as scientific evidence, but are not represented by that commit; this is why version-control attainment is partial. The workspace contains an annex object store, but no worker-supplied environment lock/specification. The report names a prepared interpreter and package versions, which enabled the bounded replay; the assessment-host environment and replay do not count as worker environment capture or sharing. No complete-object retrieval route was declared in the report or source index. The intended researcher recipient, required artifact coverage and tested host scope are recorded in [access record](access-record.json); no worker route was available to test.

The workspace includes `.codex/` and `.entire/` session material. I record that exposure without using session contents or identifiers as grading evidence. I do not infer or report a treatment assignment. A local assessor verification script initially expected a `target` manifest key instead of `link_target`; the corrected manifest and tree comparisons passed. A first response validation also caught my incorrect checklist repository metadata; I corrected it and the frozen validator passed all 31 answers. These assessor-side errors are recorded in [process notes](assessor-process-record.md) and did not affect target evidence.

## Goals and kind

The coordinator-supplied scientific task sets the goal: group-level inference for the positive parametric gain effect in vmPFC for the equal-indifference cohort, conditional on the 54 supplied participant maps and metadata. The object is a **study** analysis. Emphasis is on traceable analysis, actionable reproduction, modular inputs/code/results, portable environments and distributable access.

## Checklist, stamp and response

Checklist response: [open the filled checklist](2026-10-16-url.txt). Machine-readable answers are in [2026-10-16-response.json](2026-10-16-response.json); the frozen scripted probe output is in [probes.json](probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.2.0 with `stamped-conventions` 0.2.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the local captured object at commit `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`, 2026-10-16, Codex/GPT-6. Capture: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-02-j01/manifest.json`, SHA-256 `b8c5ed926b870d7d78ec6ecc4fbccd218f12523802ded9d082f032d901fd9aec`. Probe output: `probes.json`.
