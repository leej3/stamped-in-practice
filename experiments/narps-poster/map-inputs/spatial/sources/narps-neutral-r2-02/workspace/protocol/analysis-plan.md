# Analysis plan (before group inference)

## Question and scope
Test whether the participant-level gain-effect estimates in the complete NARPS equal-indifference group have a positive group mean, and whether this evidence localizes to vmPFC. The supplied 54 maps are fixed AO86 participant contrast estimates; do not refit preprocessing or first-level models.

## Analysis unit, sample, and variables
The independent unit is participant (n=54). Outcome is each participant's voxelwise unthresholded gain contrast parameter estimate, averaged across four runs upstream. It is neither a t/z statistic nor a response change per currency unit. Gain regressor was centered and variance-normalized before HRF convolution, with choice and loss handled by the fixed upstream model. No missing covariates are needed for the primary group mean model.

## Primary estimand and inference
At each voxel estimate the one-sample population mean of participant gain-effect estimates. Test a positive mean with one-sided sign-flip permutation inference (participant maps are the exchangeable independent units), using the maximum t statistic over the analysis mask for whole-brain family-wise error control at alpha=.05. Use 10,000 random sign patterns with a fixed seed and include the observed arrangement; report Monte Carlo resolution. Invert the one-sample t model for a descriptive two-sided 95% CI at a transparently selected vmPFC anatomical ROI. Group inference uses equal participant weights because participant-level variance maps are unavailable; it is not a precision-weighted mixed-effects analysis.

## Spatial domain and vmPFC identification
Use the common nonzero finite map support as the estimable brain mask, requiring a voxel to be nonzero in at least 90% of participants; document support checks. Define vmPFC with a 10-mm-radius sphere centered at MNI [0, 40, -8], clipped to that common map mask. This is an explicit anatomical coordinate operationalization for display and descriptive summary; it does not restrict whole-brain correction or create a small-volume confirmatory test. Report corrected whole-brain clusters and whether they overlap this prespecified anatomical sphere.

## QC, exclusions, uncertainty, and limits
Verify participant IDs exactly match metadata, uniqueness, 54 images, dimensions, affine, spatial units, finite values, and checksum identities. Inspect map support and distributional summaries; no participant exclusions based on outcome magnitude or significance. Use a sensitivity check with a stricter >=95% support mask and report any effects on the maximum-T conclusion. Lack of corrected evidence means the supplied group maps do not support a spatially specific positive effect at the chosen error rate; it does not establish a null or rule out effects below power. Upstream separate gain/loss models, normalized regressor scale, lack of first-level variance maps, and lack of access to raw time series constrain interpretation.

## Deliverables
Executable Python analysis, machine-readable QC and summary results, rendered figures with source script, environment identity and concise report. Main run uses the prepared common Python 3.13.16 environment and records package versions.
