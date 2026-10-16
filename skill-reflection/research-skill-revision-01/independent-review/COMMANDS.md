# Review command record

The material checks were run from the repository's existing shell. All writes
were confined to this independent review directory. `review_checks.py` saves
its subprocess argv, exit codes, stdout and stderr in `commands.json`.

```sh
python3 -B /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/research-skill-revision-01/alignment-independent-review-01/review_checks.py
pixi run --manifest-path /Users/johnlee/code/CON/stamped-in-practice/pixi.toml --locked python -B /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/research-skill-revision-01/alignment-independent-review-01/review_checks.py
```

The first command used host Python 3.14. Its encoder commands failed before
validation because `jsonschema` was absent. Results are retained as
`checks-first-host-python-attempt.json`. The second command used the explicitly
supplied runtime and completed all checks. The only generated warning was a
Pillow deprecation notice for reading pixel arrays; pixel comparison completed.
The scientific `analyze.py` and `reproduce.py` were never executed by the reviewer.

Read-only discovery and inspection used `pwd`, `rg --files`, `ls -la`, `sed`,
targeted `rg -n`, and Python standard-library reads. The first recursive file
inventory included the retained virtual environment and was truncated; subsequent
inspection was limited to declared manifests and the top level of `evidence`.
The read sets are bound by `source-hashes.json`, including the initial manifests,
prompt and invocation, `FRICTION.md`, before/after reports and responses, code,
environment files, run receipts, logs and frozen skills. The current
`verification-venv` executable was queried for metadata only, with `-B`.

`view_image` inspected these two local images:

- `alignment-trial-01/project/figures/paired-assay.png`
- `alignment-trial-01/project/runs/verification-20261016/figures/paired-assay.png`

The parent subsequently authorized a separate read of prospective wording
changes. An initial Git diff with paths relative to the wrong candidate root
returned no diff; a direct read using that root raised `FileNotFoundError`.
`rg --files` found the correct nested `skills/` root. Python `difflib.unified_diff`
then compared exactly these paths against the frozen snapshot:

- `align-with-stamped-principles/SKILL.md`
- `create-stamped-project/templates/preflight.sh`
- `create-stamped-project/templates/run-recorded.sh`

That comparison wrote only `prospective-clarifications.diff` and
`prospective-clarification-hashes.json` here. It did not edit or re-evaluate the
trial snapshot. The prospective wording is explicitly excluded from the
trial-tested claims.
