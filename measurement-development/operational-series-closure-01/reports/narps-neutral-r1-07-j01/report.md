# Independent assessment

Capture: SHA-256 `a870dc3c816f624dcd1ecd9e513fe56b76cf182e109a2f95963749235a4df8d7`; captured HEAD `d857ab1302d13cb660a7a044af07141f44bfa9ba`. Canonical-capture paths below identify the original evidence. The operational copy matched all 1,140 captured workspace entries by file bytes, modes and retained link targets. Inspection changed `.git/annex/keysdb/db` (captured SHA-256 `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca`, operational SHA-256 `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`) and created regular-file sidecars `db-shm` (32,768 bytes; SHA-256 `fd4c9fda9cd3f9ae7c962b0ddf37232294d55580e1aa165aa06129b8549389eb`) and `db-wal` (0 bytes; SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). These three changes fall within the operational-metadata exception; this does not establish logical database equivalence. The launcher verified the canonical capture before and after assessment.

## Scientific assessment

Scientific adequacy: qualified.

We found no support for a positive gain effect in vmPFC in the equal-indifference group under whole-brain familywise correction.

The report supports that qualified conclusion. It analyzes the 54 prespecified equal-indifference participants as independent observations, checks exact IDs and map geometry/support, and uses a one-sided whole-brain maximum-t sign-flip procedure (9,999 permutations, α=.05) on a brain mask aligned to MNI152NLin2009cAsym. A stated midline anatomical vmPFC box is descriptive; inference remains whole-brain corrected. No voxel in that box survives correction (peak max-T FWE p=.7742), while corrected positive peaks are posterior (max-T FWE p=.0006), outside the vmPFC definition. The ROI mean is −0.00261 COPE (95% t interval −0.02195 to 0.01673; uncorrected one-sided p=.606), so the result is absence of support, not evidence of exactly no effect.

The inference is conditional on the supplied AO86 participant COPEs, whose gain regressor was mean-centered and variance-normalized; its coefficients are not response change per currency unit. The report accurately notes absent participant variance maps and limits from the upstream model. A one-sample random-effects t test with sign flips is defensible under participant-level exchangeability/symmetry, and the permutation maximum controls whole-brain familywise error. The shared finite/nonzero-support mask excludes 5.2% of the template brain mask; the report discloses that this can discard genuine zeros. The analysis summary records an independent SciPy spot check of the peak t/raw p and ten permutation maxima. These limitations qualify generalization and calibration but do not materially undermine the stated absence of corrected vmPFC support.

Evidence: canonical capture `content/workspace/scientific-report.md` (SHA-256 `9573bd34e4db368eb719e949095019e17dcaf345ab6d8ce5d442bab0378384d0`); `content/workspace/research-protocol.md` (`fd82723ae27072a2dc5c3077756192457bcbc11e9b9a80eb378c33af0a9541c3`); `content/workspace/input/upstream-methods.md` (`508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`); `content/workspace/results/primary_v2_template_mask/summary.json` (`81e50cce17229e0eed5a518b845355616a167eec507e5b8696a4474d8d093488`); `content/workspace/results/primary_v2_template_mask/input_qc.csv` (`ee9999f5b11a29488ec5029deae3a436347d7a343d9607f186de927149d01f94`); `content/workspace/results/primary_v2_template_mask/whole_brain_fwe_voxels.csv` (`3b4222a0be521be6917d17de3105681f52f021fab6fefae1984441545637be99`). Figures are `content/workspace/figures/primary_v2_template_mask/group_t_map.png` and `vmPFC_participant_effects.png`.

Reported outcome and adequacy are separate: the report says there is no support for the positive vmPFC hypothesis; this assessment rates the reasoning supporting that report as qualified.

## STAMPED evidence and item judgments

The probe sweep is retained in `probes.json`. It evaluated 58 tracked paths and therefore missed substantive untracked worker-stop content. I manually considered the complete stopped workspace, including README, analysis, results, figures and external template files. This changes probe-only results for must/007, must/008 and should/003. Evidence below identifies the complete original capture; operational Git observations are explicitly described as observations and are not worker-produced artifacts.

