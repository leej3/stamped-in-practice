# Independent assessment — paired assay teaching study

**Assumption and kind.** I treated this as a study: a small analysis that uses supplied synthetic pairs to answer a stated question and deliver code, results, and interpretation. The documentation states that goal in `README.md`, `protocol.md`, and `input/study-task.md`. No human guidance was attached, so the assumption was not confirmed.

**Overall STAMPED findings.** MUST: 10 met, 2 partial, 4 unmet, 1 not-applicable, 0 not-checked (17 items). SHOULD: 1 met, 2 partial, 3 unmet, 2 not-checked, 1 not-applicable (9 items). MAY: 3 met, 1 partial, 1 not-applicable (5 items). A partial MUST is not satisfied. No overall score is assigned.

**Capture and attribution.** The canonical original delivery is capture SHA-256 `5a695edf17e525c1cdbfa1767bcee2e1356c4df20bc2df27b3f5c57536c5a6b5`, workspace `content/workspace`, original captured HEAD `20171384fc05892008d889ed7440d7646eef6c5b`, captured 2026-10-16 09:47:52 UTC. The worker stop receipt (`worker-end-state.json`, SHA-256 `ad9850bf0f532c0ea5a56f913674f16028128f57a2941b2c0c85f480e89d2b63`) records a complete stop with no omissions and the same HEAD. The scientific artifacts, code, documentation, and `requirements.txt` exist in the complete stop state, but are untracked; the commit alone is not the delivery. The worker's versioning, provenance, environment publication, and sharing receive no credit from coordinator preservation or this assessment's replay.

All target citations below are capture-relative paths under `content/workspace`; each refers to the canonical capture SHA stated above. An intermediate operational-manifest audit found 194 of 196 expected entries because `.git/annex/keysdb/db-shm` and `db-wal` were absent; these regular-file sidecars are in the expressly permitted operational-metadata class. On the final audit both sidecars were present again and all 196 expected entries matched, with no extra or integrity-invalidating paths (`operational-integrity.json` and the retained intermediate audit log). This change is an inspection-copy observation, not worker evidence, and does not establish logical database equivalence. The frozen launcher also verified the target against its manifest before and after assessment.

The project boundary contains the analysis and its local annex input payload. The retained outside-workspace skill symlinks named in `judge-target.json`'s `reference_limits` were not followed; they are coordinator-supplied observation resources, not evidence about the worker's research practice. The delivered ignored `.codex/` and `.entire/` session-metadata paths indicate assistant tooling was present. I did not inspect their interaction contents or use them as grading evidence; this is the observed assistance exposure.

**Scientific adequacy — supported.** The complete twelve-row CSV was read from the operational copy, whose scientific bytes match the canonical capture under the integrity audit. An independent calculation of all twelve after-minus-before differences gives mean 0.4167 units, SE 0.1086, 95% t interval [0.1777, 0.6557], *t*(11) = 3.8369, two-sided *p* = 0.002761, and range [-0.3, 0.9]. These agree with `results/summary.json` and `results/report.md`. The paired direction, paired uncertainty, two-sided test, interval, all-sample count, and individual-difference figure are correct. The report discusses matching, independence, the t-model assumption, small-sample uncertainty, and explicitly limits interpretation to synthetic pairs; it makes no causal or real-assay claim. This supports the reported inference for these synthetic pairs under its stated assumptions, not a broader biological claim.

**Reported hypothesis outcome (kept separate from adequacy):** “The two-sided paired t test of a zero mean change gave *t*(11) = 3.837, *p* = 0.0028.” This is the result statement in the delivered `results/report.md`; adequacy does not determine or replace it.

**Replay.** Before replay, `replay-plan.md` declared the exact command, prerequisites, generated outputs, and comparisons. The frozen helper made one new writable copy from the complete canonical capture; the inspection copy was not replayed. It used the README's documented Python 3.13 virtual-environment and `requirements.txt` installation steps, then `python analysis/run_analysis.py`. Selected outputs were exactly `results/paired-differences.csv`, `results/summary.json`, `results/report.md`, and `figures/paired-changes.png`; no broad deletion pattern was used. All four regenerated outputs were byte-identical to the shipped outputs, so the numeric table, summary, prose, and figure matched exactly (stricter than the declared `rtol=1e-6` table tolerance). The run took about 25.5 seconds and exited 0. It used captured inputs without adapter prefetch; the 5 GB compatibility parameter did not meter dependency downloads. The entrypoint's install step can download packages and those bytes were not metered. This replay supports computational repeatability, not scientific validity or worker environment-publication credit. See `2026-10-16-fresh-rerun.json`, `replay-copy/replay.stdout`, and `replay-copy/replay.stderr`.

**Access and publication.** The intended recipient is a researcher authorized to use the worker-declared route. No worker retrieval route is declared, and captured `.git/config` has no remote. The delivered report says to run from the received directory but does not say how to obtain it. Required coverage is the complete workspace, including the annex payload, code, pinned package list, generated table/summary/report/figure, and setup documentation. No route could be tested; only local inspection and replay on the assessor host were tested. Coordinator delivery to the assessor does not establish worker access. The detailed `access-record.json` records this limitation.

