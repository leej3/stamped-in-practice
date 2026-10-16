# Independent assessment: NARPS Hypothesis 1

## Verdicts

MUST: 4 met / 3 partial / 10 unmet / 0 not-checked. SHOULD: 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable. MAY: 1 met / 1 partial / 2 unmet / 1 not-applicable. These are item judgments, not an overall score.

**Scientific adequacy: qualified.** The reported “no positive vmPFC response supported” conclusion is reasonably supported under the chosen whole-brain test and is carefully limited to lack of support, not proof of zero. The one-sample participant-level model, 9,999 sign-flip max-T correction, all 54 participants, map grid checks, and uncertainty summaries are inspectable in `analysis/run_analysis.py`, `results/summary.json`, and `report.md`. AAL3 is used as an explicit anatomical proxy, but it is resampled onto maps described as MNI152NLin2009cAsym without a documented transform between template spaces; this makes the precise vmPFC localization approximate. The ROI confidence interval also remains compatible with modest positive and negative effects. One ancillary volume field is wrong by 1,000×: 186,400 × 2 × 2 × 2.4 mm³ is about 1.79 L, while `common_support_volume_liters` reports about 1,789. This does not change the voxelwise test. See scientific reasoning and artifacts below.

**Reported hypothesis outcome:** “The supplied gain-effect estimates do **not** support a positive response in vmPFC.” This is not an inference from the adequacy label.

## What to address first

1. Track the worker’s analysis, report, figures, and results, then record each run’s exact command and environment with outputs. This links the scientific conclusion to its procedure and closes `must/004`, `must/006`.
2. Add a reproducible environment declaration and installation/run instructions, including the Nilearn dataset retrieval/cache requirement and system assumptions. This makes the analysis actionable and portable and closes `must/003`, `must/007`, `must/010`–`must/017` as applicable.
3. Make the atlas/template relationship explicit and transform or validate the anatomical ROI in the maps’ stated space; correct the volume unit conversion. This strengthens localization and QC.
4. Publish a declared, authorized retrieval route for the worker-state object and test access to code, data, and results together. Coordinator preservation alone does not establish worker publication (`must/016`).

## What is already strong

- The task is narrowly framed and the report names the complete 54-person cohort, no exclusions, the supplied contrast’s scaling limits, and absence of participant variance maps (`report.md`; `input/upstream-methods.md`).
- The code checks map/metadata matching, unique IDs, common shape and affine, finite values, and produces transparent participant, voxelwise, and figure artifacts (`analysis/run_analysis.py`; `results/summary.json`).
- Large supplied maps are annex-backed within the object, while the report and code use relative paths. The canonical manifest records the annex keys and retrieved-byte hashes.

## Evidence boundary and attribution

Assessment used the complete operational copy of canonical capture SHA-256 `51645420c0f50700227093660ac8e7859e8d228fc2325f59ebc2b32279f7584b`. Citations below identify capture-relative paths; for example `report.md` means that path in this exact capture. The worker-stop receipt reports the same capture and HEAD `a724b670072a95a253e752be8336783858df768a`, with no omissions or errors. At stop, `analysis/`, `figures/`, `report.md`, and `results/` were untracked; they are included in this assessment as delivered scientific evidence but do not earn worker tracking credit. `input/` and the annex payloads were supplied materials. Coordinator retention and this operational copy are not evidence of worker publication.

The operational Git working tree showed those four untracked output paths and no other tracked changes. No remote was configured. No external pointer was followed. Relative map links resolve through the captured `.git/annex/objects` mapping. `judge-target.json` lists no reference limits. The only worker-state Git commit is the captured input-supply commit; later coordinator preservation is not attributed to the worker.

**Assessor operation:** an initial GNU `find -printf` inventory command failed because this host does not support that option. The failure is preserved in `logs/initial-inventory-command.*`; a read-only Python inventory completed the check. This did not affect the target or leave any assessment measure unavailable. No frozen-runner malfunction occurred.

A supplied base commit contains Codex co-author metadata, and `.entire/` conversation artifacts are present. This records exposure to assistance-related identifiers only; those identifiers and logs were not used as grading evidence, and they do not establish who authored the analysis.

## Scientific assessment

