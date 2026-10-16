# Retained round reporting inputs

This reporting layer preserves completed research and judgments while allowing the reporter to recognize the authorized research-skill pins for rounds two and three.
It performs no research, replay, regrading, or replacement judgments.
The original failed reporting outputs remain in each package.

`bindings/round-bindings.json` contains the exact source and skill commits and hashes of retained authorization records.
Its digest is `afde668d22b417d2796ace3cf13a44b432f15628c7dad85bf92afa663ff666ee`.
The corrected reporter still checks the original allocation, scientific inputs, fixed research source, native capture integrity, assessor identity, and output bindings.
Selecting an authorization file does not itself prove those checks.

Recreate the bindings from immutable iteration history:

```sh
python scripts/prepare_retained_round_bindings.py \
  --iteration-repository /path/to/iterations/narps-neutral-v1 \
  --iteration-commit 5541abee8fafbad5b049a7538029c0955f2428c0 \
  --output /new/bindings --round 2 --round 3
```

Package an existing closed extraction without modifying its evidence:

```sh
python scripts/package_retained_reporting.py \
  --snapshot /path/to/closed/snapshot \
  --reporting-registration /path/to/original-registration.json \
  --assessment-pin /path/to/sealed-source/assessment-version.json \
  --output /new/portable-inputs --archive /new/portable-inputs.tar.gz
```

Both output paths must be new.
The tool requires all 32 assigned judges closed and no pending slots.
It copies the complete original snapshot and validates its source mappings, then checks that source bytes stayed unchanged during packaging.
The archive contains regular files and stable gzip/tar metadata; its printed SHA-256 authenticates the complete archive.

The round-two snapshot omitted two uniquely linked files from judgment `narps-neutral-r2-12-j02` because their Markdown targets began with a space.
Recover these exact retained bytes with the additional options:

```sh
  --recover-whitespace-links narps-neutral-r2-12-j02 \
  --capture-index /path/to/final-findings-01/retention-closure/local-capture-index.json
```

The correction is additive.
It retains the original index and output binding, quotes the exact native links and line numbers, verifies the native final against the closed capture, and copies selected outputs only from hash-checked capture members.
It changes no checklist answers or scientific judgment categories.
Ambiguous links, escaping paths, missing capture members, and hash mismatches fail.
This recovery does not repair malformed replay links or any scientific or checklist failure.

For future intake, import `normalize_output_link` and `selected_link` from `scripts/package_retained_reporting.py`.
The helper handles surrounding spaces, angle delimiters and URL-encoded filenames, rejects escaping paths and URLs, and requires one unique selected file.
Preserve its exact-link receipt and validate the selected bytes against native capture before admitting outputs.
The active frozen extraction scripts are unchanged.

If original retained payloads have since become unavailable, an explicit `--prior-package /path/to/verified/package` can supply previously copied bytes.
The complete prior package is hash-checked first, each replacement must still match the original capture hash, and the new manifest records every fallback and retains the prior package manifest.
No retrieval or source repair occurs.

Use `--supplement /path/to/final-replay-audit-01` when a later final audit supplements the closed extraction, as for round one.
All original support records, native replay observations, and native events remain in the package.
Helper completion, entrypoint execution, and verified selected outputs are distinct events; retain their status and primary/duplicate judgment IDs when reporting them.
Do not count all helper completions as successful reproduction.

Unpack and verify in any location before aggregation:

```sh
python scripts/package_retained_reporting.py \
  --unpack /path/to/portable-inputs.tar.gz \
  --archive-sha256 REPLACE_WITH_RECORDED_DIGEST \
  --output /new/relocated-inputs
python scripts/package_retained_reporting.py --verify /new/relocated-inputs
```

Supply the relocated `index.json` and `source-manifest.json` to the reporter.
Original absolute paths in raw receipts are identifiers resolved through that hash-checked manifest, not dependencies on the original host filesystem.
The reporter additionally needs a coordinator Git repository containing the exact declared source commits for its unchanged-file checks, and the pinned assessor runtime.
Neither scientific image payloads nor execution environments are copied into these small reporting packages.

Run the extraction regression checks with:

```sh
python scripts/test_package_retained_reporting.py
```

