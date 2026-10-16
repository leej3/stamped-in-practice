# Anatomical localization resource

`HarvardOxford-cort-maxprob-thr25-2mm.nii.gz` is the Harvard-Oxford cortical structural maximum-probability atlas at 25% threshold and 2 mm resolution, distributed through Nilearn 0.14.1's `fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")` interface. Nilearn labels this image `MNI152NLin6Asym`; the participant maps are `MNI152NLin2009cAsym`. For the descriptive vmPFC ROI, this atlas was resampled to the participant-map grid with nearest-neighbor interpolation. The mask combines label indices 1 (Frontal Pole), 25 (Frontal Medial Cortex), 27 (Subcallosal Cortex), and 28 (Paracingulate Gyrus), restricted to |MNI x| <= 14 mm and z < 0. This operationalization has been used in a published vmPFC ROI definition: [Jiang et al. (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8197643/). It is an approximate cross-template anatomical localization, not a patient-specific segmentation.

SHA-256: `586d76a7defd278fcea4d83d301994d7e096aa8272d26e3c7539b4f8ebd588c1`.

Atlas documentation: [FSL standard templates and atlases](https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html).
