# Result inventory

`group-analysis/` is the accepted final analysis, generated from the final committed protocol and code with checksum-verified local atlas, seed 20261015, 9,999 sign flips, and an all-participant nonzero-support intersection. `audit.json` is a separate SciPy-based numerical check.

`pre-common-support/`, `pilot-*`, and `prepin-final/` are retained development runs. They are not accepted results. `pre-common-support/` used the union rather than intersection of participant nonzero support. Some pilots also used Nilearn label-list positions as NIfTI volume indices, where the prepended background entry shifted positions by one. The final script uses all-participant common support and selects atlas volumes using the included XML indices, with checksums verified. Earlier outputs remain unchanged to preserve the analysis history.

`pilot-atlas/` contains partial outputs from a run that failed during figure cleanup. All failed-run diagnostics are retained in `../logs/`; see `../logs/attempts.md` for the interventions and run identities.
