# Independent assessment — NARPS potential gain and brain activity

**STAMPED verdicts:** MUST: 12 met / 1 partial / 4 unmet / 0 not-checked (17 total). SHOULD: 0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total). MAY: 2 met / 0 partial / 1 unmet / 0 not-checked / 2 not-applicable (5 total). There is no combined score.

**Scientific adequacy: qualified.** The analysis supports the reported conclusion of no corrected evidence for a positive vmPFC response in this sample and under the supplied first-level model. This is not evidence of zero effect or equivalence. The inference is qualified by the nonzero-intersection mask's unreported spatial extent and its inability to distinguish zero-coded missing coverage from true zero estimates.

**Reported hypothesis outcome:** no corrected evidence of a positive vmPFC response.

## Scope and provenance

I assessed the complete operational copy at worker stop, including uncommitted, untracked and ignored files, using the original delivery identified by canonical capture SHA-256 `970ccf15bdb9389aaff1a3a3df6ea2c3237e8f8ca05613b1cc1c6c8044eefec7` and original HEAD `a8b85a997ef6e15f8e5571876b2b58796b4060a4`. In this report, `content/workspace/...` paths are capture-relative paths into that canonical delivery; the response JSON records individual file hashes as well. The canonical and operational manifest identities match. All 1,219 manifest entries were checked: there were no non-metadata mismatches. Inspection changed `.git/annex/keysdb/db` and created its regular-file `db-shm` and `db-wal`; these are the only operational metadata differences. They are assessor-induced and not worker evidence; database logical equivalence was not established. See [operational integrity record](operational-integrity.json).

The worker stop receipt (SHA-256 `4b0b7a4923696755f21a4bf6d1fae26b43d80ee12f449602e034ef5f48e870e5`) records a complete, successful worker stop with the same HEAD. The report, analysis script, environment, figures and result tree are present in the complete delivery but untracked; `.codex/` and `.entire/` are ignored stop-state material. I attribute versioning, provenance, publication and access only to that worker stop state. Later coordinator preservation does not earn worker-practice credit. The captured `reference_limits` list external/absolute skill links under `content/external/0000`; I did not follow those links or any external Git pointer. There were no declared Git dependencies preventing the scoped replay. The `.entire/` and hook paths indicate session tooling, but I did not inspect session contents or use them as grading evidence; no specific assistance attribution was established.

## Scientific assessment

The question is the original NARPS Hypothesis 1: whether the supplied gain-modulator contrast estimates show a positive group effect in vmPFC for the equal-indifference group. The report correctly states that the upstream gain regressor was mean-centered and variance-normalized, so these maps do not estimate a response change per unit of currency. It also recognizes that gains and losses were modeled separately and that the supplied participant variance maps and executable upstream pipeline are absent (`content/workspace/input/upstream-methods.md`, capture SHA above).

The group analysis uses 54 independent participant maps, with unique ID agreement to the equal-indifference cohort table. It checks file hashes and bytes, common shape and affine, finite values, and exclusions; the reported QC finds all 54 valid and excludes none (`content/workspace/input/participants.tsv`, `content/workspace/input/sources.json`, `content/workspace/results/input_qc.tsv`, and `content/workspace/results/summary.json`). The one-sample t model is appropriate for unthresholded participant estimates when first-level variances are unavailable. The 9,999 participant-level sign flips and maximum positive t over the full analysis mask provide one-sided whole-brain FWE control, with the sign-symmetry assumption stated. The protocol and report correctly reject uncorrected p-values as support and use a 10-mm sphere at MNI [0, 40, −10] as a data-independent anatomical localization target (`content/workspace/analysis-protocol.md`; `content/workspace/report.md`).

The reported vmPFC mean is −0.0061 upstream contrast units, with a descriptive 95% t interval [−0.0342, 0.0221]; there is no whole-brain-FWE-significant voxel in the sphere. The whole-brain map has 24 positive FWE-significant voxels in posterior foci, outside vmPFC. The report keeps those results separate and states that the absence of a corrected vmPFC result is not evidence for a zero effect. The participant-level plot and corrected statistical map are informative; the map is titled and thresholded at the max-statistic threshold (`content/workspace/results/summary.json`, `content/workspace/figures/group_t_map.png`, `content/workspace/figures/vmPFC_participant_effects.png`).

I qualify adequacy because the analysis mask is the intersection of finite, nonzero values across all participant maps (198,029 voxels), but neither the report nor summary gives its spatial extent or separates zero-coded missing coverage from true zero estimates. This limits independent assessment of whole-brain coverage and what locations entered correction. The ROI itself contains 428 mask voxels, so the reported localized test is represented in the tested mask. The supplied inputs also do not permit independent checks of upstream motion or first-level variance. These limits narrow the claim to common supported voxels and the fixed upstream model; they do not reverse the conclusion that this analysis found no corrected positive vmPFC evidence.

