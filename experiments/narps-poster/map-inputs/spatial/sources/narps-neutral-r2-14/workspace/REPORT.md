# Potential monetary gain and brain activity

## Question and result

In the 54-person NARPS equal-indifference group, where the potential gain range was twice the loss range, the supplied gain-effect maps do **not** support a positive vmPFC response to increasing potential gain under whole-brain corrected inference. The bilateral medial orbitofrontal vmPFC proxy contained no voxel surviving the positive whole-brain max-*t* family-wise threshold. Its participant-averaged estimate was slightly negative (mean −0.0081, SD 0.0983; 95% *t* interval [−0.0349, 0.0187], in upstream coefficient units). This interval and its uncorrected one-sided *p* = 0.274 are descriptive; the hypothesis decision is based on the whole-brain analysis.

Elsewhere, 24 voxels in three small posterior occipital clusters survived whole-brain correction (largest *t* = 6.62; empirical max-*t* FWE *p* = 0.001). Their peaks were at MNI (−26, −102, −3.6), (26, −98, −1.2), and (30, −94, −8.4) mm. None overlapped the vmPFC proxy. These off-target findings do not support the vmPFC hypothesis and should be interpreted cautiously; cluster extents are descriptive, not cluster-level tests.

**Conclusion:** no whole-brain-corrected evidence here for the predicted positive gain effect in vmPFC. This is not evidence that the true effect is exactly zero: a weak or spatially focal effect may be undetected, and the result depends on the supplied participant model and the specified group test.

![Unthresholded group t map displayed at t greater than 2, centered on the anatomical vmPFC proxy](figures/group_t_map.png)

![Voxels surviving positive whole-brain max-t FWE correction](figures/group_fwe05.png)

![Distribution of participant-averaged vmPFC proxy estimates](figures/roi_participant_distribution.png)

## Group model and quality checks

The original NARPS instructions state a positive vmPFC hypothesis for the equal-indifference group and request a whole-brain-corrected decision and group statistical maps ([instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). I used a one-sided, one-sample *t* test of the participant effect estimates against zero, with participant-wise random sign flips and a maximum-*t* statistic over the full analysis mask. This controls voxelwise family-wise error at .05 under the null sign-symmetry assumption. The positive, directional test matches the stated hypothesis. It used 4,999 sign-flip permutations (seed 20261016; minimum possible empirical *p* = 1/5,000); the 95th-percentile max-*t* threshold was 5.404.

The vmPFC localization was defined before inspecting group effects as the intersection of the analysis mask with bilateral `Frontal_Med_Orb` parcels in AAL3v2, an anatomical medial orbitofrontal proxy rather than a uniquely standardized vmPFC boundary ([AAL3 description](https://doi.org/10.1016/j.neuroimage.2019.116189)). The whole-brain correction, rather than an ROI-only *p* value, determines support for the hypothesis. This narrow anatomical proxy may not include every definition of vmPFC.

All 54 participants were retained; there were no exclusions. The code verified exact participant-ID correspondence, each map's SHA256 and byte count against the supplied manifest, finite voxel values, and identical 97 × 115 × 81 voxel grids and affines. The analysis mask included voxels nonzero in at least 90% of maps (210,968 voxels). No additional spatial smoothing was applied. Input checksums and per-map coverage/range checks are in `results/input_checksums.tsv` and `results/map_qc.tsv`.

Because participant variance maps were not supplied, the group test gives equal weight to each participant's effect estimate; a variance-weighted mixed-effects analysis was not possible. Permutation calibration avoids relying on a parametric *t* null but still relies on sign symmetry and independent participants. The supplied coefficients are from a mean-centered, variance-normalized gain modulator and cannot be read as BOLD change per unit of currency. They are conditional on the fixed upstream model: gain and loss were modeled separately, and response-time duration, response choice, motion, flagged volumes, and drift were included upstream. These maps therefore test the group mean of that model's gain-modulator coefficient, not a newly estimated raw gain slope, a causal neural effect, or a direct behavioral valuation parameter.

## Reproducibility

Run from the workspace root with the supplied Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/group_analysis.py --permutations 4999 --seed 20261016
```

The script saves the unthresholded group mean and *t* map, voxelwise max-*t* FWE *p* map, corrected binary map, analysis and vmPFC masks, permutation maxima, cluster summary, participant ROI estimates, QC tables, and figures. `results/summary.json` contains the main statistics. `notebooks/narps_gain_group.ipynb` is an executed results viewer; `code/group_analysis.py` is the executable analysis. No time-series scans or upstream analyses were used.
