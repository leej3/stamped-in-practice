# Potential gains and brain activity

## Result

**The supplied group maps do not support a positive gain response in vmPFC under whole-brain family-wise correction.** Across 54 equal-indifference participants, no voxel in the prespecified vmPFC coordinate ROI overlapped a positive whole-brain significant voxel. A descriptive mean over that ROI was close to zero (mean participant ROI estimate = 0.0022 model units; 95% t interval −0.0155 to 0.0200; one-sided, uncorrected *p* = .400). This is not evidence that the true effect is exactly zero.

The positive whole-brain search did identify 24 significant voxels in three small clusters, all posterior occipital (largest peak MNI −26, −102, −3.6; *t*(53) = 6.62; max-*T* FWE *p* = .0008). These findings do not provide anatomical support for the stated vmPFC hypothesis and should be treated as unexpected spatial results, not as a substitute confirmation.

![Positive gain-effect voxels surviving whole-brain max-T correction](results/whole_brain_fwe.png)

![Distribution of participant vmPFC ROI estimates](results/vmPFC_roi_distribution.png)

## Analysis

The input comprised all 54 AO86 equal-indifference unthresholded participant gain-effect (COPE) maps named in the supplied metadata; participant IDs, grids, finite values, and coverage were checked. No participants were excluded. Maps shared a 97 × 115 × 81 MNI152NLin2009cAsym grid at 2 × 2 × 2.4 mm. The analysis mask included voxels with nonzero map support in at least 90% of participants (210,968 voxels), avoiding inference on the zero-filled exterior while retaining minor coverage variation. Individual map ranges and represented voxel counts are in [`participant_qc.tsv`](results/participant_qc.tsv).

At each masked voxel, I estimated the group mean with a one-sample t statistic and tested the hypothesis-predicted positive direction. Family-wise error was controlled across the entire mask using 9,999 random participant-level sign flips and the maximum positive t statistic in each permutation (seed 861734; 95th percentile critical *t* = 5.389). This max-*T* procedure corrects the whole-brain voxelwise search and preserves spatial dependence among voxels. The test assumes participant effects are exchangeable under sign reversal. Inference is at the voxel level; no cluster-extent threshold was used.

Because “vmPFC” does not identify a unique voxel mask, I operationalized it independently of these results as bilateral medial anterior ventral prefrontal coordinates (|x| ≤ 10, 0 ≤ y ≤ 50, −20 ≤ z ≤ 10 mm, MNI). The ROI summary is descriptive and its one-sided *p* is uncorrected; it is not the basis for the hypothesis decision. The decision relies on whether any positive whole-brain corrected voxels intersect this a priori anatomical ROI.

## What the maps measure and limits

These are participant contrast parameter estimates, not standardized *t* or *z* maps. In AO86’s upstream model, the gain modulator was mean-centered and variance-normalized before HRF convolution. Thus an effect reflects a change with the within-task normalized gain regressor, **not a BOLD change per currency unit**. Response durations followed reaction times; response choice and gain modulators were modeled, nonresponse trials and nuisance terms were included, and runs were combined. Gain and loss were estimated in separate models, so the supplied gain coefficient is conditional on that modeling choice. The group analysis cannot revisit those choices or establish causal neural encoding.

Participant variance maps and the complete executable first-level pipeline were not supplied. The one-sample group model therefore estimates between-participant variation in the supplied effects; it cannot propagate first-level uncertainty as a precision-weighted mixed-effects analysis could. A null corrected vmPFC result means this analysis did not find sufficiently strong, spatially coherent evidence at the chosen whole-brain error rate. It does not establish absence of a smaller effect, rule out effects under a different defensible vmPFC definition or upstream model, or show that the task has no gain sensitivity.

## Reproduction

Run `python analyze.py` with the supplied scientific environment to recreate the group maps, QC table, summary, and initial figures; then run `python finalize_results.py` to add corrected-cluster summaries and format the final whole-brain figure. Outputs are in [`results/`](results/). The software uses Python, NumPy, SciPy, pandas, NiBabel, Matplotlib, and Nilearn. The original NARPS Hypothesis 1 specifies a positive parametric gain effect in vmPFC for the equal-indifference group ([analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)); this report applies whole-brain corrected inference as requested.
