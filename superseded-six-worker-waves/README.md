# Prospective comparison draft

Read [registration.md](registration.md) for the complete design and [remaining-decisions.md](remaining-decisions.md) for the execution identities and implementation still needed before sealing.
No workers have been launched by this draft.

- [worker-common.md](worker-common.md) preserves the original scientific task verbatim and adds only neutral resource/workspace instructions.
  Append exactly the assigned additional prompt from [conditions.json](conditions.json).
- [common-resources.template.md](common-resources.template.md) must be filled with verified resource facts identically for every strategy; it is not ready to send as written.
- [judge-common.md](judge-common.md) and the unchanged [scientific-judging.md](scientific-judging.md) define the common independent judgment.
- [allocation.json](allocation.json) fixes all 72 workers and 96 assigned judgments, including duplicate selection and balanced waves, using [prepare_draft.py](prepare_draft.py) and its retained seed.
  This is a proposed allocation until sealed, with no outcome-based reselection.
- [input-manifest.json](input-manifest.json) records the original 58 input paths, Git blobs, annex identities and SHA256 values.
  Available local bytes matched; unmaterialized paths are explicitly unchecked.
  This is not execution-host readiness evidence.
- [source-manifest.json](source-manifest.json) records the exact existing design sources consulted.
  Completed round-one outcomes appear only as design limitations in the registration, not in worker instructions.

The settled sample is six workers per strategy per round across three rounds, with two independently duplicated judgments per cell.
The final round is untuned.
No overall spending cap or score-dependent extension is proposed.
