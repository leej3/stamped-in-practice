| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files`, `remote-retrieval/get` | All required files are under the repository root; annex payloads resolve through the documented remote. |
| must/002 | S.1 | met | judgement | `scripts/analyze.py`, `input/sources.json` | All 54 maps and cohort metadata are included under input/; sources.json preserves original provenance links. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `scripts/analyze.py` | Analysis libraries and TemplateFlow are declared in pixi.toml; nibabel is a Nilearn dependency. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/worker-end-state.json` | Git tracks the committed analysis and the worker-stop receipt records a clean tree at this commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `.datalad/config` | Large maps use Git-annex pointers rather than Git blobs. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `logs/final-analysis-releaseinfo.json`, `pixi.toml` | Run logs record command and exit status, but no exact lock or environment hash links results to a pinned environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `git ls-files` | No README or Makefile provides installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md#Reproducibility`, `scripts/analyze.py` | The report names the runnable script and exact pixi command; scripts/analyze.py is the analysis entry point. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/analyze.py` | The analysis resolves inputs and outputs relative to its own repository root. |
| must/010 | P.1 | met | judgement | `scripts/analyze.py`, `pixi.toml` | Imports are covered by pixi.toml directly or through declared Nilearn dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md#Reproducibility` | Pixi platform targets are stated, but Pixi installation and TemplateFlow network access are undocumented host prerequisites. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `scripts/analyze.py` | Package requirements are listed, but the host Pixi bootstrap and required network access are not documented. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is version-controlled with the analysis. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No environment lock/update command or dependency-update history establishes a repeatable update process. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `git ls-files pixi.lock` | pixi.toml is shared, but wildcard versions and the absence of pixi.lock do not freeze the environment. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `remote-retrieval/remote-get.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-02/judgment-01/worker-end-state.json` | The hub currently serves the exact commit and all annex payloads, but the receipt cannot attribute annex publication to the worker stop. |
| must/017 | D.1 | unmet | judgement | `results/report.md#Reproducibility`, `pixi.toml` | The report gives a command but does not explain how to install or obtain the environment specification. |
| should/001 | T.2 | met | judgement | `git ls-files`, `results/group_mean_gain_effect.nii.gz` | Git versions text and code while Git-annex tracks large binary content within the same repository. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | There is no CI configuration that checks the documented workflow. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, analysis code, results and environment specification occupy distinct paths. |
| should/004 | E.1 | not-checked | probe:fresh-rerun+judgement | `2026-10-16-fresh-rerun.json` | The only replay attempt was invalidated when the runner deleted input/participants.tsv before execution; no retry was authorized. |
| should/005 | E.1 | unmet | judgement | `results/report.md#Reproducibility` | pixi run reuses the project environment; no disposable environment is created per execution. |
| should/006 | D.2 | unmet | probe:ci-present | `pixi.toml` | No locked environment or CI job regularly tests environment reconstitution. |
| should/007 | D.2 | unmet | judgement | `git ls-files`, `pixi.toml` | The environment is described by package declarations only; no environment artifacts are archived. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No environment update command is declared and no update instance appears in history. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the object contains no restricted data or software component; the supplied maps are publicly retrievable. |
| may/001 | M.2 | unmet | judgement | `.gitmodules`, `input/data and pixi.toml` | No external data or software is included through submodules; maps use annex and packages use Pixi. |
| may/002 | M.2 | unmet | judgement | `results/report.md` | Directories separate inputs, code and results, but no document explains modular composition. |
| may/003 | M.2 | unmet | judgement | `scripts/analyze.py` | All components share one repository and the script assumes fixed paths; boundaries are not independently versioned. |
| may/004 | M.2 | unmet | judgement | `scripts/analyze.py` | No module composition mechanism is provided beyond the single analysis script. |
| may/005 | M.2 | partial | judgement | `results/report.md`, `No top-level README or module map is tracked.` | The results report links figures and names the analysis command, but gives no guide to the input/code/environment boundaries. |
