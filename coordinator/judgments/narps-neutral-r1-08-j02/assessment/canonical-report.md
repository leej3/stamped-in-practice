# Independent assessment: NARPS Hypothesis 1

Assessment date: 2026-10-16 UTC. Object kind: **study**. The goal is the coordinator-supplied scientific question in the retained brief: test whether potential gain has a positive group effect in vmPFC for the equal-indifference cohort. This goal and kind are assumptions from the supplied brief and delivered report; no human guidance was attached to confirm them.

## Verdicts

MUST: **5 met / 1 partial / 11 unmet / 0 not-checked** (17 items)

SHOULD: **1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable** (9 items)

MAY: **1 met / 2 partial / 0 unmet / 0 not-checked / 2 not-applicable** (5 items)

No overall score is assigned.

## What to fix first

1. Add a pinned, retrievable environment specification with installation instructions and a dependency update procedure. It matters because the shipped analysis cannot be reconstructed from the worker delivery. Closes must/003, 010–017; should/006–008.
2. Record the exact command, environment identity, inputs and outputs for each run. It matters because the code and results coexist without a worker run record linking them. Closes must/006 and should/006.
3. Track the delivered report, analysis code and generated results at worker stop. It matters because the current Git commit omits the principal scientific deliverables. Closes must/004.
4. Document an authorized retrieval route covering the analysis, data, results and environment. It matters because coordinator delivery alone does not make the worker's object accessible to another researcher. Closes must/016–017.
5. Add repeatable clean-environment checks once the environment is declared. It matters because instructions and environment reconstruction have no repeat-test evidence. Closes should/002, 004 and 006.

## What the project already does well

- The supplied maps are separately represented by git-annex pointers and materialized in-boundary payloads; all 54 scientific map payload hashes match the stop receipt (`input/data/`, `worker-end-state.json`).
- The scientific report gives a whole-brain max-T correction, an explicit vmPFC proxy, participant-level quality checks, uncertainty and a careful account of the limits of the supplied effects (`REPORT.md`, `analysis.py`, `results/summary.json`).
- Inputs, code, results and figures can be navigated within one workspace, and the analysis uses paths relative to its own location (`analysis.py`, `input/upstream-methods.md`).

## Scientific assessment

**Scientific adequacy: supported. Reported hypothesis outcome: not supported.** These are distinct labels: the analysis supports its limited conclusion that these data do not provide evidence for a positive vmPFC gain response; it does not support the positive hypothesis.

The delivered report and outputs include all 54 participant gain-effect maps and report no participant exclusions. `analysis.py` checks map count, image dimensions, affine equality and finite values; uses a common MNI brain mask with a 95% nonzero-coverage rule; and tests the positive group effect with 10,000 participant-level sign flips and whole-brain maximum-*t* FWE correction over 190,657 voxels. The 12-mm sphere centered at MNI [0, 40, −12] is an explicit, literature-motivated operational vmPFC proxy intersected with the tested mask (762 voxels). The ROI mean is −0.0057 (95% *t* interval [−0.0323, 0.0210]); the one-sided ROI test is *t*(53) = −0.43, *p* = .664, and no ROI voxel survives whole-brain correction. The whole-brain corrected positive peak (*t* = 6.62, FWE *p* = .00090) is at [−26, −102, −3.6], outside the vmPFC proxy, and is not used as evidence for the hypothesis (`REPORT.md`; `results/summary.json`; `figures/whole_brain_fwe.png`; `figures/vmPFC_participants.png`).

The linked original NARPS instructions PDF timed out during direct retrieval (400); the whole-brain correction requirement and interpretation above follow the supplied task and coordinator scientific guidance. The failed retrieval is retained in `commands/narps-instructions-fetch.txt`.

The inference is conditional on the fixed AO86 participant model. The effects are mean-centered, variance-normalized gain coefficients, not changes per currency unit; participant-level variance maps are unavailable; and sign-flip inference assumes exchangeable, approximately symmetric participant effects under the null. The confidence interval includes modest effects in either direction, so the non-significant vmPFC result is not evidence that the true response is exactly zero. The anatomical sphere is one defensible operational definition, not a unique vmPFC boundary. The reported absence of support is therefore appropriately limited; the posterior finding does not establish the hypothesized vmPFC response.

