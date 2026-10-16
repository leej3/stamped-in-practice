# Potential gains and vmPFC response in the NARPS equal-indifference group

## Conclusion

This analysis **does not support** the predicted positive vmPFC response to potential gain. The AAL3-defined vmPFC average was slightly negative (mean cope = −0.0064 model units; 95% t CI [−0.0251, 0.0124]), and no vmPFC voxel survived the required one-sided whole-brain familywise-error (FWE) correction. The interval includes zero and small positive values, so this is a lack of corrected evidence for the predicted effect, not evidence that the effect is exactly zero.

There were 23 positive voxels passing voxelwise whole-brain FWE (10,000 sign-flip permutations; max-T threshold *t* = 5.38, df = 53), in three small posterior clusters (peaks at MNI y = −94 to −102 mm). None intersected the vmPFC ROI. Those results do not support the vmPFC hypothesis. The extracted ROI mean and its uncorrected test are descriptive; they did not determine the primary decision.

## Data and group model

The input was the complete equal-indifference sample (54 participants; age 26.1 ± 3.0 years, range 21–37; 30 F and 24 M as recorded) and the supplied AO86 unthresholded gain-effect maps. All 54 map checksums matched `input/sources.json`; maps had matching shape, affine, and 2 × 2 × 2.4 mm voxel size. No participant was excluded.

Each participant’s cope map was treated as one observation in a one-sample random-effects *t* test against zero. The target was a positive group mean. The original instructions ask for whole-brain corrected yes/no decisions and specify directional hypotheses [NARPS instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). Accordingly, we used a one-sided permutation max-*T* correction over the brain mask: 10,000 whole-map sign flips, seed 20261016, with the maximum positive *t* statistic recorded on each permutation. The 95th percentile of those maxima was 5.38; corrected voxel p values use the plus-one permutation estimate. This controls voxelwise FWE across the tested mask under the sign-symmetry null. The code uses NumPy, SciPy, NiBabel, and Nilearn; versions are recorded in `results/summary.json`.

The analysis mask included voxels with finite cope values and nonzero estimates in at least 49/54 maps, intersected with an MNI152 brain mask resampled by nearest neighbor to the supplied MNI152NLin2009cAsym grid (192,339 voxels). This conservative intersection reduces edge and exterior voxels; the generic MNI152 mask is only an approximate anatomical match to the 2009cAsym reference.

To identify vmPFC without using the observed effects to select it, the anatomical ROI was defined from bilateral AAL3 labels for medial orbital frontal cortex, medial/anterior/posterior orbitofrontal cortex, and gyrus rectus. AAL3 was resampled by nearest neighbor to the cope grid. The ROI contains 5,332 tested voxels. Anatomical atlases provide an operational boundary, not a unique definition of vmPFC; atlas boundaries and the chosen label set limit localization. Whole-brain correction was retained rather than reducing the search space to this ROI. [AAL3 atlas description](https://doi.org/10.1016/j.neuroimage.2019.116189).

## Results and quality checks

| Measure | Result |
|---|---:|
| Group | *n* = 54; df = 53 |
| Positive whole-brain FWE voxels | 23 (three contiguous clusters) |
| Largest peak | *t* = 6.62; FWE *p* = 0.00060 at [−26, −102, −3.6] mm MNI |
| vmPFC mean cope | −0.00639 |
| vmPFC 95% t interval | [−0.02513, 0.01235] |
| vmPFC one-sided uncorrected ROI test | *t*(53) = −0.68; *p* = 0.751 |
| FWE-positive voxels overlapping vmPFC | 0 |

The other corrected peaks were at [30, −94, −8.4] mm (*t* = 6.19; FWE *p* = 0.0033) and [26, −98, −1.2] mm (*t* = 5.76; FWE *p* = 0.0124). All are far posterior to vmPFC. Peak coordinates and cluster sizes are descriptive; inference is based on voxelwise max-*T*, not cluster-level testing.

Participant-level map summaries and correlations with the group mean are in `results/participant_qc.csv`. The five weakest spatial correlations ranged from −0.007 to 0.030 (lowest: sub-113, then sub-049); the map summaries also show varying spatial SDs. These checks did not identify a prespecified basis for removing participants, so all 54 remained. The complete group summary and thresholded/unthresholded maps are in `results/`.

![Voxelwise whole-brain FWE results and vmPFC outline](figures/whole_brain_fwe_glass_brain.png)

![Participant vmPFC estimates and group mean interval](figures/vmPFC_subject_estimates.png)

![Distribution of participant whole-brain map means used for QC](figures/participant_map_qc.png)

## What the effect estimates and null result mean

The maps are participant **effect estimates**, not *t* or *z* statistics. Upstream, the gain modulator was mean-centered and variance-normalized before HRF convolution, and response events used response-time durations with separate choice and gain modulators. Therefore, cope magnitude is in upstream model units and must not be read as BOLD change per dollar or other currency unit. Gain and loss were fit in separate models, so the gain estimate is conditional on that modeling choice. This group analysis does not redo or independently validate those fixed upstream choices.

First-level variance maps were not supplied. The one-sample model treats the cope maps as participant observations and captures their between-person spread, including unobserved first-level estimation noise, but cannot precision-weight participants or reproduce a variance-aware mixed-effects model. The sign-flip correction assumes participant-level errors are symmetric about zero under the null; 10,000 random permutations give a smallest attainable corrected p of 0.0001. The uncorrected ROI average is broad and could obscure a smaller subregional response.

Thus, “no support” means this analysis did not demonstrate the predicted positive vmPFC effect at the requested whole-brain corrected threshold. It does not establish equivalence, rule out a small or spatially localized response, or show that potential gain has no neural effect. The positive posterior clusters are outside the hypothesis region and should not be treated as vmPFC evidence.

## Reproducibility files

- [`code/group_analysis.py`](code/group_analysis.py): full analysis and figure-generation code.
- [`group_analysis.ipynb`](group_analysis.ipynb): notebook wrapper to rerun the script and inspect results.
- [`results/summary.json`](results/summary.json), [`results/participant_qc.csv`](results/participant_qc.csv): numerical results and QC.
- `results/*.nii.gz`: group mask, mean cope, *t* statistic, positive FWE p map, and thresholded positive map.
- `figures/*.png`: whole-brain, vmPFC, and participant QC figures.

The NARPS study highlighted that analytic choices can change whole-brain conclusions across teams [Botvinik-Nezer et al. (2020)](https://www.nature.com/articles/s41586-020-2314-9); this result is one explicitly defined group analysis of the supplied fixed effects, not a consensus across pipelines.
