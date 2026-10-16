# Potential gain and vmPFC response in the NARPS equal-indifference group

## Result

The 54-participant group did **not** show evidence that potential gains produced a greater vmPFC response. No voxel in the independently specified vmPFC sphere survived one-sided whole-brain familywise error (FWE) correction (max-T permutation, α = .05). Within that sphere, the mean participant effect was −0.010 model units (95% t interval −0.036 to 0.015; one-sided uncorrected descriptive *p* = .788; *t*(53) = −0.80). Exactly 27 of 54 participant-level sphere means were positive.

Across the full brain mask, 23 voxels passed positive-direction whole-brain max-T FWE correction; the strongest was at MNI (−26, −102, −3.6), outside vmPFC. This does not support the specified vmPFC hypothesis. The posterior/inferior finding is outside the target region and is not interpreted as evidence for the hypothesis.

![Positive effects passing whole-brain max-T FWE correction](figures/whole_brain_t_map.png)

*Figure 1. Positive group t statistics are shown only where voxelwise whole-brain max-T FWE p < .05. The strongest corrected voxel is outside the hypothesized vmPFC region.*

![Participant-level vmPFC estimates](figures/vmPFC_participant_estimates.png)

*Figure 2. Each point is one participant’s average effect estimate within the prespecified vmPFC sphere. The line and shaded band show the mean and its two-sided 95% t interval; this ROI summary is descriptive and uncorrected.*

## Analysis

I included all 54 equal-indifference participants listed in the supplied metadata. The effect maps’ SHA-256 values matched the supplied manifest, all maps shared a 97 × 115 × 81 voxel grid and affine in MNI152NLin2009cAsym space, and all values were finite. No participant or map was excluded. Quality checks are in [`image_qc.csv`](results/image_qc.csv).

The equal-indifference task condition used a potential-gain range twice the potential-loss range. The group model was a one-sample test of the 54 participant maps against zero, giving each participant equal weight. Because participant variance maps were not supplied, precision-weighted mixed-effects inference was not possible. For the primary positive-direction test, I computed voxelwise one-sample t statistics and used 9,999 random participant sign flips to build the maximum-t null distribution over an explicit MNI brain mask (Nilearn MNI152 brain mask resampled to the supplied image grid). Plus-one Monte Carlo p values control voxelwise familywise error across the entire mask. This tests a positive group mean under the assumption that participant effects are independent and approximately symmetric around zero under the null. The seed was 20261016.

The original hypothesis is a positive gain effect in vmPFC for the equal-indifference group ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). Since vmPFC has no single agreed anatomical atlas boundary, I used a 10-mm-radius sphere centered at MNI (4, 42, −8), a published mixed-gamble valuation locus ([Tom et al., 2007](https://pubmed.ncbi.nlm.nih.gov/17255512/)). This sphere identifies the target location for reporting; it does not replace whole-brain correction. The NARPS multi-team paper similarly notes the lack of a direct anatomical vmPFC definition and describes combining anatomical and meta-analytic information ([Botvinik-Nezer et al., 2020](https://www.nature.com/articles/s41586-020-2314-9)).

## Interpretation and limits

This is a lack of support for a detectable positive group effect in this vmPFC operationalization, not evidence that the true effect is exactly zero or that vmPFC never represents value. The interval includes small positive and negative effects; limited power, measurement noise, or variation in responses across participants could obscure a modest positive mean.

The supplied images are participant-level effect estimates, not z/t maps, and the upstream gain modulator was mean-centered and variance-normalized before HRF convolution. Therefore, the reported effect is in arbitrary model units, not a change in BOLD per dollar. The upstream model also used response-time event durations, modeled choice separately, and fitted gain and loss in separate models. The group analysis cannot revise those choices or establish a raw monetary dose-response. As fixed upstream inputs, no time-series scans or participant variance maps were reanalyzed. Equal weighting treats participants equally but cannot account for differing first-level precision. The sign-flip FWE procedure additionally relies on null symmetry.

## Reproduction and files

Run from the workspace root with the prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/group_analysis.py
```

The script uses Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, NiBabel 5.4.2, Nilearn 0.14.1, and Matplotlib 3.11.2. It writes the summary to [`summary.json`](results/summary.json); the voxelwise group mean, t, and FWE p maps and vmPFC sphere mask are in [`results/`](results/). Participant sphere estimates are in [`vmPFC_participant_effects.csv`](results/vmPFC_participant_effects.csv). Figures are in [`figures/`](figures/).
