# Round-two operational assessment

The 24 assigned round-two research deliveries are complete.
Their 24 primary judgments and eight preselected duplicates are running once each under the existing Luna/high operational v4 mechanism.
No research is restarted.

[Registration and exact order](registration/series.json), [assessment seal](registration/assessment-procedure.json), [original delivery bindings](registration/retained-objects.json), and [first native starts](first-native-starts.json) retain the execution identities.
Seal `fe2478235e58b5d7b1ac16043d947b47e06014e7c3b4d420ed2538541ee23b82` differs from the previous round-one seal only in its retained-object bindings; [the static comparison](registration/static-binding-check.json) records that boundary.
Source `4f72ef49` and assessor `9852d836` remain fixed.

The user-authorized schedule permits up to 10 local native sessions.
The existing three-slot batches overlap in their original order; this changes timing interpretation, not the assigned sample or condition labels.
[The scheduling-only diff](registration/scheduling-only.diff) preserves the coordinator amendment separately from frozen native runtime source.

Failures, malformed outputs, replay limitations, missing measures and disagreement remain outcomes.
No retries, repairs, replacement judgments or sample extension are authorized.
Known limitations of the old v4 procedure remain disclosed; prospective main-branch fixes are not this execution source.

The active controller is the original local copy of `registration/run_series.py`, using `registration/dispatch_series.py`.
Its state is under `~/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/`.
Inspect `queue-01`, per-slot `dispatch.json` and `completion.json`, and actual process state before any continuation.
Never start a second controller while this one is active or duplicate a dispatched slot.
Repository copies document these scripts; moving them changes their relative path assumptions.

Full delivery/native preservation proceeds locally.
Hub payload publication is pending and does not delay executable assignments.
Earlier round-one series remain unchanged.
