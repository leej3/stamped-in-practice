# Analysis protocol

## Question and estimand

Test whether the mean participant-level AO86 gain-modulator contrast estimate is greater than zero in the NARPS equal-indifference group, and whether any positive whole-brain corrected findings localize to an independently defined vmPFC region. The independent sampling unit is the participant (N=54). Estimates are model coefficients for a mean-centered, variance-normalized gain modulator after HRF convolution, not BOLD change per currency unit, standardized statistics, or raw signal. Because gain and loss were modeled separately, the gain contrast is conditional on that upstream model.

## Fixed inputs and exclusions

Use all 54 supplied maps and all 54 matching participants in `input/participants.tsv`; no demographic covariates or participant exclusions are planned. Verify participant ID set, map checksums, dimensionality, affine, voxel size, and finite values. Inferential voxels will be those with nonzero map support in at least 90% of participants; this coverage threshold is fixed before inspecting group statistics and avoids treating outside-brain zeros as measured null effects. Report any resulting coverage limitations.

## Primary model

At each inferential voxel, test the one-sample group mean against zero in the positive direction using a one-sample t statistic. Calibrate the maximum studentized mean statistic over the entire supported brain mask with 4,999 Monte Carlo sign-flip permutations (participant-level sign flips, fixed seed 20261016). Each sign-flipped mean is standardized by the observed voxelwise standard error, fixed across flips; the statistic under the observed sign pattern equals the usual one-sample t. This yields single-step whole-brain family-wise-error corrected p-values under the assumption of independent participants and a symmetric null distribution of participant effects. Use alpha=.05. The minimum attainable Monte Carlo p-value is 0.0002.

## vmPFC identification

The primary inference is whole brain, as required by the NARPS instructions. Label a corrected cluster as vmPFC only if it overlaps an independently specified Harvard-Oxford cortical atlas anatomical mask: Frontal Pole, Frontal Medial Cortex, Subcallosal Cortex and Paracingulate Gyrus, restricted to |x|<=14 mm and z<0 in MNI space. This follows a published operational vmPFC definition and is not derived from the observed maps. The atlas mask is descriptive localization and does not replace whole-brain correction. Report the mask source, overlap, and ROI summary as supporting description only.

## Checks, uncertainty, and interpretation

Inspect the participant-by-voxel coverage and estimate distributions; retain all maps unless a prespecified integrity check fails. Report the ROI mean and participant-level 95% t interval and one-sided test as descriptive supporting information, with the whole-brain corrected result governing evidence for the hypothesis. A non-significant corrected result means this analysis did not establish a positive gain effect under the specified model and correction; it does not establish absence or equivalence. Missing first-level variance maps preclude precision-weighted mixed-effects group analysis. The upstream model and supplied coefficients are fixed; conclusions do not validate that model or imply a per-dollar neural response.
