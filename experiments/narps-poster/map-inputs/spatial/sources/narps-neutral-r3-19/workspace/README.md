# NARPS gain-effect group analysis

This workspace contains a reproducible group analysis of the 54 supplied equal-indifference participant gain-effect maps. See [`report.md`](report.md) for the scientific question, methods, results, figures, and limitations; see [`analysis-protocol.md`](analysis-protocol.md) for the analysis plan recorded before inference.

## Inputs and run

Inputs are retained under `input/`. The executable is `run_analysis.py`; dependencies and exact package versions are specified in `environment.yml`.

```sh
conda env create -f environment.yml
conda run -n narps-gain-group python run_analysis.py
```

The default run uses 9,999 sign-flip permutations, seed `20261016`, and writes maps, QC, summary values, and permutation maxima to `results/`, with editable-figure source in `run_analysis.py` and rendered figures in `figures/`. The reduced 64-permutation pilot is retained separately in `results/pilot/` and `figures/pilot/`; it is not used for the reported inference.

## Main outputs

- `results/summary.json`: analysis settings, headline results, QC, and runtime identity.
- `results/input_qc.tsv`: per-map byte/checksum/grid/value checks.
- `results/mean_effect.nii.gz`, `t_stat.nii.gz`, `p_uncorrected.nii.gz`, `p_fwe.nii.gz`, `analysis_mask.nii.gz`: voxelwise outputs.
- `results/null_max_t.npy` and `max_t_null.tsv.gz`: sign-flip max-statistic null.
- `results/vmPFC_participant_effects.tsv`: participant-level regional summaries.
- `results/provenance.json` and `replay_comparison.json`: source/environment hashes and same-host exact replay evidence.
- `figures/group_t_map.png`, `figures/vmPFC_participant_effects.png`: report figures.
