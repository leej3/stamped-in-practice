# Result inventory

`group-analysis/` is the accepted final analysis, generated from commit `05878b7` with the checksum-verified local atlas, seed 20261015, and 9,999 sign flips. `audit.json` is a separate SciPy-based numerical check.

`pilot-*` and `prepin-final/` are retained development runs. They are not accepted results. The earlier atlas-based summaries used Nilearn label-list positions as NIfTI volume indices; the label list includes a background entry, shifting those positions by one. The final script instead selects volumes using the included atlas XML indices and verifies the atlas checksums. The earlier outputs remain unchanged to preserve the analysis history.

`pilot-atlas/` contains partial outputs from a run that failed during figure cleanup. All failed-run diagnostics are retained in `../logs/`; see `../logs/attempts.md` for the interventions and run identities.
