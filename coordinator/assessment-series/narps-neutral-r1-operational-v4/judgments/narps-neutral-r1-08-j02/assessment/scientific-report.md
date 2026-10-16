# Independent assessment — NARPS gain effects

**MUST:** 6 met / 1 partial / 10 unmet / 0 not-checked. **SHOULD:** 1 met / 1 partial / 6 unmet / 0 not-checked / 1 not-applicable. **MAY:** 4 met / 1 partial / 0 unmet / 0 not-checked.

## What to improve first

1. Add and pin a reproducible environment, list system prerequisites, and describe how to install it. `analysis.py` imports scientific packages and calls Nilearn's standard-mask loader, while the report only refers to a supplied environment. This would address must/003, must/010–015, and must/017.
2. Track the submitted analysis, report, figures and results in the worker's versioned state. They were delivered but uncommitted at stop, so the commit alone does not identify the complete research state. This would address must/004.
3. Publish a worker-declared retrieval route for the complete delivery and environment, with recipient access checked for all required artifacts. The worker stop state provides no route. This would address must/016.
4. Record the exact environment with the run and test reconstruction in a fresh environment. Session evidence shows execution in a shared external environment, but no environment pin or reconstruction test was delivered. This would address must/006 and should/004–007.
5. State a recurring test and an environment update process. The captured workspace documents neither. This would address should/002 and must/014 / should/008.

## What is already done well

