# Analysis protocol

## Question and target

Test whether gain-related participant contrast estimates are positive on average in the complete equal-indifference cohort, and whether any positive group response survives whole-brain family-wise error correction in vmPFC. The independent sampling unit is the participant (n=54); each input is one unthresholded participant-level gain contrast estimate averaged over four runs. It is not a standardized statistic and, because participant variance maps are unavailable, cannot support precision-weighted mixed-effects inference.

## Fixed inputs and exclusions

Use only the 54 locally supplied AO86 maps and `input/participants.tsv`, preserving the upstream modeling described in `input/upstream-methods.md`. No participants are excluded unless a map is unreadable, mismatched, non-finite in analysis coverage, or structurally incompatible; report any exclusions and reasons. Treat exact zero voxels as no map support and define the group domain as the intersection of an independent MNI152 brain mask with nonzero support in all 54 maps. This uses a fixed n at every tested voxel and avoids treating unsupported voxels as zero effects. Demographic adjustment is not part of the primary model.

## Model and inference

At each covered voxel, estimate the unweighted mean of participant contrast estimates and its one-sample t statistic against zero. Test the directional positive effect with participant-level sign-flip permutation and a maximum-t statistic over the entire analysis mask, controlling family-wise error at 0.05. The null exchangeability assumption is sign symmetry of participant effects under zero mean; use 9,999 random sign patterns plus the observed arrangement, seed 20261016, and the tie-inclusive empirical tail fraction. Report the ROI mean and t-based 95% confidence interval descriptively; a ROI-only p-value cannot establish the hypothesis.

## Anatomical localization and checks

Use the Harvard-Oxford cortical atlas, independent of these effects, to define an operational vmPFC proxy as atlas Subcallosal Cortex plus Frontal Orbital Cortex voxels within |x| <= 20 mm, intersected with the common-support group mask. This conservative midline ventral mask is a proxy (the atlas has no label named vmPFC), not a functional localization. The hypothesis is supported only if at least one positive whole-brain FWE-significant voxel overlaps the proxy. Check participant identity joins, duplicate IDs, checksums, headers/affines, finite values, map coverage, mask size, ROI size and effect distribution. Compare ROI t statistics with an independently computed SciPy one-sample t test. Keep the supplied upstream model fixed and interpret effects as relative contrast estimates, not BOLD change per currency unit.

## Execution and stopping

Run `analysis/run_analysis.py` using the prepared Python 3.13.16 interpreter specified in `README.md`. Keep derived maps, tables and figures under `results/`. Stop after the predeclared group model, correction, QC and independent numerical check; report limitations rather than tuning the ROI or analysis to attain significance.
