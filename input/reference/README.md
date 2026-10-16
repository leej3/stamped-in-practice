# Anatomical reference atlas

The vmPFC operationalization uses labels in the Harvard-Oxford cortical atlas, `cort-maxprob-thr25-2mm`, distributed by FSL and fetched with Nilearn's `fetch_atlas_harvard_oxford`. The 25% maximum-probability image is stored here so the label mask can be regenerated without relying on a user cache. The atlas uses MNI152 2-mm geometry and is nearest-neighbor resampled onto the supplied MNI152NLin2009cAsym maps. The selected broad medial/orbitofrontal labels are Frontal Medial Cortex, Subcallosal Cortex, Paracingulate Gyrus, and Frontal Orbital Cortex. Atlas citation: Desikan et al. (2006), *An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest*, NeuroImage 31:968–980; FSL atlas page: https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html#harvard-oxford-atlases.

SHA-256 of the stored image: `586d76a7defd278fcea4d83d301994d7e096aa8272d26e3c7539b4f8ebd588c1`.
