
## Pilot attempt 1 (input path resolution)
The first header/QC pilot did not run because `sources.json` file paths are relative to `input/`, while the initial probe incorrectly resolved them from the workspace root. No scientific outputs were produced. Corrected the path base to `input/` before rerunning; no input files were changed.

## Pilot attempt 2 (TFCE computational bound)
The 99-permutation TFCE pilot remained CPU-bound after nearly three minutes and produced no completed output. Before inspecting any inferential values, the correction statistic was revised to voxelwise permutation max-T: this remains one-sided whole-mask FWER control by the maximum statistic over all tested voxels, but avoids TFCE's spatial enhancement cost. The primary inference and all subsequent materials will use this revised method; TFCE is not reported as a result. A bounded max-T pilot will be run before the primary batch.

## Primary accepted run
Executed the revised, explicitly one-sided whole-mask max-t model with all 54 participants, 5,000 permutations and seed 20261016. Run completed successfully (exit 0). It produced 24 positive FWE-corrected voxels in three posterior clusters; no corrected voxels intersect the predefined vmPFC proxy. `primary_summary.json`, NIfTI maps, participant QC, arrays and cluster coordinates retain the result. The primary output was regenerated after correcting its numerical-reference metadata field; the inferred maps and corrected results were identical.

## Independent numerical validation and figures
`analysis/validate_results.py` confirmed participant IDs/metadata, all 54 SHA256s, common grid and mask, and the result voxel counts. Its independent SciPy one-sample t reference agreed at 250 deterministic in-mask voxels with a maximum absolute difference of 9.54e-7. The final figures were generated from the accepted primary outputs with `analysis/make_figures.py` and visually inspected at display resolution. The 99-permutation TFCE attempt was stopped before output; its pilot result is not used. The AAL3v2 atlas retrieval attempt failed at OSF (HTTP 500); the descriptive coordinate proxy was retained and no atlas-based claim is made.
