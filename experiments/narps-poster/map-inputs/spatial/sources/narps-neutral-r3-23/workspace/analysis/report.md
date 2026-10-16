# Potential gains and brain activity in the NARPS equal-indifference group

## Result

**The supplied gain-effect maps do not support a greater vmPFC response with increasing potential gain.** In the a priori vmPFC region, the average participant cope was −0.006 (95% CI −0.032 to 0.019; one-sample *t*(53)=−0.48; one-sided sign-flip *p*=.681). No vmPFC voxels survived the required whole-brain family-wise error (FWE) correction.

The one-sided whole-brain test did find 24 FWE-significant voxels in three small posterior occipital clusters (17, 2, and 5 voxels). The peak was at MNI (−26, −102, −3.6) mm (*t*=6.62, max-*t* FWE *p*=.0006). These findings do not localize to vmPFC and do not support the hypothesis as posed. The vmPFC ROI's largest observed *t* was 2.45 at (10, 36, −18) mm, but its whole-brain corrected *p* exceeded .05.

A lack of support here means the maps and this group model did not provide evidence for a positive vmPFC effect under a whole-brain-corrected decision rule. It does not show that the true effect is exactly zero or exclude smaller effects; the ROI confidence interval spans both signs, and no equivalence bound was specified.

## Methods

The complete equal-indifference cohort was analyzed: 54 participants (age mean 26.06, SD 3.05 years; 30 F, 24 M in the supplied metadata). All 54 supplied cope images had matching dimensions and affine, and all voxels were finite. No participants were excluded. The common-support whole-brain mask comprised 210,968 voxels, requiring nonzero cope support in at least 49/54 maps (90%). Per-map nonzero support ranged from 217,625 to 232,390 voxels. These checks detect geometry, missing-data, and support problems; they do not validate the original participant models.

At each masked voxel, the group estimate was the unweighted mean of the 54 participant cope maps, with a one-sample *t* statistic against zero. Positive effects were tested using 9,999 participant-level random sign flips (seed 20261016). The primary inference used the maximum *t* across all masked voxels in each permutation, controlling one-sided whole-brain FWE at α=.05. The Monte Carlo corrected *p* uses the plus-one correction. This max-statistic test is deliberately whole-brain; vmPFC was not treated as an independently corrected small-volume test.

For anatomical localization, vmPFC was operationalized before inspecting effects as a bilateral medial, anterior, ventral MNI coordinate region (|x|≤10, y=30–60, z=−20–0 mm; 1,408 masked voxels). This coordinate-defined mask is independent of the observed maps and makes the anatomical decision explicit. vmPFC boundaries vary across atlases and subregions, so it is a practical region definition rather than a claim that it captures every vmPFC parcel. The ROI mean and its *t*-based CI are descriptive; whole-brain max-*t* remains the hypothesis decision. The source instructions require a binary decision based on whole-brain-corrected analysis ([NARPS original instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

## Interpretation and limitations

These are participant contrast parameter estimates (copes), not standardized test statistics or group results. In the upstream model the gain regressor was mean-centered and variance-normalized before HRF convolution, so the cope is not a change in BOLD per currency unit. The gain range was twice the loss range; consequently this result cannot be read as a direct gain-versus-loss sensitivity comparison. Gain and loss were modeled separately, making the gain cope conditional on that modeling choice. Response-trial durations, response-choice modulators, flagged volumes, motion, and drift were handled upstream as described in [`input/upstream-methods.md`](../input/upstream-methods.md); these fixed choices were not revisited.

The participant variance maps and executable upstream pipeline were unavailable. The group analysis therefore weights participant copes equally and cannot use a precision-weighted mixed-effects model or propagate uncertainty from each participant's first-level estimate. Sign-flip inference assumes participant effects are exchangeable under sign reversal under the null; the 9,999 permutations approximate the null distribution. The coordinate ROI is one defensible vmPFC operationalization, but other boundaries could alter its ROI-average estimate. Finally, the posterior clusters are whole-brain statistical associations and do not by themselves establish a specific perceptual or cognitive mechanism.

## Reproducibility and files

Run from the workspace root with the prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/analyze.py
```

The analysis code is [`analyze.py`](analyze.py); a notebook entry point is [`group_analysis.ipynb`](group_analysis.ipynb). Machine-readable statistics, participant QC, peak and cluster tables, and unthresholded group maps are in [`results/`](results/). Figures are [`wholebrain_mean_and_fwe.png`](figures/wholebrain_mean_and_fwe.png) and [`vmPFC_participant_effects.png`](figures/vmPFC_participant_effects.png).
