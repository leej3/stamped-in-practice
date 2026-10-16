# Potential gains and brain activity in the equal-indifference group

## Result

The supplied data do **not support a positive vmPFC gain effect** at the required whole-brain corrected level. A positive whole-brain effect was detected, but all three corrected foci were in the Harvard–Oxford Occipital Pole label (23 voxels total), not vmPFC. The broad, independently specified vmPFC summary was close to zero (mean participant ROI estimate 0.0019; 95% CI −0.0200 to 0.0238 model units; descriptive one-sample *t*(53)=0.18, *p*=.86). The ROI result is descriptive; the confirmatory decision uses whole-brain correction.

The strongest corrected focus was at MNI (−26, −102, −3.6) mm (16 voxels; max-T FWE *p*=.0006). Two additional occipital foci were at (26, −98, −1.2) mm (2 voxels; *p*=.0124) and (30, −94, −8.4) mm (5 voxels; *p*=.0033). These posterior effects do not establish the stated vmPFC hypothesis.

![Whole-brain gain effect; cyan outlines mark positive whole-brain permutation-FWE voxels.](figures/whole_brain_t_and_fwe.png)

The vmPFC estimate is small relative to its participant-to-participant uncertainty:

![Participant vmPFC ROI estimates and group mean with a 95% confidence interval.](figures/vmPFC_roi_effects.png)

## Analysis

I analyzed all 54 equal-indifference participants with no exclusions (mean age 26.1 years, SD 3.0; 30 F, 24 M). Each input was a participant-level unthresholded contrast parameter estimate averaged across four runs, not a standardized statistic or group result. The one-sample group model tested whether mean gain-effect estimates were positive. Participant IDs matched the metadata; all 54 supplied SHA256 checksums matched; maps were finite and shared dimensions and affine. The analysis mask was the intersection of a standard MNI brain mask resampled to the supplied grid and voxels nonzero in at least 90% of participants (192,403 voxels; 2 × 2 × 2.4 mm grid).

For primary inference I used 10,000 participant-level sign flips with a one-sided maximum-statistic correction over the entire analysis mask. The statistic is the mean divided by its root-mean-square participant scale; this scale is invariant under sign flips, avoiding unstable near-zero sample variances in permuted maps. Each permutation assigned one sign to each participant’s *whole map*. The randomization test assumes independent participants and a symmetric zero-centered null. The smallest attainable Monte Carlo *p* is 0.0001. At α=.05, 23 voxels survived correction, all at the occipital pole. The visualized statistic map is thresholded at 2 for legibility; cyan marks the corrected voxels.

There is no unique anatomical boundary for vmPFC. For localization, I used Harvard–Oxford Frontal Medial, Subcallosal, Frontal Orbital, and anterior Cingulate labels, restricted to |x| ≤ 20, y ≥ 0, z ≤ 10 mm, then intersected with the analysis mask (2,524 voxels). This broad atlas-based ROI is only a descriptive summary; the original NARPS report noted the lack of a single anatomical vmPFC definition and used an anatomical/functional conjunction. The ROI does not replace or weaken the whole-brain corrected test.

## Interpretation and limits

The result means this analysis did not demonstrate that gain-related responses increase in vmPFC. It is not evidence that the effect is exactly zero: the ROI interval remains compatible with small positive or negative effects, and absence of a corrected focus can reflect limited precision or power. The detected occipital foci are outside the hypothesized region and should not be treated as confirmation.

The gain regressor was mean-centered and variance-normalized before HRF convolution. Thus the supplied coefficient is a response to the upstream standardized gain modulator, not a change in fMRI signal per currency unit. Response trials were modeled with response-time durations, and separate choice and gain modulators, nonresponse trials, motion, flagged volumes and drift terms were included. Gain and loss were modeled separately, so this effect is conditional on that model. The input maps alone cannot verify those upstream choices or recover trial-level effects. No participant variance maps were supplied, so the group model cannot use inverse-variance weights or fully propagate first-level estimation uncertainty. The inferential results therefore describe variability among these 54 participant estimates.

The atlas and brain mask were resampled from standard MNI152 resources to MNI152NLin2009cAsym; labels near boundaries are approximate. The ROI boundary is one transparent operational definition, not a definitive vmPFC parcellation. The gain range being twice the loss range motivates the gain hypothesis, but this gain-only analysis does not test gain-versus-loss range effects.

## Reproducibility files

- Analysis script: [`analyze.py`](analyze.py)
- Main results: [`results/summary.json`](results/summary.json), [`results/corrected_clusters.csv`](results/corrected_clusters.csv), [`results/vmPFC_roi_summary.json`](results/vmPFC_roi_summary.json)
- Participant summaries: [`results/participant_global_means.csv`](results/participant_global_means.csv), [`results/participant_vmPFC_means.csv`](results/participant_vmPFC_means.csv)
- Unthresholded NIfTI outputs: [`results/mean_effect.nii.gz`](results/mean_effect.nii.gz), [`results/rms_standardized_stat.nii.gz`](results/rms_standardized_stat.nii.gz), [`results/p_fwe_maxT.nii.gz`](results/p_fwe_maxT.nii.gz)
- Additional figures: [`figures/mean_gain_effect.png`](figures/mean_gain_effect.png), [`figures/participant_global_means.png`](figures/participant_global_means.png)

The analysis used the prepared Python environment with NumPy, SciPy, pandas, NiBabel, Matplotlib and Nilearn. Run from this directory with `python analyze.py`.

## Sources

- [NARPS instructions for analysis teams, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) (whole-brain corrected hypothesis decisions).
- [Botvinik-Nezer et al., 2020, *Variability in the analysis of a single neuroimaging dataset by many teams*](https://pmc.ncbi.nlm.nih.gov/articles/PMC7771346/) (NARPS methods and vmPFC localization discussion).
- Fixed input methods and provenance are documented in [`input/upstream-methods.md`](input/upstream-methods.md) and [`input/sources.json`](input/sources.json).
