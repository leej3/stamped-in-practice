# Group analysis protocol

## Question and target

Test whether the group mean gain-effect estimate is positive in the equal-indifference cohort, and whether any whole-brain-corrected positive effect overlaps an independently specified vmPFC region. The sampling unit is participant (54 participants); the estimand is the mean of AO86's participant-level gain contrast estimates over this cohort. It is not a currency-unit slope or a causal effect of changing gain.

## Fixed inputs and exclusions

Use all 54 participant maps enumerated in `input/sources.json`, joined one-to-one to `input/participants.tsv` by participant ID. Verify map count, checksums, dimensions, affine, finite values and the common nonzero support. No participants are excluded unless an input is missing, corrupt, nonfinite or spatially incompatible; report any such exclusion by ID and reason. The cohort table is the complete equal-indifference group, so demographic covariates are not needed for this one-sample question.

## Primary inference

At each voxel in the intersection of participant nonzero support, calculate a one-sample t statistic against zero and test the prespecified positive direction. Control family-wise error across all tested voxels with a one-sided maximum-t sign-flip permutation test (5,000 random participant-level sign assignments, seed 20261016). This requires exchangeability of signs under the null and symmetric participant errors; the small Monte Carlo p-value resolution is 1/5,001. A vmPFC claim requires a positive voxel passing whole-brain FWE p < .05 inside the vmPFC mask. The mask is the union of Harvard-Oxford cortical atlas 2-mm, 25%-threshold maximum-probability labels `Frontal Medial Cortex`, `Subcallosal Cortex`, `Paracingulate Gyrus`, and `Frontal Orbital Cortex`, nearest-neighbor resampled to the supplied maps. This is an explicit, broad anatomical operationalization, not a universally agreed boundary.

Report the voxelwise effect mean, t, uncorrected p, maximum-t FWE p, and coordinates at the strongest positive voxel. Also report a descriptive participant-level vmPFC mean and t-based 95% CI, and a leave-one-participant-out range for that mean. The atlas ROI summary is descriptive and cannot establish support without the whole-brain-corrected criterion.

## Validity and limits

Input checksums and participant joins must match the committed source manifest. Check common spatial geometry, finite values, sample sizes, and the computed mask/ROI sizes. Display the effect distribution and corrected whole-brain result. The maps are first-level contrast parameter estimates from AO86, not standardized statistics; their regressor was centered and variance-normalized before HRF convolution, so coefficients are not per-unit monetary effects. Separate gain/loss models mean gain effects are conditional on that upstream choice. No participant variance maps or executable upstream workflow are supplied, preventing a first-level precision-weighted mixed-effects analysis. A null corrected result means insufficient evidence at this sample and correction threshold; it does not establish no vmPFC response or equivalence to zero.

## Stopping rule

Stop if checksums fail, maps cannot be consistently registered, or the vmPFC mask has no overlap with the tested support. Do not change the model or threshold in response to observed significance. Any method change must be recorded as a separately named analysis.
