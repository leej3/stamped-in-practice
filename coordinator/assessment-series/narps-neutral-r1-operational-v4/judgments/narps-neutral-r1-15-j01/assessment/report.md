# Independent assessment

Assessment date: 2026-10-16. Object kind: study with a group neuroimaging analysis. This assessment covers the full stopped workspace, including untracked and ignored files, rather than HEAD alone.

## Checklist verdicts

**MUST: 5 met / 1 partial / 11 unmet / 0 not-checked / 0 not-applicable.**  
**SHOULD: 0 met / 2 partial / 2 unmet / 4 not-checked / 1 not-applicable.**  
**MAY: 1 met / 1 partial / 0 unmet / 1 not-checked / 2 not-applicable.**

The item-level table is in [response-table.md](response-table.md); machine-readable answers are in [response.json](response.json). The checklist app URL is retained in [checklist-url.txt](checklist-url.txt).

### What to fix first

- Commit the report, analysis script, figures, and results, or otherwise track their complete state. At worker stop, Git reported `analysis/`, `figures/`, `report.md`, and `results/` as untracked; their presence in the complete capture does not make them versioned.
- Add an installable, complete environment declaration and a documented setup/run route. The report lists Python and package versions, but does not pin the full environment, declare installation steps, or record which environment generated the delivered results. The analysis downloads the Harvard–Oxford atlas at runtime, so its network prerequisite should also be documented.
- Publish a worker-declared access route covering inputs, code, results, and environment information. No worker remote or other authorized retrieval route was available to check.

### Strong evidence in the scientific work

- `analysis/group_analysis.py` checks each map against `input/sources.json`, validates shape, affine consistency and finite values, and analyzes the common nonzero coverage. `results/input_qc.csv` retains per-map byte, checksum, geometry, and finite-data checks.
- `report.md` explains that the maps are participant gain-effect estimates rather than test statistics or per-currency-unit slopes, and notes that participant variance maps and the upstream pipeline are unavailable.
- The inference uses the 54 participants as independent units, applies a single sign to each participant's full map per draw, and controls positive one-sided whole-brain inference with max-T. The report and figures distinguish the corrected whole-brain result from a descriptive ROI average.

## Scientific assessment

**Scientific adequacy: supported.** The analysis is an adequate group-level test of the supplied hypothesis conditional on the fixed AO86 maps. The cohort metadata and file selection target the 54 equal-indifference participants; the code checks checksums, expected geometry, matching affines and finite data, uses the intersection of nonzero coverage, and excludes no participants. Its one-sample voxelwise mean test and participant-level sign flips preserve each map's spatial dependence and address the positive directional hypothesis with whole-brain max-T correction. The operational vmPFC mask is described using Harvard–Oxford labels, spatial restrictions, nearest-neighbour resampling and common coverage; the report acknowledges atlas/template and boundary uncertainty. No vmPFC voxel survived the stated correction, while the corrected positive voxels were posterior and outside the ROI. The ROI mean and interval are explicitly descriptive and do not substitute for corrected inference.

The reported hypothesis outcome is: **This group analysis did not support the predicted positive gain effect in vmPFC.** This is a lack of corrected evidence in these data, not proof of a zero effect. The report appropriately limits interpretation because the upstream gain modulator was normalized, maps are conditional on fixed modeling choices, participant variance maps and executable upstream analysis are absent, and the sign-flip test assumes independent participants and a symmetric null. The conclusion is supported at the group-analysis stage; it does not validate upstream modeling or generalize beyond this group and contrast.

Evidence reviewed in the canonical capture (SHA-256 `f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9`): `report.md` (file SHA-256 `f6804e630acad03d64a4503451751d62b37849c026678a234775f9414737a726`), `analysis/group_analysis.py` (`5e4224df7b7a4c1e5d4fb47271604e908bc4313685322d29710f1dfafec8ddfb`), `input/upstream-methods.md` (`508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`), `input/participants.tsv` (`faca815bcb042144bdb8dcff915f45de0d27650f60416ed76a5a72557341abbf`), `results/summary.json` (`df9593e4a9df67cdf50fd355c3ca8e34734ccafc95c78ec67366f79ad5d39f9a`), `results/input_qc.csv` (`f99f9807fa8e53b31e1f7252c037526ec6152a62648f07ae41ac479ee128e124`), `results/fwe_clusters.csv` (`a1fce2adef2b3ca9a3f950f5f04e91810891794816ca8e9cb1c6f4f6c4ffd94f`), and `results/vmPFC_mask_definition.txt` (`599b0c61062912e2ab55f43f408437f822302a446e38ca5e401b5aa9301133e0`).

## Replay and measurement availability

