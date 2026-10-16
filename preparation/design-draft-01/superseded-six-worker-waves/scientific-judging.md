# Scientific assessment context

Assess the original NARPS Hypothesis 1: a positive parametric effect of potential gain in vmPFC for the equal-indifference group.
The original [analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) require whole-brain-corrected inference.
The scientific task is in `input/study-task.md`.

Workers receive 54 participant gain-effect maps from team AO86 and the corresponding cohort metadata.
Preprocessing and participant modeling are fixed; evaluate group inference conditional on those inputs.
Judge whether the analysis handles the intended participants, image geometry, quality, gain scaling, uncertainty and anatomical interpretation appropriately.
The maps represent independent participants; runs have already been combined within each person.
Evaluate exclusions, uncertainty and multiple-comparison correction against the actual method.
Defensible approaches can reach different conclusions; matching a prior team's answer is not the criterion.
Keep scientific validity separate from the frozen STAMPED assessment.
Check how image coverage and missing observations enter the analysis; whether spatial alignment, vmPFC definition, group-model assumptions and whole-brain correction support the claimed inference; and whether quality checks, uncertainty and figures make those decisions inspectable.
Do not require a particular mask, atlas, model or numerical result.
Participant variance maps are absent; judge methods against the supplied data.
