# Potential gains and brain activity in the NARPS equal-indifference group

## Finding

**No whole-brain-corrected evidence supported the predicted vmPFC increase.** In a positive one-sample test of the 54 participants, 24 voxels survived voxelwise family-wise error (FWE) correction at .05. They formed three small clusters in posterior brain locations near MNI y = −100 mm. None overlapped the operationalized vmPFC box defined below. The most positive voxel in that box had whole-brain FWE p = .796.

The descriptive mean participant effect in the vmPFC coordinate box was 0.00047 (participant-level 95% t interval −0.0140 to 0.0150, in the supplied effect-map units). This interval is descriptive; the confirmatory decision comes from the whole-brain corrected map. The original NARPS instructions requested a yes/no decision based on whole-brain corrected analysis, which motivates this criterion ([NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

![Whole-brain corrected gain effect and descriptive vmPFC distribution](results/gain_group_results.png)

**Figure 1.** Left: positive t statistics surviving voxelwise max-statistic FWE correction (p ≤ .05), shown at the posterior peak. Three small posterior clusters survived; none was in vmPFC. Right: participant mean estimates averaged over an approximate vmPFC coordinate box; the red line marks the mean. This histogram is descriptive, not a separate ROI hypothesis test.

## Analysis

We used the 54 supplied AO86 unthresholded participant gain-effect estimates and the equal-indifference cohort table. The participant IDs matched exactly, and all 54 image checksums matched `input/sources.json`. All maps were finite and shared the same 97 × 115 × 81 image grid and affine; no participant was excluded. We analyzed 210,968 voxels with nonzero map support in at least 90% of participants, a common-coverage mask derived from the supplied maps.

At each voxel, we tested whether the group mean effect was greater than zero with a one-sided one-sample t statistic. We generated 5,000 participant-level random sign flips (seed 20261016) and used the maximum positive t statistic across the full mask for each flip. The resulting voxelwise max-statistic p values control whole-brain FWE. This sign-flip inference assumes participant effects are exchangeable under sign reversal (approximately symmetric errors under the null). The analysis uses the whole brain for correction; the approximate vmPFC location was used only to assess whether corrected findings localized to the target.

For transparent anatomical localization, we operationalized approximate vmPFC as MNI x = [−20, 20], y = [20, 60], z = [−20, 10] mm. This broad coordinate box is a descriptive anatomical proxy, not a cytoarchitectonic boundary or an independently selected ROI. In the box, the maximum t was 4.19, but its whole-brain FWE p was .796; no voxel survived correction there. The global maximum was t = 6.62 at (−26, −102, −3.6) mm (whole-brain FWE p = .0010).

## Interpretation and limits

This result does not establish that vmPFC has no gain-related response. It means this sample and these supplied maps did not provide whole-brain-corrected evidence for a positive vmPFC effect at the chosen threshold. A smaller effect, a spatially different vmPFC definition, or an effect not detectable with this sample and model remains possible. The posterior corrected clusters are outside the hypothesized region and do not count as support for the vmPFC prediction.

The inputs are participant effect estimates, not z/t statistics or group results. Upstream, the gain modulator was mean-centered and variance-normalized before HRF convolution; therefore these coefficients are not changes per currency unit. The model was fitted to response trials with response-time durations, separate response-choice and gain modulators, motion/flagged-volume/drift terms, and gain and loss represented in separate models. Thus the supplied estimate represents the gain effect conditional on that modeling choice. The task's gain range was twice its loss range, but this analysis does not estimate a gain-versus-loss contrast or the effect per dollar.

Participant variance maps and a complete executable first-level pipeline were not supplied. The group model therefore treats participant estimates equally and cannot propagate their differing first-level uncertainty in a precision-weighted model. The one-sample sign-flip test also relies on symmetry/exchangeability across participants. This is a group-analysis result for the specified 54-person cohort, not a claim about every population or task.

## Reproduction and files

Run from the workspace root with the prepared Python environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis.py
```

`analysis.py` regenerates `results/`. `results/summary.json` records the key statistics, software versions, mask, seed and exclusions; `results/voxel_results.csv` contains the voxelwise estimates and p values; `results/included_participants.tsv` records the analyzed cohort. NIfTI outputs include the common mask, mean effect, t map, whole-brain FWE p map, and thresholded t map. No time-series scans were downloaded or reprocessed; the supplied map contents were retrieved from the workspace's annexed files.

The local `skills/` folder contains the installed Jupyter notebook reproducibility skill and the neuroimaging community `datalad-get` skill. The latter documents annexed-file retrieval; this workspace uses git-annex directly and has no DataLad dataset metadata, so its DataLad-specific workflow was not invoked.
