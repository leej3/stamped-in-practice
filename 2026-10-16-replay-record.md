# Authorized replay record

- Source: target path supplied by the coordinator, checked out at `e2d266ea0ca7cc52e9ecab358e0f5a8c9085f6b9`.
- Runner: coordinator-supplied `assessment.py fresh-rerun`.
- Entry: `pixi run python analysis/run_group_analysis.py` (documented analysis subcommand; worker run info records the same direct Pixi command).
- Workspace: `replay-workdir/clone` (retained); host scope: same host.
- Content: runner fetched 57 annex objects through the local source's configured route, then removed six presumed outputs, including the required `input/participants.tsv` table.
- Result: exit code 1 before analysis; `FileNotFoundError` for `input/participants.tsv`. This attempt does not determine whether the entry point succeeds when the required input is present. No second attempt was made.
- Full runner record: `2026-10-16-fresh-rerun.json`. Captured runner stdout/stderr: `records/fresh-rerun.stdout`, `records/fresh-rerun.stderr`.
- The clone, its generated local environment lock, and any generated artifacts are preserved for coordinator review.
