# Independent assessment

**STAMPED:** 5/17 MUST met, 1 partial, 11 unmet, 0 not-checked; 0/9 SHOULD met, 2 partial, 5 unmet, 1 not-checked, 1 not-applicable; 2/5 MAY met, 2 partial, 0 unmet, 0 not-checked, 1 not-applicable. These are per-item counts, not an overall score.

The target is a study research object. Its canonical original capture SHA-256 is `21b5f53f9cbc01dce2bc961e06a436fa5fbeae8a6e8118d53866c2a0ccfb014d`, and its worker-stop HEAD is `c341bb810566ffec5a12747e921f38c28c618b4a`. Paths in the item table and scientific discussion are relative to that captured workspace and identify original evidence. Per-file hashes are retained in `response.json`.

## What to fix first

1. Commit the analysis script, report, and derived outputs before delivery → the recorded Git state otherwise omits the main scientific work → MUST 004; SHOULD 001.
2. Include an installable, pinned environment specification and link it to the run → the current report points to an environment outside the workspace → MUST 003, 006, 010, 013, 015–017; SHOULD 006–008.
3. Add complete setup instructions, including the external template resources and host requirements → a researcher cannot reconstruct the documented execution route → MUST 007, 011, 012.
4. Record regular checks and a clean-environment run → the captured execution history shows analysis runs, not an ongoing testing or isolation process → SHOULD 002, 004, 005.
5. Explain the module boundaries and any update contracts → the input, code, and result folders are visible, but their interfaces are not documented → SHOULD 003; MAY 002–003.

## What the project does well

