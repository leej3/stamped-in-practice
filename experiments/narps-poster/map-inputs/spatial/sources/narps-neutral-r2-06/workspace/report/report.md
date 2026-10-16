# Potential gains and vmPFC response in the NARPS equal-indifference group

## Result
The supplied gain-effect maps do **not** support a positive vmPFC response to increasing potential gain. Across 54 participants, the mean effect in the prespecified bilateral medial prefrontal ROI was −0.0037 (95% t interval −0.0230 to 0.0156; one-sided t(53) p = .650, descriptive). No vmPFC voxel survived positive whole-brain family-wise correction. The interval spans small negative and positive effects, so this is a lack of evidence for the hypothesized increase, not evidence that the true response is exactly zero.

Whole-brain testing did identify 11 positive voxels after Bonferroni correction (198,029 voxels; strongest t(53) = 6.62, corrected p = .00184). They were in posterior occipital locations (y = −94 to −102 mm), outside vmPFC. This shows that the maps contain a corrected positive group signal somewhere, but does not support the target hypothesis.

## Analysis
The analysis unit was the participant (n = 54). At each voxel with shared valid coverage, I estimated the mean participant effect and tested it against zero with a one-sample t model (df = 53), using the directional positive alternative. The [original NARPS Hypothesis 1 instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) require whole-brain correction. The participant-level estimates supply between-person variability for a random-effects group test; because participant variance maps were not supplied, the analysis is unweighted and cannot model within-person precision. One-sided p values were Bonferroni-adjusted over the full analyzed voxel set, controlling whole-brain family-wise error at .05.

I operationalized vmPFC as MNI x = −12 to 12, y = 25 to 60, z = −10 to 10 mm, covering bilateral medial orbitofrontal and subgenual medial prefrontal territory. This anatomical box was set without reference to the observed effect. Its mean and interval are descriptive; whole-brain correction, rather than an ROI-only test, determines support.

All 54 metadata IDs matched one map each, every image had matching 97 × 115 × 81 geometry and affine, all values were finite, and each map SHA256 matched the supplied `sources.json`. There were no exclusions. The common analysis domain was the intersection of nonzero map support (198,029 voxels), treating zeros outside a participant's modeled support as unavailable rather than as measured zero. The ROI contained 1,872 common-support voxels. Participant ROI means varied in both directions (figure 2).

## Meaning and limits
These are AO86 participant contrast parameter estimates, averaged over four runs, not standardized statistics or group maps. Upstream gain modulation was mean-centered and variance-normalized before HRF convolution. Consequently neither the ROI mean nor voxelwise effects mean a BOLD change per currency unit; they quantify the supplied modeled gain contrast. The gain effect was estimated in a separate gain model from loss, so this is not a matched-unit gain-versus-loss comparison. In this group, the potential-gain range was twice the loss range. Response-trial duration, choice regressors, motion, flagged volumes and drift were included upstream according to the supplied methods description.

A nonsignificant vmPFC result means these data and this analysis did not establish a positive group response after the required whole-brain correction. It does not establish absence of a biologically meaningful effect: the ROI interval still includes positive values, and no equivalence margin was specified. Inference is also limited by the fixed upstream model, unavailable participant variance maps, the parametric one-sample t assumptions, and the chosen operational ROI bounds. Bonferroni correction is conservative and spatially ignores dependence, but controls family-wise error without relying on cluster-forming choices.

## Figures

![Mean modeled gain effect across participants; cyan outline marks the vmPFC ROI](../figures/group_mean_slices.png)

*Figure 1. Unthresholded group mean of the supplied modeled gain effects. The cyan outline marks the prespecified vmPFC bounds. Display is descriptive; do not infer significance from the colors.*

![Positive whole-brain voxels surviving Bonferroni correction](../figures/wholebrain_fwe_positive.png)

*Figure 2. Positive t statistics surviving whole-brain Bonferroni FWE at .05 (threshold t = 5.719). The surviving posterior voxels are outside the vmPFC outline.*

![Participant-level vmPFC ROI means](../figures/vmPFC_roi_distribution.png)

*Figure 3. Each point is one participant's average over shared vmPFC support; the red point and whisker show the group mean and 95% t interval.*

## Reproduction and supporting files
Run from the workspace root with the prepared common Python 3.13.16 environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/analyze.py
```

The script uses NumPy, SciPy, pandas, Matplotlib, NiBabel and Nilearn; versions and platform are recorded in `results/run_metadata.json`. Input identities and upstream source details are in `input/sources.json`.
