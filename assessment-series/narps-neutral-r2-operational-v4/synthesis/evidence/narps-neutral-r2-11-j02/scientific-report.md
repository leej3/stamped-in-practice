# Independent assessment: NARPS Hypothesis 1

## Scope and evidence identity

This assessment concerns the complete worker stop-state capture identified by canonical manifest SHA-256 `51645420c0f50700227093660ac8e7859e8d228fc2325f59ebc2b32279f7584b`, with original captured HEAD `a724b670072a95a253e752be8336783858df768a`. Unless stated otherwise, citations below refer to capture-relative paths under `content/workspace/` in that capture. The operational copy was used for inspection; the supplied capture manifests report matching initial canonical and operational identities. `judge-target.json` gives no reference limits. No target mismatch was observed during inspection. The launcher performs its own exact pre/post verification.

The worker stop receipt reports a complete stop, no omissions, normal exit, and 58 supplied input identities. The analysis files and outputs were present in the stop inventory as untracked work (`git status`: `?? analysis/`, `?? figures/`, `?? report.md`, `?? results/`); they are part of the delivery but were not versioned at worker stop. The captured HEAD is only the supplied input scaffold. Any later coordinator preservation or repository activity is excluded from worker-practice credit. The stop receipt also records common prompt/resource seed hashes; that indicates exposure to supplied session resources, which is noted here and was not used as grading evidence.

## Scientific assessment

**Scientific adequacy: qualified.** The reported outcome is: “In the 54-person NARPS equal-indifference group, the supplied gain-effect estimates do **not** support a positive response in vmPFC.” (`report.md`, Results). That conclusion is supported as a statement of lack of corrected evidence in the supplied maps, with the qualifications below; it is not a claim that the underlying response is exactly zero.

The analysis uses all 54 participant-level contrast estimates, checks map/metadata ID agreement and uniqueness, dimensions, affine agreement and finite values, and excludes no participant (`analysis/run_analysis.py`; `results/summary.json`; `input/participants.tsv`). It applies a common nonzero-support mask intersected with a standard brain mask, and identifies bilateral AAL3 medial orbital frontal parcels as a reproducible vmPFC approximation. The parcel mean is −0.00779 estimate units (SE 0.01321; 95% t interval −0.03429 to 0.01870); no parcel voxel passes the reported whole-brain max-T threshold. The report correctly treats the ROI one-sided p=.72 as descriptive and does not mistake the significant posterior-edge whole-brain finding (MNI [−26, −102, −3.6]) for vmPFC evidence (`results/summary.json`, `figures/whole_brain_fwe.png`, `figures/vmPFC_roi_effect.png`, `figures/participant_effect_distribution.png`).

The one-sided participant-level sign-flip maximum-t procedure addresses whole-brain multiplicity under its stated symmetric, zero-centered exchangeability assumption and reports its 9,999 draws, seed, threshold, observed maximum, and global max-T p value. The report appropriately says that the family-wise claim is under the global null. This is a qualification: the nonzero-map support rule is an operational coverage assumption, sign symmetry is not independently verified, and max-T global-null calibration alone does not establish strong FWER under every possible partial-null configuration. These caveats temper voxelwise absence claims. They do not create evidence for the targeted positive effect: the ROI summary is negative, its interval spans zero, no ROI voxel meets the reported corrected threshold, and the report explicitly limits interpretation. Participant variance maps are absent, so the equal-weight group test cannot account for first-level precision. Upstream methods describe mean-centered, variance-normalized gain modulation and separate gain/loss models; hence coefficients are not per-currency-unit slopes and are conditional on AO86's fixed first-level analysis (`input/upstream-methods.md`).

The report includes numerical results, participant-level effects, four NIfTI group maps, a run log, and three figures. Its description of uncertainty and lack of support is appropriately cautious. No conclusion about causal effects or dollar scaling is justified. The result is conditional on the fixed supplied participant maps and does not compare gain against loss.

### Replay

Before replay, the declared entrypoint was `python analysis/run_analysis.py` from the delivery root. The selected generated outputs were `results/mean_effect.nii.gz`, `results/t_stat.nii.gz`, `results/p_uncorrected.nii.gz`, `results/fwe_significant.nii.gz`, `results/participant_vmPFC_effects.tsv`, `results/summary.json`, and the three PNGs under `figures/`. `input/` and `analysis/run_analysis.py` were protected. The comparison rule was exact image geometry plus numeric arrays/summary/table values at rtol 1e-6 (atol 1e-6); figure scientific content and labels, disregarding rendering metadata; and no credit for pre-existing shipped outputs.

The frozen helper copied the complete delivery and removed only those nine selected outputs. Its single attempt failed at import with `ModuleNotFoundError: No module named 'nibabel'`. There is no worker-supplied environment/dependency declaration; the report lists package versions but no installation or environment specification. Under the no-repair rule, replay is **not checked**. This is a missing replay prerequisite in the delivered research object, not scientific evidence against the shipped analysis and not a malfunction of the assessor. The failed command and stderr are retained in `replay.json`, `replay-workdir/replay.stderr`, and the replay command logs. No replay comparison was possible.

## Access and retrieval

The intended recipient is a researcher using the routes declared in `input/sources.json`. Required input coverage is the 54 AO86 participant maps, the equal-indifference cohort table, and the cited AO86 methods source. At worker stop, these source URLs were recorded, but there is no worker-published route for the worker's own report, code, figures, or results; their presence in the coordinator's retained capture does not establish worker sharing. No authentication condition was declared.

