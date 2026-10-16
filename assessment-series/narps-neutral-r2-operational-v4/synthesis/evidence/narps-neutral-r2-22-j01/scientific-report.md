# Independent assessment — NARPS potential-gain study

**Scope and identity.** I assessed the complete worker-stop workspace through its operational copy. The canonical original capture is `41f0afbc51de5f23bd32384cdeabb8734de508f73afc30e083baf23c4aa3ac7c`; the captured HEAD is `767f76ed3d12c3a7ff9fb23989358c768b301bc5`. Citations below use paths relative to the captured workspace, prefixed `content/workspace/`. Worker-stop evidence is the receipt at SHA-256 `96de7793e4f0b94f1ba2dfd09936e5644076f04420ad5eb53ab4e54f9dd0dbe7`.

The worker stop receipt records a completed stop with return code 0. The submitted analysis, report, figures and results are present in the complete capture but untracked at stop (`analysis/`); they were not part of HEAD. The Git commit and annexed input objects were present in the supplied state, so I do not attribute their creation or conversion to the worker. The worker's analysis package is assessed as scientific evidence, while versioning, environment and publication verdicts are based on the worker-stop state. The captured `.codex/` and `.entire/` metadata indicates assistant-tool use; I noted that exposure but did not use it as grading evidence. A broad initial read also exposed coordinator allocation metadata in the supplied procedure; it was excluded from the assessment, and I made no assignment inference.

**Capture integrity.** The canonical and operational initial manifests identify the same capture digest. After inspection, the only operational-copy deltas were regular files `.git/annex/keysdb/db`, `db-shm`, and `db-wal`, the three paths explicitly allowed for operational metadata. Scientific files, links, Git index/refs/objects and configuration matched the initial inventory. This is a byte-level path comparison only; it does not establish logical database equivalence. The inspection-induced database changes are not worker evidence.

## Verdicts

MUST: **4 met / 2 partial / 10 unmet / 1 not-checked** (17 items). SHOULD: **0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable** (9 items). MAY: **2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable** (5 items). A MUST marked partial is not satisfied. These are item counts, not an overall score.

## What to improve first

- Track the scientific analysis, report and generated results in the delivered version-control state; they are all untracked at stop. This closes the principal T.1/T.3 gap (must/004, should/001).
- Deliver a portable, complete environment specification and setup instructions, including the atlas/template resources or a declared retrieval route. This supports dependency completeness and repeatable use (must/003, 006, 007, 010–017; should/005–008).
- Publish a worker-declared access route covering code, data, results and the environment, and test retrieval as a researcher would. No remote or whole-object access route is present (must/016).

## What is already strong

- The result is inspectable: the report, analysis code, source checksums, quality checks, summary table, maps and figures are all in the complete capture (`content/workspace/analysis/README.md`, `analysis/analyze.py`, `analysis/report.md`, `analysis/results/`).
- The shipped group analysis checks participant/map identity, checksums, image geometry and common support; it includes all 54 participants and explains the missing participant-variance maps (`analysis/results/quality_checks.json`, `analysis/results/input_integrity.tsv`, `analysis/report.md#L9-L13`, `#L39-L41`).
- It uses a one-sided whole-brain maximum-t sign-flip procedure and an independent atlas proxy, reports uncertainty, and avoids treating a nonsignificant vmPFC result as proof of zero (`analysis/analyze.py#L45-L83`, `analysis/report.md#L11-L19`, `#L37-L41`).

## Scientific assessment

**Scientific adequacy: qualified.** The group analysis supports the narrow reported outcome under its stated independent-participant, symmetric-null and fixed-upstream-map assumptions. The maximum-t sign-flip procedure provides whole-brain family-wise control if participant effects are sign-symmetric under the null; the report states this assumption, but does not diagnose it. The atlas-defined medial-frontal/subcallosal ROI is a reasonable independent vmPFC proxy with an orbital-frontal sensitivity mask, but cannot represent every vmPFC boundary. Missing first-level variance maps also limit precision weighting and variance-component modeling. These qualifications do not overturn the report's appropriately conditional conclusion.

**Reported hypothesis outcome:**

> The supplied gain-effect maps do **not** support a positive gain response in vmPFC under whole-brain family-wise error (FWE) control.

