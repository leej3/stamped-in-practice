# Independent assessment: NARPS potential gains and vmPFC

**STAMPED items:** MUST: 4 met / 1 partial / 10 unmet / 2 not-checked; SHOULD: 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable; MAY: 1 met / 0 partial / 3 unmet / 0 not-checked / 1 not-applicable. Partial MUST items do not count as met. No overall score is assigned.

## Scientific judgment

Scientific adequacy: supported. The reported conclusion is supported as a lack-of-evidence claim at the stated whole-brain-corrected criterion, with uncertainty and model limits disclosed.

Hypothesis conclusion: The supplied group maps do not support a positive gain effect in vmPFC.

I find the scientific reasoning and reported outcome supported. The script uses all 54 equal-indifference participants, checks finite values and shared image geometry, and forms a nonzero-coverage mask rather than treating uncovered structural zeros as observations. It tests the positive direction with an equal-weight one-sample model and participant sign flips, using the maximum positive t statistic over 210,968 voxels. The report identifies the 5,000-flip threshold and exchangeability assumption. The descriptive 10-mm sphere at [0, 44, -10] mm is identified before interpretation and is not used to replace the required whole-brain decision. Its mean estimate is negative with a 95% interval including zero; the 24 corrected voxels are posterior and remote from the sphere. The report correctly avoids interpreting these normalized gain-modulator estimates as currency-unit slopes and avoids treating non-significance as equivalence or proof of absent neural coding. The lack of participant variance maps and the data-derived coverage mask limit interpretation but do not invalidate the cautious no-support conclusion. Evidence: the worker report and analysis at capture `44b45c2d1e80cd01a5c6725623e8bffd63b3732ef2c1f010cdceea08c89f6878`, `content/workspace/report.md` (SHA-256 `9ea79bef10dedfe5b1ff40558fa07070c2c0704ae17252abe51b3945a446eb74`), `content/workspace/code/group_analysis.py` (SHA-256 `4c062e7888f85698b15ae65942f7dbd1340489192415df05628f70e68861da2a`), and `content/workspace/results/summary.json` (SHA-256 `0aba6b80df86de1910b1c36be524c2970e065b63f51ba8600a8dce9dffd9b7f4`).

## Fix first

1. Commit the analysis script, report, figures, and results at worker stop; this would make the versioned project represent the delivered result (must/004, should/001).
2. Add a tracked, locked environment declaration and link the result run to it; this would make the analysis installable and its provenance attributable (must/003, 006, 010, 013, 015, 016; should/006, 007).
3. Add concise install and run instructions naming the command and outputs; this would make the existing script usable by another researcher (must/007, 017).
4. Document the authorized retrieval route for the complete object and the exact coverage it provides; this would let a recipient obtain more than the referenced source maps.

## What is present

- The delivery includes 54 annexed participant maps, matching cohort metadata, a group-analysis script, results, figures, and a detailed scientific report. The report explains why the supplied maps are not currency-unit slopes and the limits of the upstream model. Evidence is cited above and in the response JSON.
- All artifacts are under one workspace root, and the analysis locates files relative to its own path. The report links the code, results, QC tables, and figures.
- The worker-stop receipt records a complete capture, a normal worker exit, and the same original HEAD as the capture. It inventories the supplied resources separately from subsequently created scientific artifacts. Receipt: `worker-end-state.json`, SHA-256 `ebf92e88edc21d3312725711918512cf15c0fe25c083e95a5ee51cce6dd36640`.

## Worker attribution and integrity

The canonical original capture SHA-256 is `44b45c2d1e80cd01a5c6725623e8bffd63b3732ef2c1f010cdceea08c89f6878`; original captured HEAD is `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`. The worker stop receipt identifies a normal exit and complete delivery. The report, code, figures, and results were present in the complete stop-state but were untracked: the frozen probe on the operational copy observed `?? code/`, `?? report.md`, `?? figures/`, and `?? results/`. That observation is assessor-generated and is used only to characterize the matching stop-state, not as worker-authored evidence. The worker's captured Git commit is not treated as the whole delivery. The 54 maps were already annex links among the supplied resources; the stop receipt does not attribute annex setup to the worker, so must/005 remains not-checked despite the probe recognizing the storage format.

