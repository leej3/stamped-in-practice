# From the poster to the evidence

[Project overview](../README.md) · [Results and interpretation](results.md) · [Repository map](repository-map.md)

The poster presents a study of research guidance: fresh agents tackle the same neuroscience question, independent assessments inspect their work, and the guidance is revised between rounds.
It combines examples of the scientific analyses with summaries of the agents' scientific and reproducibility outcomes.
These are different views of the same research object, with different denominators and limitations.

## Read or edit the poster

The [poster introduction and download instructions](https://github.com/con/talks/blob/codex/stamped-example-poster/2026-usrse/stamped-ai-study/README.md) are in `con/talks`, the repository used for presentations.
The `codex/stamped-example-poster` branch contains the editable HTML/CSS, figure display copies and exported PDF.
It is a poster development branch, separate from this repository's research records.
Follow that page's current download status: an annex pointer shown by GitHub is not itself a PDF, and a locally rebuilt export may not yet have been uploaded.

## Follow a poster element

| Poster element | Begin here | What the destination contains |
| --- | --- | --- |
| Scientific question and input data | [NARPS study introduction](https://github.com/leej3/stamped-in-practice/blob/codex/study-narps/README.md) | The task, participant maps, source information and input retrieval instructions |
| Research loop and skill bundle | [Skills guide](skills.md) | An explanation of the research workflows, assessor and tested revisions |
| Outcome table and progression graph | [Results guide](results.md) | Definitions of scientific adequacy, replay and checklist attainment, followed by round-level evidence |
| Brain map and spatial agreement figure | [Scientific figure guide](https://github.com/leej3/stamped-in-practice/blob/codex/stamped-poster-analysis/experiments/narps-poster/README.md) | What the figures measure, their source deliveries and how to rebuild them |
| Assessment and revision lessons | [Methodological lessons](../LESSONS.md) | Lessons about assessment design, coordination, model capability, dependencies and infrastructure support |
| Original research objects | [Repository map: read a run](repository-map.md#read-a-run-in-context) | How to find an agent's delivered report, code, results and subsequent assessment |

## Interpret the scientific figures

The example brain map comes from **round two, run nine**.
It illustrates one agent's analysis of the supplied participant maps, rather than a new analysis performed for the poster.
The [figure guide](https://github.com/leej3/stamped-in-practice/blob/codex/stamped-poster-analysis/experiments/narps-poster/README.md) leads to that delivery's report, code and numerical results.

The spatial agreement figure summarizes **48 deliveries from rounds two and three**, or 12 per condition.
Color shows the fraction reporting a positive whole-brain corrected finding within their shared tested coverage.
Agents retained their own analysis methods, so variation reflects the delivered analyses rather than a standardized reanalysis.
The outcome table and progression chart instead summarize judgments across **all three rounds**, with unavailable records excluded and denominators retained.

## Why the figure links open another branch

The `codex/stamped-poster-analysis` branch holds derived reporting tables, plotting code and selected copies from original deliveries.
This separates later presentation work from what research workers originally produced.
It does not mean that the entire branch should be merged into every study or experiment.
The figure manifests identify the exact sources; copies used in `con/talks` are presentation artifacts, not additional research runs.
For exact source hashes and reproduction commands, continue to the figure guide after reading these explanations.
