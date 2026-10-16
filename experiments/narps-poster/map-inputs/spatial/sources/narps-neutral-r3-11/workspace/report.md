# Potential gains and vmPFC activity in the equal-indifference group

## Question and result

The NARPS Hypothesis 1 prediction is a positive parametric gain effect in ventromedial prefrontal cortex (vmPFC) for participants in the equal-indifference group ([original analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). I tested whether the group mean of the supplied participant gain-effect maps was positive, with whole-brain family-wise error (FWE) control.

**The supplied maps do not support a positive vmPFC effect after whole-brain correction.** None of the 23 voxels significant under the whole-brain correction fell in the vmPFC localization envelope. The strongest voxel in that envelope had *t*(53) = 4.19, but its whole-brain max-statistic FWE *p* was .771. The envelope mean participant effect was −0.0014 cope units (participant SD 0.0534; participant bootstrap 95% CI for the mean [−0.0152, 0.0127]). The positive whole-brain corrected maximum was posterior (MNI −26, −102, −3.6 mm; *t*(53) = 6.62; FWE *p* = .0010, the smallest attainable with 5,000 permutations and the plus-one estimator).

This is a lack of corrected support for the stated vmPFC hypothesis in these fixed maps. It does not establish that the true effect is exactly zero, that vmPFC never responds to gains, or that the task has no gain-related neural response. The interval allows effects of either sign, and the supplied upstream estimates have important limits described below.

## Group analysis

The analysis used all 54 equal-indifference participants and their unthresholded AO86 gain contrast parameter estimates. I fit an equal-weight one-sample group *t* model at each voxel, testing the directional alternative that the population mean cope is positive. For multiplicity control, I generated 5,000 participant-level sign flips (seed 20261016), recomputed the one-sample statistic over the entire analysis mask for each permutation, and used the permutation distribution of the maximum positive *t* statistic to calculate voxelwise max-*T* FWE *p* values. This preserves each participant's spatial map while controlling family-wise error over the tested brain. Inference assumes independent participants and a sign-flip/symmetric null; the Monte Carlo *p* resolution is 1/5,001.

The analysis mask was the standard MNI152 brain mask resampled to the supplied maps' grid, intersected with voxels nonzero in every participant map. vmPFC was operationalized for localization as the bilateral MNI envelope |x| ≤ 20, y = 20–65, z = −25–15 mm. This broad anatomical envelope makes the region check explicit; it was not used to restrict inference or to claim an uncorrected ROI result. The hypothesis is considered supported only if positive signal survives whole-brain FWE correction and overlaps this envelope.

The upstream NARPS model mean-centered and variance-normalized the gain modulator before HRF convolution. Thus, a cope is the participant's estimated response to that standardized modulator under the specified event model, not a response change per dollar. Response trials were modeled with response-time durations and separate response-choice and gain modulators; gain and loss were fit in separate models. The group analysis therefore concerns this conditional gain-modulator estimate, not a causal or currency-scaled slope.

## Quality checks and uncertainty

All 54 participant IDs matched the metadata and supplied manifest; all map checksums matched, image dimensions and affines agreed, and all voxel values were finite. No participants were excluded. The resulting common analysis mask contained 186,400 voxels. Participant-wide map means ranged from −0.139 to 0.116 cope units and maximum absolute voxel values ranged from 1.45 to 10.45; these summaries were retained as QC rather than used for outcome-dependent exclusions. See [`participant_qc.csv`](results/participant_qc.csv).

The 23 corrected positive voxels were all posterior (MNI y = −104 to −94 mm), not in the target region. This unexpected location should be interpreted cautiously and is not evidence for the vmPFC prediction. Whole-brain correction is stringent, while the vmPFC mean interval is not narrow enough to demonstrate practical equivalence to zero. A null corrected result can reflect a small or heterogeneous effect, noise, modeling choices, or limited sensitivity as well as absence of the hypothesized association.

The supplied files lack participant-level variance maps, so the group model cannot weight participants by first-level precision or propagate their contrast-estimate uncertainty in a hierarchical model. The upstream pipeline is fixed and not re-estimated here; the gain regressor's normalization, response-duration model, and separate gain/loss models constrain interpretation. The results are also specific to this one group's cope maps, mask, and directional test. They should not be generalized to all potential-gain ranges or to other task/model specifications.

## Figures

![Unthresholded mean gain cope and whole-brain corrected positive statistic map](figures/group_gain_maps.png)

Left: group mean participant cope estimate, unthresholded. Right: positive *t* values among voxels surviving one-sided whole-brain max-*T* FWE *p* ≤ .05 (23 voxels; displayed at *t* ≥ 4 for visibility); cyan outlines show the vmPFC localization envelope. Axial slices are in MNI z coordinates. The posterior corrected signal lies outside the vmPFC envelope.

![Participant-level vmPFC-envelope gain cope distribution](figures/vmpfc_participant_distribution.png)

Each observation is one participant's mean cope within the vmPFC localization envelope. The bootstrap interval summarizes the group mean; it is descriptive and is not a separate confirmatory ROI test.

## Reproducibility files

- [`analysis.py`](analysis.py): checksum and geometry QC, group model, permutation correction, and figure generation.
- [`results/summary.json`](results/summary.json): machine-readable model, quality, and inference summary.
- [`results/significant_peaks.csv`](results/significant_peaks.csv): the ten strongest corrected positive voxels.
- [`results/mean_cope.nii.gz`](results/mean_cope.nii.gz), [`results/t_positive.nii.gz`](results/t_positive.nii.gz), [`results/p_fwe_maxT.nii.gz`](results/p_fwe_maxT.nii.gz): group maps on the input grid. Voxels outside the analysis mask are NaN in estimate/statistic maps and set to 1 in *p* maps.
- [`results/standard_mni152_brain_mask.nii.gz`](results/standard_mni152_brain_mask.nii.gz) and [`results/mni152_template.nii.gz`](results/mni152_template.nii.gz): standard-space references used for analysis and display.

Run from the workspace root with the prepared Python environment: `python analysis.py`. The script uses NumPy, SciPy, pandas, Matplotlib, NiBabel, and Nilearn.
