# Assessment target-integrity failures

Two assigned judgments in the first two batches finished their native sessions but failed the frozen launcher check that the assessment copy remain unchanged: `narps-neutral-r1-13-j01` (primary) and `narps-neutral-r1-22-j02` (preselected duplicate).
Both added `.git/annex/keysdb/db-shm` and `db-wal` and changed the existing 53,248-byte `keysdb/db` file.
The retained path comparison found no missing paths or changes to other declared paths.
These are changes to annex database metadata during assessment, including changed existing bytes, rather than only added sidecars.

The original worker captures remain unchanged.
The copied assessment targets were preserved as found, with complete manifests and before/copy/after equality checks.
The [incident index](incidents.json) binds the original result receipts and exact deltas; the full targets and raw judgment attempts are retained with their experiments.

The unchanged admission rule requires `target_unchanged: true`.
Consequently, the affected assigned judgments supply no formal checklist or scientific-adequacy measures, even though their raw reports remain available.
This is assessment-tool attrition, not evidence that the worker's science failed.
No repair, replacement, relabeling of primary and duplicate roles, or selection of a more favorable judgment is made.
The round synthesis will report available denominators and assessment attrition separately by assigned condition and cause.
