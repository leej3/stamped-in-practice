# Independent assessment — NARPS Hypothesis 1

**MUST:** 5 met / 2 partial / 10 unmet / 0 not-checked. **SHOULD:** 1 met / 1 partial / 6 unmet / 0 not-checked / 1 not-applicable. **MAY:** 2 met / 3 partial / 0 unmet / 0 not-checked / 0 not-applicable. No overall score is assigned.

## Scientific assessment

**Scientific adequacy: supported. Reported hypothesis outcome: not supported.** The analysis asks whether the supplied participant-level gain-effect estimates show a positive group response and does not mistake a whole-brain posterior finding for vmPFC evidence. In [analysis.py](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/analysis.py), the worker checks that all 54 maps share dimensions and affine and contain finite values, creates a common-coverage brain mask, tests positive one-sample effects, and controls whole-brain family-wise error with 10,000 participant sign flips and maximum t statistics. The independent 12-mm sphere at [0, 40, −12] is a defensible, explicitly operational vmPFC proxy.

[REPORT.md](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/REPORT.md) reports no whole-brain FWE-corrected voxel in that proxy, with mean effect −0.00565 and 95% t interval [−0.0323, 0.0210]. The whole-brain result is a 23-voxel posterior cluster (peak t=6.62, max-T FWE p=.00090), outside the proxy. The report appropriately interprets the null result as lack of evidence for a positive effect, not proof of zero. The participant-level table and three figures make the distributions and results inspectable ([summary](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/results/summary.json), [participant QC and ROI table](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/results/participant_qc_and_roi.csv), [figures](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/figures/)).

Limitations: this is conditional on AO86 participant contrast estimates, whose gain modulator is normalized rather than per currency unit and whose first-level variance maps are absent. The one-sample sign-flip method assumes exchangeability and approximate symmetry. The 95% nonzero-coverage mask and standard MNI152 brain mask resampled to an MNI152NLin2009cAsym grid are documented, though the template-space approximation deserves caution near anatomical boundaries. The ROI is one reasonable operational definition; alternate vmPFC definitions could differ. No replay was performed because the worker did not supply a reproducible Python environment; this does not invalidate the inspected numerical analysis, but limits independent computational confirmation.

## What to fix first

- Add a pinned environment and installation instructions, including Python and package versions and the nilearn template-mask prerequisite → make the documented entrypoint runnable → closes must/003, /007, /010–/017 and should/006–/008.
- Track the analysis script, report, figures and results at the worker stop → preserve the scientific deliverable in version control → closes must/004.
- Add a run record linking the generated outputs to the exact environment and command → make the reported values attributable to a computation → closes must/006 and strengthens should/002, /004, /006.
- Document how the input, analysis, results and figures fit together → make the study structure easier to navigate and update → strengthens should/003 and may/002–/005.

## What is already strong

- The full stopped workspace contains the complete report, analysis script, generated maps, tabular QC and figures, even though those core files were untracked ([worker stop receipt](../worker-end-state.json); [probe output](./2026-10-16-probes.json)).
- Inputs are source-identified and checksum-recorded, with 54 participant maps carried by git-annex ([input/sources.json](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/input/sources.json); large-in-annex probe).
- The scientific report explicitly states the corrected inference, uncertainty, ROI choice and limits of the upstream model ([REPORT.md](../../../../../../judge-targets/narps-neutral-r1-08-j01/content/workspace/REPORT.md)).

