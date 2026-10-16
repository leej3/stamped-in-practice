# Potential gains and brain activity

## Question and result

In the 54-person equal-indifference group, the supplied gain-modulator estimates did **not** support a positive group response in vmPFC. A one-sided whole-brain test found no positive voxel surviving familywise error correction (max-T permutation, 5,000 sign flips; peak t(53) = 0.90, MNI [−26, −102, −3.6] mm, FWE p = 1.000; zero voxels at FWE p < .05). The 95th percentile of the permutation maximum-t distribution was 5.39.

As a descriptive, independently defined vmPFC summary, the mean estimate in a 10-mm-radius sphere centered at MNI [0, 40, −10] was −0.0061 cope units (SD across participants = 0.103; 95% t CI [−0.0342, 0.0221]; one-sided uncorrected p = .666; n = 54). The estimate and its interval do not indicate a positive mean response in this sphere. This ROI summary is not a second confirmatory test and is not whole-brain corrected.

![Mean gain-effect cope and unthresholded group t maps; no voxels passed whole-brain correction](figures/group_maps.png)

Participant values in the vmPFC sphere are shown below. The interval is a t-based 95% confidence interval for the group mean.

![Participant vmPFC estimates](figures/vmPFC_participants.png)

## Group analysis

I included every supplied map: all 54 files matched the participant table, all SHA-256 values matched `sources.json`, all images were finite, and all shared the same 97 × 115 × 81 grid and affine (2 × 2 × 2.4 mm voxels). No participants were excluded. For voxelwise inference, I restricted analysis to the 198,029 voxels with nonzero estimates in every participant. This common-support mask prevents outside-brain zero padding from being treated as measured zero effects; voxels outside this intersection were not tested.

The primary statistic was the positive one-sample t statistic across participants at each voxel. I generated 5,000 random participant-level sign flips under the one-sample null, recalculated t maps, and recorded the maximum positive t over the entire common mask for each draw. The corrected p value at each voxel is the proportion of permutation maxima at least as large as its observed t, with the standard plus-one correction. This gives whole-brain familywise error control for the directional hypothesis. The one-sided direction follows the preregistered claim of a positive gain effect in the [original NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf), which required teams to base their yes/no decisions on whole-brain-corrected analysis.

I identified vmPFC anatomically rather than by selecting a peak from these data: the midline anterior ventral prefrontal region was summarized with a 10-mm sphere centered at [0, 40, −10] mm in MNI space. The sphere is a transparent coordinate-based approximation, not a cytoarchitectonic boundary. It was used only for a descriptive estimate and uncertainty interval; the primary decision came from correction across the whole brain, so the hypothesis was not rescued by an uncorrected ROI result.

## Interpretation and limits

These maps are participant-level contrast parameter estimates (cope), not z or t statistics. The group t test tests whether their average is above zero while using between-participant dispersion. Because participant variance maps were not supplied, the analysis cannot weight participants by first-level precision or fit a variance-weighted summary-statistics model. The sign-flip inference assumes independent participants and a symmetric one-sample null. The fixed upstream model is also a limit: its gain modulator was mean-centered and variance-normalized before HRF convolution, so cope units are arbitrary modulator units, not change in BOLD per currency unit. Gain and loss were modeled separately, making this a gain effect conditional on that upstream model. In this group the possible-gain range was twice the possible-loss range; this gain-only analysis cannot establish a gain-versus-loss difference.

The lack of a corrected positive finding means these data and this analysis do not provide sufficient evidence for the hypothesized positive whole-brain response. It does not establish that the true effect is exactly zero, that no participant responds to gain, or that vmPFC is unresponsive under other task/model choices. The vmPFC interval includes modest positive and negative mean effects, so meaningful small effects remain compatible with the ROI summary. The report is limited to the supplied group-analysis inputs; preprocessing and individual models were not rerun.

## Reproducibility files

- `analysis/group_analysis.py` — integrity checks, group inference, ROI summary, maps and figures.
- `results/summary.json` — numerical result summary and software versions.
- `results/input_qc.tsv` — participant-level file, checksum and image checks.
- `results/participant_summary.tsv` — participant summary measures and metadata.
- `results/group_mean_effect.nii.gz`, `results/group_tstat.nii.gz`, `results/group_p_uncorrected.nii.gz`, `results/group_p_fwe_maxT.nii.gz`, `results/group_tstat_fwe_p05.nii.gz` — group maps in the supplied MNI image geometry.
- `figures/group_maps.png`, `figures/vmPFC_participants.png` — report figures.

Reproduce with the prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/group_analysis.py
```
