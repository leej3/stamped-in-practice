# Potential gain and brain activity in the NARPS equal-indifference group

## Question and answer

Does the participant-level gain effect increase in vmPFC? In this group-level analysis, **we found no whole-brain-corrected evidence for a positive vmPFC response**. None of the 24 voxels passing one-sided whole-brain correction overlapped our anatomically defined vmPFC approximation. The ROI-average coefficient was near zero (mean −0.0011 arbitrary model units; 95% t interval −0.0228 to 0.0207). This is a failure to find corrected support for the hypothesis, not evidence that the true response is exactly zero.

## Methods

The input was the complete set of 54 AO86 participant gain-effect maps for the equal-indifference group in MNI152NLin2009cAsym space. We tested the group mean coefficient against zero at each voxel using a one-sample t statistic, with a one-sided positive alternative. Inference used 5,000 synchronized participant-level sign flips (seed 20261015). For each flip, we retained the largest positive t over the whole analysis mask. The resulting maximum-t distribution controls voxelwise family-wise error at 0.05 across the whole brain; the observed critical value was **t = 5.36**. This studentized sign-flip test treats participants as the sampling units and does not require a parametric spatial smoothness model. It does assume participant effects are exchangeable under the null (approximately symmetric about zero). The cluster table reports connected components of voxels passing voxelwise correction; cluster extent was not itself the correction statistic.

The mask is the intersection of nonzero estimation support across all 54 maps (198,029 voxels; 1,901 ml). Zeros outside an individual's estimation mask were therefore not interpreted as zero effects. We used the Harvard-Oxford cortical max-probability atlas at its 25% threshold as an anatomical localization aid. Our transparent vmPFC approximation combines Frontal Medial, Subcallosal, Frontal Orbital, and Paracingulate labels, restricted to |MNI x| ≤ 20 mm, y ≥ 0 mm, and z ≤ 0 mm, then intersects that region with the group mask (2,203 voxels). There is no agreed anatomical boundary for vmPFC; this atlas-based approximation is not identical to the original NARPS paper's combination of Harvard-Oxford regions and a Neurosynth map. We used whole-brain corrected inference for the hypothesis and report ROI summaries descriptively.

These are group tests of supplied participant coefficient maps, not re-estimates from time series. In the equal-indifference group, the range of potential gains was twice the range of potential losses. The fixed upstream model mean-centered and variance-normalized the gain regressor before HRF convolution; a coefficient is therefore not change in BOLD per currency unit. Upstream effects were averaged across four runs; gain and loss were modeled separately, so this analysis does not compare their slopes. No participant-level variance maps were supplied, so the group analysis cannot use precision-weighted mixed-effects estimates or propagate uncertainty from each participant's first-level model.

## Results

All 54 maps passed SHA-256 verification against `input/sources.json`, had finite values, and shared the same spatial grid. No participant was excluded. Whole-brain correction identified 24 positive voxels in three small posterior clusters. The peak was **t = 6.62**, whole-brain FWE **p = 0.0008**, at MNI **(−26, −102, −3.6)**; no corrected cluster overlapped the vmPFC approximation. This posterior finding is outside the hypothesized region and does not support Hypothesis 1.

The vmPFC approximation's mean across participants was −0.0011 (SD 0.0796; 95% t interval −0.0228 to 0.0207); 25/54 participant ROI means were positive. The strongest voxel in the ROI had **t = 4.19**, whole-brain FWE **p = 0.788**. The one-sample ROI summary and its interval are descriptive and do not replace the required whole-brain-corrected test.

![One-sided t map. The display threshold is uncorrected p < .001 for visualization; hypothesis inference uses the whole-brain max-t correction described above.](figures/whole_brain_gain_t_map.png)

*Figure 1. Group t map on the MNI template. The color overlay is shown at an uncorrected one-sided display threshold (p < .001); it is not the inferential threshold. The whole-brain max-t threshold is t = 5.36. Corrected positive voxels are posterior; none are in vmPFC.*

![Participant mean coefficients within the vmPFC atlas approximation.](figures/vmPFC_participant_effects.png)

*Figure 2. Each point is one participant's mean coefficient over the vmPFC approximation. The diamond and interval show the group mean and 95% t interval in arbitrary model units.*

## Interpretation and limitations

The data do not provide whole-brain-corrected support for increased vmPFC activity with potential gain in this group. The interval remains compatible with small positive or negative mean coefficients, and this analysis was not an equivalence test. Thus, lack of support does not show that vmPFC is unresponsive, that potential gain has no behavioral value, or that the effect is absent under another model or contrast. N=54, first-level measurement error is unavailable, and the upstream gain coefficient reflects a normalized regressor in a separate gain model. The vmPFC approximation is necessarily operational; a different defensible boundary could change the ROI summary, while the whole-brain corrected test avoids relying on that boundary for its primary conclusion.

## Reproducibility and files

- Analysis script: [`analysis/run_group_analysis.py`](../analysis/run_group_analysis.py)
- Machine-readable results: [`group_results.json`](group_results.json)
- Corrected clusters: [`fwe_clusters.tsv`](fwe_clusters.tsv)
- Input quality checks: [`map_quality.tsv`](map_quality.tsv)
- Participant ROI means: [`vmPFC_participant_means.tsv`](vmPFC_participant_means.tsv)
- NIfTI outputs: mean coefficient, SD, t, whole-brain FWE p, corrected mask, group support mask, and vmPFC approximation mask in this directory.
- Complete command metadata, stdout/stderr, resource samples, and run summaries: `logs/` in the repository. Failed attempts are retained there as well.

The original NARPS instructions specify a positive vmPFC effect for Hypothesis 1 and the equal-indifference group ([instructions PDF](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). The NARPS report describes the lack of a single agreed vmPFC boundary and its use of atlas plus Neurosynth information ([NARPS paper](https://www.nature.com/articles/s41586-020-2314-9)). The atlas labels were obtained through Nilearn's [Harvard-Oxford dataset interface](https://nilearn.github.io/stable/modules/datasets.html).
