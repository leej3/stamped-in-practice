# Potential gains and brain activity: group analysis

## Conclusion

The supplied gain-effect maps do **not** support a positive gain response in vmPFC under whole-brain family-wise error (FWE) control. A positive whole-brain signal did survive correction, but it was posterior (peak MNI coordinate −26, −102, −3.6 mm) and did not overlap the independently defined vmPFC proxy. This is evidence against detecting the hypothesized response with this analysis and these data; it is not evidence that the true vmPFC effect is exactly zero.

## Data and model

All 54 equal-indifference participants were included. Map IDs matched the cohort table, all 54 source checksums and byte counts matched, and the maps shared a 97 × 115 × 81 grid with 2 × 2 × 2.4 mm voxels in MNI152NLin2009cAsym space. No participants were excluded. The analysis mask comprised 198,029 voxels with finite, nonzero values in every map.

At each voxel, I fit a one-sample group t test to participant cope estimates against zero, testing the prespecified positive direction (df = 53). For confirmatory whole-brain inference, I used 10,000 independent participant-level sign flips and the maximum positive t statistic over the full mask. The add-one Monte Carlo p values control voxelwise whole-brain FWE; the 95th percentile maximum-t threshold was 5.381. The test assumes independent participants and a symmetric null distribution for the participant estimates. The seed was 20261016.

I operationalized vmPFC with an independent Harvard–Oxford cortical atlas (2 mm, max-probability threshold 25): the bilateral Frontal Medial Cortex and Subcallosal Cortex labels (1,422 in-mask voxels). This is an anatomical proxy, not a unique consensus boundary for vmPFC. As a broader boundary sensitivity check, I added the atlas's Frontal Orbital Cortex label (3,719 voxels total). The whole-brain corrected test remains the basis for the hypothesis decision, consistent with the [original NARPS instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

## Results

The max-T test identified 24 positive voxels at FWE p ≤ .05 (three 6-connected components, sizes 17, 5, and 2 voxels). The peak was at (−26, −102, −3.6) mm, t(53) = 6.62, Monte Carlo pFWE = .0006. None of these voxels fell in the vmPFC proxy or the broader medial/orbital frontal mask. The minimum corrected p within either mask was .780.

The average cope within the vmPFC proxy was 0.0027 (95% t interval −0.0217 to 0.0270; one-sided uncorrected p = .414). In the broader mask including Frontal Orbital Cortex, the mean was −0.0048 (95% t interval −0.0243 to 0.0147; one-sided uncorrected p = .690). These intervals describe variation in the supplied cope estimates, not precision-weighted estimates from the original time series.

![Mean gain-effect estimates](figures/group_mean_effect.png)

*Figure 1. Mean participant cope estimates. The color scale is in the upstream model's arbitrary coefficient units. A standard MNI template is shown only as an anatomical underlay.*

![Whole-brain FWE-corrected positive result](figures/group_t_fwe_corrected.png)

*Figure 2. Positive group t values exceeding the whole-brain maximum-t threshold (5.381), displayed on a standard MNI template. The corrected voxels are posterior and outside the vmPFC proxy.*

![vmPFC proxy](figures/vmPFC_proxy.png)

*Figure 3. Atlas proxy used to identify vmPFC: Frontal Medial and Subcallosal Cortex. The map is an anatomical guide; inference uses the whole-brain family-wise correction.*

![Participant vmPFC estimates](figures/vmPFC_participant_estimates.png)

*Figure 4. Subject-level mean cope estimates within the vmPFC proxy and their group mean interval.*

## Interpretation and limitations

The upstream coefficient is for a mean-centered, variance-normalized gain modulator, so it is not a response change per currency unit. The maps average four runs, but are participant-level effect estimates rather than standardized statistics. The upstream model used response-time durations and separate gain and loss models; therefore, this analysis tests the supplied gain coefficient conditional on those modeling choices and cannot establish how the signal would look under another first-level model. In this equal-indifference group, gains also span twice the range of losses.

Participant variance maps were not supplied. The group t test therefore treats each participant cope map as one observation and cannot weight participants by first-level precision or fit a conventional variance-component mixed-effects model. Its uncertainty reflects the observed across-participant spread, which mixes true heterogeneity and estimation error. The atlas ROI boundary is approximate; changing it did not change the conclusion, but no atlas mask exhausts all plausible vmPFC definitions. Finally, a nonsignificant vmPFC result does not demonstrate no effect: effects too small or heterogeneous for this sample and this upstream model remain plausible.

## Reproducibility

Run from the workspace root with the provided Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/analyze.py
```

The script verifies map IDs, source checksums, byte sizes, and grid consistency; performs the analysis; and writes the outputs under `analysis/results/` and `analysis/figures/`. It uses NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2, and Nilearn 0.14.1. Nilearn fetches/caches the Harvard–Oxford atlas and MNI template if they are not already available. No time-series scans are used.

Key outputs: `results/summary.tsv`, `results/quality_checks.json`, `results/input_integrity.tsv`, group mean/t/FWE p maps, and the vmPFC ROI mask. The p map is NaN outside the analysis mask.
