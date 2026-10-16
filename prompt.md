# Improve research skills through repeated use

Use this process for a formal run from the prepared repository in a fresh clone with shallow history.
Run this workshop to improve reusable STAMPED research skills through evidence from scientific work.
Use the study submodules selected for the new comparison as inputs to the repeated process.
Read the [completed trial history](docs/trials.md) and [lessons](LESSONS.md) first; NARPS is an existing study option, not a default instruction to resume completed work.
Each iteration tests one pinned skill revision with fresh agents, independently assesses their research objects, and uses the findings to improve the next revision.
Compare scientific validity, STAMPED evidence, effort and variability using the frozen [comparison plan](comparison-plan.md).
Report null, adverse and favorable outcomes using the same criteria.
The whole workshop must itself become a STAMPED research object.

1. Fix the study set, each scientific question and input package, evaluation criteria, common resources, model/settings, repetitions and completion/stopping rules before starting.
   Each study's `input/study-task.md` asks its question and defines its scope; workers choose defensible methods, software, figures and reproducibility practices.
   Keep reference answers and evaluation guidance in `coordinator-guidance/`, outside worker inputs.
   Register the number of rounds, workers per condition, duplicate assessments and fixed allocation for this comparison.
   Declare the resource budget and stopping rules; do not extend the sample to obtain favorable results.
   Select worker and judge models separately, calibrate judging on representative deliveries and record exact model identifiers and settings.
   Use the selected scientific task at its declared scope; fast computation is fine.
   Do not add scientific work solely to reach a target duration.
   Define milestone deliverables, a bounded repair budget, escalation conditions and when to advance with recorded failures.
   Provide the same explicit tool and dependency guidance to every condition, encouraging established scientific libraries and recoverable setup recipes.
   Record which infrastructure tasks the coordinator handles and which are part of the worker task.

2. For each selected study, launch fresh agents in four conditions, varying launch order: baseline, general skill discovery, reproducible-science skill discovery, and explicit pinned STAMPED.
   All receive the same fixed, materialized input package, model/settings, tool and network access, and optional common resources. Baseline receives no supplied research skills or discovery instruction; spontaneous discovery remains part of its observed behavior. General discovery asks agents to find, install and use useful skills; reproducible-science discovery asks for skills that improve scientific quality and reproducibility. Explicit STAMPED invokes the supplied pinned workflows. No condition receives previous solutions, judgments or coordinator history. Retain the exact added prompt and assigned condition separately from observed searches, candidates, selection reasons, source revisions, skill contents/hashes, installation outcomes and time, loaded instructions and evidence of use.
   Keep unsuccessful discovery and installation attempts in their assigned condition.
   Record exact input and environment revisions for every run.

3. Have fresh, independent judges assess each complete original delivery for scientific validity and STAMPED evidence separately.
   Freeze the assessor source, runtime, judging prompt, model/settings and replay scope before the first iteration.
   Supply the target object and scientific evaluation guidance without condition labels or coordinator conclusions.
   Evaluate the reasoning, evidence, limitations and reproducibility of the chosen approach; defensible alternative methods need not match a published solution.
   Preserve tracked, dirty, untracked and ignored scientific files, with a content-capture identity and the actual Git identity when present.
   Coordinator preservation is separately attributed and earns no worker-practice credit.
   Independently judge the registered subset of preselected objects twice; retain both judgments and distinguish judge disagreement from worker variability.
   Describe residual blinding limits honestly.

4. Compare outcomes within each study and across iterations, then improve research skills using observed failures and successful practices.
   In `iterations/<iteration>/`, link the exact study/input and skill revisions, worker branches, judgments and comparisons to the changes they motivate.
   Compress or modularize the guidance without inserting study-specific answers; record whether the next iteration resolves the problem.
   Keep study questions, inputs, baseline conditions and the assessor fixed within each comparison.
   Add new studies as explicitly recorded transfer checks; do not treat a changed study set as a skill effect.
   Record evidence-specific assessment defects as unavailable measurements; preserve unaffected evidence and every original attempt without selecting a better replacement.
   A necessary change to common setup or assessment defines a declared comparability boundary, not a skill-only effect.
   Finish with an iteration using the final skills without further tuning on its results.
   Interpret contrasts as effects of assistance strategies, since prompts can change behavior without skill use.
   Use the explicit pinned condition to test our skill revisions; keep unmatched historical results and preparation pilots separate.

Duct logging is requested for scientific execution; capture coordinator execution evidence outside worker instructions where supported.
Available tools, logging and coordinator preservation do not impose Git, DataLad, annex, Pixi, lock files, publication or a directory layout on workers.
Retain every attempt, input, output, assessment, intervention and execution record, including failures and partial results, under their study's `results/`.
Register each preserved experiment there as a pinned submodule; keep it uninitialized until needed.
The coordinator uses annex for large artifacts, preserves relevant environment snapshots and verifies independent retrieval.
Replay is a proportionate, optional assessment instrument; protect inputs, compare scientifically relevant outputs and report unavailable adapters as measurement limitations.
When reassessing results, state what stays fixed and what changes across data, code, dependencies and host, according to the question being tested.

Deliver improved shareable skills, evidence about their impact, examples of the frozen assessment, and a STAMPED research object documenting the workshop.
Include clear figures of scientific outcomes, checklist attainment, recurring failures, costs and variability across iterations.
Keep scientific validity separate from STAMPED evidence, retain `not-checked`, and do not invent an overall assessor score.
Have a fresh judge assess the complete effort.
Limit conclusions to the evaluated studies and exploratory sample; further studies can test transfer.
