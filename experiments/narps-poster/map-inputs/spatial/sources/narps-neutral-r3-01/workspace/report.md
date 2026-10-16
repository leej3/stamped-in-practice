# Potential gain and vmPFC response in the equal-indifference group

## Conclusion

The supplied group maps do **not** support a positive gain-related response in vmPFC after whole-brain correction. A one-sided max-T permutation test found 24 positive voxels somewhere in the common brain coverage, but none fell in the independent anatomical vmPFC proxy. Those voxels lie at the far posterior edge of the maps (peak MNI coordinate −26, −102, −3.6 mm), not in vmPFC; their anatomical interpretation is uncertain. This is not evidence that the true vmPFC effect is zero.

## Data and group model

I analyzed all 54 supplied AO86 equal-indifference participants. In this task condition, the range of possible gains was twice the range of possible losses. The input list and map filenames matched exactly; all maps had matching dimensions and affine, finite values, and SHA-256 hashes matching `input/sources.json`. No participant was excluded. Voxelwise inference used the intersection of voxels with finite, nonzero values in every map (198,029 voxels), preventing zeros outside an individual's modeled coverage from being treated as measured zero effects.

Each image is a participant-level gain-modulator contrast estimate (COPE), not a t/z statistic. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution, so these estimates index response to a standardized within-task gain regressor, **not change per ILS**. A one-sample group t model tested whether the mean estimate exceeded zero. Because participant variance maps were not supplied, this was an unweighted model; voxelwise sign flips across participants provided a studentized max-T null distribution (4,999 random flips; seed 20261016). Inference was one-sided at family-wise α=.05 over the full common-coverage mask, following the original NARPS instruction to decide hypotheses from whole-brain-corrected maps. The sign-flip inference assumes independent, approximately symmetric participant errors under the null.

For anatomical localization only, I used a broad, independently defined vmPFC proxy formed from Harvard-Oxford cortical atlas labels *Frontal Medial Cortex*, *Subcallosal Cortex*, and *Frontal Orbital Cortex* (25% maximum-probability atlas, 2 mm; 3,719 in-mask voxels). I did not use an ROI-only result to decide the hypothesis: a vmPFC effect counts as support only if it appears in the whole-brain-corrected map within this independently specified region.

## Results

| Measure | Result |
|---|---:|
| Participants / exclusions | 54 / 0 |
| Whole-brain max-T threshold | t = 5.397 |
| Largest positive effect anywhere | t = 6.62; max-T FWE p = .001 |
| Positive voxels surviving whole-brain correction | 24 |
| Corrected positive voxels in vmPFC proxy | 0 |
| Mean participant vmPFC-proxy COPE | −0.0048 (arbitrary upstream units) |
| Participant-bootstrap 95% CI for that mean | [−0.0235, 0.0144] |

The strongest corrected voxel was at MNI −26, −102, −3.6 mm (mean COPE 0.112). The surviving voxels form small posterior edge foci. They are spatially separate from vmPFC; given their extreme posterior coordinates, they should not be overinterpreted anatomically. The vmPFC-proxy mean is close to zero and its descriptive participant-bootstrap interval includes zero. That interval is not a whole-brain-corrected test.

![Whole-brain positive max-T corrected results](results/figures/whole_brain.png)

**Figure 1.** Positive group t values surviving one-sided whole-brain max-T FWE correction at α=.05. The small foci lie at the posterior edge, not in vmPFC. The map is displayed on a standard MNI template; slight template differences and the extreme edge coordinates limit precise anatomical labeling.

![Participant mean estimates in vmPFC proxy](results/figures/vmPFC_values.png)

**Figure 2.** Each point is a participant's average COPE in the independent atlas proxy; the diamond and interval show the mean and bootstrap 95% CI across participants. This summary is descriptive, not the confirmatory test.

## Interpretation and limits

The result is **no support for the stated vmPFC hypothesis under whole-brain-corrected inference**, despite corrected positive signal elsewhere. It does not establish absence of a small effect: the sample and input maps may be too imprecise, and no equivalence bound was specified. Missing participant variance maps prevent a precision-weighted mixed-effects analysis. The upstream model is fixed and not reproduced here; separate gain and loss models make this gain estimate conditional on that modeling choice. The normalized regressor also prevents translating the result into response change per unit of money. Finally, a task modulator effect does not on its own establish how gain affects acceptance decisions.

## Reproduction and files

Run from the workspace root with the supplied prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis.py
```

The script verifies input hashes and writes `results/results.json`, participant QC and vmPFC summary tables, the null max-T distribution, NIfTI group maps/masks, and the figures. Software versions, permutation seed, and threshold are recorded in the JSON. Inputs and fixed upstream-method details are documented in `input/sources.json` and `input/upstream-methods.md`.

## Sources

- NARPS analysis instructions, Hypothesis 1 and whole-brain corrected decision requirement: [PDF](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).
- NARPS mixed-gambles data descriptor: [Scientific Data](https://www.nature.com/articles/s41597-019-0113-7).
- Per-image source URLs and retrieved-byte SHA-256 values: `input/sources.json`.
