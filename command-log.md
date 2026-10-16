# Command and attempt log

All paths are under this judgment output directory unless noted. Runner interpreter and runner: `$STAMPED_ASSESSMENT_PYTHON`, `$STAMPED_ASSESSMENT_RUNNER`; target: `$STAMPED_JUDGE_TARGET`; output: `$STAMPED_JUDGE_OUTPUT`.

## Commit verification

`git -C "$STAMPED_JUDGE_TARGET" rev-parse HEAD` → `f30190d8144a9e15acfa1c0d973eadf0d655c83c`.

## Frozen runner and probes

- `$STAMPED_ASSESSMENT_PYTHON $STAMPED_ASSESSMENT_RUNNER check`; output: `runner-check.stdout`, `runner-check.stderr`.
- `$STAMPED_ASSESSMENT_PYTHON $STAMPED_ASSESSMENT_RUNNER response --help`; output: `runner-response-help.stdout`, `runner-response-help.stderr`.
- Failed probe syntax attempt: `$STAMPED_ASSESSMENT_PYTHON $STAMPED_ASSESSMENT_RUNNER probes --path "$STAMPED_JUDGE_TARGET" --kind study --check-remote --output "$STAMPED_JUDGE_OUTPUT/2026-10-16-probes.json" --response "$STAMPED_JUDGE_OUTPUT/2026-10-16-response.json"`. It exited 2 because the target is a positional argument; retained in `probes.stdout` and `probes.stderr`.
- Successful probe attempt: `$STAMPED_ASSESSMENT_PYTHON $STAMPED_ASSESSMENT_RUNNER probes "$STAMPED_JUDGE_TARGET" --kind study --check-remote --output "$STAMPED_JUDGE_OUTPUT/2026-10-16-probes.json" --response "$STAMPED_JUDGE_OUTPUT/2026-10-16-response.json"`; output: `probes-attempt-2.stdout`, `probes-attempt-2.stderr`, and `2026-10-16-probes.json`.

## Fresh-clone replay (the only replay attempt)

`$STAMPED_ASSESSMENT_PYTHON $STAMPED_ASSESSMENT_RUNNER fresh-rerun --path "$STAMPED_JUDGE_TARGET" --entry 'pixi run python scripts/group_analysis.py --permutations 5000 --seed 20261015' --outputs results/analysis_results.json results/group_summary.csv results/whole_brain_fwe_clusters.csv results/quality_checks.json results/participant_roi_effects.csv results/maps/group_mean_effect.nii.gz results/maps/group_tstat.nii.gz results/maps/group_positive_maxT_pFWE.nii.gz results/maps/group_positive_maxT_FWE05_tstat.nii.gz results/maps/vmpfc_aal3_medial_orbitofrontal_mask.nii.gz results/figures/roi_participant_effects.png results/figures/group_tmap_vmPFC.png results/figures/whole_brain_maxT_FWE.png --rtol 1e-6 --workdir "$STAMPED_JUDGE_OUTPUT/replay-work-1" --timeout 7200 --max-get-gb 5.0 --output "$STAMPED_JUDGE_OUTPUT/2026-10-16-fresh-rerun.json"`. Output and receipt: `fresh-rerun.stdout`, `fresh-rerun.stderr`, `2026-10-16-fresh-rerun.json`; clone retained in `replay-work-1/`.

## Remote retrieval checks

- `git -C "$STAMPED_JUDGE_TARGET" ls-remote origin HEAD` and exact target SHA lookup; receipts under `remote-check/git-origin-*`.
- `git clone --bare "$(git -C "$STAMPED_JUDGE_TARGET" remote get-url origin)" "$STAMPED_JUDGE_OUTPUT/remote-check/origin-bare.git"`; verify branch and commit with `show-ref` and `cat-file`; receipts under `remote-check/git-*`.
- First map check: curl the `sub-001` NeuroVault URL from `input/sources.json`, then SHA-256 and byte count; outputs under `remote-check/neurovault-sub-001*`.
- Full source retrieval: Python read `input/sources.json`, curl each of its 54 `.nii.gz` URLs into `remote-check/neurovault-all-maps-attempt-2/`, compare each retrieved file's byte count and SHA-256 with the manifest, and write `retrieval-manifest.json`. Per-map stdout is retained in `retrieval-manifest.json` and `attempt-2.stdout.reconstructed`; stderr is `attempt-2.stderr`.
- An earlier Python `urllib` retrieval attempt received HTTP 403 responses and stopped on a non-map record without a URL. Its outcome is summarized in `remote-check/urllib-attempt-1.stderr-summary`; that attempt is not used as evidence.

## Response helpers

Every helper was invoked as `$STAMPED_ASSESSMENT_PYTHON $STAMPED_ASSESSMENT_RUNNER response <helper> ...`. The `items`, `template`, all `set` calls, `stamp`, `table`, `encode`, `decode`, and `validate` outputs are retained as `response-*`, `response-set-*`, `response-template.*`, `2026-10-16-response-table.md`, `2026-10-16-url.txt` and `2026-10-16-decoded-response.json`. Final validations: `response-validate-final.stdout` and `runner-validate.stdout`.

## Supplied scientific reference

Attempted to open `https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf`; the browser fetch timed out before returning content. Receipt: `external-source-check.txt`. Scientific interpretation relies on the task brief and coordinator rubric retained in the assessment request, and on object artifacts.
- Failed first report-writing shell attempt used an unquoted Markdown heredoc and caused shell expansion errors. It was replaced by a quoted heredoc; retained command description, empty stdout, and a stderr summary as `assessment-write-attempt-1.*`.
- The initial urllib source-check stdout is reconstructed per map from the tool-visible 403 responses in `remote-check/urllib-attempt-1.stdout.reconstructed`; stderr summary is `remote-check/urllib-attempt-1.stderr-summary`. The successful curl retrieval is the access evidence.
