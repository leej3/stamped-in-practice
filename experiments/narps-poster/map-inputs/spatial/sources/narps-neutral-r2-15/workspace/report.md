# Potential gains and brain activity

## Conclusion

In the 54-person equal-indifference group, the supplied gain-effect estimates do **not** support a positive vmPFC response to increasing potential gain at the whole-brain family-wise error (FWE) corrected level. The positive one-sample group effects that survived correction were in posterior occipital cortex, not vmPFC. In a broad, coordinate-defined vmPFC search zone, the average effect was near zero (mean 0.0001, 95% t interval −0.0152 to 0.0154; exploratory one-sided *p* = .494). This is a lack of convincing support in these maps, not evidence that the true effect is exactly zero.

## Analysis

The target was the NARPS Hypothesis 1 positive parametric gain effect in the equal-indifference group ([original team instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). We analyzed the 54 supplied unthresholded AO86 participant effect maps. All files matched the source SHA256 manifest; all maps shared a 97 × 115 × 81 MNI152NLin2009cAsym grid and contained finite values. No participants were excluded.

At each voxel we fit a one-sample group model testing whether the mean participant effect estimate exceeded zero. This treats participant effects as equally precise because participant variance maps are unavailable. Inference used 5,000 one-sided sign/permutation max-*t* draws (seed 20261016), controlling voxelwise FWE across the analysis mask. The mask intersected a standard MNI152 brain mask resampled to the input grid with voxels having a nonzero estimate in at least 90% of participants (192,339 voxels). The anatomical image is a standard MNI template; input maps were not resampled.

To make the anatomical interpretation explicit, vmPFC was operationalized descriptively as the midline anterior-ventral MNI search zone |*x*| ≤ 20, *y* = 0 to 60, *z* = −25 to 10 mm. These coordinates provide a broad locator, not a cytoarchitectonic boundary. The regional estimate is exploratory; the primary hypothesis assessment is the whole-brain corrected map.

## Results

Twenty-three voxels in three small clusters passed positive whole-brain max-*t* FWE *p* ≤ .05. Cluster peaks were at (−26, −102, −3.6) mm (*t* = 6.62, FWE *p* = .0004; 16 voxels), (26, −98, −1.2) (*t* = 5.76, *p* = .0106; 2 voxels), and (30, −94, −8.4) (*t* = 6.19, *p* = .0038; 5 voxels). These posterior coordinates are outside the vmPFC search zone. There were no corrected positive voxels in vmPFC.

The average participant-level vmPFC search-zone estimate was 0.00012 (SD 0.0561; *t*(53) = 0.015; two-sided nominal *p* = .988). Its 95% interval spans effects in both directions. The most positive voxel in the zone was at (−2, 24, −18) mm (*t* = 4.19), but its whole-brain FWE *p* was .798. The search-zone summary is not an independent atlas-defined ROI test and should not be read as a separate confirmatory result.

![Positive gain-effect voxels surviving whole-brain max-t FWE correction](figures/whole_brain_fwe_anatomical.png)

*Figure 1. Positive one-sample group effects surviving whole-brain max-*t* FWE correction at .05, overlaid on a standard MNI anatomical template. Corrected voxels are posterior and do not overlap the vmPFC search zone.*

![Subject-level estimates in vmPFC search zone](figures/vmPFC_subject_estimates.png)

*Figure 2. Each point is one participant's mean gain-effect estimate within the coordinate-defined vmPFC search zone. The diamond and error bar show the mean and 95% t interval; the dashed line marks zero.*

## Interpretation and limits

These maps contain participant contrast parameter estimates, not standardized test statistics. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution, so coefficients are not change per currency unit. The gain coefficient is also conditional on the upstream choice to model gain and loss in separate models. The study context says gains varied over twice the range of losses, but these maps alone do not estimate an unnormalized response slope per monetary unit or a direct gain-versus-loss contrast.

The group model gives all participants equal weight and uses the between-participant distribution of the supplied estimates; unavailable first-level variance maps prevent a precision-weighted summary-statistic analysis. Permutation inference assumes participant effects are exchangeable under sign changes under the null. The broad coordinate-based vmPFC locator is anatomically approximate. The small corrected occipital clusters should be treated cautiously and do not rescue the vmPFC hypothesis. A non-significant vmPFC result cannot distinguish a genuinely negligible response from a smaller, heterogeneous, or noisily estimated positive response. It also does not generalize beyond this group and this fixed upstream model.

## Reproducibility

Run `python analyze.py` with the prepared environment and supplied inputs. It verifies map checksums, reports quality checks and participant summaries, writes the group maps and voxelwise corrected p map under `results/`, and generates the figures under `figures/`. Key outputs are `results/analysis_summary.json`, `results/fwe_clusters.csv`, `results/vmPFC_search_zone.json`, and the NIfTI maps. The full per-map QC table is `results/participant_qc_summary.csv`.