## Replay

Before execution, [replay-plan.md](replay-plan.md) records the exact environment reconstruction, documented entrypoint, prerequisites, eight generated outputs, protections and comparison rule. The frozen runner made a new writable copy from the canonical capture, removed only those explicitly selected outputs, and ran the delivered Conda specification and analysis script once. All eight selected outputs were byte-identical to the shipped generated files after regeneration; the script returned 0 in 114.9 seconds. This establishes repeatability for those selected outputs on this host, not scientific validity or cross-host access. Full record: [replay.json](replay.json); preserved command output: [stdout](replay/replay.stdout) and [stderr](replay/replay.stderr). The worker's own same-host replay remains a separate stop-state artifact (`content/workspace/results/replay_comparison.json`).

## Access

The intended recipient is a researcher using the declared authorized route. No worker-declared route was present in the complete delivery, and no remote appeared in the captured Git configuration. Thus there was no route to test. Required coverage would include the full object, including annexed inputs and the results/code/environment records. The assessor's local canonical delivery and same-host replay do not demonstrate that the worker made those bytes accessible. Details: [access record](access-record.json).

## What to change first

- Track the analysis script, report, protocol, environment declaration and generated results in the worker's versioned project state → makes the submitted scientific work and provenance traceable → `must/004`, `must/013`, `should/001`.
- Add a Conda lockfile or equivalent exact build-level environment record, and use it in result provenance → lets another researcher reconstruct the analyzed environment more exactly → `must/015`, `should/006`, `should/007`.
- Publish a worker-authorized retrieval route covering the annex content and the complete project → lets intended researchers obtain the same object → `must/016`.
- Define and record the environment update process and a repeatable test schedule → keeps reproduction instructions current → `must/014`, `should/002`, `should/008`.
- Report mask extent and validate common nonzero coverage against a data-independent brain/coverage definition → makes the whole-brain correction domain inspectable → scientific limitation; no STAMPED item.

## What is already done well

- The protocol prespecifies the one-sample model, independent participant unit, max-statistic whole-brain correction, target sphere and interpretation limits (`content/workspace/analysis-protocol.md`).
- The report and code perform broad data integrity checks and preserve per-participant QC and source checksums (`content/workspace/run_analysis.py`, `content/workspace/results/input_qc.tsv`).
- The report shows individual vmPFC values and a corrected map, and avoids interpreting non-significance as proof of no effect (`content/workspace/report.md`, `content/workspace/figures/`).

## Per-item STAMPED checklist

