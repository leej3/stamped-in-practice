# Analysis protocol

Question: among the 54 equal-indifference NARPS participants, do supplied gain-modulator contrast estimates have a positive group mean in brain locations anatomically corresponding to vmPFC?

## Fixed inputs and estimand

Use exactly the 54 participant maps listed in `input/sources.json` and the matching rows in `input/participants.tsv`. Each NIfTI is an unthresholded participant gain-effect estimate, averaged over four runs in MNI152NLin2009cAsym. It estimates a coefficient for a mean-centered, variance-normalized gain modulator, not a currency-unit slope or a standardized statistic. Upstream preprocessing and individual models are fixed; no time series are retrieved. The group estimand is the one-sample mean participant contrast at each voxel for this selected group.

## Primary group model and inference

At each voxel, estimate the one-sample mean and standard error across independent participant maps and test the directional alternative mean > 0 with a one-sample t statistic (df=53). Use an explicit common finite-data analysis mask derived from voxels covered by every map. Primary whole-brain family-wise correction uses the maximum positive t across 9,999 participant-level sign-flip permutations (seed 20261016); it requires symmetry of participant effects under the null and preserves each participant as the sampling unit. The p-value uses the plus-one correction. Parametric voxelwise Bonferroni is also retained as a conservative reference that does not rely on spatial smoothness. The support criterion is a positive whole-brain-corrected voxel in an anatomically plausible vmPFC location; a subthreshold result is not evidence of no effect. Report the map-based mean contrast and t statistic, without interpreting coefficient magnitude in dollars.

## Checks and exclusions

Verify input SHA-256 and byte counts against the supplied manifest; enforce unique IDs and exact set match to metadata; inspect affine, shape, voxel sizes, finite coverage and per-map summary distributions. Exclude no participant for statistical extremity; only structural or nonfinite failures could exclude a map, reported individually. No covariates are included: age/gender are not needed for this group mean and would change the estimand. Report the overlap mask size, all exclusions and the non-parametric upstream limitations (participant variance maps unavailable; gain and loss were fit separately).

## Validation and deliverables

Cross-check voxelwise t and one-sided p-values against SciPy's independent one-sample t-test on selected voxels and summarize a coordinate-defined vmPFC display box separately from whole-brain inference. Generate checked table and NIfTI outputs, editable plotting code, figures and execution/environment records. No sensitivity result replaces the primary result.

## Protocol revision record

The initial written protocol proposed voxelwise Bonferroni correction as primary. Before accepting the final run, this was revised to sign-flip maximum-t FWE as primary because the participant-level maps permit a direct sampling-unit resampling test with whole-brain max-statistic control. Bonferroni remains a reference analysis. The coordinate-defined vmPFC box is descriptive, not used to select the whole-brain inference. This amendment is reported as an analysis choice, not a prespecified design feature.
