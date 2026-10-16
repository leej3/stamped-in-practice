# Potential gains and brain activity in the equal-indifference group

## Question and conclusion

In the 54-person NARPS equal-indifference group, these data do **not support a positive vmPFC gain effect**. The hypothesized medial orbitofrontal vmPFC summary was slightly negative (mean participant effect −0.0079 model units; 95% t interval −0.0346 to 0.0188; one-sided *p* = .723). No vmPFC voxel survived whole-brain correction. The interval includes small positive and negative effects, so this is a lack of evidence for the proposed increase, not evidence that the true effect is exactly zero.

The whole-brain test did find 24 positive voxels surviving one-sided familywise correction, in three small posterior clusters (17, 5, and 2 voxels). Their peaks were at MNI (−26, −102, −3.6), (30, −94, −8.4), and (26, −98, −1.2) mm; the latter two are in right fusiform cortex in AAL3. These posterior findings do not provide evidence for the vmPFC hypothesis.

## Group analysis

The input was all 54 supplied unthresholded participant gain-effect maps, with no exclusions. IDs matched the equal-indifference rows in the supplied cohort table; map sizes and SHA-256 hashes matched the manifest. Maps shared a 97 × 115 × 81 MNI152NLin2009cAsym grid (2 × 2 × 2.4 mm). We tested the group mean effect against zero using a one-sample *t* statistic, with the directional alternative that the response increases with modeled gain. The search space was the 198,029-voxel intersection of nonzero map support, ensuring complete participant coverage at every tested voxel.

For confirmatory inference, 4,999 random participant-level sign flips generated a one-sided maximum-*t* null distribution across the entire search space. The 95th percentile of the maximum statistic was *t* = 5.394. The peak was *t*(53) = 6.62, with Monte Carlo whole-brain FWE *p* ≈ .001; 24 voxels passed FWE *p* < .05. This follows the NARPS instruction to make the hypothesis decision from a whole-brain corrected analysis, rather than from a selected ROI alone ([original instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf); [NARPS study report](https://pmc.ncbi.nlm.nih.gov/articles/PMC6602933/)). The sign-flip test assumes independent participants and symmetric errors under the null.

We operationalized vmPFC independently of the functional results using the bilateral AAL3 `Frontal_Med_Orb` parcels, resampled with nearest-neighbor interpolation to the map grid (1,297 in-mask voxels). These medial orbital frontal parcels provide an explicit anatomical proxy for ventral medial prefrontal cortex; they do not capture every possible vmPFC definition ([AAL3 atlas](https://pubmed.ncbi.nlm.nih.gov/31521825/)). As a descriptive secondary check, each participant’s map was averaged within this fixed mask and tested with a one-sided one-sample *t* test. The Wilcoxon signed-rank sensitivity test was also negative (*p* = .877). Leave-one-participant-out ROI means remained negative (−0.0135 to −0.0044).

![Whole-brain group mean effects and the voxels passing one-sided max-t FWE correction.](figures/whole_brain_gain_effect.png)

*Figure 1. Top: unthresholded group mean gain-effect estimate in arbitrary model units. Bottom: positive group *t* values exceeding the one-sided whole-brain max-*t* threshold (FWE *p* < .05). Displayed slices pass through posterior peaks.*

![Participant vmPFC effect estimates and group mean interval.](figures/vmPFC_participant_effects.png)

*Figure 2. Participant-level mean effect in bilateral AAL3 medial orbital frontal parcels; the diamond and bar show the group mean and 95% t interval.*

## Interpretation and limitations

The supplied maps estimate each participant’s response associated with the upstream gain modulator. That modulator was mean-centered and variance-normalized before HRF convolution, so the coefficients are not response changes per currency unit. They are also conditional on the upstream decision, response-time, and separate gain/loss modeling choices described in [the fixed upstream methods](input/upstream-methods.md). In this group, the potential-gain range was twice the loss range; these gain maps alone cannot establish how gain coding compares with loss coding. The tested maps are not standardized test statistics, and no participant variance maps were supplied. Consequently, the group model treats participant effect estimates as observations and cannot account for differences in their first-level precision.

No participant was excluded. The analysis uses only this group and this supplied upstream pipeline; it does not show that gain causes a neural response. A missing corrected vmPFC effect can reflect a small or heterogeneous response, measurement and modeling uncertainty, or limited power; it cannot establish absence or equivalence to zero. The additional posterior whole-brain clusters are exploratory in interpretation and do not alter the vmPFC conclusion.

## Reproducibility files

- Analysis code: [`scripts/analyze_gain.py`](scripts/analyze_gain.py)
- Machine-readable results: [`results/summary.json`](results/summary.json)
- Participant-level vmPFC values: [`results/participant_vmPFC_effects.tsv`](results/participant_vmPFC_effects.tsv)
- Permutation maximum-*t* null: [`results/permutation_max_t.tsv.gz`](results/permutation_max_t.tsv.gz)
- Group mean, *t*, corrected-*p*, and significance maps: `results/mean_gain_effect.nii.gz`, `results/t_gain_effect.nii.gz`, `results/p_fwe_gain_effect.nii.gz`, `results/significant_fwe05.nii.gz`
- Software: Python 3.13, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, NiBabel 5.4.2, Nilearn 0.14.1, Matplotlib 3.11.2.

Re-run from the workspace with the supplied Python interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/analyze_gain.py
```
