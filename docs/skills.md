# Research guidance and assessment

[Project overview](../README.md) · [Repository map](repository-map.md)

The project uses two kinds of guidance.
Research skills help an agent plan, execute and document a study.
The assessor examines the resulting research object and records evidence against the STAMPED checklist.
Keeping these roles separate lets us change the research guidance while retaining a fixed assessment procedure for a comparison.

## Explore the research skills

The [tested round-three research bundle](https://github.com/con/skills/tree/codex/narps-round3-research-guidance/skills) is in the separate `con/skills` repository.
Its branch name identifies the guidance developed for this study; it is not a claim that these changes are part of that repository's default branch or a general validated release.
Each `SKILL.md` is an instruction file for an agent.

| Workflow | What it helps an agent do |
| --- | --- |
| [Complete a research loop](https://github.com/con/skills/blob/codex/narps-round3-research-guidance/skills/do-full-research-loop/SKILL.md) | Carry a scientific question through planning, analysis, checks and reporting |
| [Create a STAMPED project](https://github.com/con/skills/blob/codex/narps-round3-research-guidance/skills/create-stamped-project/SKILL.md) | Organize a new research object with explicit inputs and an executable route |
| [Improve an existing project](https://github.com/con/skills/blob/codex/narps-round3-research-guidance/skills/align-with-stamped-principles/SKILL.md) | Address observed gaps in the research workflow and its documentation |

For reuse, begin with the workflow that fits your own question and project.
Read its instructions and requirements before asking an agent to apply it.
The bundle is experimental: the NARPS comparison does not establish that it improves performance on other datasets or scientific tasks.

## What changed between rounds

The research skills were tested at three exact revisions:

| Round | Tested revision | Role |
| --- | --- | --- |
| 1 | [f2e74ea3](https://github.com/con/skills/tree/f2e74ea3ed372f966c95692cb0826d56ad5e6a6c/skills) | Initial guidance for the three-round comparison |
| 2 | [d83d7d66](https://github.com/con/skills/tree/d83d7d66a9060be6afae57336124afdcfc1743e9/skills) | Revised research guidance |
| 3 | [32660661](https://github.com/con/skills/tree/326606610af6c261876c92032ca1f89f6d3ad1f1/skills) | Final tested guidance, including a clarification to supply an executable setup recipe or retrievable pinned source |

The [revision evidence](https://github.com/leej3/stamped-in-practice/tree/codex/iteration-narps-neutral-v1/skill-reflection) lives in the comparison dataset because it records why guidance changed.
The [lessons](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/final-synthesis/LESSONS.md) provide the narrative before the detailed inspection records.
Exact revisions identify what was tested; browsing the latest branch is not a substitute for them when replaying an earlier round.

## Understand the assessor

The [assessment instructions](https://github.com/con/skills/blob/codex/pr26-neutral-assessor/skills/assess-alignment-with-stamped-principles/SKILL.md) describe how the evaluator inspects a research object.
The completed operational series used assessor revision [9852d836](https://github.com/con/skills/tree/9852d8360f9519d21d11099b45f5deb8ba80cb28/skills/assess-alignment-with-stamped-principles).
The coordinator's current `assessment/` link can serve later development; the completed iteration records remain the authority for what its judges used.

A fixed assessor makes the procedure traceable, but does not by itself establish reliable judgments.
Read [the results guide](results.md) for disagreement, reporting corrections and the difference between scientific adequacy and checklist attainment.
To inspect the principles themselves, open the [STAMPED checklist](https://checklist.stamped-principles.org/).
