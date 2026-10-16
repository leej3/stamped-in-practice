# Independent assessment — NARPS Hypothesis 1 group analysis

## Verdicts

**MUST:** 4 met / 3 partial / 9 unmet / 1 not-checked (17 items). **SHOULD:** 0 met / 1 partial / 5 unmet / 2 not-checked / 1 not-applicable (9 items). **MAY:** 1 met / 2 partial / 1 unmet / 0 not-checked / 1 not-applicable (5 items). `Partial` does not satisfy a MUST. There is no overall score.

**Scientific adequacy: qualified — the reported lack of whole-brain-corrected vmPFC evidence is supported conditional on the supplied maps, but anatomical coverage and equal-weight group inference limit the strength and scope of that conclusion.**

**Hypothesis outcome:** “In the equal-indifference group, these maps do not provide whole-brain-corrected evidence that the gain effect is positive in vmPFC.”

**Capture boundary.** The canonical original complete delivery has SHA-256 `7918c97a370bac1741a7558d4eccbf52e164ae63cef2e6ce9248e066ee6da58e`; the worker stop receipt has SHA-256 `4eefa66bdb111f9042ca6c2370f4f597991f6aa646a4376363dd7b9853d7d44c`. `C:<path>` below means that capture-relative path in the canonical delivery. The captured original HEAD is `767f76ed3d12c3a7ff9fb23989358c768b301bc5`. The operational manifest initially matched the canonical manifest; inspection used the operational copy. The inspection changed regular-file `.git/annex/keysdb/db` metadata (same size, different SHA-256); it is separately classified operational metadata and does not establish logical database equivalence. The launcher verifies the canonical capture before and after assessment. No non-exempt integrity mismatch was found.

## What to fix first

1. Track the analysis script, report, figures and results at the worker stop, and publish a stable versioned project route. This makes the actual answer inspectable and retrievable; addresses must/004, must/016 and should/001.
2. Include and publish a complete pinned environment specification with install/use instructions. The documented absolute interpreter path depends on an external host environment; addresses must/003, must/007, must/010–017 and should/005–008.
3. Add a worker run record connecting exact input identities, command, environment and generated results. This makes the shipped result traceable to its computation; addresses must/006.

## What is already good

- The complete 54-map input set and metadata are inside the workspace, and the captured inputs are annex-backed (worker attribution is not established) (C:`content/workspace/input/sources.json`; C:`content/workspace/input/data/sub-001_hypo1_cope.nii.gz`). The documented NeuroVault collection responded to HTTP HEAD (details in `access-record.md`).
- The analysis checks cohort correspondence, byte hashes, finite values and image geometry, and reports exclusions and uncertainty (C:`content/workspace/analysis/run_analysis.py`; C:`content/workspace/analysis/report.md`).
- The primary group test uses a positive one-sample sign-flip maximum-*t* permutation correction over the common mask; vmPFC localization is explicit and does not restrict the primary test (C:`content/workspace/analysis/run_analysis.py`; C:`content/workspace/analysis/report.md`).

## Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/analysis/run_analysis.py` | All essential project files and inputs are within the workspace root; data links resolve to local annex content. |
| must/002 | S.1 | met | judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/input/sources.json` | All 54 input maps and metadata are delivered under input/ and map links resolve within the captured root. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analysis/report.md`, `content/workspace/analysis/run_analysis.py` | The delivered code depends on Python packages in an external host environment; no environment file or linked module is supplied. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `content/workspace/analysis/run_analysis.py`, `content/workspace/.git/index` | The worker's analysis code, report and results were untracked at stop; the sole captured commit does not version them. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `content/workspace/.git/COMMIT_EDITMSG`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-12-j02/attempt-01/worker-end-state.json` | Annex storage is visible, but stop evidence identifies these maps as supplied inputs and does not attribute annex setup to the worker. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/analysis/results/results.json`, `content/workspace/analysis/report.md` | Shipped results have no worker run record linking outputs, actions and an exact environment; the later assessor replay is not worker provenance. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/analysis/report.md` | The report documents usage, but gives no instructions for obtaining or installing its external environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/analysis/report.md`, `content/workspace/analysis/run_analysis.py` | The report gives a clear runnable starting command and names the analysis script. |
| must/009 | P.1 | met | judgement | `content/workspace/analysis/run_analysis.py` | The analysis script uses paths rooted relative to its own location; the host-specific interpreter path is documented separately. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analysis/report.md`, `content/workspace/analysis/run_analysis.py` | The report lists versions but no complete installable dependency specification is delivered. |
| must/011 | P.1 | unmet | judgement | `content/workspace/analysis/report.md` | The documented command assumes a host-specific absolute interpreter and external environment without documenting host requirements. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/analysis/report.md` | The report names Python package versions, but omits complete installation and system requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/.git/index`, `content/workspace/analysis/report.md` | No environment specification is versioned alongside the code and data. |
| must/014 | P.3 | unmet | judgement | `content/workspace` | No environment update process or tracked environment specification is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked | `content/workspace/analysis/report.md` | No frozen environment manifest or container digest is supplied to reproduce the reported package set. |
| must/016 | D.1 | unmet | judgement | `content/workspace/input/sources.json`, `content/workspace/.git/config` | The worker provides no project publication route; tested NeuroVault access covers source maps, not code, environment or results. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/analysis/report.md` | The report explains how to run the script but not how to obtain its external Python environment. |
| should/001 | T.2 | unmet | judgement | `content/workspace/analysis/run_analysis.py`, `content/workspace/.git/COMMIT_EDITMSG` | Worker analysis code and results were untracked; the tracked input state was supplied and cannot establish worker version control across components. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `content/workspace` | No CI or repeated-test record is present; regular testing outside the captured workspace cannot be established. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input`, `content/workspace/analysis` | Inputs and analysis outputs are separated, but code shares analysis/ with results and no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/analysis/report.md` | Worker-stop evidence does not show a fresh environment test; the assessor replay cannot establish worker practice. |
| should/005 | E.1 | unmet | judgement | `content/workspace/analysis/report.md` | The documented route invokes one pre-existing shared environment, not a disposable environment per execution. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `content/workspace` | No environment specification or record of regular reconstitution testing is supplied. |
| should/007 | D.2 | unmet | judgement | `content/workspace` | No environment lock, container image or executable environment artifact is archived in the project. |
| should/008 | D.2 | unmet | judgement | `content/workspace` | No environment update process or tracked specification is supplied; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: no restricted data or software component is identified; source inputs are publicly retrievable. |
| may/001 | M.2 | not-applicable | judgement | `content/workspace/input`, `content/workspace/analysis/run_analysis.py` | N/A: no independently maintained project modules are assembled; input data are included and runtime packages are dependencies. |
| may/002 | M.2 | partial | judgement | `content/workspace/analysis/report.md` | The report relates inputs and outputs, but does not document the project module boundaries or how to recombine them. |
| may/003 | M.2 | unmet | judgement | `content/workspace/analysis/run_analysis.py` | The analysis assumes a fixed root layout and does not define independently updateable component boundaries. |
| may/004 | M.2 | met | judgement | `content/workspace/analysis/run_analysis.py` | The analysis script composes the included input module and analysis outputs through root-relative paths. |
| may/005 | M.2 | partial | judgement | `content/workspace/analysis/report.md` | The report identifies input, results and figures, but offers no overall module map or navigation guide. |

## Flagged items

- **must/005:** annex backing is observable, but the seeded input state does not establish worker attribution; the probe credited storage regardless of provenance.
- **must/006, must/011, must/012, should/006:** complete-workspace reading resolves missing run/environment records or host-path assumptions beyond the probes’ tracked-path and recognized-record scope.
- **must/007, must/008:** the probe sees tracked HEAD, while the delivered report and entry script are untracked but present in the complete stopped workspace; the report gives a use command, but not environment acquisition instructions.
- **must/014, should/008:** these are duplicate checklist questions and carry the same answer by design.

## Not checked

- **must/005:** annex storage is visible, but the stop record identifies the maps as supplied inputs and does not attribute annex setup to the worker; worker attribution evidence would settle it.
- **should/002:** the capture contains no CI or repeated-test history. A dated regular test record or workflow would settle it.
- **should/004:** worker-stop evidence does not establish a fresh-environment test. A worker-attributed fresh run would settle it. This assessment’s replay does not earn worker-practice credit.

## Goals and kind

Assumption, not confirmed with human guidance: the goal is to answer whether potential gain increases vmPFC response in the equal-indifference group using the supplied fixed participant maps, with whole-brain-corrected inference. This is a **study**: its product is a group-level scientific conclusion with reproducible code, results and figures. This kind gives greatest emphasis to linking results to actions/environments and keeping essential inputs reachable in the study boundary.

## Scientific assessment

The worker analyzed all 54 equal-indifference participants with no exclusions. The script checks IDs against the participant table, verifies input size and SHA-256 against `sources.json`, checks finite values and matching dimensions/affines, and defines common coverage as voxels nonzero in every map (C:`content/workspace/analysis/run_analysis.py`; C:`content/workspace/input/participants.tsv`; C:`content/workspace/input/sources.json`). This is a transparent conservative mask, though treating every zero as outside coverage can discard genuine in-mask zero estimates if any occur.

