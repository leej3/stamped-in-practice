# Reproduce the group analysis

From the workspace root, use Python 3.13 and install the direct dependencies from the workspace's `requirements.txt` (`python -m pip install -r requirements.txt`). The exact runtime and package versions used for the reported run are in `results/group_results.json`.

```sh
python analysis/run_group.py --pilot
python analysis/run_group.py --permutations 5000 --seed 20261016
python analysis/validate_results.py
```

The pilot writes `results/pilot.json`. The confirmatory command recreates the group outputs and figures. Inputs are read-only; all derived files are written under `results/` and `figures/`. See `analysis/protocol.md` for the estimand, support mask, inference assumptions, ROI localization and stopping checks.