Canonical and initial operational manifests have the same capture identity. The inspection copy contained no missing or changed scientific files. Git status inspection changed `.git/annex/keysdb/db` and created `db-shm` and `db-wal`; all are regular-file operational metadata under the explicitly allowed paths, not worker evidence. Their logical database equivalence is not claimed. No other changes were found. See `integrity/operational-compare.json`.

A repository-local remote was not configured. The worker supplied no authorized retrieval route for the complete research object. `input/sources.json` cites upstream map and metadata sources, but these cover inputs rather than the report, code, results, environment, and complete delivery. Access record: `access-record.json`. The intended recipient is a researcher following the worker-declared authorized route; because none was declared, the recipient route and host scope could not be tested. Coordinator custody of this copy is not evidence that the worker published it. `judge-target.json` lists no reference limits; I did not follow external targets. The captured `.git/config` has an absolute `core.hooksPath` outside the copy; hooks were not invoked.

Replay was not checked. The report links a script and names generated artifacts, but does not document an exact invocation or an installable environment/dependency declaration; therefore no exact worker-documented command and prerequisites could be established. I did not run a guessed command or reconstruct dependencies. The replay record lists the candidate generated artifacts and the reason no attempt was made. No scientific output was removed or regenerated.

Exposure noted: the captured `.codex` and `.entire` paths identify agent-workflow artifacts. This exposure was not used as grading evidence.

## Per-item verdicts

See [`checklist-table.md`](checklist-table.md) for the pinned item-by-item table and evidence. The full response is [`response.json`](response.json); unedited frozen probe results are [`probes/probes.json`](probes/probes.json).

### Probe override

- **must/005:** the probe identified annex storage for the supplied maps, but the stop receipt classifies those maps as supplied inputs. The format is observed; worker attribution is not established, so practice credit is withheld.
- **must/008:** the tracked-path entry-point probe reported no start script, but it did not count untracked files. The complete worker delivery includes `code/group_analysis.py`, and the report identifies it as the analysis script. The item is met on the complete stopped delivery; the probe result is retained and flagged as overridden.
- **should/003:** the probe recognized only `input/`, while the complete stop-state also separates `code/`, `results/`, and `figures/`. The item remains partial because environment definitions are absent and the module boundaries are not explained.

### Not checked

- **must/005:** the input maps use annex links, but they were supplied in that form and no worker annexing action is recorded.
- **must/011:** the report names Python and package versions, but the complete delivery does not establish all host or system-library assumptions.
- **should/002:** no recognized CI exists; the capture does not establish whether regular manual testing occurred.
- **should/004–005:** the stop-state contains no record settling fresh-environment testing or disposable execution.
- **Replay:** there is no worker-documented command or supplied installable environment to replay safely.
- **Access:** no worker-authorized complete-object route exists in the stop-state to test.

## Goal and kind

The stated goal is a group-level analysis of the potential-gain effect in vmPFC among the equal-indifference NARPS participants, conditional on supplied participant maps and metadata. This is a study/research object with scientific analysis and results; emphasis is on transparent inputs, a traceable analysis, and a usable scientific environment.

## Checklist link and provenance

Checklist-app link: [`checklist-url.txt`](checklist-url.txt). Full machine-readable response: [`response.json`](response.json). Capture identity: canonical manifest SHA-256 `44b45c2d1e80cd01a5c6725623e8bffd63b3732ef2c1f010cdceea08c89f6878`; original captured HEAD `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`; captured at `2026-10-16T07:41:21.554566+00:00`.

Produced with `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on 2026-10-16, Codex. Probe output: `probes/probes.json` (operational-copy observations; SHA-256 `28ef321b6d38e9ab719685763ca3786e0b665cf0decce43b4d9bd0a56718ec50`).
