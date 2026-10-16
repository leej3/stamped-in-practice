# Environment and replay

The task used the supplied common Pixi environment without modifying shared software or installing task-specific packages. Interpreter: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python`, Python 3.13.16 on macOS 27.0.1 arm64.

Analysis packages: NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2 and Nilearn 0.14.1. The common manifest is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/pixi.toml`; it is a shared resource and uses version ranges rather than a task-specific lock. Actual runtime versions and input map checksums are recorded in `results/run_metadata.json`.

From the workspace root, replay with:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/analyze.py
```

The script regenerates maps, tables and figures under `results/` and `figures/`. No time-series inputs are required.
