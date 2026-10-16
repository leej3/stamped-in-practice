# Completed trials and the next study

[Project overview](../README.md) · [Lessons](../LESSONS.md) · [Results](results.md)

This project improves research skills by using them in scientific work, assessing what agents produce and testing revised guidance with fresh agents.
The repository is the continuing framework for that process.
An individual trial supplies evidence about a particular task and setup; it is not the whole project.

## What we did and why

| Completed work | Purpose | What it contributed |
| --- | --- | --- |
| [Trial with failed results reporting](../iterations/trial-with-failed-results-reporting/) | Exercise the initial research-and-assessment setup on NARPS | Twelve research workers and sixteen assigned assessments exposed reporting problems and workflow constraints; this became development evidence |
| [NARPS study runs](../iterations/narps-study-runs/) | Compare four assistance strategies across three rounds of fresh workers | Seventy-two research attempts and ninety-six operational judgments supplied scientific results, reproducibility assessments and evidence for revising the skills |

The first effort began with a larger planned series, but its completed first round became a development trial.
The second effort used a separately registered setup that allowed workers more freedom in tools and delivery practices.
They should not be pooled as if they were one unchanged experiment.
Both are complete.

The NARPS work shows why scientific adequacy, checklist attainment, model capability and infrastructure support need to be considered together.
Its results do not establish a causal skill benefit, but the experience identifies practical changes worth testing.
The [lessons](../LESSONS.md) explain those changes; the [results guide](results.md) introduces the measures before the detailed records.

## Where the records live

The main branch provides the project narrative, lessons, navigation and reusable coordinator tools.
The two submodules hold the completed trial records at exact versions.
Their descriptive paths replace `iterations/narps-v1/` and `iterations/narps-neutral-v1/`, respectively.
Historical dataset IDs, branch names, registrations and individual run names remain unchanged so recorded evidence stays traceable.

For an existing local checkout, use `git submodule sync` after updating main, then initialize the new path you need with `git submodule update --init -- iterations/narps-study-runs` or `iterations/trial-with-failed-results-reporting`.
Keep any old working directory with local changes until those changes have been accounted for; it is not the newly named submodule.
A fresh clone can initialize just the selected new path.
See the [retrieval guide](../RETRIEVAL.md) for large payloads.

## Plan the next trial

1. Choose a study and scientific question, with versioned inputs and evaluation guidance.
   Use `studies/narps` for a new NARPS comparison or register another study under `studies/<name>/`.
2. Decide what is being tested: assistance strategies, skill revisions, worker capability or another explicit factor.
   Select worker and judge models separately and define common tool, dependency and infrastructure support.
3. Rehearse representative deliveries through assessment and reporting.
   Include a skill revision between rounds, and calibrate the judges before fixing the procedure.
4. Register a clearly named new iteration with its sample, resource budget, milestone completion rules, repair limits and escalation decisions.
   Preserve failures without letting repeated repair prevent completion.
5. Run fresh agents, assess the original deliveries, compare outcomes and revise the skills.
   Finish with a test of the final guidance; use additional studies to examine transfer.

The [coordinator prompt](../prompt.md) describes this workflow, the [comparison plan](../comparison-plan.md) defines the outcomes, and the [launcher guide](../scripts/README.md) covers execution.
The completed NARPS settings are historical choices, not mandatory settings for every future study.
