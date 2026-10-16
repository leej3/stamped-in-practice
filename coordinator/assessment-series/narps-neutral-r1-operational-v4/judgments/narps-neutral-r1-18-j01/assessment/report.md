# Independent assessment — NARPS potential gains and vmPFC

**Scope and identity.** The complete captured worker stop state was assessed from operational copy inspection. Canonical capture SHA-256: `e72b24b4fadd4e55dc6cb69acb18172372637f551fa6a40c3d99eb68f6ec29da`; evidence paths below are relative to that capture's `content/workspace/`. The separate worker stop receipt is SHA-256 `8c1924f5440d677d80e9a94cf2f34f1ebafabebf6334dada68cb63392b74eec9`. Its captured HEAD is `afb62884c70115b6e46a92ddcd1d17bbf4f33544`.

**Capture integrity.** Canonical and operational manifest SHA-256 values matched. A read-only comparison found no mismatch among 1,112 operational workspace entries, including symlink targets, file bytes and modes, except the separately classified annex database files. Inspection changed `.git/annex/keysdb/db` and created `.git/annex/keysdb/db-shm` and an empty `.git/annex/keysdb/db-wal`; these are operational metadata, not worker evidence. This does not establish logical database equivalence. No other mismatch or repair occurred. All Git commands addressed the operational copy with the supplied lock settings.

## Scientific assessment

**Scientific adequacy: supported.** The reported no-support conclusion is supported for the supplied group maps and the specified group-analysis question. The code analyzes 54 cohort-matched participant cope maps, checks hashes, finite values and shared image geometry, and uses a one-sample positive-direction group test with 5,000 sign flips and maximum-T whole-brain FWER control at .05. It defines vmPFC independently of observed peaks as a 12-mm sphere centered at MNI (0, 42, −10), and reports its whole-brain-corrected results as well as a descriptive ROI estimate and uncertainty. In `results/summary.json`, the vmPFC mean is −0.0078 cope units, the one-sided *p* is .717, the 95% interval is [−0.0350, 0.0194], and the minimum corrected p in that sphere is 1.00. The 24 corrected positive voxels are reported in posterior/occipital cortex, outside the hypothesis region. This is a defensible absence of positive vmPFC support, not proof of zero effect.

The report appropriately limits interpretation to supplied participant effect estimates and the fixed upstream model: gain was normalized before HRF convolution, the values are not per-currency-unit slopes, gain and loss were modeled separately, and participant variance maps are absent. The symmetric sign-flip null is stated. The mask uses the intersection of nonzero voxels across maps as a proxy for common coverage; that is reasonable if zeros mark out-of-coverage voxels, though an explicit participant coverage mask would better distinguish missing coverage from a true exact-zero effect. This limitation does not overturn the reported vmPFC result on the evidence supplied. No equivalence margin is specified, so the report correctly avoids claiming equivalence or no effect.

**Hypothesis outcome as reported:** “In the NARPS equal-indifference group, the supplied gain-effect estimates do **not** support a positive average vmPFC response to increasing potential gain.” This is distinct from the adequacy category above.

Scientific evidence: `reports/report.md`, `analysis.py`, `input/upstream-methods.md`, `input/participants.tsv`, `input/sources.json`, `results/summary.json`, `results/participant_qc.tsv`, `results/top_peaks.tsv`, `results/vmPFC_participant_summary.tsv`, `results/voxel_results.tsv.gz`, the four NIfTI maps under `results/`, and the three figures under `figures/`. Each citation refers to the canonical capture digest stated above.

## Worker stop state and reproducibility

The receipt records a complete worker stop and the supplied input identities. It identifies the 54 map links as initial input material; those maps, the metadata and upstream methods must not be credited as worker-authored publication or versioning. At stop, the only Git commit was the supplied input commit. `analysis.py`, `reports/report.md`, `narps_gain_analysis.ipynb`, `figures/`, and `results/` were untracked; `.skills/` was also untracked, and `.codex/` and `.entire/` were ignored. Thus the commit alone omits the scientific analysis and all results, although the complete capture preserves them.

The report documents `python analysis.py`, and the script is a clear entry point. The report's “prepared Python environment” has no accompanying dependency declaration, pinned environment, installation instructions or host requirements. There is no exact environment-to-results run record. I did not replay: although the entrypoint and exact generated outputs are identifiable, the required environment cannot be reconstructed solely from worker-supplied instructions or declarations. See [replay record](replay-record.json). This is not a replay failure and says nothing about the worker's research budget.

