# NARPS equal-indifference gain-effect group analysis

Read [the scientific report](report.md) and [the fixed-input protocol](analysis/protocol.md) first. `input/` contains the supplied participant metadata, source manifest and participant maps. `reference/` contains the pinned atlas image used only for anatomical localization. `results/` contains the checked outputs.

## Reproduce

Requires Python 3.13.16 and packages pinned in `requirements.txt`. From the project root, create a local environment and install the recipe:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run the group analysis and its independent numerical check:

```sh
OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 .venv/bin/python analysis/run_analysis.py
.venv/bin/python analysis/validate_results.py
```

The prepared runtime used for the delivered results was Python 3.13.16 (conda-forge build, Clang 21.1.8) from the common environment. It used NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2 and Nilearn 0.14.1. Atlas provenance and checksum are in `reference/atlas_source.md`; participant-map checksums are verified against `input/sources.json` at every run. Nilearn supplies the standard MNI152 visualization background; it is only a figure backdrop, not used in inference.

## Key outputs

- `report.md`: concise result, interpretation and limits.
- `analysis/run_analysis.py`: executable group analysis and figure generation.
- `analysis/validate_results.py`: SciPy and permutation-p calculation checks.
- `results/summary.json`, `results/validation.json`: machine-readable analysis and validation summaries.
- `results/input_qc.tsv`, `results/participant_vmPFC_effects.tsv`, `results/whole_brain_clusters.tsv`: input QC and participant/cluster summaries.
- `results/group_mean.nii.gz`, `results/group_t.nii.gz`, `results/p_fwer_maxT.nii.gz`, `results/q_fdr_bh.nii.gz`, `results/vmPFC_atlas_mask.nii.gz`: statistical and anatomical maps.
- `results/vmPFC_participants.png`, `results/whole_brain_fwer_map.png`: rendered figures; their editable source is the analysis script.