That outcome is supported as a failure to detect a positive vmPFC effect under whole-brain correction, not as evidence that the true effect equals zero. The reported positive whole-brain cluster is posterior, with peak at MNI (−26, −102, −3.6), t(53)=6.62, max-T Monte Carlo pFWE=.0006; it does not overlap the core or broader medial/orbital frontal masks. Within the core proxy, mean cope is 0.0027 (95% t interval −0.0217 to 0.0270), uncorrected one-sided p=.414, and minimum whole-brain corrected p=.780 (`analysis/report.md#L17-L19`; `analysis/results/summary.tsv`). Figure 2 shows the corrected posterior signal (`analysis/figures/group_t_fwe_corrected.png`).

The code's common mask is finite and nonzero in all 54 maps, with matched shapes and affines; the report identifies the data as MNI152NLin2009cAsym and interprets the upstream mean-centered, variance-normalized gain coefficient in model units, not currency units (`analysis/analyze.py#L24-L44`, `#L75-L83`; `analysis/results/quality_checks.json`; `input/upstream-methods.md`). The one-sample group t statistic treats participant cope maps as independent observations and cannot weight by unprovided participant variances. The zero-intersection mask and atlas boundary condition the spatial inference. The report discloses these limits and the gain/loss range difference. No exclusion is reported.

## Access and sharing

The intended recipient is a researcher using the worker's declared authorized retrieval route. No such whole-object route is declared: the captured `.git/config` has no remote, and the analysis report gives no publication URL or access instructions. `input/sources.json` records source identities for input data only; it does not establish worker publication of this analysis. I checked the captured Git remote configuration and report, but did not attempt anonymous or external access because no worker route was provided. On this assessment host, all 54 relative input links resolved inside the captured annex object tree and their sizes and SHA-256 values matched `sources.json` (`logs/local-input-access.stdout`). This is a same-host inspection observation, not proof of worker access. Required coverage for a usable research delivery is the analysis code, report, generated results and figures, all 54 maps and metadata, and the environment/resource specification. Tested host scope: this local operational copy only. Coordinator delivery to this assessor does not establish worker-side availability.

## Replay

Replay status is **not checked**; no attempt was made. The documented command is the absolute shared-host interpreter shown in `analysis/report.md#L45-L51`, and no environment specification is included. The instruction forbids following that external absolute target; installing or inventing a replacement environment would also exceed scope. The script additionally fetches the Harvard–Oxford atlas and MNI template (`analysis/analyze.py#L75`, `#L156`), and the captured-delivery adapter does not retrieve scientific inputs. See `replay-record.json` for the declared command, prerequisites, exact generated-output selection and comparison rule. Shipped outputs were assessed as evidence, not counted as replay.

## STAMPED checklist

