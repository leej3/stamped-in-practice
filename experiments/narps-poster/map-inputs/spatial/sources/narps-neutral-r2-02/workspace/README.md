# NARPS potential-gain group analysis

Start with [`REPORT.md`](REPORT.md) for results and interpretation. The preregistered-for-this-run analysis decisions (recorded before group inference) are in [`protocol/analysis-plan.md`](protocol/analysis-plan.md). Inputs and pinned provenance are in `input/`; computation is in `code/group_analysis.py`; machine-readable results and rendered figures are in `results/` and `figures/`.

Replay from the project root using the prepared environment:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/group_analysis.py
```

The 54 NIfTI maps are supplied as Git-annex content under `input/data/`. To retrieve payloads in another clone, use `git annex get input/data/` before running. The script validates each retrieved payload against `input/sources.json` and writes only derived outputs under `results/` and `figures/`.
