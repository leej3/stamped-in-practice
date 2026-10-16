# Potential gains and brain activity

## Result

The supplied equal-indifference maps do **not provide evidence for a positive gain effect in vmPFC** under whole-brain familywise error (FWE) control. In an a priori 10-mm sphere centered at MNI [0, 40, -8], the mean gain-effect estimate was −0.0057 (SD 0.0983; 95% t interval −0.0326 to 0.0211; N=54). No positive whole-brain FWE-significant voxels overlapped this vmPFC region.

The whole-brain test did identify 24 positive voxels at FWE α=.05. The peak was at MNI [−26, −102, −3.6] (t=6.62; max-t corrected p=.0005), in posterior occipital cortex rather than vmPFC. This is a whole-brain finding, but it does not support the specific vmPFC hypothesis. The corrected p value is at the Monte Carlo resolution floor of 1/(9,999+1).

![Participant-level effects in the a priori vmPFC region](figures/vmPFC_participant_effects.png)

![Positive group t statistics surviving whole-brain max-t correction](figures/group_t_fwe05.png)

The vmPFC estimate is a descriptive summary of each participant’s average effect within the sphere. Its uncorrected one-sided t test was not significant (t(53)=−0.43, p=.665); whole-brain inference remains the basis for the hypothesis decision, as required in the [NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

## Analysis

I modeled the 54 participant-level gain-effect maps with an unweighted one-sample group t statistic against zero. The participant is the independent sampling unit. Positive-direction inference used 9,999 participant-level sign flips and the maximum positive t statistic across the analysis mask, controlling familywise error over the whole brain at α=.05. The critical maximum t was 5.374. Sign flips preserve each participant map’s spatial structure; the method assumes participant independence and sign symmetry under the null. Because participant variance maps were not supplied, all participants have equal weight.

The vmPFC is not a uniquely bounded anatomical label, so I operationalized it before inspecting the result as a 10-mm sphere centered at [0, 40, −8] mm in MNI space: a medial, anterior, ventral prefrontal coordinate region. This ROI supports anatomical localization and descriptive estimates only. No uncorrected ROI test was used to decide the hypothesis; the decision uses whole-brain corrected results.

All 54 expected maps matched participant metadata and their source SHA256 checksums; maps were finite and shared a common shape and affine. No participant was excluded. The analysis mask was the intersection of nonzero map coverage across all participants (198,029 voxels), so every tested voxel had the same N. This avoids interpreting zero-filled locations outside a participant’s modeled coverage as measured zero effects.

The maps contain participant-level contrast parameter estimates averaged across four runs, not t or z statistics. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution, so coefficients do not measure BOLD change per unit of currency. The gain coefficient is also conditional on the fixed upstream model, which used separate gain and loss models. The equal-indifference task’s potential gain range was twice its loss range, but that fact does not convert these normalized estimates into currency-unit slopes.

A lack of vmPFC support here means that this group model and correction did not establish a positive average gain effect in the operationalized vmPFC region. It is not evidence that the true effect is exactly zero, and it does not rule out effects under other task models, anatomical definitions, or a more precise study. The confidence interval shows substantial uncertainty around small positive and negative mean estimates. This analysis cannot reassess preprocessing or individual models, and the absent participant variance maps preclude precision-weighted group inference.

## Reproduction and supporting files

Run from the project root with the supplied interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/run_analysis.py
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/validate_results.py
```

The exact analysis settings and environment identity are recorded in [protocol/protocol.md](protocol/protocol.md) and [results/run_record.txt](results/run_record.txt) (Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, Nilearn 0.14.1, NiBabel 5.4.2). Numerical results are in [results/summary.json](results/summary.json); per-map integrity and coverage checks are in [results/input_qc.tsv](results/input_qc.tsv); the saved null max-t distribution is [results/permutation_max_t.tsv](results/permutation_max_t.tsv). Independent SciPy checks of the t statistic at four voxels, the first sign-flip max statistic, and the recalculated permutation threshold/count passed ([results/validation.json](results/validation.json)). The executable analysis and validator are [code/run_analysis.py](code/run_analysis.py) and [code/validate_results.py](code/validate_results.py). Unthresholded mean, t and FWE p maps and the thresholded t map are in `results/`; code and key input-manifest hashes are in [results/provenance_sha256.txt](results/provenance_sha256.txt).
