# MRIQC study protocol

## Question and scope

Describe acquisition quality in the first four ascending participants of ds000102, with one T1w and two flanker BOLD runs each (12 image inputs).
Assess within-person run differences and identify scans warranting review; no required positive finding.
This small convenience subset supports descriptive conclusions, not population quality estimates.
Cohort size remains provisional until the timing pilot.

Use pinned MRIQC 24.0.2 via ReproNim/containers and the same MechaBABS installation, configuration, scheduler resources and container runtime across conditions.
Keep participant and group stages distinct.
Verify group aggregation requirements against the actual version: do not assume reports can be rebuilt from a final CSV alone.
Retain native MechaBABS job and collection records.

## Design controls

Start independent workers from identical committed inputs, resources and prompt.
Use the coordinator's existing condition design, launch ordering and frozen assessor.
This scientific prompt specifies the shared tools and handoff destination without teaching the baseline a STAMPED checklist or giving it coordinator QC answers.
Report spontaneous tool/skill discovery as observed.
All conditions may access the same official documentation and host services.

Container retrieval, input preparation and any common repair happen before freeze.
The image is a deliberate fixed-method component; workers retain scientific choices about summaries, review and conclusions.
Do not claim the task tests invention of QC algorithms.
Readiness remains false until every preparation gate is evidenced.

## Compute envelope

Pilot one participant, both runs and anatomy, then size the initial four-person array to roughly 30 minutes elapsed productive compute.
Record concurrency and CPU-hours; report queue, setup, transfers and agent time separately.
MechaBABS uses its native records; record other scientific execution with requested duct.
Measure instead of promising that this image/cohort has a known runtime.

## Sources inspected during design

- [Upstream dataset and acquisition description](https://openneuro.org/datasets/ds000102/versions/00001).
- [ReproNim container catalogue](https://github.com/ReproNim/containers); exact commit and image annex key are in `input/sources.json`.
- [MRIQC execution documentation](https://mriqc.readthedocs.io/en/24.0.2/usage.html).
- [FSL FEAT user guide](https://fsl.fmrib.ox.ac.uk/fsl/docs/task_fmri/feat/user_guide.html).

Source metadata and catalogue pointer inspection occurred on 2026-10-16.
Neither image payload availability nor scientific outputs were checked.
