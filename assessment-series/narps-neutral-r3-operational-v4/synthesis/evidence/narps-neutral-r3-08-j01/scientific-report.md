# Independent assessment — NARPS potential gains and vmPFC

## Verdicts

**MUST:** 7 met / 2 partial / 8 unmet / 0 not-checked / 0 not-applicable (17 items).  
**SHOULD:** 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 items).  
**MAY:** 0 met / 2 partial / 2 unmet / 0 not-checked / 1 not-applicable (5 items).

These are checklist item counts, not an overall score. All original-evidence paths below are relative to `content/workspace/` in canonical capture SHA-256 `408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce`. Artifact SHA-256 values identify files in that capture.

## What to improve first

1. Commit the analysis, report, figures and results before worker stop. They were all untracked at the recorded stop, so the captured HEAD does not version the reported answer (`must/004`).
2. Add a worker-owned, versioned environment/dependency specification and keep it with the study. The script imports multiple external Python packages; the report names a supplied environment but does not preserve a lock or setup route (`must/003`, `/010`, `/013`, `/015`–`/017`; `should/006`–`/008`).
3. Add installation instructions to the report’s reproduction command. The entry point is clear, but readers are told to use a prepared environment without instructions to obtain or recreate it (`must/007`, `/012`, `/017`).
4. Publish a recipient-accessible route for the complete study. The checked URLs cover input sources only; the captured worker Git configuration had no remote (`must/016`; see [access record](2026-10-16-access-record.json)).
5. Document how the input, code and results relate and which parts can be updated or recombined independently (`should/003`, `may/002`–`/005`).

## What is already good

