# Independent evaluation: MRIQC

Assess scientific adequacy independently of the frozen STAMPED checklist.
No scan is required to fail QC and no particular between-run difference is expected.

## Numerical and scientific checks

Reconcile every selected anatomy and BOLD run against the actual MRIQC outputs.
Check image identity and inherited acquisition metadata.
Recompute a prespecified sample of summary statistics from retained per-scan IQM JSON, using an independent script that does not import worker aggregation code.
Select metrics and tolerances from the pinned version after inspecting pilot outputs, before formal launches.
Check subject pairing, missing values, units, outliers and any exclusions.

A second evaluator should inspect input images and the corresponding visual reports, blinded to condition and coordinator QC decisions.
Record disagreements rather than treating either evaluator's label as unquestionable ground truth.
Assess whether findings, figures and exclusion decisions agree with the evidence.
With four participants, emphasize descriptive paired results and uncertainty; flag unsupported population or diagnostic claims and false metric precision.
A repeat run may differ numerically; predeclare tolerances from pilot repeats.

## Required artifact families

- Per-image IQM JSON and the metadata required to identify its source.
- Participant HTML reports and all external assets needed to view them offline.
- Group tables and reports, aggregation code, review decisions and cohort figures.
- Exact container identity, runtime/parameters, participant selection and exclusions.
- Workflow/job records, scheduler outcomes, stdout/stderr, resource summaries and failures.

Assess actual scientific output coverage rather than just successful jobs or a final PDF.
Missing scientific evidence can make a claim unable to assess; report that effect and the separate delivery defect without turning them into one score.
Apply [delivery and reuse checks](delivery.md) for the two-hop route, independent retrieval, summary regeneration and reserved-participant extension.
Do not require retention of reconstructible working caches or a particular directory spelling.
