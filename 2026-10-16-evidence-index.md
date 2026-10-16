# Assessment evidence index

All files here are under STAMPED_JUDGE_OUTPUT, outside the assessed checkout.

- `initial-commit-verification-command.txt`, `initial-commit-verification.stdout`, `runner-check.stdout`, `response-help.stdout`, `response-items.stdout`, `response-template.stdout`, `probes-help.stdout`, `fresh-rerun-help.stdout`: pinned runner verification and interfaces.
- `probes-command.txt`, `probes.stdout`, `probes.stderr`, `2026-10-16-probes.json`, `2026-10-16-response-draft.json`: frozen probes with remote checks and their unedited output.
- `retrieval-command.txt`, `retrieval.stdout`, `retrieval.stderr`, `retrieval/github/object/`: GitHub exact-commit clone succeeded; public GitHub annex retrieval failed for the 58 payloads.
- `verify_source_maps.py`, `source-map-retrieval-command.txt`, `source-map-retrieval.stdout`, `source-map-retrieval.stderr`, `source-map-retrieval.json`, `retrieval/neurovault/`: all 54 source inputs retrieved and SHA/size checked.
- `fresh-rerun-command.txt`, `fresh-rerun.stdout`, `fresh-rerun.stderr`, `2026-10-16-fresh-rerun.json`, `replay/workspace/`: the single authorized replay. It used a same-host fresh clone, fetched the shipped annex payloads, removed shipped outputs, and reproduced 13/14 outputs; `results/report.md` was not regenerated. The clone remains for preservation.
- `worker-stop-audit.json` is a retained first summary attempt that looked for annex-content fields in the Git index; that location was wrong. `worker-stop-audit-2.py`, `worker-stop-audit-2.stdout`, `worker-stop-audit-2.json` correct the check against the receipt worktree and confirm 58/58 annex payloads locally available at stop, exact path/index agreement, and clean worker status.
- `image-view-local-failure.txt`: the assessed checkout’s figure symlink was not materialized locally; the replay-generated figure was inspected and matched its shipped hash.
- `apply-response-sets.sh`, `response-set.stdout`, `response-set.stderr`, `response-stamp-command.txt`, `response-stamp.stdout`, `finalize-response-commands.sh`, `finalize-response.stdout`, `finalize-response.stderr`: all response edits, stamping, rendering, validation, encoding and decoding were run through the coordinator runner’s `response` action (and the requested `validate` shortcut).
- `2026-10-16-template.json`, `2026-10-16-table.md`, `2026-10-16-response.json`, `2026-10-16-url.txt`, `2026-10-16-roundtrip.json`: helper-generated template, table, canonical response, app URL and decoded app-format round trip.

Additional final checks:
- environment-history.stdout and environment-absent-files.stdout preserve dependency-history and README/lock absence checks.
- response-fix-apply.sh, response-fix.stdout and response-fix.stderr contain final helper edits and revalidation.
- report-route-patch-attempt1.txt preserves a failed path-expansion attempt; report-route-patch.stdout records the successful report edit.
- report-table-patch-attempts.txt preserves two failed tool-construction/command-policy attempts; report writing succeeded afterward.
- roundtrip-check.py and response-roundtrip-check.json confirm the decoded checklist-app answers match all 31 response values and reasons.
- roundtrip-check-attempt1.txt records a comparison that initially expected evidence/source metadata to survive the compact URL; roundtrip-check-2.py checks the fields the checklist app encodes. The corrected 31-item comparison passes.
The source-map summary is retained both as retrieval/source-map-retrieval.json beside downloaded files and source-map-retrieval.json at the output root for direct report/response citations.