All item citations in the following table refer to the canonical capture digest stated above. Probe outputs came from the operational copy and are retained separately; they were checked against the complete captured artifacts. The probe's `entry-point` finding was overridden for must/008 because the untracked script and report do provide a start command. Its must/007 finding was also reviewed: equivalent usage documentation exists, but no installation route, so the item remains unmet. The annex probe's presence finding is not worker credit: the maps were supplied, so must/005 remains not-checked for worker practice. The no-submodule probe was overridden after inspecting the in-root annex mapping (must/002) and the absence of a separate project module (may/001).

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/study-task.md`, `content/workspace/analysis/README.md` | The complete study tree, inputs, analysis code, results and Git metadata sit under one workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/targets/narps-neutral-r2-22-j01/canonical/manifest.json` | All 54 input links resolve within the captured workspace to retained annex objects; no external data route is needed for this copy. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analysis/analyze.py`, `content/workspace/analysis/report.md` | The analysis imports external Python packages, but no dependency environment is delivered inside the project boundary. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `content/workspace/.git/HEAD`, `content/workspace/analysis/analyze.py`, `content/workspace/analysis/report.md` | Git tracks supplied inputs, while the scientific code, report, figures and results remain untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `worker-end-state.json` | Annex payloads are present, but the 54 maps were supplied; no worker action establishes annexing worker-generated large data. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/analysis/report.md#L45-L51`, `content/workspace/analysis/results/summary.tsv` | The result report names packages and a host path, but no run record links these results to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `content/workspace/analysis/README.md#L3-L11`, `content/workspace/analysis/report.md#L45-L51` | The report gives a run command, but provides no installation or environment setup instructions a recipient can follow. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/analysis/report.md#L45-L52`, `content/workspace/analysis/analyze.py` | The report identifies analysis/analyze.py as the entry point and documents the command that generated the analysis products. |
| must/009 | P.1 | met | probe:no-abs-paths | `content/workspace/analysis/analyze.py#L10-L19` | The script derives the workspace root from its own location and uses root-relative paths for data and outputs. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analysis/analyze.py#L5-L10`, `content/workspace/analysis/report.md#L51` | No environment manifest declares direct or transitive dependencies; prose package versions do not reconstruct the environment. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/analysis/report.md#L45-L51` | The only execution route depends on a host-specific absolute interpreter path; OS and other host requirements are not specified. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/analysis/report.md#L51`, `content/workspace/analysis/README.md#L1-L11` | Six software versions are listed, but there is no complete dependency installation route or documented system requirement list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/analysis/report.md#L51`, `content/workspace/analysis/analyze.py` | No environment specification is tracked or included with the analysis code. |
| must/014 | P.3 | unmet | judgement | `content/workspace/analysis/README.md`, `content/workspace/analysis/report.md#L43-L53` | No environment specification or dependency-update procedure is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/analysis/report.md#L45-L51`, `content/workspace/analysis/results/summary.tsv` | No immutable environment snapshot, lockfile or container digest identifies the software used for these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/analysis/report.md#L45-L53` | No worker-declared authorized route publishes the code, data and environment as a retrievable research object. |
| must/017 | D.1 | unmet | judgement | `content/workspace/analysis/report.md#L45-L51` | The report assumes a provided host environment but does not explain how a researcher obtains or reconstructs it. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `content/workspace/.git/HEAD`, `content/workspace/analysis/analyze.py` | Git and annex track supplied inputs, while the scientific code, report and generated products remain outside version control. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `content/workspace/analysis/report.md#L43-L53` | The delivery shows no recurring workflow test; CI absence alone cannot establish whether the route was tested regularly elsewhere. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input/`, `content/workspace/analysis/`, `content/workspace/analysis/report.md#L45-L53` | Inputs, analysis code and outputs occupy separate directories, but there is no distinct environment module. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/analysis/results/summary.tsv`, `content/workspace/analysis/report.md#L45-L53` | Shipped outputs do not establish a fresh-environment test, and no such test record is present in the delivery. |
| should/005 | E.1 | unmet | judgement | `content/workspace/analysis/report.md#L45-L51` | The documented command reuses a shared host Python installation; the workflow does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `content/workspace/analysis/report.md#L45-L53`, `content/workspace/analysis/README.md` | No declared environment can be repeatedly reconstituted or tested; no environment specification is supplied. |
| should/007 | D.2 | unmet | judgement | `content/workspace/analysis/`, `content/workspace/analysis/report.md#L45-L51` | The project does not archive a package environment, container image or required binaries with its results. |
| should/008 | D.2 | unmet | judgement | `content/workspace/analysis/README.md`, `content/workspace/analysis/report.md#L43-L53` | No environment specification or dependency-update procedure is declared. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: no restricted data or software component is identified in this delivered study. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | N/A: the external input dataset is copied into this single workspace; no independently maintained project module is linked. |
| may/002 | M.2 | partial | judgement | `content/workspace/analysis/README.md#L1-L11`, `content/workspace/input/upstream-methods.md` | The analysis README maps code, report, results and figures, but the overall relationship among inputs, code and outputs is not fully documented. |
| may/003 | M.2 | partial | judgement | `content/workspace/analysis/analyze.py#L10-L19`, `content/workspace/analysis/README.md#L1-L11` | Input, analysis and result directories have clear local roles, but updates still depend on the fixed workspace layout and no independent module interface is defined. |
| may/004 | M.2 | met | judgement | `content/workspace/analysis/report.md#L45-L53`, `content/workspace/analysis/analyze.py#L18-L22` | The analysis script composes the supplied input directory into results and figures through one documented command. |
| may/005 | M.2 | met | judgement | `content/workspace/analysis/README.md#L1-L11`, `content/workspace/analysis/report.md#L21-L35` | The analysis README and report direct readers to the entry script, principal results, quality checks and figures. |

## Flagged items

