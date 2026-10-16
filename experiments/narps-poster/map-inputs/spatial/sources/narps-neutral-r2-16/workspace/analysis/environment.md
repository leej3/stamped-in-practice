# Execution environment and display reference

## Analysis software

The common workspace interpreter was used directly; no package installation or shared environment change was made.

- Interpreter: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python` (Python 3.13.16)
- Environment recipe: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/pixi.toml`
- Exact package versions used: recorded in `results/primary_summary.json`
- Entry points: `analysis/run_analysis.py`, `analysis/make_figures.py`, `analysis/validate_results.py`

## Anatomical display template

The final corrected-map figure uses TemplateFlow's matching `MNI152NLin2009cAsym` 2 mm T1 reference image. It is an anatomical visualization reference only and was not used in analysis or inference.

- URL: <https://templateflow.s3.amazonaws.com/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz>
- Local copy: `results/reference_data/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz`
- SHA256: `7c4e551ae8150ac1f468595bd62074aa15aed747cd334fce6d177182972b6220`

An AAL3v2 atlas download was attempted for an atlas-defined medial orbitofrontal proxy but the Nilearn/OSF source returned HTTP 500. The report consequently uses a transparent coordinate proxy, not an atlas label, for descriptive estimates. No atlas-derived inference was performed.
