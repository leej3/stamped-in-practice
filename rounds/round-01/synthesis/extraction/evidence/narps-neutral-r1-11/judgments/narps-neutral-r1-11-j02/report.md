# Independent assessment — NARPS potential gains and vmPFC

**STAMPED verdicts:** MUST: 5 met / 2 partial / 10 unmet / 0 not-checked (17); SHOULD: 0 met / 2 partial / 6 unmet / 0 not-checked, 1 not-applicable (9); MAY: 3 met / 1 partial / 0 unmet / 0 not-checked, 1 not-applicable (5). Partial does not satisfy a MUST. No overall score is assigned.

## What to fix first

1. Add a relocatable, pinned environment specification and reproducible setup instructions, then record which environment produced each result. The current report points to a machine-specific interpreter and does not declare its imported packages. This closes the main gaps in MUST 003, 006, 010–017 and SHOULD 006–008.
2. Track the worker-created analysis, report, and results in the repository. The stop receipt shows those directories were untracked; the annexed participant maps were supplied in the seed state. This addresses MUST 004–005 and SHOULD 001.
3. Publish a retrieval route for the complete study deliverable, including code, report, generated maps/tables/figures, and environment. The checked URLs cover inputs, not the worker-created analysis product.
4. For a sharper anatomical claim, map the Harvard–Oxford ROI into the maps' MNI152NLin2009cAsym space with a documented transform or use a vmPFC definition already in that space.

## What the project does well

- It includes all 54 input maps and cohort metadata in the common root, and the analysis verifies participant hashes, finite values, and common image geometry (`analysis/run_analysis.py`, `input/sources.json`).
- The analysis uses a directional one-sample group test with whole-brain max-statistic correction, an independently defined ROI proxy, and participant-level QC; the report distinguishes a null finding from evidence of an exact zero (`report.md`, `results/results.json`).
- The report documents the limits of the supplied cope estimates, the missing first-level variance maps, the standardized gain modulator, and the sign-symmetry assumption (`input/upstream-methods.md`, `report.md`).

## Scientific assessment (separate from STAMPED)

**Adequacy: qualified.** The group analysis is a defensible analysis of the supplied fixed inputs. It includes the full 54-person group, treats participant maps as independent effect estimates, uses a common-support mask based on nonzero coverage rather than effect direction, and tests the positive hypothesis with 10,000 participant sign flips and a whole-brain maximum-t correction. The ROI summary is descriptive and the corrected map is the primary inference. The input documentation and report correctly limit the coefficients to the upstream mean-centered, variance-normalized gain regressor; they are not slopes per currency unit. The absence of participant variance maps appropriately prevents precision weighting or auditing the first-level fits.

The main qualification is anatomical: the supplied maps are MNI152NLin2009cAsym, while the included Harvard–Oxford atlas is on the standard MNI152 grid. The script resamples the atlas by affine onto the map grid but does not document a nonlinear template transform. The report appropriately calls the Frontal Medial and Subcallosal labels a proxy, but precise vmPFC membership is therefore uncertain. The sign-flip test also relies on participant-level error symmetry under the null. These limitations qualify the anatomical interpretation without invalidating the broad whole-brain group test.

**Reported hypothesis outcome: no corrected support for a positive vmPFC effect.** The shipped summary reports a vmPFC proxy mean of 0.0062, *t*(53)=0.47, one-sided descriptive *p*=0.321, 95% CI [−0.0204, 0.0327], and zero ROI voxels surviving whole-brain FWE correction. Elsewhere, 24 voxels survived correction (global FWE *p*≈0.00060; peak *t*=6.62 at the Occipital Pole); this does not support the vmPFC hypothesis. The result is absence of corrected evidence in this sample and model, not proof that the true effect is zero or that smaller/subregional effects are absent (`results/results.json`, `results/figure1_whole_brain.png`, `results/figure2_vmPFC_participants.png`). These are shipped worker outputs, not replay results.

## Delivery boundary, attribution, and measurement limits

