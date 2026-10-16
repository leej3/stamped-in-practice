# Potential gains and vmPFC activity

## Question and result

In the NARPS equal-indifference group, the supplied participant maps do **not** support a greater vmPFC response with increasing potential gain under a whole-brain corrected test. The group mean effect within the independently defined vmPFC mask was slightly negative (mean participant ROI estimate = −0.017 cope; 95% t interval −0.038 to 0.004; one-sided ROI *p* = .949). No voxel in vmPFC survived whole-brain family-wise error (FWE) correction. This is a lack of corrected support for the predicted positive effect, not evidence that the true effect is exactly zero.

Across the 184,315 voxel analysis mask, 24 voxels passed positive whole-brain max-*T* correction at FWE *p* < .05. The peak was at MNI [−26, −102, −3.6] mm (*t*(53) = 6.62, uncorrected one-sided *p* = 9.3 × 10⁻⁹, max-*T* FWE *p* = .00050), outside the vmPFC mask. This posterior finding does not support the vmPFC hypothesis and should be interpreted cautiously as a secondary observation.

![Group mean cope and positive group t statistic near vmPFC](results/group_maps.png)

**Figure 1.** Group mean participant effect estimates and positive one-sample *t* values in orthogonal slices through vmPFC. The unthresholded *t* map is shown for localization; no vmPFC voxel passes the whole-brain max-*T* threshold. Values are cope units, not change per unit of currency.

![Participant mean effect estimates in vmPFC](results/vmPFC_subject_effects.png)

**Figure 2.** Each point is one participant's spatial mean cope across the vmPFC mask; the horizontal colored line is the group mean. The ROI summary is descriptive and does not substitute for the required whole-brain inference.

## Group analysis

The fixed upstream inputs were the 54 unthresholded AO86 gain cope maps for the complete equal-indifference cohort. Each map is a participant-level contrast parameter estimate averaged over four runs, rather than a *z* statistic, group statistic, or variance image. We fit a one-sample random-effects group model to the cope maps, testing the prespecified positive direction against zero with a studentized *t* statistic. Participants received equal weight because participant variance maps were unavailable.

Whole-brain FWE control used 10,000 Monte Carlo sign-flips of participant maps, with the maximum positive *t* over the analysis mask recorded for each permutation. The mask included voxels nonzero in at least 90% of participants and with at least 5% probability in the union of Harvard–Oxford cortical and subcortical atlas labels. Its 184,315 voxels covered the shared brain volume at the maps' MNI152NLin2009cAsym grid. The 95th percentile of the null maximum-*T* distribution was *t* = 5.36. Corrected *p* values use the plus-one estimate; with 10,000 permutations the minimum resolvable value is 1/10,001. Sign-flipping assumes symmetric participant errors under the null.

vmPFC was identified independently of the observed results using Harvard–Oxford cortical atlas labels Frontal Medial Cortex, Subcallosal Cortex, and Frontal Orbital Cortex at 25% probability, restricted to the medial band |*x*| ≤ 20 mm. This broad operational definition produced 4,639 in-mask voxels. The atlas mask is used to describe localization only: the hypothesis decision is based on whole-brain corrected inference, as required by the NARPS instructions, rather than an ROI-only threshold.

## Data checks, exclusions, and limits

All 54 expected participant IDs matched between metadata and maps. Every map's retrieved byte count and SHA-256 matched `input/sources.json`; maps had matching dimensions and affine, and all voxel values were finite. Maps not materialized from the supplied annex links are retained in `input/retrieved_maps/`. No participants were excluded. Age and gender were not used as covariates because the target is the mean effect in the specified complete group, and they are not part of the stated hypothesis.

The supplied gain modulator was mean-centered and variance-normalized before HRF convolution. Therefore, cope values do not measure BOLD change per ILS and cannot be read as a calibrated dose-response per currency unit. The gain estimate is conditional on the upstream model choice to fit gains and losses separately. The fixed upstream choices, absence of participant variance maps, and lack of an executable upstream pipeline prevent us from checking trial-level model fit, revising the regressor, incorporating first-level uncertainty, or testing alternative upstream specifications. The standard group interval and sign-flip inference also rely on between-participant assumptions that cannot be checked fully from these maps alone.

Accordingly, no corrected vmPFC result means that these data and this fixed pipeline provide insufficient evidence for the predicted positive group effect. It does not establish that no vmPFC response exists, rule out a smaller effect, or show what would happen under a different task model, sample, or gain/loss specification.

## Reproducibility

Run `analysis/run_group_analysis.py` with the prepared Python environment (NumPy, SciPy, pandas, Matplotlib, NiBabel, Nilearn). Set `NILEARN_DATA` to a workspace-local directory; set `NARPS_N_PERM` to override the default of 10,000 permutations. The script writes the numerical summary and group maps under `results/`.

Key outputs: [analysis code](analysis/run_group_analysis.py), [machine-readable results](results/analysis_results.json), [participant ROI estimates](results/vmPFC_subject_effects.tsv), [group mean cope map](results/group_mean_cope.nii.gz), [group *t* map](results/group_t_positive.nii.gz), and [whole-brain corrected *p* map](results/group_p_fwe_positive.nii.gz).

## Sources

- [NARPS instructions for analysis teams, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) (whole-brain corrected hypothesis decisions).
- [NARPS mixed-gambles dataset description](https://www.nature.com/articles/s41597-019-0113-7).
- [Harvard–Oxford atlas documentation](https://nilearn.github.io/stable/modules/generated/nilearn.datasets.fetch_atlas_harvard_oxford.html).
- Fixed upstream analysis details and data provenance are included in [`input/upstream-methods.md`](input/upstream-methods.md) and [`input/sources.json`](input/sources.json).
