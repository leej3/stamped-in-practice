# Potential gains and vmPFC activity

## Finding

In the 54-person NARPS equal-indifference group, the supplied gain-effect maps do **not support a positive vmPFC response to increasing potential gain**. The prespecified vmPFC summary was slightly negative and uncertain (mean effect −0.014, 95% CI −0.044 to 0.015; one-sided *t*(53) = −0.97, *p* = .832). The interval includes zero and small positive effects, so this is a lack of evidence for the predicted increase, not evidence that the true effect is exactly zero. The whole-brain analysis did identify 11 individually significant voxels after conservative FWE correction, all in posterior occipital cortex rather than vmPFC.

## Analysis

All 54 supplied unthresholded AO86 participant contrast maps were analyzed; none was excluded. The script checked participant IDs against the pinned cohort table and verified the byte size and SHA-256 digest of each map against `input/sources.json`. All maps were finite and shared a shape of 97 × 115 × 81 with 2 × 2 × 2.4 mm voxels in MNI152NLin2009cAsym space. The group mask was the intersection of their common nonzero support and a standard MNI152 brain mask resampled to the supplied image grid (186,400 voxels). This avoids treating out-of-coverage zeros as measured effects and excludes nonbrain edge voxels.

The primary group model was a one-sample, one-sided *t* test of participant effects against zero at each masked voxel, testing the predicted positive direction. Participant maps are treated as independent observations with equal weight because participant variance maps were not provided. Whole-brain family-wise error was controlled at .05 using Bonferroni correction across all 186,400 voxels. This correction is conservative and does not depend on spatial independence. The assumptions for the voxelwise *t* tests are independent participants and an approximately normal sampling distribution of participant effects; no smoothing or cluster-extent inference was added at the group stage. The script uses Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, NiBabel 5.4.2, Nilearn 0.14.1, and Matplotlib 3.11.2.

The vmPFC summary used a 10 mm radius sphere centered at MNI [2, 46, −8], a published positive-value vmPFC focus from an independent coordinate meta-analysis. This gives an a priori anatomical/functional target that is independent of the present activation results ([Bartra et al., 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3756836/)). The sphere summary is reported as a targeted estimate with a t-based 95% interval, not as a substitute for whole-brain correction.

## Results

The vmPFC sphere contained 429 masked voxels. Its mean participant effect was −0.0143 (between-participant SD 0.1084); 25 of 54 participants had a positive sphere average. The one-sided *t* test gave *p* = .832; a one-sided Wilcoxon signed-rank sensitivity test also did not support a positive effect (*p* = .880).

Across the whole brain, the most positive voxel was in left posterior occipital cortex at MNI [−26, −102, −3.6] (*t*(53) = 6.62; uncorrected one-sided *p* = 9.3 × 10⁻⁹; Bonferroni FWE *p* = .00174). Eleven voxels passed voxelwise Bonferroni FWE, in three small occipital islands (8, 2, and 1 voxels). These are outside the vmPFC target. Figure 1 displays the uncorrected *t* map only for spatial context; Figure 2 shows the corrected positive whole-brain effects; Figure 3 shows all vmPFC participant summaries.

## Interpretation and limits

The tested estimates are participant-level coefficients for a mean-centered, variance-normalized gain modulator after HRF convolution, not standardized *t* or *z* statistics. They therefore do not mean a change in BOLD per dollar. The upstream model used response-time durations, included response-choice and other nuisance terms, and modeled gain separately from loss. The group result is conditional on those fixed choices; separate gain and loss models do not establish a gain-versus-loss difference. The group’s gain range being twice its loss range does not rescale these coefficients back to monetary units.

The confidence interval is compatible with zero and modest positive or negative effects. Failure to support the predicted increase does not establish no vmPFC involvement, rule out smaller effects, or show that the gain effect is equivalent to zero. Nor can these maps assess upstream preprocessing/model misspecification or account for first-level precision differences, since variance maps and an executable upstream pipeline were not supplied. No time-series data were reprocessed. The reported hypothesis and task context follow the [original NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

## Figures and reproducibility

![Uncorrected whole-brain group t map. Color is shown for |t| ≥ 2 for orientation, not inference; blue outline marks the independently defined vmPFC sphere.](figures/whole_brain_tmap.png)

*Figure 1. Uncorrected whole-brain group t map (t53); colored voxels are for spatial context only.*

![Positive effects passing voxelwise Bonferroni FWE p < .05; blue outline marks the vmPFC sphere.](figures/whole_brain_fwe.png)

*Figure 2. Positive effects passing whole-brain Bonferroni FWE correction (one-sided p < .05). The corrected voxels are posterior and do not overlap the vmPFC target.*

![Participant mean effects within the vmPFC sphere, with group mean and t-based 95% interval.](figures/vmPFC_participant_effects.png)

*Figure 3. Participant vmPFC sphere means and the group mean with a 95% t interval; dashed line marks zero.*

Run the complete analysis from the workspace root with:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_group_analysis.py
```

The script uses Python, NumPy, SciPy, pandas, NiBabel, Matplotlib, and Nilearn. Main outputs are `results/summary.json`, participant QC and ROI tables, and NIfTI files for the group mean, t map, FWE p map, mask, and ROI.