## Delivery verification and attribution

The assessor checked all 1,135 entries against the supplied manifest (436 directories, 645 files and 54 symlinks). The manifest has no declared omissions or errors, and the worker-stop receipt records a complete capture. One mismatch remains: `.git/annex/keysdb/db` is 53,248 bytes but its captured SHA-256 is `233c0be3…7372be80`, versus manifest SHA-256 `f6f8fd7a…c9fde5ca`. All 58 stop-receipt seed-input payloads match; specifically all 54 scientific map payloads match. I bound this discrepancy to Git-annex bookkeeping and do not treat it as evidence of changed scientific inputs. Full verification is in [delivery-verification.json](delivery-verification.json).

The captured `.codex/` and `.entire/` paths indicate coding-assistance/editor instrumentation was present. This exposure is recorded but not used as grading evidence; no treatment assignment is inferred.

At worker stop, the recorded commit was `eece8595d255a766517e32ff10b2e6574d3c4e6a`; `REPORT.md`, `analysis.py`, `figures/` and `results/` were untracked. `.codex/` and `.entire/` were ignored but included in the complete capture. I attribute the untracked state to the worker stop receipt, not to a later coordinator snapshot. The visible commit is retained as identity, not credited as worker tracking of the scientific deliverables. The annex-backed inputs were supplied resources; their presence does not establish a worker action. No worker run record identifies the exact environment used to make the shipped results.

## Access and replay

The intended recipient is a researcher using the worker's declared authorized route; anonymous access is not required. No route for retrieving the complete worker object was declared, and no route was tested. `input/sources.json` records original source URLs for maps and metadata, but these are provenance pointers rather than a route to the complete report, code, results and environment. The coordinator's local delivery to this assessment is not proof of worker publication. See [access-record.json](access-record.json) for recipient, required artifact coverage and host scope.

Replay is **not checked**. The report names `analysis.py` and refers to a “supplied Python environment,” but no environment declaration or dependency lock exists in the delivery. I did not execute with the coordinator's assessor runtime or repair the object. One planned invocation, its prerequisites, explicit output list and comparison rule are retained in [replay-record.json](replay-record.json). No replay attempt or replay-generated artifacts exist.

## STAMPED checklist

