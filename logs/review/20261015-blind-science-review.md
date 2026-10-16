# Blind scientific review record

Reviewed commit: `53fa3fbed94ed81029877300b4c2b299abf3724b`.

The reviewer independently found the one-sample positive group-mean model with whole-brain max-t sign flips coherent for the supplied participant effects. Reported counts, peak coordinates/statistic/p value, and vmPFC descriptive mean/interval agreed with committed artifacts. Posterior corrected foci are far from plausible vmPFC boundaries, so the main conclusion does not depend on the coordinate-box boundary.

Supported findings and responses:

1. The previous validator checked null length/order and threshold count, but not permutation statistics or voxelwise corrected p values. The validator now directly recomputes 20 fixed-seed sign-flip maxima, reconstructs the corrected p map from the stored null, and checks both thresholded maps voxelwise.
2. The pre-analysis plan specified Bonferroni sensitivity and descriptive full-brain-average/selected-vmPFC-voxel uncertainty. The analysis now produces those summaries; the report labels them as sensitivity/descriptive and notes peak selection.
3. The report previously left the environment branch unnamed. It now names `codex/env-narps-r1-11`.
4. The original corrected-map panel used vmPFC slices and missed the posterior foci. Its corrected panel now uses the peak slices; the coordinate projection shows all corrected voxels relative to the vmPFC search box.

The review found no result-changing defect. The validation failure in the earlier commit is a scope gap, not an indication that the primary result was numerically wrong.
