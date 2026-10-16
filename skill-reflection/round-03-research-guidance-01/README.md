# Round-three research-guidance revision

Round two completed all 24 research workers and 32 assigned judges.
The frozen reporting gate rejected all 32 judgments because it compares each worker's coordinator commit with the original research seal: `cfeccf4fd14c1f1ef2fe6e27500c3ea139df986e` instead of the approved round-two source `9068886f91615b2c69578bdaa6042a858f4d9011`.
There are no admissible round-two scientific or checklist scores and no available duplicate-agreement estimate.
These are measurement failures, not zero scores or scientific failures.
The original judgments and reporting rejections remain unchanged.

This one research-skill revision is informed by direct inspection of closed round-two deliveries, not replacement grading.
In the explicit-skill condition, runs 02, 06, 09, 16 and 21 documented a shared host interpreter and versions; their cited setup documents did not provide a retrievable environment recipe.
Run 23 delivered `environment.yml`.
The [byte-identical document copies](delivery-evidence.json) retain the inspected paths and hashes.
This observation does not establish that run 23 works on another host or that any condition performs better.

The revision clarifies one existing requirement in `do-full-research-loop`: deliver the environment recipe itself, or a retrievable pinned source, alongside the runtime identity and setup instructions.
It distinguishes a usable recipe from a host-local path or prose version list.
It does not impose a particular environment manager, lock policy, new environment replay or scientific method.
No study answer is added.

The base skill revision is `d83d7d66a9060be6afae57336124afdcfc1743e9`.
Only `skills/do-full-research-loop/SKILL.md` changes.
The assessor, rubric, prompts, helpers and runtime remain frozen.
Round three is the next independent behavioral test; no extra pilot or judgment was run.
Its reporting remains subject to the same disclosed provenance-gate limitation.
A completed run or passing structural check is not evidence of skill effectiveness.

Snapper formatted the edited file.
The existing structural validator checked the changed skill with zero errors or warnings; its complete command, output and resource record is in `duct/`.
The change, before/after skill files, exact source bindings and final skill commit are retained beside this note.
Publication of this evidence does not repair or replace the original research objects.
