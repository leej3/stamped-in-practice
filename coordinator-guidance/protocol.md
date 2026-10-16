# Task-fMRI study protocol

## Question and scope

Estimate correct-incongruent minus correct-congruent task responses in ds000102.
Start with the first four ascending participants and both runs each.
These data have short event-related flanker acquisitions (upstream TR 2 s); the inspected event table uses seconds and condition-specific correct/incorrect labels.
The metadata are evidence, not proof of NIfTI header consistency or usable images.
Inspect every selected run before freeze, including error trials and missingness.

Use FSL 6.0.7.23 in the pinned ReproNim-distributed Neurodesk image, with simple Slurm participant/array jobs and a declared run-combination/summary stage.
Workers choose defensible methods within this software stack.
Preprocessing from raw images is included in the proposed scope; no existing preprocessed derivative has been verified.
This deliberately exposes preprocessing, model and QC artifacts that a final contrast map alone would omit.
No full fMRIPrep/FreeSurfer run is needed.

Require per-run contrasts and within-person combination before cohort summaries.
The four-person cohort is descriptive and not powered for population discovery.
No particular anatomical activation or positive significance finding is required.
Do not use a behavioral effect as proof of a neural effect or average unaligned native-space maps.
Workers may choose defensible alignment or report the limits of spatial comparison.
Judge inferential claims conditional on the actual method.

## Budget decision before freeze

Pilot one participant end to end: preprocessing, both first-level models, QC, within-person combination and output return.
Then test a bounded array.
Target 20–40 minutes elapsed productive computation; begin with at most four jobs.
If full preprocessing exceeds this envelope, reduce cohort/concurrency demands where scientifically sensible, or prepare one common derivative package with its own complete provenance.
The latter changes the study scope and requires updating both the worker prompt and judging guidance before freeze.
Never silently supply preprocessed inputs to a task described as raw-data analysis.
Preserve the pilot and scope decision; do not claim runtime qualification until measured.

## Comparison controls

Use identical dataset bytes, common preparation, scheduler route, FSL image, resources and task in all coordinator conditions.
Keep reference outputs and judging code outside `input/`.
Use current coordinator repetitions and ordering; do not launch just two workers as a substitute.
Freeze pipeline-independent scientific checks and method-conditional tolerances before formal runs.
The companion MRIQC study shares this source cohort but its answers are not worker inputs.
Any shared QC exclusions must be fixed and supplied equally before launch.
Otherwise workers make independent, documented QC decisions.

## Sources inspected during design

- [Upstream dataset and acquisition description](https://openneuro.org/datasets/ds000102/versions/00001).
- [ReproNim container catalogue](https://github.com/ReproNim/containers); exact commit and image annex key are in `input/sources.json`.
- [MRIQC execution documentation](https://mriqc.readthedocs.io/en/24.0.2/usage.html).
- [FSL FEAT user guide](https://fsl.fmrib.ox.ac.uk/fsl/docs/task_fmri/feat/user_guide.html).

Source metadata and catalogue pointer inspection occurred on 2026-10-16.
Neither image payload availability nor scientific outputs were checked.
