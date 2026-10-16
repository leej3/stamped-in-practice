# Potential monetary gain and vmPFC activity

## Result

In the 54-person equal-indifference group, the gain-modulator effect estimate in an independently defined vmPFC sphere was close to zero and slightly negative (mean −0.014 cope units; participant-level 95% t interval −0.044 to 0.015). No sphere voxel passed the one-sided whole-brain family-wise error (FWE) threshold; the smallest max-T adjusted p within the sphere was 1.00. We therefore find **no corrected support for a positive vmPFC gain effect** in this group.

The whole-brain test did identify 24 positive voxels in three small posterior clusters (17, 2, and 5 voxels). The strongest was at MNI [−26, −102, −3.6] (mean cope 0.112, t(53)=6.62, max-T FWE p=0.0007). These locations are outside vmPFC and do not support the target hypothesis.

![Unthresholded mean gain-effect cope map. A display-only threshold of |cope| > 0.05 improves visibility.](results/figures/mean_effect.png)

![Positive effects passing one-sided whole-brain max-T FWE p < .05.](results/figures/positive_fwe.png)

![Participant mean cope within the descriptive vmPFC sphere.](results/figures/vmpfc_effects.png)

## Analysis

We tested the directional group hypothesis using a one-sample t statistic over the strict intersection mask (finite, nonzero in all 54 maps). This avoids treating padded zeros outside a participant's coverage as measured effects, at the cost of a conservative brain-boundary mask. For inference, we sign-flipped each participant's complete map 9,999 times and compared observed t statistics to the permutation distribution of the maximum positive t over the entire mask. This gives one-sided whole-brain max-T FWE control at α=.05 and assumes symmetric participant-level errors under the null. The seed was 20261016. The original NARPS instructions ask teams to make hypothesis decisions from whole-brain-corrected results, rather than ROI-only results ([instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

We localized vmPFC using a 10-mm-radius sphere centered at MNI [2, 46, −8], the independent subjective-value meta-analysis peak reported by [Bartra, McGuire, and Kable (2013)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3756836/). The sphere contains 429 analyzed voxels. Its mean and interval summarize participant-level ROI averages descriptively; they are not a second, uncorrected hypothesis test.

All 54 maps passed file size and SHA-256 checks, shared one affine and grid (2 × 2 × 2.4 mm), and had finite values in the analysis mask. No participant was excluded. Participant map distributions are shown in the QC figure.

![Participant map QC; all 54 participants were retained.](results/figures/participant_qc.png)

## Interpretation and limits

These supplied maps are unthresholded participant contrast parameter estimates (copes), not standardized statistics or group maps. In the fixed upstream model, the gain modulator was mean-centered and variance-normalized before HRF convolution. Thus, cope units describe the response to a change in that model-scaled regressor, not BOLD change per currency unit. The response-time-duration, response-choice, nonresponse, motion, flagged-volume, and drift terms and the separate gain/loss model are inherited from upstream; they cannot be revisited with these files. The group estimate is conditional on that modeling choice.

Without participant variance maps, we could not perform precision-weighted mixed-effects inference; each person's cope contributes equally. The 95% vmPFC interval describes variability of the ROI mean across these participants, not all uncertainty from the first-level models. A null corrected result does not show that the vmPFC effect is exactly zero or that vmPFC never represents value. It means this analysis did not detect the predicted positive response at the required whole-brain FWE criterion; smaller effects may remain uncertain. Because gains span twice the loss range in this group, the result is specific to that design and should not be read as a gain-versus-loss comparison or generalized to other gain ranges.

## Reproducibility

- Main report: `report.md`
- Analysis code: [`code/analyze.py`](code/analyze.py)
- Runnable experiment notebook: [`results/gain_effect_group_analysis.ipynb`](results/gain_effect_group_analysis.ipynb)
- Machine-readable inference summary: [`results/results.json`](results/results.json)
- Participant QC: [`results/participant_qc.csv`](results/participant_qc.csv)
- Peak table: [`results/top_voxels.csv`](results/top_voxels.csv)
- Statistical maps: `results/mean_effect.nii.gz`, `results/t_statistic.nii.gz`, `results/p_fwe_maxT.nii.gz`, `results/common_brain_mask.nii.gz`
- Data provenance and source checksums: `input/sources.json`

Rerun from the workspace root with the supplied prepared Python environment:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/analyze.py
```