No worker-declared complete-delivery retrieval route or Git remote is present. The URLs in `input/sources.json` identify upstream source data, not a route to retrieve the complete code, report and result bundle. The intended recipient is a researcher using an authorized route; required coverage is the entire stopped workspace. No remote host was available to test. Coordinator delivery to this assessor is not evidence that the worker had published the object. Details are in the [access record](access-record.json).

Inspection of the captured `.codex/`, `.entire/` and `.skills/` paths reveals assistance tooling/session artifacts. This exposure is recorded only; those materials were not used as scientific or STAMPED grading evidence. No treatment assignment was inferred or reported.

## STAMPED assessment

**Assumption, not user-confirmed:** the object is a **study** whose product is a group-level scientific conclusion with its code, inputs and outputs. The task and report describe that goal. The seven principles are judged against the worker stop state, not the coordinator's later preservation.

- MUST: **4 met / 1 partial / 12 unmet / 0 not-checked** (17 items).
- SHOULD: **0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable** (9 items).
- MAY: **3 met / 0 partial / 2 unmet / 0 not-checked** (5 items).

### What to address first

1. Track the analysis, report, notebook, figures and results in the worker's versioned delivery, including large generated images. This makes the research state reviewable and recoverable (`must/004`, `must/005`, `should/001`).
2. Declare and pin the Python dependencies and document how to create the environment and host requirements; link the exact environment to the run that produced the shipped outputs (`must/003`, `must/006`, `must/010`–`must/017`, `should/006`–`should/008`).
3. Publish a complete, authorized retrieval route for the code, environment and results, and state the intended recipient and terms (`must/016`, `must/017`; license gap is an extra finding).
4. Keep the existing direct analysis script, but document an install-and-run path and retain evidence of a clean-environment execution (`must/007`, `should/002`, `should/004`).

### What is already useful

- All 54 maps and cohort metadata are included; the source manifest records image identities, hashes and source URLs (`input/sources.json`, `input/participants.tsv`).
- The analysis script checks participant membership, input checksums, finite values and image geometry, and reports QC without excluding a participant (`analysis.py`, `results/participant_qc.tsv`).
- The report explains the negative vmPFC result, whole-brain correction, limitations of the cope estimates and what lack of support means (`reports/report.md`).

### Per-item checklist

