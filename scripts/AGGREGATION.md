# Aggregate a registered comparison

`aggregate_comparison.py` reads coordinator extractions and produces descriptive tables and figures.
It does not inspect worker repositories, run judges, change the procedure, or infer scientific verdicts.
The allocation supplies every run, condition, replicate, launch order and duplicate selection.
All assigned workers remain visible when evidence is missing.

Use the coordinator environment and a new output directory:

```sh
pixi run python scripts/aggregate_comparison.py \
  --allocation iterations/narps-v1/allocation.json \
  --index /path/to/extraction-index.json \
  --assessment-procedure-sha256 <approved-amended-seal-digest> \
  --output /path/to/comparison-report-01
```

The assessor repository must contain the commit in `assessment-version.json`.
Use `--assessment-pin` for the exact pin selected by the approved amendment.
Use `--assessor /path/to/assessment` for an initialized checkout elsewhere.
The tool reads its immutable checklist, lock and response schema with `git show`; it does not execute the assessor.
Neither existing output directories nor source artifacts are overwritten.
It exits 2 for malformed input or evidence errors.
Artifact errors also appear in generated `issues` tables; valid independent observations are retained.

An honest initial index is:

```json
{"schema_version": 2, "runs": []}
```

This produces 36 pending workers and 48 assigned judgment slots for `narps-v1`, with no invented item verdicts or zero-valued effort measurements.
The amended digest is unnecessary for an empty index or excluded-attempt-only records.

## Admission to the comparison

The CLI verifies allocation and original procedure bytes against the independent original `registration.json`.
By default, `registration.json` and `procedure.json` are siblings of the allocation; override with `--registration` and `--research-procedure`.
Supply the approved amended digest from the amendment record through `--assessment-procedure-sha256`, independently of the extraction index.
An index cannot select its own amendment or replace the original research registration.

For included outcomes, the index needs one `comparison_provenance` object:

```json
{
  "assessment_seal": {"path": "assessment-procedure-v2.json", "sha256": "<approved digest>"},
  "research_procedure_sha256": "<original registered digest>"
}
```

The selected version 2 seal must embed the exact original research procedure bytes and preserve the research design, settings, replay policy, environment and fixed files outside the four assessment adapter files permitted by the amendment.
The loaded assessor pin must match the amended seal exactly.
Each included judgment needs `native.procedure_status` and `native.result`, both hashed artifact references to the retained native files.
The gate requires formal verification, both procedure digests, the original worker-stop hash, identical procedure receipts, the selected assessor source and environment, the exact scientific result commit, an unchanged target, a completion timestamp and native session IDs.
Judge sessions must have a null condition; IDs cannot be reused across included or excluded attempts.
Nonzero process return codes remain operational facts and do not choose or replace primary judgments.

Runs listed in the amendment's `retained_objects` must match its seed, result and original stop identities.
Other runs also need hashed `worker_native.procedure_status`, `worker_native.result`, and `worker_input` references.
These bind the original research procedure, assigned condition, seed commit, worker input identity, stop receipt and stopped HEAD.
Future research workers must use the original frozen research driver and original seal; the assessment-only amendment cannot authorize research launches.
The original worker HEAD need not equal the later preserved scientific result commit.

Each included extraction also requires a hashed `output_binding` manifest:

```json
{
  "schema_version": 1,
  "kind": "coordinator-assessment-output-binding",
  "native_result_sha256": "<finalized native result hash>",
  "native_session_ids": ["<native session UUID>"],
  "outputs": {
    "response": {"path": "judgment/response.json", "sha256": "<response hash>"},
    "report": {"path": "judgment/assessment.md", "sha256": "<report hash>"}
  }
}
```

Create this manifest from retained session output evidence; its hashes must match every indexed response and report, and its result hash and session IDs must match the native receipts.
Paths in the manifest are retained source locators, so files may be relocated in the extraction index without changing their bytes.
This is a coordinator attribution record: native result receipts do not themselves hash assessment outputs.
The gate checks consistency and known reuse, not native authorship or the truth of an extraction.
Preserve the supporting capture or root-file manifest separately.
Bytes already recorded as an excluded attempt's response or report cannot enter an included judgment.