- **must/002 (`probe-overridden`)** — the probe only noted the absence of subdatasets; the retained in-root annex mapping makes the supplied inputs available within this complete capture.
- **must/004 (`probe-overridden`)** — the clean-tree probe found the untracked analysis; partial records the tracked supplied inputs but gives no worker credit for the untracked analysis package.
- **must/005 (`probe-overridden`)** — the annex probe detects supplied maps; the stop receipt does not establish worker annex work.
- **must/006 (`probe-overridden`)** — the run-record probe found no environment-linked record; the report documents only an absolute interpreter and package versions, not an exact environment.
- **must/007 (`probe-overridden`)** — the filename probe missed the untracked analysis documentation; it contains a command but no environment installation route, so the unmet verdict remains.
- **must/008 (`probe-overridden`)** — the probe missed the untracked script and documented command; the complete delivery supplies a clear entry point.
- **must/011 (`probe-overridden`)** — the command scan could not assess the host assumption; the documented route requires a host-specific absolute interpreter.
- **must/012 (`probe-overridden`)** — the command scan could not assess requirements; the report lists package versions but omits installation/system requirements.
- **must/014 and should/008 (`upstream-duplicate`)** — the checklist repeats the same dependency-update question.
- **must/015 (`probe-overridden`)** — the run-record probe found no named environment; the report does not supply an immutable environment pin.
- **should/006 (`probe-overridden`)** — the CI probe could not answer reconstitution; the complete delivery has no environment specification to reconstitute.
- **may/001 (`probe-overridden`)** — no independently maintained project module is linked; the external source dataset is bundled as input rather than a separate module.
- **must/002 (`probe-overridden`)** — the probe only noted the absence of subdatasets; the retained in-root annex mapping makes the supplied inputs available within this complete capture.
- **must/007 (`probe-overridden`)** — the filename probe missed the untracked analysis documentation; it contains a command but no environment installation route, so the unmet verdict remains.
- **must/008 (`probe-overridden`)** — the probe missed the untracked script and documented command; the complete delivery supplies a clear entry point.
- **must/014 and should/008 (`upstream-duplicate`)** — the checklist repeats the same dependency-update question.
- **may/001 (`probe-overridden`)** — no independently maintained project module is linked; the external source dataset is bundled as input rather than a separate module.

## Extra finding

The license probe found no project-level license or stated reuse terms. I checked the supplied source metadata and task/methods documents for a license statement and found none; the project does not establish permitted reuse of the code or bundled analysis products (`content/workspace/input/sources.json`, `study-task.md`, and `upstream-methods.md` in the canonical capture). This is an extra distributability finding, not a separate checklist item.

## Not checked

- **must/005:** the annex payloads exist, but the 54 maps were supplied and no worker action establishes annexing worker-generated large data. A worker-attributed record of large-data handling would settle this.
- **should/002:** the complete stop state has no recurring test record, but absence of CI alone does not establish whether testing happened regularly elsewhere. A scheduled or repeated test record would settle this.
- **should/004:** shipped results do not establish a fresh-environment run. A fresh-copy execution record with a declared environment would settle this.

## Goals and kind

The stated goal is a group-stage analysis of the 54 supplied equal-indifference gain-effect maps, testing a positive gain effect in vmPFC with whole-brain correction (`content/workspace/input/study-task.md`). The object is a **study**: its product is a scientific conclusion supported by code, results and figures. The assessment emphasizes input boundary, result provenance, portability and sharing. The goal and kind are assumptions from the supplied task and were not separately confirmed by a human.

## Records and provenance

- [Response JSON](2026-10-16-response.json)
- [Probe results](2026-10-16-probes.json)
- [Checklist URL](2026-10-16-url.txt)
- [Access record](access-record.json)
- [Replay record](replay-record.json)
- [Scientific judgment record](scientific-judgment.json)
- All attempted assessor commands and captured stdout/stderr are retained under `logs/`; generated assessment artifacts are in this directory.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study at commit `767f76ed3d12c3a7ff9fb23989358c768b301bc5`, 2026-10-16, Codex API session (model identity not exposed). Probe output: `2026-10-16-probes.json`.

**Reference limits.** `judge-target.json` declares no reference limits. I inspected the retained in-root annex mapping and checked only relative links that resolve within the operational workspace. The absolute interpreter path and `core.hooksPath` were treated as captured text and not followed; I did not run Git through an external `.git` pointer.
