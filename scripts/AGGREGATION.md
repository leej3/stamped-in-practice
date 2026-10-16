# Aggregate a registered comparison

`aggregate_comparison.py` turns evidence-backed coordinator extractions into descriptive tables and figures.
It does not inspect research objects, launch judges, replay analyses or decide scientific verdicts.
Use the allocation and sealed procedure for the comparison being reported; every assigned worker and judgment remains visible when evidence is missing.

## Current procedure: neutral-v1

Use extraction `schema_version: 3` for the tool-neutral comparison.
Its original version 3 procedure is the research and assessment seal; obtain the digest from the independent registration, not from the extraction index.
The NARPS allocation assigns 72 workers and 96 judgments: three rounds, four conditions, six workers per cell and two preselected duplicate judgments per cell.
The first assigned judgment remains primary regardless of outcome or completion order.

With the selected iteration and assessor available, run in the coordinator environment:

```sh
pixi run python scripts/aggregate_comparison.py \
  --allocation iterations/narps-neutral-v1/allocation.json \
  --index /path/to/extraction-index.json \
  --assessment-procedure-sha256 <registered-procedure-sha256> \
  --output /path/to/comparison-report-01
```

`registration.json` and `procedure.json` default to siblings of the allocation; override with `--registration` and `--research-procedure` if needed.
`--assessor` selects an available assessor checkout and `--assessment-pin` selects its exact version record; defaults are root `assessment/` and `assessment-version.json`.
The checkout must contain the pinned commit, but its code is not executed: the tool reads the immutable checklist, lock and response schema with `git show`.
Existing outputs are never overwritten.
Exit 2 means malformed inputs or evidence errors; generated `issues` tables preserve artifact errors alongside valid independent observations.

An empty index, `{"schema_version": 3, "runs": []}`, honestly reports every assignment as pending.
As evidence arrives, add `comparison_provenance` with `research_procedure_sha256` and an `assessment_seal` artifact.
The original series uses the same research and assessment seal.
A separately registered version 4 assessment series uses its own assessment digest and embeds the exact original research procedure and allocation with the unchanged assessor pin.
Pass that assessment digest to the command above, retaining the original allocation and research procedure.
Keep each series' extraction index and outputs separate; never substitute or pool repeated measurements with the original series.
For a round-one report, distinguish its 24 workers and 32 assigned judgments from the full 72/96 allocation: later, unlaunched rounds remain pending, outside that series.
Every artifact reference is `{ "path": "relative/or/absolute/path", "sha256": "<exact bytes>" }`; relative paths resolve against the containing index or disposition.
Unknown fields, duplicate JSON keys, nonfinite numbers, unknown runs and repeated judgment IDs are errors.
The full machine-readable contracts are `INDEX_SCHEMA`, `DISPOSITION_SCHEMA` and their component schemas in [the script](aggregate_comparison.py).

For retained receipts containing old absolute paths, add `--source-manifest /path/to/source-manifest.json`.
This list maps each absolute `source_path` and `sha256` to a `copy` artifact with a relative path; the copies resolve beside the manifest.
Every supplied copy is hash-checked, and referenced bytes must still match the original receipt's digest.
With a map, an unmapped absolute artifact is an error even when the old path exists; ordinary relative references remain relative to their containing index or disposition.
Keep native receipts unchanged and retain the map alongside the copied evidence.
The report records the map and reporting-tool hashes separately from the frozen assessment identity.
When updating reporting code for a sealed series, retain its original outputs and verify agreement before using the new report; relocated table reproduction alone does not establish cross-host scientific replay.

## Bind the original delivery

Keep these identities distinct in each run record:

| Field | Meaning |
| --- | --- |
| `run_id` | Allocated worker identifier |
| `seed_commit` | Supplied Git seed |
| `worker_head`, `result_commit` | Actual stopped Git HEAD, or explicit `null` when unavailable |
| `delivery_capture` | Hashed original-delivery manifest, including dirty, untracked and ignored files |
| `worker_end_state` | Hashed original version 2 stop receipt |
| `worker_input` | Hashed external version 3 input-boundary receipt |
| `worker_native` | Hashed native `procedure_status` and `result` receipts |
| `retention_commit` | Optional later coordinator publication, never a worker identity |
| `skill_commit` | Optional exact research-skill revision |
| `worker_completion` | `pending`, `completed`, `failed`, `interrupted` or `unknown` |

A HEAD still equal to the seed does not identify the worker's uncommitted scientific files; the capture does.
The gate binds the run, condition, seed, input tree, common prompt, resources and coordinator source through the supplied receipts.
The native judge target and canonical response must match both the capture digest and nullable Git identity.
Original capture URIs remain provenance when retained files relocate.
The aggregator validates manifest metadata and receipt bindings; full payload integrity remains the frozen launcher's capture-validation responsibility.
Partial captures retain their omissions and do not automatically become scientific failure verdicts.
Coordinator preservation and process exit codes do not change a worker's raw judgment.

## Extract judgments without regrading

Put assigned judgments under `judgments.primary` and, when allocated, `judgments.duplicate`.
Each has its allocated `judgment_id`, hashed native receipts, canonical `response`, `report` and `output_binding`.
Omitted evidence remains missing; invalid responses contribute no checklist items.
The canonical response must contain every pinned item and pass the frozen response contract.
A duplicate never fills a missing primary.

The output binding records `schema_version: 1`, `kind: "coordinator-assessment-output-binding"`, the exact native result SHA256, native session IDs and an `outputs` mapping of hashed artifacts.
It binds response and report bytes to retained session-output evidence; native result receipts alone do not hash those outputs.
Retain the supporting capture or file manifest separately.
The gate checks consistency and known reuse, not native authorship or the truth of an extraction.

