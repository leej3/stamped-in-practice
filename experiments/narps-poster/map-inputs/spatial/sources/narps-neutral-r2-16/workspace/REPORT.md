# Potential gains and brain activity

## Result

**The supplied maps do not support a greater gain-related response in vmPFC after whole-brain correction.** In an intercept-only, one-sided group analysis of all 54 equal-indifference participants, 24 voxels passed whole-brain permutation max-*t* family-wise error correction at *p*<.05. They formed three small posterior occipital clusters (26-neighbor connectivity); none overlapped the vmPFC proxy described below. The strongest voxel was at MNI152NLin2009cAsym (−26, −102, −3.6 mm), *t*=6.62, corrected *p*=.0010. These posterior findings do not support the vmPFC hypothesis.

## Analysis

The unit of analysis was the participant. All 54 supplied unthresholded AO86 gain-effect maps were used, with no exclusions. The maps had matching MNI152NLin2009cAsym grids (97×115×81; 2×2×2.4 mm). We tested the positive group mean at every voxel using an intercept-only second-level model and 5,000 one-sided sign-flip permutations (seed 20261016), with maximum-*t* family-wise error control over the whole common-support mask at α=.05. The analysis used no smoothing or demographic covariates. This implements the original study's requirement for a whole-brain corrected decision rather than basing support on a restricted ROI ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

An initial 99-permutation TFCE pilot remained computationally incomplete after nearly three minutes. Before any inference result was inspected, we selected voxelwise max-*t* for the primary run; this retains whole-mask FWER control and completed the 5,000-permutation run. The abandoned TFCE attempt contributes no reported result.

The mask included the 198,029 voxels with finite, nonzero estimates in every participant map (21.9% of the grid). A zero was treated as outside that participant's modeled support; the intersection rule therefore excludes voxels not represented for every participant. The participant maps contained no nonfinite values. All IDs matched the 54 equal-indifference rows; age and gender metadata were complete but were not used as covariates.

There is no single agreed anatomical boundary for vmPFC, a source of variability noted in the NARPS multi-team analysis ([Botvinik-Nezer et al., 2020](https://pmc.ncbi.nlm.nih.gov/articles/7771346/)). We therefore defined a transparent, deliberately narrow coordinate proxy for descriptive localization and individual summaries: |x|≤12, y=24–56, z=−20–4 mm in MNI152NLin2009cAsym, intersected with common support. This samples medial orbital/ventromedial frontal territory; it does not define the primary correction mask or supply a separate hypothesis test. None of the corrected voxels fell in this proxy.

| Peak rank (by *t*) | Voxels | Peak MNI coordinates (mm) | Peak *t* | Peak corrected *p* |
|---|---:|---:|---:|---:|
| 1 | 17 | −26, −102, −3.6 | 6.62 | .0010 |
| 2 | 5 | 30, −94, −8.4 | 6.19 | .0028 |
| 3 | 2 | 26, −98, −1.2 | 5.76 | .0128 |

The proxy's participant-mean estimate was −0.00016 a.u. (SD=.0712; 95% *t* interval −.0196 to .0193 a.u.; 2,210 voxels). The estimate's near-zero average and wide participant spread are descriptive; this interval is not a whole-brain-corrected test.

![Positive whole-brain max-t FWE map, displayed on its MNI152NLin2009cAsym anatomical template.](figures/primary_whole_brain_maxt.png)

![Participant gain-effect estimates averaged in the vmPFC coordinate proxy; diamond and interval show the mean and 95% t interval.](figures/primary_vmPFC_proxy.png)

## Interpretation and limits

The absence of corrected vmPFC voxels means this analysis did not find whole-brain-corrected evidence for a positive gain effect in the hypothesized region. It does **not** establish that the true effect is zero, rule out a smaller effect, or establish equivalence. The modest sample and multiple-comparison correction limit sensitivity; no equivalence bound or prospective power analysis was available. Exact zero-valued voxels were treated as outside participant model support when forming the intersection mask. Upstream mask files were unavailable to verify whether every exact zero denotes missing model coverage rather than a genuine zero estimate.

The supplied values are contrast parameter estimates, not standardized *t*/*z* scores. Upstream, the gain modulator was mean-centered and variance-normalized before HRF convolution, so the coefficients cannot be read as BOLD change per monetary unit. Gain and loss were modeled separately, and the group analysis cannot recover their joint contribution. No participant variance maps were supplied, so the group model was unweighted and could not account for differing first-level precision. Preprocessing and first-level modeling were fixed; this report does not independently validate those upstream steps or estimate responses from raw time series. The coordinate proxy is only one defensible vmPFC convention, and conclusions about a different boundary may differ.

## Reproduction and checks

From the workspace root, run the analysis and then the rendering and validation steps with the supplied interpreter:

```sh
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py --n-perm 5000
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/make_figures.py
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/validate_results.py
```

The input contract/checksums and machine-readable summary are in `input/sources.json` and `results/primary_summary.json`. Validation confirmed all 54 SHA256 values, complete unique participant metadata, matching grids, and agreement between the reported *t* map and an independent SciPy one-sample calculation at 250 deterministic in-mask voxels (maximum absolute difference 9.54×10⁻⁷). The final figure uses the matching-resolution TemplateFlow MNI152NLin2009cAsym T1 template from `results/reference_data/` (SHA256 recorded in `analysis/environment.md`); this is an anatomical display reference, not study data.

Python 3.13.16 was supplied by the common environment. Analysis package versions are recorded in `results/primary_summary.json` (Nilearn 0.14.1; NiBabel 5.4.2; NumPy 2.5.4; SciPy 1.18.1; pandas 3.0.6). The shared environment recipe is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/pixi.toml`; no shared environment files were modified. Analysis code, participant QC, numeric maps, proxy summary, rendered figures and validation record are retained in this workspace.