## STAMPED item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md` | All supplied project files sit under the workspace root; input, code, results and figures have distinct paths. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | The participant maps are annex-linked under input/data and their source inventory is inside the same root. |
| must/003 | S.1 | unmet | judgement | `analysis.py`, `probe:env-spec-tracked` | The script imports external Python packages, but the delivery has no environment declaration or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probe:tree-clean`, `REPORT.md` | Git is used, but the report, analysis script, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `input/sources.json` | Git-annex carries the 54 participant maps; the stop capture includes their bytes and mapping. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `probe:env-spec-tracked` | The probe's not-checked result was resolved by inspecting the complete stopped delivery; the cited absence is in that delivery. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md`, `probe:entry-point` | REPORT.md gives a usage pointer to analysis.py but does not provide installation or dependency setup instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis.py`, `REPORT.md` | analysis.py is a clear starting point and REPORT.md identifies it as the complete group workflow. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis.py`, `probe:no-abs-paths` | The analysis script derives input and output paths from its own location with pathlib. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analysis.py`, `probe:env-spec-tracked` | NumPy, pandas, nibabel, nilearn, SciPy and matplotlib are imported without any delivered environment specification. |
| must/011 | P.1 | unmet | judgement | `REPORT.md`, `analysis.py` | The report assumes a supplied Python environment but does not identify its platform, Python version or required host configuration. |
| must/012 | P.2 | unmet | probe:env-spec-tracked | `REPORT.md`, `probe:env-spec-tracked` | No delivered documentation or environment file lists the system requirements and dependencies needed to run analysis.py. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment specification is present in the worker's captured workspace or tracked repository. |
| must/014 | P.3 | unmet | judgement | `REPORT.md`, `probe:env-spec-tracked` | The delivery declares no process for updating environment specifications when dependencies change. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `probe:env-spec-tracked`, `worker-end-state.json` | The probe's not-checked result was resolved by inspecting the complete stopped delivery; the cited absence is in that delivery. |
| must/016 | D.1 | unmet | judgement | `probe:env-spec-tracked`, `worker-end-state.json` | No worker-supplied environment specification exists to share or retrieve. |
| must/017 | D.1 | unmet | judgement | `REPORT.md`, `probe:env-spec-tracked` | The report says to use a supplied Python environment but gives no way to obtain or use a specified environment. |
| should/001 | T.2 | met | probe:large-in-annex+judgement | `probe:large-in-annex`, `probe:tree-clean` | The study uses Git for project metadata and git-annex for the participant maps within the same repository. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `worker-end-state.json` | The probe's not-checked result was resolved by inspecting the complete stopped delivery; the cited absence is in that delivery. |
| should/003 | M.1 | partial | probe:modules-separated | `probe:modules-separated`, `analysis.py` | Inputs, generated results and figures have separate directories, but code and environment are not separate modules. |
| should/004 | E.1 | unmet | judgement | `probe:ci-present`, `worker-end-state.json` | No worker record shows this pipeline tested in a fresh container, batch job, clean VM or cloud instance. |
| should/005 | E.1 | unmet | judgement | `REPORT.md`, `probe:env-spec-tracked` | The documented route is a local script and does not create a disposable environment for execution. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `probe:env-spec-tracked` | The probe's not-checked result was resolved by inspecting the complete stopped delivery; the cited absence is in that delivery. |
| should/007 | D.2 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment artifacts such as a lockfile, image or archived runtime are included in the worker delivery. |
| should/008 | D.2 | unmet | probe:run-env-linked+judgement | `REPORT.md`, `probe:env-spec-tracked` | The probe's not-checked result was resolved by inspecting the complete stopped delivery; the cited absence is in that delivery. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: delivered participant maps and metadata are publicly sourced; no restricted component is identified. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `probe:large-in-annex` | The independently maintained participant dataset is identified by source, participant, path, byte count and checksum; its bytes are carried via annex. |
| may/002 | M.2 | partial | judgement | `REPORT.md` | Input, result and figure locations are named, but their modular relationships and recombination are not documented. |
| may/003 | M.2 | partial | judgement | `analysis.py`, `REPORT.md` | Input and generated-output directories have boundaries, but no stable module interfaces or independent update guidance are described. |
| may/004 | M.2 | met | judgement | `analysis.py` | analysis.py is the composition mechanism: it consumes the input module and generates the result maps, table and figures. |
| may/005 | M.2 | partial | judgement | `REPORT.md`, `probe:entry-point` | REPORT.md points readers to key files, but there is no README or dedicated guide to navigate the project structure. |

## Additional finding outside the pinned checklist

- Reuse terms are not declared for the study code/results (probe license-declared; no LICENSE, LICENSES/ or REUSE.toml found in the complete captured workspace). This is recorded as extra_items in the response and is not folded into checklist counts.

## Flagged items

- must/004: the tree-clean probe measured whether Git contained the whole state; it found report, script, figures and results untracked. The full captured delivery still contains them, so Git use is partial, not absent.
- must/006, must/015, should/006: probes could not map an environment to run records; inspection of the complete capture confirmed that neither run-environment provenance nor an environment specification is present.
- must/007: the filename probe did not recognize REPORT.md; the report does provide a usage pointer, but lacks installation and dependency setup.
- must/008: the filename probe did not recognize analysis.py as an entrypoint; the report explicitly identifies it.
- should/002: the CI probe did not check equivalent records; inspection found no recurring test or repeated workflow-validation record.
- should/008: repeats must/014 by checklist design (upstream-duplicate).

## Not checked and scope limits

- Replay: not checked; no worker-supplied environment declaration establishes safe prerequisites. The exact entrypoint, output selection and comparison rule are recorded in [replay record](./2026-10-16-replay.json). No outputs were removed.
- Access: the input data route was checked from this assessment host for the collection and one representative map; it does not cover the complete project package. The worker's complete-delivery publication route is not evidenced. See [access record](./2026-10-16-access.json).
- No external Git pointers or original absolute links were followed. The manifest reports no external Git dependencies and judge-target.json has no reference limits. Participant-map symlinks point within the captured workspace to retained annex objects.
- Probe-supported Git checks ran against the captured local .git directory. The worker stop receipt, not later preservation or coordinator access, is the attribution boundary.

### Snapshot and attribution

**Capture comparison note:** the complete manifest validated before probes. A read-only post-assessment comparison found only an annex SQLite bookkeeping database changed and db-shm/db-wal sidecars appeared; all scientific inputs, code, report, results and figures still matched the manifest. The cause is not established and may be annex bookkeeping from probe/tool access. This mismatch is recorded in [activity log](./activity-log.md); no repair was made. Worker tracking conclusions rely on the stop receipt and the probe output, not the changed annex database.

**Attribution:** the stop receipt marks the 54 participant maps and supplied cohort/source/method files as inputs. REPORT.md, analysis.py, results and figures are present in the worker's complete stop capture but were untracked in Git. Later coordinator preservation does not change that worker-stop state or establish worker publication. The capture also retains .entire session metadata; its contents were not used as grading evidence and no assistance attribution is inferred.

## Goals and kind

Assumption, not human-confirmed: the goal is a concise, reproducible group analysis of the positive gain effect in vmPFC for the NARPS equal-indifference group. This is a study object: it contains supplied participant inputs, analysis code, group results and interpretation. This assessment follows the task brief and report because no human guidance is attached.

Checklist URL: [2026-10-16-url.txt](./2026-10-16-url.txt). Response: [2026-10-16-response.json](./2026-10-16-response.json). Probes: [2026-10-16-probes.json](./2026-10-16-probes.json).

Produced by assess-alignment-with-stamped-principles 0.1.0 with stamped-conventions 0.1.0, checklist 0.3.1 (stamped-checklist-schema@v0.3.1, af259ba), on the original complete delivery captured 2026-10-16T06:30:33.212873Z at worker commit eece8595d255a766517e32ff10b2e6574d3c4e6a; assessor GPT-6 API agent (deployment build not exposed), 2026-10-16. Probe output: 2026-10-16-probes.json. Capture SHA-256: 2afd81ca5fdfaa03e85f2d3e65b04aac9f4b3d90eb39f95c2497266e4cf3cdc7.
