# NARPS potential gain group analysis

This workspace contains a group-stage analysis of the 54 supplied AO86 gain-effect maps for the equal-indifference group. The frozen protocol is in `analysis/protocol.md`; the report and figures are under `report/` and `figures/`; numerical maps and tables are in `results/`.

## Reproduce

Use Python 3.13.16 and install the pinned packages in `requirements.txt` in a project-local environment. From this directory run:

```sh
python -m pip install -r requirements.txt
python analysis/run_analysis.py
```

The prepared shared interpreter used for this run was Python 3.13.16 with NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, and NiBabel 5.4.2. Its absolute path is host-specific; the requirements file and command above are the portable recipe. `input/sources.json` records source and image checksums; the script checks all supplied image checksums before analyzing.
