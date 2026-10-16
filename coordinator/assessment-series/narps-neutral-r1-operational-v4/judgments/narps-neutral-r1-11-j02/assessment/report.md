# Independent assessment

## Delivery and scope

**Canonical capture:** `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa`  
**Captured HEAD:** `eece8595d255a766517e32ff10b2e6574d3c4e6a`  
**Scientific adequacy:** **supported**  
**Reported hypothesis conclusion:** In the 54-person NARPS equal-indifference group, the supplied gain-effect maps do **not support a positive vmPFC response** at the group-analysis stage.

I assessed the full operational workspace, including its uncommitted analysis, report, and results. Its initial operational manifest carries the same canonical identity. After inspection, all 1,163 workspace entries other than annex-key database metadata matched the initial manifest; no nonmetadata mismatch was found. The annex `keysdb/db-shm` and `keysdb/db-wal` sidecars present in the initial manifest were absent after Git/annex probing. I treat this as inspection-induced operational metadata, not worker evidence, and make no claim of logical database equivalence. The runner’s before/after capture verification also completed. The original capture has no declared reference limits.

The worker-stop receipt records a complete, successful stop and the captured HEAD above. It attributes all submitted files to that stopped state. Later coordinator preservation and this assessment’s annex metadata activity do not count as worker practice. The target includes a captured session transcript and prompt metadata under `.entire/`; this exposes assistance/session information. I record that exposure but do not use it as grading evidence.

## Scientific assessment

The scientific conclusion is supported by the reported evidence and analysis, conditional on the supplied participant-level estimates. `input/participants.tsv` lists 54 equal-indifference participants, and `input/sources.json` identifies 54 matching participant maps. The script checks the participant IDs, common image shape and affine, finite values, and each map’s recorded SHA-256. It retains an effect-independent support mask at 90% nonzero coverage. These choices address cohort membership and basic geometry and data-quality checks without outcome-based exclusions. [Capture evidence: `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/input/participants.tsv`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/input/sources.json`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/analysis/run_analysis.py`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/results/participant_qc.tsv`]

The group model treats each map as one participant coefficient estimate and uses an equal-weight, one-sided one-sample t statistic. Its 10,000 participant-wise sign flips retain the maximum positive statistic over the full 210,968-voxel mask, giving whole-brain max-T family-wise correction under the stated participant-level sign-symmetry null. The output reports 24 corrected voxels in three small posterior foci, but none in the vmPFC proxy. The independently selected Harvard–Oxford Frontal Medial and Subcallosal labels provide a defensible, explicitly limited vmPFC proxy. The ROI average is 0.0062 coefficient units, with a two-sided 95% interval of [−0.0204, 0.0327]; its uncorrected one-sided p-value is descriptive. The reported result is therefore a lack of corrected support for the positive vmPFC hypothesis, not evidence that the true effect is zero. [Capture evidence: `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/analysis/run_analysis.py`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/results/results.json`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/report.md`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/results/figure1_whole_brain.png`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/results/figure2_vmPFC_participants.png`]

The conclusions are appropriately bounded by the supplied data. `input/upstream-methods.md` says that these are gain-modulator coefficients after mean-centering and variance normalization, not change per currency unit; it also records that first-level variance maps and an executable upstream model are absent. The report acknowledges equal weighting, the sign-symmetry assumption, and the non-unique anatomical boundary. One limitation is that voxels represented in at least 90% of maps still include zeros for the remaining participants; those values are not modeled as missing. This can affect inference near coverage boundaries, but the common-support rule and disclosed interpretation keep it from materially overturning the reported vmPFC absence. The supplied effects also cannot establish that the upstream model fully captures the biological response. [Capture evidence: `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/input/upstream-methods.md`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/analysis/run_analysis.py`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/report.md`]

**Scientific adequacy: supported.** The conclusion accurately describes the corrected evidence and its limits. The reported hypothesis outcome remains the bounded absence of corrected positive vmPFC support.

## STAMPED checklist attainment

These verdicts concern the worker’s recorded stop state. Probe output was used as a starting point, then corrected where untracked files in the complete delivery supplied evidence the Git-only probes did not see. The validated response JSON is the machine-readable record; no overall score is assigned.

| Item | Attainment | Evidence and reason |
|---|---|---|
| must/001 | met | Workspace content is rooted under one project directory; annex map links resolve within its `.git/annex/objects` tree. |
| must/002 | met | The maps and cohort metadata are included under `input/`; source URLs are recorded in `input/sources.json`. |
| must/003 | unmet | The downloaded atlas is included, but software dependencies are not packaged or declared in a tracked environment or linked software component. |
| must/004 | unmet | Captured Git state tracks the supplied inputs, while `analysis/`, `report.md`, and `results/` are untracked at stop. The repository commit alone is not the complete result. |
| must/005 | met | Git annex carries 54 map pointers; no oversized binary blob was found in Git. |
| must/006 | partial | `results/results.json` records Python and major library versions, but no exact environment specification is present to link the run to a reproducible environment. |
| must/007 | partial | `report.md` contains a usage command, but there is no README or Makefile, and the command points to an external machine-specific environment. |
| must/008 | met | `analysis/run_analysis.py` is a clear entrypoint and `report.md` documents how the worker intended it to be invoked. The probe missed these untracked files. |
| must/009 | met | The script derives its workspace paths from its own location and uses relative project paths. |
| must/010 | unmet | No dependency or environment specification is supplied. |
| must/011 | unmet | The report points to one external environment path but does not document the host assumptions required to recreate it. |
| must/012 | unmet | Installation requirements and system dependencies are not listed. |
| must/013 | unmet | No environment specification is present alongside the code. |
| must/014 | unmet | No update process for environment specifications is documented. |
| must/015 | unmet | No frozen environment specification is supplied. |
| must/016 | unmet | There is no worker-published environment artifact to retrieve. |
| must/017 | unmet | No instructions explain how to obtain or use a reproducible environment specification. |
| should/001 | partial | One Git repository is used, but the report, code, and generated analyses were not committed. |
| should/002 | unmet | The complete delivery contains no recurring test or validation process. A single captured set of outputs is not evidence of regular testing. |
| should/003 | partial | Inputs, code, and results occupy separate directories, but environment dependencies are not separated or declared. |
| should/009 | not-applicable | No restricted data or software is identified in the captured project. |
| should/004 | not-checked | No clean-host or fresh-container test is recorded; the scoped replay was unsafe to attempt. |
| should/005 | unmet | No disposable execution environment is specified or documented. |
| should/006 | unmet | No exact environment is available for regular reconstitution checks. |
| should/007 | partial | The Harvard–Oxford atlas and MNI template are included, but the software environment is not archived. |
| should/008 | unmet | No environment update process is documented. |
| may/001 | not-applicable | The project has no independently maintained submodule or subdataset component. |
| may/002 | partial | The folder structure separates inputs, analysis code, and results, but their composition is not documented as modular interfaces. |
| may/003 | partial | The input/code/results boundaries are visible, but there is no environment module and no independent update mechanism. |
| may/004 | partial | The analysis script composes the supplied inputs into results, but there is no explicit module-composition mechanism. |
| may/005 | partial | The directory names and report orient a reader, but no README or module map is supplied. |

The probe’s extra checks found no declared license (`license-declared: unmet`), no text blob over 10 MiB (`clone-weight: met`), and no linked-module input state to compare (`inputs-untouched: not-applicable`). `no-abs-paths` passed for scanned tracked text, but the full untracked report does contain an absolute environment path; that path is documented, not embedded in the analysis script. `entry-point` also reported unmet because it inspected tracked files only; the full delivery changes must/008 to met as described above. [Capture evidence: `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/.git/HEAD`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/.git/index`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/analysis/run_analysis.py`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/report.md`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/results/results.json`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/input/sources.json`]