**Probe and process notes.** The frozen probes are retained in `2026-10-16-probes.json`. They inspect tracked Git paths, while most scientific artifacts were untracked; I inspected those artifacts and overrode probe findings where the complete delivery supported a different conclusion (notably the entrypoint and delivered dependency specification). A first probe invocation mistakenly used unsupported `--path` syntax and returned usage without running; the positional-path retry succeeded. This was an assessor invocation error, not target behavior. The target was not repaired. Retained external links were not resolved and no undeclared retrieval route was contacted.

**Checklist verdicts.** Evidence URIs in the response JSON include the canonical capture digest and capture-relative path; the table shows the paths for readability.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md` | All project materials and the annex payload sit within the delivered workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/paired-assay.csv` | The CSV is an internal relative annex link and its payload is inside the common root. |
| must/003 | S.1 | met | judgement | `requirements.txt` | requirements.txt declares the external Python packages used by the analysis. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `README.md` | The worker stopped with the report, code, outputs, and environment file uncommitted. |
| must/005 | T.1,T.3,T.5 | not-applicable | probe:large-in-annex+judgement | `.git/annex/objects/fJ/0P/SHA256E-s167--7cfc112a3d6a3922c347695e62bdb9ad2b92c0265c7bb18c7fd50eed2763050b.csv/SHA256E-s167--7cfc112a3d6a3922c347695e62bdb9ad2b92c0265c7bb18c7fd50eed2763050b.csv` | N/A: the supplied CSV and generated figures are small; no large binary data is present. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `results/summary.json` | summary.json records input hash and package versions, but no code identity or complete run record links the actions to the exact environment. |
| must/007 | A.1 | met | probe:entry-point+judgement | `README.md` | README documents Python setup, installation, and usage. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/run_analysis.py` | analysis/run_analysis.py is a clear executable starting point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis/run_analysis.py` | The analysis uses relative input and output paths, with CLI overrides. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `requirements.txt` | All direct nonstandard imports are pinned in the delivered requirements file. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `README.md` | README states Python 3.13 and gives the POSIX shell activation and run commands; no additional host service or hardware is needed. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `README.md` | README and requirements.txt list Python and package prerequisites. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `requirements.txt` | requirements.txt is part of the stopped delivery but was not tracked at worker stop. |
| must/014 | P.3 | unmet | judgement | `README.md` | No command or policy for updating dependency specifications is documented. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `requirements.txt` | Direct package versions are pinned and recorded, but transitive resolution and an exact Python patch/platform environment are not frozen. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config` | No worker-declared authorized retrieval route or Git remote makes the environment specification accessible to intended recipients. |
| must/017 | D.1 | met | judgement | `README.md` | README explains how to obtain packages and run the analysis from the delivered directory. |
| should/001 | T.2 | partial | judgement | `.git/index` | Git contains the supplied inputs, but the worker code, report, outputs, and requirements remain untracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `validation/replay.md` | A replay is documented, but the delivery does not establish a recurring testing cadence. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input` | Input, code, and generated results have distinct directories; requirements.txt remains at the project root. |
| should/004 | E.1 | met | judgement | `../replay-record.json` | A fresh copied delivery and new virtual environment reproduced every selected output exactly. |
| should/005 | E.1 | unmet | judgement | `README.md` | The documented workflow creates a persistent .venv for reuse rather than a disposable environment per run. |
| should/006 | D.2 | not-checked | probe:ci-present+judgement | `validation/replay.md` | The delivered replay evidence and this successful replay are isolated checks, but no regular cadence is established. |
| should/007 | D.2 | unmet | judgement | `requirements.txt` | No package archive, executable environment, or container image is retained with the project. |
| should/008 | D.2 | unmet | judgement | `requirements.txt` | No environment update process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: this synthetic teaching project contains no restricted data or software. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `README.md` | N/A: this study has no independently maintained project components; Python packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `README.md` | README and protocol describe the input, analysis, outputs, and how they connect. |
| may/003 | M.2 | partial | judgement | `protocol.md` | Directories give basic boundaries, but no interface or policy promises independent component updates. |
| may/004 | M.2 | met | judgement | `analysis/run_analysis.py` | The analysis script composes the input data with the computation and writes the declared outputs. |
| may/005 | M.2 | met | judgement | `README.md` | README and protocol provide navigation and explain the project layout. |

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md` | All project materials and the annex payload sit within the delivered workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/paired-assay.csv` | The CSV is an internal relative annex link and its payload is inside the common root. |
| must/003 | S.1 | met | judgement | `requirements.txt` | requirements.txt declares the external Python packages used by the analysis. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `README.md` | The worker stopped with the report, code, outputs, and environment file uncommitted. |
| must/005 | T.1,T.3,T.5 | not-applicable | probe:large-in-annex+judgement | `.git/annex/objects/fJ/0P/SHA256E-s167--7cfc112a3d6a3922c347695e62bdb9ad2b92c0265c7bb18c7fd50eed2763050b.csv/SHA256E-s167--7cfc112a3d6a3922c347695e62bdb9ad2b92c0265c7bb18c7fd50eed2763050b.csv` | N/A: the supplied CSV and generated figures are small; no large binary data is present. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `results/summary.json` | summary.json records input hash and package versions, but no code identity or complete run record links the actions to the exact environment. |
| must/007 | A.1 | met | probe:entry-point+judgement | `README.md` | README documents Python setup, installation, and usage. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/run_analysis.py` | analysis/run_analysis.py is a clear executable starting point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis/run_analysis.py` | The analysis uses relative input and output paths, with CLI overrides. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `requirements.txt` | All direct nonstandard imports are pinned in the delivered requirements file. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `README.md` | README states Python 3.13 and gives the POSIX shell activation and run commands; no additional host service or hardware is needed. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `README.md` | README and requirements.txt list Python and package prerequisites. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `requirements.txt` | requirements.txt is part of the stopped delivery but was not tracked at worker stop. |
| must/014 | P.3 | unmet | judgement | `README.md` | No command or policy for updating dependency specifications is documented. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `requirements.txt` | Direct package versions are pinned and recorded, but transitive resolution and an exact Python patch/platform environment are not frozen. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config` | No worker-declared authorized retrieval route or Git remote makes the environment specification accessible to intended recipients. |
| must/017 | D.1 | met | judgement | `README.md` | README explains how to obtain packages and run the analysis from the delivered directory. |
| should/001 | T.2 | partial | judgement | `.git/index` | Git contains the supplied inputs, but the worker code, report, outputs, and requirements remain untracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `validation/replay.md` | A replay is documented, but the delivery does not establish a recurring testing cadence. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input` | Input, code, and generated results have distinct directories; requirements.txt remains at the project root. |
| should/004 | E.1 | met | judgement | `../replay-record.json` | A fresh copied delivery and new virtual environment reproduced every selected output exactly. |
| should/005 | E.1 | unmet | judgement | `README.md` | The documented workflow creates a persistent .venv for reuse rather than a disposable environment per run. |
| should/006 | D.2 | not-checked | probe:ci-present+judgement | `validation/replay.md` | The delivered replay evidence and this successful replay are isolated checks, but no regular cadence is established. |
| should/007 | D.2 | unmet | judgement | `requirements.txt` | No package archive, executable environment, or container image is retained with the project. |
| should/008 | D.2 | unmet | judgement | `requirements.txt` | No environment update process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: this synthetic teaching project contains no restricted data or software. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `README.md` | N/A: this study has no independently maintained project components; Python packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `README.md` | README and protocol describe the input, analysis, outputs, and how they connect. |
| may/003 | M.2 | partial | judgement | `protocol.md` | Directories give basic boundaries, but no interface or policy promises independent component updates. |
| may/004 | M.2 | met | judgement | `analysis/run_analysis.py` | The analysis script composes the input data with the computation and writes the declared outputs. |
| may/005 | M.2 | met | judgement | `README.md` | README and protocol provide navigation and explain the project layout. |

