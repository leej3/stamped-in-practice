# Potential gains and brain activity in the NARPS equal-indifference group

## Question and conclusion

Does the gain-modulator response increase with potential monetary gain in vmPFC? In the 54 equal-indifference participants, **the supplied gain-effect estimates do not support a positive vmPFC response under whole-brain family-wise error (FWE) control**. A one-sided, whole-brain maximum-statistic permutation analysis found 24 significant voxels, but they were all posterior (peaks near MNI y = −94 to −102 mm), outside the vmPFC search region. The result is a lack of corrected support for the stated vmPFC hypothesis; it does not establish that the true effect is zero.

## Inputs and model

The inputs were all 54 unthresholded AO86 participant gain-effect maps listed for the complete equal-indifference group in `input/participants.tsv`; each map is averaged across four runs. Their dimensions, affine transforms, finite values, and SHA-256 checksums against `input/sources.json` were checked. All maps passed; no participant was excluded. The voxel analysis mask retained voxels with finite, nonzero estimates in at least 90% of participants (210,968 voxels). Maps have a 2 × 2 × 2.4 mm grid in MNI152NLin2009cAsym space.

At each voxel, the group estimand was the equally weighted mean of the 54 participant contrast estimates, tested against zero with a one-sample t statistic (53 df). The directional alternative was positive. For whole-brain inference, 5,000 participant-level sign flips were used to form a null distribution of the maximum positive t statistic over the analysis mask. The resulting voxelwise maximum-t p-values control FWE across that mask at .05. The random seed was 20261016; the 95th percentile max-t threshold was 5.40. The smallest attainable Monte Carlo p-value was 1/1001 = .001.

The vmPFC search region was fixed in MNI coordinates as |x| ≤ 15, y = 25–65, and z = −15–5 mm, a bilateral anterior medial prefrontal box. This is used to label the anatomical relevance of corrected whole-brain findings, not to substitute an uncorrected ROI result for the required whole-brain test. A region mean is also reported descriptively.

## Results

No significant positive voxel was inside the vmPFC box (0 of 2,400 voxels; smallest max-t FWE p = 1.00 there). The mean participant coefficient averaged over the vmPFC voxels was −0.0027 (95% t interval −0.0226 to 0.0171 in the supplied coefficient scale). The directional one-sample test on participant-level ROI averages was not positive (t = −0.28, one-sided p = .608); this uncorrected ROI statistic is descriptive and is not the basis for the whole-brain conclusion.

Whole brain, 24 voxels passed FWE p < .05 in three small posterior clusters. The largest had 17 voxels (163 mm³), peak t = 6.62, max-t FWE p = .001 at MNI (−26, −102, −3.6). Two smaller clusters had 5 voxels (48 mm³), peak t = 6.19, FWE p = .0036 at (30, −94, −8.4), and 2 voxels (19 mm³), peak t = 5.76, FWE p = .012 at (26, −98, −1.2). These posterior findings are not evidence for the vmPFC hypothesis and should be interpreted cautiously given their small extents.

![Mean gain-effect estimates and prespecified vmPFC box](figures/group_mean_and_vmPFC.png)

![Positive t map; cyan outlines mark voxels passing whole-brain FWE correction](figures/whole_brain_fwe.png)

![Participant-level vmPFC averages and voxelwise t distribution](figures/vmPFC_estimates.png)

## Interpretation and limitations

These maps contain participant-level contrast parameter estimates, not standardized t or z statistics. In the upstream model, the gain modulator was mean-centered and variance-normalized before HRF convolution, so its coefficient is **not a change in fMRI signal per currency unit**. Response trials were modeled with response-time durations and separate response-choice and gain modulators; nonresponse trials and nuisance terms were included, runs were combined, and gain and loss were modeled separately. The group result therefore concerns this specific conditional, normalized gain contrast under the fixed upstream choices. It does not independently validate those first-level choices or establish a causal neural response per dollar.

The group t model gives every participant equal weight because first-level variance maps were not supplied. Sign-flip inference assumes participant errors are exchangeable and sufficiently symmetric under the null. Five thousand permutations limit tail p-value precision. The analysis mask is based on common nonzero map support and is broad; a different justified mask or anatomical definition could change the tested family and results. No corrected positive evidence in vmPFC means this dataset and analysis did not detect the hypothesized increase at the chosen error rate. It cannot distinguish a truly absent effect from a small, heterogeneous, or poorly estimated effect, nor rule out effects under a different first-level model or vmPFC definition.

## Reproducibility

Run from the workspace root with the supplied interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analyze.py
```

The script writes `results/summary.json`, participant QC, group mean/t/p maps and the binary vmPFC and corrected-significance masks, plus the figures above. Software versions and analysis parameters are recorded in the JSON. Source study instructions: [NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).
