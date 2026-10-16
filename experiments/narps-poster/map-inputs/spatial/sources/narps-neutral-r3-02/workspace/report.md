# Potential gains and brain activity

## Question and result

In the 54-person NARPS equal-indifference group, the supplied gain-modulator maps do **not** support a greater response in vmPFC under whole-brain family-wise error (FWE) control. The one-sided whole-brain test instead found 24 corrected voxels in three small posterior clusters (peaks at MNI [−26, −102, −3.6], [26, −98, −1.2], and [30, −94, −8.4] mm). These are outside vmPFC and do not answer the hypothesized anatomical prediction. The maximum t was 6.62 (permutation FWE p = .001; 5,000 sign flips, minimum reportable corrected p = 1/5,001). The posterior finding is unexpected and should not be interpreted as evidence about vmPFC.

As a descriptive anatomical check, I defined a broad medial anterior ventral prefrontal coordinate proxy (MNI |x| ≤ 15, y = 0–50, z = −25–0 mm). Its average participant effect was 0.00563 coefficient units (95% t interval −0.0126 to 0.0239; one-sided uncorrected p = .269). This region is only a transparent operational proxy: vmPFC has no single agreed atlas boundary, as noted in the NARPS report ([study methods and ROI definition](https://pmc.ncbi.nlm.nih.gov/articles/PMC7771346/)); the proxy summary is not the confirmatory whole-brain test. It is consistent with the lack of a corrected vmPFC finding.

## Analysis

Each participant contributed one unthresholded gain-effect map, averaged over four runs. I tested whether the equal-weight group mean was positive at each voxel using a one-sample t statistic and 5,000 participant-level sign flips. The largest positive t over the shared brain support on each flip formed a max-t null distribution, controlling one-sided FWE across 198,029 voxels at α = .05. The direction follows the positive gain hypothesis and the original NARPS instructions, which required whole-brain-corrected decisions ([NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). A t-statistic implementation check against SciPy agreed at 17 fixed sampled voxels.

QC confirmed 54 unique map IDs exactly matching the participant table, no exclusions, finite data in every image, and matching 97 × 115 × 81 geometry and MNI affine. The tested mask is the intersection of voxels nonzero in all maps, avoiding treating outside-mask zeros or unequal edge coverage as observations. Full parameters, checksums, and runtime identity are in `results/summary.json`.

## Interpretation and limits

These inputs are participant contrast parameter estimates, not standardized statistics. In the fixed AO86 first-level model, gain was centered and variance-normalized before HRF convolution, so coefficients cannot be read as response change per currency unit. Response-time-duration trials, choice and gain modulators, separate gain/loss models, and run combination are upstream choices held fixed here. Therefore the group result is conditional on that model and does not isolate a causal effect of monetary gain from other task features.

The group t model weights participants equally because participant variance maps were not supplied; it cannot propagate uncertainty in the individual estimates. Sign-flip inference assumes exchangeable, approximately symmetric participant effects under the null. The 54 participants are the complete supplied group, but the sample still limits sensitivity. No corrected vmPFC result is not proof of no vmPFC effect: a smaller effect may be missed, and this analysis is not an equivalence test. The posterior clusters warrant independent follow-up and are not a basis for revising the hypothesis.

## Reproduction

Run `pixi install` then `pixi run analyze`. See `analysis/protocol.md`, `analysis/run_analysis.py`, and `README.md` for model details, inputs, and outputs. The fixed upstream methods and source provenance are in `input/upstream-methods.md` and `input/sources.json`.

## Figures

![Mean participant gain-effect coefficients in coefficient units, not currency units](figures/mean_gain_effect.png)

![Whole-brain positive t map thresholded at the permutation max-t FWE critical value](figures/wholebrain_fwe_peak.png)

![Participant variation in the descriptive vmPFC coordinate proxy](figures/vmPFC_proxy_distribution.png)