Rebuild reporting into a new canonical analysis directory:

```sh
python scripts/reaggregate_retained_reporting.py \
  --archive experiments/retained-round-reporting/round-02/input.tar.gz \
  --archive-sha256 REPLACE_WITH_RECORDED_DIGEST \
  --scratch /new/scratch/round-02 \
  --output experiments/retained-round-reporting/round-02/analysis \
  --source-repository /path/to/coordinator-repository \
  --assessor /path/to/pinned/assessment \
  --round-bindings experiments/retained-round-reporting/bindings/round-bindings.json \
  --round-bindings-sha256 afde668d22b417d2796ace3cf13a44b432f15628c7dad85bf92afa663ff666ee
```

For round one, omit the two round-binding options.
For round three, use its closed input archive and separate output/scratch paths.
The runner validates the archive and original index, uses only packaged registration and evidence, and retains the command, streams and return status in `analysis-execution/`.
An exit status of 2 from the reporter can represent retained admission failures; it is preserved, together with the reporting output, for review.

## Retained data and pooled results

The [pooled condition table](pooled/README.md) gives each original research run one observation.
It selects the operational round-one assessment and corrected round-two and round-three assessments, with six assigned runs per condition in each round.
Duplicate judgments remain in the round reports and never replace unavailable primaries.
All three rounds have completed their assigned judgments and the same retained-input reporting checks.
Run `pixi run poster-outcomes` to regenerate the pooled table, every run's measurements, round-specific summaries, source hashes and revision identities.

| Round | Portable inputs | Corrected report | Preserved issues |
| --- | --- | --- | --- |
| 1 | [Archive identity](round-01/input.json), [archive](round-01/input.tar.gz) | [Judgments](round-01/analysis/judgments.tsv) | [Two invalid primary checklist responses](round-01/analysis/issues.tsv) |
| 2 | [Archive identity](round-02/input.json), [archive](round-02/input.tar.gz) | [Judgments](round-02/analysis/judgments.tsv) | [Two protected-copy failures for run 05](round-02/analysis/issues.tsv) |
| 3 | [Archive identity](round-03/input.json), [archive](round-03/input.tar.gz) | [Judgments](round-03/analysis/judgments.tsv) | [One protected-copy failure for run 20](round-03/analysis/issues.tsv) |

Each archive includes the untouched original report under `analysis/`, all original rejection records, native judgment output and its extraction evidence.
The separately published `round-NN/analysis/` is the corrected report; its `analysis-execution/` sibling retains the exact reporting command and outcome.
All three reporting commands exit 2 because the individual failures remain present.
This is distinct from a reporting execution error: all produced complete tables with empty standard error, and all 3,430 packaged input files still matched their hashes after reporting.

Round one retains 24 primary scientific judgments and 22 valid primary checklists.
Rounds two and three each retain 23 primary scientific judgments and 23 valid primary checklists.
The excluded round-two run-05 judgments and round-three run-20 primary are not converted into negative scientific results or zero checklist scores.
The round-two whitespace-link correction recovers an existing duplicate checklist and report; round three recovers the existing run-19 primary checklist and report.
Neither changes an answer, grade or original file.

