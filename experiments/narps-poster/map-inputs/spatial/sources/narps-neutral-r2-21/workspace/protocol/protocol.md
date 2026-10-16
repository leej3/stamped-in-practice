# Analysis protocol

## Question and target
Test whether mean gain-parametric fMRI effect is positive in the complete supplied equal-indifference cohort, and whether any positive signal is supported at whole-brain corrected inference. The independent sampling unit is the participant (N=54); each supplied image is one participant-level gain-modulator contrast estimate averaged across four runs.

## Fixed inputs and scope
Use the 54 `hypo1_cope` maps and matching rows in `input/participants.tsv`; preprocessing and participant-level modeling are fixed. No time-series scans or upstream reruns. Source image identities and retrieved checksums are in `input/sources.json`. The supplied coefficients arise from a mean-centered and variance-normalized gain modulator before HRF convolution and therefore are not BOLD change per currency unit. The gain estimate is conditional on a separate gain/loss model. Participant variance maps are absent.

## Primary analysis
One-sample group model of participant effect images against zero. Test the prespecified positive direction with sign-flip permutation max-t familywise error control across all voxels in a common MNI brain analysis mask, alpha=.05. Sign flips operate on whole participant images, preserving within-image spatial dependence. Use 9,999 Monte Carlo sign flips with plus-one p-values and fixed seed. Report unthresholded mean and t maps and the whole-brain FWE thresholded result. Inference assumes independent participants and null sign symmetry; no variance maps means equal participant weighting and no precision weighting.

## vmPFC interpretation
Operationalize vmPFC a priori as a 10-mm-radius sphere centered at MNI [0, 40, -8] mm, a conservative medial ventral prefrontal coordinate region. This sphere is a localization aid only: evidence for the hypothesis is decided by the whole-brain max-t test, not an uncorrected ROI test. Report whether corrected positive voxels overlap the sphere and summarize the average participant effect within it.

## Checks, exclusions, uncertainty
Verify the image-to-participant bijection, input SHA256, finite values, common shape/affine, and spatial coverage. Exclude only unusable maps under those objective checks; document each exclusion. Inspect sample-level effect distributions and the result maps. Add the conventional one-sample parametric t result as a sensitivity summary, not as a replacement for the primary permutation result. Uncertainty is participant-level sampling variation; report mean, SD, standard error and 95% t interval for the ROI summary. A null corrected result means insufficient evidence under this group model and correction, not evidence of no effect or proof that gain has no neural correlate.

## Reproducibility
Executable entry point: `code/run_analysis.py`; outputs go to `results/` and `figures/`. Use the supplied Python environment at `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python` (Python 3.13.16; NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2, Nilearn 0.14.1). Keep the fixed RNG seed and command in the run record.