- The delivered code and report make a scientific starting point and explain the outputs, although the code and report were uncommitted at worker stop (`content/workspace/analysis.py`, SHA-256 `e06520fcf4667336e63c864ad33f286e50ccea6b08409081532ab9daf3d905c3`; `content/workspace/REPORT.md`, SHA-256 `a621fde6376b7af8f5b3a120d631fb1bf16585dc1fce16ef3029d12901a0d769`).
- The 54 source maps are identified and retained through Git-annex pointers under `input/`; `sources.json` records their origins and byte checksums (`content/workspace/input/sources.json`, SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`).
- The scientific report discloses uncertainty and upstream limits, including that the maps are effect estimates, not standardized statistics, and that first-level variance maps are unavailable (`content/workspace/input/upstream-methods.md`, SHA-256 `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`; `content/workspace/REPORT.md`, SHA-256 `a621fde6376b7af8f5b3a120d631fb1bf16585dc1fce16ef3029d12901a0d769`).

## Scientific assessment

**Scientific adequacy: supported.** The delivered one-sided group test uses all 54 participant effects, checks map geometry and coverage, and applies whole-brain maximum-*t* permutation correction. It reports no corrected voxels in the stated vmPFC proxy and a proxy mean with a *t* interval spanning modest negative and positive effects. The conclusion is appropriately limited to lack of support at this inferential resolution; it does not claim a true zero effect. The report states the proxy center and size, the MNI grid, and the sign-flip symmetry/exchangeability assumption. The participant maps are unthresholded gain-effect parameter estimates from fixed upstream models; the report correctly avoids interpreting them as standardized statistics or effects per currency unit. Missing first-level variance maps, upstream model choices, ROI operationalization and sample sensitivity remain meaningful limitations. These do not invalidate the bounded conclusion.

**Scientific adequacy: supported — the whole-brain max-T FWE analysis found no corrected vmPFC proxy voxels, the proxy mean estimate is near zero with a CI spanning small effects in both directions, and the report limits interpretation to absence of support.**

Reported hypothesis outcome: “Thus, these maps do not support the predicted positive vmPFC response, despite evidence for positive effects elsewhere in the brain.”

Evidence: `content/workspace/REPORT.md` (SHA-256 `a621fde6376b7af8f5b3a120d631fb1bf16585dc1fce16ef3029d12901a0d769`); `content/workspace/analysis.py` (`e06520fcf4667336e63c864ad33f286e50ccea6b08409081532ab9daf3d905c3`); `content/workspace/results/summary.json` (`302e27d4392831093cbee1baadb0c8969f61f22a6b8b7432b3945b7c3e785c7c`); `content/workspace/results/participant_qc_and_roi.csv` (`f67d97492035770e74615341d0f5cce246fffd006282708d9db400134be1ee4d`). Each citation is within canonical capture SHA-256 `2afd81ca5fdfaa03e85f2d3e65b04aac9f4b3d90eb39f95c2497266e4cf3cdc7`.

## Per-item checklist

Each `content/workspace/...` evidence URI in this table is from canonical capture SHA-256 `2afd81ca5fdfaa03e85f2d3e65b04aac9f4b3d90eb39f95c2497266e4cf3cdc7`; per-file hashes are recorded in `response.json`.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/analysis.py` | Inputs, code, results and documentation sit under one captured workspace root. |
| must/002 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | All inputs are reachable inside the root through retained relative annex links. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analysis.py`, `content/workspace/REPORT.md` | Scientific software dependencies are imported but not declared or linked in the delivery. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `content/workspace/REPORT.md`, `content/workspace/analysis.py`, `content/workspace/.git/index` | Git versions the input pointers and setup, but the scientific report, code and results were uncommitted at stop. |
| must/005 | T.1,T.3,T.5 | met | judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/input/sources.json` | Git-annex carries the 54 large participant maps inside the captured repository. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/.entire/metadata/01a14362-b15b-7eb2-916e-7dbb9b4b8215/full.jsonl`, `content/workspace/results/summary.json` | Session evidence records execution, but the environment used for these outputs is neither specified nor linked to results. |
| must/007 | A.1 | met | probe:entry-point+judgement | `content/workspace/REPORT.md` | REPORT.md gives the entrypoint, working directory and usage instruction. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/analysis.py`, `content/workspace/REPORT.md` | analysis.py is a clear group-analysis starting point for producing the reported results. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/analysis.py` | The workflow derives input and output paths from its own location. |
| must/010 | P.1 | unmet | judgement | `content/workspace/analysis.py`, `content/workspace/REPORT.md` | The required Python packages and the atlas-data prerequisite are not declared for installation. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/REPORT.md`, `content/workspace/.git/config` | Host and service assumptions are not documented; the captured Git config also retains an absolute hooks path. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `content/workspace/REPORT.md`, `content/workspace/analysis.py` | No clear system requirements or complete dependency list is provided. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analysis.py`, `content/workspace/REPORT.md` | No environment specification is included in the delivered version control state. |
| must/014 | P.3 | unmet | judgement | `content/workspace/REPORT.md` | No process for updating environment specifications is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/REPORT.md`, `content/workspace/.entire/metadata/01a14362-b15b-7eb2-916e-7dbb9b4b8215/full.jsonl` | No pinned environment specification is delivered for exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/REPORT.md` | The worker stop state declares no route to retrieve this research object or its environment. |
| must/017 | D.1 | unmet | judgement | `content/workspace/REPORT.md` | The report does not explain how a recipient obtains or installs the unspecified environment. |
| should/001 | T.2 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | Git and Git-annex are used within one repository for text and large maps. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `content/workspace/.entire/metadata/01a14362-b15b-7eb2-916e-7dbb9b4b8215/full.jsonl` | The captured delivery and session show one analysis effort, with no recurring test process. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input/sources.json`, `content/workspace/analysis.py`, `content/workspace/REPORT.md` | Inputs, code and results have separate directories, but environment artifacts are absent and outputs are not independently versioned. |
| should/004 | E.1 | unmet | judgement | `content/workspace/.entire/metadata/01a14362-b15b-7eb2-916e-7dbb9b4b8215/full.jsonl` | The captured session ran in a shared existing environment, not a fresh isolated environment. |
| should/005 | E.1 | unmet | judgement | `content/workspace/.entire/metadata/01a14362-b15b-7eb2-916e-7dbb9b4b8215/full.jsonl` | Execution uses a long-lived shared environment rather than creating a disposable environment per run. |
| should/006 | D.2 | unmet | judgement | `content/workspace/REPORT.md`, `content/workspace/results/summary.json` | No exact environment specification or recurring reconstruction test is delivered. |
| should/007 | D.2 | unmet | judgement | `content/workspace/REPORT.md`, `content/workspace/analysis.py` | No environment artifacts or package cache are archived with the project. |
| should/008 | D.2 | unmet | judgement | `content/workspace/REPORT.md` | No environment update process is stated; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: the captured inputs and declared source data are public; no restricted component is present. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The independently maintained AO86 maps are identified by source URLs and separated under input/. |
| may/002 | M.2 | met | judgement | `content/workspace/REPORT.md` | The report documents the input, workflow and result locations and how they relate. |
| may/003 | M.2 | partial | judgement | `content/workspace/analysis.py`, `content/workspace/REPORT.md` | Inputs are distinct, but code, environment and generated outputs do not have independent versioned boundaries. |
| may/004 | M.2 | met | judgement | `content/workspace/analysis.py` | analysis.py composes the input maps and metadata into the group results and figures. |
| may/005 | M.2 | met | judgement | `content/workspace/REPORT.md` | The report identifies the main workflow and the supplied and generated artifacts. |

## Flagged items

- **must/004:** the path-based probe found uncommitted artifacts; the judgment records partial attainment because Git is used for some delivered material, while the research report, workflow and results remain outside the worker commit.
- **must/007 and must/008:** the entrypoint probe only recognized conventional README/Makefile or tracked-code forms. The complete stopped workspace includes `REPORT.md` usage instructions and the untracked `analysis.py` entrypoint.
- **must/006:** the run-environment probe found no linked environment. The session transcript does show execution, but only through an external shared environment path; no specification or pin is delivered.
- **must/011 and must/012:** command scanning could not settle host assumptions or system requirements. Reading the report and code shows the environment and dependencies are not documented.
- **must/014 and should/008:** the pinned checklist duplicates the environment-update question; both carry `upstream-duplicate`. No update process is documented.
- **should/002:** the CI probe could not settle recurring workflow tests. The complete worker session evidence shows one research session and no recurring test record.
- **may/001:** the submodule probe did not recognize source-level component links. `sources.json` identifies the external AO86 map collection and per-map retrieval URLs; local map pointers have a clear `input/` boundary.

## Not checked

No STAMPED checklist item remains not-checked. The scientific replay is separately not checked; see the replay record and report below.

## Goals, kind and scope

The stated goal is group-level inference for the positive potential-gain effect in the equal-indifference group, using the supplied 54 AO86 participant maps and fixed upstream methods. This is a **study**: it combines research code, participant-level inputs, group results and interpretation. This goal and kind come from the retained task brief, not a worker-edited replacement.

The assessed original complete delivery was captured 2026-10-16 at `2afd81ca5fdfaa03e85f2d3e65b04aac9f4b3d90eb39f95c2497266e4cf3cdc7`; its captured HEAD is `eece8595d255a766517e32ff10b2e6574d3c4e6a`. The worker stop receipt is SHA-256 `77c8a710004eeb6bc42610e3a53bb6905ac963c8746604860256cf30491dde98`. The canonical and initial operational manifests identify the same capture. The workspace includes code, report, results and figures outside HEAD; the stop inventory records them as delivered, and the Git status probe confirms they were uncommitted. The user-supplied launcher verifies the target before and after assessment. Inspection-induced annex `keysdb` metadata is operational metadata, not worker evidence; no claim of logical database equivalence is made.

Worker-state attribution is limited to the original stop: the available HEAD, index, configuration, Git-annex state, untracked and ignored workspace, and captured session evidence. The session records analysis invocations using a shared Python environment outside the delivery, but the delivery contains no corresponding environment specification. The captured Git config contains a host-specific absolute hooks path. No worker-declared publication or retrieval route appears in the report or Git config. Coordinator preservation or delivery to this assessor is not evidence that the worker had published the delivery. The worker session identifiers disclose Codex assistance; that exposure is recorded here and was not used as grading evidence. No treatment assignment was inferred or reported.

### Access record

The intended recipient is a researcher using the worker's declared authorized route. No such route was found in the stopped workspace, so there was no worker route to test. Required coverage would be the complete research delivery: code, report, all 54 maps and metadata, scientific outputs, and the environment needed to reproduce them. No recipient access or host scope beyond the local inspection host was tested. The coordinator's later delivery to this assessment does not establish worker access.

### Replay record

Replay status is **not-checked** (zero attempts). The documented entrypoint is `python analysis.py` from the workspace root. The workflow's identifiable generated scientific outputs are `results/summary.json`, `results/participant_qc_and_roi.csv`, `results/group_mean_effect.nii.gz`, `results/t_statistic.nii.gz`, `results/p_uncorrected_one_sided.nii.gz` and `results/p_fwe_maxT.nii.gz`. The worker did not supply a dependency declaration or reconstructable environment; the session used an external shared environment and the script loads a Nilearn standard mask. Therefore the documented prerequisite cannot be established from supplied instructions without adding missing dependencies or retrieving data. No output was removed and the inspection copy was not used for execution. A replay record is at [replay-record.json](replay-record.json).

## Assessment files

- [Response JSON](response.json)
- [Probe output](probes.json)
- [Checklist link](checklist-url.txt)
- [Access record](access-record.json)
- [Replay record](replay-record.json)
- [Scientific judgment record](scientific-judgment.json)

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the original delivery at commit `eece8595d255a766517e32ff10b2e6574d3c4e6a`, 2026-10-16, Codex/GPT-6. Probe output: `probes.json`.