The replay summary uses [round one's final native audit](round-01/final-replay-audit-01/result.json) [round two's native observations](round-02/replay-native-observations.json), and [round three's original observations](round-03/replay-native-observations.json) plus its [independently verified run-19 native completion](round-03/native-replay-corrections/result.json).
Original and additive records remain separate.
All retained replay events and support files are in the input archives.
A native entrypoint execution, a partial selected-output match and a complete selected-output match are separate observations.
The checklist mean gives equal weight to each run's fraction `met / (met + partial + unmet)`; not-checked and not-applicable items remain explicit, and evaluated-item coverage is recorded alongside the mean.

Retrieve annexed archives and tables with the root Pixi environment, following [the retrieval guide](../../RETRIEVAL.md).
The small pooled JSON and TSV reports are ordinary Git content.
The exact validated root `pixi.lock` is preserved on [`codex/env-stamped-retained-reporting-20261016`](https://github.com/leej3/stamped-in-practice/tree/codex/env-stamped-retained-reporting-20261016); restore that lock before `pixi install --locked` for environment replay.
A fresh clone needs the named research-source branches `codex/neutral-protocol-launcher`, `codex/narps-round2-research-source-candidate` and `codex/narps-round3-research-source`, plus the pinned `assessment/` submodule, for the reporter’s source checks.

## One-time round-three refresh

Run this from an isolated reporting checkout only after the existing round-three extraction has a closed snapshot (32 closed launchers, zero pending slots).
This is the user-authorized reporting refresh: no new research, judges, replay, regrading, or modification of the original files.
Set `REPORTING_SNAPSHOT` to the exact completed snapshot directory if its final name differs below.
The independently approved round-binding digest is supplied literally; do not replace it with a digest calculated from an edited binding file.

```sh
set -e
REPORTING_STATE=/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1
REPORTING_SNAPSHOT="$REPORTING_STATE/round-03-operational-extraction-01/snapshot-final-02"
REPORTING_DEST=experiments/retained-round-reporting/round-03
REPORTING_SCRATCH=$(mktemp -d)

test -f "$REPORTING_SNAPSHOT/snapshot.json"
test -f "$REPORTING_SNAPSHOT/processing-result.json"
test ! -e "$REPORTING_DEST"
mkdir "$REPORTING_DEST"

pixi run python scripts/package_retained_reporting.py \
  --snapshot "$REPORTING_SNAPSHOT" \
  --recover-whitespace-links narps-neutral-r3-19-j01 \
  --recover-whitespace-support narps-neutral-r3-19-j01:replay \
  --recover-whitespace-support narps-neutral-r3-19-j01:access \
  --capture-index "$REPORTING_STATE/round-03-operational-extraction-01/final-findings-01/retention-closure/local-capture-index.json" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/snapshot-final-01" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/pre-source-binding-correction" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/reporting-source-binding-correction.json" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/processing-failures-01.json" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/reporting-bindings-final-01.json" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/commands/snapshot-final-01-build" \
  --supplement "$REPORTING_STATE/round-03-operational-extraction-01/summarize-final-findings.py" \
  --reporting-registration "$REPORTING_STATE/round-03-assessment-registration-01/original-registration.json" \
  --assessment-pin "$REPORTING_STATE/round-03-operational-extraction-01/sealed-source/assessment-version.json" \
  --output "$REPORTING_SCRATCH/packaged" \
  --archive "$REPORTING_DEST/input.tar.gz" \
  > "$REPORTING_DEST/input-manifest.json"

REPORTING_ARCHIVE_SHA=$(pixi run python -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["archive"]["sha256"])' \
  "$REPORTING_DEST/input-manifest.json")

if pixi run python scripts/reaggregate_retained_reporting.py \
  --archive "$REPORTING_DEST/input.tar.gz" \
  --archive-sha256 "$REPORTING_ARCHIVE_SHA" \
  --scratch "$REPORTING_SCRATCH/reconstructed" \
  --output "$REPORTING_DEST/analysis" \
  --source-repository "$PWD" \
  --assessor "$PWD/assessment" \
  --round-bindings experiments/retained-round-reporting/bindings/round-bindings.json \
  --round-bindings-sha256 afde668d22b417d2796ace3cf13a44b432f15628c7dad85bf92afa663ff666ee
then
  REPORTING_EXIT=0
else
  REPORTING_EXIT=$?
fi
test "$REPORTING_EXIT" -eq 0 || test "$REPORTING_EXIT" -eq 2
```

The new destination prevents accidental replacement of a prior refresh.
Retain the scratch directories, execution receipts, original failures and reporter exclusions for review.
The round-three command now selects the independently observed exact whitespace-link recovery for `narps-neutral-r3-19-j01`.
Its replay and access files are retained as supporting evidence, separate from admitted checklist/scientific outcomes.
Original native replay observations remain unchanged; adding a replay outcome requires a separate same-event native audit.
The failed first extraction and its source-registry hash correction are retained as supplements.
Add the completed round to the poster pool only after reviewing the existing admission results and the native evidence for selected-output reproduction.

The [publication audit](publication.json) verifies all 113 annex payloads needed by these reporting records and scientific figures by full anonymous download and SHA-256 comparison (120,782,071 bytes total).
