# Potential gain and brain activity in the NARPS equal-indifference group

## Question and conclusion

Does the participant-level fMRI response increase with potential gain in vmPFC? **These maps do not support a positive vmPFC response after whole-brain familywise correction.** The whole-brain test did identify 24 positive voxels in three small posterior clusters, but their peaks lie at MNI y = −94 to −102 mm, far posterior to vmPFC. No voxel in the independently defined vmPFC proxy survived correction (minimum max-T FWE p = 0.788). This is not evidence that the true vmPFC effect is exactly zero; the result is a lack of corrected support at this sample size and with these inputs.

## Data and estimand

The sample comprises all 54 equal-indifference participants (30 women, 24 men; mean age 26.1 years, SD 3.0); no participants were excluded. Each supplied map is AO86’s unthresholded gain contrast estimate, averaged over four runs, in MNI152NLin2009cAsym space. The participant is the independent sampling unit. The group estimand is the mean of these contrast estimates, tested against zero in the positive direction.

These values are contrast parameter estimates, not t/z statistics. The upstream gain regressor was mean-centered and variance-normalized before HRF convolution, so the maps do not express response change per currency unit. They are conditional on the fixed upstream modeling choices, including response-time durations, separate choice and gain modulators, and separate gain and loss models. Participant variance maps are unavailable, so this is a one-sample group model of the participant effects, not a second-level model weighted by within-participant precision.

## Group model and checks

We used an intercept-only voxelwise one-sample t model (df = 53), with a one-sided positive alternative. The common analysis domain is the intersection of nonzero support across the 54 maps (198,029 voxels); all maps had matching shape and affine, finite values, and verified against the checksums in `input/sources.json`. This common-support mask avoids treating absent map coverage as a measured zero, but the resulting inference applies only to that intersection.

Whole-brain familywise error was controlled with 9,999 Monte Carlo sign flips and a maximum positive t statistic across all tested voxels for each flip (seed 240519; p resolution 0.0001). This test relies on sign exchangeability under the null. We independently checked the observed and permuted t formulas against SciPy. The 95th percentile of the null maximum-t distribution was 5.36. At pFWE ≤ .05, 24 voxels survived in three small clusters; the most significant voxel was at (−26, −102, −3.6) mm, t(53) = 6.62, pFWE = 0.0012. The other peaks were (26, −98, −1.2) and (30, −94, −8.4) mm. These posterior locations do not identify vmPFC. The peak coordinate is outside the AAL3v2 atlas labels (atlas background), so its precise anatomical assignment is uncertain.

We identified vmPFC independently of the observed map using a broad anatomical proxy: the bilateral AAL3v2 medial orbital frontal and rectus labels intersected with the common analysis mask (2,400 voxels). No proxy voxels passed whole-brain max-T correction; the minimum corrected p within it was 0.788. As a secondary summary, averaging each participant’s effects across this proxy gave mean = −0.0037 contrast units, 95% t interval [−0.0287, 0.0212], t(53) = −0.30, one-sided p = 0.617. Leave-one-participant-out means ranged from −0.0088 to −0.0004. A less stringent whole-brain BH-FDR sensitivity produced 210 voxels at q ≤ .05 overall, including one proxy voxel at q = 0.0499; this does not meet the required FWE criterion and does not alter the primary conclusion.

The participant-level whole-brain mean contrast ranged from −0.134 to 0.104 across participants. The figures show this distribution and the proxy-level values rather than only the group mean.

## Uncertainty and scope

A lack of corrected support means these data do not establish a positive vmPFC response at the specified error rate; it does not prove no response or rule out a smaller effect. The broad AAL proxy is an operational anatomical approximation, not a uniquely agreed boundary for vmPFC. Whole-brain inference also depends on the common-support mask and the symmetric-null/sign-flip assumption. The small posterior findings are spatially distant from the hypothesis and include atlas-background peaks, so they should not be interpreted as confirmation of the vmPFC hypothesis. Upstream preprocessing and participant models are fixed and cannot be audited or revised here; individual variance maps and time-series scans were intentionally not used.

## Reproducibility and files

Run from the project root with the supplied Python 3.13.16 interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/analyze.py --permutations 9999 --seed 240519
```

The script verifies input hashes, checks group geometry and values, runs inference, and regenerates result maps, tables, and figures. Environment package versions and source hashes are recorded in `results/summary.json`. The pre-analysis choices are in `protocol/analysis-plan.md`; the failed pilot and invalid first permutation denominator are retained and explained in `results/pilot-attempt-log.md` and `results/invalid-standard-deviation-denominator/`. The latter outputs are invalid and not used above.

Figures: [whole-brain corrected peaks](../figures/positive_maxT_FWE_peak.png), [vmPFC-centered corrected map](../figures/positive_maxT_FWE.png), [proxy participant distribution](../figures/vmPFC_proxy_distribution.png), and [participant map summaries](../figures/participant_qc.png).

Original study instructions: [NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). The instructions asked teams to evaluate the hypotheses with whole-brain results. Anatomical proxy used here is from Nilearn’s [AAL3v2 atlas](https://www.gin.cnrs.fr/en/tools/aal/).
