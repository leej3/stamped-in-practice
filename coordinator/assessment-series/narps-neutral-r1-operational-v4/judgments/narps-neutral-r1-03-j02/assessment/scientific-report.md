# Independent assessment — NARPS potential gains and vmPFC

**STAMPED verdicts:** MUST: 3 met / 3 partial / 10 unmet / 1 not-checked (17). SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9). MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable (5). Partial does not satisfy a MUST. No overall score is assigned.

**Scientific adequacy: supported.** The delivered analysis supports a defensible absence of corrected positive vmPFC evidence for the stated hypothesis. This is separate from the worker’s hypothesis conclusion, item attainment, and replay availability.

**Hypothesis conclusion:** The supplied 54 equal-indifference participant gain-effect maps do not support a positive vmPFC response to increasing potential gain under whole-brain correction.

## What to fix first

1. Track the analysis script, report, and generated results as part of the worker’s stopped state. They are currently untracked, so the captured commit does not identify the delivered analysis (must/004, should/001).
2. Deliver a frozen environment specification, dependency-update process, and acquisition instructions. The report lists package versions but points to an external host path (must/003, must/010–015, must/017; should/005–008).
3. Replace the host-specific launch path with a portable documented command and state the host requirements (must/009, must/011–012).
4. Add a run record linking the shipped maps, action, exact environment, and outputs (must/006). A new run would also settle the fresh-environment test items (should/002, should/004, should/006).
5. Declare and test a recipient route that covers the code, source inputs, environment and results; no worker route is recorded at stop (must/016).

## What is already good

