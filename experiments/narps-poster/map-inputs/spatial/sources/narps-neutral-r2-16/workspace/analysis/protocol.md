# Analysis protocol

## Question and scope
Test whether participant gain-effect estimates show a positive group mean at any brain location in the NARPS equal-indifference cohort, using only the 54 supplied AO86 participant maps and pinned metadata. Preprocessing and participant models are fixed. No time-series scans or upstream reanalysis are in scope.

## Inputs and unit
The independent sampling unit is a participant (n=54). Each map is the unthresholded gain-modulator contrast parameter estimate (COPE-like effect estimate), averaged across four runs, in MNI152NLin2009cAsym. The gain modulator was mean-centered and variance-normalized before HRF convolution; therefore the map coefficient is not response change per monetary unit. Gain and loss were fit in separate models. Cohort metadata are `input/participants.tsv`; image identities and retrieved-byte hashes are in `input/sources.json`.

## Estimand and model
At each voxel, estimate the across-participant mean of the supplied gain-effect estimates and test H0: population mean <= 0 versus H1: mean > 0. Use an intercept-only one-sample group model, no demographic covariates, and one-sided sign-flip permutation inference with voxelwise maximum-t family-wise error correction over the analysis mask (alpha=.05). This is random-effects group inference over participants, based on observed between-participant variation in the supplied effects; unavailable first-level variance maps preclude variance-weighted second-level modeling. Maximum-t was selected after a 99-permutation TFCE pilot proved computationally impractical (nearly three minutes without completion); this revision occurred before any inference output was inspected.

## Spatial support and vmPFC identification
Before inference, verify identical grids, finite data, matching participant IDs and input checksums. Define the analysis mask as voxels with finite, nonzero estimates in all 54 maps, then report its voxel count and extent; exact zero is treated as outside participant-model support. Whole-brain corrected inference is primary, as requested by the original study. Label a corrected cluster as vmPFC only if its peak/extent occupies medial orbital prefrontal anatomy; use bilateral medial orbitofrontal cortex as an operational atlas proxy because vmPFC lacks a unique agreed boundary. No ROI-restricted p-value will determine the primary decision.

## Quality checks and uncertainty
Inspect the pilot map and group outputs; tabulate per-map finite/nonzero coverage and robust distribution summaries; check demographic metadata completeness and ID joins. Report excluded participants (if any), mask coverage, corrected p-values, and a spatially descriptive unthresholded group map. Permutation results use a fixed seed and 5,000 permutations; minimum attainable Monte Carlo p is 1/(5000+1). A null whole-brain result means this analysis did not provide corrected evidence for a positive effect at the available sensitivity; it does not establish no effect or falsify all vmPFC effects.

## Reproducibility
Entry point: `analysis/run_analysis.py`; environment: supplied Python 3.13.16 interpreter with Nilearn 0.14.1, NiBabel 5.4.2, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2. All generated outputs are under `results/` and `figures/`; command and software identities are recorded in the report.
