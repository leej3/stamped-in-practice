# Potential gain effects in the equal-indifference group

## Question and conclusion

NARPS Hypothesis 1 predicted a positive gain-related response in vmPFC for the equal-indifference group. **This analysis does not support that prediction:** no positive voxel in the operational vmPFC region survived whole-brain family-wise error (FWE) correction. The strongest vmPFC-proxy voxel had *t*(53) = 4.19 but whole-brain max-*T* corrected *p* = .780. The average participant-level effect over the proxy was −0.0048 cope units (95% *t* interval −0.0243 to 0.0147).

There were 24 positive voxels surviving the whole-brain test elsewhere (peak *t*(53) = 6.62 at MNI [−26, −102, −3.6], corrected *p* = .0006). This posterior finding does not establish the hypothesized vmPFC effect and should be interpreted cautiously as a result outside the target region.

![Sagittal group maps through the midline vmPFC and the whole-brain-corrected peak. The black outline marks the anatomical proxy.](../figures/group_maps.png)

*Figure 1. Mean gain cope and unthresholded one-sample *t* at x = 0, with the vmPFC proxy outlined; the corrected positive signal is shown at the posterior peak slice (x = −26).*

![Mean gain cope in the vmPFC anatomical proxy for each participant, with group mean and 95% t interval.](../figures/vmPFC_participant_means.png)

*Figure 2. Descriptive participant-level mean cope within the vmPFC proxy; this ROI summary is not the whole-brain-corrected hypothesis test.*

## Data and group analysis

The input was 54 AO86 participant gain-effect (cope) maps, one per equal-indifference participant. The maps were not in the workspace initially, so the 54 files listed in the supplied `input/sources.json` were retrieved from their NeuroVault links; each file's byte count and SHA-256 matched that manifest. No time-series scans were retrieved or analyzed. All 54 participants were retained; there were no exclusions. Images shared a 97 × 115 × 81 grid and affine, with 2 × 2 × 2.4 mm voxels, and contained only finite values. Group analysis used the intersection of the nonzero map supports (198,029 voxels; 78.9% of the union), so every tested voxel had an estimate from every participant. This is a complete-case coverage mask, not an independent anatomical brain mask; exact zero-valued estimates inside an individual map's field of view could be omitted by this rule.

At each included voxel, we estimated the mean cope and tested whether it was greater than zero using a one-sample, one-sided sign-flip permutation max-*T* test (9,999 random sign flips; seed 20261016). For each permutation the statistic was studentized, and the maximum positive *t* over the full tested mask provided the null distribution for whole-brain FWE correction. The 5% max-*T* threshold was *t* = 5.38. This gives a direct whole-brain corrected test for the positive direction specified by the original NARPS instructions, which request a binary decision from a whole-brain-corrected analysis ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). The sign-flip test assumes participant effects are exchangeable under sign changes (in particular, a symmetric zero-centered null).

The vmPFC boundary is not unique. To make the anatomical check explicit and independent of the observed map, we used an inclusive Harvard-Oxford cortical atlas proxy: Frontal Medial Cortex, Subcallosal Cortex, and Frontal Orbital Cortex (max-probability labels at 25%), resampled by nearest neighbor into the supplied MNI152NLin2009cAsym grid. The atlas labels and MNI-space alignment follow the [FSL Harvard-Oxford atlas documentation](https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html). This broad composite is an approximate vmPFC definition; it is used to locate the target for interpretation, not as a smaller search volume for significance. The hypothesis decision remains based on whole-brain-corrected results. None of the proxy's 3,719 common-support voxels passed that correction.

## Interpretation and limits

These are first-level gain-modulator parameter estimates, not standardized *t*/*z* statistics and not raw BOLD signal changes. The upstream gain regressor was mean-centered and variance-normalized before HRF convolution, so cope magnitude is not change in response per currency unit. The upstream model also used response-time durations, separate gain and loss models, and response-choice modulators; the gain effect is conditional on those fixed choices. The supplied participant variance maps and executable upstream model were unavailable, so the group analysis cannot weight participants by first-level precision or audit/re-estimate those models. The unweighted one-sample model instead treats each participant cope map as an estimate with equal group-level weight.

The near-zero vmPFC average and its interval show no clear group-average positive effect under this operational definition. Lack of corrected support is not proof that the true effect is exactly zero, that no participant shows a positive response, or that other vmPFC boundaries/modeling choices would give the same result. It means this group analysis does not provide the required whole-brain-corrected evidence for the predicted positive response. The posterior corrected cluster does not change that conclusion.

## Reproducibility files

- Analysis script: [`scripts/analyze.py`](../scripts/analyze.py)
- Machine-readable results and input checks: [`results/summary.json`](../results/summary.json), [`results/input_quality_checks.csv`](../results/input_quality_checks.csv)
- Unthresholded group mean, *t*, corrected-*p*, and common-support maps: `results/group_mean_cope.nii.gz`, `results/group_t_unthresholded.nii.gz`, `results/group_p_fwe_maxT.nii.gz`, `results/group_common_support_mask.nii.gz`
- Anatomical proxy and participant summaries: `results/vmPFC_anatomical_proxy_mask.nii.gz`, [`results/vmPFC_proxy_participant_means.csv`](../results/vmPFC_proxy_participant_means.csv)
- Figures: [group maps](../figures/group_maps.png), [participant ROI summaries](../figures/vmPFC_participant_means.png)
- Run with the prepared interpreter: `python scripts/analyze.py` (requires NumPy, SciPy, pandas, Matplotlib, NiBabel, and Nilearn).
