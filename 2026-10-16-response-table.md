| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files` | The study inputs, code, environment, run logs, and results sit under one repository root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/neurovault-all-maps-attempt-2/retrieval-manifest.json` | All 54 source map URLs returned manifest-matching bytes and SHA-256; code reads the in-root input/data paths. |
| must/003 | S.1 | met | judgement | `pixi.toml` | Analysis libraries are declared in pixi.toml; the atlas cache is included in results/. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git status --short --branch` | Git tracks the code and documentation, and the assessed worker stop was clean. |
| must/005 | T.1,T.3,T.5 | met | probe:large-annex | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-probes.json` | Git-annex tracks the large map and atlas payloads; no large binary is a Git blob. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `logs/group-analysis-releaseinfo.json` | The release log records command and host, but no lock or exact environment pin links outputs to a full environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `results/report.md` | No README or Makefile gives installation and usage; results/report.md has only a reproduction command. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md` | The documented Pixi command starts scripts/group_analysis.py and is recorded in the release log. |
| must/009 | P.1 | met | probe:no-abs-paths | `scripts/group_analysis.py` | Tracked analysis code uses paths relative to its repository root. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Analysis imports are declared in pixi.toml, but the documented pixi run also assumes Pixi is installed on the host. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Pixi lists macOS and Linux targets, but host Pixi installation and network access for atlas retrieval are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Package dependencies and target platforms are listed, but Pixi setup and host requirements are not. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is tracked with the analysis code and data. |
| must/014 | P.3 | unmet | judgement | `pixi.toml` | No dependency update or lock regeneration process is declared in the environment specification or report. |
| must/015 | D.1 | unmet | judgement | `pixi.toml` | pixi.toml uses broad version ranges and no pixi.lock pins the resolved environment. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/target-ref-verification.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/remote-check/neurovault-all-maps-attempt-2/retrieval-manifest.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The worker stop and remote branch share this commit; all 54 maps fetch, but annexed results and atlas payloads failed fresh-clone retrieval. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md` | The report gives a Pixi command, but omits how to install Pixi and obtain a pinned environment. |
| should/001 | T.2 | met | judgement | `.gitattributes` | Git and git-annex track the code, maps, cached atlas, and results within one dataset. |
| should/002 | A.2 | unmet | probe:ci-present | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-probes.json` | No CI configuration checks the workflow or keeps its instructions accurate. |
| should/003 | M.1 | met | probe:modules-separated | `input` | Inputs, analysis code, results, and environment specification occupy distinct paths. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The fresh clone could not retrieve annex payloads, so the analysis entrypoint never ran. |
| should/005 | E.1 | unmet | judgement | `results/report.md` | The documented Pixi environment is reused on the host; no disposable container or job environment is declared. |
| should/006 | D.2 | unmet | probe:ci-present | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-07/judgment-01/judgment/2026-10-16-probes.json` | No CI rebuilds and tests the environment used for the results. |
| should/007 | D.2 | unmet | judgement | `pixi.toml` | The object contains specifications and atlas cache files, but no archived executable environment or package image. |
| should/008 | D.2 | unmet | judgement | `pixi.toml` | No process for updating dependencies is declared or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: supplied data and declared software are public; no restricted component is present. |
| may/001 | M.2 | unmet | judgement | `input/data` | The external dataset is annexed within this repository, not linked as a submodule. |
| may/002 | M.2 | partial | judgement | `results/report.md` | Directories separate inputs, code, results, and environment, but recombination is not documented. |
| may/003 | M.2 | partial | judgement | `scripts/group_analysis.py` | Inputs and code are separable by path, but the script expects fixed filenames and results layout. |
| may/004 | M.2 | unmet | judgement | `results/report.md` | The object has no module composition mechanism; the workflow is a single repository command. |
| may/005 | M.2 | partial | judgement | `results/report.md` | The report links the analysis and key outputs, but no root README explains repository navigation. |
