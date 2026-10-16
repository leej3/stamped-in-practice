# Analysis protocol: NARPS Hypothesis 1

## Question and target
Test whether the population mean participant-level gain contrast is positive in the equal-indifference cohort (one-sample group effect, direction fixed positive), at the group-analysis stage. Sampling unit: participant, n=54. Outcome: supplied unthresholded participant gain-effect contrast estimates averaged across four runs; these are not test statistics and are not interpretable as signal change per dollar because the upstream gain modulator was normalized. They are conditional on AO86's fixed separate gain/loss models and response-time-duration modeling.

## Inputs and population
Use all 54 maps listed in `input/sources.json` and all 54 equalIndifference rows in `input/participants.tsv`, joined by participant ID. Check unique IDs, checksum/size manifest, spatial shape/affine, finite values and coverage. No outcome-based exclusion; exclude only a missing, unreadable or spatially incompatible map, documenting it. Report whether any exclusion occurs. No time-series data or upstream reanalysis.

## Group model and inference
Fit a voxelwise one-sample t model to participant contrast maps (intercept-only; df=53) over the common supported brain domain. Primary alternative is positive. Whole-brain familywise error is controlled at .05 by a one-sided permutation max-T procedure: randomly sign-flip participant maps under the null, refit the one-sample t statistic, and retain the maximum positive t over all tested voxels for each permutation. Use a fixed RNG seed and at least 9,999 Monte Carlo sign flips; corrected p=(1+number of null maxima >= observed t)/(B+1). This addresses spatial multiplicity, conditional on the mask and sign-exchangeability/symmetric-null assumption. Show uncorrected effects descriptively but do not use them as confirmatory support.

vmPFC is a hypothesis label rather than an explicit ROI boundary in supplied methods. Preserve whole-brain inference as primary; anatomically identify any corrected peak using an independent atlas/anatomical coordinates and report peak MNI coordinates. Do not define the search region from observed effects. If the broad vmPFC boundary is ambiguous, explicitly state that anatomical assignment is approximate. Any atlas ROI summary is secondary/descriptive and not used to claim whole-brain corrected support.

## Checks, uncertainty, outputs
QC includes sample/ID agreement, map geometry/finite coverage, subject-wide map summaries, group mean and t distributions, residual/participant influence summaries, and re-computation of the observed t statistic by an independent formula. Sensitivity: compare sign-flip max-T inference to voxelwise parametric one-sample t with whole-brain Benjamini-Hochberg FDR (clearly secondary), and assess leave-one-participant-out vmPFC descriptive estimates or peak stability. Report effect estimate, 95% CI and p-values; absence of corrected support means insufficient evidence for a positive spatially localized effect at this sample/measurement/model, not evidence of zero or absence of coding.

## Reproducibility
Executable analysis: `code/analyze.py`; output derivatives in `results/`, figures and concise report in `figures/` and `report/`. Inputs pinned by `input/sources.json`; runtime Python is the supplied Pixi Python 3.13.16 with NumPy/SciPy/pandas/Matplotlib/NiBabel/Nilearn. Record versions, command, seed, permutation count and input hashes with results. The protocol is fixed before looking at inferential results; any necessary deviation will be logged.