The checklist table below covers every pinned item. The probe output is retained in [2026-10-16-probes.json](2026-10-16-probes.json); individual readings and overrides are shown in the response and in the table.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/`, `analysis.py`, `results/`, `figures/` | Workspace root contains input, code, results and figures; supplied map links resolve within it. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/data/`, `input/participants.tsv`, `input/sources.json` | All 54 gain maps and participant metadata are included under input/; no external dataset route is needed. |
| must/003 | S.1 | unmet | judgement | `analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | analysis.py imports external Python packages, but no delivered environment spec or linked software module includes them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-08/judgments/narps-neutral-r1-08-j02/attempt-01/judgment/2026-10-16-probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-08/judgments/narps-neutral-r1-08-j02/attempt-01/worker-end-state.json` | Git is used, but analysis.py, REPORT.md, figures/ and results/ were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `input/data/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-08/judgments/narps-neutral-r1-08-j02/attempt-01/worker-end-state.json` | The 54 participant maps are git-annex pointers with in-boundary payloads; map identities match the stop receipt. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `analysis.py`, `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | Shipped results have no worker run record linking the analysis action to an exact environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `REPORT.md#Reproducibility files`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | REPORT.md names the script and says to use a supplied Python environment, but gives no install or executable usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md#Reproducibility files`, `analysis.py` | REPORT.md identifies analysis.py as the complete group workflow; the script is a usable starting point. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-08/judgments/narps-neutral-r1-08-j02/attempt-01/judgment/2026-10-16-probes.json` | The workflow builds input and output paths relative to its own location. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | Required Python packages are imported by analysis.py, but no environment specification declares them. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `REPORT.md#Reproducibility files`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | The route assumes a supplied Python environment, but the delivery documents no OS, Python stack or host prerequisites. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `REPORT.md`, `analysis.py` | No clear system requirements or dependency list is delivered. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | No environment specification is present in the complete worker delivery. |
| must/014 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | No environment update process is documented, and no environment specification is present. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json`, `results/summary.json` | No frozen environment specification identifies the packages used for the shipped results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config`, `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | No worker-declared route publishes an environment specification; the captured Git config has no remote. |
| must/017 | D.1 | unmet | judgement | `REPORT.md#Reproducibility files`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | The report refers to a supplied Python environment, but does not say how to obtain or reconstruct it. |
| should/001 | T.2 | met | judgement | `.git/config`, `input/data/` | One Git repository tracks code, inputs and configuration; git-annex stores the large map payloads. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-08/judgments/narps-neutral-r1-08-j02/attempt-01/judgment/2026-10-16-probes.json` | No repeated-test history or schedule is recorded; such records would establish regular workflow testing. |
| should/003 | M.1 | partial | probe:modules-separated | `input/`, `results/`, `figures/`, `analysis.py` | Inputs and generated outputs have separate directories, but code is at root and no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-08/judgments/narps-neutral-r1-08-j02/attempt-01/judgment/replay-record.json` | No fresh-environment run was attempted because the worker supplied no reconstructible environment; a clean run record would settle this. |
| should/005 | E.1 | unmet | judgement | `analysis.py` | analysis.py runs in the active Python environment and does not create a disposable environment per execution. |
| should/006 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | No exact environment specification exists to reconstitute and test against the shipped results. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | No environment image, binaries or archived environment artifacts are included. |
| should/008 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | No environment update process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `input/participants.tsv` | N/A: the supplied anonymized NARPS derivatives and software have no identified restricted component. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `.git/config`, `analysis.py` | N/A: there are no independently maintained project modules; package dependencies are not project modules. |
| may/002 | M.2 | partial | judgement | `REPORT.md#Reproducibility files`, `REPORT.md` | REPORT.md identifies the input, workflow, result maps and figures, but does not document their modular composition. |
| may/003 | M.2 | partial | judgement | `analysis.py`, `REPORT.md` | Inputs, code and outputs are separated by path, but the workflow has no environment boundary or documented component interface. |
| may/004 | M.2 | not-applicable | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-08-j02/manifest.json` | N/A: the object has no independently composed modules. |
| may/005 | M.2 | met | judgement | `REPORT.md#Reproducibility files` | REPORT.md explains the main script and enumerates the result and figure files for navigation. |

## Flagged items

- **must/002** — the probe only found no submodules; direct inspection showed all scientific input maps and metadata are inside the root.
- **must/006** — the probe missed untracked result artifacts; the complete stopped delivery contains results, but no worker record links them to an exact environment.
- **must/008** — the probe searched tracked paths and missed the untracked `analysis.py` identified by the report.
- **may/001** — the probe's lack of submodules did not settle the item; inspection found no independently maintained project modules, so it is not applicable.

## Not checked

- **should/002:** no repeat-test history or schedule was available; a run history or CI record would settle regular testing.
- **should/004:** no clean-environment replay was performed because the worker supplied no environment specification; a clean run in a declared environment would settle it.
- **Replay measurement:** not attempted for the same missing-prerequisite reason; details are in `replay-record.json`.
- **Worker retrieval route:** none was declared, so no route/host check could be made.

## Extra finding

Reuse terms are unstated: the complete worker delivery has no license file or BIDS license field. This is outside the pinned checklist and is retained as `license-declared` in `2026-10-16-response.json`.

## Checklist link and stamp

[Open the completed checklist](2026-10-16-url.txt). Canonical machine-readable answers and evidence are in [2026-10-16-response.json](2026-10-16-response.json); probe results are in [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on the captured study at Git commit `eece8595d255a766517e32ff10b2e6574d3c4e6a`, 2026-10-16, Codex 0.162.0-alpha.17.2 / GPT-6 (exact runtime variant not exposed). Frozen assessor pin: `assessment-version.json`; successful version check and runner logs are under `commands/`.
