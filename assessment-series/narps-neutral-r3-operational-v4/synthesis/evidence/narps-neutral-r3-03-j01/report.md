# Independent assessment: NARPS potential-gain group analysis

## Verdicts

**MUST:** 5 met / 1 partial / 11 unmet / 0 not-checked. **SHOULD:** 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable. **MAY:** 1 met / 3 unmet / 1 not-applicable. No overall score is assigned.

The original complete delivery capture is `accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd` (`manifest.json`); its captured HEAD is `82443e43a1171f47c085c5e0fadc9e8132a12053`. The worker-stop receipt (`worker-end-state.json`, SHA-256 `f0e216cddf471b52448636819a8483a4c1f5103967c0f3900711b587ad6cef91`) records a complete stop with no omissions. `judge-target.json` records the same canonical and operational capture digest. Findings below cite that original capture by digest and capture-relative path. Operational-copy observations are identified separately; the coordinator's preservation and this assessment's outputs do not count as worker actions.

## What to improve first

1. **Commit the analysis, report, figures, and results into the worker's versioned state** → the scientific product is not represented by the captured Git commit, which holds only part of the delivery → `must/004`.
2. **Add a worker-supplied, pinned environment declaration and an installation route** → the current command depends on an external host-specific Python installation, so another researcher cannot reconstruct the analysis environment → `must/003`, `must/007`, `must/010–017`, `should/005–008`.
3. **Record each run with its code/input identity and exact environment** → readers can connect the shipped maps, tables, and figures to the action that produced them → `must/006`, `should/002`, `should/004`, `should/006`.
4. **Declare an authorized retrieval route for the complete object** → researchers need the analysis, all 54 input maps and metadata, and generated results and figures → `must/016–017`.

## What the project already does well

- The study question, fixed upstream assumptions, data source metadata, and all 54 participant maps are inside the capture. Each map is a relative symlink into a retained Git-annex payload; the analysis resolves paths from its own location (`content/workspace/input/data`, `input/sources.json`, `analysis/group_analysis.py`).
- The analysis preserves all 54 equal-indifference participants, checks IDs, input checksums, finiteness, image grids, and affines, and reports those checks in `results/input_qc.tsv` (`analysis/group_analysis.py`, `results/input_qc.tsv`, `input/participants.tsv`).
- The report separates whole-brain inference from a descriptive, independently defined vmPFC sphere and explains what a non-significant result does and does not mean (`report.md`, `results/summary.json`).

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion of no corrected positive whole-brain finding is supported by a defensible analysis of the supplied group-stage maps. The analysis treats each participant's unthresholded cope as an independent observation, checks participant coverage and image geometry, uses the intersection of nonzero map support to avoid treating outside-brain zero padding as measured effects, and applies a one-sided sign-flip max-T correction over that common mask. The report gives the permutation count, seed, degrees of freedom, peak and corrected p value, and number of corrected voxels. Its inferential assumptions (independent participants and a symmetric one-sample null) are stated in code/report and are reasonable for this analysis.

The anatomical check is not used to select a peak: a 10-mm MNI sphere at [0, 40, −10] is presented as a coordinate-based descriptive summary. Its mean (−0.0061 cope), 95% t interval [−0.0342, 0.0221], and uncorrected one-sided p value are clearly labeled as secondary and non-confirmatory. The figures show the mean cope and group t statistic and state that no voxel passes whole-brain correction (`figures/group_maps.png`, `figures/vmPFC_participants.png`). The result therefore supports the *absence of sufficient evidence for the positive hypothesis under this model*; it does not establish a true zero effect or rule out smaller effects.

Important scope limits are acknowledged: cope values come from a mean-centered and variance-normalized upstream gain modulator, so they are not BOLD change per currency unit; gain was modeled separately from loss; participant variance maps are absent, so inverse-variance weighting is not available; and preprocessing/first-level models are fixed inputs. These limits constrain interpretation but do not invalidate the stated group-level conclusion. The common-support mask and sign-flip test are appropriate conditional choices; the report does not claim that this analysis is the only defensible method.

**Scientific adequacy: supported —** the delivered max-T whole-brain test, coverage handling, and qualified interpretation support the report's conclusion that the supplied data do not provide sufficient evidence for a positive response. This is an assessment of the reasoning and evidence, separate from STAMPED item attainment and replay availability.

**Reported hypothesis outcome (verbatim):** “In the 54-person equal-indifference group, the supplied gain-modulator estimates did not support a positive group response in vmPFC.” This remains the reported outcome; it is not inferred from the adequacy label.

