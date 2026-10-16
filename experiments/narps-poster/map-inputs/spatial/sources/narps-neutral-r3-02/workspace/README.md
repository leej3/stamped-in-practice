# NARPS gain-effect group analysis

Reproducible group-stage analysis of the 54 supplied AO86 equal-indifference participant gain-effect maps. The upstream preprocessing and participant models are fixed and described in `input/upstream-methods.md`.

## Run

Requires Pixi. From this directory, run `pixi install` followed by `pixi run analyze`. The pinned recipe and resolved package builds are in `pixi.toml` and `pixi.lock`. The analysis reads `input/` and regenerates `results/` and `figures/`.

## Contents

- `report.md`: concise results, interpretation, and limitations.
- `analysis/protocol.md`: estimand, model, correction, QC and limits.
- `analysis/run_analysis.py`: complete executable group workflow.
- `results/summary.json`: parameters, numerical findings, runtime identity and retrieved-input SHA256 checksums.
- `results/participant_qc.tsv`: per-map QC; `results/fwe_clusters.tsv`: corrected cluster inventory.
- `results/mean_effect.nii.gz`, `group_t.nii.gz`, `fwe_p.nii.gz`, `common_mask.nii.gz`: spatial results and analysis mask.
- `results/vmPFC_proxy_participant_values.tsv`: values behind the descriptive participant plot.
- `figures/`: rendered figures; their editable source is the Python analysis script.
