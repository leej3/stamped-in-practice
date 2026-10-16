# NARPS equal-indifference gain group analysis

This research object tests whether the gain-modulator effect estimate is positive in vmPFC in the 54 equal-indifference participants. Read [`scientific-report.md`](scientific-report.md) for the result and interpretation; [`research-protocol.md`](research-protocol.md) records the model and method revision.

## Run

From the workspace root, run:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/analyze.py
```

The analysis uses the supplied Python 3.13.16 environment (NumPy, SciPy, pandas, NiBabel, Matplotlib, Nilearn). It does not fetch data at run time. The two local MNI152NLin2009cAsym res-02 template files used for the analysis mask and figure are in `external/`; their retrieval URLs and SHA256 hashes are recorded in the summary JSON. The 54 fixed participant maps and cohort table, retrieval links, and hashes are recorded in `input/sources.json`. `external/nilearn-cache/icbm152_2009/` contains a symmetric 2009a template inspected during mask selection and not used in the final asymmetric 2009c analysis.

## Outputs

`results/primary_v2_template_mask/` contains the summary/provenance JSON, per-input QC table, unthresholded mean/t/FWE-p images, positive FWE-significant t image, top positive voxels and the FWE-significant voxel table. Values outside the analysis mask are NaN in NIfTI output. `figures/primary_v2_template_mask/` contains the whole-brain corrected map and participant-level vmPFC box plot. Run again with the command above to regenerate them.

`results/pilot_shared_support/` and `figures/pilot_shared_support/` preserve the initial shared-support pilot. It was superseded after figure review showed support outside the anatomical brain; the final primary analysis applies the matching asymmetric MNI template brain mask. The pilot is retained to make the method change inspectable.
