# Execution history

All substantive runs were launched through Pixi and captured by duct in this directory. Each `*_info.json` records the exact command, run status, environment/host metadata, output paths and resource summary; paired `_stdout`, `_stderr`, and `_usage.jsonl` files retain command output and sampled resource use.

| Run | Outcome and intervention |
| --- | --- |
| `pilot_2026.10.15T23.21.09-81743_` | Failed after 999 sign flips: Nilearn returned the atlas as an in-memory image, but the first implementation tried to load it as a filename. Fixed atlas handling and retained the failure. |
| `pilot-retry_2026.10.15T23.22.04-82793_` | Failed after inference: the initial frontal-medial label had no overlap with the ventral ROI. Replaced it with orbital/subcallosal anatomy. |
| `pilot-atlas_2026.10.15T23.23.46-85156_` | Inference and outputs completed, then failed at unavailable module-level `plotting.close()`. Changed to close the returned display. Partial outputs retained separately. |
| `pilot-final_2026.10.15T23.24.06-85415_`, `pilot-review_2026.10.15T23.24.33-85689_`, `final_2026.10.15T23.24.49-85832_` | Workflow/figure pilots and an initial full run succeeded. Subsequent independent atlas review found an index offset: Nilearn's display-label list prepends `Background`, so those runs selected the wrong atlas volumes. They are retained as superseded derivatives and must not be interpreted as final estimates. The final workflow now reads the volume indices from the pinned XML. |
| `final-pinned_2026.10.15T23.27.11-92611_` | Checksum guard correctly stopped before computation because the script used repository-root-relative paths instead of the input-manifest-relative paths. Fixed the path lookup. |
| `final-pinned-retry_2026.10.15T23.27.21-92830_` | Accepted final 9,999-permutation inference; checksum validation passed for all maps, the participant table, atlas, and display template. |
| `audit_2026.10.15T23.29.20-97173_` | Independent SciPy and max-null numerical checks passed. |

The first duct invocation used an extra `run` subcommand (`pixi run duct run ...`) and was rejected by duct before starting a child process; it produced no duct record. This invocation error did not launch analysis and was corrected immediately.
