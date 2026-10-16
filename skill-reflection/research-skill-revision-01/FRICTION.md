# Independent alignment-skill trial

The supplied skill was usable without the author's context and produced a useful
local handoff. The main cost was adapting its recording guidance to a small plain
Python project and completing two full checklist records around a small change.
No originating checkout, other study, trial record or coordinator plan was read.
No additional agent, commit, remote publication or Workshop collection was used.

## Exact assessed state

- Target: the sibling `project/` directory.
- Git revision before and after:
  `2c0f98e0ee14847ef515a0fa301306b2192aa64c`.
- Before: all eight supplied files, including untracked `REPORT.md` and ignored
  CSV/PNG. [Manifest](before-manifest.json) SHA-256:
  `f6da8efe69d56225b23692af3e50c9e5950bb5c4133a1992a69e30e8cc6b9847`.
- After: all 44 delivered files, including uncommitted workflow/docs/lock changes,
  both new run receipts, source snapshots and generated verification outputs.
  [Manifest](after-manifest.json) SHA-256:
  `d7748c97e5b4f8776e33b726188b405c1f96386763ef934685860fccb7a8dfb5`.
- Complete file archives: [before](before-delivery.tar.gz) and
  [after](after-delivery.tar.gz). They omit Git administration, not delivered files.
- Frozen skill/runtime-assets inventory:
  [skill-snapshot-manifest.json](skill-snapshot-manifest.json), SHA-256
  `89086c3609a9d142c7be1f5faaf6d640378292c515c3f2901bca62dd3e449353`.
  The same supplied assessor and checklist 0.3.1 were used for both assessments.

## Skill wording and bundled-resource friction

1. **No matching Python stack reference.** Alignment says to “use a supplied stack
   reference … when it matches the project's tools.” The snapshot supplies only
   `references/stacks/datalad.md`. This is not a blocker under “when it matches,”
   but there is no small Python/Git example showing the desired run receipt or
   environment capture. I designed a standard-library wrapper and a pip-compatible
   runtime lock within the existing Python workflow.

2. **The generic templates retain a stronger, tool-specific assumption.** The
   supplied `run-recorded.sh` says, “Commit before execute: a run that starts from
   a dirty tree cannot be rerun.” `preflight.sh` says, “the committed state is the
   whole state.” These conflict with the conventions' property-based treatment of
   complete uncommitted deliveries when read as general requirements. A retained
   content snapshot can identify an uncommitted execution, as this trial does.
   The fallback also runs `git add -A` and an automatic `git commit`, and records
   nothing when outputs do not change. I did not install these templates: their
   DataLad/commit lifecycle did not fit this scoped local handoff. The alignment
   instruction to use guards only for a demonstrated gap allowed that choice.

3. **Verification versus research-loop boundary needs interpretation.** Alignment
   says, “Scientific recomputation or a changed method belongs in
   do-full-research-loop,” then requires, “Validate the actual repaired entry
   point.” Executing the same statistical script for a check is recomputation in
   ordinary language. I treated the explicitly authorized proportionate checks as
   the assessor's optional isolated replay, preserved the method and original
   artifacts, and did not invoke a new research loop. A phrase explicitly allowing
   unchanged-method verification here would remove that ambiguity.

4. **Probe coverage is narrower than this delivery.** The before and after
   `derived-have-records` probes both returned `not-applicable` because no output
   was tracked, even though supplied outputs and later receipts existed. The
   environment probe similarly missed the new untracked exact lock. The skill
   explicitly warns that “Covered is not answered” and tells the assessor to
   inspect ignored/uncommitted artifacts; following that instruction prevented
   false conclusions. The cost is many manual overrides, all retained with flags.
   The remote-based distributability probe also needed a `mapping-questioned`
   flag for this expressly local handoff.

5. **Full record production is substantial for a tiny study.** The original
   analysis is 23 lines. The required two assessments entail 62 per-item judgments,
   eight main assessment products, capture identities, flagged-item explanations
   and the replay report. The supplied `set`, `stamp`, `table`, `validate` and
   `encode` commands worked and avoided hand-maintaining the schema or URL.
   This is procedural overhead, not a missing tool or an inability to finish.

6. **Identity can remain explicitly unavailable.** The assessor allows an
   unavailable identity rather than guessing. Exact active model and runtime
   versions were not exposed within this trial's permitted read boundary, so the
   records state that limitation. No commit was made and no provenance was copied
   from the baseline commit. This fallback kept the scoped trial moving.

The useful instructions were the complete-delivery boundary, preservation of the
actual Git revision, separation of scientific adequacy from tracking, explicit
probe overrides, and the rule against silently scoring unverified retrieval.
No required bundled runtime file was missing. No skill instructions were edited.

## Environment and tool limitations

- The provided scientific environment lacked `pip`. A fresh standard-library
  venv supplied pip through ensurepip; installing all thirteen lock entries and
  `pip check` succeeded. See [installation log](environment-install.log) and
  [dependency check](pip-check.log). This was a resolved environment detail.
- Both the fresh pip environment and the provided scientific environment matched
  the supplied summary CSV byte-for-byte. Their PNGs differed in bytes and pixels;
  visual inspection showed the same twelve trajectories and labels. The cause of
  rendering variation was not established and is not attributed to the skill.
  [Figure comparison](figure-comparison.json) retains the observation.
- Snapper was available. It formatted the changed README and handoff note and its
  check exited successfully, with advisory wrapping diagnostics. No pre-commit
  hook ran because no commit was made. An explicit empty configuration avoided
  loading unrelated parent-directory configuration.
- There was no authentication, remote-access or package-install blocker.

## Target issues and remaining tradeoffs

The supplied study had clear synthetic-data limits, a complete input and a
root-relative executable analysis. It lacked version pins and historical
execution receipts; Git excluded the delivered outputs and omitted the report.
Those are target properties, not assessment failures.

The work adds an exact package/interpreter specification, a preserved-baseline
reproduction command with hashes and source snapshots, and concrete local handoff
and dependency-update instructions. Original input, analysis, summary, figure
and report bytes are unchanged. The real entry point succeeded twice, and four
rejection cases passed: existing destination, altered input, interpreter mismatch
and package mismatch. See [validation.json](validation.json).

The new lock and handoff files remain uncommitted. The assessment therefore moves
`must/013` from met to partial rather than pretending the lock is versioned.
Original runtime provenance cannot be recovered. The object still has no regular
testing history, bundled environment binaries, automatic fresh Python environment
per execution, independently verified recipient retrieval or selected public
licence. These are explicit limits, not claims of full STAMPED compliance.

## Assessment products

- [Before report](2026-10-16-assessment.md) and
  [canonical response](2026-10-16-response.json).
- [After report](2026-10-16-2-assessment.md) and
  [canonical response](2026-10-16-2-response.json).
- [Ten item-level status changes](item-differences.md), with machine-readable
  evidence in [item-differences.json](item-differences.json).
- [Replay record](2026-10-16-2-fresh-rerun.json).

Both complete responses passed the supplied validator: 31 answers against the
unchanged checklist 0.3.1. No overall score is computed. The after MUST result is
11 met, 4 partial, 0 unmet, 1 not-checked and 1 not-applicable, out of 17.
