# Potential gains and brain activity

## Finding

In the 54-person equal-indifference group, the supplied gain-effect estimates do **not** support a greater vmPFC response with increasing potential gain. The a priori vmPFC summary was slightly negative (10-mm sphere centered at MNI [0, 40, -8]: mean estimate = -0.0057, *t*(53) = -0.43, one-sided *p* = .665; 95% two-sided CI [-0.0326, 0.0211]). No voxel in this sphere survived whole-brain family-wise error correction. The interval is compatible with small positive or negative effects; this is a lack of evidence for the predicted response, not evidence that the true effect is exactly zero.

The whole-brain positive test did identify 24 voxels in three small, spatially separated posterior occipital foci (largest voxel *t* = 6.62; minimum max-*t* corrected *p* = .0009). These foci are outside vmPFC and do not support the stated hypothesis. Their isolated location is reported as a secondary whole-brain observation, not as an explanation of gain coding.

![Whole-brain positive effects after max-T correction; yellow marker is the vmPFC sphere center.](figures/whole_brain_fwer_vmPFC.png)

![Participant mean gain-effect estimates within the vmPFC sphere.](figures/vmPFC_participant_effects.png)

## Analysis

I fitted a one-sample random-effects *t* model to the 54 participant contrast parameter estimates, testing a positive group mean. These maps are unthresholded participant effect estimates, not standardized statistics. The supplied methods state that AO86 mean-centered and variance-normalized the gain modulator before HRF convolution. Thus the estimated effect is per normalized modulator unit, not per currency unit; the gain coefficient is also conditional on the separate gain-model specification described in `input/upstream-methods.md`. The experiment's wider gain than loss range does not rescale these estimates into monetary units.

The confirmatory map uses 9,999 participant-level sign flips of the studentized one-sample statistic and the maximum positive *t* across the whole common-coverage brain on each draw. This one-sided max-*t* procedure controls family-wise error across tested voxels at .05 (critical *t* = 5.357). It assumes participant effects are independent and sign-exchangeable under the null. The analysis mask includes the 198,029 voxels nonzero in every map, so map zeros outside an individual's estimation mask are not treated as measured zero effects. The vmPFC region is an a priori 10-mm-radius sphere centered at MNI152NLin2009cAsym [0, 40, -8], covering medial orbitofrontal/ventromedial frontal cortex; its center is shown in yellow in Figure 1. The regional summary is descriptive and uncorrected; any claim of support is gated by whole-brain correction.

## Quality checks and limits

All 54 expected participant maps were present, had matching 97 × 115 × 81 geometry and affine, contained finite values, and matched the SHA-256 checksums in `input/sources.json`. No participants were excluded. Participant mean estimates over common brain coverage ranged from -0.134 to 0.104, with no data-driven outlier exclusion. The supplied files lack participant variance maps, so a precision-weighted group model could not be fit; the unweighted one-sample model estimates between-participant variability in the supplied effects. The sign-flip test adds a distributional assumption and has Monte Carlo resolution of 1/10,000.

These results address group inference on fixed upstream effects, not reprocessing or re-estimation of the trial-level model. They cannot establish a response per dollar, separate gain from correlated task properties beyond AO86's model, prove absence of a smaller effect, or generalize beyond this group and model. The vmPFC interval is not an equivalence test. A null or negative group result means the supplied maps do not provide corrected evidence for the predicted positive group response under these assumptions.

## Reproduction and files

Run `python analysis/analysis.py` using the supplied prepared Python environment (Python 3.13, Nilearn 0.14, NiBabel, NumPy, SciPy, pandas and Matplotlib). The script checks input checksums, geometry and finite values, then writes the group maps, ROI/QC table, permutation null distribution, JSON summary and corrected focus table (`results/whole_brain_foci.tsv`). Figures are in `figures/`. The original study's Hypothesis 1 instructions are available [here](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf); the analysis follows the supplied task's whole-brain correction requirement.
