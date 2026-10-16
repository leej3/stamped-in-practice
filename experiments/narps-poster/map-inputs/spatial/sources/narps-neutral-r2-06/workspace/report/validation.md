# Checks and validation

- Matched the 54 unique `participants.tsv` IDs to the 54 expected map paths; asserted equal-indifference group membership and rejected missing or duplicate IDs.
- At load time, checked all 54 image shapes and affines against the first map, required finite values, and verified each SHA256 against `input/sources.json`. All passed.
- All participant maps had 100% finite voxels and a mean nonzero support fraction of 24.8% (range 24.1–25.7%). The common nonzero support contained 198,029 voxels; no participants were excluded.
- Independently reconstructed the vmPFC group mean, standard error, t statistic, one-sided p value and 95% t interval from `participant_roi_means.csv` using NumPy and SciPy. The largest absolute difference from the saved values was 8.2e-8; the whole-brain corrected voxel count and analyzed voxel count also matched the saved map and summary.
- Inspected the generated figures at display size. The ROI is outlined and labeled; participant points, zero reference and interval are visible; the corrected map threshold agrees with the Bonferroni t cutoff in `wholebrain_summary.csv`.
- The result was rerun from the documented command after final code changes. `code/validate_results.py` independently recalculates the ROI statistics from participant means and reconciles whole-brain voxel counts; its values are retained in `results/validation_roi_recalculation.json`. Map hashes, participant count and numerical summaries are retained in `results/`.

## Attempt log

Two pre-analysis implementation errors were encountered and corrected: a keyword-argument syntax error in the plot setup stopped the pilot before any output; then an array-shape mismatch in reporting the strongest voxel stopped the first full run after intermediate maps had been written. The code was corrected, the pilot passed, and the final full run regenerated all outputs from the fixed inputs. Neither failed attempt contributed an inferential result.
