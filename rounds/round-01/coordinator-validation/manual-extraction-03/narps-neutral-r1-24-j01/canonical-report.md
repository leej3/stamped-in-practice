# Independent assessment — NARPS potential-gain group analysis

## Verdict

**MUST:** 4 met / 6 partial / 7 unmet / 0 not-checked / 0 not-applicable (17).  
**SHOULD:** 0 met / 2 partial / 5 unmet / 1 not-checked / 1 not-applicable (9).  
**MAY:** 4 met / 0 partial / 0 unmet / 1 not-checked / 0 not-applicable (5).

These are checklist item counts, not a single overall score. `Partial` does not satisfy a MUST.

## What to fix first

1. **Commit or otherwise track the analysis, report, figures, and results at the worker stop.** These files were present in the complete delivery but untracked, so the Git commit does not identify the scientific product or capture how it changed (`must/004`, `should/001`).
2. **Include a portable, complete environment specification and use a relative entry command.** The README points to an absolute interpreter and manifest outside the project; that prevents an independent reader from reconstructing the stated environment and following the documented run (`must/003`, `must/007`–`must/008`, `must/010`–`must/017`, `should/006`–`should/008`).
3. **Link each result set to a retained execution record and exact environment.** The summary captures package versions, parameters, and a code hash, but no frozen environment or captured execution record (`must/006`, `must/015`).
4. **Publish the complete research object through a worker-declared route.** The tested NeuroVault and GitHub routes cover source inputs, not the code, report, figures, derived maps, or environment (`must/016`–`must/017`).

## What the delivery does well

- The delivered project has one root and contains the scientific artifacts alongside input metadata. All 1,144 workspace entries match the retained capture manifest; this includes files outside Git tracking. The input maps are internally linked to retained annex payloads (`must/001`–`must/002`, [manifest verification](manifest-verification.json)).
- The protocol states the estimand, participant-level sign-flip max-*t* inference, whole-brain correction, mask, atlas ROI, and planned coverage sensitivity ([analysis protocol](../../../../../../judge-targets/narps-neutral-r1-24-j01/content/workspace/analysis/protocol.md)).
- The report interprets copes as normalized-modulator effects rather than currency-unit slopes, gives uncertainty and first-level variance limitations, and does not treat the absence of vmPFC support as proof of zero effect ([scientific report](../../../../../../judge-targets/narps-neutral-r1-24-j01/content/workspace/report/report.md)).

## Scientific adequacy — **qualified**

**Reported hypothesis outcome:** no whole-brain-corrected evidence supports a positive vmPFC gain effect in this group. This is a lack of support for the positive hypothesis, not a claim that the effect is exactly zero.

The group analysis uses the 54 supplied equal-indifference participants, checks map IDs, hashes, dimensions, affine geometry and finite values, and excludes none. It estimates an unweighted participant mean cope and uses 9,999 participant sign flips with a maximum positive *t* statistic over the whole common-coverage mask. The primary analysis contains 198,029 voxels; the reported threshold is *t*=5.38. No vmPFC annotation voxel survives whole-brain FWE (*minimum FWE p*=0.780), and the broad atlas ROI mean is −0.0048 (95% *t* interval −0.0243 to 0.0147). A 90%-coverage sensitivity analysis gives the same lack of vmPFC support. The report appropriately distinguishes 24 corrected posterior occipito-temporal voxels from evidence for the vmPFC hypothesis ([primary summary](../../../../../../judge-targets/narps-neutral-r1-24-j01/content/workspace/results/summary.json), [sensitivity summary](../../../../../../judge-targets/narps-neutral-r1-24-j01/content/workspace/results/sensitivity_90pct/summary.json)).

The inferential approach is defensible for these participant-level effects: maps are not mistaken for *t/z* statistics; the study-mandated whole-brain correction is applied; the participant is the sampling unit; and the report states the sign-symmetry assumption and absence of within-participant variance maps. The protocol calls itself frozen before analysis, but its files were untracked at worker stop and no timestamped run record establishes that chronology. A superseded permutation run is retained and labeled invalid; the final code uses the corrected studentized statistic and reports SciPy cross-checks. The no-support conclusion is reasonably supported conditional on AO86's fixed upstream model.

