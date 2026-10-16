# Improving STAMPED research skills

<img src="assets/workbench.png" alt="STAMPED workbench" width="280">

This repository is a workshop for improving STAMPED research skills.
It compares four ways of assisting agents with scientific studies, evaluates the resulting research objects using a versioned assessment, and uses that evidence to revise the skills.
The question is whether the guidance helps agents do sound science with more thorough, efficient and consistent reproducibility.

Each iteration tests a pinned skill revision on selected studies: run matched agents, assess their work independently, compare outcomes and effort, then improve and compress the reusable guidance.
Study inputs and scientific outputs belong to study submodules; root iteration records connect that work to changes in the skills.

The broader hypothesis concerns both humans and agents; this experiment tests agents.
Repeated baseline runs help distinguish improvements from ordinary variability.
Results from one study do not establish transfer to other studies.

| Condition | Added assistance |
| --- | --- |
| Baseline | No supplied research skills or discovery instruction |
| General discovery | Find, install and use skills useful for the task |
| Reproducible-science discovery | Find, install and use skills for scientific quality and reproducibility |
| Explicit pinned STAMPED | Invoke the supplied, versioned STAMPED workflows |

All conditions receive the same scientific task and common resources.
We record assigned assistance separately from what agents actually discover, install and use, including unsuccessful attempts.
These comparisons measure assistance strategies: wording can affect behavior even without skill use.
The explicit STAMPED condition directly tests the guidance we are improving.

During preparation, the assessor and its runtime can improve alongside the other skills.
Formal runs begin from a fresh clone with shallow history and keep their assessment version fixed.

To start a coordinator, give it this repository and a request such as:

> Follow `prompt.md` using `studies/narps` and its registered comparison in `iterations/narps-v1/`.

| Location | Purpose |
| --- | --- |
| `prompt.md` | The research, assessment and skill-improvement loop |
| `AGENTS.md` | Instructions for the coordinator |
| `iterations/<iteration>/` | Skill revisions, linked trials and assessments, comparisons and reasons for changes |
| `studies/<study>/` | A versioned study submodule |
| `studies/<study>/input/` | The scientific prompt and verified data supplied to research workers |
| `studies/<study>/coordinator-guidance/` | Evaluation guidance and reference material for the coordinator and judges |
| `studies/<study>/results/<run>/` | An experiment submodule containing the worker's research object, assessments and execution records |
| `skills/` | Evolving `con/skills`, pinned to [our development branch](https://github.com/con/skills/tree/codex/pr26-operational-environment) |
| `assessment/` | The selected assessor version, identified by `assessment-version.json` |

Keep study and experiment submodules uninitialized until needed.
Open selected paths and retrieve their required annex content; the coordinator tree retains their exact commits without expanding every experiment.

The intended result is transferable guidance: an independent agent can use these skills with a researcher's own data and hypothesis to produce scientifically useful, rigorous and convenient research.
The products are improved shareable skills, evidence about their impact, and a STAMPED research object documenting the whole workshop.
Figures summarize scientific outcomes, reproducibility, effort and variability.

NARPS is the first formal study.
The tested source and preparation evidence are linked in [`source-version.json`](source-version.json); formal trials and skill iterations are recorded here.

Round 1 is completing its original **12 research workers and 16 assigned judgments**; it is not restarting the science.
All twelve original research workers have finished.
All twelve primaries and three preselected duplicates have finished; the final assigned duplicate is running.
One supplementary repair attempt is retained separately.
The [current status](iterations/narps-v1/assessment-hold.md) and [ledger](iterations/narps-v1/round-1.json) track progress.
The [measurement disposition](iterations/narps-v1/measurement-disposition-01.md) preserves first-assigned judgments and marks infrastructure-affected measures unavailable.
Successful replay is not a completion gate.

The [common-workflow limitation](iterations/narps-v1/common-workflow-limitation-01.md) records that all round-one conditions were required to use Pixi, a fixed output location, duct and annex.
The baseline tests added assistance within that supplied workflow; scientific adequacy remains separate from tool and format conformity.

The entire first round will be retained as development evidence.
After its comparison and skill reflection, a declared tool-neutral setup will separate coordinator preservation from worker guidance and establish a stable protocol for subsequent comparable rounds.
Changes across that boundary will not be presented as a clean skill effect.
