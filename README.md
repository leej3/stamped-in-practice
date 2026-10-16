# NARPS study runs

This completed study compared four ways of assisting research agents on the same neuroscience task: no supplied skills, general skill discovery, reproducible-science skill discovery and explicit STAMPED guidance.
Workers analyzed the same 54 participant effect maps and scientific question, choosing their own methods and delivery practices.
The purpose was to test and improve research guidance through repeated scientific work.

**All three rounds are complete: 72 research attempts and 96 operational judgments.** Each round used six fresh workers per condition, with selected deliveries assessed twice to examine judge disagreement.
Research guidance changed between rounds; the final round tested the final revision without further tuning.

## Start with the findings

Read [the results and interpretation](https://github.com/leej3/stamped-in-practice/blob/main/docs/results.md) for the outcome measures, poster figures and what the comparison supports.
The corrected reporting provides 70 primary scientific assessments and 68 valid checklists.
Scientific adequacy and checklist attainment did not move together consistently, and the study does not establish a causal skill benefit.
The [project-wide lessons](https://github.com/leej3/stamped-in-practice/blob/main/LESSONS.md) explain what we learned about assessment design, coordination, model capability, dependencies and infrastructure.

## Explore the study records

| Question | Where to look |
| --- | --- |
| What was planned? | [Registered design](registration.md), [allocation](allocation.json) and [procedure](procedure.json) |
| What are the completed outcomes? | [Reporting correction and results](final-synthesis/REPORTING-CORRECTION.md), with links to per-round and per-run summaries |
| Why did the guidance change? | [Research-skill revisions](skill-reflection/) |
| What happened during each round? | [Round records](rounds/) and [assessment series](assessment-series/) |
| Which files can I retrieve? | [Publication and access record](final-synthesis/PUBLICATION.md) |
| Is execution finished? | [Completed status](STATUS.md) |

Earlier reports describe intermediate states, including the original round-one assessment and later reporting failures.
They are retained to explain the development history, not as the current completion status.
The later reporting correction used existing judgments without rerunning workers or changing their grades.

## Where this dataset fits

On the coordinator's main branch, this dataset is linked at `iterations/narps-study-runs/`.
Its historical identifier is `narps-neutral-v1`; the hosting branch remains `codex/iteration-narps-neutral-v1` to preserve existing evidence links.
The [trial history](https://github.com/leej3/stamped-in-practice/blob/main/docs/trials.md) explains how this study followed the earlier development trial and how to start a new comparison.

`study/`, `assessment/` and `skills/` link to versioned inputs and guidance; initialize only the components you need.
Coordinator preservation and later presentation are recorded separately from the workers' original deliveries.
All assigned execution is finished; historical controllers must not be restarted.
