# Retained failed attempt

`first-run.stderr` records the first analysis attempt's postprocessing error: the helper attempted to index flattened voxel coordinates with a 3D mask. The group statistics and interim maps had been computed, but the script exited before writing the summary and figure. The issue was fixed by removing the unused indexing operation; `group_analysis.py` then reran the entire analysis from the verified inputs. No participant, voxel mask or statistical method changed because of this code correction. The failed copy of the script is retained for audit.
