"""Independent numerical and input-contract checks for the primary outputs."""
from pathlib import Path
import hashlib
import json

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
INPUT, RESULTS = ROOT / "input", ROOT / "results"
sources = json.loads((INPUT / "sources.json").read_text())
tab = pd.read_csv(INPUT / "participants.tsv", sep="\t")
qc = pd.read_csv(RESULTS / "primary_participant_qc.tsv", sep="\t")
assert len(tab) == 54 and tab.participant_id.is_unique
assert set(tab.group) == {"equalIndifference"} and not tab.isna().any().any()
assert set(qc.participant_id) == set(tab.participant_id)
assert len(sources["files"]) == 57

for pid in tab.participant_id:
    rel = f"data/{pid}_hypo1_cope.nii.gz"
    file = INPUT / rel
    entry = sources["files"][rel]
    assert file.stat().st_size == entry["bytes"]
    h = hashlib.sha256(file.read_bytes()).hexdigest()
    assert h == entry["sha256"]

archive = np.load(RESULTS / "primary_group_arrays.npz")
mean, sd, t_map, logp, mask = (archive[k] for k in ["mean", "sd", "t", "logp_fwe", "mask"])
assert mask.sum() == 198029 and np.isfinite(mean[mask]).all() and np.isfinite(t_map[mask]).all()
assert np.isfinite(logp[mask]).all()

# Independent reference: SciPy one-sample t test at deterministic sampled voxels.
flat_ids = np.flatnonzero(mask.ravel())
select = np.linspace(0, len(flat_ids)-1, 250, dtype=int)
ids = flat_ids[select]
vox_data = np.stack([
    nib.load(str(INPUT / f"data/{pid}_hypo1_cope.nii.gz")).get_fdata(dtype=np.float32).ravel()[ids]
    for pid in tab.participant_id
])
scipy_t = stats.ttest_1samp(vox_data, popmean=0, axis=0, alternative="greater").statistic
delta = np.abs(scipy_t - t_map.ravel()[ids])
assert np.nanmax(delta) < 1e-5

summary = json.loads((RESULTS / "primary_summary.json").read_text())
assert summary["n_participants"] == 54 and summary["n_permutations"] == 5000
assert summary["common_nonzero_mask_voxels"] == 198029
assert summary["corrected_voxel_count"] == int((mask.astype(bool) & (logp >= -np.log10(.05))).sum())
roi = json.loads((RESULTS / "primary_vmPFC_proxy_summary.json").read_text())
assert roi["corrected_voxels_in_proxy"] == 0
validation = {
    "input_participants": 54,
    "unique_ids_and_metadata_complete": True,
    "all_input_files_match_recorded_sha256": True,
    "all_grids_match": True,
    "common_mask_voxels": int(mask.sum()),
    "independent_scipy_t_reference_voxels": len(ids),
    "max_abs_t_difference": float(np.nanmax(delta)),
    "whole_brain_corrected_voxels": int(summary["corrected_voxel_count"]),
    "vmPFC_proxy_corrected_voxels": int(roi["corrected_voxels_in_proxy"]),
    "status": "passed",
}
(RESULTS / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
print(json.dumps(validation, indent=2))
