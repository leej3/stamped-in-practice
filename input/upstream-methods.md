# Fixed upstream analysis

Each map is one participant's unthresholded gain-effect estimate from NARPS team AO86, averaged across four runs.
The 54 participants comprise the complete equal-indifference group in OpenNeuro ds001734 version 1.0.4.
These are effect estimates, not standardized test statistics or group results.
Maps are reported in MNI152NLin2009cAsym space.

AO86 used fMRIPrep outputs and nistats participant models.
Their reported gain regressor was mean-centered and variance-normalized before HRF convolution; its coefficients must not be interpreted as change per currency unit.
Response trials used response-time durations, with separate response-choice and gain modulators.
Nonresponse trials, motion terms, flagged volumes and drift terms were also modeled; runs were combined within participant.
Gain and loss used separate models, so the supplied gain effect is conditional on that modeling choice.

The reported upstream choices are fixed for this task.
Participant variance maps and a complete executable upstream pipeline are not supplied; account for these limits when choosing and interpreting group inference.
`participants.tsv` retains the source group, age and gender columns.
`sources.json` identifies each original image, its retrieved-byte checksum, the pinned cohort table and the original methods report.