The primary analysis tests the positive mean cope with 10,000 subject-level sign flips and a maximum positive studentized statistic across the whole common mask. The report gives a 95th-percentile threshold of *t* = 5.38 and conditions validity on a symmetric participant-level null (C:`content/workspace/analysis/run_analysis.py`; C:`content/workspace/analysis/report.md`; C:`content/workspace/analysis/results/results.json`). The broad Harvard–Oxford composite is identified as an approximation and used descriptively, not for small-volume inference. The vmPFC mean was 0.00265, its 95% *t* interval crossed zero, and no vmPFC voxel survived whole-brain correction; the significant small clusters were occipital and were not assigned a gain-valuation interpretation (C:`content/workspace/analysis/report.md`; C:`content/workspace/analysis/results/results.json`; C:`content/workspace/analysis/results/whole_brain_fwe_clusters.tsv`).

The report correctly states that the supplied maps estimate a mean-centered, variance-normalized gain modulator rather than a slope per currency unit, that gain and loss were modeled separately, and that participant variance maps are absent (C:`content/workspace/input/upstream-methods.md`; C:`content/workspace/analysis/report.md`). The wide interval and leave-one-out sign changes do not support an equivalence or exact-null claim. Atlas choice and the nonzero-based coverage mask leave anatomical and coverage uncertainty. These limits qualify the inference but do not overturn the cautious conclusion: the supplied maps do not establish the prespecified positive vmPFC effect at the stated whole-brain error rate. This is lack of support, not proof of no effect. The scientific task’s whole-brain correction requirement follows the original [NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

## Worker stop, versioning and access

The stop receipt records a complete capture and the same HEAD as `judge-target.json`. At stop, `analysis/` and `.codex/` were untracked and `.entire/` was ignored. The only Git commit was `767f76e` (“chore(study): supply materialized scientific inputs”); therefore the analysis code, report, figures and result files were present in the delivery but not versioned in the worker repository (C:`content/workspace/.git/HEAD`; C:`content/workspace/analysis/run_analysis.py`; C:`content/workspace/analysis/report.md`; C:`content/workspace/analysis/results/results.json`). The 54 input maps were annex-backed at the captured stop (C:`content/workspace/input/data/sub-001_hypo1_cope.nii.gz`; C:`content/workspace/.git/annex/objects`). Coordinator preservation and this assessment replay do not change those worker-stop judgments.

The intended recipient is a researcher seeking the study inputs and analysis. No worker-declared project retrieval route is present. The source route in supplied `input/sources.json` was checked as context: NeuroVault’s collection page returned HTTP 200 to HEAD on this host; no map body was fetched. It covers upstream source maps, not the worker’s code, report, environment or result artifacts. No worker project remote is recorded in `.git/config`; delivery to the coordinator is not worker publication. The complete recipient, route, coverage and tested-host record is `access-record.md`. No project-level license is declared. The only captured `LICENSE.txt` is scoped to the bundled PDF skill; public retrieval does not establish reuse terms.

The stopped workspace contains `.entire` session-trace and assistant-session metadata paths. I recorded that exposure but did not inspect those trace contents or use them as grading evidence. No treatment assignment was inferred or reported.

## Measurement availability and replay

The frozen probe run covers tracked Git paths and reports analysis artifacts absent from HEAD. Manual assessment used the entire captured workspace, including untracked and ignored files. This distinction yields met on must/008 (the untracked but documented entrypoint exists) and partial on must/007 (usage is documented, environment acquisition is not). Probe output is retained at `2026-10-16-probes.json`.

One frozen replay recreated all 11 selected generated artifacts byte-for-byte from a fresh writable copy of the canonical complete delivery. It used the worker-documented absolute interpreter, captured maps/metadata/atlas cache, no input retrieval and no code repair; elapsed time was 18.4 seconds (see `replay-plan.md` and `2026-10-16-fresh-rerun.json`). This supports computational repeatability in the tested host and environment, not scientific validity or worker-attributed environment capture. The complete original capture, with uncommitted and ignored files, was used; HEAD was not substituted.

## Checklist link and stamp

The per-item machine record is [`2026-10-16-response.json`](2026-10-16-response.json); the checklist link is [`2026-10-16-url.txt`](2026-10-16-url.txt).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on canonical capture SHA-256 `7918c97a370bac1741a7558d4eccbf52e164ae63cef2e6ce9248e066ee6da58e` at original commit `767f76ed3d12c3a7ff9fb23989358c768b301bc5`, 2026-10-16, Codex API / GPT-6 (exact runtime variant unavailable). Probe output: `2026-10-16-probes.json`.
