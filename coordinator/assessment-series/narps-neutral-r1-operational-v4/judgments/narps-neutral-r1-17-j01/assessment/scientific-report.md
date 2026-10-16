# Independent assessment: NARPS potential gain and vmPFC

## Verdict

MUST: 5 met / 2 partial / 10 unmet / 0 not-checked / 0 not-applicable (17 total).

SHOULD: 0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total).

MAY: 2 met / 3 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total).

## Fix first

1. Add a portable, pinned environment specification and a provenance record linking the exact environment and command to outputs → the analysis currently depends on a host-specific interpreter path and package versions listed only in prose → must/006, 010–017; should/006–008.
2. Track the analysis code, report, protocol, figures and generated results at the worker stop → these are the core scientific deliverables, but they were untracked in the captured state → must/004; should/001.
3. Publish a researcher-accessible route covering the complete project and document how to obtain the environment → the captured repository has no configured Git remote; the input-source URLs cover only source data → must/016–017.
4. Replace the absolute interpreter path in user instructions with a project-relative setup/run procedure → the current command cannot be assumed to work on another host → must/007, 009, 011–012.
5. Add a recurring clean-host workflow check → the worker recorded a same-environment rerun, while this assessment's separate-copy replay is evaluator evidence, not worker practice → should/002, 004–006.

## What is already done well

- The scientific analysis is transparent and unusually well specified: it uses the full 54-person cohort, checks hashes and spatial geometry, defines common support, and performs positive one-sided max-t sign-flip inference over the whole analysis mask. The vmPFC sphere is defined independently and the ROI result is kept descriptive. (Capture citation: `content/workspace/protocol.md`, `content/workspace/analysis/group_analysis.py`, `content/workspace/results/summary.json`.)
- The report correctly interprets the negative vmPFC estimate as no support for the hypothesized positive response, not proof of a zero effect; it explains normalized-regressor units and missing first-level variance maps. The figures, QC table, code and machine-readable summary are present in the stop-state delivery. (Capture citation: `content/workspace/report/analysis-report.md`, `content/workspace/figures/`, `content/workspace/results/`.)
- Large inputs were annexed and materialized in the captured workspace, and the worker recorded checksums and a replay history. The frozen assessment replay on a separate complete copy also recreated all 12 declared outputs byte-for-byte. The latter is assessor measurement, not worker-practice credit. (Capture citation: `content/workspace/.git/annex/`, `content/workspace/input/sources.json`, `content/workspace/results/run_history.md`; evaluator record: `replay/replay.json`.)

## Scientific judgment

**Scientific adequacy: supported.** The supplied analysis provides a defensible test of the positive vmPFC hypothesis using the supplied fixed upstream maps. It uses the independent participant as the sampling unit; verifies all 54 source-listed maps, metadata joins, finite values, shared image shape and affine; and restricts inference to finite nonzero common coverage so zero-filled outside-mask voxels are not treated as observations. The group mean is tested with a one-sided sign-flip max-t procedure over 198,029 voxels, which addresses the required whole-brain correction. Its sign-exchangeability assumption is stated, the seed and plus-one p-value are recorded, and a SciPy check supports the statistic implementation. The 5 mm MNI sphere at [2, 46, -8] is an explicit independent anatomical proxy rather than a post hoc peak; the report does not use its uncorrected p-value as the primary decision.

The reported outcome is no support for a greater vmPFC response: the sphere mean is −0.012 upstream normalized-regressor units, its 95% t interval includes zero, and there is no positive whole-brain corrected discovery inside the sphere. Positive corrected voxels occur posteriorly, not in the defined vmPFC region. This is a careful absence-of-support conclusion, not a claim of no effect. The analysis also properly limits interpretation because coefficients are not per-currency-unit slopes, gain and loss were modeled separately upstream, and first-level variance maps are unavailable. The result is conditional on AO86's supplied participant models and on the sign-flip assumptions; it does not test gain against loss or establish causality.

**Scientific conclusion:** “The supplied group maps do not support a greater vmPFC response with increasing potential gain.” This is the report's conclusion, retained separately from the adequacy label.

