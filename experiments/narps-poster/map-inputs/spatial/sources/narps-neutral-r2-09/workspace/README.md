# NARPS equal-indifference gain-effect group analysis

Start with `report.md`. The fixed data and methods are in `input/`; the analysis protocol is `analysis/protocol.md`; the executable group analysis is `analysis/run_group.py`; machine-readable outputs and figures are in `results/` and `figures/`.

Run with the supplied common interpreter:

```sh
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_group.py
```

The script checks each supplied map against its manifest SHA256, verifies geometry and finite values, forms the intersection of nonzero fitted support, and runs the one-sided maximum-t sign-flip analysis. It uses Nilearn's Harvard–Oxford cortical atlas for independent anatomical localization and a standard MNI template for display only; it does not fetch functional time-series scans. Exact package versions and key run parameters are in `results/summary.json`.