- The report distinguishes participant cope estimates from group statistics, states that gain coefficients are not per-currency-unit effects, and explains the missing participant variance maps and fixed upstream model. It identifies all 54 participants and explains the common-support choice. (Capture evidence: `input/upstream-methods.md`, SHA-256 `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`; `analysis/report.md`, SHA-256 `63f7dddf3339708b8f6c3f9c17478661a5c51910b16fdbf049eb1f26e0d4bd0b`.)
- The whole-brain inference is one-sided and uses Bonferroni FWER correction over the stated 198,029 common-support voxels. The ROI estimate, uncertainty interval and figures are consistent with the reported conclusion. (Capture evidence: `analysis/group_analysis.py`, SHA-256 `0fb8ba1cdd5a4bb876c4c4c81d3e132f2c7188fb60240f72369da5f15012ecaa`; `results/summary.json`, SHA-256 `26caa4b98950d05907ac83fad3c8134b5ffd5cd752fcf7b9282c020733e89c09`; figures under `results/figures/`.)
- The captured source inventory identifies the 54 supplied AO86 maps, participant table, upstream methods and retrieval checksums. (Capture evidence: `input/sources.json`, SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`.)

## Scientific assessment

The worker reports that the 54 equal-indifference participants’ mean effect in a prespecified 12-mm MNI sphere centered at (0, 40, −10) was −0.0055 cope units (95% CI −0.0309 to 0.0199; one-sided *t*(53) = −0.44, *p* = .667). No voxel in that sphere survived the whole-brain correction. The whole-brain analysis found 11 positive voxels after Bonferroni correction across 198,029 common-support voxels; the peak at (−26, −102, −3.6) is posterior to vmPFC. The supplied corrected map and participant-level ROI plot visually agree with those statements (`results/group_bonferroni_fwe_p.nii.gz`, `results/figures/whole_brain_fwe_t.png`, `results/figures/vmpfc_participant_effects.png`).

The analysis uses one independent participant map per person, checks matching geometry and finite values, confirms IDs against group metadata, and retains all 54 participants. The group *t* model treats participant effects equally. The common intersection of nonzero map support avoids counting out-of-coverage zeros as observations. Bonferroni is conservative but valid for arbitrary voxel dependence and addresses the required whole-brain family. The independently defined sphere is a transparent operational vmPFC summary; it is not presented as an atlas boundary or as a substitute for corrected whole-brain inference.

The result supports a lack of corrected positive vmPFC evidence; it does not establish a zero effect. The ROI interval includes small positive and negative values. Inference is conditional on AO86’s fixed preprocessing and first-level modeling. Gain regressors were normalized before HRF convolution, gain and loss were modeled separately, and participant variance maps are unavailable. The result therefore does not estimate change per currency unit, compare gain-versus-loss sensitivity, or support a fully weighted mixed-effects analysis. The script’s common-support mask is based on nonzero values, so any genuine exact-zero in-coverage coefficients would also be omitted; the report does not separately validate that edge case against an anatomical coverage mask. This is a bounded limitation, not a reason to reject the stated conclusion.

**Replay status: not checked.** The documented entrypoint is `analysis/group_analysis.py`, and its outputs can be explicitly selected. However, the report’s only launch command uses `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python`, an external absolute path. The stopped delivery includes no environment lock, environment declaration, or archived environment. Reconstructing that external environment would cross the supplied boundary, so no replay helper was invoked and no output was removed. The predeclared replay plan and limitation are in `replay-record.json`. This is an unavailable measurement, not evidence of scientific failure.

## Delivery boundary, attribution and access

The canonical capture is `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`, identified by the retained canonical manifest. The complete original workspace has no capture omissions. The canonical and initial operational manifests share this SHA-256; no starting identity mismatch was observed. The original captured HEAD is `d857ab1302d13cb660a7a044af07141f44bfa9ba`. Unless stated otherwise, every capture-relative path in this report refers to that canonical SHA; cited file SHA-256 values are from its manifest. Operational-copy observations are identified as such and are not treated as worker evidence.

The worker stop receipt (SHA-256 `2d6b098f70edec77b7994f1bc00a9ec902dc6a1c324607c6b5c0572584e1cb68`) records a normal exit at 2026-10-16 06:44:45 UTC and the same capture identity. Its seeded-input inventory includes the participant maps and metadata. At the stopped state, Git status showed `analysis/` and `results/` untracked; `.codex/` was untracked and `.entire/` ignored. The captured HEAD contains the supplied inputs, not the worker’s analysis code or results. The commit, annex representation of seeded maps, and local integration settings are not credited as worker-created versioning, publication, or environment practices. The receipt does not independently identify who authored each untracked file.

The intended recipient is a researcher following the worker-declared authorized route. No such route is declared: the report gives a local environment path, the captured Git configuration has no remote, and no publication URL or access instructions are supplied. Required coverage would include the analysis, all 54 maps and metadata, environment specification, and generated report/results. Tested host scope: local inspection of the captured Git configuration only; there was no worker route to test, and coordinator delivery is not evidence of worker access. See `access-record.json`.

Captured `.codex/hooks.json` (SHA-256 `d0ed5dd1cf5d2d269abfdb6c00161b406d0233b7a4bf1ff72f288405b4959b10`) and `.entire/settings.local.json` (SHA-256 `b8d01a092e151ab8c251ff67b17f16cba06e3550932513174b727816c52ac185`) expose Codex/Entire integrations. This is recorded as an assistance-exposure indicator only and is not used as grading evidence; it does not establish which tools were used to produce the scientific work.

## Item-level STAMPED assessment

All item evidence below refers to the canonical capture SHA above unless the URI explicitly identifies an assessment output or the external worker-stop receipt. Probe results are in [probes.json](probes.json); the full response with hashes and evidence descriptions is [response.json](response.json).

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `analysis/report.md` | The complete workspace and its retained annex payload paths sit under one root. |
| must/002 | S.1 | met | judgement | `input/sources.json` | All 54 maps and metadata are included under the workspace and reached through in-root annex pointers. |
| must/003 | S.1 | unmet | judgement | `analysis/group_analysis.py` | Python software is imported but no delivered environment declares or installs it. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `analysis/group_analysis.py` | Git versions supplied inputs, but the worker's analysis code, report and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `input/data/sub-001_hypo1_cope.nii.gz` | Annex pointers are present, but the stop receipt identifies the maps as supplied inputs; worker tracking practice is not attributable. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `analysis/report.md` | Shipped results have a script and narrative, but no provenance record links their generation to an exact environment specification. |
| must/007 | A.1 | unmet | judgement | `analysis/report.md` | The report gives a run command but no install or environment acquisition instructions a reader can follow. |
| must/008 | A.1 | met | judgement | `analysis/group_analysis.py` | The report identifies analysis/group_analysis.py as the reproducibility entrypoint. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `analysis/report.md` | The script uses workspace-relative paths, while the documented launch command hardcodes a host-specific Python path. |
| must/010 | P.1 | unmet | judgement | `analysis/group_analysis.py` | The scientific script's imported packages are not captured in an environment specification. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `analysis/report.md` | The report names one absolute host path and package versions but omits OS, system-library and other host requirements. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `analysis/report.md` | No README or environment specification lists system requirements and dependencies. |
| must/013 | P.3 | unmet | judgement | `input/sources.json` | No environment specification is present in the complete captured workspace. |
| must/014 | P.3 | unmet | judgement | `analysis/report.md` | No dependency-update process or tracked environment specification is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `analysis/report.md` | The external prepared environment path and package list do not provide a frozen, retrievable environment specification. |
| must/016 | D.1 | unmet | judgement | `analysis/report.md`, `.git/config` | No worker-declared retrieval route exists for the environment or study; the captured Git config has no remote. |
| must/017 | D.1 | unmet | judgement | `analysis/report.md` | Readers are not told how to obtain the prepared environment; the report supplies only a local absolute path. |
| should/001 | T.2 | partial | judgement | `analysis/group_analysis.py` | Git contains supplied inputs, while worker-authored code and results remain untracked. |
| should/002 | A.2 | not-checked | judgement | `analysis/report.md` | No repeated workflow-test record is present; a worker run log or scheduled test history would settle this. |
| should/003 | M.1 | partial | judgement | `analysis/report.md` | Input, analysis and result directories are separated, but the environment is absent and components lack independent module boundaries. |
| should/004 | E.1 | not-checked | judgement | `analysis/report.md` | No fresh-environment replay or equivalent worker test record is available; a completed clean replay would settle it. |
| should/005 | E.1 | unmet | judgement | `analysis/report.md` | The workflow invokes a pre-existing shared environment rather than creating a disposable one per execution. |
| should/006 | D.2 | unmet | judgement | `analysis/report.md` | No exact environment specification exists to reconstitute or test against the shipped results. |
| should/007 | D.2 | unmet | judgement | `analysis/report.md` | No environment image, binary archive or package cache is included with the worker delivery. |
| should/008 | D.2 | unmet | judgement | `analysis/report.md` | No dependency-update process or tracked environment specification is declared. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software component is identified in this public-source study delivery. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json` | N/A: no independently maintained project modules or submodules; the input dataset is bundled under the root. |
| may/002 | M.2 | partial | judgement | `analysis/report.md` | The report links inputs, analysis and results, but does not define module boundaries or how modules can be recombined. |
| may/003 | M.2 | partial | judgement | `analysis/group_analysis.py` | Separate folders permit some independent updates, but no boundary contract or compatibility mechanism is documented. |
| may/004 | M.2 | met | judgement | `analysis/group_analysis.py` | One documented script composes the bundled maps and metadata into identified result artifacts. |
| may/005 | M.2 | met | judgement | `analysis/report.md` | The report links methods, source metadata and result figures and gives the workspace-root launch location. |

## Flagged items

- **must/004 — mapping-questioned:** `tree-clean` measured whether the working tree is clean, while the item asks whether Git is used for code and documentation. The actual distinction is that supplied inputs are committed and worker analysis/results are not.
- **must/005 — probe-overridden:** annex pointers exist, but the stop receipt identifies those maps as seeded resources; this cannot establish worker data-versioning practice.
- **must/006 — probe-overridden:** `derived-have-records` only recognized tracked products; the complete delivery contains untracked scientific results, and no exact environment-linked provenance record accompanies them.
- **must/009 — probe-overridden:** `no-abs-paths` scanned tracked files only; the untracked report’s launch command uses a host-specific absolute interpreter path.
- **must/011 and must/012 — probe-overridden:** the command scan did not resolve host requirements. The report discloses a local environment path and package versions but no complete host/system requirements list.
- **must/015 — probe-overridden:** no environment is named in a recognized run record, and the report’s external path is not a frozen, retrievable environment specification.
- **may/001 — probe-overridden:** no independently maintained module exists; bundled input data are not a project submodule.
- **should/008 — upstream-duplicate:** this repeats must/014 word for word, so it carries the same finding by design.

## Not checked

- **must/005:** the maps are annexed in the stop-state bytes, but the receipt identifies them as supplied inputs; worker action cannot be attributed. A worker-authored input-tracking record would settle this.
- **should/002:** no regular workflow test record is in the complete delivery. A scheduled or repeated test history would settle it.
- **should/004:** no fresh-environment test or equivalent worker record is present. A fresh execution from a complete, declared environment would settle it.
- **Replay:** no attempt was made because the only documented environment path is outside the capture and no environment declaration is supplied. A worker-supplied reconstructable environment would permit the one scoped replay.
- **Access:** there was no worker-declared route to check. A route plus an independent retrieval test covering the required artifacts would settle access.

## Goals and kind

**Assumption (not confirmed with a human):** the goal is to answer the supplied NARPS Hypothesis 1 question from the fixed 54 participant effect maps and report an inspectable group analysis. This is a **study**: a scientific question answered through data and computation. The source is `input/study-task.md` (capture SHA `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`; file SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`).

## Checklist link and provenance stamp

Checklist app: [open the filled checklist](2026-10-16-url.txt). Machine-readable answers: [response.json](response.json). Scripted probe receipt: [probes.json](probes.json). Access and replay records: [access-record.json](access-record.json), [replay-record.json](replay-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on canonical capture manifest `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/targets/narps-neutral-r1-03-j02/canonical/manifest.json`, SHA-256 `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`, original HEAD `d857ab1302d13cb660a7a044af07141f44bfa9ba`, 2026-10-16, Codex API / GPT-6. Probe output: `probes.json`.
