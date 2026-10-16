# Potential monetary gains and vmPFC activity

## Question and conclusion

In the 54-person NARPS equal-indifference group, the supplied gain-effect maps do **not** provide whole-brain-corrected support for an increasing gain-related response in vmPFC. No voxel in the operational medial anterior ventral prefrontal region survived positive one-sided max-T familywise error correction (minimum corrected p = .776). The mean effect across this broad vmPFC region was −0.00055 cope units (95% t interval −0.0183 to 0.0172). This is a lack of corrected evidence for the hypothesized increase, not evidence that the true effect is exactly zero.

The whole-brain analysis did identify 24 positive voxels across three small, posterior clusters (maximum t = 6.62 at MNI [−26, −102, −3.6], max-T FWE p = .0004; whole-brain critical t = 5.37). None of these peaks met the vmPFC bounds. These posterior findings do not answer the vmPFC hypothesis and should be interpreted cautiously given the small extent and unknown first-level precision.

| Cluster | Voxels | Peak MNI (mm) | Peak t | Positive max-T FWE p |
|---:|---:|---:|---:|---:|
| 1 | 17 | [−26, −102, −3.6] | 6.62 | .0004 |
| 2 | 2 | [26, −98, −1.2] | 5.76 | .0130 |
| 3 | 5 | [30, −94, −8.4] | 6.19 | .0028 |

![Whole-brain positive effects surviving voxelwise max-T FWE p ≤ .05](../figures/whole_brain_fwe_glass.png)

## Inputs and effect meaning

I analyzed the 54 supplied AO86 single-participant gain-effect maps and all 54 equal-indifference participants; no participant was excluded. Each map passed the SHA-256 and byte-size checks in `input/sources.json`, had finite values, and shared the same MNI152NLin2009cAsym grid. The common analysis mask was the intersection of nonzero voxels across all maps (198,029 voxels). The group comprised 30 women and 24 men; mean age was 26.1 years (SD 3.0, range 21–37).

These inputs are participant-level contrast parameter estimates, not z/t maps or group statistics. AO86's gain modulator was mean-centered and variance-normalized before HRF convolution, and response trials used response-time durations. Thus, a cope is not a change in BOLD per currency unit. The first-level model also included response-choice and gain modulators, nuisance terms, and separate gain and loss models; the gain effect is conditional on those choices. This analysis does not refit those models or use time-series data. The supplied methods and provenance are documented in [`upstream-methods.md`](../input/upstream-methods.md) and [`sources.json`](../input/sources.json).

## Group model and correction

At each common-mask voxel I fit a positive one-sample t test of participant copes against zero. Participants were treated as independent. With no participant variance maps, the model gives each cope equal weight and estimates uncertainty from between-participant variation; it cannot propagate first-level precision or account for differing cope-estimate variances. This is a group-stage summary-statistic model, not a full precision-weighted mixed-effects analysis.

To satisfy the original whole-brain correction requirement, I used 5,000 random sign flips of the participant maps and the maximum positive t statistic across the entire common mask. Voxelwise familywise p values are (1 + number of null maxima at least as large as observed)/(5,001); alpha was .05, one-sided to match the directional hypothesis. The seed was 864201. Sign-flip inference assumes participant-level effects are independent and their null distribution is symmetric. For descriptive localization, vmPFC was operationally defined as common-mask voxels with |x| ≤ 12, 0 ≤ y ≤ 60, and −20 ≤ z ≤ 10 mm in MNI space, covering medial, anterior, ventral prefrontal territory. These coordinate bounds provide an explicit operational localization because vmPFC has no single universal atlas boundary; they are not an atlas-derived parcel, and the ROI summary is descriptive rather than a separate confirmatory test. All hypothesis support was judged using full-mask correction. Whole-brain peaks were reported in MNI coordinates.

![Participant mean cope within the coordinate-bounded vmPFC region](../figures/vmpfc_participant_effects.png)

## Interpretation and limitations

The broad vmPFC mean is near zero with an interval spanning both negative and positive values, while no voxel there survives whole-brain correction. The data therefore fail to establish the predicted increase at the specified group-analysis threshold. They do not establish equivalence to zero, rule out smaller effects, or show that gain has no neural representation. The interval and unweighted model also reflect only between-participant variation in the supplied first-level estimates.

The source methods note that the gain regressor was normalized and that gain and loss were modeled separately. Therefore these maps cannot establish a per-dollar response, a gain-versus-loss comparison, or an unconfounded causal effect of gain independent of all correlated task properties. Missing first-level variance maps and the incomplete executable upstream pipeline further limit reconstruction and precision-weighted inference. Finally, the coordinate bounds are an operational vmPFC definition rather than a probabilistic atlas boundary; different anatomical boundaries could change the descriptive ROI average. They do not change the full-mask corrected map or the observation that all corrected peaks lie far posterior to vmPFC.

## Reproducibility files

- [`group_analysis.py`](../code/group_analysis.py): complete group analysis, provenance checks, permutation inference, and figure generation.
- [`group_analysis.ipynb`](group_analysis.ipynb): notebook entry point for the analysis.
- [`analysis_summary.json`](../results/analysis_summary.json), [`fwe_clusters.csv`](../results/fwe_clusters.csv), [`vmpfc_descriptive.json`](../results/vmpfc_descriptive.json), [`cohort_summary.json`](../results/cohort_summary.json), and [`input_audit.json`](../results/input_audit.json): numerical results and input checks.
- [group_mean_effect.nii.gz](../results/group_mean_effect.nii.gz), [group_t_positive.nii.gz](../results/group_t_positive.nii.gz), [group_p_fwe_positive.nii.gz](../results/group_p_fwe_positive.nii.gz), and [group_t_fwe05.nii.gz](../results/group_t_fwe05.nii.gz): volumetric result maps.
- [`whole_brain_fwe.png`](../figures/whole_brain_fwe.png), [`whole_brain_fwe_glass.png`](../figures/whole_brain_fwe_glass.png), [`whole_brain_t_unthresholded.png`](../figures/whole_brain_t_unthresholded.png), and [`vmpfc_participant_effects.png`](../figures/vmpfc_participant_effects.png): figures.

The script used Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, NiBabel 5.4.2, and Matplotlib 3.11.2. The study's analysis instructions specify whole-brain correction for this hypothesis ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).
