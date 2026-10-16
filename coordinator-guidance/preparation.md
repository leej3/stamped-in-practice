# Preparation gates

Complete these before setting readiness to true.
Retain evidence and failed attempts.

1. Retrieve the exact dataset and container commits in `input/sources.json`.
   Retrieve selected image and container annex keys; compare the retrieved keys and hashes.
   Metadata inspected during design does not prove image or container access.
   Preserve upstream attribution and license text, and record container terms separately.
2. Inspect NIfTI geometry, TR, volume count, coverage and finite values; check event times against scan duration and inherited JSON metadata.
   Run a pinned community BIDS validator on the selected package.
   The OpenNeuro page reports a validation error: identify the actual finding, document any necessary derivative repair, preserve originals and apply identical preparation to every condition.
3. Start with sub-01, both runs, on one compute node.
   Use MechaBABS for MRIQC; use an identical Slurm-array route across all conditions for the FSL workflow.
   Check installed-version help and site configuration; no invented launch commands.
   Use the coordinator's programmatic resource-readiness checks and host providers.
   Keep scheduler account, host paths and credentials outside tracked source.
4. Retain one complete successful job through cluster output collection, local relay, hub publication and fresh authorized retrieval without cluster scratch access.
   Include a failed-job case or a controlled collection fixture outside formal runs.
   MechaBABS retains native records; capture requested duct streams, resource data and summaries for other substantive scientific commands.
5. Measure productive elapsed compute (excluding queue, initial downloads and image setup), CPU-hours, peak RAM, disk and bytes transferred.
   Initial scope is four subjects and two runs each, at most four concurrent jobs; resource allocations are provisional.
   Target roughly 20–40 minutes elapsed compute per arm.
   Resize subjects/concurrency from pilot measurements before freeze, preserving both runs per selected subject.
   Never add sleep or pointless computation.
   Record setup and transfers separately; report total end-to-end cost too.
6. Prepare the actual worker data package under `input/`, annexing large payloads with published retrieval locations.
   The launcher exports files/annex links, not nested submodules.
   Keep source revisions and all needed inherited metadata.
   Do not copy coordinator answers, pilot outputs or scientific reference values.
7. Reserve the next ascending participant for the later extension test, outside the initial worker package.
   Freeze its source identity and the extension question.
   Freeze selected subjects/runs, container bytes, common task/resources, scientific tolerances, expected artifact families and assessor before formal launches.
   Apply the coordinator's current conditions and repetitions; this proposal does not replace that design with a new two-arm-only experiment.
8. Publish the frozen study revision, update the coordinator gitlink, and seal the formal procedure.
   Keep preparation pilots distinct from research workers.

No live HPC run, annex publication or credential request is part of this design PR.
