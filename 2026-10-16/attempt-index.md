# Assessment attempt index

All assessment products, command logs, errors, remote retrieval clones and generated artifacts are retained beside this file. The source checkout was not changed. `identity-verification.log` records the final target commit check and worker-receipt hash.

## Runner and probes

- `runner-check.log`, `runner-response-help.log`: requested runtime check and response help.
- `runner-probes-help.log`, `runner-rerun-help.log`, `runner-validate-help.log`, `response-*-help.log`: runner/helper usage inspected.
- `runner-probes.log`: first probe invocation failed because `--path` was supplied to a positional-path action.
- `runner-probes-attempt-2.log` and `2026-10-16-probes.json`: successful full probe run against the absolute target path.

## Formal replay

- `runner-fresh-rerun.log` and `2026-10-16-fresh-rerun.json`: one authorized runner replay, `--path "$STAMPED_JUDGE_TARGET"`, documented entry `pixi run group-analysis`, retained `replay-workspace/`.
- `replay-summary-science-fields.diff`, `.status`, and `replay-runtime-difference.json`: non-runtime summary comparison; all scientific fields agree, while runtime differs.

## Remote retrieval and environment checks

- `object-remote-ls-remote-attempt-1.log`: failed hostname lookup from a mistyped remote host.
- `object-published-clone.log` and `object-published-annex-get.log`: shallow single-branch clone reached the commit but annex retrieval failed; `object-published-annex-get-attempt-2.log` and `object-published-annex-fsck-attempt-2.log` retain the subsequent no-location result.
- `object-datalad-clone.log`: default-branch clone did not select the task branch; the expected input path was absent.
- `object-datalad-target-branch-clone.log`, `object-datalad-target-branch-get.log`, `object-datalad-results-get.log`, and `object-datalad-annex-fsck.log`: successful exact-branch retrieval, map/result payload retrieval and integrity checks. The full clone remains in `object-datalad-target-branch/`.
- `environment-remote-ls-remote.log`, `environment-remote-clone.log`, `environment-snapshot-head.txt`, `environment-pixi-lock-sha256.txt`, `environment-pixi-toml.txt`, and `environment-history*.log`: companion lock branch retrieval, hash check and history review. The clone remains in `environment-snapshot-clone/`.

## Response helpers

Every response helper was invoked as `assessment.py response <helper> ...` in the frozen runtime. `checklist-items.log`, `template-response.json`, `response-set*.log`, `response-stamp.log`, `response-table.md`, `response-encode-final.stderr`, `response-decode-final.log` and `response-validate-final.log` preserve the work. The final response is `2026-10-16-response.json`; the encoded app URL is `2026-10-16-url.txt`. `runner-validate.log` is the final runner shortcut validation.
- `checklist-pin-check.log`: the frozen vendor check confirmed checklist 0.3.1 and all 31 items.
- `identity-verification.log`, `final-target-head.txt`, `final-target-status.log`, and `worker-end-state.json`: final source identity, clean status and retained attribution receipt.
- `2026-10-16-assessment.md`: final report, with the helper-rendered table inserted after response completion.
