# Attempt log: corrected-figure regeneration

- **Stage:** figure generation after deterministic group results were written.
- **Failure:** `NameError: name 'sig_t_values' is not defined` at the plotting preparation line.
- **Impact:** no model estimates or inferential results were affected; script terminated before saving updated figures.
- **Cause:** the plotting refactor used `sig_t_values` without assigning it before figure rendering.
- **Intervention:** define the thresholded statistic array before constructing the saved and plot images; rerun the complete entry point and check exit status, output summary, and rendered figures.
