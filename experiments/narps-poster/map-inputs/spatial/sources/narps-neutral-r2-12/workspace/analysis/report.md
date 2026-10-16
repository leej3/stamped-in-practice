# Potential gains and brain activity

## Conclusion

In the equal-indifference group, these maps do not provide whole-brain-corrected evidence that the gain effect is positive in vmPFC. The mean vmPFC estimate was close to zero, and no vmPFC voxel survived the required whole-brain correction. This is a lack of support for the prespecified positive vmPFC hypothesis, not evidence that the true effect is exactly zero.

## Data and analysis

We analyzed the 54 AO86 participant-level gain contrast parameter estimates supplied for the complete equal-indifference cohort. The original NARPS hypothesis predicts a positive gain effect in vmPFC and instructs teams to report whole-brain analyses rather than relying on an ROI-only test ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

All 54 participant IDs matched the cohort table. Every map passed its manifest byte-count and SHA-256 checks; all maps had finite data and identical dimensions and affines. The common coverage mask contained voxels nonzero in all 54 maps (198,029 voxels). No participant was excluded. The cohort's mean age was 26.1 years (SD 3.0; 30 women, 24 men).

We tested the positive mean effect voxelwise with a one-sample sign-flip permutation test (10,000 draws; seed 20261016). For each draw, participant maps were independently multiplied by +1 or -1, and the largest positive studentized statistic in the common brain mask was recorded. The 95th percentile of this maximum-statistic null distribution gave a whole-brain family-wise error (FWE) threshold of *t* = 5.38. This provides voxelwise whole-brain FWE control for the positive-direction hypothesis, under a symmetric participant-level null.

The analysis used Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, NiBabel 5.4.2, Nilearn 0.14.1, pandas 3.0.6, and Matplotlib 3.11.2.

For anatomical localization and descriptive effect estimation only, vmPFC was operationalized as Harvard–Oxford cortical atlas Frontal Medial and Subcallosal Cortex plus the medial part (|x| ≤ 10 mm) of Frontal Orbital Cortex, intersected with the common mask. The atlas and its region labels are described in [FSL documentation](https://fsl.fmrib.ox.ac.uk/fsl/docs/other/atlas_xml.html). This broad atlas composite is an explicit approximation of vmPFC; it was not used to restrict the primary test or to claim small-volume-corrected significance.

## Results

There were 24 positive voxels across the brain above the whole-brain FWE threshold. They formed three small clusters in the Occipital Pole, outside the vmPFC hypothesis. The strongest peak was at MNI (−26, −102, −3.6) mm (*t* = 6.62, FWE *p* = .0006). These unexpected locations do not support the vmPFC hypothesis and should not be given a gain-valuation interpretation based on this analysis.

The anatomical vmPFC composite contained 1,425 voxels. Its equal-weight group mean cope was 0.00265 (between-participant SD 0.089; 95% *t* interval −0.0217 to 0.0270; one-sided uncorrected *p* = .414). The largest vmPFC voxel statistic was *t* = 4.19 at (−2, 24, −18) mm, with whole-brain FWE *p* = .780; no vmPFC voxels survived correction. The uncorrected ROI summary is descriptive and does not replace the whole-brain test. Leaving out one participant at a time moved the ROI mean between −0.0022 and 0.0062, showing that even the small positive mean's sign was not fully stable.

![Participant effects in the anatomical vmPFC composite](figures/vmPFC_participant_effects.png)

![Positive whole-brain clusters after maximum-t family-wise correction](figures/whole_brain_fwe_glass.png)

![vmPFC reference slices showing no corrected cluster](figures/vmPFC_localization.png)

## Interpretation and limitations

The maps are unthresholded participant contrast parameter estimates, not z or t statistics. Their gain modulator was mean-centered and variance-normalized within participant before HRF convolution. Thus, a positive cope reflects greater modeled BOLD response with increasing relative gain in that participant's specified model; it is not a slope per monetary unit. In this group the potential-gain range was twice the potential-loss range, but the supplied normalized estimates do not quantify response change per dollar or permit direct calibration of that range difference.

The gain and loss effects came from separate upstream models. The gain estimate is conditional on that modeling choice and on the other regressors in the fixed participant model; it is not a gain coefficient jointly adjusted for loss. Because participant variance maps were not supplied, the group test gives each participant cope equal weight rather than weighting by first-level precision. The original upstream models and choices were not re-estimated here.

No vmPFC voxel passing whole-brain correction means this analysis did not establish a reliable positive vmPFC effect at the chosen error rate. It does not establish a null effect, rule out smaller effects, or show that vmPFC is unresponsive to monetary value. The interval remains compatible with both small negative and small positive average copes, and no smallest scientifically meaningful effect was specified for an equivalence test. The anatomical boundary of vmPFC is also not unique; the reported atlas composite is a transparent approximation, while whole-brain inference remains primary.

## Reproducibility

Run from the workspace root with the supplied environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py
```

The script records input-integrity checks, creates the statistic and corrected-p maps, participant ROI estimates, permutation maxima, cluster summary, and figures. Main outputs are in `analysis/results/`; figures are in `analysis/figures/`. Results are also saved in machine-readable form in `analysis/results/results.json`.
