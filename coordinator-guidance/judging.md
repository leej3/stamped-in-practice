# Independent evaluation: task-fMRI contrasts

Judge scientific correctness separately from evidence of rigor, reproducibility, reuse and cost.
A null or qualified conclusion can be scientifically adequate.

## Independent checks

1. Verify selected image identities, NIfTI geometry, TR and actual volume counts; confirm event units, scan-relative onset convention and modeled durations.
   Inspect all condition labels, error/missing-response handling and dropped volumes.
   A scan-count or onset shift must also be reflected in the design matrix.
2. Independently reconstruct a sample of event regressors under the declared HRF, filtering and nuisance conventions, without importing worker modeling code.
   Check the contrast sign and condition-column mapping, design rank, collinearity and available degrees of freedom.
   Use a known-sign synthetic design as a separate edge-case check, not as evidence that real data are correctly processed.
3. Independently recompute selected voxel contrasts and standard errors from the retained design and declared temporal-noise model.
   Ordinary least squares is not a numerical oracle for prewhitened FILM results.
   Freeze method-appropriate tolerances after the pilot; retain any inability to validate a method.
4. Inspect motion, brain coverage, registration and residual diagnostics, plus the images behind representative figures.
   Check image grids/affines before spatial aggregation; nearest-neighbor atlas/mask interpolation differs from continuous-image resampling.
   Explain exclusions without outcome selection.
5. Verify run combination respects within-participant dependence and any available variance estimates.
   Check cohort summaries do not treat runs as independent subjects.
   Assess uncertainty, exploratory choices and multiple-comparison control against the claims actually made.
   No expected activation is ground truth.

## Required artifact families

- Per-run effect/contrast and variance or standard-error maps, relevant statistic maps, brain masks, geometry and preprocessing outputs needed to inspect/reuse modeling.
- Design matrices, contrast definitions, event transformations, motion/nuisance regressors, model specifications and model-fit/QC diagnostics.
- Within-participant combined effects and uncertainty, cohort summaries, figures, decisions/exclusions and the scientific report.
- Exact input/container identities, code, runtime parameters and re-execution route.
- Slurm scripts, job identities/accounting, stdout/stderr, requested duct resource records and retained failures/crash diagnostics.

After observing actual pilot output structure, freeze coverage at the artifact-family level and define acceptable alternatives for scientific methods.
Do not demand every FSL scratch file or reward one favored directory layout.
A final map alone cannot establish design correctness, uncertainty or successful delivery.

Apply [delivery and reuse checks](delivery.md).
Regenerate the cohort summary from published participant outputs, then extend with the reserved participant; existing subjects should not need recomputation merely because paths changed.
Report costs, intervention and failures separately from the frozen STAMPED verdicts.
