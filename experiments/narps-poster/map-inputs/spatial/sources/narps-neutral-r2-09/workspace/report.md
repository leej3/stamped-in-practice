# Potential gains and brain activity in the NARPS equal-indifference group

**Question.** Do larger potential gains produce a greater fMRI response in vmPFC? **Answer.** This group analysis found no support for a positive vmPFC effect. The whole-brain corrected positive findings were in occipital-pole voxels, outside the vmPFC region.

## Analysis

I analyzed the 54 supplied AO86 participant gain-effect maps as the units of analysis. The source table confirms 54 equal-indifference participants (age 26.1 ± 3.0 years, range 21–37; 30 female, 24 male). Here, the nominal range of potential gains was twice that of potential losses. The maps had matching geometry (97 × 115 × 81; 2 × 2 × 2.4 mm) and finite values; every image matched its SHA256 in the input manifest. All 54 were retained. I used the intersection of their nonzero fitted support (198,029 voxels; 88% of the median individual support) so that no subject's outside-coverage zeros entered the group estimate. The group model was a one-sample intercept-only test of mean cope > 0, with equal subject weights.

For whole-brain family-wise error control, I used a one-sided maximum-t sign-flip test across the common-support mask (9,999 Monte Carlo permutations; seed 20261016; α = .05). This preserves spatial dependence and controls the maximum statistic across tested voxels. Sign flips assume independent participants and approximately symmetric null errors. The supplied files lack participant variance maps, so a variance-weighted mixed-effects group model could not be fit; the one-sample model treats participants equally. The original NARPS instructions specify whole-brain-corrected group results for hypothesis decisions ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The hypothesis names vmPFC but does not specify exact boundaries. For anatomical localization I used an independent Harvard–Oxford cortical max-probability atlas at 25% threshold, defining a transparent vmPFC proxy as its *Frontal Medial Cortex* plus *Subcallosal Cortex* labels. The atlas is a probabilistic structural atlas distributed with FSL ([atlas description](https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html)). This proxy did not determine the correction: the primary test covered the full common-support mask, and the atlas was used only to identify where the corrected results fell and summarize subject-level effects in vmPFC.

## Results

| Analysis | Result |
|---|---:|
| Whole-brain FWE-significant positive voxels | 24, in 3 small 26-connected components |
| Peak positive statistic | *t*(53) = 6.62 at MNI (−26, −102, −3.6); one-sided max-T FWE *p* = .0007 |
| Anatomical label at peak | Occipital Pole; 0 significant voxels overlapped the vmPFC proxy |
| vmPFC proxy participant mean | 0.0027 cope units; 95% t interval [−0.0217, 0.0270]; one-sided descriptive *p* = .414 |

The max-T 5% critical value was *t* = 5.382. Of the 24 corrected voxels, 21 were labeled Occipital Pole and 3 fell outside a Harvard–Oxford label; their peaks were 4.0–5.7 mm from the edge of common fitted support, so this non-target finding merits caution. No corrected positive voxel was in the vmPFC proxy, and its participant-average estimate was near zero with an interval spanning positive and negative values. Therefore, these data do not establish that gain-related response increases in vmPFC in this group.

![Whole-brain maximum-t FWE results at p ≤ .05, shown on standard MNI anatomy at axial slices −8, −4, and 0 mm. The corrected positive voxels are confined to posterior occipital locations.](figures/whole_brain_fwe.png)

![Participant-level mean gain-effect estimates within the vmPFC atlas proxy. The line is the mean and the band is its two-sided 95% t interval.](figures/vmPFC_participant_estimates.png)

## Interpretation and limits

The null vmPFC result is a **lack of corrected support**, not evidence that the true effect is exactly zero. The ROI interval is compatible with small effects in either direction, and 54 participants may not resolve small or spatially variable effects. The anatomical proxy is one defensible boundary choice; vmPFC has no single universally agreed atlas boundary. The gain effect itself is the upstream model's mean-centered, variance-normalized gain-modulator coefficient, not BOLD change per currency unit. It is conditional on AO86's response-time-duration model with response-choice terms and separate gain and loss models, so it does not test gain against loss sensitivity or isolate a causal neural response to monetary value. Preprocessing and first-level modeling were fixed and not re-estimated. These group-stage results should not be generalized to the equal-range group or interpreted as behavioral effects.

## Reproducibility

- Protocol and scope: [analysis/protocol.md](analysis/protocol.md)
- Executable analysis: [analysis/run_group.py](analysis/run_group.py)
- Replay comparison: [analysis/replay_validate.py](analysis/replay_validate.py), [results/replay_validation.txt](results/replay_validation.txt); run corrections: [results/attempts/attempt_history.md](results/attempts/attempt_history.md)
- Fixed upstream methods and input provenance: [input/upstream-methods.md](input/upstream-methods.md), [input/sources.json](input/sources.json)
- Machine-readable results: [results/summary.json](results/summary.json); participant QC: [results/participant_qc.tsv](results/participant_qc.tsv); corrected peaks: [results/fwe_clusters.tsv](results/fwe_clusters.tsv)
- Statistical maps and retained atlas/ROI: [results/](results/)
- Validated interpreter: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python` (Python 3.13.16; NumPy 2.5.4; SciPy 1.18.1; pandas 3.0.6; NiBabel 5.4.2; Nilearn 0.14.1). Run from this workspace with `python analysis/run_group.py`; Nilearn supplies the versioned Harvard–Oxford atlas and the standard template used only in the figure. Key parameters, versions, input-manifest hash, seed, and permutation count are recorded in `results/summary.json`.

An early run encountered an output-assignment shape error. After fixing it, inspection found an implausible permutation threshold caused by a scaling error in the permutation t statistic. The denominator was corrected, and the final script now checks numerical equivalence to the conventional one-sample t statistic before permutation inference. Attempt logs are retained under `results/attempts/`; only the corrected run is represented in the results above.