## Replay measurement

Before replay, I declared the README entrypoint, worker-documented interpreter, captured input prerequisites, 12 generated outputs, and the frozen numeric tolerance of 1e-6. The helper made a new writable copy from the canonical complete delivery, removed only those listed outputs, disabled hooks through its replay-only environment overlay, and did not retrieve inputs. The command returned 0 in 24.0 seconds; all 12 outputs matched byte-for-byte, so no numerical tolerance was needed. This confirms replay on the assessor host with the documented interpreter path available; it does not establish clean installation on a different host. Full command, stdout/stderr and result are retained in `commands/replay.*` and `replay/`.

## Worker stop state, delivery and access

The canonical original delivery SHA-256 is `5dd86ac67e52dd77cb1d69b913060eb4c644b88d9dcf50d577a18967fee0fc22`; its captured HEAD is `e929d623d8de313d2ecdd97911ea8487077af580`. The worker stop receipt records a completed capture, exit status 0, no omissions and no capture errors. The operational manifest initially has the same capture identity. All original-evidence citations below are relative to `content/workspace/` within that canonical capture.

At worker stop, `README.md`, `protocol.md`, `analysis/`, `figures/`, `report/`, `resources/` and `results/` were untracked; `.codex/` and `.entire/` were ignored. The captured HEAD contains the supplied study/input commit, not the untracked scientific deliverables. I credit annex use for large inputs but do not credit untracked scientific material as version controlled. The worker did record software versions and a same-environment replay in prose/history, but supplied no tracked environment lock/specification or environment-linked run record. The report/README point to an absolute shared-host Python path. There is no configured worker Git remote in the captured `.git/config`.

**Access record:** intended recipient: a researcher using a route authorized for that recipient. Worker-declared project route: none found (no configured remote and no repository URL in the README). The declared NeuroVault/OpenNeuro source URLs identify input data and metadata only; they do not cover the analysis code, protocol, report, results, figures or execution environment. No full-project route was therefore available to test. Tested host scope: local assessor host, by inspecting the captured workspace and local Git configuration; this does not demonstrate recipient access from another host. The evaluator's delivery of this copy is not worker publication evidence. Access details are also in `access-record.json`.

## Per-item checklist

The citations in this table refer to the canonical capture SHA above; paths are capture-relative under `content/workspace/`. Probe output is preserved at `probes.json`.

