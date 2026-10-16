# NARPS equal-indifference gain effect: group analysis

This workspace contains a script-first, reproducible group analysis of the 54 fixed AO86 participant gain-effect maps. The concise scientific report is in [`report.md`](report.md).

## Reproduce

Use Python 3.13 with NumPy, SciPy, pandas, Matplotlib, NiBabel, and Nilearn (the supplied shared environment has these packages):

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/fetch_maps.py
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/group_analysis.py
```

The first command restores the exact participant effect maps listed in `input/sources.json` to `work/maps/` and verifies every SHA-256 before analysis. It retrieves no fMRI time series. The second command writes group maps, QC summaries, voxelwise results, and figures. Set `NARPS_PERMUTATIONS` to change the number of sign-flip draws; the default is 10,000 and the seed is recorded in `results/group_results.json`.

## Main files

- `scripts/fetch_maps.py`: exact-file retrieval and checksum validation.
- `scripts/group_analysis.py`: geometry/QC checks, common-mask group test, max-t permutation inference, ROI summary, and figures.
- `results/group_results.json`: primary numerical results and analysis settings.
- `results/participant_qc.tsv`: participant-level map and vmPFC summaries.
- `results/voxel_results.csv.gz`: voxelwise t, uncorrected p, max-t FWE p, and ROI membership.
- `results/group_mean_effect.nii.gz`, `group_t_positive.nii.gz`, `group_p_uncorrected.nii.gz`, `group_p_fwe_maxT.nii.gz`: NIfTI results in the source MNI grid.
- `figures/`: report figures.

The files under `input/` are fixed task inputs. The task-specific skill installation is under `.codex/skills/`.
