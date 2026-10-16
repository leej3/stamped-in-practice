# Scientific criteria wording calibration

Retain the exact pre-test candidate as a prospective wording clarification.
All four assigned readers returned all six cases; all 24 judgments and their friction notes are retained unchanged.
Registered input hashes and the frozen deck, expectations, source snapshots and candidate patch match.

The original-wording readers disagreed on C01 and C05: j01 chose **not supported**, while j04 chose **qualified**.
Both identified the same defensible bounded finding and unsupported wider scope, and both explicitly reported that the qualified boundary was undefined.
The candidate readers both chose **qualified** for these cases and reported no ambiguity on this deck.
All four readers agreed on the other cases: bounded positive and negative findings were supported, missing essential results were unable to assess, and the sign-reversing error was not supported.

See [the full category table](case-table.md), [aggregate JSON](aggregate.json), and [source paths and SHA-256 digests](source-index.json).
The retained author expectations explain the intended distinctions; they are not an external gold standard.
The original j01 labels are a defensible interpretation of its supplied wording, not evidence of reader failure.
No cases, criteria, judgments or readers were changed or added after inspecting outcomes.

The candidate and deck author reviewed this aggregate with assignments and expectations visible.
This targeted check covers six constructed vignettes and two readers per excerpt; the 24 entries are repeated readings of six cases.
It does not establish reliability, validity, efficacy or transfer, and no formal NARPS judgment is changed.
Scope narrowing is directly exercised; weaker-certainty qualifications, mixed errors and missing evidence, and multi-claim reports remain untested.
Full operational assessor behavior is also untested.

The launch records include retrospective entries and an initial capacity-blocked dispatch.
They record the default/no-override policy, not complete actual per-reader runtime identities; the coordinator is retaining that evidence separately.
No model comparison is made.

`aggregate.py` is the retained checking and aggregation source.
Its execution and subsequent source checks are captured under `logs/` with `duct --fail-time 0`.
The source branch contains only the exact two-file candidate patch; integration requires a new prospective source/runtime record and must preserve the frozen series.
