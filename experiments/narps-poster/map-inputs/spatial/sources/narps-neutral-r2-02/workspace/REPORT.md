# Potential gain effects in the NARPS equal-indifference group

## Finding
The 54 supplied AO86 participant maps do **not support a positive gain-related response in vmPFC**. In the prespecified coordinate-defined vmPFC sphere (10 mm radius around MNI [0, 40, -8]), the mean participant gain-effect coefficient was −0.0057 (between-participant SD 0.0983; 95% t interval −0.0326 to 0.0211; one-sided uncorrected p=.665). The interval includes zero and both signs. The sphere is an explicit anatomical operationalization of vmPFC; it was used for a descriptive estimate, while confirmatory inference covered the whole brain.

A whole-brain one-sided max-T sign-flip test did identify positive effects somewhere in the brain (maximum t=6.62; family-wise corrected p=.00060; 10,000 sign patterns; 24 voxels passed voxelwise max-T FWE p≤.05). The three small corrected clusters were posterior (largest at MNI [−26, −102, −3.6]) and none overlapped the vmPFC sphere. Thus this whole-brain result does not support the vmPFC hypothesis. The stricter 95% common-support mask gave the same maximum and corrected p. Participant estimates in the ROI were mixed (25/54 above zero; Figure 1).

![Individual participant vmPFC-sphere mean estimates and group interval](figures/vmPFC_participant_estimates.png)

![Whole-brain max-T FWE-significant posterior voxels shown as −log10 adjusted p](figures/whole_brain_group_results.png)

## Data and model
The independent analysis unit was participant. Inputs were the 54 unthresholded gain-effect contrast parameter estimates for equal-indifference participants, averaged across four runs upstream. All 54 participant IDs matched `participants.tsv`; all file sizes and SHA-256 hashes matched `sources.json`; maps had identical 97×115×81 grids and affines, and finite values. No participant was excluded. The group model was a one-sample mean test at each voxel, giving each participant equal weight because participant-level variance maps were not supplied. A positive one-sided sign-flip permutation test used the maximum t statistic over voxels to control whole-brain family-wise error at .05. The analysis mask included voxels nonzero in at least 90% of maps; a 95% support mask was the prespecified robustness check. We verified voxelwise t statistics and sign-flip calculations against independent SciPy formulas on sampled voxels.

The vmPFC sphere is centered at [0, 40, −8] mm, radius 10 mm, with 429 voxels in the analysis mask. This transparent coordinate definition represents ventromedial prefrontal cortex for a focused descriptive summary, without searching the result map for a favorable ROI. Whole-brain correction remained the basis for inferential evidence, as required in the original NARPS instructions.

## Interpretation and limits
Each supplied value is a coefficient for a mean-centered, variance-normalized gain modulator, not a standardized statistic and not a change per dollar. The task’s potential-gain range was twice its potential-loss range, but this coefficient cannot be read as currency-scaled sensitivity or used to compare raw gain and loss slopes. It supports inference about the sign of the upstream gain-modulation coefficient, not an effect size per currency unit. Upstream response events were modeled with response-time durations and separate choice and gain modulators; gain and loss were fit in separate models. The result is conditional on these fixed first-level choices. Missing participant variance maps prevent precision-weighted mixed-effects inference. Sign-flip inference assumes independent participants and a symmetric null distribution of estimates. The coordinate sphere and analysis mask are operational definitions. The support mask treats exact zeros as outside coverage, although true exact-zero coefficients cannot be distinguished from background without supplied participant masks. Acquisition coverage and header spatial units were not independently available beyond the supplied MNI affine and map metadata.

No corrected vmPFC evidence does not establish that the vmPFC effect is exactly zero. The confidence interval allows modest positive or negative average coefficients, and sensitivity/power may be limited by sample size and the upstream model. It means these supplied maps do not provide whole-brain-corrected support for the stated positive vmPFC effect under this group model. The posterior whole-brain findings are outside the hypothesis location and should not be reinterpreted as vmPFC evidence.

## Reproduction and artifacts
Run from this directory with the prepared interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/group_analysis.py
```

The fixed seed is 20261016. Environment: Python 3.13.16; NumPy 2.5.4; SciPy 1.18.1; pandas 3.0.6; NiBabel 5.4.2; Nilearn 0.14.1; Matplotlib 3.11.2. No package installation or upstream refitting was performed. See `protocol/analysis-plan.md`, `input/upstream-methods.md`, `input/sources.json`, and `results/summary.json` for the protocol, source pins, checksums, parameters, and complete numerical output. `results/participant_qc.tsv` and `results/vmPFC_participant_values.tsv` provide participant-level checks and values; NIfTI files in `results/` preserve group maps.

Original study source: [NARPS original analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). The source PDF endpoint was not reachable during this run; its stated whole-brain-correction requirement was provided in the task.
