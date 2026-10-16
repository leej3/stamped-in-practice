# Scientific assessment — potential gain and vmPFC response

**Scientific adequacy: supported**, for the report's stated conclusion that the supplied group maps provide no whole-brain-corrected evidence of a positive vmPFC response. This supports a defensible absence of a positive finding; it does not establish a zero effect or disprove all gain sensitivity. The positive Hypothesis 1 effect itself is **not supported by these results**.

## Evidence and analysis

The analysis includes the complete equal-indifference cohort (54 participants, no exclusions), verifies input SHA-256 values and common image grids, rejects non-finite values, and uses the intersection of nonzero estimation support so missing voxels are not treated as zero (`analysis/run_group_analysis.py`, `results/map_quality.tsv`, `results/group_results.json`). The input maps are participant gain-effect estimates, averaged across runs, not t-statistics; the analysis correctly treats participants as independent units and does not interpret coefficients per unit of currency (`input/upstream-methods.md`, `results/report.md`).

The group test is a one-sample positive-effect test with 5,000 synchronized participant-level sign flips and a maximum-t statistic across the whole 198,029-voxel all-participant mask. This controls one-sided voxelwise whole-brain FWE at 0.05 without a spatial-smoothness model. It relies on exchangeability/symmetry of participant effects under the null. The observed maximum-t cutoff is 5.36. Twenty-four corrected positive voxels appeared in three small posterior clusters; the peak is t=6.62, whole-brain FWE p=0.0008 at MNI (-26, -102, -3.6). None overlaps the vmPFC approximation (`results/group_results.json`, `results/fwe_clusters.tsv`).

The vmPFC approximation uses Harvard-Oxford Frontal Medial, Subcallosal, Frontal Orbital and Paracingulate labels, restricted to |x|≤20 mm, y≥0 mm and z≤0 mm, then intersects with group coverage. This is transparently described as an operational anatomical approximation. The ROI mean is -0.0011 (SD 0.0796; 95% t interval [-0.0228, 0.0207]); 25/54 participant means are positive. The strongest ROI voxel has t=4.19 and whole-brain FWE p=0.788. The ROI mean and interval are descriptive; whole-brain corrected maps carry the primary inference. Figures distinguish the uncorrected display threshold from corrected inference (`results/report.md`, `results/figures/whole_brain_gain_t_map.png`, `results/figures/vmPFC_participant_effects.png`).

## Interpretation and limits

The reported conclusion is appropriately narrow: there is no corrected support for a positive vmPFC response in this group, while the data do not establish absence or equivalence. The interval is compatible with modest positive or negative ROI means. The atlas boundary is approximate, and the original NARPS localization used additional Neurosynth information; another defensible vmPFC definition could change the descriptive ROI summary. The primary whole-brain test is less dependent on that boundary.

The fixed upstream model mean-centered and variance-normalized the gain regressor, so these coefficients are not BOLD change per currency unit. Gain and loss were modeled separately, so this does not compare gain and loss slopes. Participant-level variance maps are unavailable, preventing precision weighting and propagation of first-level uncertainty. These limits are stated in `input/upstream-methods.md` and `results/report.md` and are compatible with a group analysis conditional on the supplied maps.

## Replay distinction

The retained worker logs show an earlier successful `pixi run python analysis/run_group_analysis.py` on the worker host. The one authorized fresh-clone replay in this assessment did not reach the analysis: the supplied runner classified `input/participants.tsv` as a shipped output and removed it before launch, producing `FileNotFoundError`. This is a replay-harness limitation, not evidence that the scientific result was independently reproduced here. The full attempt and clone are retained at [the replay record](./2026-10-16-fresh-rerun.json) and [replay workspace](./replay-work/replay-1/clone/).
