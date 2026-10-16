# Analysis protocol

## Question and scope
Test whether the supplied participant gain-effect estimates show a positive group mean in vmPFC for the NARPS equal-indifference group. The 54 participants are the sampling units. Inputs are the fixed AO86 unthresholded participant maps and matching metadata; no time-series processing or refitting is permitted.

## Estimand and interpretation
Primary estimand: mean across participants of the supplied gain contrast estimate at each voxel. Upstream gain modulation was mean-centered and variance-normalized before HRF convolution, so this is not signal change per currency unit. Because participant variance maps are unavailable, use an unweighted one-sample random-effects t model over participant estimates; between-participant variability determines uncertainty.

## Primary inference
At each shared finite, nonzero-coverage voxel, test H1: population mean > 0 with a one-sample t statistic (df=53). Correct one-sided p values by Bonferroni over all analyzed voxels (strong whole-brain family-wise control, conservative). Do not infer from uncorrected maps or ROI-only testing.

## vmPFC definition
For anatomical description only, define a bilateral medial prefrontal ROI in MNI coordinates: x = -12..12, y = 25..60, z = -10..10 mm, restricted to shared valid brain coverage. This covers medial orbitofrontal/subgenual vmPFC; the bounds are an operational anatomical choice, not data-derived. Any positive whole-brain corrected voxels in these bounds count as corrected spatial evidence in the target region. Report ROI mean and t interval descriptively, not as a substitute for whole-brain correction.

## QC, exclusions and assumptions
Match participant IDs exactly and reject duplicates or missing maps. Inspect image dimensions, affine, voxel size, nonfinite values, zeros, coverage intersection, per-subject whole-map distribution and ROI coverage. Exclude only a participant with unreadable/mismatched image or no ROI/brain support; document reason. Zeros outside a map's support are treated as missing coverage; use intersection of nonzero support across all 54 maps to keep the analyzed domain identical. The one-sample t model assumes independent participants and sufficiently well-behaved participant-level estimates; inspect distributions and report the limitation that upstream variance/precision cannot be modeled.

## Outputs and stopping rule
Produce a rendered concise report, editable figure source, summary tables, group effect/statistic/corrected-p maps, and executable Python entry point. Stop after all map and metadata checks pass and inference/plots are reproduced; no threshold shopping or result-driven ROI changes.
