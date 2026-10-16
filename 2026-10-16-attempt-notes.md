# Assessment attempt notes

- `2026-10-16-replay-map-check.stdout.txt` records an unsuccessful checksum-check attempt caused by omitting the `data/` portion of manifest paths. The corrected second attempt is recorded in `2026-10-16-replay-map-check-2.*` and verified 54/54 maps.
- One response-set batching attempt quoted the literal `$STAMPED_JUDGE_OUTPUT` path in shell redirections. Each redirection failed with “No such file or directory” before the runner or response helper was invoked. The successful per-item `response set` calls, with distinct stdout/stderr/exit files, are retained as `2026-10-16-set-*.{stdout,stderr,exit-code}.txt`.
- An initial worker inventory comparison stopped on a string-to-octal formatting error. The corrected inventory check and its result are recorded in `2026-10-16-worker-inventory-check.*`.
- The prescribed fresh replay was attempted exactly once. Its full command output, stderr, exit code, JSON receipt, clone and shipped-output snapshots are retained under `2026-10-16-fresh-rerun.*` and `2026-10-16-replay-work/`; no retry was made.
