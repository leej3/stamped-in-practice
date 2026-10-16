# Potential gains and brain activity

## Result

In the 54-person equal-indifference group, the whole-brain analysis did **not** support a positive gain effect in vmPFC. The Harvard–Oxford anatomical vmPFC proxy had no voxels surviving positive one-sided max-T familywise correction (FWE p < .05). Its mean participant effect was 0.0027 (SD 0.0891; 95% t interval −0.0217 to 0.0270; t(53) = 0.22; unadjusted one-sided p = .414). The interval includes zero and both small negative and positive effects.

There was a positive corrected result elsewhere: 24 voxels survived whole-brain correction, with peak t(53) = 6.62 at MNI (−26, −102, −3.6), in the Harvard–Oxford Occipital Pole label (FWE p = .0006). The strongest vmPFC-proxy voxel was t = 4.19 at (−2, 24, −18), but its whole-brain FWE p was .780. Thus, the corrected finding does not localize to the hypothesized region.

![Mean unthresholded gain-effect estimates with the vmPFC proxy outlined in white.](results/figures/group_mean_orthogonal.png)

![Positive voxels surviving whole-brain max-T correction.](results/figures/whole_brain_fwe.png)

![Participant-level vmPFC-proxy mean effects and group interval.](results/figures/vmPFC_roi_estimates.png)

## Group analysis

The analysis used the supplied AO86 unthresholded participant contrast parameter estimates. At each voxel, the group model was a one-sample test of the 54 participant estimates against zero, with equal participant weighting. This is a random-effects group test over participants; the estimate is not a test statistic. The gain regressor was mean-centered and variance-normalized upstream, so the group coefficient is **not a change per dollar**. It is also conditional on the upstream choice to model gain and loss in separate models, with response-time event durations and separate choice and gain modulators. It does not isolate a gain effect adjusted simultaneously for loss or establish a causal neural response to money.

For primary inference, we used a positive one-sided sign-flip permutation test with 9,999 random sign patterns and a max-t statistic over the complete common-coverage brain mask. This controls voxelwise familywise error across the whole analyzed brain and matches the positive directional NARPS Hypothesis 1; the original instructions specify a positive vmPFC effect, and NARPS teams reported whole-brain-corrected outcomes ([original instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf); [NARPS study report](https://www.nature.com/articles/s41586-020-2314-9)). The Monte Carlo seed was 20261016. The anatomical vmPFC proxy was defined from the Harvard–Oxford cortical max-probability atlas (25% threshold), combining its Frontal Medial and Subcallosal Cortex parcels. This broad independent anatomical proxy was intersected with the common map coverage. The proxy is an operational definition, not a uniquely agreed boundary for vmPFC. The ROI mean and interval summarize magnitude; the unadjusted ROI p-value is secondary and is not used to claim whole-brain support.

## Input checks, exclusions, and limits

The supplied map paths resolve through Git Annex, and all 54 maps passed the supplied byte-count and SHA-256 checks. IDs matched `participants.tsv`; all maps had the same 97 × 115 × 81 geometry and affine, finite values, and nonempty coverage. No participant was excluded. Nonzero coverage varied across maps, so the voxelwise test used the intersection mask (198,029 voxels; 78.9% of the 251,063-voxel union); this gives every voxel the same 54 participants but leaves some peripheral voxels outside the tested search space. The ROI covered 1,422 voxels within this mask. Leave-one-participant-out ROI estimates remained close to zero (means −0.0022 to 0.0063; one-sided t-test p = .299–.576).

These group estimates have no supplied participant variance maps. The analysis therefore cannot use precision-weighted mixed-effects inference, and it treats participant maps as equally precise. Sign-flip inference relies on independent participants and a symmetric null distribution of participant effects. A non-significant vmPFC result means the data do not provide the required whole-brain-corrected evidence for the predicted positive effect; it does not demonstrate that the true effect is exactly zero or rule out a smaller effect. The ROI interval is not an equivalence test. Conclusions are also limited by the fixed upstream model and its regressor scaling, event-duration and nuisance choices.

## Reproducibility

Run from the workspace with the supplied Python environment:

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 \
  /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analyze.py
```

`analyze.py` verifies source hashes, performs the group test and ROI summary, and writes the maps, QC table, participant ROI values, JSON summary, and figures in `results/`. Key outputs are `results/summary.json`, `results/input_qc.csv`, `results/group_t_map.nii.gz`, `results/fwe_p_map.nii.gz`, and `results/vmPFC_HO_proxy_mask.nii.gz`. The exact input provenance and fixed upstream-methods description are in `input/sources.json` and `input/upstream-methods.md`.