The worker stop receipt records HEAD `eece8595d255a766517e32ff10b2e6574d3c4e6a`, an exited worker, and the complete stopped workspace. The initial check found all 1,238 entries present and all 726 regular-file hashes matching (458 directories also present; no declared omissions or capture errors). A follow-up hash check found every surviving regular file and symlink still matched the manifest. The 54 annexed maps appear in the receipt as supplied seed identities. The worker-created `analysis/`, `report.md`, and `results/` were untracked at stop; the report and script are therefore part of the scientific delivery but not worker-tracked outputs. No worker publication route for these outputs or a worker environment lock was identified. Coordinator delivery and retention are not credited as worker publication, annex conversion, or environment capture.

The assessor probe pass was followed by disappearance of `.git/annex/keysdb/db-shm` and `db-wal`, two transient sidecars present in the initial manifest. All substantive scientific files remained hash-identical. The frozen replay helper then failed capture preflight with `Capture file list differs (missing or unexpected entries)` before materializing a copy or executing the target. No repair was made and the single allowed attempt was not repeated. Replay is **not checked** due to assessor-side measurement interference; this is not target execution failure. See [replay plan](2026-10-16-replay-plan.json), [replay record](2026-10-16-fresh-rerun.json), [captured stdout](2026-10-16-fresh-rerun.stdout), [stderr](2026-10-16-fresh-rerun.stderr), and [capture difference](2026-10-16-capture-diff.json).

**Access record.** Intended recipient: a researcher using the routes declared in `input/sources.json`. NeuroVault's map URL for `sub-001` and the pinned raw GitHub `participants.tsv` URL both returned HTTP 200 from the assessor host on 2026-10-16. This tests those two host/path examples, not every map. The declared routes provide a working route for the maps and cohort metadata, but the recorded AO86 methods-workbook URL returned HTTP 404. The supplied upstream-methods.md remains present. No declared route covers the worker's script, report, results, or environment. Anonymous access was not required. Coordinator delivery to the assessor is not evidence of worker access. Details and retained command output: [access record](2026-10-16-access.json), [map request](2026-10-16-access-curl.stdout), [metadata request](2026-10-16-access-metadata.stdout), [methods request](2026-10-16-access-methods.stdout).

**Assumptions and scope.** No human guidance was attached. I treated the stated goal in `input/study-task.md` as a group-level assessment study and the primary object kind as **study**. The scientific assessment uses the unchanged scientific file bytes from the initially verified complete delivery. The report states that the worker installed and used the `datalad-fsck` skill; I recorded that exposure but did not use it as grading evidence. No external Git pointer was followed, no Git command was run through an external `.git` pointer, no treatment assignment was inferred, and no scientific replay output is claimed. The script itself uses root-relative paths; the absolute interpreter path documented in the report is assessed under host assumptions and environment requirements. Probe status details are in [probes](2026-10-16-probes.json); the full item table follows.