The probe pass is retained unedited at [probes.json](probes.json). The table below is generated from the completed response.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/README.md`, `content/workspace/input/study-task.md` | The complete study delivery is rooted at one workspace, with inputs, analysis, results and environment specification inside it. |
| must/002 | S.1 | met | judgement | `content/workspace/run_analysis.py`, `content/workspace/input/participants.tsv` | The script reads the supplied participant maps and metadata through workspace-relative paths. |
| must/003 | S.1 | met | judgement | `content/workspace/environment.yml` | The environment specification declares all analysis libraries; external package installation is handled by that specification. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `content/workspace/.git/config`, `content/workspace/README.md`, `inspection/git-status.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-19-j01/attempt-01/worker-end-state.json` | The delivered analysis, report, environment and outputs were untracked at worker stop; Git did not track the complete research state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `content/workspace/input/sources.json`, `probes.json` | The 54 supplied participant maps are tracked as git-annex content; source inventory and probe confirm pointer tracking. |
| must/006 | T.1,T.3,T.5 | met | probe:run-env-linked+judgement | `content/workspace/results/provenance.json`, `content/workspace/results/summary.json`, `probes.json` | The result provenance records the environment.yml digest and runtime package versions alongside source hashes. |
| must/007 | A.1 | met | probe:entry-point+judgement | `content/workspace/README.md`, `probes.json` | README gives environment installation and usage instructions for the delivered analysis. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/run_analysis.py`, `content/workspace/README.md`, `probes.json` | run_analysis.py is a clear executable starting point and the README names it. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/run_analysis.py` | The analysis constructs paths relative to its own workspace root. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `content/workspace/environment.yml`, `content/workspace/README.md`, `probes.json` | The declared Python and scientific Python packages cover the analysis imports; Conda is named as the installer. |
| must/011 | P.1 | met | judgement | `content/workspace/README.md`, `content/workspace/results/provenance.json` | The observed runtime platform and exact Python/package versions are recorded; README documents Conda setup. No further host-specific prerequisite is evident in the delivered route. |
| must/012 | P.2 | met | judgement | `content/workspace/README.md`, `content/workspace/environment.yml` | README explains how to create and use the Conda environment, and environment.yml lists the packages. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `content/workspace/environment.yml`, `content/workspace/.git/config`, `inspection/git-status.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-19-j01/attempt-01/worker-end-state.json` | environment.yml and the analysis artifacts were not tracked in the worker Git state; only the input-side files were committed. |
| must/014 | P.3 | unmet | judgement | `content/workspace/README.md`, `content/workspace/environment.yml` | No environment update or regeneration process is documented in the README or environment specification. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/environment.yml`, `content/workspace/results/provenance.json` | Direct package versions are pinned and results link the spec, but no lockfile fixes transitive package builds or platform resolution. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/README.md`, `access-record.json` | No worker-declared authorized retrieval route or publication is identified; the local repository has no remote, and coordinator delivery is not worker access. |
| must/017 | D.1 | met | judgement | `content/workspace/README.md`, `content/workspace/environment.yml` | README explains where the environment specification is located and how to create and use it. |
| should/001 | T.2 | unmet | probe:modules-separated+judgement | `content/workspace/.git/config`, `content/workspace/run_analysis.py`, `inspection/git-status.stdout` | Git does not cover all components: analysis, environment, report and results are untracked at worker stop. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `content/workspace/results/pilot.log`, `content/workspace/results/replay_comparison.json`, `probes.json` | Pilot and full replay records show repeated manual runs, but there is no evidence that the workflow is tested regularly against its instructions. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/README.md`, `content/workspace/analysis-protocol.md` | Inputs, code, environment and derived outputs have identifiable directories, but they are not separated into independently maintained modules. |
| should/004 | E.1 | unmet | judgement | `content/workspace/results/replay_comparison.json`, `content/workspace/results/provenance.json` | The worker records a same-host replay; there is no clean container, batch, VM or cloud execution record. |
| should/005 | E.1 | unmet | judgement | `content/workspace/README.md`, `content/workspace/run_analysis.py` | The documented workflow uses a named Conda environment; the analysis does not create a disposable environment for each run. |
| should/006 | D.2 | unmet | judgement | `content/workspace/results/replay_comparison.json`, `content/workspace/results/provenance.json` | The worker replay reruns the script in the existing environment; no record shows reconstituting the declared environment and testing it repeatedly. |
| should/007 | D.2 | unmet | judgement | `content/workspace/environment.yml`, `content/workspace/README.md` | The delivery includes a package specification but no archived environment image or executable environment artifact. |
| should/008 | D.2 | unmet | judgement | `content/workspace/README.md`, `content/workspace/environment.yml` | No process for updating the environment specification is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the supplied public dataset and declared public packages provide no restricted component to isolate. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | — | N/A: no independently maintained project components are declared; input images and package dependencies are ordinary data/runtime dependencies. |
| may/002 | M.2 | met | judgement | `content/workspace/README.md` | README describes the input, script, environment, results and figures sufficiently to navigate the delivered workspace. |
| may/003 | M.2 | unmet | judgement | `content/workspace/README.md` | The directory layout separates data and outputs, but there are no modular boundaries that support independent updates. |
| may/004 | M.2 | not-applicable | judgement | — | N/A: the workspace defines no independently maintained modules that require a composition mechanism. |
| may/005 | M.2 | met | judgement | `content/workspace/README.md` | README identifies the main files and outputs and gives the analysis command. |

## Flagged items

- `must/006`: the probe did not recognize the delivered provenance record; `results/provenance.json` links the output to the environment declaration and runtime.
- `must/007` and `must/008`: the entry-point probe searched tracked files and missed the delivered, untracked README and script.
- `must/010`: the environment-spec probe measured tracking, while this item asks whether dependencies are declared; the specification covers imported libraries.
- `must/016`: the probe's tracking heuristic does not establish a worker access route; the route assessment is based on the complete workspace and captured Git configuration.
- `should/002`: the CI probe did not test the manual pilot and replay records; the evidence supports repeat runs, but not regular testing.
- `should/008`: repeats the environment-update process question from `must/014` by checklist design.

## Not checked

None. The access record is unmet because the complete worker state has no declared route, not because a declared route was unavailable to the assessor.

## Goals and kind

The worker's stated goal is the group-stage NARPS equal-indifference gain-effect analysis in `content/workspace/input/study-task.md` (capture SHA above). The object is a study/research project, so the assessment includes the input maps, cohort metadata, analysis, results and environment declaration. The coordinator-supplied task/rubric is not worker evidence.

## Checklist URL and assessment stamp

[Open the completed checklist](checklist-url.txt). Machine-readable verdicts and capture identity: [response.json](response.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the complete delivery at original HEAD `a8b85a997ef6e15f8e5571876b2b58796b4060a4`, captured 2026-10-16; Codex/GPT-6. Probe output: [probes.json](probes.json). The scientific judgment is [scientific-judgment.json](scientific-judgment.json).