Missing or invalid admission evidence blocks both checklist and narrative outcomes while preserving every allocated slot and its denominator.
No fallback to a matching checklist version is permitted.
`inclusion_status` is `pending`, `eligible`, or `invalid`; eligibility is separate from canonical response validation and scientific adequacy.
Library callers must supply trusted registration bytes and an approved digest; the CLI additionally verifies allocation and original-seal hashes against the registration.

## Extraction index

Paths in artifact references are absolute or relative to the index file.
Every artifact reference has `path` and the lowercase SHA-256 of its exact bytes.
The tool verifies hashes before reading responses, reports or measurement sources.
Unknown fields, duplicate JSON keys, nonfinite numbers, unknown runs, repeated judgment IDs, and unselected duplicates are rejected.
The complete machine-readable contract is `INDEX_SCHEMA` in the script.

Each optional run record has:

- `run_id`: the allocated identifier.
- `result_commit`: exact scientific commit, required when a judgment is supplied.
- `seed_commit` and hashed `worker_end_state`: original worker identities required for admission.
- Optional `worker_head`, `retention_commit` and `skill_commit`: exact Git IDs.
- Optional `worker_completion`: `pending`, `completed`, `failed`, `interrupted` or `unknown`.
- `judgments`: an object with optional `primary` and `duplicate` records.
  Roles mean first assigned and preselected second judgment, regardless of completion time or result.
  A duplicate never fills a missing primary.
- `operations`: optional observations described below.
- `excluded_attempts`: original infrastructure attempts retained outside assigned judgment slots.

A judgment has a unique `judgment_id`, admission evidence described above, optional hashed `response` and `report` references, optional `adequacy`, and optional `conclusion`.
Omitted evidence remains missing.
An invalid response contributes no checklist items.
The response must contain all pinned item IDs and the indexed result commit; metadata, evidence and verdict semantics must validate against the frozen contract.
Use canonical response JSON, never the checklist URL or a probe draft.

This judgment fragment illustrates an explicit narrative extraction.
Replace placeholder hashes with actual hashes before use:

```json
{
  "judgment_id": "neutral-judgment-01",
  "response": {"path": "judgment/response.json", "sha256": "<64 lowercase hex>"},
  "report": {"path": "judgment/assessment.md", "sha256": "<64 lowercase hex>"},
  "adequacy": {
    "extraction_status": "explicit",
    "category": "qualified",
    "excerpt": {
      "quote": "Scientific adequacy: qualified.",
      "start_line": 8,
      "end_line": 8
    }
  },
  "conclusion": {
    "quote": "The reported conclusion, copied exactly.",
    "start_line": 12,
    "end_line": 12
  }
}
```

Categories are `supported`, `qualified`, `not supported`, and `unable to assess`.
Explicit extraction requires an exact quotation within inclusive, one-based report lines.
The quotation and its complete cited lines must name the selected category and no competing category.
Copy a concise sentence or clause, not the rubric's list of possible verdicts.
The tool verifies traceability; it does not decide whether reasoning is correct.
Use `extraction_status: "missing"` or `"ambiguous"` with `category: null` when no unique explicit category is available.
Do not turn a missing classification into `unable to assess`.
Keep the scientific conclusion separately, including defensible null findings.

## Operations and effort

Record original pre-amendment attempts in `excluded_attempts`, with a unique `judgment_id`, a nonempty `reason`, optional `native` receipt references, and optional hashed `response` and `report` references.
They are validated against the original seal and original assessor pin, and never supply checklist, adequacy, conclusion or disagreement outcomes.
Incomplete receipts remain visible as invalid operational evidence; they do not prevent retention of the attempt or other assignments.
Omit scientific extraction fields from this collection.
An operation may use `excluded_attempt_id` to identify one of its run's excluded attempts; it cannot also claim `judgment_role`.
Its recorded duration remains in `operations`, but enters `effort` only when both its measurement sources and excluded-attempt provenance validate.
Excluded infrastructure costs are labeled and plotted separately from assigned comparison measurements, even when their stage, actor and scope match.

