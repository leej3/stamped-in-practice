# Supporting results

- `group_results.json`: analysis settings, numerical summary, software versions, and verified input checksums.
- `participant_map_qc.tsv`: per-map finite-value and coverage checks plus coefficient summaries.
- `participant_vmPFC_effects.tsv`: participant-average effects in the anatomical vmPFC approximation.
- `group_mean_effect.nii.gz`, `group_tstat.nii.gz`, `neglog10_p_fwe.nii.gz`, and `significant_fwe_mask.nii.gz`: voxelwise group outputs.
- `group_coverage_mask.nii.gz` and `aal3_vmPFC_localization_mask.nii.gz`: search and localization masks.
- `max_t_null.npy`: the seeded permutation maxima used for the empirical FWE threshold.
- `significant_components.tsv`: descriptive connected components of corrected voxels; cluster extent is not the inferential statistic.