The rating is qualified because coverage is inferred from exact nonzero cope values rather than a supplied explicit coverage mask; the Harvard–Oxford atlas is in a different MNI template variant from the maps and is resampled directly; and the broad Frontal Medial/Subcallosal/Frontal Orbital annotation is an operational proxy rather than a narrow vmPFC boundary. Participant QC values are retained, but the report does not state explicit outlier thresholds or show a separate anatomical overlay validating the atlas-to-map alignment. These limitations weaken precise anatomical and null interpretation without creating a material error in the reported lack of corrected vmPFC support. The estimate remains conditional on normalized gain scaling, separate gain/loss models, and unavailable first-level variance maps; it does not estimate response per currency unit or establish equivalence.

The coordinator-cited original NARPS PDF could not be fetched by the browser tool (timeout); the whole-brain-correction requirement was available in the supplied scientific task and guidance. The failed fetch is recorded separately in [scientific-guidance-fetch.json](scientific-guidance-fetch.json).

## Delivery boundary and attribution

The delivery manifest is complete and verified against the unchanged workspace: 666 regular files and 54 symlinks had no content or target mismatches. The 54 participant map links resolve to annex payloads inside the workspace, using the retained dependency mapping. The manifest reports no omissions. The recorded worker stop was 2026-10-16 07:27:26 UTC at commit `675620fed8a134102b1b07226fe39d67630ee6f7`; its receipt records a normal exit. At that stop, `README.md`, `analysis/`, `figures/`, `report/`, and `results/` were untracked. The commit is the initial supplied-input commit, not a worker commit containing the results. The input maps, cohort table, source manifest, task, and upstream methods are identified as supplied resources in the stop receipt. Their annexing and source URLs are properties of the delivered inputs, not worker-created versioning or publication. No Git remote is recorded in the captured `.git/config`; external hooks paths were not followed. Coordinator preservation and delivery to this assessment do not establish worker publication.

## Access check

The intended recipient is a researcher using the public source route declared in `input/sources.json`. `neurovault.org` returned HTTP 200 for the collection and a HEAD request to one representative map; `raw.githubusercontent.com` returned HTTP 200 for the pinned cohort table. The map body was not downloaded and all 54 map endpoints were not individually tested. This route covers retrieval of source maps and source cohort metadata. No worker-declared route was found for the analysis code, report, figures, derived results, or environment; coordinator delivery is not proof of access from the worker's stop state. See the [access record](2026-10-16-access.json) and retained headers.

## Replay

**Not checked; no replay was run.** The documented command depends on an absolute Python executable and `pixi.toml` outside the assessed root, and the complete delivery contains no environment declaration from which to reconstruct the prerequisite. External targets were not followed and no substitute environment was created. The planned command, prerequisites, selected generated artifacts, comparison rule, and frozen limits are recorded in the [replay record](2026-10-16-replay.json). Shipped results are assessed as scientific evidence, not presented as replay evidence.