| Item | Verdict | Evidence and reason |
|---|---|---|
| must/001 | met | All workspace materials reside under `content/workspace/`, including `README.md` and `analysis/analyze.py`. |
| must/002 | met | `input/data/` carries 54 retained annex links into workspace-local `.git/annex/objects`; `analysis/analyze.py` resolves inputs relative to the project root. |
| must/003 | unmet | `README.md` names Python packages but no environment or submodule supplies them; no environment specification appears in the complete capture inventory. |
| must/004 | unmet | At worker stop, the captured HEAD is `d857ab…f44bfa9ba`; code, report, README, results and figures are untracked in the operational copy's Git status. The complete stop receipt records the whole workspace; later coordinator retention is not worker credit. |
| must/005 | met | 54 participant-map pointers are tracked through git-annex; corresponding local annex content is captured. |
| must/006 | unmet | `results/primary_v2_template_mask/summary.json` records package versions and a command, but no exact environment specification/lock links those actions to a reproducible environment. |
| must/007 | partial | `README.md` gives usage and dependencies, but no installation procedure; its run command depends on an absolute interpreter path. |
| must/008 | met | `README.md` identifies `analysis/analyze.py` as the starting entrypoint and the generated output locations. |
| must/009 | unmet | `README.md` uses `/Users/johnlee/.../python`, a host-specific absolute path, despite project-relative paths in the analysis script. |
| must/010 | unmet | Dependencies are named but not pinned/provided in an environment specification. |
| must/011 | unmet | The README relies on a prepared host interpreter path/environment and does not state a portable host setup or system requirements. |
| must/012 | met | `README.md` explicitly lists Python 3.13.16 and NumPy, SciPy, pandas, NiBabel, Matplotlib and Nilearn. |
| must/013 | unmet | No environment specification is in the captured project alongside code and data. |
| must/014 | unmet | No dependency-update process or tracked environment changes are documented. |
| must/015 | unmet | No frozen environment specification is included; package version strings alone do not reproduce dependency resolution. |
| must/016 | unmet | No worker-published environment artifact/specification is evidenced at stop. |
| must/017 | unmet | README refers to a supplied prepared environment but does not explain how a recipient obtains it. |
| should/001 | partial | Git and git-annex cover seed materials and large inputs, but the analysis and generated research products are untracked at stop. |
| should/002 | unmet | No recurring CI or equivalent repeated workflow testing is evidenced; a retained pilot/method revision is not regular testing. |
| should/003 | partial | `input/`, `analysis/`, `results/`, `figures/`, and `external/` separate several kinds of material, but no environment module is supplied. |
| should/009 | not-applicable | The source inventory identifies public NARPS/OpenNeuro/NeuroVault inputs; no restricted dataset or software is declared. |
| should/004 | not-checked | No evidence that the workflow was tested in a fresh container, batch job, VM or cloud environment. |
| should/005 | not-checked | No disposable per-run environment is documented. |
| should/006 | unmet | No exact environment specification exists to reconstitute and test. |
| should/007 | unmet | No environment artifact is archived in the project. |
| should/008 | unmet | No process for updating and tracking environment specifications is documented. |
| may/001 | not-applicable | No independently maintained project component requires submodule composition; the data are annexed and runtime packages are dependencies. |
| may/002 | met | `README.md` and `research-protocol.md` describe the input, analysis, outputs and their relationship. |
| may/003 | partial | Inputs, code, derived results and figures have separate directories, but there is no independently versioned environment or documented independent-update contract. |
| may/004 | not-applicable | The delivered analysis is a single project; no component-composition mechanism is needed or documented. |
| may/005 | met | README links the report/protocol and names the script and outputs, providing a usable navigation path. |

Citations for the table (all paths relative to the canonical capture with SHA-256 `a870dc3c816f624dcd1ecd9e513fe56b76cf182e109a2f95963749235a4df8d7`): `content/workspace/README.md` (`b3962989dd4f90de42176285182bf88cf9ea6dc72698fe28237d5de2b872f97e`); `content/workspace/analysis/analyze.py` (`a881abeea818018c57b767504d18472867da80fac8b13dd8a93d34d2a457dde2`); `content/workspace/input/sources.json` (`919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`); `content/workspace/research-protocol.md` (`fd82723ae27072a2dc5c3077756192457bcbc11e9b9a80eb378c33af0a9541c3`). Inventory and stop-state context are the canonical manifest and supplied worker-stop receipt (SHA-256 `f5893d27e5a793fefd9e6f206399753c64f3efc45f362fb0d28b0f9b5ceac95d`). The README and scientific artifacts exist in the complete capture even though not in the captured HEAD.

## Attribution, access and replay

The worker-stop receipt is complete with no recorded omissions/errors, lists 58 supplied seed identities, and identifies the original captured HEAD. The full stop snapshot contains the later analysis, report, figures and results as untracked worker-stop content; coordinator capture metadata preserves that state. The captured Git commit message (`content/workspace/.git/COMMIT_EDITMSG`, SHA-256 `39c62105f6398577b19389a4b5b17fe00d9282eabe1e0a00baac3a1b801a7cfa`) includes a `Co-Authored-By: Codex Desktop` trailer. This is recorded as assistance exposure only and was not used to judge scientific or STAMPED attainment. The worker-stop receipt does not establish worker publication, environment capture, or an authorized project-sharing route. The operational `git remote -v` observation returned no remote; there is no intended recipient route or host to test. The NeuroVault/OpenNeuro URLs in `input/sources.json` identify scientific source inputs, not a route for obtaining the worker's complete analysis object. Coordinator delivery to the assessor is not treated as worker sharing.

Replay was not checked. The documented candidate entrypoint is `python analysis/analyze.py`; README instead invokes an absolute interpreter outside the project and names packages without a lock/specification. Following that external path or substituting the assessor/host environment would violate the supplied replay constraints. No replay command was launched and no outputs are claimed as replay evidence. Had a supported environment been available, identifiable generated outputs would include the files under `results/primary_v2_template_mask/` and `figures/primary_v2_template_mask/`; these shipped outputs were assessed only as preexisting evidence. No scientific-input retrieval or target modification was performed.

## Measurement availability

Scientific adequacy is qualified on available report, code and results. STAMPED item verdicts are based on the full captured stopped workspace, with probe coverage limits noted above. Replay and worker access-route checks are unavailable because no supported project route or reproducible in-project environment was supplied. No overall score is assigned.