## Access and retrieval

The intended recipient is a researcher using a route the worker declared. The only worker-declared retrieval route found is the source mapping in `input/sources.json`: NeuroVault for participant maps and pinned GitHub raw content for cohort metadata. A HEAD request to one NeuroVault map URL and the cohort-table URL returned HTTP 200 from the assessment runtime host on 2026-10-16. This tests only those example source endpoints from this host. Those URLs cover upstream inputs, not the worker’s report, code, figures, or complete stopped workspace. No worker-declared route for retrieving the complete project or its derived artifacts is present in the captured Git configuration or report. Coordinator delivery to the assessor is not evidence that the worker had published the complete object. [Capture evidence: `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/input/sources.json`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/report.md`, `33a09d4cca1ff0dfd711b954e140e94c53309fa3eb938ee0d86f62a158f7bdfa:content/workspace/.git/config`]

## Replay and measurement availability

**Replay status: not checked.** The documented command is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py`, from the workspace root. Its interpreter is an external absolute path, which I did not follow; the workspace contains no `pixi.toml`, lockfile, requirements file, container definition, or other dependency declaration from which to reconstruct the worker’s environment. Running with the assessor’s Python would substitute an undeclared environment. No replay copy or execution was made.

If prerequisites had been available, the identifiable generated outputs selected from the script would have been `results/analysis_mask.nii.gz`, `results/figure1_whole_brain.png`, `results/figure2_vmPFC_participants.png`, `results/group_mean_cope.nii.gz`, `results/group_t.nii.gz`, `results/minus_log10_p_fwe.nii.gz`, `results/minus_log10_p_uncorrected.nii.gz`, `results/participant_qc.tsv`, `results/permutation_max_t.tsv`, `results/results.json`, `results/significant_fwe05.nii.gz`, and `results/vmPFC_atlas_roi.nii.gz`. The comparison rule would use the frozen helper tolerance `rtol=1e-6` for scientific numeric output, while treating timestamps, logs, prose, and image formatting as nonnumeric differences; shipped outputs would not count as replay evidence. Because the necessary environment could not safely be established, those outputs remain unavailable as replay measurements. The assessment helper was not malfunctioning; replay was skipped under the supplied safety rule.

## Records

The accompanying `probes.json`, `response.json`, `checklist-url.txt`, `access-record.json`, `replay-record.json`, and `scientific-judgment.json` preserve the machine-readable decisions and records. The `commands/` directory retains the runner check, probe execution, access checks, integrity checks, and their outputs, including a failed first version of the local integrity comparison script; that checker was corrected before drawing the integrity finding.