## STAMPED checklist details

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `../../manifest.json` | Workspace has one root; the manifest verifies all 1,144 workspace entries. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data` | All 54 source maps resolve through relative in-root annex links; cohort and sources are under input/. |
| must/003 | S.1 | unmet | judgement | `analysis/run_analysis.py`, `README.md` | The analysis imports external Python packages, but no environment specification is included in the workspace. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `tree-clean: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#tree-clean` | Git tracks supplied inputs, but the analysis, report, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `large-in-annex: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#large-in-annex` | Git-annex stores all 54 participant map payloads; the complete capture retains their bytes. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/summary.json`, `README.md` | Results record package versions and parameters, but no exact environment specification is linked to the run. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `entry-point: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#entry-point` | README instructions identify a script and command, but rely on an absolute environment path absent from this delivery. |
| must/008 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `entry-point: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#entry-point` | A main script is documented, but the declared command depends on an external environment unavailable in the workspace. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `no-abs-paths probe: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#no-abs-paths` | The analysis script builds project paths from __file__ and uses no hardcoded host paths. |
| must/010 | P.1 | unmet | judgement | `env-spec-tracked probe: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#env-spec-tracked` | Dependencies are listed in prose, but no environment specification declares all software dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md`, `results/summary.json` | Python package versions are named, but the required host environment and external atlas retrieval/cache assumptions are not reproducibly specified. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md` | README lists Python and package versions, but omits a portable system requirements and dependency specification. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `env-spec-tracked: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#env-spec-tracked` | No environment specification is present in version control or the complete delivered workspace. |
| must/014 | P.3 | unmet | judgement | `../../manifest.json` | No dependency update or environment regeneration process is documented. |
| must/015 | D.1 | unmet | judgement | `results/summary.json`, `README.md` | The exact environment specification used for results is outside the delivery and is not linked in a retained run record. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `env-spec-tracked: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#env-spec-tracked` | No worker-published environment or complete research object retrieval route is recorded. |
| must/017 | D.1 | unmet | judgement | `README.md` | README names an external environment path but does not explain how a recipient can obtain it. |
| should/001 | T.2 | partial | judgement | `tree-clean and large-in-annex: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json` | Git and annex cover supplied inputs, but scientific code and outputs were outside version control at worker stop. |
| should/002 | A.2 | not-checked | judgement | `ci-present: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#ci-present` | No retained schedule or recurring test log establishes regular workflow testing; such run records would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `modules-separated: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json#modules-separated` | Inputs, analysis, results and figures have separate directories, but the environment is external and lacks a module boundary. |
| should/004 | E.1 | unmet | judgement | `results/summary.json`, `README.md` | The recorded run used the supplied prepared host environment; no fresh container, batch job, VM or cloud run is evidenced. |
| should/005 | E.1 | unmet | judgement | `README.md`, `results/summary.json` | Execution instructions use a shared prepared environment; no per-run disposable environment is provided. |
| should/006 | D.2 | unmet | judgement | `env-spec-tracked and ci-present: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/judgment/2026-10-16-probes.json` | No exact environment specification exists to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `../../manifest.json` | No environment artifact is archived in the complete delivered workspace. |
| should/008 | D.2 | unmet | judgement | `README.md` | No process for updating dependency specifications is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the declared data and software components are public; no restricted material requires a separate module. |
| may/001 | M.2 | met | judgement | `input/sources.json`, `neurovault-route-map.headers` | The independently maintained source dataset is identified by its NeuroVault collection and per-map retrieval URLs. |
| may/002 | M.2 | met | judgement | `README.md`, `analysis/protocol.md` | README and analysis protocol explain input, code, results, figures and how the workflow connects them. |
| may/003 | M.2 | not-checked | judgement | `README.md` | Separate directories are present, but no compatibility contract or independent-update evidence establishes whether modules can change safely. |
| may/004 | M.2 | met | judgement | `README.md`, `analysis/run_analysis.py` | The README documents a direct composition route: run the analysis script against input/ to generate results/ and figures/. |
| may/005 | M.2 | met | judgement | `README.md` | README links the report and protocol and names the primary inputs, results and figures. |

### Flagged items

- `must/004`: the probe's untracked-path finding was refined to partial because some supplied inputs were tracked while the scientific product was not.
- `must/007` and `must/008`: the filename-based probe missed the untracked README and analysis entry point; the documented route exists but depends on an outside environment.
- `must/009`: the path probe only covered tracked files; direct inspection found the script uses `__file__`-relative paths, so the item is met. The absolute interpreter in README affects the documented execution route and is handled under `must/007` and `must/008`.
- `should/008`: duplicate of `must/014` in the pinned checklist; both are unmet because no environment-update process is documented.

### Not checked

- `should/002`: no retained evidence establishes routine repeat testing; regular test logs or a schedule would settle it.
- `may/003`: the directories are described, but independent module update compatibility is not established; a module contract or update test would settle it.
- Replay: the documented outside environment cannot be verified from the delivery; an in-boundary environment specification would permit the single scoped replay.

## Goals and kind

**Assumption (not confirmed by a human):** this is a study whose product is a group-level scientific conclusion from supplied participant effect maps. The stated goal is to assess a positive gain effect in vmPFC for the equal-indifference group with whole-brain correction. This is a **study**; the strongest emphasis is on input reachability, tracking of scientific outputs, linking results to actions and environment, and a recipient's ability to retrieve the complete research object.

## Checklist and provenance

[Open the filled STAMPED checklist](2026-10-16-url.txt). The validated per-item record is [2026-10-16-response.json](2026-10-16-response.json), and the frozen probe receipt is [2026-10-16-probes.json](2026-10-16-probes.json).

Produced using `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1, with the verified frozen assessment runner source `9852d8360f9519d21d11099b45f5deb8ba80cb28` and runtime `3552d5003a2485b6405805236d5c54e7ed42f097`, on the original delivery at commit `675620fed8a134102b1b07226fe39d67630ee6f7`, 2026-10-16. The worker-stop receipt is [worker-end-state.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-24/judgments/narps-neutral-r1-24-j01/attempt-01/worker-end-state.json). The assessed capture manifest SHA-256 is `76ac670f9e4cce6766e693dd8c5530c28998efb09d91bbeb09fbb3ef8198c311`.
