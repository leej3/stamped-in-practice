# Potential monetary gains and vmPFC activity

## Question and conclusion

We found **no whole-brain corrected support** for the predicted positive gain effect in vmPFC. No vmPFC voxel passed the one-sided max-T family-wise error (FWER) threshold of .05 in the 54-person NARPS equal-indifference group. There were 89 significant voxels elsewhere; the maximum was t = 6.61 at MNI (−26, −102, −3.6), with whole-brain max-T p = .0004. This posterior peak does not support the specific vmPFC hypothesis.

The primary analysis was a one-sided one-sample group test of the supplied participant contrast estimates, with whole-brain family-wise error control using sign-flip maximum-statistic permutations. This follows the original NARPS instruction to make hypothesis decisions from whole-brain corrected analysis rather than a small ROI-only analysis ([original analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

## Data and group analysis

The input comprised all 54 equal-indifference participants’ unthresholded AO86 gain-effect maps. We verified all 54 SHA256 manifest entries, matching spatial grids, and finite values. No participant was excluded. A common-support mask retained 210,968 voxels nonzero in at least 90% of maps. We smoothed estimates at 6 mm FWHM, then computed the group mean and one-sample t statistic. The positive one-sided null distribution used 5,000 random participant sign flips; for each flip we retained the largest positive t statistic anywhere in the mask. The resulting max-statistic p values control whole-brain FWER at .05. This sign-flip inference relies on participant errors being exchangeable and approximately symmetric under the null.

For anatomical localization, vmPFC was operationalized descriptively as the medial frontal box |x| ≤ 20, 25 ≤ y ≤ 55, and −20 ≤ z ≤ 15 mm in MNI coordinates, covering ventral medial prefrontal and rostral cingulate territory. This approximate box is not used to restrict or define the primary multiple-comparison family. The mean vmPFC estimate was −0.00006 (95% t interval [−0.01364, 0.01352], arbitrary model units); its unadjusted one-sided ROI p value was .504, and no vmPFC voxel passed whole-brain correction.

![Whole-brain gain effect](output/figures/whole_brain_gain_effect.png)

*Figure 1. Unthresholded group t statistic shown in sagittal, axial, and coronal views. Yellow outlines mark voxels passing one-sided whole-brain max-T FWER p ≤ .05; no corrected voxels occur in the vmPFC search region.*

![Participant estimates in vmPFC](output/figures/vmPFC_estimates.png)

*Figure 2. Each point is a participant’s average smoothed gain-effect estimate across the descriptive vmPFC mask. Diamond and error bar show the group mean and two-sided 95% t interval.*

## Interpretation and limitations

The inputs are contrast parameter estimates, not standardized statistics. The upstream gain modulator was mean-centered and variance-normalized within participant before HRF convolution; therefore coefficients do not estimate BOLD change per currency unit. In this equal-indifference design, the potential-gain range was twice the loss range, but the maps are conditional on a model with separate gain and loss models. They also reflect the fixed response-time duration, response-choice and gain-modulator regressors, and nuisance regressors. This analysis estimates the group average of those participant coefficients, not a causal effect of changing money or a direct gain-versus-loss contrast.

Participant-level variance maps and a complete executable first-level workflow were not supplied. Thus we could not weight group estimates by first-level precision or independently assess first-level uncertainty; the conventional equal-weight one-sample analysis treats the supplied estimates as the observations and relies on between-participant variability. The sign-flip test addresses group-level inference under its symmetry assumption but does not repair upstream model misspecification. The anatomical box is approximate, and nonsignificance is not evidence that the true effect is exactly zero: it means this analysis did not detect a positive effect surviving whole-brain correction at this sample size and model scale. A smaller effect, spatially different effect, or effect under a different defensible pipeline may remain. Age and gender metadata were not used as covariates because this was a single-group mean-effect question and no covariate adjustment was specified.

## Reproducibility

Run `python analysis.py` with the prepared Python environment (Python 3.13.16; NumPy 2.5.4; SciPy 1.18.1; NiBabel 5.4.2; Nilearn 0.14.1; Matplotlib 3.11.2). It writes the JSON results, participant QC table, participant ROI estimates, analysis/statistic maps, and figures under `output/`. The notebook at `output/jupyter-notebook/narps_hypothesis1_gain_effect.ipynb` documents the analysis and runs the same script. Fixed inputs and their provenance are described in `input/upstream-methods.md` and `input/sources.json`.
