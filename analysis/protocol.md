# Group-analysis protocol (frozen before analysis)

## Question and target
Test the directional group hypothesis that the mean participant-level gain-effect estimate is positive in the equal-indifference cohort, with whole-brain family-wise error (FWE) control. Sampling unit: participant (54 supplied participants). The estimand is the cohort mean cope across participants at each voxel, conditional on AO86's fixed participant models; it is not a currency-unit response slope or a causal effect of gain.

## Inputs and exclusions
Use all participant cope maps listed in `input/sources.json`, joined to the pinned cohort metadata by exact participant ID. Check uniqueness, missing files, image geometry, finite values, and spatial coverage. Do not exclude on outcomes. Exclude only a participant/map for a predeclared technical failure (missing/corrupt image or incompatible geometry); document any such exclusion. Preserve participant age/gender as descriptive metadata, not adjustment variables.

## Primary model and inference
Use a one-sample group model of the cope maps with an intercept and test intercept > 0. Use participant-level sign-flip permutation inference and the maximum voxel statistic over the common intersection of all participant nonzero coverage masks to control whole-brain FWE at alpha=.05. This avoids treating zero-filled out-of-coverage voxels as measured zero effects. It provides nonparametric null calibration under independent, sign-symmetric participant errors; it does not propagate unavailable first-level variance estimates. Report permutation count, seed, mask definition, voxelwise and maximum-statistic outputs. A conventional one-sample t model and interval summaries are descriptive cross-checks, not a substitute for the primary whole-brain corrected inference.

## vmPFC identification
Define vmPFC anatomically and independently of these effects using a bilateral atlas ROI (Harvard-Oxford cortical atlas; frontal medial, subcallosal, and frontal orbital parcels) and show its overlap with the analysis mask. The ROI supports anatomical interpretation only; the confirmatory decision uses whole-brain FWE. If atlas/standard template retrieval is unavailable, record the alternative and rationale before inspecting effect results.

## QC, uncertainty, and deliverables
Inspect all maps for geometry, coverage, nonfinite/extreme values, participant mean and spatial outliers before group inference. Plot cohort mean and variation plus corrected statistical maps. Retain code, environment identity, executed parameters, machine-readable summaries, and figures. Independently cross-check observed and permuted voxelwise t calculations against SciPy. Since QC showed zero-filled voxels with incomplete coverage, also report a labeled 90%-coverage sensitivity analysis to show the impact of a broader mask. State limitations from the upstream normalized gain modulator, separate gain/loss models, and absent participant variance maps.
