# Independent assessment — NARPS potential-gain study

**Scope and identity.** I assessed the complete captured stopped workspace, including its untracked and ignored files, using operational copy `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/targets/narps-neutral-r2-05-j02/operational/content/workspace`. All original-evidence citations below use canonical capture SHA-256 `ed364b7f272d7828b6460ab12bb0e15fc7aed55f852a83e0da0bd576a8b8d21c` and capture-relative paths rooted at `content/workspace/`. The captured HEAD is `ee2121676b82900d355458da4ad9a13014094fc4`; the stop receipt identifies a complete capture and a worker process that exited with return code 0. Canonical and operational manifests report the same identity and no capture omissions. The assessment identifies assistance-related `.entire/` session records in the capture; they are recorded as exposure only and were not used as grading evidence. No treatment assignment is inferred.

**Goals and kind (assumption, not confirmed).** The documented goal is a group-level scientific answer about a positive gain effect in vmPFC for the equal-indifference cohort, with code, results and a concise report. I classify the object as a **study**: its product is a scientific conclusion from supplied maps and metadata. No human guidance was attached to confirm this assumption.

## Scientific assessment

**Scientific adequacy: supported.** The report's conclusion of no whole-brain-corrected evidence for the predicted vmPFC increase is supported by a defensible group analysis. `analysis.py` validates all 54 participant IDs and source checksums, checks finite values and common shape/affine, includes the complete cohort, uses a common-coverage mask, and performs a one-sided participant-level sign-flip max-statistic test across the whole analysis mask. The approximate vmPFC box is used descriptively rather than as an uncorrected confirmatory ROI. The summary reports 24 FWE-significant voxels in three posterior clusters, none in that box; the strongest box voxel has whole-brain FWE p=.796. The figure distinguishes the corrected map from the descriptive ROI distribution. A fresh replay recreated the selected summary, voxel table and cohort table byte-for-byte.

This supports the reported *absence of corrected evidence*, not a claim that vmPFC has no gain response. Limitations are material but disclosed: sign-flip inference assumes symmetry/exchangeability; the broad coordinate box is not a cytoarchitectonic definition; there are no participant variance maps, so unequal first-level uncertainty is not modeled; and the reported gain coefficients are not per-currency-unit effects. The supplied maps and upstream-methods description support the stated group-stage scope. The result does not estimate a gain-versus-loss contrast.

**Reported hypothesis outcome:** “No whole-brain-corrected evidence supported the predicted vmPFC increase.” This is retained separately from adequacy.

**Replay declaration and record.** I ran the report's exact command, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis.py`, through the frozen helper in a fresh writable copy of the canonical complete delivery. The worker-declared interpreter path was the prerequisite; no dependency repair or adapter retrieval was added. Only the explicitly generated `results/summary.json`, `results/voxel_results.csv`, and `results/included_participants.tsv` were removed from that copy. The JSON was compared byte-for-byte; numeric tables used the frozen relative tolerance `1e-6`. All three recreated identically. This same-host replay did not reconstruct a fresh environment and does not test the figure/NIfTI serialization. The helper's 7,200-second limit and 5 GB prefetch compatibility parameter were retained; it performed no prefetch. The selected paths, hashes, return code, timing and stdout/stderr locations are in `2026-10-16-fresh-rerun.json` and `2026-10-16-replay-work/`.

## STAMPED assessment

**Verdicts: 4/17 MUST met, 1 partial, 12 unmet, 0 not-checked; 0/9 SHOULD met, 2 partial, 3 unmet, 3 not-checked, 1 not-applicable; 3/5 MAY met, 2 partial, 0 unmet.** A partial does not satisfy a MUST. Not-checked and not-applicable are reported separately. These describe the stopped worker delivery; the coordinator-created input commit and annex store, this assessment's replay, and the current NeuroVault response do not earn worker-practice credit.

The highest-leverage improvement is to include a versioned, reconstructable environment specification and installation instructions alongside the analysis. The worker's `analysis.py`, report, and `results/` outputs were untracked at stop, so the delivered scientific work is not captured by HEAD. The useful foundation is that the complete inputs and source checksums are under `input/`, the report explains the group inference and its limitations, and the documented command successfully recreated the selected numerical outputs in a copied delivery.

