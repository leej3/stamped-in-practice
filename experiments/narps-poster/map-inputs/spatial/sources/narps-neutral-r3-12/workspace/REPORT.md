# Potential gains and brain activity

## Question and conclusion

In the 54-person NARPS equal-indifference group, these data do **not support a positive gain-related response in vmPFC**. This group's possible gain range was twice its possible loss range. The primary one-sided whole-brain sign-flip test found no voxels surviving familywise error correction (FWE; 10,000 sign flips, α = .05). In the Harvard–Oxford Frontal Medial Cortex parcel used as an anatomical vmPFC proxy, the average participant cope was −0.009 (95% CI −0.040 to 0.022; one-sided *p* = .723, unadjusted). This parcel result is descriptive and is not substituted for the required whole-brain test.

The strongest observed positive group statistic was *t*(53) = 6.62 at MNI [−26, −102, −3.6] mm, far posterior to vmPFC. Its permutation max-statistic FWE *p* was 1.00. A parametric one-sample *t* sensitivity analysis with Bonferroni correction across the same 186,400 brain voxels flagged 11 voxels (minimum corrected *p* = .00174); they were also posterior and outside the vmPFC parcel. The parametric and permutation whole-brain results differ, so the off-target finding should be treated cautiously. Neither analysis provides evidence for the specific vmPFC hypothesis.

## Analysis

We analyzed the supplied unthresholded participant-level cope maps as fixed inputs; we did not rerun preprocessing or individual models. Each map is AO86’s gain-effect estimate averaged over four runs. AO86 mean-centered and variance-normalized the gain modulator before HRF convolution, so the cope is not a slope per currency unit. It is also conditional on the upstream response-time, response-choice, motion, censoring, drift, and separate gain/loss modeling choices described in [upstream-methods.md](input/upstream-methods.md).

We fit a one-sample group model to the 54 participant maps, testing a positive mean effect. The tested mask was the intersection of nonzero coverage in all 54 maps and a standard MNI152 brain mask (186,400 voxels). We controlled whole-brain FWE using the maximum positive *t* statistic across voxels for 10,000 participant-level sign flips, with a fixed random seed. This directional test follows the positive-effect hypothesis. The original NARPS instructions specified whole-brain analyses for the hypotheses, rather than ROI-only analyses ([NARPS instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The analysis uses Python, NiBabel, Nilearn, NumPy, pandas, SciPy, and Matplotlib; exact versions are recorded in `results/analysis_summary.json`.

To make the anatomical localization explicit, we used the Harvard–Oxford cortical atlas “Frontal Medial Cortex” label as a broad, reproducible proxy for vmPFC. This atlas parcel is only used to describe where the hypothesized region lies and summarize participant values; statistical support is based on the whole-brain correction. The cope estimates within this parcel were averaged per participant before computing the reported mean and *t* interval.

The sign-flip maximum-*t* null had a very long upper tail (5% critical value 290.20), making this correction highly conservative for this dataset. As a sensitivity check, we also applied one-sided voxelwise one-sample *t* tests and Bonferroni correction across the same mask. That analysis found 11 posterior voxels, but no vmPFC voxels. This check assumes the participant estimates are adequately modeled by the one-sample *t* distribution; we report it to expose the method dependence rather than to replace the primary permutation result.

## Quality checks and limits

All 54 expected participant IDs matched the metadata and map filenames; all maps had matching dimensions and affine, finite values, and common nonzero coverage. No participants were excluded. Whole-mask participant means had no extreme outliers by a ±3 SD screen (largest absolute standardized mean = 2.27); this screen did not drive exclusions. Participant-level coefficient maps are the only variance information available, so we could not weight participants by first-level uncertainty or fit a full hierarchical model. The group *t* analysis therefore treats the participant estimates as independent observations with equal weight.

The atlas label is broad and is not a precise functional vmPFC boundary. The supplied estimates inherit the upstream model’s choices and potential misspecification; they cannot establish a causal effect of monetary gain, a response per currency unit, or an effect independent of the separately modeled loss regressor. The permutation test also depends on sign symmetry of participant effects under the null. A corrected null result means that these maps do not provide sufficiently reliable evidence for the prespecified positive vmPFC effect under the stated group analysis; it does not establish that the true effect is exactly zero or that vmPFC never encodes gain.

## Figures

![Unthresholded group t map with the vmPFC anatomical proxy outlined](results/figures/whole_brain_fwe_vmPFC.png)

**Figure 1.** Unthresholded one-sample group *t* map (display threshold |*t*| ≥ 2). Cyan marks the atlas Frontal Medial Cortex parcel. No voxel survived the primary one-sided permutation max-*t* FWE correction.

![Participant mean cope values in the vmPFC anatomical proxy](results/figures/vmPFC_roi_estimates.png)

**Figure 2.** Participant mean cope within the Frontal Medial Cortex parcel. The diamond and bars show the mean and two-sided 95% one-sample *t* confidence interval; the dashed line is zero.

## Reproducibility files

- Analysis script: [analysis/run_analysis.py](analysis/run_analysis.py)
- Numerical summary: [results/analysis_summary.json](results/analysis_summary.json)
- Participant quality checks: [results/participant_qc.tsv](results/participant_qc.tsv)
- Group *t*, mean cope, permutation FWE *p*, and Bonferroni *p* maps: `results/group_*.nii.gz`
- Permutation maximum statistics: [results/permutation_max_t.tsv](results/permutation_max_t.tsv)
- ROI estimates and summary: [results/vmPFC_roi_participants.tsv](results/vmPFC_roi_participants.tsv), [results/vmPFC_roi_summary.json](results/vmPFC_roi_summary.json)

Run from the project root with the prepared Python environment:

```bash
python analysis/run_analysis.py
```
