# Potential gains and brain activity in the equal-indifference group

## Question and conclusion

Does the BOLD response increase with potential gain in vmPFC? **These supplied maps do not support that vmPFC-specific hypothesis.** The vmPFC estimate is near zero and its participant-level 95% confidence interval includes both negative and positive effects. A whole-brain-corrected positive effect is present elsewhere, at the posterior edge of the brain; that finding does not establish the predicted vmPFC response.

## Methods

I analyzed all 54 equal-indifference participants' unthresholded AO86 gain-effect maps, the complete cohort listed in the supplied metadata. The contrast maps were treated as participant effect estimates, not as t/z maps. At each voxel I estimated the across-participant mean and used a one-sample t statistic (54 independent participants, equal participant weights). This is a random-effects test over participants; participant-specific first-level variances were not supplied, so precision-weighted mixed-effects inference was unavailable.

For the directional positive hypothesis, family-wise error was controlled across the whole common-coverage brain using 5,000 participant-level sign-flip permutations and the maximum positive t statistic per permutation. The test assumes independent participants and a symmetric zero-mean null for sign-flipping. The estimated FWE p value uses the plus-one permutation correction. The common mask was the intersection of nonzero voxels in all 54 maps (198,029 voxels; 2 × 2 × 2.4 mm voxels). Before analysis, I checked that all files match their supplied SHA-256 checksums and byte counts, have finite values, and share the same image grid and affine.

Because no vmPFC atlas mask was supplied, I operationalized the region with a fixed MNI sphere (center [0, 40, −10] mm, radius 10 mm; 428 common-coverage voxels), chosen to sample medial orbital/ventral medial prefrontal cortex. I use the ROI only to summarize the target region; the confirmatory multiplicity control remains the required whole-brain correction. ROI estimates are the average contrast estimate within the sphere for each participant. The confidence interval is a two-sided t interval across participants. An unadjusted Wilcoxon signed-rank test is reported only as a descriptive robustness check.

The upstream model is fixed. Its gain regressor was mean-centered and variance-normalized before HRF convolution, and the supplied maps are its coefficient estimates averaged across four runs. Thus, effects are in the upstream model's BOLD contrast units for a normalized regressor; they are **not** change per currency unit. Response-time-duration trials, separate choice and gain modulators, nonresponse trials, motion, flagged-volume and drift terms, and separate gain/loss models are features of the fixed upstream analysis, not re-estimated here. These choices condition what the maps mean.

## Results

All 54 participants passed the prespecified file/grid/finite-value checks; none were excluded. In the vmPFC sphere, the mean gain effect was −0.0061 (SD across participants 0.1031; SE 0.0140; 95% CI [−0.0342, 0.0221]). Its one-sided unadjusted t-test p value was 0.666; the descriptive one-sided Wilcoxon p value was 0.604. The interval is compatible with a small effect in either direction and is not an equivalence test.

The largest positive whole-brain statistic was t(53) = 6.62 at MNI [−26, −102, −3.6] mm, with max-T FWE p = 0.0010 (5,000 permutations; minimum attainable p = 0.00020). Twenty-four voxels passed voxelwise max-T FWE p < 0.05, forming small posterior clusters (largest: 17 voxels, 163 mm³). None overlapped the vmPFC sphere. The posterior location is not the hypothesized vmPFC location and lies near the back edge of the analyzed field; its anatomical and functional interpretation should therefore be cautious.

![Whole-brain max-T FWE-corrected positive t map. The lime marker shows the vmPFC sphere center; significant voxels occur posteriorly, not at the target.](figures/whole_brain_fwe.png)

![Participant-level average gain-effect estimates within the fixed vmPFC sphere.](figures/vmPFC_participant_estimates.png)

## Interpretation and limits

The result is a lack of support for the *vmPFC-localized* positive gain hypothesis under the specified group model and whole-brain correction. It does not show that vmPFC has exactly zero response, that no participant or subregion responds, or that gain has no effect elsewhere. The interval is broad enough to include small effects of either sign; establishing practical absence would require an equivalence bound and an analysis designed to test it. A compact coordinate sphere may not cover every defensible vmPFC boundary, so the ROI summary is definition-dependent. The whole-brain inference, however, did not yield corrected positive voxels in this defined target.

The unweighted one-sample model cannot use first-level uncertainty, and the sign-flip test relies on participant independence and symmetry. A conventional parametric t model is also sensitive to the distribution of participant estimates. The supplied regressor is normalized, so the coefficient does not identify a response per monetary unit or isolate a causal effect of gain from the task/model context. Finally, no time-series scans or executable participant-level pipeline were re-run; upstream design and modeling limitations remain inherited. The original NARPS instruction specified the positive vmPFC gain hypothesis and whole-brain reporting [NARPS team instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf); the group analysis here follows that correction requirement.

## Reproducibility files

- [`analysis.py`](analysis.py) performs checksum and image QC, group inference, and figure generation.
- [`results/summary.json`](results/summary.json) contains primary and ROI results.
- [`results/participant_qc.tsv`](results/participant_qc.tsv) records participant-level QC summaries.
- [`results/fwe_p_positive_maxT.nii.gz`](results/fwe_p_positive_maxT.nii.gz), [`results/group_t_positive.nii.gz`](results/group_t_positive.nii.gz), and [`results/group_mean_effect.nii.gz`](results/group_mean_effect.nii.gz) contain inferential and descriptive maps.
- [`results/fwe_clusters_p05.tsv`](results/fwe_clusters_p05.tsv) lists corrected clusters; [`results/uncorrected_clusters_p001.tsv`](results/uncorrected_clusters_p001.tsv) is descriptive only.

The analysis ran with the supplied Python 3.13.16 environment (NumPy, SciPy, pandas, NiBabel, Matplotlib, Nilearn). The random seed is fixed in the script. Input provenance, map checksums, and upstream model summary are in `input/sources.json` and `input/upstream-methods.md`.
