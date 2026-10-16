# Potential monetary gain and vmPFC activity

## Conclusion

In the 54-person NARPS equal-indifference group, these data do **not** support a positive gain-related response in vmPFC under the required whole-brain family-wise error (FWE) criterion. In an independently defined 10 mm sphere centered at MNI [0, 40, -12], the mean participant gain effect was -0.0054 COPE units (95% t interval -0.0346 to 0.0237; one-sided uncorrected p = .645). The largest t statistic inside the sphere was 1.70; its whole-brain max-t FWE p-value was 1.00. The interval includes zero and the point estimate is near zero.

The positive whole-brain analysis did find 24 FWE-significant voxels in three small components near posterior/inferior cerebellar coordinates (peaks: [-26, -102, -3.6], [26, -98, -1.2], and [30, -94, -8.4] mm). None overlaps the vmPFC sphere. These findings outside the target do not support the vmPFC hypothesis.

![Positive whole-brain clusters surviving max-t FWE correction](figures/group_t_map_fwe.png)

![Participant mean effects in the vmPFC sphere](figures/vmPFC_effects.png)

## Analysis

The supplied unthresholded AO86 participant COPE maps were treated as fixed first-level estimates. All 54 equal-indifference participants in the supplied table were included; no exclusions were made. SHA-256 and byte counts matched the manifest for all maps; maps had the same MNI152NLin2009cAsym grid (97 x 115 x 81 voxels; 2 x 2 x 2.4 mm) and contained no nonfinite values. Voxelwise inference used the all-participant nonzero common support (198,029 voxels), keeping the sample size constant across the search volume.

The group model was an unweighted one-sample random-effects t test of participant COPEs against zero. First-level variance maps are unavailable, so precision-weighted mixed-effects inference was not possible. The directional hypothesis was tested with 4,999 random participant sign flips and the maximum positive t statistic across the entire common brain support (seed 20261016); this controls voxelwise whole-brain FWE at alpha .05. The 95th percentile of the permutation maximum-t distribution was t = 5.397. This permutation test assumes independent participants and a symmetric null distribution of participant effects.

The vmPFC was operationalized before examining the group map as a 10 mm-radius sphere centered at MNI [0, 40, -12], a compact medial orbitofrontal/vmPFC location. This anatomically defined ROI provides a clear location check and a descriptive estimate; it does not replace the whole-brain corrected test required by the NARPS instructions. The ROI interval is a participant-level t interval, and the displayed one-sided ROI p-value is uncorrected. Whole-brain FWE p-values are the inferential basis for support.

## Interpretation and limits

The COPEs estimate modulation by the upstream mean-centered, variance-normalized gain regressor after HRF convolution. They are not a response change per dollar and do not directly measure neural firing. The upstream model used response-time durations, a separate response-choice term, and separate gain and loss models; the supplied gain effect is conditional on those modeling decisions. We did not refit or alter the upstream model.

The lack of corrected vmPFC support means that this analysis does not establish a positive gain effect in vmPFC. It does not establish that the true effect is exactly zero: the ROI confidence interval allows small positive and negative effects, and uncertainty from the individual models cannot be propagated because their variance maps are absent. The result is also conditional on the supplied AO86 modeling pipeline and the selected anatomical ROI. The small corrected clusters outside vmPFC should be treated as secondary findings rather than evidence for the target hypothesis.

The whole-brain correction follows the original NARPS analysis instructions for Hypothesis 1 ([instructions for analysis teams](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). Input image URLs, checksums, cohort provenance, and upstream methods are recorded in [`input/sources.json`](input/sources.json) and [`input/upstream-methods.md`](input/upstream-methods.md).

## Reproducibility

Run `analysis/analyze.py` from this workspace with the provided Python 3.13.16 environment. It writes the tables and NIfTI maps in `results/` and figures in `figures/`. The notebook at [`analysis/group_analysis.ipynb`](analysis/group_analysis.ipynb) documents and runs the same analysis. The key numeric outputs are in [`results/summary.tsv`](results/summary.tsv) and [`results/fwe_clusters.tsv`](results/fwe_clusters.tsv); participant-level input checks are in [`results/input_qc.tsv`](results/input_qc.tsv).

Software: NumPy 2.5.4, SciPy 1.18.1, NiBabel 5.4.2, Nilearn 0.14.1, pandas 3.0.6, and Matplotlib 3.11.2.
