# Potential monetary gain and brain activity

## Result

**The supplied maps do not support a greater vmPFC response with increasing potential gain in the NARPS equal-indifference group.** The prespecified Harvard-Oxford vmPFC estimate was slightly negative (mean participant effect = −0.0108; 95% CI [−0.0304, 0.0089]); the strongest vmPFC voxel had one-sided whole-brain FWE-corrected p = .777. The confidence interval includes zero, so these data do not establish that the response is absent.

The one-sided whole-brain test did identify 23 voxels surviving maximum-t family-wise error correction at α = .05. The peak was in left occipital pole (MNI [−26, −102, −3.6] mm; t(53) = 6.62; mean effect = 0.1121; pFWE = .0008). This corrected finding is outside the hypothesized vmPFC and therefore does not support Hypothesis 1 as posed. It is reported as a secondary whole-brain result, not as evidence for a vmPFC effect.

![One-sided whole-brain maximum-t FWE map; cyan outlines the independent vmPFC ROI.](figures/group_fwe_maxT.png)

**Figure 1.** Voxelwise −log10(FWE-corrected p) from 10,000 sign-flip permutations. The line at 1.301 marks pFWE = .05. The strongest corrected response lies in occipital pole; no corrected voxels overlap the vmPFC ROI.

![Participant-level vmPFC effect estimates and group confidence interval.](figures/vmPFC_participant_estimates.png)

**Figure 2.** Each point is a participant's mean cope estimate in the atlas-defined vmPFC. The shaded band is a t-based 95% confidence interval for the group mean.

## Methods

I analyzed the 54 supplied unthresholded AO86 participant gain-effect maps and the matching equal-indifference cohort table. The upstream preprocessing and participant model were treated as fixed. Before analysis, the code checked participant IDs, file checksums against `input/sources.json`, common image dimensions and affine, and finite voxel values. All 54 files passed; no participant was excluded.

The group model was a one-sample intercept model testing whether the mean participant gain-effect estimate was positive. Participants were treated as independent observations. No age or gender covariates were added because the target is the group's mean effect, and no participant variance maps were supplied for precision-weighted inference. The search mask was the intersection of nonzero support in every participant map and the Nilearn MNI152 2 mm anatomical brain mask, nearest-neighbor resampled to the supplied MNI152NLin2009cAsym grid. This avoids coding map-edge missing coverage as zero and excludes nonbrain voxels. The resulting search space contained 186,400 voxels (1,789 cm³).

To identify vmPFC independently of the observed effects, I used a fixed anatomical ROI consisting of Harvard-Oxford cortical max-probability atlas labels Frontal Medial, Subcallosal, and Paracingulate (labels 25, 27, and 28), intersected with the group mask. This operational definition covers medial prefrontal and adjoining subgenual/paracingulate territories; the atlas is distributed in MNI152NLin6Asym and was resampled to the maps. This ROI is used to localize and summarize the hypothesis, while the hypothesis decision uses whole-brain correction as required by the [NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). The one-sided maximum-t permutation procedure controls voxelwise family-wise error across the entire search mask ([Nilearn implementation](https://nilearn.github.io/stable/modules/generated/nilearn.glm.second_level.non_parametric_inference.html)); 10,000 permutations were run with seed 20261016. The test was directional because the stated hypothesis predicts a positive response.

The ROI estimate is the unweighted mean of each participant's cope values within the ROI. The reported interval is a conventional one-sample t confidence interval across 54 participant summaries; the unadjusted one-sided ROI p-value (.862) is descriptive and was not used to claim support. The best vmPFC voxel's maximum-t corrected p-value (.777) provides a directly multiplicity-adjusted check within the whole-brain test.

## Interpretation and limits

The supplied participant maps are contrast parameter estimates, not z/t statistics or group results. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution, so its coefficient is not a response change per dollar (or other currency unit). Potential gains also spanned twice the range of potential losses. The map estimates covariation with that gain modulator during response periods under the upstream model; they do not by themselves establish a causal neural response to monetary value. Gain and loss were modeled separately upstream, so this gain effect is conditional on that modeling choice.

Without participant-level variance maps, the group analysis cannot weight participants by first-level precision or fully propagate first-level uncertainty. The one-sample model summarizes variation among the 54 participant effects, and its permutation test assumes independent participants and sign-exchangeability under the null. The vmPFC ROI is an atlas-based approximation rather than a universally agreed boundary, and atlas-to-map resampling introduces some spatial uncertainty. A failure to find vmPFC support means this analysis did not detect the predicted positive effect at the prespecified whole-brain FWE threshold; it is not proof of a zero effect. No equivalence bound was specified, and the ROI interval still allows a small positive mean.

## Reproduction and files

Run from the workspace root with the prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/group_analysis.py
```

The script verifies inputs, reruns inference, writes the summary and participant QC/ROI table, saves unthresholded group mean and t maps plus the corrected p map, and regenerates the figures. Analysis used Python 3.13.16, Nilearn 0.14.1, NiBabel 5.4.2, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, and Matplotlib 3.11.2.

- `scripts/group_analysis.py` — complete group analysis and figure generation.
- `results/summary.json` — model, ROI, correction, and peak results.
- `results/participant_qc_and_roi.csv` — checksum and map QC summaries plus each participant's ROI estimate.
- `results/group_t_unthresholded.nii.gz`, `results/group_mean_effect.nii.gz`, `results/group_log10p_fwe_maxT.nii.gz` — unthresholded group maps and voxelwise corrected evidence.
- `figures/group_tmap_vmPFC.png`, `figures/group_fwe_maxT.png`, `figures/vmPFC_participant_estimates.png` — figures.

## References

- [NARPS analysis team instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).
- [Nilearn permutation inference](https://nilearn.github.io/stable/modules/generated/nilearn.glm.second_level.non_parametric_inference.html).
- [Nilearn Harvard-Oxford atlas documentation](https://nilearn.github.io/stable/modules/description/harvard_oxford.html).
