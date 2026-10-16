# Coordinator instructions

Follow `prompt.md` to iterate on reusable skills using the study submodules selected by the user.
The unit of iteration is a pinned skill revision; study-specific preparation and findings stay in their submodules.
The completed `iterations/narps-v1/` subdataset is development evidence; preserve its frozen records and original outcomes.
Use a separately registered stable protocol for subsequent comparable rounds, with coordinator preservation separated from worker requirements.

- Derive resource requirements from the user prompt, applicable system skills and memory.
  Use [programmatic readiness checks](scripts/READINESS.md) with user-provided host configuration; retain evidence before research and ask only for missing access or decisions.
  Do not assume a universal service list or treat executable availability as proof of access.
- Record each iteration under `iterations/<iteration>/`: skill revision, exact study/input revisions, linked worker branches and judgments, comparisons, and the rationale and outcome of skill changes.
  Keep these coordinator records outside worker inputs.
- Give research workers only the study's fixed, materialized `input/`, optional common resources and their assigned skills.
  Use `pixi run launch` to create independent repositories without coordinator history, references or prior results; separate worktrees alone share Git objects.
  Keep coding tasks in their own worktrees.
- Register each published experiment repository as a submodule at the selected study's `results/<run>/`; retain complete worker branches and failed attempts.
  Keep study and experiment submodules uninitialized by default; initialize only selected paths and required dependencies.
  Keep launch and judging receipts outside workers while they run, then retain them in a later experiment commit without changing the recorded scientific result commit that was judged.
  Before judging, preserve the complete original delivery and verify the assessment copy against its capture; publish coordinator retention separately from any worker publication.
  Use the coordinator environment for inspection and preservation; retain the worker's original environment evidence before commands that could change it.
  Keep generic guidance in `skills/` and evaluation references outside worker inputs.
- Workers choose scientifically suitable tools, environment management and delivery organization.
  Available infrastructure is not a requirement to adopt it.
  Preserve the environment evidence they actually provide; keep coordinator-managed resource environments and their provenance separate.
- Keep coordinator working `pixi.lock` files ignored.
  Preserve its exact validated lock on `codex/env-<task>-<run>`; publish that environment snapshot without merging it into main.
  Preserve worker locks and environment records in their original state rather than imposing this coordinator convention.
- Launch matched workers from the same coordinator revision and study input package.
  Use the four conditions in `prompt.md`; retain assigned condition separately from observed discovery, installation and use.
  Keep tool and network access matched, and do not relabel spontaneous baseline discovery or unsuccessful discovery runs.
  Use the registered judge launcher with the exact original delivery capture and external frozen assessor; retain its actual Git identity when present.
  Give judges the same scientific evaluation guidance without condition labels or coordinator grades.
  Keep assessment source, runtime, prompt and settings fixed throughout each comparable series.
  Seal the procedure before formal launches; use its digest and the readiness receipt with both workers and judges.
  Pass each worker's original stop receipt to its judges; coordinator preservation must not earn worker credit.
- During preparation, improve and repin the assessor and runtime as needed, retaining exact version records.
  Test revisions on new deliveries; preserve earlier judgments and distinguish measurement failures from worker outcomes.
  Keep preparation pilots and historical results from other designs separate from formal comparisons.
- Keep `skills/` pinned to the tested commit on our clearly named `con/skills` development branch; change it only between iterations.
  Improve and compress skills from observed problems and useful practices; keep study answers out of generic guidance.
- Retain code, inputs, results and execution evidence; annex large artifacts and verify independent retrieval.
  Publish study and skill commits and required annex payloads before updating their parent gitlinks.
  Keep requested duct metadata, stdout/stderr, resource data and summaries with the run; MechaBABS uses its native records.
  Pass `--capture-execution` to the launcher only when duct logging is requested.
  Credentials remain with host providers; do not publish credentials or restricted human data.
- Use Conventional Commits and freshly resolved provenance trailers for authored commits.
  Preserve native DataLad subjects and run records, appending attribution without rewriting them.
  Run Snapper on authored prose.