| Item | Verdict | Evidence and reason |
|---|---|---|
| must/001 | met | `input/`, `analysis.py`, `results/`, report and skill files are under the workspace root; capture manifest is complete. `input/sources.json`. |
| must/002 | met | All 54 input maps and cohort metadata are under `input/`; `analysis.py` reads them by workspace-relative paths and `sources.json` identifies origins. |
| must/003 | unmet | `analysis.py` imports matplotlib, nibabel, nilearn, numpy, pandas and scipy; no worker environment specification or linked software module is present. |
| must/004 | unmet | At stop, `analysis.py`, `report.md`, `results/` and `skills/` were untracked. Captured HEAD is the coordinator's `chore(study): supply materialized scientific inputs` commit. |
| must/005 | unmet | The 54 maps are annex pointers in that coordinator-created input commit; `git annex info` identifies the sole local copy as `coordinator-supplied-inputs`. No worker tracking action is evidenced. |
| must/006 | unmet | The report names an external interpreter path but no exact environment specification is linked to the generated results. Replay is coordinator measurement. |
| must/007 | partial | `report.md` documents a run command and usage, but gives no way to obtain/install the external prepared environment. The entry-point probe missed this equivalent report route. |
| must/008 | met | `report.md` names `analysis.py` as the script regenerating `results/`; the entrypoint is runnable in the copied delivery. |
| must/009 | met | `analysis.py` constructs input/output locations from `Path(__file__)`; the no-absolute-path probe omitted this untracked script, so this verdict is based on direct inspection. |
| must/010 | unmet | Scientific imports in `analysis.py` have no delivered dependency declaration; the external prepared environment is not included. |
| must/011 | unmet | The reproduction command requires a host-specific absolute interpreter path; OS and other host assumptions are not documented. |
| must/012 | unmet | No worker-supplied environment specification or system-requirements list is delivered. |
| must/013 | unmet | No environment specification is tracked at worker stop; the only committed change shown by HEAD supplied coordinator inputs. |
| must/014 | unmet | No environment update/regeneration process or environment history is present. |
| must/015 | unmet | No frozen package manifest or environment identity is included; reported software versions alone do not define the environment. |
| must/016 | unmet | No worker-published environment specification or access route is present. NeuroVault links identify source data, not the runtime environment. |
| must/017 | unmet | The report gives an absolute interpreter path but no instructions to obtain the environment. |
| should/001 | partial | Git and annex represent coordinator-supplied inputs; worker analysis, report and results were untracked at stop. |
| should/002 | not-checked | The complete stop state contains no worker-authored recurring-test record. The successful replay is a one-time coordinator measurement, not regular testing. |
| should/003 | partial | Inputs, code and outputs have separate directories, but there is no separate environment module or documented modular contract. |
| should/004 | not-checked | No worker record establishes testing in a fresh container, batch job, clean VM or cloud instance. The coordinator replay reused the host environment. |
| should/005 | unmet | The documented command invokes a pre-existing absolute-path interpreter; `analysis.py` does not create a disposable environment. |
| should/006 | not-checked | No worker environment identity/reconstitution record exists to establish repeated testing of the exact environment. |
| should/007 | unmet | No environment artifact is archived with the workspace. |
| should/008 | unmet | No environment update process is supplied; duplicate of must/014 under the pinned checklist. |
| should/009 | not-applicable | The assessed input source is public and no restricted data or software component appears in the delivery. |
| may/001 | met | `input/sources.json` separately identifies the external AO86 maps, URLs and cohort/method sources; `input/` is the clear boundary. The source route was checked only in limited scope; see access record. |
| may/002 | partial | `report.md` explains the input-to-analysis-to-results relationship but does not document a broader module/recombination structure. |
| may/003 | partial | Input, analysis and results have directory boundaries, but no environment boundary is defined and script paths couple the components. |
| may/004 | met | `analysis.py` is the composition mechanism: it reads `input/` and regenerates named files in `results/`; this route replayed successfully. |
| may/005 | met | `report.md` and `input/sources.json` describe the inputs, generated outputs and their roles. |

Probe outputs are retained unchanged in `2026-10-16-probes.json`. Direct review overrode or completed probes where the probe saw only tracked files: notably `entry-point` missed the report's documented script; `no-abs-paths` missed untracked `analysis.py`; and annex presence did not establish worker data-tracking practice. The no-submodule probe does not settle dataset reachability because the source manifest supplies direct input references. Duplicate checklist items must/014 and should/008 have the same response and are flagged as an upstream duplicate. `license-declared` is retained as a probe-only extra finding, not a checklist item.

## Retrieval and access

`input/sources.json` declares NeuroVault collection API and individual image URLs, but this file and the annex materialization are coordinator-supplied. For a researcher using the declared authorized route, the route tested was the NeuroVault API plus one representative image URL: both returned HTTP 200 to HEAD from this assessment host. This establishes only the tested NeuroVault host and these two endpoints at assessment time. Required scientific input coverage is 54 participant maps plus the equal-indifference cohort table and upstream-method description. The capture contains the maps, `participants.tsv` and methods summary; the API and one image were not checked for complete 54-map retrieval or checksums during this route test. The reported environment and dependencies have no declared retrieval route. This coordinator-side delivery and route check do not establish that the worker published or exposed the object. Full details and preserved headers are in `access-record.json` and `access-neurovault-*.stdout`.

## Integrity, attribution and scope

The launcher verifies the canonical capture before and after assessment. My independent comparison of the operational copy found new `.git/annex/reposize/` files outside the permitted metadata exception after read-only annex inspection; `.git/annex/keysdb/db`, `db-shm` and `db-wal` differences are separately classified operational metadata and do not establish logical database equivalence. This inspection-induced mismatch is documented in `operational-integrity.json`; I did not repair or remove it. It is not worker evidence. Worker and scientific conclusions rely on the original capture manifest and stop receipt, not on the changed operational annex state. Coordinator-preserved inputs, annex objects and the post-stop replay were excluded from worker-practice credit.

This assessment used the frozen checklist 0.3.1, assessment runner/environment identified by the supplied version file, and the supplied scientific guidance. Scientific adequacy, reported hypothesis conclusion, STAMPED item attainment, and replay measurement are separate judgments; no overall score is assigned.
