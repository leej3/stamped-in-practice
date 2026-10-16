# Potential gains and vmPFC activity

## Result

In the 54-person NARPS equal-indifference group, the supplied gain-effect estimates do **not** support a positive response in vmPFC. The mean across participants in the bilateral AAL3 medial orbital frontal parcels (an anatomical vmPFC operationalization) was −0.0078 estimate units (SE 0.0132; 95% t CI −0.0343 to 0.0187). No voxel in those parcels survived the whole-brain family-wise correction. The ROI-average one-sided p = 0.72 is descriptive and is not the basis for the corrected conclusion.

A one-sided whole-brain test did identify 23 corrected voxels elsewhere (max-T critical t = 5.37; observed maximum t = 6.62; max-statistic p = 0.0006). The peak was at MNI [−26, −102, −3.6], at the posterior edge of the analysis mask, not in vmPFC. This whole-brain finding does not support the targeted vmPFC hypothesis.

## Methods

I analyzed all 54 supplied unthresholded participant contrast estimates, with no participant exclusions. Before inference, the code checked map/metadata ID matching, unique IDs, common dimensions and affine, and finite values. Maps shared a 97 × 115 × 81 grid (2 × 2 × 2.4 mm); all had finite values. The analysis mask was the intersection of voxels with nonzero map support in every participant and an independent MNI152 standard brain mask (186,400 voxels). Group inference was a one-sample, one-sided test of the mean participant effect against zero. This is an unweighted random-effects group analysis: because participant variance maps were not supplied, it does not model first-level precision.

To meet NARPS's whole-brain-correction requirement, I used 9,999 participant-level sign flips and the maximum positive t statistic across the full analysis mask (α = .05; seed 20261016). The null assumes participant effects are sign-exchangeable under zero and symmetric around zero. This controls the global-null family-wise error rate over the tested brain mask; it is not a guarantee against violations of the sign-symmetry assumption.

I defined vmPFC a priori as the bilateral `Frontal_Med_Orb` parcels in AAL3 v3.2. AAL3 has an explicit vmPFC parcel definition (`FrontalMedOrb`), which gives a reproducible anatomical test region ([Hsu et al., 2020](https://academic.oup.com/cercor/article/30/11/5830/5858256)); the whole-brain corrected map remains the inferential test, and the parcel is used to localize whether any corrected result is in vmPFC. The atlas was resampled with nearest-neighbor interpolation to the supplied map grid. The NARPS instructions specify a positive vmPFC gain effect in the equal-indifference group and ask teams to make decisions from whole-brain-corrected analyses ([original instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

## Interpretation and limits

This is evidence of **lack of support**, not evidence that the vmPFC response is exactly zero. The ROI confidence interval includes both modest negative and positive average effects; the study may not have enough precision to distinguish small effects from zero. The test is also conditional on AO86's fixed participant model. Its mean-centered, variance-normalized gain modulator does not put coefficients on a per-currency-unit scale. Thus the result concerns the sign and consistency of that modeled gain contrast, not a dollar-by-dollar BOLD slope or a causal effect of changing gain. AO86 modeled gain and loss separately; the gain contrast is conditional on that modeling choice. The supplied maps average four runs, but the participant variance maps and executable first-level pipeline are unavailable, limiting checks of first-level uncertainty and sensitivity to upstream choices.

The gain range in this group was twice the loss range, as described for the task, but this analysis tests only the supplied gain contrast and cannot compare gain and loss coding. A corrected effect at the posterior edge warrants anatomical caution; the supplied data do not identify it as vmPFC activity.

## Figures and reproducibility

- [Figure 1: whole-brain max-T corrected map, cyan outline shows the vmPFC parcels](figures/whole_brain_fwe.png)
- [Figure 2: mean participant gain estimates within vmPFC parcels](figures/vmPFC_roi_effect.png)
- [Figure 3: participant distribution of vmPFC parcel-average effects](figures/participant_effect_distribution.png)
- [Analysis code](analysis/run_analysis.py)
- [Numerical summary](results/summary.json)
- [Participant-level ROI effects](results/participant_vmPFC_effects.tsv)
- [Group mean effect map](results/mean_effect.nii.gz); [t map](results/t_stat.nii.gz); [uncorrected one-sided p map](results/p_uncorrected.nii.gz); [whole-brain corrected significance mask](results/fwe_significant.nii.gz)
- [Analysis run log](results/run.log)

The analysis used Python 3.13.16, NumPy 2.5.4, SciPy, NiBabel 5.4.2, Nilearn 0.14.1, and Matplotlib. Nilearn supplied the standard brain mask and AAL3 atlas; no time-series scans or upstream participant models were downloaded or rerun. The input source and byte checksums are recorded in `input/sources.json`.
