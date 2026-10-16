# Potential gains and brain activity in the NARPS equal-indifference group

## Result

The supplied maps from the equal-indifference mixed-gambles group (in which the gain range was twice the loss range) do **not** support a positive gain response in vmPFC after whole-brain correction. The one-sided group test found 24 max-T family-wise-error-corrected voxels (5,000 sign flips; empirical p at the largest statistic = 0.0010), arranged in three small clusters in posterior/occipital cortex. The largest positive statistic was at MNI (−26, −102, −3.6) mm (t(53) = 6.62; mean effect estimate = 0.112; ordinary pointwise 95% t interval 0.078 to 0.146; this interval is not selection-adjusted for choosing the maximum voxel). This peak is outside vmPFC.

After inspecting the whole-brain result, I added a descriptive vmPFC summary using a 15 mm radius sphere centered at MNI (0, 44, −12) mm, within the anterior ventromedial prefrontal region. This post hoc coordinate-defined sphere is an approximation, not a supplied anatomical ROI; it does not determine the hypothesis decision. Its mean participant effect was −0.0056 (95% t interval −0.031 to 0.020; 1,492 voxels). Its strongest positive voxel had t(53) = 2.45 at (10, 36, −18) mm, with whole-brain max-T adjusted p = 1.00. The sphere mean and interval are descriptive, and do not replace the required whole-brain corrected test. A secondary one-sided Benjamini–Hochberg analysis identified 210 voxels at q < .05 across the whole brain; it likewise does not localize support to vmPFC.

**Interpretation:** a positive gain effect is present somewhere in the analyzed brain under this model, but the corrected signal is posterior, not vmPFC. The evidence therefore does not support the stated vmPFC hypothesis. This is a lack of corrected evidence for the predicted regional response, not proof of no vmPFC effect or of equivalence to zero.

## Analysis

All 54 equal-indifference participants were included once; there were no exclusions. We verified participant IDs against the metadata, all input checksums against `input/sources.json`, and identical image geometry. The common analysis support contained 198,029 voxels where all maps were finite and nonzero; shared zero-filled background was treated as outside modeled coverage. The test was a one-sample, equal-weight random-effects t model of the supplied participant estimates (df = 53), because participant variance maps were unavailable. A sign-flip max-t procedure controlled one-sided family-wise error across the full common support (5,000 Monte Carlo draws; seed 20261016). BH FDR is reported only as a secondary whole-brain summary. This follows the original NARPS instruction to base decisions on whole-brain-corrected analysis ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The analysis estimates group-average supplied gain-effect coefficients. They are not z/t statistics and cannot be read as BOLD change per dollar: upstream gain was mean-centered and variance-normalized before HRF convolution. The maps average four runs per participant; gains and losses were fit separately. No participant variance estimates were supplied, so the model cannot weight by first-level precision. Conclusions are conditional on that fixed upstream model, the common-support mask, and the sign-flip symmetry assumption.

## Figures

![Unthresholded mean effect and group t statistic shown at the whole-brain positive peak; the t display uses the one-sided max-T family-wise threshold.](../figures/whole_brain_group.png)

![Participant-level mean gain effects in the coordinate-defined vmPFC sphere; the band is the ordinary 95% t interval for the group mean.](../figures/peak_participant_effects.png)

## Reproduction and files

Run `git annex get input/data`, `pixi install`, then `pixi run python analysis/run_analysis.py` from the project root. The protocol, environment manifest and lock, executable analysis, input checksums, QC tables, unthresholded NIfTI maps, voxelwise table, permutation null and figure sources are retained in this project. See `README.md` and `analysis/validation-notes.md`.