Evidence paths in the table are capture-relative and tied to canonical SHA-256 `e72b24b4fadd4e55dc6cb69acb18172372637f551fa6a40c3d99eb68f6ec29da`.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `analysis.py` | All delivered inputs, analysis, report and outputs are nested under the captured workspace root. |
| must/002 | S.1 | met | judgement | `input/sources.json` | The 54 maps and cohort metadata are included beneath input/; sources.json identifies their upstream origins. |
| must/003 | S.1 | unmet | judgement | `analysis.py`, `reports/report.md` | analysis.py imports external Python packages, but no environment specification or software module is delivered. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `probes.json`, `analysis.py` | Git is present, but the worker's analysis, report, notebook and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `results/group_mean_cope.nii.gz` | Coordinator-supplied input maps use annex pointers, but derived NIfTI outputs were untracked at worker stop. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `analysis.py`, `reports/report.md`, `narps_gain_analysis.ipynb` | Results are shipped, but no provenance record links their generating action to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `reports/report.md`, `analysis.py` | The report gives a run command but no installation instructions or reproducible environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `reports/report.md`, `analysis.py` | The report names python analysis.py and the delivered script is a clear starting point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis.py` | The analysis derives paths from its own directory and uses relative artifact paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis.py`, `reports/report.md` | The script requires scientific Python packages, but no dependency declaration or environment specification is supplied. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `reports/report.md`, `analysis.py` | The documented route assumes a prepared Python environment but does not document its host or system assumptions. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `reports/report.md`, `analysis.py` | No system requirements or complete dependency list accompany the execution instruction. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `probes.json`, `analysis.py` | No environment specification is included in the worker's delivered workspace or Git history. |
| must/014 | P.3 | unmet | judgement | `analysis.py`, `probes.json` | No environment-update process or tracked environment changes are present. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `reports/report.md`, `probes.json` | No pinned package manifest or container identity lets another researcher reconstruct the result environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `probes.json`, `.git/config` | No worker-declared route shares an environment specification or the complete study delivery. |
| must/017 | D.1 | unmet | judgement | `reports/report.md` | The report says to use a prepared environment but does not say how to obtain or create it. |
| should/001 | T.2 | partial | judgement | `probes.json`, `input/data/sub-001_hypo1_cope.nii.gz` | Git/annex versions supplied inputs, while the worker’s code and derived artifacts remained outside version control. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `probes.json` | No regular workflow-testing record is present; a CI/manual test history would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `probes.json`, `analysis.py` | input/, results/ and figures/ are separated by folders, but code and environment are not independent modules. |
| should/004 | E.1 | not-checked | judgement | `reports/report.md`, `replay-record.json` | No fresh-environment execution record is supplied, and the missing environment specification prevents a scoped replay. |
| should/005 | E.1 | unmet | judgement | `analysis.py` | The documented entrypoint runs directly in the caller's prepared environment and does not create a disposable one. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probes.json`, `reports/report.md` | No exact environment specification exists to reconstitute or test against the shipped results. |
| should/007 | D.2 | unmet | judgement | `probes.json`, `reports/report.md` | No environment specification, binaries or container image are archived with the study. |
| should/008 | D.2 | unmet | judgement | `analysis.py`, `probes.json` | No environment-update process is declared or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the captured inputs and software are public; no restricted component is identified. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | The separately maintained input dataset has a clear input/ boundary and source URLs/checksums; its bytes are included locally. |
| may/002 | M.2 | unmet | judgement | `reports/report.md` | The report names input and output paths but does not document a modular structure or how components recombine. |
| may/003 | M.2 | unmet | judgement | `analysis.py` | The workflow reads from a shared root and writes outputs in place; independent module update boundaries are not defined. |
| may/004 | M.2 | met | judgement | `analysis.py` | analysis.py provides a direct composition path from included maps and metadata to the reported outputs. |
| may/005 | M.2 | met | judgement | `reports/report.md` | The report directs readers to the analysis script, numerical outputs and figures, supporting basic navigation. |

### Probe disagreements and flags

- `must/005`: the annex probe saw the 54 supplied map pointers in Git but missed the untracked derived NIfTI outputs. The full delivery supports `partial`; the MUST is therefore not met.
- `must/006`: the derived-record probe missed untracked outputs. Those outputs exist, but no exact environment-linked provenance record is supplied; the item is `unmet`.
- `must/007`: the probe's filename heuristic missed `reports/report.md`; the verdict remains unmet because that report lacks installation/environment instructions. The reason is corrected.
- `must/008`: the probe missed `analysis.py` and the report's explicit command; judgement changes the verdict to met.
- `must/011`, `must/012`: the platform command scan cannot settle documentation completeness. The documented prepared environment is unspecified, so both are unmet.
- `should/003`: the probe recognized only `input/`; the complete tree also has `results/` and `figures/`, but lacks independent code/environment modules, so partial remains appropriate.
- `should/006`: no exact environment spec or reconstitution evidence exists, so this is unmet despite the CI probe's not-checked result.
- `may/001`: the probe did not recognize the source manifest. It identifies separately maintained input data by boundary, source and checksum; met is based on that equivalent evidence.

### Not checked

- `should/002`: regular workflow testing may be manual; a test history would settle it.
- `should/004`: no fresh-environment run is recorded, and safe replay prerequisites are absent; a completed clean-environment run with its environment identity would settle it.

### Additional findings outside the checklist

- **License:** no reuse terms for the study or its data are declared. `.skills/jupyter-notebook/LICENSE.txt` licenses that bundled helper only. This remains an extra finding, not a checklist item.
- **Access:** no worker route for the complete delivery was identified or tested; see `access-record.json`.
- **Replay:** not checked for missing worker-supplied environment declarations; see `replay-record.json`.
- **Integrity:** no difference from the canonical capture was detected in the operational inspection copy.

Checklist artifacts: [response JSON](2026-10-16-response.json), [probe output](probes.json), and [checklist URL](2026-10-16-url.txt). Replay record: [replay-record.json](replay-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on capture `e72b24b4fadd4e55dc6cb69acb18172372637f551fa6a40c3d99eb68f6ec29da`, Git commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, 2026-10-16, Codex Desktop 0.162.0-alpha.17.2 / model identifier not exposed by runtime. Frozen runner source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`; environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: `probes.json`.
