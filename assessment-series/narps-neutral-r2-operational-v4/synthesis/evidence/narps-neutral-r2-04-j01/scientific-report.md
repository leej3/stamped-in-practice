# Independent assessment: NARPS Hypothesis 1

**Assumption and kind.** I treat the object as a study: the product is a group-level answer to whether potential gain is associated with a positive vmPFC response. The supplied brief was not user-confirmed. Citations to `content/workspace/...` refer to the canonical original capture, SHA-256 `6356d2c9870cc2696be61d96f784fd3a503e30a9d9ec89240dabf151b0e3af8a`, not coordinator-preserved additions; abbreviated workspace paths below have that prefix.

## Scientific judgment

**Scientific adequacy: supported.** The reported conclusion is appropriately limited to lack of evidence for the vmPFC-localized positive hypothesis; it does not claim an exact null or equivalence. Worker-reported hypothesis outcome from `content/workspace/report.md` (verbatim): “These supplied maps do not support that vmPFC-specific hypothesis.”

The analysis uses all 54 equal-indifference participants and treats the input images as participant effect estimates. `analysis.py` checks file hashes and byte counts, finite values, common shape and affine, then applies an unweighted one-sample group model across independent participants. Its one-sided participant sign-flip maximum-t procedure controls whole-brain family-wise error and includes a plus-one correction. The specified sphere at MNI [0, 40, −10] is used for a descriptive estimate, while the support test remains whole-brain corrected. The report correctly explains that the regressor was normalized upstream, so coefficients are not effects per currency unit, and that first-level variances were not supplied.

The vmPFC sphere estimate is −0.0061 (95% t interval −0.0342 to 0.0221), with no positive corrected voxels in the sphere. The positive whole-brain finding is posterior (peak t=6.62, max-T FWE p≈0.001 at [−26, −102, −3.6] mm) and does not establish the vmPFC hypothesis; the report cautions that it lies at the posterior edge of coverage. The interval is not an equivalence test, the sphere is one defensible anatomical operationalization, and the inference is conditional on the supplied first-level maps. These limits are made explicit in `report.md` and `input/upstream-methods.md`; the figures make the ROI spread and posterior corrected locations inspectable.

This judgment is based on the unchanged complete stopped delivery and its shipped results, not on a replay. **Replay measurement: not checked.** The report specifies Python 3.13.16 and names six packages, but the delivery has no environment specification or install instructions. The available Python 3.13.16 lacks NiBabel and Nilearn; the general Python with those packages is 3.9.18. Installing or substituting an environment would go beyond the delivered instructions. The exact basis and selected outputs are recorded in [replay-plan.md](replay-plan.md) and [replay-record.json](replay-record.json). No shipped output is treated as replay evidence.

## Worker-stop evidence and attribution

The worker-stop receipt (SHA-256 `9102d56d7e9af8e750ea208a0c4139834e73e6f5c23a92e4f19b91ec36655e92`) records a normal exit, no timeout, and no capture errors or omissions. The original captured HEAD is `447429ce6b992313fd5ad4fc326519db7a4f839a`. At worker stop, `analysis.py`, `report.md`, `figures/`, and `results/` were untracked. The scientific artifacts are part of the complete delivery and were assessed, but they are not committed history. I attribute the 54 annex-backed input maps to the supplied seed; their annex representation is not credited as a worker-created practice. No worker commit or Git remote was present, and there was no worker-declared publication or authorized retrieval route. Later coordinator preservation does not establish worker publication, versioning, environment capture, or access.

The operational inspection matched the initial operational manifest except for a changed regular file `.git/annex/keysdb/db`, which is classified as operational metadata. No other target changes were detected. Logical database equivalence was not established. This inspection-induced change is not worker evidence. The supplied `judge-target.json` lists `reference_limits: []`; no retained link or external pointer was followed. Git configuration was read as captured data; its external hooks path was not executed.

The stopped workspace contains `.codex/hooks.json` and `.entire/` session-record paths, indicating assistance/tooling records are present. I did not inspect conversation contents or use those records as grading evidence.

Several early inspection commands had assessor-side syntax or helper errors; corrected inspections were rerun. They did not affect target conclusions. Their commands, stdout/stderr and exit codes are retained in [assessor-malfunctions.json](assessor-malfunctions.json); no frozen-assessor helper malfunction occurred.

## STAMPED results

