# Potential gains and brain activity

## Question and result

In the 54-person NARPS equal-indifference group, the supplied gain-effect estimates do **not support a greater vmPFC response as potential gain increases**. The whole-brain corrected positive map contains 24 significant voxels (permutation max-T, familywise α = .05), in three small posterior clusters; none overlap the vmPFC region summarized below. Their peaks fall in posterior cerebellum: 17 voxels at (−26, −102, −3.6), two at (26, −98, −1.2), and five at (30, −94, −8.4). The strongest peak is *t*(53) = 6.62, one-sided max-T FWE *p* = .001 (the minimum attainable Monte Carlo p with 4,999 permutations). Thus, there is corrected evidence for positive gain-related effects somewhere in the brain, but it does not localize to vmPFC.

For an interpretable vmPFC summary, I defined a 12-mm-radius sphere centered at MNI (0, 42, −8), an approximate medial orbitofrontal/vmPFC location. It contains 750 tested voxels after clipping to the analysis mask. The participant-average cope in this region is −0.0068 (between-participant SD 0.094; t-based 95% CI −0.0325 to 0.0189). This descriptive interval spans zero and the ROI contains no voxel surviving whole-brain correction. The sphere is an approximate anatomical summary rather than a definitive boundary for the heterogeneous vmPFC; it was not used to claim significance. [Figure 1](results/figure1_group_maps.png) shows the group mean and corrected map; [Figure 2](results/figure2_vmPFC_roi.png) displays all participant ROI means.

## Group analysis

I fit a one-sample group model to the 54 unthresholded participant cope maps, testing the prespecified positive direction. Each participant contributes one equally weighted estimate. The tested mask is the intersection of nonzero support across maps (198,029 voxels), so the sample size is 54 at every voxel. The primary whole-brain correction uses a one-sided sign-flip permutation maximum-*t* distribution (4,999 permutations, seed 20261016). Sign flipping preserves each participant map's values while testing the group null under exchangeability of signs; maximum-*t* controls familywise error over the entire mask. The 95th percentile maximum-*t* threshold was 5.397. The corrected positive clusters are summarized in `results/fwe_significant_clusters.csv`.

All 54 maps had the expected dimensions, finite values, matching spatial geometry, and SHA-256 hashes matching `input/sources.json`; no participant was excluded. The participant-level ROI values and basic map checks are in `results/`.

## What the estimates mean and limits

These are AO86 participant contrast parameter estimates (copes), not standardized *t* or *z* maps. The upstream gain regressor was mean-centered and variance-normalized before HRF convolution, so a cope is not the BOLD change per currency unit and should not be compared as a currency-scaled slope. The response model used response-time durations and separate choice and gain modulators; gain and loss were modeled separately. Consequently, this analysis tests group consistency in the supplied gain-effect estimates conditional on that upstream model, not a new behavioral or causal effect of monetary value.

Participant variance maps and an executable upstream pipeline were unavailable. Equal-weight group inference therefore cannot use participant-specific precision and inherits uncertainty or misspecification from the fixed first-level estimates. Sign-flip inference assumes participant effects are sign-exchangeable under the null. The common-support mask is defined from map coverage; correction applies to that mask and not voxels outside supplied coverage. The vmPFC sphere is only one defensible approximate anatomical definition; the corrected whole-brain map provides the primary spatial evidence.

Failure to detect a corrected vmPFC effect is not evidence that the true effect is exactly zero or that vmPFC never represents gains. The ROI interval is compatible with small effects in either direction on this cope scale, and the analysis does not establish equivalence. The posterior cerebellar findings also do not answer the vmPFC-specific hypothesis.

## Reproducibility

Run `analyze.py` with the prepared Python environment documented in the task. It writes `results/summary.json`, CSV summaries, NIfTI group maps, and the figures. Input methods and provenance are in `input/upstream-methods.md` and `input/sources.json`.
