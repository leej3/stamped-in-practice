# Potential gains and brain activity in vmPFC

## Result

**This group analysis does not support a positive gain effect in vmPFC.** None of the positive voxels surviving whole-brain correction overlapped the independently defined vmPFC mask. The participant-average gain effect over that mask was −0.003 map units (95% t interval −0.028 to 0.022; t(53)=−0.24; one-sided descriptive p=.595). The interval spans zero and modest effects in either direction, so the result is not evidence of equivalence or proof that vmPFC is unresponsive to gain.

The one-sided whole-brain sign-flip max-T test found 159 voxels at family-wise p≤.05 across 210,968 supported voxels (4,999 flips; minimum attainable p=.0002). They formed six 26-connected clusters. The two largest were bilateral occipital-pole clusters (88 and 64 voxels); four additional components were small (1–4 voxels). **No corrected voxel was in vmPFC.** A conservative parametric Bonferroni check retained 9 voxels outside vmPFC. The positive posterior findings do not answer the vmPFC hypothesis and are not interpreted as evidence for it.

![Participant-level mean gain-effect estimates in the vmPFC atlas mask](results/vmPFC_participants.png)

*Dots show each participant’s spatial mean over the vmPFC mask; the diamond and whiskers show the group mean and 95% t interval. These are model coefficient units, not currency units.*

![Positive whole-brain effects surviving single-step max-T correction](results/whole_brain_fwer_map.png)

*Displayed values are group t statistics at voxels with one-sided whole-brain max-T p≤.05. The principal bilateral posterior clusters lie outside the hypothesized region.*

## Design and analysis

The independent units were the 54 equal-indifference participants, with one supplied unthresholded AO86 gain-effect map per participant. All 54 maps matched the metadata, passed SHA-256 and file-size checks, had the same 97×115×81 grid (2×2×2.4 mm), and contained finite values. No participants were excluded. The inference mask included voxels with nonzero support in at least 90% of maps (210,968 voxels), avoiding the interpretation of outside-brain zeros as observed null effects.

At each supported voxel, the observed statistic was the one-sample t for a positive mean. Whole-brain family-wise error was controlled with a single-step maximum statistic across the supported mask using 4,999 participant-level sign flips (seed 20261016). Each flipped mean used the observed voxelwise standard error as its fixed scale; under the observed signs this equals the usual one-sample t. This sign-flip calibration assumes independent participants and symmetric participant-level null effects. The original NARPS instructions call for a whole-brain corrected decision, which is why uncorrected ROI evidence was not used to claim support ([NARPS analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The vmPFC mask was set independently of these maps by combining Harvard-Oxford Frontal Pole, Frontal Medial, Subcallosal and Paracingulate labels, restricted to |MNI x|≤14 mm and z<0. This is a published operational anatomical definition ([Jiang et al., 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8197643/)); mask and source image are included under `results/` and `reference/`. The 2 mm atlas is labeled MNI152NLin6Asym and was nearest-neighbor resampled to the supplied MNI152NLin2009cAsym map grid. The cross-template localization is approximate; it is used to identify the hypothesized region, not to create the whole-brain correction.

## Interpretation and limits

The supplied images are participant contrast parameter estimates, not t/z maps or raw BOLD. The upstream gain modulator was mean-centered and variance-normalized before HRF convolution, so coefficient size is not response per dollar. Gain and loss were modeled separately, making this gain estimate conditional on that upstream model. Potential gains spanned twice the potential-loss range in this group; this group-level contrast cannot establish a causal neural response to a monetary unit or adjudicate alternative behavioral encodings of mixed gambles.

Participant variance maps were not supplied, so a precision-weighted mixed-effects group model was not available; the analysis gives each participant equal weight. Upstream preprocessing and first-level modeling were fixed and are not revalidated here. A lack of corrected vmPFC support means this analysis did not establish a positive effect at its chosen group model, spatial coverage, anatomical definition and correction threshold. It does not show a zero effect, rule out smaller effects, establish individual-level absence, or validate the upstream model.

## Reproducibility and validation

Run `analysis/run_analysis.py` to regenerate the maps, tables, and figures; run `analysis/validate_results.py` for independent numerical checks. The observed voxelwise t and one-sided p values agreed with SciPy to maximum absolute differences of 3.2×10⁻⁷ and 6.5×10⁻⁸, respectively, consistent with float32 NIfTI storage. Recomputed max-T p values agreed within 3.0×10⁻⁸. The independent check recovered 159 corrected voxels, zero in vmPFC, and 9 Bonferroni voxels, also zero in vmPFC. See `results/validation.json`, `results/input_qc.tsv`, `results/whole_brain_clusters.tsv`, and `results/summary.json` for details. Rejected execution attempts and their causes are recorded in `results/run_notes.md`.
