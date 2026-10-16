# Pilot execution log

- Initial 20-permutation pilot stopped during output reconstruction: the common-support mask was a 3D array, while the NIfTI helper expected a 1D vector. No inferential outputs were generated. Corrected mask serialization to preserve its 3D shape directly; this did not change the model or inference.
- Re-ran the pilot after this correction; see the rerun output in `results/pilot/`.
- Full 9,999-permutation execution completed but QC revealed a formula error in permutation t statistics: the permuted signed sum used a group-SD denominator instead of the standard error of the mean. Those outputs were retained in `results/invalid-standard-deviation-denominator/` and are invalid for inference; they are not reported as study results. Corrected denominator and independent SciPy comparison are now being applied before rerun.