Key scientific artifacts, cited against capture `accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd`: `content/workspace/report.md`; `content/workspace/analysis/group_analysis.py`; `content/workspace/results/summary.json`; `content/workspace/results/input_qc.tsv`; `content/workspace/input/upstream-methods.md`; and `content/workspace/figures/group_maps.png`.

## Worker state, tracking, and attribution

The worker-stop receipt records HEAD `82443e43a1171f47c085c5e0fadc9e8132a12053`. It attributes the task brief, cohort metadata, and 54 participant maps to supplied inputs; the untracked analysis, report, figures, and results are worker-created artifacts in the stopped workspace. The pinned assessor/runtime and its environment are coordinator-supplied. Later coordinator retention is not counted as worker versioning, environment capture, or publication. A final comparison of all 1,086 workspace entries against the initial operational manifest found no missing paths, extra paths, or non-metadata mismatches. The regular file `.git/annex/keysdb/db` changed SHA-256 from `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca` to `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`; this is within the explicit operational-metadata exception, is not worker evidence, and does not establish logical database equivalence. See [integrity-check.json](integrity-check.json). Inspection of the operational copy's Git status showed `analysis/`, `figures/`, `report.md`, and `results/` untracked, matching the captured index and complete delivery; these outputs are present and were assessed scientifically, but the Git commit is not the complete scientific product. The main analysis, report, result files, and figures therefore do not earn tracked-state credit at worker stop. Git-annex does carry all 54 input maps in the capture. The local Git configuration has no remote and includes a worker-host absolute hooks path; the path was recorded but not followed.

The report's invocation points to `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python`, outside the captured object. Package versions in `results/summary.json` are not an environment lock. No environment specification, run record linking outputs to an exact environment, system-requirement list, environment update process, or worker-facing publication route was found in the complete delivery. The default environment and runtime used to execute the frozen assessor were coordinator-supplied and are not credited to the worker. Later coordinator retention/delivery is likewise not evidence of worker publication.

The capture contains `.entire` prompt/transcript artifacts, which expose that an assistance session was recorded. I did not inspect their content or use it as grading evidence. They do not change the scientific assessment.

## Retrieval and replay

**Intended recipient:** a researcher using the worker's declared authorized route. **Route:** none is declared in the captured project; `.git/config` has no remote. **Required coverage:** the entrypoint, report, participant metadata/source records, all 54 input maps and annex payloads, and generated results/figures. These are present in the complete worker capture, but worker access for a recipient is not established. **Tested host scope:** local operational-copy host only; no remote retrieval was attempted because there is no worker-declared route. The coordinator's delivery of this copy to the assessor is not worker publication. Details are in [access-record.json](access-record.json).

**Replay: not checked; no attempt made.** The report documents the command and explicit generated output files, but its interpreter points outside the captured delivery and there is no worker-supplied environment declaration or setup procedure. Using the assessor's interpreter would substitute a new environment; following the external absolute path is outside scope. The replay record lists the exact documented command, protected inputs/source, explicit outputs, and a scientific comparison rule. The safe prerequisite could not be established, so the frozen helper was not run and no shipped output is represented as replay evidence. This is a scope limitation, not a scientific failure. See [replay-record.json](replay-record.json).

The recorded evidence supports 5 MUST, 1 SHOULD, and 1 MAY items as met; 1 MUST and 1 SHOULD are partial; 11 MUST and 4 SHOULD and 3 MAY are unmet; 1 SHOULD and 1 MAY are not-applicable; and 1 SHOULD is not-checked. The item-by-item answers and citations are in [response.json](response.json); the probe output is [probes.json](probes.json). The `derived-have-records` probe is not applicable because its tracked-path heuristic saw no derived files; the complete capture contains untracked results and figures, so that probe limitation was not treated as evidence that no results exist. `license-declared` is an extra finding: reuse terms are unstated. The probe also reports no oversized text blobs, and all participant-map checksums in the scientific QC output match the pinned source metadata.

