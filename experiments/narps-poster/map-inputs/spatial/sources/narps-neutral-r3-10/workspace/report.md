# Potential gains and vmPFC activity

## Result

In the 54-person equal-indifference group, the supplied gain-effect maps do **not** support a positive vmPFC response to increasing potential gain. In an independently specified vmPFC valuation sphere (10 mm radius, MNI [0, 40, -8]), the mean participant cope was −0.0057 (SD 0.0983; 95% t interval −0.0326 to 0.0211); 25 of 54 participant means were positive. The one-sided ROI mean test was not significant (nominal *p* = .665). No voxel in the vmPFC sphere survived whole-brain family-wise error correction (the sphere's largest voxel *t* = 1.70; max-*t* FWE *p* = 1.00).

The whole-brain test did identify 24 positive voxels in three small posterior clusters (17, 2, and 5 voxels; 26-neighbor connected), with the strongest peak at MNI [−26, −102, −3.6], *t*(53) = 6.62, FWE *p* = .0012. These posterior findings do not support the vmPFC hypothesis. The whole-brain image displays only the corrected positive voxels; a gold marker shows the vmPFC sphere center.

![Positive gain effects surviving whole-brain correction](results/figures/whole_brain_mean_effect.png)

![Participant vmPFC estimates and group confidence interval](results/figures/vmPFC_participant_estimates.png)

## Analysis

I tested the directional hypothesis with a one-sample group *t* test of the supplied participant cope estimates. For whole-brain inference, I sampled 4,999 sign flips (seed 8601) and compared each observed positive voxelwise *t* to the permutation distribution of the maximum positive *t* across the brain. This single-step max-*t* procedure controls one-sided whole-brain family-wise error at .05; the 95th percentile of the maximum-*t* null was 5.38. The analysis mask was the intersection of the 54 maps' nonzero supports (198,029 voxels), so missing/outside-coverage zeros were not treated as measured null effects. The vmPFC mask was specified independently of these results as a 10 mm sphere around the published valuation-related vmPFC focus near [0, 40, −8] MNI; vmPFC is a broad, variably bounded anatomical label, so this sphere is an explicit operational definition rather than a claim about a unique boundary. The original NARPS instructions call for whole-brain correction when evaluating this hypothesis ([instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)); the vmPFC location is motivated by independent valuation meta-analysis ([Bartra et al., 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3756836/)).

All 54 cohort participants had matching maps. All maps were finite and had identical MNI152NLin2009cAsym grids (97 × 115 × 81; 2 × 2 × 2.4 mm); none were excluded. The ROI mean interval is descriptive and not itself whole-brain corrected. The whole-brain max-*t* result is the confirmatory criterion.

## Interpretation and limitations

A lack of corrected vmPFC support means these supplied maps do not establish the predicted positive group effect at the chosen error rate. It is not evidence that the true effect is exactly zero: the ROI confidence interval includes positive and negative values, and the analysis may have limited sensitivity. A significant posterior effect elsewhere also cannot be taken as confirmation of the vmPFC prediction.

The maps are unthresholded participant **effect estimates (copes)**, not standardized statistics or group maps. AO86 mean-centered and variance-normalized the gain modulator before HRF convolution, so the coefficient does not represent response change per currency unit. Their gain effect is conditional on their specified participant model; gains and losses were fit in separate models. The maps average four runs. No participant variance maps or complete executable first-level pipeline are supplied, so the group analysis gives participants equal weight and cannot propagate first-level uncertainty or reassess upstream modeling choices. Sign-flip inference assumes symmetric participant-level errors under the null; 4,999 sampled flips give a minimum attainable corrected *p* of .0002. Finally, this cohort-specific result does not imply that gain sensitivity is absent in other groups or tasks.

## Reproducibility files

- `scripts/analyze.py` — full group analysis and figure generation.
- `analysis/group_inference.ipynb` — rerunnable notebook that executes the script and displays key results.
- `results/summary.json`, `results/participant_qc.tsv`, `results/vmPFC_participant_values.tsv`, `results/fwe_clusters.tsv` — compact numerical results and quality checks.
- `results/voxelwise_results.tsv.gz`, `results/mean_effect.nii.gz`, `results/t_statistic.nii.gz`, `results/p_fwe.nii.gz`, `results/vmPFC_sphere_mask.nii.gz` — voxelwise outputs and masks.
- `results/figures/` — report figures.

Run from the workspace root with the provided Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/analyze.py
```
