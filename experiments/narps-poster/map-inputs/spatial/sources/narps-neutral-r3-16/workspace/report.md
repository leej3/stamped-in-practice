# Potential gains and brain activity

## Result

**This group analysis does not support a positive gain effect in vmPFC at whole-brain family-wise error rate (FWER) .05.** A one-sided, voxelwise maximum-statistic permutation test found 24 significant voxels across the covered brain, but none overlapped the prespecified anatomical vmPFC proxy. The significant voxels formed small bilateral posterior inferior cerebellar foci (17, 5, and 2 connected voxels; connectedness is descriptive, while significance is voxelwise FWER corrected). The strongest voxel was at MNI [−26, −102, −3.6] mm, *t*(53) = 6.62, *p*FWER = .0010. The bilateral posterior locations do not support the hypothesized vmPFC response.

Across the vmPFC proxy, the mean participant effect estimate was 0.0027 cope units (95% *t* interval [−0.0217, 0.0270]); this descriptive interval includes zero. This is not a separate confirmatory ROI test. The conclusion is that the stated hypothesis was not supported by this analysis—not that a vmPFC effect is absent.

![Whole-brain max-T permutation result with vmPFC proxy outlined](figures/whole_brain_fwe_maxT.png)

*Figure 1. Positive one-sample effects with voxelwise maximum-t permutation pFWER < .05 are shown in warm colors. Cyan outlines the vmPFC proxy used for anatomical localization. Corrected foci are posterior and do not overlap the proxy.*

![Participant-level vmPFC proxy estimates](figures/vmPFC_subject_effects.png)

*Figure 2. Each point is one participant's mean effect estimate over the vmPFC proxy. The point and interval show the across-participant mean and descriptive 95% t interval. The outcome is in cope units, not currency units.*

## Analysis

In the equal-indifference group, the potential-gain range was twice the potential-loss range. I analyzed all 54 supplied AO86 equal-indifference participant maps. The maps were checked against the participant table and source metadata; all map byte counts and SHA256 checksums matched, and all maps shared the same 97 × 115 × 81 grid and affine. No participants were excluded. The common coverage mask retained voxels finite in every map and nonzero in all maps (198,029 voxels; voxel size 2 × 2 × 2.4 mm). This strict intersection avoids treating out-of-coverage zero values as observations. Exact zero may still be a valid estimate, so the mask remains an operational coverage proxy and may omit some true zeros.

The group model was an intercept-only, unweighted one-sample model of the participant effect maps. The directional hypothesis was a positive mean. Inference used 5,000 sign-flip permutations and a voxelwise maximum-*t* statistic over the whole coverage mask (fixed seed 20261016; one-sided test). This controls the family-wise error rate over the searched voxels without relying on a parametric smoothness estimate. It relies on sign symmetry of participant-level errors under the null. The original NARPS instructions asked teams to base decisions on whole-brain-corrected findings for the hypothesized region; the vmPFC judgment here follows that requirement rather than treating an uncorrected ROI result as support ([original analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

For anatomical localization, the vmPFC proxy was defined before looking at the group result as Harvard–Oxford cortical atlas “Frontal Medial Cortex” and “Subcallosal Cortex” labels, resampled to the supplied MNI152NLin2009cAsym grid and clipped to medial ventral coordinates (|x| ≤ 20 mm, y > 0 mm, z ≤ 15 mm). This is a transparent approximation of vmPFC, not a universally agreed boundary. The atlas and map templates are not identical, so the resampled boundary is approximate. Crucially, this proxy did not restrict the corrected whole-brain search.

## Interpretation and limits

The supplied values are participant contrast parameter estimates (cope maps), not *t* or *z* statistics. They estimate each participant's fitted gain-modulator coefficient; AO86 mean-centered and variance-normalized that modulator before HRF convolution. Therefore the group coefficient cannot be read as BOLD change per dollar. The gain estimate is also conditional on the fixed upstream model, where gain and loss were modeled separately and response-time durations, choice and gain modulators, motion, flagged volumes, and drift terms were included. This analysis does not revisit those choices.

All participants contribute equally because participant variance maps are unavailable. The group test therefore cannot weight estimates by first-level precision, and uncertainty in the upstream estimates is not modeled explicitly. The result applies to the supplied equal-indifference cohort and this fixed upstream analysis. A nonsignificant whole-brain-corrected vmPFC result means evidence did not exceed this analysis's threshold; it does not establish a zero effect, rule out a smaller effect, or adjudicate other reasonable preprocessing and modeling pipelines.

## Reproducibility

Run `python code/analyze.py`, `python code/make_figures.py`, and `python code/summarize_components.py` in sequence using Python 3.13.16, NumPy 2.5.4, NiBabel 5.4.2, and Nilearn 0.14.1. `analysis.ipynb` provides the same top-to-bottom workflow. The group maps, mask, permutation p map, atlas proxy mask, participant QC table, top-voxel and connected-component tables, and machine-readable summary are in `results/`.
