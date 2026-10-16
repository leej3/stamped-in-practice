# Potential gains and brain activity

## Finding

The supplied gain-effect maps do **not support a positive vmPFC response** in the NARPS equal-indifference group under whole-brain family-wise error (FWE) control. No positive FWE-significant voxel overlapped the independently defined vmPFC proxy. The across-participant mean in that proxy was small and positive (0.0058 contrast-estimate units; 95% t interval −0.0123 to 0.0239; n=54). A supplementary, uncorrected one-sided ROI test was also not significant (t(53)=0.64, p=.262); it is descriptive and does not determine the hypothesis decision.

Across 186,400 brain voxels, positive whole-brain max-t sign-flip inference found 23 significant voxels in three small posterior occipital clusters (26-neighbor connected; peak coordinates and values in [`cluster_summary.tsv`](results/cluster_summary.tsv)). The highest peak was t=6.62 at MNI x=−26, y=−102, z=−3.6 mm (FWE p=.0006). These sites are outside the vmPFC proxy, so they do not support the stated regional hypothesis.

![Participant estimates averaged within the vmPFC proxy, with their group mean and 95% t interval.](results/figures/roi_participant_effects.png)

![Observed maximum t against the sign-flip null distribution used for whole-brain FWE correction.](results/figures/whole_brain_fwe.png)

![Descriptive unthresholded group mean gain contrast estimates at selected axial levels.](results/figures/mean_effect_slices.png)

## Analysis

The sample comprised all 54 equal-indifference participants. No participant was excluded: every participant ID matched one supplied map, all file SHA256 checksums matched `input/sources.json`, maps shared the same 97×115×81 grid and affine, and no map contained nonfinite values. Exact zeros marked no map support. The analysis used the intersection of all 54 map supports with an independent MNI152 brain mask, retaining 186,400 of 196,120 brain-mask voxels; the other 9,720 voxels lacked support in at least one map. Another 11,629 all-supported voxels fell outside the brain mask. Age and gender were not used as covariates.

At each voxel, the group estimate was the unweighted one-sample mean and t statistic of the 54 participant contrast estimates. Positive directional inference used 9,999 random participant sign flips plus the observed arrangement and the maximum t statistic over the complete analysis mask (one-sided voxel-level FWE, α=.05; seed 20261016). The observed whole-brain maximum was t=6.62 (global max-t p=.0006); the 95th percentile of the null maximum was 5.37. The corrected map had zero significant voxels in the vmPFC proxy and 23 significant voxels overall. The ROI estimate and its interval summarize participant-level effects averaged over the 1,052 common-support ROI voxels; SciPy's one-sample t test independently reproduced the ROI t statistic, and sampled voxelwise observed and sign-flipped t statistics were also cross-checked against SciPy.

The vmPFC proxy was defined before inspecting effects from the Harvard–Oxford cortical max-probability atlas (25% threshold): Subcallosal Cortex plus Frontal Orbital Cortex within |x|≤20 mm, intersected with the analysis mask (1,052 voxels). This is an operational anatomical proxy, not a universally agreed vmPFC boundary; the atlas does not label vmPFC directly. The support decision required a positive whole-brain FWE-significant voxel overlapping this proxy, consistent with the original NARPS request for whole-brain-corrected decisions and its directional Hypothesis 1. See the [original NARPS instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) and [Nilearn Harvard–Oxford atlas documentation](https://nilearn.github.io/stable/modules/generated/nilearn.datasets.fetch_atlas_harvard_oxford.html).

## Interpretation and limits

This is a lack of corrected support, not evidence that vmPFC has no gain response. The ROI interval includes zero and remains compatible with modest effects in either direction; no equivalence bound was specified. The estimate is on the upstream contrast scale, not a change in BOLD signal per currency unit: the gain modulator was mean-centered and variance-normalized before HRF convolution. It is conditional on the supplied participant model, which modeled response-time durations and response choice separately, and fit gain and loss in separate models. The task's gain range was twice its loss range, but this analysis does not compare gain and loss effects.

Only participant contrast estimates were supplied; participant variance maps and an executable upstream pipeline were not. The unweighted group t model therefore cannot account for differences in precision among participant estimates as a variance-weighted mixed-effects model could. The sign-flip test additionally assumes participant effects are sign-symmetric under the zero-mean null. The small significant occipital clusters are corrected voxelwise discoveries but are not a priori support for vmPFC and should be treated cautiously. These results apply to the supplied cohort and fixed upstream model, not to causation or a general statement about monetary value processing.

Methods, run instructions and machine-readable results are in [`protocol.md`](protocol.md), [`README.md`](README.md), [`analysis/run_analysis.py`](analysis/run_analysis.py), and `results/`.
