# STAMPED in Practice

Can reusable research guidance help AI agents do sound science and leave work that other researchers can inspect and reproduce?
This project tests that question by comparing four ways of assisting agents on the same neuroscience task, then revising the STAMPED guidance between rounds.
STAMPED describes research objects that are **self-contained, tracked, actionable, modular, portable, ephemeral and distributable**.

<img src="assets/workbench.png" alt="STAMPED workbench" width="280">

## Start here

- **Understand the findings:** [Results and their interpretation](docs/results.md) explains the completed comparison, the poster's measures and the main limitations.
- **Find your way around:** [Repository map](docs/repository-map.md) explains why links open different branches and where to find inputs, original analyses and assessments.
- **Explore the poster:** [Poster and figure guide](docs/poster.md) connects the presentation to readable explanations and the underlying evidence.
- **Use or inspect the guidance:** [Research skills and assessment](docs/skills.md) distinguishes the instructions given to researchers from the checklist used to assess their work.
- **Download files or reproduce work:** [Retrieval guide](RETRIEVAL.md) explains what is readable on GitHub and how to retrieve larger files.

## What we compared

Agents analyzed the same 54 participant brain maps from NARPS, a study of how different teams analyze a common neuroscience dataset.
Each agent addressed the same question about responses to potential gains in a gambling task.
We compared the scientific adequacy of their conclusions, evidence of reproducible research practices, replay attempts and effort.

| Condition | Instructions added to the scientific task |
| --- | --- |
| Baseline | No supplied research skills or discovery instruction |
| General discovery | Find, install and use skills useful for the task |
| Reproducible-science discovery | Find, install and use skills for scientific quality and reproducibility |
| Explicit STAMPED | Use the supplied, versioned STAMPED research workflows |

The completed comparison has three rounds, with six fresh agents per condition per round: **72 research attempts and 96 judgments**, including duplicate assessments.
The explicit STAMPED guidance changed between rounds; the other conditions provide repeated comparisons.
What agents were asked to use and what they actually used are recorded separately.

## What we learned

The retained results show that scientific adequacy and checklist attainment are different outcomes.
A higher fraction of STAMPED items met does not necessarily accompany a better-supported scientific conclusion.
The corrected reporting makes 70 primary scientific assessments and 68 valid checklists available across the 72 attempts.
It preserves missing assessments and the original reporting failures.

The main lessons concern how to design the whole research process: assessment that recognizes scientifically useful work, precise coordination rules that let rounds finish, capable judges, and shared guidance on dependencies and tools.
John's experience also points to the difficulty of asking Luna to handle scientific reasoning and reproducibility practices together, and to the hidden effort of preparing tracking and cluster infrastructure.
The [lessons for the next study](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/final-synthesis/LESSONS.md) explain these observations and priorities for better benchmarking, isolation, capture and skill evolution.

The approach is promising, but this small, adaptive study does not establish a causal skill benefit or transfer to other scientific tasks.
Read [the results guide](docs/results.md) for the poster's measures and their interpretation.

## How this repository works

`main` is the entrance and coordinator toolkit.
Studies, comparison records and individual research deliveries are separate versioned datasets, linked here as Git submodules.
Some are hosted on other branches of this same GitHub repository, so a link can open a different directory tree without leaving the project.
Those branches preserve distinct research objects; they are not all pending changes to merge into `main`.
The [repository map](docs/repository-map.md) explains each destination and how exact revisions remain traceable.

For development, [the coordinator prompt](prompt.md) describes the research loop, [the comparison plan](comparison-plan.md) defines the measures, and [the scripts guide](scripts/README.md) covers execution.
All assigned runs in the completed comparison have finished.
Consult its [completion and publication status](docs/results.md#completion-and-access) before planning new work; historical controllers must not be restarted.
