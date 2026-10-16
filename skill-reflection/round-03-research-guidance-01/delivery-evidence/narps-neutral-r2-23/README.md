# NARPS equal-indifference gain analysis

## Reproduce

Run from this workspace with the supplied prepared interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py
```

The script reads the fixed participant effect maps and metadata under `input/`, verifies all 54 image checksums against `input/sources.json`, and regenerates the tables, NIfTI group maps and figures in `results/`. It does not access time-series scans or rerun upstream processing. The computation uses a fixed random seed (20261016), 9,999 random participant sign patterns plus the observed arrangement, and one thread under the supplied common environment defaults.

The execution interpreter was Python 3.13.16 with NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2 and Nilearn 0.14.1; these versions and hashes for the inputs and atlas are retained in `results/provenance.json`. The provided shared environment recipe is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/pixi.toml`. `environment.yml` records the package versions used if creating a task-local environment is preferred.

## Contents

- `protocol.md`: estimand, group model, ROI, correction and QC decisions.
- `report.md`: concise result and interpretation.
- `analysis/run_analysis.py`: executable analysis and figure generation.
- `results/summary.json`, `results/cluster_summary.tsv`, `results/participant_qc.tsv`, `results/roi_participant_effects.tsv`: numeric results and checks.
- `results/*.nii.gz`: group mean, t statistic, FWE p values, coverage and masks.
- `results/figures/`: rendered figures from the analysis script.
- `results/provenance.json`: software versions, checksums and method identity.
- `results/attempts/`: retained early failed runs and the final successful run log.

See `input/upstream-methods.md` for the fixed participant-level model and effect-estimate meaning.
