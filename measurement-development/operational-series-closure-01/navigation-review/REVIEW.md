# Coordinator navigation review

Reviewed coordinator commit `20081f5352011dd8dc81677e2bd5fa8c738b2808`,
starting with its README, AGENTS and prompt, then selected links at pinned
subdataset commits. Exact inspected blob identities are in `sources.json`.
No jobs, submodule initialization, external investigation or repository writes
were performed.

**Verdict:** The context lets a newcomer identify the correct next work and
preserve the comparison boundaries. Continue the existing assessment-only
series, its evidence retention/publication and separate extraction; keep new
research held for the measurement-viability decision. It does not by itself
supply a safe operational handoff to the running dispatcher. Two small navigation
corrections would make continuation unambiguous.

1. **Make the current state the first coordinator instruction.**
   `README.md:31–33` tells a starting coordinator to select and seal a prospective
   registration; only line 64 directs it to current status, through a moving
   branch URL. At this pinned revision, the registration is already sealed and
   a separate assessment series is running. A newcomer following the prominent
   recipe can begin planning a fresh registration before discovering the hold;
   following the branch URL can also mix a later status with this checkout.
   Smallest correction: change the example to read the selected iteration's
   pinned `STATUS.md` first and continue its registered stage, then follow
   `prompt.md`. Link `iterations/narps-neutral-v1/STATUS.md` locally (or by its
   exact gitlink commit), and label any branch link as the latest online state.

2. **Add a short handoff beside the running-series link.**
   `iterations/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/README.md:11–14`
   and `STATUS.md:18–21` describe a running queue and point to a committed
   snapshot. `progress.json` records 21 started and 19 completed at
   `2026-10-16T11:30:03.749189+00:00`; it does not establish present liveness.
   The retained controller is discoverable only deeper under
   `dispatch-evidence/initial-launch-01/run_series.py`; its paths assume the
   original host layout and it starts from batch one, creating a new queue
   directory with `exist_ok=False`. Those are historical launch evidence, not
   a documented continuation procedure.
   Smallest correction: add one handoff paragraph linking the controller and
   live control/evidence location, explicitly requiring reconciliation of the
   existing dispatcher and slot receipts before any continuation, and state
   whether a newcomer should monitor the existing queue or take it over.
   Also name the following tasks: finish all allocated attempts, retain and
   publish available support, extract into a separate output, then record
   measurement viability before further research. No new execution mechanism
   or study redesign is needed.

The rest of the navigation is sufficient for this review:

- Root owns reusable coordination code and the loop. The study owns fixed
  `input/`, coordinator-only scientific guidance and experiment gitlinks;
  experiments own original research objects and separately attributed
  coordinator captures. Iterations own assignments, judgments, synthesis and
  the reasons for skill changes. `skills/` and `assessment/` are separate pins.
- Frozen records include original inputs, allocation, procedure, deliveries,
  judgments and the round-one skill pin. Candidate skills, new preservation
  commits, progress and future registrations can evolve with explicit version
  boundaries. The operational assessment series preserves the original results
  and uses source `4f72ef49fdbcd50c55df6e31867579a2e7e870ad` and its separate seal.
- `rounds/round-01/synthesis/README.md` leads to figures, extracted judgments,
  observed skill actions and `EXPERIMENTS.md` for original scientific paths.
  The study README and `RETRIEVAL.md` explain exact captures and lazy retrieval.
  The completed development comparison is separately indexed by
  `iterations/narps-v1/DATASET.md`.
- `skill-reflection/research-skill-revision-01/README.md` identifies candidate
  commits, trials and untested wording changes without changing the formal pin.
- Publication limits are explicit: authorized Hub access, same-host retrieval
  rather than portability, coordinator work earning no worker credit, and
  pending operational-series archives despite available Git refs. The new
  series has two verified complete support publications in this snapshot;
  its publication failures do not erase local records or stop judging.

No additional consequential ownership, frozen-material, evidence-discovery or
publication-limitation ambiguity was found in the inspected paths. This review
assesses navigation and coordination only; it does not grade the science or
claim to verify live progress or remote payload availability.
