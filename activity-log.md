# Assessment command record — 2026-10-16

Assessment runtime: `$STAMPED_ASSESSMENT_PYTHON` at `$STAMPED_ASSESSMENT_RUNNER`, as supplied by the coordinator. The runner's check, response help, probe, response-helper, fresh-rerun, and validation calls were preserved in the individual `*.stdout`, `*.stderr`, JSON, table and URL artifacts in this directory. Key commands:

```sh
git -C "$STAMPED_JUDGE_TARGET" rev-parse HEAD
"$STAMPED_ASSESSMENT_PYTHON" "$STAMPED_ASSESSMENT_RUNNER" check
"$STAMPED_ASSESSMENT_PYTHON" "$STAMPED_ASSESSMENT_RUNNER" response --help
"$STAMPED_ASSESSMENT_PYTHON" "$STAMPED_ASSESSMENT_RUNNER" probes "$STAMPED_JUDGE_TARGET" --kind study --check-remote -o "$STAMPED_JUDGE_OUTPUT/2026-10-16-probes.json" --response "$STAMPED_JUDGE_OUTPUT/2026-10-16-response.json"
"$STAMPED_ASSESSMENT_PYTHON" "$STAMPED_ASSESSMENT_RUNNER" fresh-rerun --path "$STAMPED_JUDGE_TARGET" --entry "$(cat "$STAMPED_JUDGE_OUTPUT/2026-10-16-replay-entry.txt")" --workdir "$STAMPED_JUDGE_OUTPUT/replay-workspace" --output "$STAMPED_JUDGE_OUTPUT/2026-10-16-fresh-rerun.json" --max-get-gb 5 --timeout 7200 --rtol 1e-6
"$STAMPED_ASSESSMENT_PYTHON" "$STAMPED_ASSESSMENT_RUNNER" validate "$STAMPED_JUDGE_OUTPUT/2026-10-16-response.json"
```

The first NeuroVault verification attempt completed 54 map downloads but exited on a manifest metadata entry without a URL; its files are retained as `neurovault-retrieval.stdout`, `.stderr`, and `.exit`. A second map-only verification completed 54/54 successfully; see `neurovault-retrieval-verified.stdout`.