The question concerns whether gain increases a positive fMRI response in vmPFC among the equal-indifference participants. The delivered report analyzes all 54 supplied participant gain-effect maps without exclusions. It treats the maps as participant contrast estimates, not t/z statistics; describes the mean-centered, variance-normalized gain regressor and separate gain/loss models; and correctly avoids interpreting coefficients per currency unit or causally. It notes that first-level variance maps and the upstream executable pipeline are unavailable (`input/upstream-methods.md`; `report.md`).

The group model is an unweighted one-sample test across independent participant maps. The report states the null symmetry assumption for participant-level sign flips. Its maximum positive t statistic over the whole common analysis mask is a defensible one-sided whole-brain family-wise correction for the stated positive hypothesis. It reports 9,999 draws, α=.05, critical t=5.37, 23 corrected voxels, and a peak at [−26, −102, −3.6] outside vmPFC. No corrected voxel overlaps its bilateral AAL3 medial orbital frontal ROI. The ROI mean is −0.0078 (SE .0132; 95% CI [−.0343, .0187]); the one-sided ROI p=.72 is correctly marked descriptive. The interval is not evidence of equivalence to zero.

The task’s anatomical inference is less secure than the statistical correction: task methods specify MNI152NLin2009cAsym maps, while the code resamples a fetched AAL3 atlas and MNI152 standard mask by grid interpolation only. The report does not document whether those source templates are already aligned or how template mismatch was checked. Thus the absence of overlap supports lack of corrected evidence under the stated ROI approximation, with localization uncertainty. The report’s discussion otherwise distinguishes the posterior peak from vmPFC and does not overclaim. The incorrect liters field in the summary is a QC/reporting error, not a basis for the group conclusion.

Overall, **qualified** means the delivered conclusion is supportable as a lack of corrected evidence for a vmPFC gain effect under this group analysis, conditional on AO86’s supplied model, while anatomical localization and modest effects remain uncertain. The result does not establish no effect, test gain against loss, or settle the hypothesis for other upstream models.

The cited NARPS instructions PDF timed out when opened during assessment (`logs/narps-pdf-fetch.json`). The supplied scientific guidance independently states the whole-brain correction requirement, so this did not leave that criterion unavailable.

## Access and retrieval

- **Intended recipient:** another researcher using the route declared by the worker.
- **Worker-declared route:** none found in the delivered report, source metadata, or Git remotes at worker stop. `input/sources.json` identifies upstream public NeuroVault/OpenNeuro sources for inputs, but it does not publish this worker’s analysis/results as a complete object.
- **Required coverage:** code, report, figures, results, metadata, and the 54 input maps with their annex payloads.
- **Tested host scope:** inspection of the local operational copy only. The in-object relative annex links resolved there; no worker-host retrieval route could be tested. Anonymous access was not required. Coordinator delivery to the assessor is not worker publication evidence.

## Replay

Replay was **not checked**. The captured report links `analysis/run_analysis.py` but supplies no explicit execution command or environment declaration. The script fetches the AAL3 atlas and MNI152 templates/mask via Nilearn, and the captured-delivery adapter performs no scientific-input prefetch. There is therefore no safe documented entrypoint/prerequisite set for a replay without inferring a command or initiating unrecorded resource retrieval. No replay copy or scientific replay attempt was created. The detailed replay record is `replay-record.json`.

## Checklist table