**Replay: not checked.** The documented entrypoint is `python analysis/group_analysis.py`. It imports Python packages whose versions appear in `report.md`, but the worker supplied no dependency declaration from which to reconstruct the environment. It also fetches the atlas at runtime. Under the frozen scope, I did not install packages, fetch missing inputs, or execute the script in the assessor environment. The candidate scientific outputs and comparison rule are recorded in [replay-record.json](replay-record.json). No replay copy was created and no replay output is claimed. Existing files in `results/` and `figures/` are worker-delivered results, not replay evidence.

## Worker-stop state, access, and integrity

The worker-stop receipt records a complete capture with no capture errors or omissions, a successful worker exit, and original HEAD `d857ab1302d13cb660a7a044af07141f44bfa9ba`. The canonical original capture is manifest SHA-256 `f4ff42772c87811840ea4addf956b2869bc5328ec1ebc32b37c2b523f180e9d9`. The receipt is retained at the coordinator-supplied path in the run record; its SHA-256 is `0ce203b9e453a0252fbf93d01ea2ce98d99c5731f6cfb76b20c566d26bb7365a`. The worker's report, code, figures and results were untracked at stop. I attribute no later coordinator commits, annex conversion, publication, upload, locking, archival or access route to the worker. Annexed input pointers are present in the captured workspace, but this establishes their state in the delivery, not a worker publication route.

No worker remote or authorized retrieval route was declared in the captured Git configuration, and no route could be tested. The intended recipient is another researcher; required coverage is the complete analysis package (inputs, code, results, instructions, and environment specification). No tested worker host scope can be claimed. Coordinator delivery of the capture to this assessment is not evidence of worker-side access. See [access-record.json](access-record.json).

The supplied canonical and operational manifests report complete captures with no omissions or capture errors, the same captured HEAD, no external Git dependencies, and a workspace-resident `.git` directory. `judge-target.json` has an empty `reference_limits` list. A final byte and link comparison found no non-permitted changes to the operational copy. Inspection changed only permitted regular-file annex metadata: `.git/annex/keysdb/db` changed from captured SHA-256 `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca` to `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`; `db-shm` and `db-wal` were created. These are inspection-induced operational metadata and not worker evidence; logical database equivalence is not claimed. The launcher verifies the operational copy against the canonical capture before and after assessment. No retained external pointer was followed. The `.entire/` assistance metadata directory was present; its contents and identifiers were not used as grading evidence.

## STAMPED checklist findings

No overall score is calculated. The assessment follows checklist 0.3.1 and the frozen assessment runner checked from `assessment-version.json` (SHA-256 `27d75f55b892856b2e5b025515c07c37632a377b3e4314c894fdb0d7ae13c6c4`), source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, and environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output is [probes.json](probes.json); `commands/` retains the runner check, probe, response and validation command outputs.

The license probe found no license declaration; this is reported as an extra finding because the pinned checklist has no license item. Items marked partial, not-checked, and not-applicable are explained in the response table. A flagged item means a probe was overridden or a duplicate checklist item was identified, as recorded in `response.json`.

### Flagged checklist findings

- `must/002`: the subdataset probe only inspected Git-recognized links; the full capture contains the maps and metadata under `input/`, and the script references them relative to its root.
- `must/006`: the probe did not recognize untracked delivered results; those outputs exist, but no worker run record binds them to a complete environment.
- `must/008`: the entry-point probe missed the untracked script; `analysis/group_analysis.py` is a clear single-script starting point.
- `must/011` and `must/012`: the command scan could not assess host needs; manual inspection found runtime atlas retrieval and a prose package list, supporting unmet and partial verdicts respectively.
- `should/008`: this repeats the dependency update process asked by `must/014`; it is flagged as an upstream duplicate.

### Not checked

- `should/002`: no independently verifiable recurring test record is in the delivery; worker-side test history could settle it.
- `should/004`: no worker record establishes whether the pipeline ran on a fresh host; execution provenance could settle it.
- `should/005`: no worker record establishes disposable-environment use; execution provenance could settle it.
- `should/006`: no record establishes repeated reconstitution tests; a pinned environment and worker test history could settle it.
- `may/003`: module contracts or independent-update records could settle whether the directory boundaries support independent updates.

### Goal and project kind

The stated goal is a group-level test of a positive gain effect in vmPFC for the equal-indifference group, using the supplied participant maps and metadata (`input/study-task.md`). This is a study-level computational research object. Assessment emphasizes reproducible analysis, data/code/result organization, and evidence for the group inference.

## Scientific judgment record

The exact scientific adequacy label and verbatim report excerpts are recorded in [scientific-judgment.json](scientific-judgment.json) and validated against the canonical delivery manifest. The hypothesis outcome is recorded separately from the adequacy label.

During setup, an unfiltered dump of the frozen procedure exposed coordinator-retained object identifiers and commit metadata. I did not use those identifiers, commits, or any other worker material as grading evidence; no peer scientific output or prior judgment was opened. This exposure is recorded for transparency and does not affect the item or scientific verdicts above.
