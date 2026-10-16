# Delivery and reuse checks

Predeclare an artifact-family inventory after the pilot, before formal runs.
The initial output families are in `judging.md`; expand version-specific report assets and sidecars from actual pilot observations.
Do not use one reference implementation's filenames as the only acceptable layout.

Check the worker's original stop state separately from coordinator preservation.
If the coordinator must rescue cluster outputs, retain them but do not credit the worker with having delivered them.
Record the rescuing actor, time and changes.

For each selected subject/run, reconcile scheduled, completed, failed, excluded and missing work. An intentionally excluded scan still needs its QC and reason. Capture run identity, input identity, exact commands and environment, outputs and checksums, native workflow records, stdout/stderr and scheduler accounting.
Collect crash reports and failed attempts; distinguish reusable scientific outputs from reconstructible scratch caches.
Full scratch retention is not required.

Verify both transport hops: cluster to local host, then local to annex hub.
For required large outputs, compare annex keys/hashes and coverage at each hop; a successful Git push, annex location claim or final report is insufficient.
Publish child commits and payloads before parent pointers.
Declare the intended recipient and authorized route; anonymous public access is not required.

From a fresh clone of the published result commit, with empty local payload storage and no cluster scratch mounts, retrieve every required artifact family.
Check linked report assets, JSON/TSV records, images, code and environment identity.
Record missing files, byte counts, checksums and retrieval failures explicitly.
Use the frozen assessor's replay allowance; do not silently grant retries.
A same-host clone establishes retrieval, not cross-host portability.

Separately test reuse: regenerate the cohort summary without rerunning subjects, then add the reserved participant using the declared workflow.
Attribute all new compute and human intervention; report whether existing outputs are reusable.
These are downstream evaluation actions, not fixes credited to the original worker.
Keep numerical correctness, rigor, reuse/convenience and measured cost separate; do not combine them into an invented overall score or presume STAMPED is beneficial.