Each observation requires `operation_id` (unique within its run), `stage`, `actor`, `status`, a nonempty measurement `scope`, and one or more hashed `evidence` references.
Stages are `setup`, `worker`, `discovery`, `installation`, `computation`, `judging`, `replay`, `input-retrieval`, `output-retrieval`, `environment-retrieval`, `publication`, and `coordinator`.
Actors are `worker`, `judge`, and `coordinator`.
Optional `judgment_role` identifies `primary` or a preselected `duplicate` for judge observations.
Statuses are `succeeded`, `partial`, `failed`, `not-attempted`, `not-checked`, `interrupted`, and `unknown`.
Record only what the cited evidence establishes.

Optional `duration_s` is a nonnegative measured duration; zero is valid, absence is missing.
Optional `metrics` entries contain `name`, nonnegative numeric `value`, `unit`, and `scope`.
Record token, memory and CPU measurements with their actual scope.
The tool does not sum overlapping commands or convert token counts to spending.
Effort plots group measurements by stage, actor and exact scope.
Use a consistent scope string for comparable measurements.

Retrieval observations also require `recipient`, `route`, `artifact_class`, `required_coverage`, `verified_coverage`, and `host_scope`.
Identify the authorized recipient and distinguish metadata visibility from verified payload retrieval.
Same-host cloning does not establish cross-host portability.
Keep coordinator publication separate from worker-stop behavior.

Replay observations may separately record `replay_attempt_observed`, `helper_completed`, `entrypoint_executed`, `entrypoint_returncode`, and `replay_status`.
The latter preserves the helper's original status.
Optional output counts are `compared_outputs`, `identical_outputs`, `within_tolerance_outputs`, `differing_outputs`, and `missing_outputs`.
A consumed allowance is not proof the entrypoint ran; a zero helper exit code is not proof outputs reproduced.
An interrupted attempt with no final report remains an interrupted observation.

## Outputs and interpretation

Each normalized table is saved as TSV and JSONL.
Nested evidence, flags and excerpts remain JSON in TSV cells.
Tables are:

- `runs`: all assigned workers and known commit identities.
- `judgments`: all primary and preselected duplicate slots, response availability and narrative extractions.
- `excluded_attempts`: original infrastructure attempts, their exclusion reasons, receipt validation and operational identities.
- `items`: valid canonical item answers with evidence, source and flags; additional answer fields remain under `answer_extensions`.
- `counts`: separate status counts by level and STAMPED dimension.
- `cells`: condition-by-round adequacy counts and per-run checklist count medians/ranges.
- `operations` and `effort`: cited observations and verified duration measurements.
- `pairs` and `disagreement`: duplicate availability and exact paired status differences.
- `issues`: invalid artifacts and extraction problems.

`aggregation.json` retains allocation, registration, original procedure and index hashes, the independently approved amended digest, selected seal reference and assessor/checklist pins.
Five figures are saved in SVG and PNG: scientific adequacy, item statuses, recurring item outcomes, effort, and duplicate disagreement.
The item figure follows registered launch order.
Effort points represent observations, not sums across phases.

Keep all five statuses: `met`, `partial`, `unmet`, `not-checked`, `not-applicable`.
Count each item once per dimension even when it names several principle codes.
Pinned denominators are S=3, T=4, A=3, M=7, P=6, E=2, D=6, and MUST=17, SHOULD=9, MAY=5.
The intentionally duplicated checklist questions remain distinct items.
N/A stays visible in the full denominator, with the applicable denominator retained separately.
Partial never satisfies a MUST.
There is no combined score or certification.

Missing or invalid assessments are separate from `not-checked` verdicts.
Cell denominators retain all three allocated workers, with valid-primary availability explicit.
No observations means missing median/range, not zero.
Duplicate matrices use complete pairs and show availability out of the preselected pairs.
Checklist comparisons are nested within objects, not independent extra workers.
With three workers per cell, interpret individual observations, counts, medians and ranges descriptively.
Do not infer significance or reliable variance estimates.
