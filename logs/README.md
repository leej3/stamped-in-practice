# Run log index

- `group-2026.10.15T23.10.51-30308_*`: initial successful computation. Retained as an audit trail. Its summary field `whole_brain_support` was too broad (any significant voxel anywhere), and its t map emitted a harmless divide warning outside the analysis mask. The final code uses an explicit vmPFC support criterion and finite zero fill outside the mask.
- `group-final-2026.10.15T23.15.56-57379_*`: corrected target-region criterion and first corrected whole-brain figure.
- `group-validated-*`: completed run after removing the unused dependency and refining figures; superseded by the final run after masking the descriptive mean map to common support and adjusting the legend.
- `group-final-validated-*`: final run after all analysis and visualization changes. These outputs validate the checked-in analysis and results.

Each prefix contains duct metadata, captured stdout/stderr, and sampled resource usage. The stdout includes duct's final run summary with exit code, wall time, CPU, and peak/average memory.
