# Flanker conflict and task-evoked BOLD response

What evidence do the selected NYU Slow Flanker data provide for an increased BOLD response on correct incongruent trials relative to correct congruent trials?

Start from the selected raw T1w images, two task-BOLD runs per participant and corresponding events in ds000102, identified in `sources.json`.
Use FSL 6.0.7.23 from the pinned ReproNim container catalogue and the supplied Slurm resources.
Choose defensible preprocessing, first-level modeling, QC and visualizations.
Account for incorrect or missing responses, timing conventions, motion, temporal noise, image geometry and differences between runs.
Do not substitute reaction time analysis for the requested imaging analysis.

Estimate the correct-incongruent minus correct-congruent contrast per run, combine runs within each participant, and summarize effect direction and uncertainty across the selected participants.
Runs are repeated observations, not independent people.
Spatially localize results only where alignment supports it.
Any whole-brain significance claim requires appropriate multiple-comparison control; a descriptive result or lack of support is acceptable for this small cohort.

Deliver a concise scientific report with informative figures and the code and results supporting your conclusions, including exclusions and limits of inference.
A later researcher should be able to inspect and extend the completed analysis through the declared local-host and hub route without cluster scratch access.
Use the source metadata and acknowledge the upstream authors and access terms.
Do not obtain another worker's results or coordinator reference answers.