## Per-item STAMPED table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `report.md` | All captured files are nested under the workspace root. |
| must/002 | S.1 | met | judgement | `input/participants.tsv` | The supplied dataset and metadata are included under input/ and read by the relative-path analysis. |
| must/003 | S.1 | unmet | judgement | `analysis/run_analysis.py` | Scientific Python dependencies are used but no environment specification or linked software module is delivered. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `git status --porcelain` | Git tracks the supplied inputs, but the worker's analysis, report, and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+judgement | `input/data/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-11/judgments/narps-neutral-r1-11-j02/attempt-01/worker-end-state.json` | The 54 supplied maps use git-annex, but worker-generated binary results were untracked and annex use was inherited. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/results.json` | No exact environment specification is linked to the shipped results; results.json lists package versions only. |
| must/007 | A.1 | met | probe:entry-point+judgement | `report.md#Reproduction and artifacts` | report.md gives reproduction instructions and the analysis command despite no README or Makefile. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/run_analysis.py` | analysis/run_analysis.py is a clear starting point that creates the reported results. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `analysis/run_analysis.py` | The script uses root-relative paths, while the documented command hardcodes a host-specific interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/run_analysis.py` | No environment specification declares the imported scientific packages or their versions as installable dependencies. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `report.md#Reproduction` | The report depends on a host-specific absolute interpreter path and does not document the required host setup. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md#Reproduction` | There is no clear system requirement or dependency list; the report only names a machine-specific Python executable. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment specification is included in the worker's version-controlled state. |
| must/014 | P.3 | unmet | judgement | `complete stopped delivery` | No environment update process is declared or evidenced in the stopped delivery. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/results.json` | No frozen environment specification is included to reproduce the reported analysis environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `sources.json` | No environment specification is published or retrievable with this worker delivery. |
| must/017 | D.1 | unmet | judgement | `report.md#Reproduction` | The report does not explain how to obtain or recreate the required environment. |
| should/001 | T.2 | partial | judgement | `worker-end-state.json` | Git-annex tracks supplied inputs, while worker-created code and outputs were untracked at stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present` | The delivery contains one analysis run but no recurring test or review process for the reproduction instructions. |
| should/003 | M.1 | partial | probe:modules-separated | `input/, analysis/, results/; report.md` | Inputs, code, and results have separate folders, but no environment module is provided. |
| should/004 | E.1 | unmet | judgement | `report.md#Reproduction` | The recorded worker execution used a persistent supplied host environment; no fresh container or clean instance is specified. |
| should/005 | E.1 | unmet | judgement | `analysis/run_analysis.py` | The workflow does not create a disposable environment for each run. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probe:ci-present` | There is no environment specification that can be regularly reconstituted and checked. |
| should/007 | D.2 | unmet | judgement | `results/atlas/` | The project does not archive a reproducible software environment; the retained atlas is data, not an environment artifact. |
| should/008 | D.2 | unmet | judgement | `must/014` | No environment update process is declared or tracked; this repeats must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivered maps and software are public; no restricted component is present. |
| may/001 | M.2 | not-applicable | judgement | `input/ and results/atlas/` | N/A: no independently maintained project component is linked as a module; inputs and atlas assets are included directly. |
| may/002 | M.2 | met | judgement | `report.md#Analysis and #Reproduction` | The report describes the input, analysis, and result artifacts and their relationship. |
| may/003 | M.2 | partial | judgement | `analysis/run_analysis.py` | The folders separate inputs, code, and results, but no formal module interfaces support independent updates. |
| may/004 | M.2 | met | judgement | `analysis/run_analysis.py` | The analysis script composes the included inputs into the reported result set. |
| may/005 | M.2 | met | judgement | `report.md#Reproduction and artifacts` | The report names the reproduction command and result paths, giving users a way to navigate the object. |

## Flagged items

- **MUST 004:** The tree-clean probe found untracked worker outputs; Git exists, but those delivered code/results were not tracked at stop.
- **MUST 005:** The annex probe measured the supplied input maps. Stop-state attribution shows these were seed resources; worker-generated result maps remained untracked.
- **MUST 007–008:** The entry-point probe only recognized README/Makefile conventions. The report provides instructions and `analysis/run_analysis.py` is a usable starting point.
- **SHOULD 002:** No CI was found, and the complete delivered study shows one analysis run but no regular workflow-check process.
- **SHOULD 008:** This repeats MUST 014 by design.

The license extra finding is confirmed for the study itself: no project-level license or reuse terms were found. A bundled helper-skill LICENSE does not state terms for the study outputs; this is outside the pinned checklist items.

## Not checked

- **Scientific replay:** the sole allowed attempt failed in frozen assessor preflight after the probe pass altered transient annex sidecars. A fresh capture-integrity check would settle replay, but this assessment did not repair or retry the source.
- **Full remote retrieval:** only one map and the metadata URL were checked from the assessor host; the other 53 map URLs and full object coverage were not fetched or tested.

## Checklist URL and provenance

Checklist app link: [2026-10-16-url.txt](2026-10-16-url.txt). Canonical response: [2026-10-16-response.json](2026-10-16-response.json). Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad`), on the captured workspace at commit `eece8595d255a766517e32ff10b2e6574d3c4e6a`, 2026-10-16, Codex API; assessor model identity was not disclosed by the harness. Original capture manifest SHA-256: `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa`; worker stop receipt SHA-256: `326729607bc2dd9e90676b27d7204dd180cee4b3cdc2491383b6ec65728910b1`. Probe output is linked above. The response JSON records the capture scope and pins.