**Extra finding (outside the checklist).** No license or reuse terms are declared in the complete captured workspace; see `README.md` and the canonical inventory.

**Flagged items.** `must/002`, `must/005`–`must/008`, `must/010`–`must/012`, `must/015`, `should/003`, and `may/001` carry `probe-overridden`: the probes assessed tracked paths or recognized mechanisms, and the complete delivery and documented route supplied additional or contrary evidence. `must/014` and `should/008` carry `upstream-duplicate` because the checklist repeats the environment-update question.

**Not checked.** `should/002` and `should/006` remain not-checked: the delivery records a replay but does not establish recurring workflow or environment reconstitution cadence. A retained sequence or schedule of repeated tests would settle them.

**Goals and emphasis.** The documented goal is to estimate the mean paired change in twelve synthetic pairs, report a 95% confidence interval and two-sided paired t test, show individual changes, explain assumptions and limits, and preserve executable code and a concise colleague-facing report. The study kind puts emphasis on self-contained inputs and results linked to actions and environments.

**Checklist link and assessor stamp.** [Open the completed checklist app response](2026-10-16-url.txt). The canonical machine-readable answers are in [2026-10-16-response.json](2026-10-16-response.json); probe evidence is [2026-10-16-probes.json](2026-10-16-probes.json). Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), using the frozen assessment runner/runtime pinned by `assessment-version.json`, on the complete capture SHA-256 `5a695edf17e525c1cdbfa1767bcee2e1356c4df20bc2df27b3f5c57536c5a6b5`, commit `20171384fc05892008d889ed7440d7646eef6c5b`, 2026-10-16. The harness did not provide model identity.


The structured scientific classification and verbatim excerpts are recorded in [scientific-judgment.json](scientific-judgment.json). Command and artifact records are indexed in [commands/attempt-index.md](commands/attempt-index.md).