## Item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | All delivered material is under the workspace root, including annex payloads reached by relative links. |
| must/002 | S.1 | met | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The 54 supplied maps are linked within the root to retained annex payloads; code uses root-relative paths. |
| must/003 | S.1 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/analysis/group_analysis.py` | The Python analysis imports external libraries, but the worker supplied no environment specification or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/analysis/group_analysis.py` | Git tracks supplied inputs and configuration, while the analysis, report, figures and results remained untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/input/data` | Git-annex tracks all 54 large participant maps; their annex payloads are retained inside the captured workspace. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/results/summary.json` | The report and outputs lack a worker run record linking the generated results to an exact environment specification. |
| must/007 | A.1 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The report gives a usage command but no install or environment setup instructions; its interpreter is a worker-host absolute path. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The report names analysis/group_analysis.py and gives a direct invocation that writes the listed results and figures. |
| must/009 | P.1 | met | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/analysis/group_analysis.py` | The analysis resolves inputs and outputs from its own file location; its internal file paths are relative to the workspace. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/analysis/group_analysis.py` | Required Python libraries are imported, but no dependency declaration is included in the worker delivery. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The documented command assumes an absolute worker-specific interpreter path and does not document the host or system requirements. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | No installation instructions or list of system requirements accompanies the documented command. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | No environment specification is present in the worker delivery or tracked history. |
| must/014 | P.3 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | No environment specification or documented update process is supplied. |
| must/015 | D.1 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/results/summary.json` | The report lists library versions, but no frozen environment manifest or container digest is supplied. |
| must/016 | D.1 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/.git/config` | No worker-declared authorized route publishes an environment specification or the complete analysis object. |
| must/017 | D.1 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The report does not explain how to obtain or recreate the environment; it points to a host-specific interpreter. |
| should/001 | T.2 | met | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/.git/config` | One Git repository and its git-annex extension cover the supplied inputs and workspace history. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | No CI is present; the captured assistance transcript was excluded from grading. A separate worker-attributed record of recurring workflow tests would settle this. |
| should/003 | M.1 | partial | probe:modules-separated | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/input` | Inputs are separated under input/, but code, derived results and environment are not organized as distinct modules. |
| should/004 | E.1 | not-checked | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | No worker-attributed record establishes a fresh-container, clean-VM or batch-job run; such a record would settle this. |
| should/005 | E.1 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The documented workflow invokes a pre-existing interpreter and does not create a disposable environment per run. |
| should/006 | D.2 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | No exact environment specification is provided to reconstitute and test against the results. |
| should/007 | D.2 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | No environment lock, container image or executable environment artifact is archived with the worker delivery. |
| should/008 | D.2 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace` | No environment update process is documented or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the captured inputs and declared software contain no restricted data or software. |
| may/001 | M.2 | not-applicable | judgement | — | N/A: the project has no independently maintained external component; source maps are included through local annex payloads. |
| may/002 | M.2 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The report lists files but does not document module boundaries or how components relate and recombine. |
| may/003 | M.2 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/analysis/group_analysis.py` | No independently updateable module boundaries are defined; the analysis reads directly from the workspace input directory. |
| may/004 | M.2 | unmet | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/analysis/group_analysis.py` | No module-composition mechanism is documented; the single script reads local inputs and writes local outputs. |
| may/005 | M.2 | met | judgement | `capture:accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd#content/workspace/report.md` | The report identifies the entrypoint and enumerates the input, code, result and figure files for navigation. |

## Flagged items

- `must/004` (`mapping-questioned`, `probe-overridden`): the clean-tree probe measures whether the entire state is committed. Git is used, but the principal analysis, report, figures, and outputs are not tracked, so the verdict is partial.
- `must/008` (`probe-overridden`): the tracked-path probe missed the untracked but captured entrypoint. The report documents `analysis/group_analysis.py` and its invocation.
- `should/008` (`upstream-duplicate`): this repeats the environment-update-process question in `must/014` by design.

## Not checked

- `should/002`: no CI is present, and the captured assistance transcript was excluded from grading. A separate worker-attributed record of recurring workflow tests would settle this.
- `should/004`: no worker-attributed evidence says whether the pipeline was tested in a fresh container, clean VM, batch job, or cloud instance. A worker run record with its execution host/environment would settle it.
- Retrieval: no authorized worker route is declared, so access by an intended recipient could not be tested. A declared route and a successful check of the required artifact coverage would settle it.
- Replay: the documented absolute interpreter is outside the capture and no worker environment setup is supplied. A captured/retrievable environment declaration usable from a fresh complete copy would enable the one scoped replay.

## Goals and kind

Assumption, not confirmed with a separate human: this is a **study** whose goal is to answer the supplied NARPS group-analysis question from fixed participant gain-effect maps. The goal is stated by the retained task brief (`content/workspace/input/study-task.md`, SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`) and the worker's `report.md`. As a study, the analysis emphasizes complete inputs, traceable outputs, execution/environment provenance, and retrievability.

## Checklist link and assessor stamp

Checklist app: [open the completed checklist](2026-10-16-url.txt). Machine-readable judgments: [response.json](response.json). Probe outputs and captured stdout/stderr: [probes.json](probes.json), [commands/](commands/).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the original capture SHA-256 `accefbd1bec4eb42279cf17f789438d3936e1dc654d4801a311bad3b9c21a6dd`, commit `82443e43a1171f47c085c5e0fadc9e8132a12053`, 2026-10-16, Codex API / GPT-6 (deployed variant not exposed). The frozen external assessor check passed: source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: `probes.json`.
