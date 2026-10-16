#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference participant gain-effect maps."""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'input'; OUT=ROOT/'results'; FIG=ROOT/'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
meta=json.loads((IN/'sources.json').read_text())
participants=pd.read_csv(IN/'participants.tsv',sep='\t')
participants=participants[participants.group=='equalIndifference'].copy()
manifest={Path(k).name:v for k,v in meta['files'].items() if k.startswith('data/')}
assert len(participants)==54 and len(manifest)==54
# Check IDs and byte checksums; maps are original unthresholded COPE images.
participants['path']=participants.participant_id.map(lambda s: str(IN/'data'/f'{s}_hypo1_cope.nii.gz'))
assert participants.path.notna().all()
qc=[]; imgs=[]; arrays=[]; affine=None; shape=None
for r in participants.itertuples():
    p=Path(r.path); m=manifest[p.name]; b=p.read_bytes()
    assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'], p
    im=nib.load(str(p)); a=im.get_fdata(dtype=np.float32)
    if shape is None: shape=im.shape; affine=im.affine
    assert im.shape==shape and np.allclose(im.affine,affine,atol=1e-5)
    assert np.isfinite(a).all()
    imgs.append(im); arrays.append(a)
    qc.append({'participant_id':r.participant_id,'bytes':len(b),'sha256_verified':True,
               'nonzero_voxels':int(np.count_nonzero(a)), 'min':float(a.min()),'max':float(a.max()),
               'mean_nonzero':float(a[a!=0].mean()),'sd_nonzero':float(a[a!=0].std())})
pd.DataFrame(qc).to_csv(OUT/'map_qc.csv',index=False)
Y=np.stack(arrays,axis=0)
# Common analysis domain: voxels nonzero (in-brain coverage) in >=90% maps.
mask=(Y!=0).mean(axis=0)>=0.90
# Ensure mask isn't influenced by a small number of coverage outliers; report domain details.
N=Y.shape[0]; nvox=int(mask.sum())
vals=Y[:,mask].astype(np.float64)
mean=vals.mean(axis=0); sd=vals.std(axis=0,ddof=1); se=sd/np.sqrt(N)
t=mean/se
p=stats.t.sf(t,N-1) # prespecified positive direction
p_bonf=np.minimum(p*nvox,1.)
alpha=.05
sig=(p_bonf<alpha)
# Effect CI is on supplied standardized-regressor COPE units, not currency units.
crit=stats.t.ppf(.975,N-1)
low=mean-crit*se; high=mean+crit*se
# Generate maps on common source grid.
def full_img(v, fill=0):
    z=np.full(shape,fill,dtype=np.float32); z[mask]=v.astype(np.float32)
    return nib.Nifti1Image(z,affine)
mean_img=full_img(mean); t_img=full_img(t); p_img=full_img(-np.log10(np.maximum(p_bonf,1e-300)))
mean_img.to_filename(OUT/'group_mean_cope.nii.gz')
t_img.to_filename(OUT/'group_t_positive.nii.gz')
p_img.to_filename(OUT/'group_neglog10_p_bonferroni.nii.gz')
# Harvard-Oxford cortical labels provide an independent anatomical reference. Use
# medial frontal, subcallosal, and orbital frontal parcels as a broad vmPFC proxy.
atlas=datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
atlas_img=image.resample_to_img(atlas.maps,imgs[0],interpolation='nearest')
atlas_data=atlas_img.get_fdata().astype(int)
labels=list(atlas.labels)
roi_names=['Frontal Medial Cortex','Subcallosal Cortex','Frontal Orbital Cortex']
roi_ids=[labels.index(x) for x in roi_names]
coords=np.indices(shape); xcoord=coords[0]*affine[0,0]+affine[0,3]; zcoord=coords[2]*affine[2,2]+affine[2,3]
roi=(np.isin(atlas_data,roi_ids)&(np.abs(xcoord)<=24)&(zcoord<=10)&mask)
# ROI average is an interpretable secondary summary (not whole-brain corrected inference).
roi_nvox=int(roi.sum()); roi_subj=Y[:,roi].mean(axis=1)
roi_mean=float(roi_subj.mean()); roi_sd=float(roi_subj.std(ddof=1)); roi_se=roi_sd/np.sqrt(N)
roi_t=roi_mean/roi_se; roi_p=float(stats.t.sf(roi_t,N-1))
roi_ci=(roi_mean-crit*roi_se,roi_mean+crit*roi_se)
# ROI based sensitivity leave-one-out range.
loo=np.array([np.delete(roi_subj,i).mean() for i in range(N)])
# QC summary and stats
qcs=pd.DataFrame(qc)
summary={
 'n_participants':N,'excluded':[],'shape':list(shape),'nvox_common_mask':nvox,
 'mask_definition':'voxels with nonzero values in >=90% of the 54 images',
 'mask_voxelwise_finite_all':bool(np.isfinite(vals).all()),
 'whole_brain_model':'one-sample voxelwise t-test of unthresholded COPEs against 0; one-sided positive; df=53',
 'correction':'Bonferroni family-wise error correction across all common-mask voxels; alpha=.05',
 'n_fwe_significant_voxels':int(sig.sum()),
 'n_fwe_significant_voxels_in_vmPFC_proxy':int(np.sum(sig & roi[mask])),
 'peak_t':float(t.max()),'peak_coordinate_ijk':[int(q) for q in np.argwhere(mask)[np.argmax(t)]],
 'peak_mni_xyz_mm':nib.affines.apply_affine(affine,np.argwhere(mask)[np.argmax(t)]).tolist(),
 'peak_p_uncorrected':float(p.min()),'peak_p_bonferroni':float(p_bonf.min()),
 'mean_significant_voxel_cope':float(mean[sig].mean()) if sig.any() else None,
 'vmPFC_proxy_atlas':'Harvard-Oxford cortical atlas (25% max-probability): Frontal Medial, Subcallosal, Frontal Orbital parcels, restricted to |MNI x| <= 24 mm and z <= 10 mm; resampled nearest-neighbour to source grid',
 'vmPFC_proxy_nvox':roi_nvox,'vmPFC_proxy_mean_cope':roi_mean,'vmPFC_proxy_sd_between_subject':roi_sd,
 'vmPFC_proxy_ci95':[float(x) for x in roi_ci],'vmPFC_proxy_t':float(roi_t),'vmPFC_proxy_df':N-1,
 'vmPFC_proxy_p_one_sided_uncorrected':roi_p,'vmPFC_proxy_leave_one_out_mean_range':[float(loo.min()),float(loo.max())],
 'mean_image_mean_inside_mask':float(mean.mean()),'mean_within_subject_nonzero_cope_range':[float(Y.min()),float(Y.max())],
 'all_maps_verified_against_sha256':True}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
