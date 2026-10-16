# Potential gains and brain activity

## Conclusion

In the 54 equal-indifference participants, the supplied gain-effect maps do **not support a positive vmPFC response** at the required whole-brain-corrected level. Eleven positive voxels survived voxelwise Bonferroni correction, but all were in small clusters at the occipital pole; none overlapped the prespecified vmPFC anatomical proxy. The proxy’s group mean was slightly negative (mean −0.0048 model units, 95% CI −0.0243 to 0.0147; one-sided ROI-only *p*=0.690). This is a lack of evidence for the stated vmPFC hypothesis, not evidence that the true response is exactly zero.

## Analysis

We tested a positive group mean of the supplied participant contrast estimates with a one-sample voxelwise *t* test (*n*=54, df=53). All 54 participant maps matched the source SHA-256 checksums, were finite, and shared the same MNI grid. No participant was excluded. To use one constant sample across voxels, inference was limited to the intersection of the maps’ nonzero supports (198,029 voxels). We used a one-sided test because the hypothesis predicts a positive response, and controlled familywise error over this entire mask using Bonferroni correction (uncorrected voxel threshold *p*≤2.52×10⁻⁷, α=.05). We implemented the analysis in Python 3.13 using NumPy, SciPy, NiBabel, pandas, and Nilearn. This directly implements the NARPS instruction to base the binary decision on a whole-brain-corrected result ([original instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The largest positive statistic was *t*(53)=6.62 (*p*uncorrected=9.31×10⁻⁹; whole-brain Bonferroni *p*FWE=.00184). Its peak was at MNI (−26, −102, −3.6) mm in the Harvard–Oxford Occipital Pole label. All three FWE-significant clusters (11 voxels total) were occipital, not vmPFC. We operationalized vmPFC before inspecting results as the union of Harvard–Oxford cortical Frontal Medial, Subcallosal, and Frontal Orbital labels (25% maximum-probability atlas; [atlas label definitions](https://git.fmrib.ox.ac.uk/fsl/data_atlases/-/blob/fsl-5_0_8/HarvardOxford-Cortical.xml)). This is a transparent broad anatomical proxy because vmPFC has no single uniquely canonical atlas parcel; it is not a selective, independent ROI-only hypothesis test. The atlas proxy contained 3,719 voxels within the analysis mask.

The proxy mean was based on each participant’s average effect estimate across those voxels. Its one-sided ROI-only test is shown as a descriptive secondary summary and is **not** the basis for the whole-brain decision. The participant estimates were retained without trimming; the most extreme standardized proxy value was 3.31 SD from the sample mean.

## Interpretation and limits

These maps are unthresholded participant-level contrast parameter estimates, not *t* or *z* maps. The group test therefore asks whether the mean estimated gain-modulator effect is positive across participants. The first-level gain modulator was mean-centered and variance-normalized before HRF convolution, so the coefficients are not response change per currency unit. The source model used response-time event durations, included response-choice and gain modulators, and modeled gain and loss in separate models; the estimate is conditional on those upstream choices ([fixed upstream methods](input/upstream-methods.md)).

No participant variance maps were supplied, so we could not weight participants by first-level precision or fit a full variance-aware mixed-effects model. The one-sample *t* test uses the between-participant variance of the supplied coefficients and assumes independent participants and approximate normality of the group estimates at each voxel. Bonferroni is conservative and voxelwise; there is no cluster-extent claim. The atlas proxy is broad and atlas-dependent. A non-significant vmPFC result cannot establish absence of a gain response or rule out effects under another model or region definition; it means these fixed inputs do not provide corrected evidence for the stated positive vmPFC hypothesis.

## Figures

![Participant-level vmPFC proxy summaries](results/figures/vmPFC_proxy_participant_effects.png)

![Unthresholded signed group t map with vmPFC proxy outline](results/figures/group_t_unthresholded_with_vmPFC.png)

![Positive voxels surviving whole-brain Bonferroni correction](results/figures/positive_fwe_thresholded.png)

## Reproducibility files

- `analysis.py` — complete input checks, group analysis, atlas ROI definition, maps and figures.
- `analysis.ipynb` — short notebook entry point to reproduce the script.
- `results/results.json` — machine-readable summary.
- `results/whole_brain_fwe_clusters.tsv` — peaks and locations of all corrected clusters.
- `results/whole_brain_summary.tsv` — correction threshold and voxel counts.
- `results/participant_qc.tsv` and `results/vmPFC_proxy_participant_effects.tsv` — QC and ROI participant summaries.
- `results/group_mean_effect.nii.gz`, `group_t_positive.nii.gz`, `group_p_fwe_bonferroni.nii.gz`, and `group_t_positive_fwe05.nii.gz` — unthresholded estimates/statistics and corrected map.
