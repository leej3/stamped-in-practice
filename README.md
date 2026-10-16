# Improving STAMPED research skills

<img src="assets/workbench.png" alt="STAMPED workbench" width="280">

This repository is a workshop for improving STAMPED research skills.
It compares four ways of assisting agents with scientific studies, evaluates the resulting research objects using a versioned assessment, and uses that evidence to revise the skills.
The question is whether the guidance helps agents do sound science with more thorough, efficient and consistent reproducibility.

Each iteration tests a pinned skill revision on selected studies: run matched agents, assess their work independently, compare outcomes and effort, then improve and compress the reusable guidance.
Study inputs and scientific outputs belong to study submodules; iteration subdatasets connect that work to changes in the skills.

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

> Follow `prompt.md` using `studies/narps`; select and seal a prospective registration before launching new workers.

| Location | Purpose |
| --- | --- |
| `prompt.md` | The research, assessment and skill-improvement loop |
| `AGENTS.md` | Instructions for the coordinator |
| `iterations/<iteration>/` | An iteration subdataset with revisions, linked trials, assessments, comparisons and reasons for changes |
| `studies/<study>/` | A versioned study submodule |
| `studies/<study>/input/` | The scientific prompt and verified data supplied to research workers |
| `studies/<study>/coordinator-guidance/` | Evaluation guidance and reference material for the coordinator and judges |
| `studies/<study>/results/<run>/` | An experiment submodule containing the worker's research object, assessments and execution records |
| `skills/` | Evolving `con/skills`, pinned to [our development branch](https://github.com/con/skills/tree/codex/narps-round1-research-guidance) |
| `assessment/` | The selected assessor version, identified by `assessment-version.json` |

Keep iteration, study and experiment submodules uninitialized until needed.
Open selected paths and retrieve their required annex content; the coordinator tree retains their exact commits without expanding every experiment.

The intended result is transferable guidance: an independent agent can use these skills with a researcher's own data and hypothesis to produce scientifically useful, rigorous and convenient research.
The products are improved shareable skills, evidence about their impact, and a STAMPED research object documenting the whole workshop.
Figures summarize scientific outcomes, reproducibility, effort and variability.

NARPS is the first formal study.
The tested source and preparation evidence are linked in [`source-version.json`](source-version.json); formal trials and skill iterations are recorded here.

The [completed NARPS development comparison](https://github.com/leej3/stamped-in-practice/blob/4b6a8b34b6387150ea2a805bf48bbf5c159f8452/DATASET.md) contains twelve research workers, sixteen assigned judgments, figures and the resulting skill reflection.
Its workflow mandates and assessment changes are disclosed; the next stable comparison will keep coordinator preservation separate from worker guidance.
