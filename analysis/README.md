# Group analysis

`group_analysis.py` implements the group-stage analysis only. It loads the exact 54 supplied cope maps, verifies their identities against the cohort table and checksums in `input/sources.json`, checks common grids and finite values, constructs the common nonzero coverage mask, estimates the one-sample t map, and runs the positive whole-brain max-t sign-flip correction.

The inferential choices were recorded in `protocol.md`. Outputs are written to `results/` and `figures/`; maps are regenerated from the supplied data and code. An initial diagnostic attempt is preserved under `results/attempt-01-pre-maskfix/` because its p-map background encoded uncovered voxels as zero; use only the regenerated top-level outputs. The corrected p maps encode outside-mask voxels as NaN.
