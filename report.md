# Potential monetary gain and brain activity

## Question and conclusion

In the 54-person NARPS equal-indifference group, we found **no support for a greater vmPFC response as potential gain increased** under whole-brain family-wise error (FWE) correction. A small set of positive voxels survived correction in posterior brain regions, but none fell in our independently defined vmPFC region. This is a lack of corrected evidence for the proposed vmPFC effect; it does not establish that the effect is exactly zero.

## Inputs and group model

We analyzed the supplied, unthresholded AO86 participant gain-effect maps for all 54 participants listed as `equalIndifference` in `input/participants.tsv`. Upstream preprocessing and participant modeling were treated as fixed, as requested; no time-series data were used. The original NARPS instructions describe this as a positive parametric gain effect in vmPFC and require whole-brain-corrected group inference ([original instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

Each input is a participant contrast parameter estimate (COPE), not a t or z statistic and not a group result. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution, so these estimates are **not response changes per currency unit**. The equal-indifference task used a gain range twice as wide as its loss range; that context does not convert this gain coefficient into a gain-versus-loss comparison. Gain and loss were modeled separately upstream, so this effect is conditional on that modeling choice.

At group level, we tested whether the mean participant effect was greater than zero at each voxel using a one-sample t statistic. We used participant-wise sign flips to generate 5,000 null samples and a maximum-t statistic across all tested voxels on each sample. The resulting empirical positive-direction p values control FWE over the whole analysis mask at .05. Sign flipping assumes independent participants and a sufficiently symmetric null distribution. The analysis mask was the intersection of nonzero voxels across all 54 maps (198,029 voxels), because zeros outside each participant's map support cannot safely be treated as measured zero effects.

We operationalized vmPFC independently of these group results as a 10 mm-radius MNI152 sphere centered at (0, 40, -10), in ventral medial orbitofrontal prefrontal cortex. This compact anatomical region is used for localization and descriptive effect summaries; it does not replace the whole-brain corrected test.

## Results

No positive whole-brain-corrected voxels overlapped the vmPFC sphere. The mean participant effect within the sphere was -0.0061 COPE units (SD 0.1031; 95% t interval [-0.0342, 0.0221]); 25 of 54 participant averages were positive. The uncorrected one-sided ROI summary was p=.666 and is descriptive only.

Across the brain, 24 voxels passed positive max-t FWE < .05. They formed three small 26-neighbor components, with peaks at MNI (-26, -102, -3.6), (26, -98, -1.2), and (30, -94, -8.4) mm. The strongest peak was t(53)=6.62, empirical pFWE=.001 (5,000 sign flips; Monte Carlo resolution 1/5,001). These sites are far posterior to the vmPFC hypothesis. They should not be read as evidence for the hypothesized vmPFC response.

![Mean effect, whole-brain corrected positive map, and vmPFC participant estimates](figures/group_gain_vmPFC.png)

*Figure 1. Axial MNI slice at z=-3.6 mm shows the group mean participant COPE and the voxels surviving positive whole-brain max-t correction. The vmPFC panel shows participant-wise averages from the 10 mm sphere, with the group mean and 95% t interval. The ROI summary is descriptive and not multiplicity-corrected.*

![Distribution of whole-brain voxelwise statistics](figures/voxel_t_distribution.png)

*Figure 2. Distribution of voxelwise one-sample t statistics in the common nonzero mask; the vertical line is the uncorrected one-sided .05 threshold, shown for context.*

## Quality checks, uncertainty, and limits

All 54 expected maps were present, had matching dimensions and affine transforms (97 x 115 x 81; 2 x 2 x 2.4 mm), contained finite values, and were nonempty. No participant was excluded. No vmPFC participant mean exceeded three robust median absolute deviations from the ROI median. The complete per-participant checks and ROI estimates are in `results/participant_qc.csv`.

Participant-level variance maps were not supplied. Therefore the group model treats each participant COPE as one observation and cannot weight estimates by their upstream precision. The coordinate-defined sphere is one explicit, compact operationalization of vmPFC; anatomical boundaries differ, so other definitions may cover somewhat different tissue. Inference also depends on the fixed AO86 upstream model, including its gain-only model specification and any upstream estimation choices; these cannot be re-fit or audited from the supplied maps. The maps measure association with a normalized gain modulator in the modeled task, not a causal effect of money or a calibrated neural response per currency unit. Finally, a nonsignificant vmPFC result cannot distinguish a truly negligible response from an effect too small or variable to detect here; the ROI interval describes uncertainty in these COPE units but is not an equivalence test.

## Reproducibility

Run the analysis from the workspace root with the supplied common Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/analyze.py
```

The script checks cohort and image consistency, performs the group test, writes the JSON summary and participant QC table, saves group mean/t/FWE NIfTI maps, and regenerates both figures. The fixed permutation seed is 20261016. Main numeric results are in `results/summary.json`; derived maps are under `results/`.