**MUST: 6 met / 1 partial / 10 unmet / 0 not-checked. SHOULD: 0 met / 2 partial / 4 unmet / 3 not-checked. MAY: 3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable.** These are item verdicts, not an overall score. The per-item reasons and evidence are in [response.json](response.json); the table below is generated from that response.

### What to fix first

1. Commit the analysis, report, figures, and results so the stopped scientific state is versioned with the supplied inputs (must/004, should/001).
2. Add an environment specification with package versions and a usable install/run command; link the generated results to that exact environment (must/003, 006, 007, 010, 012–015, 017; should/006–008).
3. Publish a worker-controlled authorized retrieval route covering code, inputs, results, and environment, and verify it from a researcher context (must/016).

### What is already strong

- All 54 intended participants are included, with explicit image and file quality checks and no exclusions (`analysis.py`, `results/participant_qc.tsv`).
- Whole-brain max-T FWE inference, a fixed vmPFC sphere, uncertainty, upstream scaling, and inference limits are documented (`report.md`, `results/summary.json`).
- The input, code, and result files are navigable, and the supplied large maps use annex-backed storage; the latter was present in the supplied seed rather than created by the worker.

### Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/participants.tsv`, `content/workspace/analysis.py` | All essential maps, metadata, code, report, figures and results are inside one captured workspace root. |
| must/002 | S.1 | met | judgement | `content/workspace/analysis.py`, `content/workspace/input/sources.json` | The script reads maps and metadata through paths relative to its root; all referenced scientific inputs are within the captured root. |
| must/003 | S.1 | unmet | probe:env-spec-tracked | `content/workspace/report.md` | Python dependencies are named in the report but no delivered environment specification installs them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `probe:tree-clean`, `content/workspace/.git/HEAD`, `content/workspace/analysis.py`, `content/workspace/report.md` | At worker stop, the analysis, report, figures and results were untracked; the captured HEAD contains only the supplied seed. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/input/sources.json` | The 54 large participant maps are annex-backed; this input mechanism was present in the supplied seed, not established as worker-created. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `content/workspace/results/run-summary.json`, `content/workspace/report.md`, `probes.json` | A run summary records results, but does not link the producing action to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `content/workspace/report.md`, `probes.json` | The report identifies the script but gives no install or invocation instructions, and no README or Makefile supplies them. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/analysis.py`, `content/workspace/report.md`, `probes.json` | analysis.py is a direct main script and the report identifies it as the analysis workflow. |
| must/009 | P.1 | met | probe:no-abs-paths | `content/workspace/analysis.py`, `probes.json` | The analysis uses root-relative pathlib paths and the tracked text has no system-specific absolute paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `content/workspace/analysis.py`, `probes.json` | The script imports six third-party packages, but the stopped workspace contains no environment specification. |
| must/011 | P.1 | met | judgement | `content/workspace/report.md`, `content/workspace/analysis.py` | The report names Python 3.13.16 and the needed Python packages; the script shows no additional OS, mount, GPU or service assumptions. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/report.md` | The report names Python 3.13.16 and six packages, but omits package versions and a complete system-requirement list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json`, `content/workspace/analysis.py` | No environment specification is present in the stopped workspace or versioned with the code. |
| must/014 | P.3 | unmet | judgement | `content/workspace/report.md`, `content/workspace/.git/HEAD` | No environment specification or reproducible update command is supplied. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `probes.json`, `content/workspace/report.md` | No frozen package manifest, container digest or other exact environment specification is supplied. |
| must/016 | D.1 | unmet | judgement | `content/workspace/.git/config`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-04-j01/attempt-01/worker-end-state.json` | No worker publication or authorized retrieval route for the complete object and its environment was recorded. |
| must/017 | D.1 | unmet | judgement | `content/workspace/report.md`, `probes.json` | The report names packages but gives no instructions to obtain or install an environment specification. |
| should/001 | T.2 | partial | judgement | `probe:tree-clean`, `content/workspace/.git/HEAD`, `content/workspace/analysis.py`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | Git-annex tracks the supplied maps, but the worker-created code, report and results remained untracked at stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `probes.json`, `content/workspace/results/run-summary.json` | No CI configuration or repeat-test record is present in the reviewed project files; equivalent historical testing cannot be established from this capture. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input/participants.tsv`, `content/workspace/analysis.py`, `content/workspace/results/summary.json`, `probes.json` | Inputs and derived files are separated from the script, but there is no environment module; the probe missed the root script and results/figures. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/results/run-summary.json`, `replay-record.json` | Shipped outputs imply a completed analysis, but no record says it ran in a fresh container, batch job, VM or cloud instance. |
| should/005 | E.1 | unmet | judgement | `content/workspace/analysis.py`, `content/workspace/report.md` | The only delivered workflow is a Python script; it does not create or dispose an isolated environment for each run. |
| should/006 | D.2 | unmet | judgement | `probes.json`, `content/workspace/report.md` | No exact environment specification exists to reconstitute or test regularly. |
| should/007 | D.2 | unmet | judgement | `content/workspace/report.md`, `probes.json` | No environment image, package archive or other environment artifact is included. |
| should/008 | D.2 | unmet | judgement | `content/workspace/report.md`, `content/workspace/.git/HEAD` | No environment update process or tracked updates are supplied; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-checked | judgement | `content/workspace/input/sources.json`, `probes.json` | The metadata points to public sources but states no reuse or restriction terms; whether any supplied data/software are restricted is not established. |
| may/001 | M.2 | not-applicable | judgement | — | N/A: no independently maintained project modules are included; supplied data are within the common root and Python packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `content/workspace/report.md` | The report explains the input maps, group script, result maps/tables and figures and links the principal artifacts. |
| may/003 | M.2 | partial | judgement | `content/workspace/input/participants.tsv`, `content/workspace/analysis.py`, `content/workspace/results/summary.json` | Input, code and result locations are distinct, but no formal module boundaries or environment module are defined. |
| may/004 | M.2 | met | judgement | `content/workspace/analysis.py` | analysis.py composes supplied participant maps and metadata into the results and figures using root-relative paths. |
| may/005 | M.2 | met | judgement | `content/workspace/report.md` | The report links and describes the main analysis, input methods, result tables/maps and figures. |

### Probe disagreements and flags

- **must/006:** the run-env probe did not recognize `results/run-summary.json`; manual inspection found a result summary but no exact environment linkage, so the item is partial rather than not-checked.
- **must/008:** the entry-point probe missed untracked `analysis.py`; manual inspection confirms a main script and report reference.
- **should/003:** the module probe recognized `input/` but missed the root script and separate `results/` and `figures/`; the environment module remains absent, so the item is partial.
- **should/008:** repeats must/014 by checklist design.

### Not checked

- **should/002:** the probe found no recognized CI configuration; the capture does not establish equivalent repeated testing. A worker test-history or recurring run record would settle it.
- **should/004:** shipped outputs indicate a completed analysis, but there is no evidence it ran in a clean container, batch job, VM, or cloud instance. A recorded run environment would settle it.
- **should/009:** sources are publicly listed, but the capture states no reuse or restriction terms. A data/software rights declaration would settle whether restricted components exist.
- **Scientific replay:** prerequisites cannot be reconstructed from delivered declarations; see the replay decision above.

### Access record

The intended recipient is a researcher using the declared authorized route. No such worker route was declared or configured; the local operational copy was the only host scope inspected. The original source URLs in `input/sources.json` identify upstream input provenance and do not provide access to this complete analysis object. Required coverage is report, code, cohort metadata, all 54 maps, results, figures, and the missing environment specification. Coordinator delivery is not worker-access evidence. See [access-record.json](access-record.json).

### Extra finding

The probe extras are retained separately from checklist items: `license-declared` is unmet (no license or reuse statement); `clone-weight` is met (no text blob exceeds 10 MiB); and `inputs-untouched` is not-applicable (no linked modules to compare). Source URLs alone do not establish redistribution terms.

### Assessment artifacts and stamp

- [Response JSON](response.json)
- [Probe results](probes.json)
- [Checklist link](checklist-link.txt)
- [Replay record](replay-record.json)
- [Access record](access-record.json)
- [Operational integrity record](operational-integrity.json)

Produced with `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1, by Codex / GPT-6 on 2026-10-16. Object commit: `447429ce6b992313fd5ad4fc326519db7a4f839a`; canonical capture manifest: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/targets/narps-neutral-r2-04-j01/canonical/manifest.json`, SHA-256 `6356d2c9870cc2696be61d96f784fd3a503e30a9d9ec89240dabf151b0e3af8a`. Probe output: [probes.json](probes.json).