- The scientific files, code, report and results are organized beneath one study root. The 54 large participant maps resolve through relative Git-annex links, and `input/sources.json` records source URLs and checksums. Examples: `input/sources.json` (SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`) and `input/data/sub-001_hypo1_cope.nii.gz` (captured link).
- The group analysis checks all 54 inputs, image geometry and finite values, uses a common nonzero-coverage mask, and applies a one-sided participant sign-flip max-*t* correction over the tested brain. The report distinguishes normalized gain-modulator effects from currency-unit effects. See `analysis/analysis.py` (SHA-256 `602d670ee718391513024ca6a42e461a16f2026270523e2202486598f856509b`), `input/upstream-methods.md` (`508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`), and `report.md` (`42a412c5c15ed62626eee4149a2fb9fb35c8b1182982c9160f7dc2005dc85af8`). The task-supplied NARPS instructions require a binary decision based on whole-brain-corrected analysis ([original instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).
- The report, tables, maps and figures form an inspectable result package. A single fresh-copy replay using the documented script recreated all ten declared outputs byte-for-byte (`2026-10-16-fresh-rerun.json`). This is assessor-run repeatability on the same host and shared environment, not worker practice or independent-host reproducibility.

## Scientific assessment

**Scientific adequacy is supported for the report’s scoped conclusion because all 54 supplied effects were checked, whole-brain family-wise error was controlled, the vmPFC estimate was not positive, and the report avoids treating a nonsignificant result as proof of no effect.**

The worker’s reported hypothesis outcome is:

> “In the 54-person equal-indifference group, the supplied gain-effect estimates do **not** support a greater vmPFC response with increasing potential gain.”

The inference is appropriate for the fixed participant effects: they are independent participant estimates, not standardized statistics; all maps are stated to be in MNI152NLin2009cAsym space; and the report describes 9,999 sign flips with the maximum positive *t* over 198,029 voxels. The one-sided max-*t* procedure is a defensible whole-brain family-wise correction under its stated sign-exchangeability assumption. The 10-mm vmPFC sphere at [0, 40, -8] is anatomically plausible and the corrected map, rather than its unadjusted ROI *p*, gates support. The report’s claim that the sphere was selected a priori is not independently documented, so that aspect remains a limitation.

The shipped result has a negative vmPFC summary (mean −0.0057, *t*(53) = −0.43, one-sided *p* = .665; 95% CI [−0.0326, 0.0211]) and no sphere voxel surviving whole-brain correction. The three corrected occipital foci are outside vmPFC. This is evidence that these supplied maps do not support the predicted positive group response under the chosen model. It is not evidence of equivalence or of a true zero effect. Because participant variance maps are absent, inference is unweighted; the fixed upstream model also prevents a per-currency-unit interpretation and cannot separate gain from correlated task features beyond AO86’s specification. Supporting numeric output: `results/results.json` (SHA-256 `3b9bd54dd69f99f6a761a90d0edc4f1388cf82d186d26d1372ae82d2400993ed`); participant QC/ROI table: `results/participant_qc_and_roi.tsv` (`4ac6e2219b8c4df16c0db35f020c0eed3c98b5f17ffdcac5d09a3db871743aa2`); corrected foci: `results/whole_brain_foci.tsv` (`825ddefd9480077b635537ce639b2b9b4bc47b87d619c0faeacdd1ed6ea9e0d0`).

`scientific-judgment.json` records adequacy and the hypothesis outcome separately, quoting this report verbatim. “Supported” evaluates the report’s scoped claim about evidence in these supplied maps; it does not endorse a claim that the positive hypothesis was confirmed.

## Worker stop, provenance and access

The worker-stop receipt is complete with no recorded capture errors or omissions (receipt SHA-256 `1f05810c9fb556059c57c0cbbf9d56b5b31f26292eb05d5c8472ff3d1912c136`). It identifies original captured HEAD `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`. The captured Git status shows `analysis/`, `figures/`, `results/` and `report.md` untracked; `.codex/` and `.entire/` are ignored. Thus scientific evidence is assessable from the complete stop workspace, while code, narrative and generated outputs were not recorded in the worker’s Git history. Git-annex content for the inputs was present inside the captured workspace.

The ignored `.entire/metadata/01a14592-da4d-7893-ad81-7a3e61e15dcc/full.jsonl` (SHA-256 `9a63716ecfc3d8f4a2b3bc9f5b011d89bd9f7f8e6ec123244075277235534204`) records successful analysis commands using the prepared interpreter; the associated prompt (SHA-256 `28c57a4ec173893af7ccffbf17c99d867fd1dfecfc32f5e1ab034c3f970ef7bc`) names its package versions. I counted this as worker-session provenance linking action to environment, but the interpreter/environment itself was supplied as a common resource, not captured or published by the worker. The exact command record is therefore useful but does not satisfy environment packaging, distribution or reproducibility items by itself.

That same retained session record identifies Codex/AI assistance. This exposure is recorded for transparency and was not used as scientific or checklist grading evidence.

For access, the intended recipient is a researcher using the authorized routes declared in `input/sources.json`; anonymous access is not required. HEAD checks returned 200 for one representative NeuroVault image and the pinned raw GitHub cohort and methods sources. No payloads were downloaded. This tests only those endpoints/hosts, not all 54 input URLs or another network. Those routes cover upstream inputs, not the worker’s report, code, figures, results or environment. No worker remote/publication route for the complete study was identified; coordinator delivery to the assessor does not establish worker publication. See `2026-10-16-access-record.json` and the retained command outputs in `logs/access-*.stdout`/`.stderr`.

## Replay and integrity scope

Before replay, `replay-plan.md` records the exact command, supplied prerequisites, ten generated outputs and comparison rule. The frozen helper made a new copy of the complete canonical delivery, removed only those selected outputs in that copy, and ran the worker’s documented entry point once (28.6 seconds, exit 0). All ten outputs were byte-identical; no upstream retrieval occurred. This tests same-host reproducibility using the supplied shared environment. It does not establish a fresh environment reconstruction or independent-host execution. Captured stdout/stderr and the frozen replay record are retained under `replay/`, `logs/replay.*`, and `2026-10-16-fresh-rerun.json`.

The canonical and operational manifest files have the same SHA-256 (`408548bc…f6b58ce`). A supplemental integrity comparison found no missing paths or unexpected workspace changes. It observed regular-file changes/additions only at `.git/annex/keysdb/db`, `db-shm` and `db-wal`, classified separately as operational metadata; this does not establish logical database equivalence. An initial supplemental scan was invalid because it read the manifest’s symlink field incorrectly and included declared external artifacts in the workspace comparison. That failed output is retained as `integrity-check-initial.json`; the corrected comparison and its command output are `integrity-check.json` and `logs/integrity-check.stdout`. No scientific measure relied on the invalid scan. The launcher’s canonical-capture verification remains the authority for capture identity.

## Per-item checklist

The probe sweep is retained as `2026-10-16-probes.json`; it covers 13/17 MUST items. Direct reading was used for unsupported and incomplete checks. Every evidence URI below names the canonical capture digest and capture-relative path.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The complete study files are under one workspace root. |
| must/002 | S.1 | met | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/sources.json`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | Participant maps resolve through relative links to annex content inside the workspace. |
| must/003 | S.1 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | Python dependencies are named in the report but no delivered environment specification includes them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/results/results.json` | The worker stop left the report, analysis, figures and results uncommitted. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/sources.json` | The 54 large maps are tracked through Git annex pointers and retained annex objects. |
| must/006 | T.1,T.3,T.5 | met | probe:run-env-linked+judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/.entire/metadata/01a14592-da4d-7893-ad81-7a3e61e15dcc/full.jsonl`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/.entire/metadata/01a14592-da4d-7893-ad81-7a3e61e15dcc/prompt.txt` | Worker session records link successful analysis runs to the supplied interpreter and its package versions. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The report gives a run command and package list, but no installation instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | The report points to analysis/analysis.py as a clear reproduction entry point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | The analysis derives paths from its own location and uses relative input/output paths. |
| must/010 | P.1 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | No delivered dependency specification captures the packages imported by the analysis. |
| must/011 | P.1 | met | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The workflow has no identified OS, native-library, scheduler, mount or hardware assumptions. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The report lists Python and package names, but omits most versions and installation details. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | No environment specification is present in the worker stop delivery or captured Git state. |
| must/014 | P.3 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | No dependency update process is documented; the worker delivery has no environment specification. |
| must/015 | D.1 | unmet | probe:run-env-linked | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The worker delivery does not preserve a pinned environment specification for exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | No worker-authored environment specification is published or retrievable with the study. |
| must/017 | D.1 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The report says to use a prepared environment but does not explain how a reader can obtain it. |
| should/001 | T.2 | met | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | Git tracks the study and Git annex stores the large participant maps within the same repository. |
| should/002 | A.2 | not-checked | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | No worker-maintained recurring test schedule or equivalent record is present; such records would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/study-task.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/results/results.json` | Input, code and derived outputs have separate folders, but no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/.entire/metadata/01a14592-da4d-7893-ad81-7a3e61e15dcc/full.jsonl` | The worker ran the analysis in the supplied shared environment; no worker-run fresh-environment test is recorded. |
| should/005 | E.1 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | The documented entry point uses a persistent prepared interpreter and creates no disposable environment. |
| should/006 | D.2 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | No worker-delivered environment specification or reconstitution test exists to repeatably check. |
| should/007 | D.2 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | No environment image, lockfile or other environment artifact is archived in the worker delivery. |
| should/008 | D.2 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | No dependency update process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/sources.json` | N/A: all supplied maps and metadata are publicly sourced; no restricted component is identified. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | N/A: there are no independently maintained project modules; the participant maps are annexed inside this study. |
| may/002 | M.2 | partial | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md`, `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/input/study-task.md` | The report names the analysis entry point and output folders but does not document independent module relationships. |
| may/003 | M.2 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/analysis/analysis.py` | No independently updateable module boundaries or interfaces are defined. |
| may/004 | M.2 | unmet | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | No module composition mechanism is provided; the study runs as one script. |
| may/005 | M.2 | partial | judgement | `capture:408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce:content/workspace/report.md` | The report identifies the script and output directories, but offers no broader navigation guide. |

## Flagged items

- **must/006 (`probe-overridden`):** the run-environment probe missed the worker’s `.entire` session format. The retained worker log and prompt link the successful command to the supplied interpreter and versions; the environment itself remains a supplied resource.
- **must/007 (`probe-overridden`):** the tracked-path probe missed untracked `report.md`, which gives a run command but lacks installation instructions; partial is the better fit.
- **must/008 (`probe-overridden`):** the tracked-path probe missed the untracked but clear `analysis/analysis.py` entry point documented by the report.
- **must/009 (`mapping-questioned`):** the probe scans tracked text paths; direct inspection of the complete untracked script confirmed relative project paths.
- **should/003 (`mapping-questioned`):** the probe’s tracked-path scan missed untracked code/results directories. The complete stop state separates inputs, code and outputs, but has no environment module.

## Not checked

- **should/002:** the stop workspace does not establish recurring testing. A worker-maintained test schedule or repeated test records would settle this.
- **should/004:** worker runs used the supplied shared environment; no worker-run fresh environment is recorded. An isolated worker execution record would settle this. The assessor replay does not count as worker practice.

## Goals and kind

The task brief `input/study-task.md` (SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`) describes a group-level scientific study answering whether potential gain increases vmPFC activity in the equal-indifference group. I treat the object as a **study**: it contains fixed inputs, analysis, results and a scientific report. No human guidance beyond the task brief was attached, so this kind is an explicit assessment assumption.

## Checklist link and stamp

[Open the completed checklist in the STAMPED app](2026-10-16-url.txt). The machine-readable item responses are in [2026-10-16-response.json](2026-10-16-response.json); the scientific record is [scientific-judgment.json](scientific-judgment.json); access and replay details are [2026-10-16-access-record.json](2026-10-16-access-record.json) and [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad`), on the canonical capture SHA-256 `408548bc65714ca93fe1bdde19db4311e47c4891839f576adb24f8c83f6b58ce`, original captured HEAD `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`, 2026-10-16, Codex API / GPT-6 (exact submodel not exposed). Probe output: `2026-10-16-probes.json`.