# Save participant-level ROI estimates and the corrected voxel coordinates.
vol_idx=np.argwhere(mask)
rows=[]
for j in np.where(sig)[0]:
    ijk=vol_idx[j]; rows.append({'i':int(ijk[0]),'j':int(ijk[1]),'k':int(ijk[2]),
        'x_mm':float(nib.affines.apply_affine(affine,ijk)[0]),'y_mm':float(nib.affines.apply_affine(affine,ijk)[1]),
        'z_mm':float(nib.affines.apply_affine(affine,ijk)[2]),'mean_cope':float(mean[j]),'t':float(t[j]),
        'p_uncorrected':float(p[j]),'p_bonferroni':float(p_bonf[j]),'in_vmPFC_proxy':bool(roi[tuple(ijk)])})
pd.DataFrame(rows).to_csv(OUT/'fwe_positive_voxels.csv',index=False)
# Save participant-level ROI estimates and per-voxel table.
pd.DataFrame({'participant_id':participants.participant_id,'vmPFC_proxy_mean_cope':roi_subj}).to_csv(OUT/'vmPFC_proxy_participant_estimates.csv',index=False)
# Figure 1: spatial mean and corrected positive voxels in separate, readable montages.
plotting.plot_stat_map(mean_img,display_mode='z',cut_coords=[-8,-4,0,4],threshold=0,cmap='cold_hot',
                       colorbar=True,vmax=.15,symmetric_cbar=True,title='Mean gain-effect COPE (N=54)',
                       output_file=str(FIG/'group_mean_cope.png'))
sigvals=np.zeros(nvox,dtype=float); sigvals[sig]=t[sig]; sigmap=full_img(sigvals,fill=0)
plotting.plot_stat_map(sigmap,display_mode='z',cut_coords=[-8,-4,0,4],threshold=0,cmap='Reds',
                       colorbar=True,title='Positive voxels surviving whole-brain Bonferroni FWE (p<.05)',
                       output_file=str(FIG/'whole_brain_fwe.png'))
# Keep a combined overview under the report's primary figure name.
from PIL import Image
left=Image.open(FIG/'group_mean_cope.png').convert('RGB'); right=Image.open(FIG/'whole_brain_fwe.png').convert('RGB')
h=max(left.height,right.height); left=left.resize((round(left.width*h/left.height),h)); right=right.resize((round(right.width*h/right.height),h))
canvas=Image.new('RGB',(left.width+right.width,h),'white'); canvas.paste(left,(0,0)); canvas.paste(right,(left.width,0)); canvas.save(FIG/'whole_brain_results.png')
# Figure 2: participant-level broad vmPFC proxy average and mean CI.
fig,ax=plt.subplots(figsize=(7,4.5))
ax.scatter(np.arange(1,N+1),roi_subj,s=24,color='#285f8f',alpha=.82)
ax.axhline(0,color='black',lw=1)
ax.axhline(roi_mean,color='#c33',lw=2,label=f'Mean={roi_mean:.3f}; 95% CI [{roi_ci[0]:.3f}, {roi_ci[1]:.3f}]')
ax.fill_between([0,N+1],roi_ci[0],roi_ci[1],color='#c33',alpha=.12)
ax.set(xlim=(0,N+1),xlabel='Participant (sorted by source table order)',ylabel='Mean COPE in atlas vmPFC proxy',title='Participant-level anatomical summary')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/'vmPFC_proxy_participants.png',dpi=180); plt.close(fig)
print(json.dumps(summary,indent=2))
