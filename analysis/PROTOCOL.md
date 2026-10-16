# Group analysis protocol

## Question and estimand

In the complete supplied equal-indifference cohort (54 participants), is the mean participant-level gain-modulator effect positive across voxels in vmPFC, with evidence meeting a whole-brain family-wise error (FWE) threshold? The input maps contain one gain contrast parameter estimate per participant, averaged over four runs. They are not standardized statistics. The estimand is therefore the cohort mean of those upstream estimates, not a currency-unit slope or a new trial-level BOLD model.

## Analysis decisions

* Unit: participant. No demographic covariates are needed for this one-sample directional hypothesis.
* Primary inference: one-sided, voxelwise one-sample t statistic over a common coverage mask, calibrated with 9,999 random sign flips and a maximum-t distribution. This controls FWE across the full tested mask at alpha=.05. Seed is 20261015. Monte Carlo adjusted p-values use (1 + exceedances)/(B + 1).
* Mask: voxels finite and nonzero in every participant map. Exact zeros are treated as unsupported because separate participant brain masks are not supplied; this common-support intersection gives every voxel the same n. The union support and number of excluded partial-support voxels are recorded. This is an operational whole-brain mask from supplied maps; no statistical thresholding or ROI selection defines the inferential mask.
* vmPFC identification: independent Harvard-Oxford cortical atlas `Frontal Orbital Cortex` or `Subcallosal Cortex`, probability-thresholded at 25%, restricted to the anterior midline (|x| <= 15 mm, y >= 0) and ventral/inferior space (z <= 0). These atlas-defined orbitomedial/subcallosal areas operationalize vmPFC anatomically and are descriptive only; they do not narrow the primary corrected search. The pinned atlas volume, label XML, and MNI152 T1 2 mm display template are included under `input/atlas/`; their sources and SHA256 hashes are recorded in `input/atlas/sources.json`.
* Effect summary: participant mean within the anatomical vmPFC mask, with a two-sided 95% t interval, shown with participant values. Its p-value is descriptive and does not replace whole-brain corrected inference.
* QC: verify exact 54-person table/image identity, unique IDs, SHA256 checksums, image shape/affine agreement, finite values in the test mask, a nonempty common-support mask and ROI, and report map coverage. Exact zeros may be true zero estimates rather than missing support, so the intersection can conservatively omit valid zero-effect edge voxels. Exclude no participant absent a prespecified integrity failure; any failure stops analysis for review rather than silently excluding a map.
* No significance-driven exclusions or threshold changes. The complete cohort is retained if all supplied maps pass the integrity checks.

## Interpretation limits

AO86 mean-centered and variance-normalized the gain modulator before convolution; the cope is not a per-dollar slope. The effect is conditional on the supplied upstream model, which separately modeled gain and loss; neither participant variance maps nor the complete executable participant pipeline are supplied. Sign-flip inference assumes participant effects are independent and symmetric under the null. With 54 participants, this is plausible for a group mean but not guaranteed. A failure to detect corrected vmPFC support is not evidence of zero effect or equivalence.

## Inputs and execution

Inputs are the 54 annexed `input/data/*_hypo1_cope.nii.gz` maps and pinned `input/participants.tsv`; their provenance and checksums are in `input/sources.json`. The atlas and display template are fixed local inputs. No time-series scans or upstream refitting are used. Run `pixi run group-analysis -- --permutations 9999`; the task writes tables, maps, figures, and machine-readable summary under `results/group-analysis/`. Capture the command with `duct` under `logs/`.
