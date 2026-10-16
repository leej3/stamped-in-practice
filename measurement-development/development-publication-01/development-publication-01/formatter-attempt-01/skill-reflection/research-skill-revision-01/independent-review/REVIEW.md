# Independent engineering review: alignment trial 01

The completed local handoff is supported by the delivered bytes.
The original scientific artifacts are preserved, both completed-run records agree with their retained outputs, and the before/after assessment products are internally consistent.
No blocking defect was found in the narrow claims reviewed.
This is an engineering evaluation, not a formal NARPS grade or a new STAMPED assessment.

## Findings, in priority order

1. **Execution-environment identity is incompletely recorded (evidence gap).** Both `project/runs/*/run.json` files record `['python', 'code/analyze.py']` and identical Python/platform/package versions.
   The wrapper actually invokes `sys.executable`, but neither receipt retains that value, `sys.prefix`, the outer wrapper invocation, nor a direct identifier tying the installation log to a particular run.
   The retained `verification-venv/pyvenv.cfg`, installed distributions and successful installation log corroborate creation of a fresh environment.
   They do not independently bind that environment to the historical verification process.
   The evidence supports two completed run records and matching output files; the more specific claim that one used each environment also relies on the author's replay account.
   Preserve actual executable/prefix and wrapper argv in future receipts.
   This is a recording limitation, not evidence that either run failed or that the author is wrong.

2. **The trial snapshot has real, nonblocking instruction friction (skill wording).** Its alignment skill routes “Scientific recomputation” to a research loop while requiring validation of the repaired entry point.
   The template claims that a dirty-tree run “cannot be rerun” and calls committed state “the whole state,” although the assessment accepts retained complete dirty snapshots.
   The author reasonably used the explicitly authorized, unchanged-method checks and a separate receipt wrapper.
   The templates were optional, and no incompatible tool migration was necessary.

3. **Some validation claims retain summaries rather than replayable test transcripts (minor evidence limitation).** `validation.json` gives the four rejection cases, exit codes and stderr but omits their full invocation and fixture-mutation commands.
   The code visibly checks all four conditions before creating its output directory, so the summaries are consistent with the implementation.
   This review did not re-execute those cases or the scientific computation.
   Similarly, the supplied artifacts do not independently audit every historical read made by the trial agent; its limited-context statement is an author account supported by the invocation restrictions.

## Checks completed

- All **44** current delivered files match `after-manifest.json`, with no extra non-Git files.
  The before archive, before directory and initial eight-file ready-state manifest agree; the after archive agrees with the after manifest.
  All five initially tracked files match the initial commit.
- Input CSV, `code/analyze.py`, summary CSV, supplied PNG and `REPORT.md` preserve their original SHA-256 values.
  Only `.gitignore` and `README.md` changed among the eight supplied files.
  The method was not rewritten.
- Git remains at `2c0f98e0ee14847ef515a0fa301306b2192aa64c`; current status matches the recorded dirty delivery.
  Uncommitted files are present and were included in the review.
  No clean-tree or new-lock-format requirement was imposed.
- Both receipts have analysis and verification exit code zero.
  Their source snapshots, output hashes and replay-report copies match the actual files.
  Both generated CSVs are byte-identical to the supplied summary.
  The wrapper executes the unchanged analysis in a temporary workspace with copied input, retains generated outputs/logs, and compares numeric CSV values exactly.
- Both regenerated PNGs match each other but differ from the supplied PNG in bytes and **23,086 of 288,000 pixels**.
  All images are 600 by 480.
  Visual inspection supports the reported same trajectories and labels.
  The cause is unestablished; this review makes no pixel-level reproduction claim.
- Both responses pass the supplied validator: **31 answers, checklist 0.3.1**.
  Regenerated tables and URL files match the saved products exactly.
  Every cited local evidence path exists.
  The ten recorded status changes match the response diff.
  The after MUST counts are 11 met, 4 partial, 1 not-checked and 1 not-applicable; partial was not counted as met.
- All **34** skill/runtime source files match the initial skill snapshot and its later inventory.
  The checklist pin check passes.
  The initial prompt and invocation hashes verify; their messages differ only in trailing newline.

## Limits and friction classification

The handoff accurately separates new verification provenance from the unknown original runtime.
It discloses same-host execution, the shared Python base, version pins without wheel/OS identity, uncommitted additions, no environment binary archive, no regular test history, no automatic fresh environment per execution, unverified recipient retrieval and no chosen public licence. These are stated target/environment limits, not concealed failures.

The missing plain-Python stack example is a coverage opportunity, not a missing required dependency: the skill says to use a stack reference only when it matches.
Narrow Git-based probe coverage is confirmed by the retained probes and their flagged overrides; the surrounding instructions explicitly require complete-delivery judgment.
Two full 31-item records are observable procedural overhead; whether that cost is disproportionate is a design judgment.
The unavailable exact model/runtime identity is an allowed fallback under the trial's read boundary, not an invented provenance value.
No required bundled file was found missing.
This review's initial default-host-Python validator attempt lacked `jsonschema`; the authorized supplied environment validated successfully.
That was reviewer setup friction, not a trial failure.

## Prospective wording changes: separate, not trial-tested

At the parent's request, the three later files under `/Users/johnlee/.local/share/wt-utils/worktrees/b9d9/skills/skills/` were compared with the untouched trial snapshot.
The diff and current file hashes are retained separately in this review directory.

The new sentence allowing unchanged-method verification while preserving supplied results resolves the identified boundary ambiguity.
The template comments now describe one commit-based workflow, permit other workflows to identify dirty snapshots, and label the plain-Git fallback as incomplete execution logging.
Those clarifications address the universal wording without claiming a logic repair: automatic `git add -A`/commit and omission of an unchanged-output record remain limitations of that fallback. These edits were reviewed as text/code diffs only; this completed trial provides no behavioral test of the revised wording.

## Evidence and review boundary

Primary after-manifest SHA-256: `d7748c97e5b4f8776e33b726188b405c1f96386763ef934685860fccb7a8dfb5`.
Before-manifest SHA-256: `f6da8efe69d56225b23692af3e50c9e5950bb5c4133a1992a69e30e8cc6b9847`.
Frozen skill inventory SHA-256: `89086c3609a9d142c7be1f5faaf6d640378292c515c3f2901bca62dd3e449353`.

[checks.json](checks.json) contains independent check results; [source-hashes.json](source-hashes.json) binds all reviewed project files, frozen skill files, top-level evidence and invocation inputs.
[commands.json](commands.json) retains validation/Git commands and their output, including the failed default-Python attempts. [review_checks.py](review_checks.py) is the reproducible read-only check program. [COMMANDS.md](COMMANDS.md) records the review command entry points and reading scope. No project/snapshot/evidence file was edited, no scientific analysis was rerun, and no commit, remote write, cluster job or additional agent was used.

Reviewer environment identity is retained in [reviewer-identity.json](reviewer-identity.json); unavailable session-path fields were not guessed.
