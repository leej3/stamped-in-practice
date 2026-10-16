# Potential gains and brain activity

## Question and finding

In the 54 NARPS equal-indifference participants, the supplied gain-effect maps provide **no corrected evidence of a positive vmPFC response**. The prespecified vmPFC sphere had a near-zero mean contrast estimate (−0.0061; 95% t interval −0.0342 to 0.0221), and no voxel in it survived whole-brain family-wise error (FWE) correction. This is lack of evidence under the supplied model and sample, not evidence of zero effect or equivalence.

A one-sided whole-brain test did identify 24 positive voxels at voxelwise FWE α=.05, in three small posterior foci. The strongest voxel was at MNI [−26, −102, −3.6], t(53)=6.62, max-statistic FWE p=.0006. These findings occur outside the vmPFC target and do not support the specific hypothesis.

| Descriptive 26-connected focus | Voxels | Peak MNI (mm) | Peak t | Voxelwise FWE p |
|---|---:|---|---:|---:|
| 1 | 17 | [−26, −102, −3.6] | 6.62 | .0006 |
| 2 | 2 | [26, −98, −1.2] | 5.76 | .0124 |
| 3 | 5 | [30, −94, −8.4] | 6.19 | .0034 |

The connected foci are descriptive summaries of the voxelwise-corrected map; inference used the maximum statistic over the whole analysis mask, not cluster extent.

![Positive voxels passing whole-brain one-sided FWE correction; slices pass through the strongest peak.](figures/group_t_map.png)

![Participant vmPFC-sphere estimates and descriptive 95% interval.](figures/vmPFC_participant_effects.png)

## Methods

The analysis included every supplied participant map after integrity checks, with one map per participant and exact ID matching to the 54-row equal-indifference metadata table. All 54 SHA256 digests and byte counts matched `input/sources.json`; maps had identical 97×115×81 geometry and affine, and all voxel values were finite. The common analysis mask was the intersection of finite, nonzero voxels across participants (198,029 voxels). No participants were excluded.

At each voxel, a one-sample group t model tested whether the mean participant-level gain contrast estimate exceeded zero. Participants were the independent sampling units. Missing first-level variance maps prevent a variance-weighted second-level analysis, so the model used between-participant variance in an unweighted random-effects group test. For whole-brain control, 9,999 participant-level random sign flips generated a null distribution of the maximum positive t across the mask. The observed max-statistic threshold was t=5.381 at one-sided FWE α=.05; the random seed was 20261016. This sign-flip test relies on participant-level sign exchangeability under a symmetric null. The reported minimum empirical p resolution is 1/10,000.

vmPFC was identified independently of these maps as a 10-mm-radius MNI sphere centered at [0, 40, −10]. This coordinate lies 6.6 mm from the [2, 46, −8] vmPFC focus in a coordinate-based meta-analysis of subjective-value BOLD responses ([Bartra et al., 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3756836/)). This coordinate-based ROI operationalizes anterior vmPFC for localization; it is a deliberately narrow anatomical target, not a comprehensive atlas definition of every vmPFC subregion. The ROI estimate and t-based interval are descriptive; hypothesis support was determined only by the whole-brain corrected test. The voxelwise t statistic was checked against SciPy's independent `ttest_1samp` implementation at seven voxels (maximum absolute difference 2.8×10⁻¹⁷).

## Interpretation and limits

The supplied values are unthresholded first-level contrast parameter estimates, not t/z statistics or group effects. Upstream, the gain regressor was mean-centered and variance-normalized before HRF convolution, response trials used response-time durations, and gain and loss were modeled separately. Thus a positive value means a positive modeled gain-modulator contrast under that specification; it is not a change per currency unit. Because the potential-gain range was twice the loss range, the result also cannot be read as a direct comparison of gain and loss sensitivity. Preprocessing and individual models were fixed and not rerun.

The result does not show that vmPFC has no gain-related activity. An interval spanning zero and no corrected voxel can reflect a small or heterogeneous effect, limited power, spatial mislocalization, the chosen ROI, or upstream-model limitations. The study has no supplied first-level variance maps, motion summaries, or executable upstream pipeline, so those sources of uncertainty could not be independently assessed. The whole-brain posterior foci are not evidence for the vmPFC hypothesis and should be interpreted cautiously given the modest input set and group-level model.

## Reproduction

From this directory, install the pinned environment in [`environment.yml`](environment.yml), then run `python run_analysis.py`. The exact runtime used was Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2, and Nilearn 0.14.1 on macOS arm64. Analysis protocol, executable code, per-map QC, statistical maps, permutation null, and participant ROI summaries are included with this report. The study's original analysis instructions are available [here](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).
