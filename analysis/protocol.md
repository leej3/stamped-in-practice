# Group-analysis protocol (recorded before group inference)

## Question and estimand
Among the complete supplied NARPS equal-indifference cohort, test whether the population mean participant gain-effect estimate is positive at any brain location, with particular interest in ventromedial prefrontal cortex (vmPFC). The estimand is the voxelwise mean of the supplied, run-averaged participant contrast parameter estimates. It is not a response slope per currency unit.

## Population, unit, and inputs
The sampling unit is the participant. Include the 54 participant maps listed in `input/sources.json`, matched one-to-one to the pinned `equalIndifference` rows in `input/participants.tsv`; do not repeat preprocessing or individual modeling. The supplied maps are in MNI152NLin2009cAsym, 2 x 2 x 2.4 mm grid. Use all participants if file, geometry, finite-value, and coverage checks pass; otherwise document exclusions and reasons. Metadata age and gender are descriptive only, not adjustment variables.

## Model and inference
At each voxel, use an equal-weight one-sample t model of the 54 participant effect estimates against zero. The directional hypothesis is positive. Use sign-flip permutation of participant maps under the null, with 10,000 random sign assignments and a maximum positive t statistic over a fixed whole-brain common-coverage mask; compute family-wise corrected p-values from the max-statistic distribution. The plus-one correction is used. Randomization seed: 20261016. A voxel enters the common mask only if finite and nonzero in all 54 maps; inspect the resulting spatial mask before inference. No ROI-restricted inference or post-hoc threshold is used.

## vmPFC localization and reporting
Define vmPFC descriptively as medial (|x| <= 10 mm), anterior (y >= 25 mm), ventral (z <= 15 mm) MNI space, constrained to the common whole-brain mask. This broad coordinate rule is a transparent anatomical locator, not an independent anatomical atlas or a separate significance family. Evaluate vmPFC support only where a voxel survives whole-brain FWE correction; report peak coordinate and extent if present. Also report the unthresholded group map and distribution of estimates.

## Checks and uncertainty
Check map IDs against metadata and sources manifest; verify image dimensions, affine, voxel sizes, finite values, and common coverage; inspect participant means, standard deviations, ranges, and outliers. Inspect the pilot before executing the full analysis. Compare the voxelwise t statistic at a selected voxel to an independent direct formula. Summarize uncertainty with group mean and 95% t interval at the selected vmPFC descriptive peak, clearly identifying this as post-hoc descriptive and not inferential evidence. Interpret a null whole-brain result as failure to find corrected evidence, not proof of no vmPFC response. Limitations include absent participant variance maps, unknown upstream estimation uncertainty, normalized regressor units, and separate gain/loss participant models.

## Reproducibility
Run from workspace root with the prepared Python 3.13.16 environment: `.../bin/python analysis/group_analysis.py`. Record software versions, seed, exact inputs, outputs, and run summary in `results/`.
