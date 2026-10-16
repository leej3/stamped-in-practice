# NARPS potential-gain group analysis

This study tests whether the AO86 participant-level gain-effect cope estimates show a positive group response in the equal-indifference cohort, with whole-brain family-wise error control. Preprocessing and participant models are fixed supplied inputs; no time-series scans were downloaded or reprocessed.

## Inputs and provenance

- `input/data/`: 54 participant maps, retrieved-byte SHA256 values and NeuroVault identifiers listed in [`sources.json`](input/sources.json).
- [`participants.tsv`](input/participants.tsv): pinned cohort metadata.
- [`upstream-methods.md`](input/upstream-methods.md): fixed upstream model and measurement limits.
- [`analysis/protocol.md`](analysis/protocol.md): estimand, group model, mask, ROI and checks frozen before group inference.

The code checks exact map/cohort ID agreement, participant uniqueness, group membership, map dimensions, finite values, and the supplied map sizes and SHA256 digests.

## Run

Use the supplied prepared Python 3.13.16 environment at `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python` (NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2, Nilearn 0.14.1). The environment manifest is at `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/pixi.toml`.

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py
```

This runs the primary 100% common-coverage analysis. The broader 90% coverage sensitivity run is reproducible with:

```bash
NARPS_COVERAGE_MIN=0.9 /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py
```

Primary results go to `results/` and `figures/`; the sensitivity goes to `results/sensitivity_90pct/` and `figures/sensitivity_90pct/`. Key result files are `summary.json`, `voxel_statistics.tsv.gz` (with voxel indices and MNI coordinates), `max_t_null.tsv`, NIfTI group maps, participant ROI estimates, and rendered figures. See [`report/report.md`](report/report.md) for interpretation.
