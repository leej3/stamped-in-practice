# Evidence and retrieval for the development trial

This registered DataLad dataset contains the completed twelve-worker, sixteen-assessment development comparison and its retained supplementary repair attempt.
Read the [findings and figures](replay/RESULTS.md); the [original registration](historical-registration.md), [frozen procedure](procedure.json) and [historical synthesis](synthesis/README.md) remain unchanged.

The [skill-development record](skill-reflection/README.md) links the revised research guidance, independently versioned assessor and their closed followability trials.
[Migration verification](migration/VERIFICATION.md) retains independent reconstruction and selective retrieval proofs.

The prefix history was split from coordinator commit `ffc236c5ad2946d93a2de327ec6833f800c3f7ac`.
The original complete coordinator history remains at `codex/narps-v1-before-migration` in `git@github.com:leej3/stamped-in-practice.git`.
[The complete path manifest](migration/original-manifest.json) identifies every original Git blob and annex key; payload bytes are unchanged.
Only annex link depth changes in the original files.
New local navigation and replay indexes adapt references without rewriting frozen records or raw judgments.

`study/` pins the existing study dataset and its twelve experiment gitlinks; `assessment/` pins the exact assessment source used by the amended round-one procedure.
Both remain uninitialized until selected.
Scientific objects and their large archives are reused by revision and content key, never copied into this dataset.
Historical references beginning `../../../studies/` describe the old coordinator layout; current `replay/` indexes and links use the local `study/` pin.

For a lean checkout, clone this branch or initialize only this iteration in its parent without `--recursive`.
Retrieve selected figures with `datalad get synthesis/figures/`; retrieving all top-level dataset content does not require installing every experiment.
Use the configured authorized annex route; successful same-host access does not establish public or cross-host portability.

To aggregate the retained evidence, initialize `study` and `assessment`, then the twelve selected `study/results/narps-r1-*` gitlinks.
Retrieve the files cited by `replay/index.json` and `replay/disposition.json`, mainly `coordinator/retention-01/indexable/` in each result.
The optional full preservation archives are not needed for aggregation.
Fetch original assessor commit `0208f825` by its full identity in `procedure.json` if a shallow assessor clone lacks it; the validator checks the unchanged response contract across assessment versions.

Copy `synthesis/analysis/validated-environment.lock` to ignored `synthesis/analysis/pixi.lock`, then use the retained Pixi manifest and analysis scripts.
Run the aggregation with `--allocation allocation.json --index replay/index.json --disposition replay/disposition.json --assessor assessment --assessment-pin synthesis/analysis/assessment-version.json --assessment-procedure-sha256 5dfdfa07f8e9488a79bbddb27df75a76ad5484941ac1d0efb197b0b3126994b5 --output NEW_DIRECTORY`.
Run `synthesis/analysis/round1_figures.py` with those tables, `replay/reported-scientific-estimates.json` and another new output directory.
This reproduces the comparison and figures, not the twelve scientific analyses or judgments.

Future protocol and skill changes are prospective and are not pooled with this round as a clean skill effect.
