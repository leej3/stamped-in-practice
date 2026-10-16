# Potential gains and brain activity

## Question and result

**Does the response increase with potential gain in vmPFC?** In the 54-person NARPS equal-indifference group, the available participant maps do not support a positive vmPFC gain effect under whole-brain family-wise error (FWE) correction. The mean estimate in the prespecified vmPFC mask was slightly below zero (mean = **−0.0036**, 95% CI **[−0.0227, 0.0156]**); **no vmPFC voxels** passed the directional whole-brain FWE test (α = .05). The interval includes zero and positive effects, so this is a lack of support, not evidence that the true response is exactly zero.

The primary test did identify 24 positive voxels elsewhere in the corrected whole-brain search; its peak was at MNI x = **−26**, y = **−102**, z = **−3.6** (t = **6.62**, max-t FWE p = **0.0006**). This posterior finding is outside vmPFC and does not support the stated regional hypothesis.

![Group mean effect and vmPFC whole-brain corrected result](figures/group_effect_and_fwe.png)

*Left: mean participant gain-effect estimate in the vmPFC-centered slices. Right: no voxel in these vmPFC slices passes the whole-brain directional FWE threshold. The analysis did find corrected positive voxels elsewhere, as noted above.*

![Participant vmPFC effects](figures/vmPFC_participant_effects.png)

*Each point is one participant’s spatial average within the vmPFC mask; shading is the t-based 95% confidence interval for the group mean. This is a descriptive summary, not a second inferential test.*

![Whole-brain max-t corrected positive effects](figures/whole_brain_fwe.png)

*The 24 positive voxels surviving whole-brain max-t correction are posterior and outside vmPFC.*

## Group analysis

I used an equal-weight one-sample random-effects model on each participant’s unthresholded gain-effect estimate, with a positive one-sided test. Group t statistics were compared against **10,000 participant-level sign-flip permutations**; for each permutation, the maximum positive t across the complete common-coverage brain mask was retained. This max-t procedure controls whole-brain FWE for the directional hypothesis. The resulting positive max-t threshold was t = **5.38**. The common mask contained **198,029** voxels (2.0 × 2.0 × 2.4 mm); all maps shared a grid and affine. The vmPFC search region was specified independently in MNI152NLin2009cAsym coordinates as x ∈ [−15, 15], y ∈ [25, 65], z ∈ [−25, 10] mm, covering bilateral medial ventral prefrontal and subgenual territory. The whole-brain test, rather than an uncorrected ROI-only test, determines support, consistent with the [original NARPS instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

All **54** cohort participants were included; no maps were excluded. The 54 maps had matching geometry and passed the SHA-256 checks in `input/sources.json`. Screening participant-level whole-brain and vmPFC summaries found no robust outlier beyond |robust z| = 3.5. No covariates were added to the group model.

## What the estimate means

These are AO86 participant contrast parameter estimates, not t or z statistics and not group results. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution. Thus a positive group estimate indicates a greater modeled response for larger gains within that upstream parameterization; it **cannot be interpreted as BOLD change per dollar**. The gain and loss regressors were modeled separately, so these estimates are conditional on that modeling choice. Upstream preprocessing and participant models are fixed here; they were not repeated.

## Uncertainty and limits

The sign-flip test assumes participant effects are exchangeable around a symmetric null. The 10,000 draws give finite Monte Carlo precision (minimum possible p = 0.00010); the seed is fixed for reproducibility. The vmPFC mean is imprecise: its confidence interval is compatible with modest effects in either direction. Failure to pass a corrected threshold is not evidence of no neural coding of gain, and it does not rule out smaller effects, effects under another task/model specification, or responses in other regions.

Only participant effect maps were provided. Without participant variance maps or the full upstream executable pipeline, I could not precision-weight participants using their first-level uncertainty, audit every individual-level modeling decision, or propagate uncertainty from preprocessing and first-level estimation. As the range of possible gains was twice the loss range in this group, this result applies to this gain scale and is not a direct gain-versus-loss comparison. These limits follow from the supplied upstream methods and fixed-input design.

## Reproducibility

See [`README.md`](README.md) for run commands. Primary numerical results and analysis settings are in [`results/group_results.json`](results/group_results.json); per-participant QC and vmPFC estimates are in [`results/participant_qc.tsv`](results/participant_qc.tsv). The spatial and voxelwise maps, full voxelwise CSV, checksum record, and analysis scripts are also included in the workspace.