Keep `adequacy` separate from the scientific `conclusion`.
For an explicit category, provide `extraction_status: "explicit"`, the category and an `excerpt` containing an exact `quote` plus inclusive, one-based `start_line` and `end_line`.
Categories are `supported`, `qualified`, `not supported` and `unable to assess`.
Cite the judge's classification rather than a rubric listing possible answers.
Use `extraction_status: "missing"` or `"ambiguous"` with `category: null` when no unique category is available; missing classification is not `unable to assess`.
An explicit leading “Scientific adequacy:” label takes precedence over a separate statement that a positive scientific hypothesis is not supported.
If scientific assessment is in another file, provide its hashed `scientific_report` and include it in the output binding.
Version 4 instead requires the judge's `scientific-judgment.json` through a hashed `structured_scientific` artifact, binding the delivery capture, report hash, category and exact quoted lines.
An invalid scientific record leaves that measure unavailable without automatically discarding an otherwise valid checklist response; do not reconstruct a grade from prose.

## Measurements and limitations

`operations` records evidence-backed observations with unique `operation_id`, `stage`, `actor`, `status`, `scope` and hashed `evidence`.
Optional `duration_s` and named metrics retain their measurement scope; absent measurements stay missing.
Separate worker, discovery, installation, computation, judging, replay, retrieval, publication and coordinator effort.
Do not sum overlapping measurements or infer billing from token counts.
Use consistent scope strings for comparable observations.

Retrieval records identify the recipient, route, artifact class, required and verified coverage, and host scope.
Metadata visibility is not payload access; same-host cloning does not establish cross-host portability.
Replay records distinguish an observed attempt, helper completion, actual entrypoint execution and exit, and output comparisons.
A consumed allowance or successful helper exit does not prove reproduction.
Replay success is not required for inclusion.

For an evidenced measurement defect, use a separate `--disposition` analysis record; `--disposition-sha256` can verify its expected bytes.
It does not change the sealed procedure, authorize new launches or replace an unfavorable judgment.
Bind each affected assigned judgment to its procedure, native result and output-binding hashes.
Mark only the exact affected `replay` or `stamped-checklist:<item-id>` measure `unavailable` or `invalid`, with a factual reason and hashed evidence.
Keep raw verdicts and unaffected evidence.
Scientific dependency may be `independent` or `uncertain`; uncertainty affects duplicate comparison, not the retained label.
A disposition preserves the selected series' research and assessment digests; it does not authorize an assessment amendment.

Retain additional assessments in `supplementary_attempts` and explicitly excluded attempts in `excluded_attempts`, each with its reason and evidence.
Neither replaces an assigned slot or contributes to worker summaries.
Attribute their effort through `supplementary_attempt_id` or `excluded_attempt_id`; neither may also claim `judgment_role`.
Keep interrupted and unsuccessful attempts.

## Read the results

Tables are emitted as TSV and JSONL; nested evidence remains JSON inside TSV cells.
`aggregation.json` records the registration, allocation, procedure, index, optional disposition, tool, figure and assessor identities.

| Tables | Use |
| --- | --- |
| `runs`, `judgments` | Every assigned worker and judgment, identities and availability |
| `items`, `counts`, `cells` | Raw item answers and descriptive condition-by-round summaries |
| `measure_validity`, `comparable_items`, `comparable_counts` | Evidence-specific limitations and remaining valid measures |
| `version_strata`, `version_cells` | Procedure-specific denominators and summaries |
| `operations`, `effort` | Cited operations and validated duration measurements |
| `pairs`, `disagreement` | Preselected duplicate availability and differences |
| `supplementary_attempts`, `supplementary_items`, `excluded_attempts` | Additional evidence outside assigned outcomes |
| `issues` | Invalid artifacts and extraction problems |

Figures show scientific adequacy, checklist items, recurring item outcomes, effort and duplicate disagreement in PNG and SVG.
With a disposition, outcome figures are split by procedure identity; supplementary and version-specific effort stay separate.
Recurring item bars pool conditions and rounds descriptively; they do not show improvement.
The checklist follows registered launch order; effort points are observations, not sums across phases.
Inspect the rendered figures before publishing them.

Preserve `met`, `partial`, `unmet`, `not-checked` and `not-applicable` separately.
Missing or invalid assessments are not item verdicts, and partial never satisfies a MUST.
There is no overall score or certification.
Items linked to multiple principles count once within each dimension; intentionally repeated checklist questions remain distinct items.
Pinned denominators are S=3, T=4, A=3, M=7, P=6, E=2, D=6 and MUST=17, SHOULD=9, MAY=5.
Show applicable and full denominators, every allocated worker, availability, individual observations, medians and ranges.
Medians/ranges are unavailable when workers' valid item sets differ. Duplicate comparison uses mutually valid same-version items, retaining paired item and object denominators; checklist items are not independent workers. Follow [the frozen comparison plan](../comparison-plan.md): this small sample supports descriptive patterns, not reliable variance estimates or significance claims.

## Historical development comparison

Schema version 2 and assessment-amendment support remain for the earlier `narps-v1` development evidence.
Its planned allocation, mixed assessment versions and repaired supplementary attempts are not part of the neutral comparison.
Use its own registration, accepted amended seal, assessor pin and human-directed disposition when reproducing those tables.
The [historical guide](https://github.com/leej3/stamped-in-practice/blob/73b521343ca21081702a7252bf38fd12f6f6204a/scripts/AGGREGATION.md) retains those detailed contracts and amendment-specific instructions at an immutable revision.
Do not copy its counts, version exceptions or example paths into the current comparison.
