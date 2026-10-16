# Potential gains and brain activity

## Question and result

In the 54-person NARPS equal-indifference group, where the potential-gain range was twice the potential-loss range, the participant gain-effect estimates provide **no support for a positive vmPFC response to increasing potential gain** under whole-brain familywise-error (FWE) correction. The strongest positive voxel in the prespecified anatomical vmPFC mask had *t*(53) = 4.19 but whole-brain max-T FWE *p* = .780; no vmPFC voxels survived FWE correction. The average vmPFC estimate was slightly below zero (mean = −0.0037 model units, 95% *t* interval [−0.0222, 0.0147]; one-sided unadjusted *p* = .657).

A positive whole-brain result did occur outside vmPFC: 24 voxels in three small clusters in the occipital pole survived max-T FWE correction. The global maximum was *t*(53) = 6.62, max-T FWE *p* = .00065 (20,000 sign flips). Those posterior clusters do not support the stated vmPFC hypothesis.

| Cluster | Voxels | Peak MNI (x, y, z), mm | Peak max-T FWE *p* |
|---|---:|---:|---:|
| 1 | 17 | (−26, −102, −3.6) | .0010 |
| 2 | 2 | (26, −98, −1.2) | .0132 |
| 3 | 5 | (30, −94, −8.4) | .0029 |


## Group analysis

I fit a one-sample intercept-only model to the 54 unthresholded participant gain-effect maps, each already averaged across four runs by the fixed upstream analysis. This tests whether the population mean participant gain effect is greater than zero. Participants were equally weighted because participant-level variance maps were not supplied. The primary inference was a one-sided sign-flip permutation test of the voxelwise *t* statistic, with the maximum statistic across the full common-support brain mask used to control FWE at .05. The mask contained 198,029 voxels with nonzero estimates in every participant. I used 20,000 sign flips (seed 20261016); the 95th percentile of the maximum-null distribution was *t* = 5.37. This is a strict voxelwise whole-brain correction. It relies on independent, sign-exchangeable participant effects under the null.

The hypothesis is about vmPFC, but inference was not restricted to a small ROI. I characterized vmPFC using a fixed anatomical mask made by combining the Harvard-Oxford cortical atlas maximum-probability (25%) labels “Frontal Orbital Cortex” and “Subcallosal Cortex,” resampled to the supplied maps. This offers an explicit, reproducible approximation of ventral medial prefrontal territory; the atlas labels are not a uniquely agreed definition of vmPFC. All positive voxels were then assessed against the whole-brain max-T null. The atlas ROI was also summarized descriptively at participant level.

## Quality checks and exclusions

All 54 maps passed their manifest SHA-256 and byte-size checks, shared a 2 × 2 × 2.4 mm MNI152NLin2009cAsym grid, and contained finite values. The cohort table had 30 women and 24 men; mean age was 26.1 years (SD 3.0). No participants were excluded. One participant (sub-025) was flagged by a 3×IQR screen on their vmPFC average; removing that participant as a sensitivity check did not change the conclusion (n = 53, mean = −0.0080; one-sided unadjusted *p* = .828). The flag was not used as an exclusion criterion.

## Interpretation and limits

The supplied maps are participant contrast parameter estimates, not *t* or *z* statistics. AO86 mean-centered and variance-normalized the gain modulator before HRF convolution, so coefficients do not express change per currency unit. The gain and loss regressors were analyzed in separate models, so this estimate is conditional on those upstream modeling choices and is not a gain effect independently adjusted for a jointly fitted loss modulator. The response events were modeled with response-time durations and the upstream model also included choice, nonresponse, motion, flagged-volume, and drift terms; this group analysis does not revisit those decisions.

Without participant variance maps, the group model cannot weight effects by their first-level precision or propagate within-participant uncertainty. The available maps therefore support a conventional equal-weight second-level estimate, not a full hierarchical model. In addition, the common-support mask excludes voxels without estimates in every participant. The atlas ROI is an approximate anatomical definition. A lack of corrected vmPFC support means that this analysis did not detect a positive association at the required whole-brain-controlled threshold; it does not establish that the true effect is zero, demonstrate equivalence, or rule out smaller effects. The ROI interval remains compatible with small positive and negative mean effects.

The original NARPS Hypothesis 1 specified a positive parametric gain effect in vmPFC for the equal-indifference group, with results evaluated using whole-brain analysis; NARPS task and design details are described in the study paper ([original instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf), [NARPS paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7771346/)). The Harvard-Oxford atlas is a probabilistic structural atlas distributed with FSL ([atlas documentation](https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html)).

## Figures

**Whole-brain corrected inference.** The positive whole-brain corrected clusters are posterior and do not overlap the vmPFC mask.

![Whole-brain FWE map](results/figures/whole_brain_fwe_map.png)

**vmPFC participant estimates.** Points show each participant's mean estimate within the orbital/subcallosal atlas mask; band is the unadjusted 95% *t* interval around the group mean.

![vmPFC estimates](results/figures/vmPFC_subject_effects.png)

The unthresholded mean map is provided as a descriptive figure at [mean_gain_effect_map.png](results/figures/mean_gain_effect_map.png).

## Reproducibility files

- [Analysis code](analysis.py): input checksum checks, mask construction, one-sample model, max-T inference, atlas ROI summary, QC, figures, and output tables/maps.
- [Numerical summary](results/summary.json)
- [Corrected cluster table](results/tables/corrected_clusters.csv)
- [Participant ROI/QC table](results/tables/participant_qc.tsv)
- [Whole-brain outputs](results/): mean effect, *t*, max-T FWE *p*, corrected *t* map, and vmPFC mask in NIfTI format.
- Software versions and random seed are recorded in `summary.json`.

Run from the workspace root with the prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis.py
```