| Item | Principles | Verdict | Evidence and reason |
|---|---|---|---|
| must/001 | S.1 | met | `README.md`, `input/`, `analysis/`, `report/`, `results/`: the workspace is a single rooted project. |
| must/002 | S.1 | met | `analysis/group_analysis.py`, `input/data/`, `input/participants.tsv`: supplied inputs are reachable from the script within the root. |
| must/003 | S.1 | unmet | `README.md`, `resources/nilearn/`: the documented Python environment is outside the root and no external software is included as a submodule. |
| must/004 | T.1,T.3,T.5 | unmet | Captured Git status: `README.md`, `analysis/`, `protocol.md`, `report/`, `figures/` and `results/` are untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | `.git/annex/` and `input/data/`: large maps use git-annex and are materialized in the captured copy. |
| must/006 | T.1,T.3,T.5 | unmet | `results/summary.json`, `results/run_history.md`: versions and a run history are recorded, but no exact environment specification is linked to this result set. |
| must/007 | A.1 | partial | `README.md`: a run command is present, but installation and portable usage instructions are absent; it uses a host-specific interpreter path. |
| must/008 | A.1 | met | `README.md`, `analysis/group_analysis.py`: the README names a clear executable starting point. |
| must/009 | P.1 | met | `analysis/group_analysis.py`: data and output paths are formed relative to the script root. |
| must/010 | P.1 | unmet | `README.md`, `report/analysis-report.md`: packages are named/versioned in prose, but no complete dependency specification is supplied. |
| must/011 | P.1 | unmet | `README.md`, `protocol.md`: no portable host/system configuration requirements are documented. |
| must/012 | P.1 | partial | `report/analysis-report.md`: Python package versions are listed, but system requirements and installation steps are missing. |
| must/013 | P.3 | unmet | Captured root file listing: no worker-tracked environment specification accompanies the analysis. |
| must/014 | P.3 | unmet | `README.md`, `protocol.md`: no process for updating/tracking dependency specifications is documented. |
| must/015 | D.1 | unmet | `results/summary.json`: runtime versions are recorded, but there is no frozen manifest/container identity for exact reconstitution. |
| must/016 | D.1 | unmet | `.git/config`, `README.md`: no worker-published environment artifact or project remote is declared. |
| must/017 | D.1 | unmet | `README.md`: the absolute interpreter path is not an instruction for obtaining a reusable environment specification. |
| should/001 | T.2 | partial | `.git/`, `.git/annex/`, captured status: one Git repository stores inputs, but key scientific materials were untracked at worker stop. |
| should/002 | A.2 | unmet | `results/run_history.md`: a same-environment rerun is recorded, but there is no recurring or automated workflow test. |
| should/003 | M.1 | partial | `input/`, `analysis/`, `results/`, `figures/`, `report/`: data, code, outputs and report are separated; environment is not. |
| should/009 | M.4 | not-applicable | No restricted data or software module is identified in `input/sources.json` or project documentation. |
| should/004 | E.1 | unmet | `results/run_history.md`: worker reruns used the same environment; this assessment's fresh-copy run is not worker evidence. |
| should/005 | E.1 | unmet | `README.md`: no disposable environment per execution is specified. |
| should/006 | D.2 | unmet | `results/run_history.md`: replay used the same environment; no environment reconstitution test is recorded. |
| should/007 | D.2 | unmet | Root inventory and `README.md`: no environment artifact is archived inside the project. |
| should/008 | D.2 | unmet | `README.md`, `protocol.md`: no dependency update process is documented. |
| may/001 | M.2 | partial | `input/sources.json`, `resources/nilearn/`: data sources and some software references are external, but not composed as submodules. |
| may/002 | M.2 | met | `README.md`, `protocol.md`: the input, analysis, result and reporting roles are described and linked. |
| may/003 | M.2 | partial | Directory separation is visible, but no independent module update contract is documented. |
| may/004 | M.2 | partial | `README.md` documents a single analysis invocation; no broader module composition mechanism is supplied. |
| may/005 | M.2 | met | `README.md`, `protocol.md`: project navigation links identify report and analysis decisions. |

## Probe differences and not-checked items

`entry-point` marked must/007 and must/008 unmet. Reading the delivered README and script supports a partial must/007 and met must/008: the entrypoint is clearly named, although its invocation depends on a host-specific interpreter and has no setup guidance. These two responses are flagged `probe-overridden` in `response.json`. Other probe findings are retained in `probes.json`. The license probe also found no declared project license; this is recorded as an extra item in `response.json`. No checklist item remains not-checked; the absence of documented environments/remotes was assessable from the complete captured root and worker stop-state files.

## Goal, kind and record

The stated goal is the group-stage test of a positive gain effect in vmPFC for the equal-indifference group, conditional on fixed upstream participant maps (`input/study-task.md`, `input/upstream-methods.md`). Project kind: study; the emphasis here is on preserving the study's code, data, environment and provenance together.

STAMPED checklist link: [open the filled checklist](checklist-url.txt). The machine-readable checklist answers are in [response.json](response.json); the scientific adequacy record is [scientific-judgment.json](scientific-judgment.json); the replay receipt is [replay/replay.json](replay/replay.json).

Assessment runtime: frozen `assessment.py` source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; runner check passed before probe, replay and response actions. The operational copy was used for inspection and Git commands. The operational manifest comparison found no invalidating mismatches; `.git/annex/keysdb/db`, `db-shm` and `db-wal` changed or were created during inspection and are classified only as allowed operational metadata. Logical database equivalence is not established (`integrity-check.json`). The worker stop receipt SHA-256 is `032361148ea1f213f1360b9ab2eb408288dc978cae37befebf9527c1169130a2`. No coordinator-only preservation action is credited to the worker.
