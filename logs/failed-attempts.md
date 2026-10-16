# Pre-analysis failed attempts

These exploratory failures did not change or exclude any supplied data.

| Attempt | Command | Result |
|---|---|---|
| Retrieve the original NARPS instruction PDF for local visual review | `curl -L --fail --silent --show-error https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf -o /tmp/narps_instructions.pdf` | Failed with `curl: (56) The requested URL returned error: 522`. The source link and indexed search excerpt remain cited in the report; no local copy was obtained. |
| Initial map coverage preflight | `pixi run python - <<'PY' ... counts.append((m&mask0).sum()/mask0.sum(), (m!=mask0).sum()) ... PY` | Failed due to a Python call typo: `TypeError: list.append() takes exactly one argument (2 given)`. Corrected and rerun immediately; it showed 54 available maps and minimum 94.8% overlap with the first map's nonzero support. No analysis or files were affected. |
| First analysis presentation pass | `pixi run duct ... pixi run python scripts/analyze_gain.py` (duct record `logs/gain-group-2026.10.15T21.42.37-46612_`) | The primary test ran, but review found the descriptive interval was specified at 5% instead of 95%, and the corrected-effect figure's fixed slices missed the occipital peak. The run was retained; corrected interval, peak-slice figure, and vmPFC family-wise-error summary were added and rerun in the later duct record. Primary permutation inference was unchanged. |
| Figure title layout adjustment | `pixi run duct ... pixi run python scripts/analyze_gain.py` (duct record `logs/gain-group-final-2026.10.15T21.44.49-50164_`) | Failed after the permutation calculation because Nilearn's `OrthoSlicer` exposes its figure through `frame_axes.figure`, not `_figure`; retained in stdout, stderr, resource, and info logs. Updated the figure call and reran. |