Read-only HEAD checks from this assessment host returned HTTP 200 for the NeuroVault collection, a representative participant map endpoint, and the pinned GitHub cohort-table URL; the pinned GitHub methods spreadsheet URL returned HTTP 404. The map test represents the declared NeuroVault media route and does not verify all 54 object URLs or the integrity of a complete fresh retrieval. The capture itself contains the methods summary at `input/upstream-methods.md`. Tested host scope is this assessment host and the four exact URLs recorded in `access-record.json`; no broader availability claim is made.

## STAMPED item judgments

The response JSON records item attainment separately from scientific adequacy and replay measurement availability. Probe output is retained in `probes.json`; probes were used as leads and corrected where they examined tracked Git state only rather than the complete stopped workspace. Evidence references below are in the canonical capture identified above.

| Item | Attainment | Evidence and reason |
|---|---|---|
| must/001 | met | All delivered components sit under the workspace root (`report.md`, `analysis/`, `input/`, `results/`, `figures/`). |
| must/002 | met | Maps and cohort/methods descriptions are included/referenced in `input/`; sources and URLs are recorded in `input/sources.json`. |
| must/003 | unmet | Analysis depends on external Python packages and remote Nilearn atlas/mask resources; no software package/submodule is included or linked inside the project. `analysis/run_analysis.py`, `input/sources.json`. |
| must/004 | unmet | Git exists, but the complete scientific code, report, figures, and results remained untracked at worker stop. Stop receipt plus `git status` over `content/workspace/`. |
| must/005 | met | 54 participant maps are Git-annex pointers and their annex content is captured; probe confirms 54 pointers. `input/data/` and annex dependencies. |
| must/006 | unmet | Run log and summary report selected versions but no exact environment specification is linked to the run. `results/run.log`, `results/summary.json`, `report.md`. |
| must/007 | unmet | No README with install/use instructions or Makefile is supplied. |
| must/008 | met | The report links to the clear analysis entrypoint `analysis/run_analysis.py`; it is present in the complete stop state. |
| must/009 | met | Script paths derive from `__file__` and are relative to the workspace; no host-specific paths are needed. `analysis/run_analysis.py`. |
| must/010 | unmet | No dependency/environment declaration accompanies the listed Python packages. `report.md`, `analysis/run_analysis.py`. |
| must/011 | unmet | Host/platform assumptions and external atlas/mask retrieval prerequisites are not documented. `report.md`, `analysis/run_analysis.py`. |
| must/012 | unmet | Software names/versions are listed, but no usable system/dependency requirements list or install route is supplied. `report.md`. |
| must/013 | unmet | No environment specification is present in the complete workspace, let alone tracked alongside code. |
| must/014 | unmet | No environment-update process is documented; no environment specification exists. |
| must/015 | unmet | No lockfile, container digest, or frozen package manifest specifies the run environment. |
| must/016 | unmet | No worker-accessible environment specification is supplied. |
| must/017 | unmet | No instructions explain how to obtain/use an environment specification. |
| should/001 | unmet | Git and annex manage the supplied scaffold and maps, but worker code, report, figures, and results are untracked at stop, so version control does not cover all components. |
| should/002 | not-checked | No repeated-testing record or recognized CI is present; one run does not establish regular testing. |
| should/003 | partial | Inputs, code, results, and figures occupy separate directories, but no environment module exists. |
| should/004 | not-checked | No worker record shows the pipeline tested in a fresh container/VM/batch host. Assessor replay is not worker practice. |
| should/005 | not-checked | No evidence shows executions create disposable isolated environments. |
| should/006 | unmet | No environment specification exists to be reconstituted and regularly tested. |
| should/007 | unmet | No environment artifacts are archived in the workspace. |
| should/008 | unmet | No environment update process is documented. |
| should/009 | not-applicable | No restricted data or software is identified in the supplied contents. |
| may/001 | not-applicable | No independently maintained project submodules/components are present; external runtime dependencies are separate evidence. |
| may/002 | partial | The report links input, code, results, and figures, but does not document reusable module relationships. |
| may/003 | partial | Input/code/output boundaries exist, but no declared interfaces support independent updates. |
| may/004 | not-applicable | No separately maintained project modules need composition. |
| may/005 | met | Report links and describes the input, script, summary, maps, participant table, log, and figures. `report.md`. |

## Integrity and attribution limits

The canonical and operational manifest hashes are identical at assessment start (`51645420c0f50700227093660ac8e7859e8d228fc2325f59ebc2b32279f7584b`). The captured HEAD is `a724b670072a95a253e752be8336783858df768a`, which is the input-materialization commit, not the worker's uncommitted scientific work. Probe and Git inspection was directed only at the operational copy with the launcher-supplied Git/annex settings preserved. No scientific or other non-metadata target files differed from the initial operational manifest in the post-inspection audit (`operational-integrity.json`). Git/annex inspection changed or created only the allowed regular files `.git/annex/keysdb/db`, `db-shm`, and `db-wal`; these are inspection-induced metadata, not worker evidence. Their logical database equivalence is not established. No mismatch affects the scientific files or reported conclusions. The launcher performs final exact integrity verification.

No overall score is assigned. The scientific adequacy category, reported hypothesis outcome, each checklist item, and replay availability are distinct judgments.
