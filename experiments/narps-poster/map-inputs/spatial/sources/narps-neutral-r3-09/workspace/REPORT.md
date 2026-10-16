# Potential gains and vmPFC activity

## Question and result

In the 54-person NARPS equal-indifference group, the supplied gain-effect estimates do **not support a positive vmPFC response to increasing potential gain** under whole-brain family-wise error correction. All 54 matched participant maps were included; no participants were excluded and no demographic covariates were added to the group-mean model. The whole-brain positive test did identify 24 significant voxels, but they formed three small posterior occipital clusters, with no overlap with the vmPFC localization envelope. This does not show that the vmPFC effect is exactly zero: the estimates are uncertain, and a non-significant result is not evidence of equivalence.

## Analysis

I analyzed all 54 supplied participant maps as unthresholded effect estimates, using a one-sample group t statistic at each voxel. Positive-direction whole-brain inference used 5,000 participant-level sign flips and the maximum t statistic across the common finite, nonzero support (198,029 voxels) to control FWE at .05. This avoids treating outside-brain zero padding as measured zero and does not require a spatial smoothness model. The procedure assumes participant independence and a symmetric null distribution; 5,000 Monte Carlo permutations give a minimum attainable p of 0.00020. The observed maximum t was 6.62 (Monte Carlo whole-brain pFWE=.0010); the 95th percentile maximum-t threshold was 5.40.

vmPFC was localized transparently in MNI152NLin2009cAsym space using a broad coordinate envelope (x −20 to 20, y 20 to 60, z −20 to 5 mm). This is an approximate localization aid, not a claim that these bounds are a unique anatomical definition. The primary inference remained whole brain, as required by the original NARPS instructions. The descriptive mean of participant-level averages in the envelope was 0.0012 contrast-estimate units (95% t interval −0.0138 to 0.0162; t(53)=0.16, two-sided uncorrected p=.876); none of the whole-brain-significant voxels were in this region.

| Positive cluster | Voxels | Peak t | Peak MNI coordinate (mm) | vmPFC overlap |
|---|---:|---:|---:|---:|
| 1 | 17 | 6.62 | (−26, −102, −3.6) | 0 |
| 2 | 2 | 5.76 | (26, −98, −1.2) | 0 |
| 3 | 5 | 6.19 | (30, −94, −8.4) | 0 |

## Figures

![Positive whole-brain max-t FWE results. Gray shows common map support; colored voxels exceed the whole-brain threshold t=5.40.](figures/whole_brain_fwe.png)

![Participant-level means within the vmPFC coordinate envelope and descriptive 95% t interval for the group mean.](figures/vmPFC_participant_estimates.png)

![Distribution of finite nonzero voxel coverage across the 54 maps.](figures/coverage_qc.png)

## Interpretation and limits

The result is a lack of corrected support for the stated vmPFC hypothesis in these supplied estimates. It does not establish no vmPFC effect or contradict a specific effect size: there is no equivalence margin or power analysis for a minimally meaningful effect, and the vmPFC interval includes positive and negative values. The posterior clusters are outside the hypothesized region and should not be treated as vmPFC evidence.

These are first-level contrast estimates averaged across four runs, not standardized statistics. Upstream gain was mean-centered and variance-normalized before HRF convolution, so the values cannot be interpreted as BOLD change per currency unit. The upstream model used response-time durations and separate gain and loss models; this gain estimate is conditional on those choices. Because the supplied files omit participant variance maps and the executable upstream pipeline, I could not model first-level uncertainty or reassess preprocessing and individual-model validity. The common support is based on finite nonzero map values rather than an independent anatomical brain mask. Finally, the approximate coordinate envelope and voxelwise max-t test do not resolve subregional vmPFC anatomy.

The task states that the potential gain range was twice the potential loss range in this group. That design context does not turn this normalized gain coefficient into a per-unit monetary slope or permit a direct gain-versus-loss comparison.

## Reproduction and supporting files

Run from the workspace root with Python 3.13 and the direct dependency pins in `requirements.txt`:

```sh
python -m pip install -r requirements.txt
python analysis/run_group.py --pilot
python analysis/run_group.py --permutations 5000 --seed 20261016
python analysis/validate_results.py
```

The analysis used Python 3.13.16 on macOS arm64; package versions are recorded in `results/group_results.json`. The original NARPS instructions state the positive vmPFC hypothesis and require teams to report whole-brain analysis; the supplied `input/upstream-methods.md` and `input/sources.json` document the fixed inputs and their provenance. See [NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) and [the NARPS study report](https://pmc.ncbi.nlm.nih.gov/articles/7771346/).

Key artifacts: `analysis/run_group.py` (analysis and figures), `analysis/validate_results.py` (independent numerical cross-check), `analysis/protocol.md`, `results/group_results.json`, `results/participant_qc.tsv`, `results/permutation_max_t.tsv.gz`, `results/independent_validation.json`, and the NIfTI mean, t, and corrected-p maps in `results/`.
