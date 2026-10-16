# Analysis protocol: NARPS equal-indifference gain effects

## Question and estimand

Among the 54 supplied equal-indifference participants, is the population mean participant-level gain-modulator contrast positive anywhere in the brain, with vmPFC identified as the prespecified target? The estimand is the group mean of the supplied first-level contrast estimates at each voxel. These estimates come from mean-centered, variance-normalized gain modulators and therefore are not a response change per currency unit, nor can they establish a dose-response slope in currency units.

## Inputs and population

Use the 54 unthresholded `*_hypo1_cope.nii.gz` maps in `input/data/` and all participant rows in `input/participants.tsv`. One row/map per participant; require exact ID agreement, unique IDs, finite voxel values, and identical shape/affine. No exclusion based on observed effect magnitude. Exclude only a participant/map if a prespecified integrity or geometry check fails; document any such exclusion. The pinned source descriptions and checksums are in `input/sources.json`.

## Model and inference

At each voxel, fit a one-sample random-effects group model to the participant contrast estimates (mean and sample standard deviation across participants); the positive alternative tests whether the population mean is greater than zero. This is the natural second-level model for unthresholded subject effects when subject variance maps are unavailable. It treats participants as independent sampling units, and its t-statistic uses between-participant variability. Use a sign-flip permutation null with 9,999 random participant-level sign patterns and a maximum positive t statistic over the full analysis mask for one-sided family-wise error control at alpha=.05. This controls whole-brain voxelwise FWE under the exchangeability/symmetry null; report the finite-permutation resolution and that symmetry assumption. An uncorrected parametric t map is not evidence for the hypothesis.

The analysis mask is the intersection of nonzero finite voxels across all participant maps, intended to retain only locations covered in every input map. Verify and report its size and spatial extent. The single vmPFC region is a 10-mm-radius sphere centered at MNI [0, 40, -10] mm, a conventional anterior ventromedial prefrontal location selected independently of these data. It is descriptive for anatomical localization; no ROI-only p-value substitutes for the required whole-brain correction. Evidence for the target requires a whole-brain FWE-significant positive voxel whose MNI location falls in this sphere. The sphere's mean effect and participant distribution are descriptive.

## Quality and validity checks

Verify input bytes against supplied SHA256 values, participant joins, map geometry, finite values, mask coverage, and image-level summaries. Inspect map distributions and participant ROI means; do not use effect magnitude as an exclusion rule. Compare the observed voxelwise t statistic at independently computed representative voxels to the direct one-sample t formula. Check the permutation maximum-statistic threshold and p-value with an independently summarized null distribution. Report a confidence interval for the vmPFC sphere's mean participant-level effect as descriptive uncertainty.

## Interpretation limits and stopping rule

The gain regressor was standardized before HRF convolution, response trials used response-time durations, and gain and loss were modeled separately. Thus effects reflect the supplied upstream model's relative gain-modulator contrast conditional on that model, not absolute gain scaling or a causal effect of changing gain. Missing first-level variance maps preclude a variance-weighted second-level model; use an unweighted one-sample model and state this limitation. A failure to find a whole-brain FWE-significant positive voxel is lack of corrected evidence at this sample and model, not evidence of zero response or equivalence. Stop after QC, inference, figure review, and replay of the documented script.
