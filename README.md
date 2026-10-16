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

To start or resume a coordinator, give it this repository and a request such as:

> Follow `prompt.md` using `studies/narps`.
> First read the selected iteration's pinned `STATUS.md` and reconcile any active runs.
> Continue its registered next step; select and seal a new registration only when no existing one applies.

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
The [retrieval guide](RETRIEVAL.md) gives the current NARPS payload route and commands for a selected experiment.

The intended result is transferable guidance: an independent agent can use these skills with a researcher's own data and hypothesis to produce scientifically useful, rigorous and convenient research.
The products are improved shareable skills, evidence about their impact, and a STAMPED research object documenting the whole workshop.
Figures summarize scientific outcomes, reproducibility, effort and variability.

NARPS is the first formal study.
The tested source and preparation evidence are linked in [`source-version.json`](source-version.json); formal trials and skill iterations are recorded here.

The [completed NARPS development comparison](https://github.com/leej3/stamped-in-practice/blob/851f3905ab26d0a9ac6deb7c52f85bd085cc54ff/DATASET.md) contains twelve research workers, sixteen assigned judgments, figures and the resulting skill reflection.
Its workflow mandates and assessment changes are disclosed.
The [sealed tool-neutral comparison](https://github.com/leej3/stamped-in-practice/blob/5056bebf6eb33c2b9b02262efc39d084259424ce/registration.md) fixes 72 new workers and 96 judgments.
The [first tool-neutral round](https://github.com/leej3/stamped-in-practice/blob/20917d21f5c698152b032ecff37374ab4e603a82/rounds/round-01/synthesis/README.md) completed 24 research workers and 32 assigned judgments.
Only 21 judgments passed the frozen measurement gate; 11 were excluded because assessment changed annex database metadata.
The linked findings and figures preserve those missing measurements and explain why a separate assessment boundary is needed before further research.
The [latest online status](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/STATUS.md) may be newer than the iteration pinned in this checkout.
