# Analysis protocol

## Question and target
Test whether the group-average AO86 gain-effect estimate is greater than zero among the 54 NARPS equal-indifference participants. The supplied images are fixed participant-level contrast parameter estimates (COPE-like estimates) from four runs, not t/z statistics or effects per monetary unit. The group target is the population mean of those participant estimates under the supplied upstream model.

## Inputs and population
Use `input/participants.tsv`, `input/sources.json`, `input/upstream-methods.md`, and all 54 supplied `input/data/*_hypo1_cope.nii.gz` maps. Unit of analysis is participant. Join by exact `sub-NNN` ID. Require one map per participant, no duplicate IDs, common shape/affine, and finite data. Include all participants matching the source table; only exclude a participant for a prespecified input-integrity failure. The spatial analysis mask is the intersection of nonzero image coverage across all included participants, not a statistical threshold.

## Primary model and inference
At each covered voxel, estimate an unweighted one-sample mean and one-sample t statistic against zero. This is a group-level random-effects-style test over participants but is not variance-weighted because participant variance maps are unavailable. The directional alternative is positive. Control whole-brain family-wise error at 0.05 with 9,999 participant-level random sign flips and the maximum positive t statistic over the entire common-coverage mask. Seed: 20261016. Corrected p values use the plus-one Monte Carlo estimator. The sign-flip test assumes participant errors are independent and sign-symmetric under the null; report this assumption and Monte Carlo resolution.

The hypothesis decision is positive only if at least one voxel is significant at whole-brain FWE p < .05 and can be anatomically assigned to vmPFC; otherwise report no whole-brain-corrected support. Also report the strongest positive voxel in a fixed descriptive vmPFC mask (MNI x −15..15, y 20..60, z −20..10 mm), with its uncorrected one-sided p and group mean/SE/CI. This coarse coordinate mask is a descriptive anatomical approximation, not a substitute for whole-brain correction or a precise atlas parcel.

## Quality and validity checks
Check source-file SHA256 values against `sources.json`, exact participant/map matching, grid/affine agreement, finite values, coverage, and participant-wise map summaries. Independently compare selected voxel statistics against SciPy's one-sample t test; calculate an ROI-mean participant-level t test independently from the voxelwise search; inspect distributions and rendered figures. No exclusion based on effect magnitude or significance. No covariates are included in the primary model because the target is the group mean and n=54; age and gender are retained only as metadata.

## Scope and stopping
Do not redo preprocessing or participant models, retrieve time-series scans, or claim an effect per currency unit. A nonsignificant result means this analysis did not detect positive group-average gain modulation at the whole-brain FWE threshold; it is not evidence of equivalence or absence. Upstream regressor scaling/modeling and missing participant variance maps limit interpretation and precision.
