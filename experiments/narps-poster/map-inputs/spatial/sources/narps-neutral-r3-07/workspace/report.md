# Potential gains and brain activity

## Result

**The supplied maps do not support a greater vmPFC response with increasing potential gain in the equal-indifference group.** Across participants, the mean gain-effect estimate in the coordinate-defined vmPFC region was slightly below zero (mean cope = −0.0042; 95% CI −0.0217 to 0.0133; one-sided *p* = .685). None of its 2,730 voxels survived whole-brain family-wise error (FWE) correction. The strongest voxel in that region had *t* = 2.83 and max-*t* FWE *p* = 1.00.

The whole-brain test did find a small positive focus outside vmPFC (peak MNI [−26, −102, −3.6], *t*(53) = 6.62, max-*t* FWE *p* = .0006; 24 FWE-significant voxels). This finding does not establish the specific vmPFC hypothesis. The NARPS instructions call for a whole-brain-corrected decision for each stated hypothesis; here the corrected focus is remote from the hypothesized region. [NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

![Whole-brain positive effect after max-t FWE correction](results/figures/whole_brain_fwe_vmPFC.png)

*Figure 1. Positive group t statistics exceeding the 95th percentile of the sign-flip maximum-t distribution (one-sided whole-brain FWE α = .05), displayed over an MNI template at the strongest whole-brain voxel. The corrected focus is posterior and outside the vmPFC region.*

![Participant-level vmPFC estimates](results/figures/vmPFC_participant_estimates.png)

*Figure 2. Mean cope within the vmPFC ROI for each participant. The diamond is the group mean and 95% one-sample t interval.*

## Analysis

All 54 participants in the supplied equal-indifference table were included. Image dimensions, affine, and finite values were checked; all 54 map SHA-256 checksums matched the supplied manifest. No participants were excluded. The common whole-brain analysis mask was the intersection of exact nonzero support across the maps (198,029 voxels; union 251,063), so every tested voxel had 54 observed estimates and outside-mask zeros were not treated as data.

At each voxel, I estimated the across-participant mean cope and tested it against zero with a one-sided one-sample *t* statistic (df = 53). Whole-brain multiplicity was controlled using 9,999 participant-level sign flips and the maximum positive *t* statistic over the mask, with a fixed random seed (20261016) and plus-one Monte Carlo *p*-values. This preserves spatial dependence between voxels and tests the directional prediction. The 95th percentile max-*t* threshold was 5.38.

The vmPFC check used an a priori, coordinate-defined approximation in the stated MNI space: x = −12 to 12, y = 25 to 55, z = −15 to 20 mm, intersected with the common mask. This anatomically centered ROI is reported as a participant-level mean so the 2,730 correlated voxels are not treated as independent observations. Its one-sample interval and *p*-value are descriptive ROI summaries; they do not replace the required whole-brain correction. The ROI is an operational approximation rather than a universally agreed anatomical boundary.

## Interpretation and limits

The result is a lack of support for this vmPFC prediction, not evidence that the true effect is exactly zero. The interval remains compatible with small negative or positive average cope effects, and this analysis was not an equivalence test. The uncorrected peak elsewhere is not evidence for vmPFC and could reflect a real effect outside the hypothesis or a false positive even after correction.

These inputs are participant contrast parameter estimates (cope maps), not *t* or *z* maps. AO86 mean-centered and variance-normalized the gain modulator before HRF convolution, so these coefficients are not response changes per unit of currency. The gain effect is conditional on the upstream model, including separate gain and loss models and response-time-duration regressors; it cannot resolve alternative upstream specifications or establish a causal neural mechanism. The potential gain range was twice the potential loss range, so the gain coefficient should not be read as a gain-versus-loss comparison.

Participant variance maps were not supplied. I therefore used an equal-weight random-effects one-sample model rather than a precision-weighted mixed-effects model. The group interval and sign-flip inference also rely on participant effects being independent and reasonably symmetric under the null. The common-support mask excludes voxels not covered in every map, including some map-edge coverage; this trades coverage for a constant sample size.

## Reproducibility

- Run: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py`
- Analysis code: [analysis/run_analysis.py](analysis/run_analysis.py)
- Machine-readable summary: [results/summary.json](results/summary.json)
- Map QC and checksums: [results/map_qc.tsv](results/map_qc.tsv)
- Participant vmPFC estimates: [results/vmPFC_participant_estimates.tsv](results/vmPFC_participant_estimates.tsv)
- Group outputs: `results/group_mean_cope.nii.gz`, `results/group_t_one_sided.nii.gz`, `results/group_p_fwe_maxT.nii.gz`, and `results/group_sig_fwe05.nii.gz`.

The analysis used Python 3.13, NumPy 2.5.4, SciPy 1.18.1, NiBabel 5.4.2, and Nilearn 0.14.1. The original instruction PDF host returned a gateway timeout during retrieval; the report uses the supplied official URL and its indexed study instructions.
