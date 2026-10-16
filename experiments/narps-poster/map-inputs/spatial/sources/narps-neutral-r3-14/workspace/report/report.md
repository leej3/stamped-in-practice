# Potential monetary gain and brain activity

## Result

**No whole-brain-corrected support was found for a positive gain effect in vmPFC.** In the 54 equal-indifference participants, the strongest voxel within a fixed vmPFC coordinate mask (MNI x = −15 to 15, y = 20 to 60, z = −20 to 10 mm) had a positive group estimate (0.232 map units; *t*(53) = 4.19; one-sided uncorrected *p* = .000053), but its whole-brain max-*t* family-wise error corrected *p* was .780. The participant-level mean across the vmPFC mask was −0.0012 map units (SE = 0.0088; 95% CI [−0.0188, 0.0164]); its one-sided ROI-average *p* = .555. These estimates do not indicate a positive vmPFC response in this group under the supplied model.

The whole-brain test did identify 24 positive voxels at max-*t* FWE *p* < .05, in three small connected clusters outside vmPFC, centered near posterior MNI coordinates (largest cluster: peak −26, −102, −3.6 mm). Thus the group maps contain positive gain-related effects elsewhere, but those do not support the specified vmPFC hypothesis.

## Analysis

The unit of analysis was the participant. We fit an unweighted one-sample group model at each voxel, testing whether the mean supplied gain-effect estimate exceeded zero. The 54 maps share a 2 × 2 × 2.4 mm MNI152NLin2009cAsym grid. The inference domain was the intersection of nonzero map coverage (198,029 voxels); zero-valued background outside this mask was not treated as measured data. We retained all 54 matched participants and excluded none.

For whole-brain family-wise error control, we used 9,999 participant-level random sign flips and the maximum positive *t* statistic across all covered voxels on each flip (seed 20261016; one-sided α = .05). The 95th percentile of the maximum-*t* null was 5.38. This approach controls the search across the whole covered brain while preserving spatial dependence; it assumes independent participants and sign-symmetric errors under the null. Monte Carlo corrected *p* values have resolution 0.0001. The fixed vmPFC coordinate box is a coarse anatomical approximation, used to locate and summarize vmPFC effects; it is not an atlas-defined parcel. The final hypothesis decision remains based on whole-brain correction.

## Checks, uncertainty, and scope

All 54 source SHA256 values matched `input/sources.json`; participant IDs matched metadata one-to-one; maps were finite and had matching dimensions and affines. We inspected map coverage and participant summaries, and selected voxelwise *t* and one-sided *p* values agreed with independent SciPy one-sample tests. The ROI-average test was separately computed from one mean per participant. Figures were rendered and visually inspected.

The participant estimates are not standardized statistics or effects per unit of currency. Upstream, the gain regressor was mean-centered and variance-normalized before HRF convolution, response trials were modeled with response-time durations and separate response-choice and gain modulators, and gain/loss effects came from separate models. The task used a potential-gain range twice the potential-loss range. Those choices are fixed here and constrain what the group estimate means; separate gain and loss models and the normalized gain regressor mean this analysis does not compare gain sensitivity with loss sensitivity or estimate a slope per currency unit. Participant variance maps are unavailable, so the analysis cannot weight individuals by first-level precision or use a variance-aware mixed-effects model. The unweighted one-sample test treats participant estimates as the inputs and cannot propagate uncertainty from each first-level fit.

A failure to reach whole-brain-corrected vmPFC significance means that this analysis did not detect the hypothesized positive group mean at its chosen error threshold. It does not demonstrate equivalence, prove no vmPFC effect exists, or rule out effects that are smaller or less precisely estimated. The coordinate mask is approximate, and the result is conditional on the supplied AO86 estimates rather than a reanalysis of the time series. No preprocessing or individual modeling was repeated.

## Artifacts

- Protocol: [`analysis/protocol.md`](../analysis/protocol.md)
- Executable analysis: [`analysis/run_analysis.py`](../analysis/run_analysis.py)
- Reproduction recipe: [`README.md`](../README.md), [`requirements.txt`](../requirements.txt)
- QC and numeric summary: [`results/participant_qc.tsv`](../results/participant_qc.tsv), [`results/summary.json`](../results/summary.json)
- Whole-brain outputs: [`results/group_mean.nii.gz`](../results/group_mean.nii.gz), [`results/group_t.nii.gz`](../results/group_t.nii.gz), [`results/fwer_p.nii.gz`](../results/fwer_p.nii.gz), [`results/max_t_null.tsv`](../results/max_t_null.tsv)
- Figures: [`figures/group_effects.png`](../figures/group_effects.png), [`figures/max_t_null.png`](../figures/max_t_null.png)
