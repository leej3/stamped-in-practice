# Scan quality in the NYU Slow Flanker data

Which scans in the selected ds000102 cohort warrant further review before a functional task analysis, and how consistent is image quality between runs?

Analyze T1w and both task-BOLD runs for the selected participants in `sources.json`.
Use MRIQC 24.0.2 from the pinned ReproNim container catalogue on the supplied HPC resources, with MechaBABS for participant jobs and MRIQC group aggregation.
Use the same software identity throughout.
Inspect the upstream metadata and acknowledge the dataset authors and access terms.

Choose defensible quality summaries and inspect the relevant images and reports.
Distinguish algorithmic quality indicators, visual judgments and decisions to exclude a scan.
Investigate within-participant run differences without treating runs as independent participants.
Do not infer a neurological diagnosis or treat an arbitrary metric threshold as clinical ground truth.

Deliver a concise scientific report with informative figures, scan-level findings, uncertainty and limitations, and the code and results supporting the conclusions.
The completed analysis will be handed to another researcher through the declared local-host and hub route for inspection and extension without cluster scratch access.
Describe what is needed to understand and repeat it.
Do not repeat task-contrast modeling: this study concerns acquisition quality, not evidence for a task effect.