Every object path in this table refers to canonical capture SHA-256 `51645420c0f50700227093660ac8e7859e8d228fc2325f59ebc2b32279f7584b`; file hashes are recorded in `response.json`.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `report.md` | All delivered materials share the workspace root. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | All 54 inputs resolve through relative annex links within the captured Git boundary. |
| must/003 | S.1 | unmet | probe:env-spec-tracked+judgement | `analysis/run_analysis.py`, `report.md` | No environment declaration includes the imported scientific packages. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `analysis/run_analysis.py`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-11-j01/attempt-01/worker-end-state.json` | Git tracks supplied materials, but worker analysis, report, figures, and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | The supplied large participant maps are annex-backed in the captured object. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/run.log`, `report.md` | Derived results lack a record linking the action and outputs to an exact environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `report.md` | The report names artifacts but gives no installation or usage instructions. |
| must/008 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md`, `analysis/run_analysis.py` | A main analysis script is identified, but no exact invocation or reproducible setup is documented. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis/run_analysis.py` | The analysis script builds data and output paths relative to its own location. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/run_analysis.py`, `report.md` | Imports include multiple external packages, but no dependency specification is delivered. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `analysis/run_analysis.py`, `report.md` | The script fetches Nilearn atlas/template resources, requiring an undocumented network or cache. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md` | The report names Python and packages, but omits a complete system/dependency setup and installation route. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/targets/narps-neutral-r2-11-j01/canonical/manifest.json` | No version-controlled environment specification is present. |
| must/014 | P.3 | unmet | judgement | `report.md` | No environment-update process is declared or tracked. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/run.log` | No exact environment specification is recorded for replication. |
| must/016 | D.1 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-11-j01/attempt-01/worker-end-state.json`, `input/sources.json` | No worker-declared route publishes the complete study object; no Git remote was configured at stop. |
| must/017 | D.1 | unmet | probe:env-spec-tracked+judgement | `report.md` | There are no instructions for obtaining or using an environment specification. |
| should/001 | T.2 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `report.md and analysis/run_analysis.py` | Git and git-annex are used across text/code and large binary inputs. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `results/run.log` | The complete delivery contains no recurring workflow-test record or CI configuration. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/`, `analysis/, figures/, results/` | Inputs, analysis, figures, and results have separate directories; environment is not separated or specified. |
| should/004 | E.1 | not-checked | judgement | — | No fresh-environment run was attempted; a clean run with the documented setup would settle this. |
| should/005 | E.1 | not-checked | judgement | `report.md` | The worker environment lifecycle is not recorded; a run policy or environment record would settle this. |
| should/006 | D.2 | unmet | probe:ci-present+probe:run-env-linked+judgement | `report.md` | No exact environment specification or reconstitution test record is present. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `report.md` | No environment artifacts or pinned environment specification are archived with the object. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment-update process is declared or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivered public study contains no restricted data or software component. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/data/` | N/A: there are no independently maintained project modules; package dependencies are not modules. |
| may/002 | M.2 | unmet | judgement | `report.md` | The directory layout is not documented as a composable modular structure. |
| may/003 | M.2 | partial | judgement | `input/, analysis/, figures/, results/` | Inputs, code, and outputs are separated by directory, but independent update boundaries are not documented. |
| may/004 | M.2 | unmet | judgement | `analysis/run_analysis.py` | No mechanism composes independently maintained modules; the script reads paths in one root. |
| may/005 | M.2 | met | judgement | `report.md` | The report links users to the analysis code, figures, and numerical outputs. |

## Flagged items

- `must/006`: the tracked-path probe called results not applicable because it missed the delivered untracked `results/`; complete-delivery inspection shows derived outputs without a run-to-environment provenance link.
- `must/008`: the entry-point probe found no recognized tracked entrypoint; report and code identify a main analysis script, but omit an exact run command and environment, so this is partial.
- `must/011`: the command scan did not identify platform assumptions; code-level Nilearn data fetching introduces a network/cache prerequisite absent from documentation.
- `must/015`, `should/002`, `should/006`: filename/CI probes could not settle these items; full-delivery inspection confirms no environment specification or repeated reconstitution/test record, so absence is established.
- `must/014` and `should/008`: duplicate checklist wording; both reflect the absence of a declared environment update process.

## Not checked

- `should/004`: no fresh-environment replay was attempted; a successful run in a clean environment using the delivered route would settle this.
- `should/005`: the worker’s environment lifecycle is not recorded; a run record or environment policy would settle whether runs use disposable environments.
- Replay: a worker-documented command, complete supplied environment declaration, and explicit generated-output comparison plan would make one scoped attempt possible.

## Goals and kind

Assumption (not confirmed by a human): this is a **study** whose product is a group-level answer to the NARPS Hypothesis 1 question, with code and derived outputs. The goal follows `report.md` and `input/study-task.md`; all seven STAMPED principles apply, with emphasis on linking results to actions/environments and making the inputs retrievable.

## Records and provenance

- [Checklist response JSON](response.json)
- [Checklist app URL](checklist-url.txt)
- [Probe output](probes.json)
- [Access record](access-record.json)
- [Replay record](replay-record.json)
- [Scientific judgment record](scientific-judgment.json)
- [Command and output log](commands.log)

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on capture `manifest.json`, SHA-256 `51645420c0f50700227093660ac8e7859e8d228fc2325f59ebc2b32279f7584b`, original commit `a724b670072a95a253e752be8336783858df768a`, 2026-10-16, Codex / model identity not exposed by runtime. Probe output: `probes.json`.
