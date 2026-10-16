# Potential gains and brain activity

## Result

In the 54-person equal-indifference mixed-gambles group (potential-gain range twice the potential-loss range), the supplied gain-effect estimates did **not** support a positive vmPFC response to increasing potential gain. The whole-brain positive-direction max-statistic test found no voxel in the broad vmPFC localization region at whole-brain FWE p < .05 (smallest vmPFC voxelwise FWE p = .162). The descriptive mean across that region was 0.0003 cope units (95% t interval −0.0140 to 0.0145; t(53) = 0.036). This interval describes between-participant uncertainty in the average cope; it does not establish that the effect is exactly zero.

The whole-brain test did detect 159 FWE-significant positive voxels elsewhere, concentrated in posterior visual cortex. The maximum was at MNI (−26, −102, −3.6), t(53) = 6.62, max-t FWE p = .00020, with a corresponding right posterior cluster. These findings do not support the vmPFC hypothesis and are not interpreted as a confirmatory gain effect in another region. The minimum possible Monte Carlo p-value with 5,000 permutations is .00020.

![Positive effect voxels surviving whole-brain max-t FWE correction](results/figures/positive_fwe_result.png)

*Figure 1. Positive mean cope estimates at voxels with whole-brain max-t FWE p < .05. The surviving locations are posterior; none overlap the vmPFC localization region. The map displays mean cope values, not t statistics.*

![Participant-level vmPFC cope estimates](results/figures/vmPFC_subject_effects.png)

*Figure 2. Each point is one participant's average cope in the vmPFC coordinate region. The bar and shaded region show the group mean and ordinary 95% one-sample t interval. This is descriptive and is not a substitute for the whole-brain corrected test.*

## Methods

The original NARPS instructions define Hypothesis 1 as a **positive parametric gain effect in vmPFC in the equal-indifference group**, and require teams to make their decision from a whole-brain corrected analysis rather than an ROI-only test ([instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). We therefore tested the positive one-sample group effect over a whole-brain mask and used the vmPFC region only to interpret whether any corrected findings were in the hypothesized area. The NARPS publication notes that vmPFC lacks a single unambiguous atlas boundary and describes a combined anatomical and Neurosynth definition ([NARPS paper](https://www.nature.com/articles/s41586-020-2314-9)). For a transparent, reproducible localization check here, we used a broad bilateral MNI coordinate box (x −20 to 20, y 20 to 60, z −25 to 10), covering medial orbitofrontal and subgenual/ventral medial frontal cortex. This approximate box is descriptive, not an exact recreation of that paper's atlas-plus-meta-analysis conjunction; the primary whole-brain correction does not depend on its boundaries.

The fixed AO86 input is a participant-level, unthresholded **contrast parameter estimate (cope)**, averaged across four runs, not a standardized test statistic or a group result. AO86 mean-centered and variance-normalized the gain modulator before HRF convolution. Cope values thus index response per unit of this standardized modulator; they cannot be read as BOLD change per currency unit. The response-time duration model included response-choice and gain modulators, and gain and loss were fit in separate models. The estimate is conditional on those fixed upstream choices. It does not establish causal effects of changing money, nor isolate gain coding from every possible task or model component.

We fit an unweighted one-sample group model to the 54 participant copes. The directional voxel statistic was a one-sample t statistic, and inference used 5,000 participant-level sign flips with the maximum positive t across the mask retained on each permutation. The corrected voxel p-values therefore control familywise error over the whole search mask, without a Gaussian random-field smoothness estimate. This test assumes independent participants and sign-symmetric errors under the null. It does not use participant-level variance maps, which were not supplied; consequently it does not weight estimates by first-level precision. A two-sided ordinary t interval is reported for the descriptive regional average, not as the confirmatory test.

The search mask included voxels with nonzero estimation support in at least 90% of maps (210,968 voxels). This accommodates minor differences in participant map support while excluding voxels outside most participants' estimates. Repeating the search over the strict all-participant intersection (198,029 voxels), while retaining the more conservative maximum distribution from the larger primary mask, left 155 FWE-significant voxels; vmPFC conclusions were unchanged. The whole-brain corrected map covers all voxels in the mask; findings outside the vmPFC localization region are treated only as secondary localization results. Voxelwise result maps are in `results/`.

## Quality checks, uncertainty, and limitations

All 54 expected participants were included, with no exclusions. Participant IDs matched the pinned metadata table; all map SHA256 checksums matched `input/sources.json`; all maps had the same MNI grid and affine, finite values, and nonzero support ranging from 217,625 to 232,390 voxels. The primary mask and stricter-intersection sensitivity check are saved with the outputs. There was no access to first-level residuals, participant variance maps, or time series, so first-level modeling and estimation quality could not be independently re-evaluated.

Failure to find corrected vmPFC support means this analysis does not provide evidence for a positive group-average vmPFC gain effect at the chosen whole-brain FWE threshold. It is not evidence that the effect is exactly absent, that every participant lacks an effect, or that another task design/model would produce the same result. The wide individual spread and regional interval reflect uncertainty; the test may have limited sensitivity to small effects at n = 54. The approximate vmPFC boundary, support mask, unweighted group model, sign-symmetry assumption, and upstream regressor scaling are additional limits. The posterior corrected voxels warrant no mechanistic interpretation from this single fixed-input analysis.

## Reproducibility

Run from the workspace root with the prepared interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis.py
```

The analysis uses Python 3.13.16, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, NiBabel 5.4.2, Nilearn 0.14.1, and Matplotlib 3.11.2. `analysis.py` writes the JSON summary, voxelwise NIfTI maps, participant-level ROI values, and figures under `results/`. The random seed is 20261016.
