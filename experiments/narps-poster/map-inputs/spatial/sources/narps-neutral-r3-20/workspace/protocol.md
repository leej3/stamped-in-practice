# Analysis protocol: NARPS Hypothesis 1, equal-indifference group

## Question and target
Test whether participant-level gain-effect estimates have a positive group mean at brain voxels in the complete 54-person equal-indifference group. The group estimand is the mean of the supplied participant gain-effect estimates (AO86; four runs averaged within participant), not a per-currency-unit neural slope. The fixed upstream regressor was mean-centered and variance-normalized before HRF convolution. Gain estimates are conditional on the separate gain-model specification and are not standardized statistics.

## Inputs and population
Use all 54 `input/data/*_hypo1_cope.nii.gz` maps identified in `input/sources.json`, joined by participant ID to `input/participants.tsv`. No time-series data or upstream refitting. Include participant once; exclude only if map is unavailable, geometry differs, or values are nonfinite in the analysis domain. Missing/nonfinite coverage is not interpreted as zero. Any exclusions will be tabulated.

## Group inference
Primary test: one-sample, equal-weight group t statistic on participant estimates, positive direction, with 53 df. Since participant variance maps are not supplied, use between-participant variability (random-effects one-sample model) and do not precision-weight. To control whole-brain family-wise error, use a one-sided sign-flip max-t permutation test (5,000 Monte Carlo sign patterns, seed 20261016) over the common valid brain support; this relies on independent participants and approximate symmetry of null errors. Report the empirical corrected p value and unthresholded t map. Also provide voxelwise one-sided t p values and Benjamini-Hochberg q values as a secondary, less conservative whole-brain FDR summary. No ROI-only test determines support.

## Domain, checks, uncertainty
Common valid support is the intersection of finite, nonzero map voxels; this removes shared zero-filled background. Inspect shape/affine, finite data, nonzero coverage, participant distributions and map summaries. Report the number of voxels, exclusions, mean effect and confidence interval at the whole-brain positive peak. A positive peak is interpreted as vmPFC only if its MNI coordinates and anatomical display support that label; this is a descriptive localization, not an ROI gate or independent corrected test. Whole-brain correction across the full analyzed support remains required.

## Presentation and limits
Provide a whole-brain group mean/statistic display and participant-level vmPFC descriptive distribution if a reproducible anatomical definition is available; otherwise use coordinates and atlas labels descriptively. Failure to reject does not show no effect or equivalence: it means this sample and supplied estimates did not provide whole-brain-corrected evidence under this model. Discuss one-sample model assumptions, missing first-level variance, fixed upstream modeling, and the fact that the slope scale is not currency units.

## Exploratory vmPFC follow-up

After the primary whole-brain result was inspected, a coordinate-defined vmPFC approximation was added solely to summarize the stated target region: a 15 mm radius sphere centered at MNI (0, 44, -12) mm, within anterior ventromedial prefrontal cortex. The supplied files contain no vmPFC mask or participant variance maps. This post hoc sphere is not an atlas-derived ROI and does not provide the hypothesis decision; its mean, ordinary t interval and location are descriptive. Whole-brain max-T-adjusted voxelwise evidence is used to assess regional localization.
