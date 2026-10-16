# Analysis protocol

## Question and estimand

Test whether the mean participant gain-effect estimate is greater than zero in the equal-indifference cohort (N=54). The supplied contrast maps are participant-level parameter estimates for a mean-centered, variance-normalized gain modulator. The estimand is therefore the cohort mean of those contrast estimates, not change in BOLD per currency unit.

## Data and unit

Use all 54 `input/data/*_hypo1_cope.nii.gz` images identified in `input/sources.json`, joined one-to-one by participant ID to `input/participants.tsv`. The independent sampling unit is participant. Do not repeat upstream preprocessing or individual modeling. Check file hashes, dimensions, affine, finiteness, coverage and metadata join before group analysis. Exclude only an input that fails a declared integrity/spatial/QC check; record any exclusion and reason.

## Model and inference

Primary model: one-sample group mean at each voxel, testing positive mean (one-sided, ex ante directional hypothesis). Estimate uncertainty across participants. Use sign-flip permutation of participant maps with a maximum-t statistic across the complete analysis mask for family-wise error control over the whole brain. Use 9,999 random sign patterns plus the observed arrangement; fix and record the seed and use the plus-one permutation p-value. This inference assumes participant effects are independent and sign-exchangeable under the null. Also report conventional one-sample t estimates and uncorrected p-values as descriptive support, not as the hypothesis decision.

The analysis mask is the common spatial support of all input maps (nonzero finite values in every participant), because zero-filled voxels outside the upstream brain analysis mask are not observations. Document voxel count and geometry. Operationalize vmPFC with a literature-defined 5 mm MNI sphere centered at [2, 46, -8], reported as a vmPFC valuation focus in Bartra et al. (2013), external to these maps. The localization supports the claim only if a positive whole-brain FWE-significant voxel is within that independently defined ROI. Report ROI summaries descriptively and do not use them to replace whole-brain correction.

## QC, uncertainty and limitations

Retain a participant QC table and descriptive maps/distributions. Report N and exclusions, sign-flip count, mask, peak coordinates, effect estimate and uncertainty, FWE p-value, and whether any corrected voxel intersects the vmPFC ROI. Report a sensitivity check against an independent one-sample t implementation. Note that participant variance maps and upstream model are unavailable; group inference treats contrast maps as measured effects and cannot propagate first-level uncertainty. The upstream gain regressor normalization prevents interpreting coefficients per currency unit, and gain and loss were modeled separately.

## Deliverables and stopping rule

Provide executable analysis code, machine-readable results, figures, a concise report, and a documented command/environment. Stop after data/QC review, primary inference, independent numerical check, figure inspection, and replay of the recorded analysis.