- The complete 54-map input set is organized under `input/`; Git-annex carries the map payloads, and `input/sources.json` records source and checksum metadata. `scripts/group_analysis.py` resolves paths from the workspace root. (Canonical capture: `input/sources.json`, SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`; `scripts/group_analysis.py`, SHA-256 `a6e6dee319d4da34bedb13adcd4777c88e19af0afa80cadafe957203dcfa0ffe`.)
- The report and code make the group model, positive-direction whole-brain max-T FWE procedure, sphere definition, exclusions, and limitations inspectable. The shipped summary, quality table, participant values, and figures support review. (Canonical capture: `output/report.md`, `output/results/summary.json`, `output/results/image_qc.csv`, and `output/figures/`.)
- The scientific interpretation distinguishes no corrected positive evidence from proof of a zero effect and explains that the upstream gain coefficients are normalized model units rather than BOLD change per dollar. (Canonical capture: `input/upstream-methods.md` and `output/report.md`.)

## Scientific assessment

**Scientific adequacy: supported.** The reported absence of corrected positive evidence in the specified vmPFC region is supported by the submitted group analysis and is appropriately limited to the supplied participant estimates and the chosen vmPFC operationalization. It does not establish that the true effect is exactly zero.

**Worker-reported hypothesis outcome (verbatim):**

> The 54-participant group did **not** show evidence that potential gains produced a greater vmPFC response.

The worker included all 54 equal-indifference participants and used an equal-weight one-sample group test of the unthresholded participant gain-effect estimates. The code computes a positive-direction statistic and a 9,999-draw participant sign-flip max-T correction over a resampled MNI brain mask. That addresses the task's whole-brain correction requirement. The independently located 10-mm sphere at MNI (4, 42, −8) is used to identify vmPFC for reporting, not to replace whole-brain correction. The shipped results report no sphere voxel passing FWE correction; the sphere mean is −0.010 model units (95% t interval −0.036 to 0.015), with 27/54 positive participant means. There are 23 corrected voxels across the whole mask, with the strongest outside vmPFC. (Canonical capture: `scripts/group_analysis.py`, `output/results/summary.json`, `output/results/vmPFC_participant_effects.csv`, and both files under `output/figures/`.)

The maps are treated as independent participant inputs, not as standardized statistics. The supplied metadata and source inventory cover 54 participants and maps. The worker QC reports matching checksums, one 97 × 115 × 81 grid and affine, and finite values. I independently inspected the in-copy annex payloads through the retained operational dependency mapping: all 54 maps shared the same grid/affine, and all 429 voxels in the shipped vmPFC sphere mask were nonzero in every participant map. The zero-valued voxels elsewhere in the maps therefore do not indicate missing observations in this ROI. The full-brain code does acknowledge zero-filled, zero-variance voxels and assigns them t=0; participant-specific coverage outside the vmPFC sphere is not separately quantified, so full-mask inferences remain conditional on that handling. (Canonical capture: `input/participants.tsv`, `input/sources.json`, `output/results/image_qc.csv`, `output/results/vmPFC_sphere_mask.nii.gz`, and `input/data/sub-001_hypo1_cope.nii.gz`; inspection output: `inspection/nifti-inspection.stdout.txt` and `inspection/roi-coverage.stdout.txt`.)

The worker's report correctly notes that the first-level gain modulator was mean-centered and variance-normalized, that participant variance maps are absent, and that the sign-flip approach relies on approximate null symmetry. Thus the effect is not a monetary-unit slope, and equal weighting cannot account for differing first-level precision. These are material limits, but they do not invalidate the narrower result that this analysis did not detect a positive group effect in the fully observed sphere after whole-brain correction.

The supplied figures are legible and aligned with the report: one shows only whole-brain corrected positive voxels, and the second displays the 54 participant sphere means with the mean and interval. Existing outputs are worker-shipped results; they are not replay evidence.

## Replay and access

Replay status is **not-checked**. The documented command is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/group_analysis.py`; that environment is outside the captured workspace. The report lists package versions but supplies no installable environment specification or procedure to obtain the referenced environment. I did not add declarations, install dependencies, or run the script in the inspection copy. The one-attempt limit remains unused. `replay-record.json` declares the nine generated outputs, protects inputs/code/metadata, and sets the comparison rule if a supported environment becomes available. Shipped outputs were not removed or treated as a successful replay.

No worker-declared route for retrieving the complete workspace was found. The worker-stop `.git/config` has no remote; the report points to local files and an external interpreter, and the URLs in `input/sources.json` concern upstream input provenance. No host could therefore be tested for authorized access to the complete project. Coordinator delivery to the assessor is not evidence that the worker published or shared it. See `access-record.json`.

## Worker-stop attribution and integrity

The worker-stop receipt records a complete, non-timeout exit, HEAD `c341bb810566ffec5a12747e921f38c28c618b4a`, and no omissions or receipt errors. It identifies starter files separately from the worker's later additions. At stop, Git had the supplied inputs but left `scripts/`, `output/`, and `.task-skills/` untracked; `.entire/` and `.codex/` were ignored. Later coordinator commits or delivery actions receive no worker-practice credit.

The worker session log records an initial path-resolution failure, then a run with a zero-standard-error warning. The worker changed the input path and zero-variance handling and ran again; later code and output changes were followed by another successful run. The final shipped code and results reflect those later changes. These are worker actions, not assessor malfunction. The captured workspace also contains `.entire/` session metadata and a bundled `.task-skills/pdf/` skill file, which records assistance-related material; I did not use that material as grading evidence or infer any treatment assignment. (Canonical capture: `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl` and `.task-skills/pdf/SKILL.md`.)

I compared the operational copy against the canonical manifest without traversing external targets. No non-allowlisted change was found. `.git/annex/keysdb/db` changed, and regular files `.git/annex/keysdb/db-shm` and `db-wal` were created during inspection; these are operational metadata only, and their logical database equivalence was not established. `judge-target.json` has no reference limits. The target's `.git` is a directory, not an external pointer; no external hook target was followed or run. The failed optional NiBabel import in the assessor environment is retained in `inspection/nibabel-import.attempt.stderr.txt`; the in-copy NIfTI header/value inspection used a read-only parser instead.

## Per-item checklist

The complete per-item evidence and verdicts are also in [`response.json`](response.json). The frozen runner produced this table:

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/participants.tsv`, `scripts/group_analysis.py`, `output/results/summary.json` | All supplied inputs, analysis code, and outputs are contained under the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/participants.tsv`, `scripts/group_analysis.py` | The 54 maps and metadata are delivered under input/ and the script reads them from the workspace root. |
| must/003 | S.1 | unmet | judgement | `output/report.md`, `scripts/group_analysis.py` | External libraries are named, but no software environment or linked software component is delivered. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `.git/config`, `scripts/group_analysis.py`, `output/report.md`, `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl` | Git tracks the supplied inputs, but worker analysis code and outputs were untracked at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | Git-annex carries the 54 binary maps while source metadata retains their checksums. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `output/report.md`, `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl` | The run used an external interpreter and lists package versions, but no exact environment specification links the action to these results. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `output/report.md` | The report gives a run command and package versions, but no installation or environment setup instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `output/report.md`, `scripts/group_analysis.py` | The report names scripts/group_analysis.py as the reproduction entrypoint, and the script reads local inputs and writes outputs. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/group_analysis.py` | The analysis script derives paths from its own location and uses workspace-relative input/output paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `output/report.md`, `scripts/group_analysis.py`, `probes.json` | The report lists versions, but the workspace has no dependency specification that installs them. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `output/report.md`, `scripts/group_analysis.py` | The documented route relies on an external host environment and Nilearn template resources without documenting host or network requirements. |
| must/012 | P.2 | unmet | probe:entry-point+probe:env-spec-tracked+judgement | `output/report.md`, `probes.json` | No README or environment specification gives complete system requirements and dependencies. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json`, `output/report.md` | No environment specification is included in the captured workspace. |
| must/014 | P.3 | unmet | judgement | `output/report.md`, `probes.json` | No environment specification or tracked update process is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `output/report.md`, `probes.json` | The listed package versions are not a frozen environment specification that can reconstitute the run. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `probes.json`, `.git/config` | No environment specification or worker publication route is provided. |
| must/017 | D.1 | unmet | judgement | `output/report.md`, `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl` | The report points to a machine-specific interpreter path but does not explain how to obtain the environment. |
| should/001 | T.2 | partial | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `scripts/group_analysis.py`, `output/report.md`, `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl` | Git and annex version the supplied data, but code and derived results are outside the worker commit. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl`, `probes.json` | The stop record shows a final run and earlier debugging, but does not establish regular testing beyond this captured session. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/participants.tsv`, `scripts/group_analysis.py`, `output/results/summary.json` | input/, scripts/, and output/ are distinct, but no environment module is included. |
| should/004 | E.1 | unmet | judgement | `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl`, `output/report.md` | The recorded execution used a shared host environment; no fresh container, clean VM, batch, or cloud run is recorded. |
| should/005 | E.1 | unmet | judgement | `.entire/metadata/01a14552-3bce-7273-bef7-ad8341e9d1ef/full.jsonl`, `output/report.md` | The recorded workflow uses an existing external environment path, with no disposable environment creation mechanism. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `probes.json`, `output/report.md` | No exact environment specification or reconstitution test is included. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `probes.json`, `output/report.md` | No environment artifact is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `probes.json`, `output/report.md` | No process for updating environment specifications is supplied. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the supplied inputs are publicly sourced and the stopped workspace contains no identified restricted component. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json`, `scripts/group_analysis.py` | N/A: there are no independently maintained project components; the supplied maps are data inputs and Python libraries are runtime dependencies. |
| may/002 | M.2 | partial | judgement | `output/report.md`, `scripts/group_analysis.py` | The report names the script and output locations, but does not explain module relationships or recombination. |
| may/003 | M.2 | partial | judgement | `input/sources.json`, `scripts/group_analysis.py`, `output/results/summary.json` | Inputs, code, and results occupy separate directories, but no interface or contract supports independent updates. |
| may/004 | M.2 | met | judgement | `scripts/group_analysis.py`, `output/report.md` | The single documented analysis script composes local input maps into the reported result and figure directories. |
| may/005 | M.2 | met | judgement | `output/report.md`, `output/results/summary.json`, `output/figures/whole_brain_t_map.png`, `output/figures/vmPFC_participant_estimates.png` | The report links the analysis script, summary, results, and figures for navigation. |


### Probe overrides and flags

- **MUST 002:** the subdataset probe stopped at the absence of submodules; the complete delivery includes the maps and metadata under `input/`, so the item is met.
- **MUST 004:** the clean-tree probe measured whether Git contained the entire stop state. The item is only partial because the supplied inputs are tracked, but the analysis code and outputs are not.
- **MUST 007:** the filename probe missed `output/report.md`; it gives usage and version information, but not installation instructions, so attainment is partial.
- **MUST 008:** the probe missed the untracked script. The report names `scripts/group_analysis.py` as the starting point, so this item is met.
- **SHOULD 003:** tracked-path detection missed the full `scripts/` and `output/` directories. Those modules are separated in the stop state, but the environment module is absent, leaving partial attainment.

### Not checked

- **SHOULD 002:** one captured session shows final execution and debugging, but cannot establish whether the workflow is tested regularly outside this delivery. A repeated-testing record would settle it.
- **Replay measurement:** no worker-supplied installable environment or retrieval instructions exist for the documented host-specific interpreter. A supported environment declaration would allow one fresh complete-delivery replay.
- **Access measurement:** no authorized retrieval route for the complete project was declared, so there was no route host to test.

### Probe-only observations

The frozen probe also reports that no license file or BIDS License field is present. This is an additional reuse concern, not a pinned checklist item. The probe's clone-weight result and its no-linked-inputs result do not change the pinned item verdicts above.

### Goal and kind

The goal comes from the supplied coordinator scientific task: assess a positive gain effect in vmPFC for the equal-indifference group at the group-analysis stage. The object is a **study** research artifact. No treatment assignment was inferred or reported.

## Checklist URL and records

- Checklist-app URL: [`2026-10-16-url.txt`](2026-10-16-url.txt)
- Machine-readable response: [`response.json`](response.json)
- Unedited frozen probes: [`2026-10-16-probes.json`](2026-10-16-probes.json)
- Access record: [`access-record.json`](access-record.json)
- Replay record: [`replay-record.json`](replay-record.json)
- Scientific judgment: [`scientific-judgment.json`](scientific-judgment.json)
- Command and output ledger: [`inspection/command-ledger.md`](inspection/command-ledger.md)

Assessor: frozen external assessment runner and runtime pinned by `STAMPED_ASSESSMENT_VERSION`; harness Codex / GPT-6; assessment date 2026-10-16. Scope: full stopped workspace inspection, frozen probes, worker-stop attribution, route check, and replay eligibility assessment. Replay was not attempted because the required environment could not be reconstructed from worker-supplied declarations.
