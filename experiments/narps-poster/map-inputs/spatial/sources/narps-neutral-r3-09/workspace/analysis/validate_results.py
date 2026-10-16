"""Independent numerical cross-check of delivered group summaries."""
import json
from pathlib import Path
import numpy as np, pandas as pd, nibabel as nib
from scipy import stats
root=Path(__file__).resolve().parents[1]
sources=json.loads((root/'input/sources.json').read_text())
participants=pd.read_csv(root/'input/participants.tsv',sep='\t')
images={v['participant_id']:root/'input'/k for k,v in sources['files'].items() if 'participant_id' in v}
ref=nib.load(str(images[participants.participant_id.iloc[0]]))
roi_sum=[]
for pid in participants.participant_id:
    im=nib.load(str(images[pid])); assert im.shape==ref.shape and np.allclose(im.affine,ref.affine)
    a=im.get_fdata(dtype=np.float32)
    ii,jj,kk=np.indices(a.shape)
    x=2*ii-96; y=2*jj-132; z=2.4*kk-78
    mask=(np.abs(x)<=20)&(y>=20)&(y<=60)&(z>=-20)&(z<=5)
    # The ROI is intersected with all-participant common nonzero coverage below.
    roi_sum.append(a)
stack=np.stack(roi_sum)
common=np.all(np.isfinite(stack)&(stack!=0),axis=0)
ii,jj,kk=np.indices(ref.shape); x=2*ii-96; y=2*jj-132; z=2.4*kk-78
roi=common&(np.abs(x)<=20)&(y>=20)&(y<=60)&(z>=-20)&(z<=5)
sub_roi=stack[:,roi].mean(axis=1)
t,p=stats.ttest_1samp(sub_roi,0)
ci=stats.t.interval(.95,len(sub_roi)-1,loc=sub_roi.mean(),scale=stats.sem(sub_roi))
res=json.loads((root/'results/group_results.json').read_text())
tmap=nib.load(str(root/'results/group_t.nii.gz')).get_fdata()
maxima=pd.read_csv(root/'results/permutation_max_t.tsv.gz',sep='\t').max_t.to_numpy()
check={
 'participant_count_matches':len(participants)==res['N']==54,
 'common_mask_count_matches':int(common.sum())==res['common_nonzero_support_voxels'],
 'roi_voxel_count_matches':int(roi.sum())==res['roi_voxels'],
 'roi_mean_independent':float(sub_roi.mean()),'roi_t_independent':float(t),'roi_p_two_sided_independent':float(p),
 'roi_ci_independent':[float(ci[0]),float(ci[1])],
 'roi_mean_matches':bool(np.isclose(sub_roi.mean(),res['roi_participant_mean_estimate'],rtol=1e-6,atol=1e-8)),
 'roi_ci_matches':bool(np.allclose(ci,res['roi_mean_95pct_t_ci'],rtol=1e-6,atol=1e-8)),
 'max_t_map_matches':bool(np.isclose(tmap[common].max(),res['max_t_observed_whole_brain'],rtol=1e-6)),
 'permutation_threshold_matches':bool(np.isclose(np.quantile(maxima,.95,method='higher'),res['max_t_threshold_95pct'])),
 'permutation_corrected_max_p_independent':float((1+(maxima>=tmap[common].max()).sum())/(len(maxima)+1)),
 'whole_brain_significant_voxel_count_independent':int((tmap[common]>=res['max_t_threshold_95pct']).sum()),
}
assert all(check[k] for k in ['participant_count_matches','common_mask_count_matches','roi_voxel_count_matches','roi_mean_matches','roi_ci_matches','max_t_map_matches','permutation_threshold_matches'])
(root/'results/independent_validation.json').write_text(json.dumps(check,indent=2)+'\n')
print(json.dumps(check,indent=2))
