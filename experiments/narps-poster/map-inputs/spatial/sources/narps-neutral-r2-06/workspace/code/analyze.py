#!/usr/bin/env python3
"""Group inference for fixed NARPS AO86 gain-effect maps."""
from pathlib import Path
import argparse, hashlib, json, platform, sys
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'input'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
ROI = {'x_mm': [-12, 12], 'y_mm': [25, 60], 'z_mm': [-10, 10]}

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true', help='QC first 3 maps only; no inference')
    args=ap.parse_args()
    meta=pd.read_csv(INPUT/'participants.tsv',sep='\t')
    assert meta.participant_id.is_unique
    assert set(meta.group)=={'equalIndifference'}
    source_manifest=json.loads((INPUT/'sources.json').read_text())
    rows=[]
    paths=[]
    for pid in meta.participant_id:
        p=INPUT/'data'/f'{pid}_hypo1_cope.nii.gz'
        if not p.exists(): raise FileNotFoundError(p)
        paths.append(p)
    use_n=3 if args.pilot else len(paths)
    imgs=[nib.load(str(p)) for p in paths[:use_n]]
    ref=imgs[0]
    for p,img in zip(paths[:use_n],imgs):
        if img.shape!=ref.shape or not np.allclose(img.affine,ref.affine,atol=1e-5):
            raise ValueError(f'geometry mismatch: {p}')
        a=img.get_fdata(dtype=np.float32)
        finite=np.isfinite(a)
        nonzero=finite&(a!=0)
        actual_hash=sha256(p)
        expected_hash=source_manifest['files'][str(p.relative_to(INPUT))]['sha256']
        if actual_hash!=expected_hash: raise ValueError(f'checksum mismatch: {p}')
        rows.append({'participant_id':p.name.split('_')[0], 'path':str(p.relative_to(ROOT)), 'sha256':actual_hash,
                     'shape':'x'.join(map(str,img.shape)), 'finite_fraction':float(finite.mean()),
                     'nonzero_fraction':float(nonzero.mean()), 'nonzero_mean':float(a[nonzero].mean()),
                     'nonzero_sd':float(a[nonzero].std()), 'nonzero_min':float(a[nonzero].min()),
                     'nonzero_max':float(a[nonzero].max())})
    if args.pilot:
        OUT.mkdir(exist_ok=True)
        pd.DataFrame(rows).to_csv(OUT/'pilot_qc.csv',index=False)
        print(json.dumps({'pilot_maps':len(rows),'shape':ref.shape,'affine':ref.affine.tolist(),'qc':'passed'},indent=2))
        return
    data=np.stack([img.get_fdata(dtype=np.float32) for img in imgs],axis=0)
    support=np.isfinite(data)&(data!=0)
    common=support.all(axis=0)
    n=int(common.sum())
    if n==0: raise ValueError('empty shared nonzero support')
    x=data[:,common].astype(np.float64)
    means=x.mean(axis=0)
    sd=x.std(axis=0,ddof=1)
    t=means/(sd/np.sqrt(x.shape[0]))
    df=x.shape[0]-1
    p1=stats.t.sf(t,df)
    p2=stats.t.sf(np.abs(t),df)*2
    padj=np.minimum(p1*n,1.0)
    # Return the lower-bound corrected p values; ties and spatial correlation do not invalidate Bonferroni.
    roi_grid=np.indices(ref.shape,dtype=np.float32)
    xyz=nib.affines.apply_affine(ref.affine,roi_grid.reshape(3,-1).T).T.reshape((3,)+ref.shape)
    roi=(np.abs(xyz[0])<=12)&(xyz[1]>=25)&(xyz[1]<=60)&(xyz[2]>=-10)&(xyz[2]<=10)&common
    r=int(roi.sum())
    if r==0: raise ValueError('empty vmPFC ROI coverage')
    xr=data[:,roi].mean(axis=1)
    roi_mean=float(xr.mean()); roi_sd=float(xr.std(ddof=1)); roi_se=roi_sd/np.sqrt(len(xr))
    roi_t=roi_mean/roi_se
    roi_p=float(stats.t.sf(roi_t,len(xr)-1))
    roi_ci=stats.t.interval(.95,len(xr)-1,loc=roi_mean,scale=roi_se)
    # map outputs keep original geometry; zeros outside the analyzed intersection.
    def save_map(vals,name,dtype=np.float32):
        full=np.zeros(ref.shape,dtype=dtype); full[common]=vals
        img=nib.Nifti1Image(full,ref.affine,ref.header.copy()); img.set_data_dtype(dtype)
        nib.save(img,str(OUT/name))
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    save_map(means,'group_mean_effect.nii.gz')
    save_map(t,'group_t_positive.nii.gz')
    save_map(padj,'wholebrain_bonferroni_p.nii.gz')
    pd.DataFrame(rows).to_csv(OUT/'participant_qc.csv',index=False)
    sig_indices=np.flatnonzero(padj<=.05)
    sig_coords=np.argwhere(common)[sig_indices]
    sig_rows=[]
    for c,idx in zip(sig_coords,sig_indices):
        q=nib.affines.apply_affine(ref.affine,c)
        sig_rows.append({'x_mm':q[0],'y_mm':q[1],'z_mm':q[2],'mean_effect':means[idx],
                         't':t[idx],'p_uncorrected':p1[idx],'p_bonferroni_fwe':padj[idx]})
    pd.DataFrame(sig_rows).to_csv(OUT/'wholebrain_significant_voxels.csv',index=False)
    vox=pd.DataFrame({'n_voxels': [n], 'df':[df], 'one_sided_bonferroni_alpha_0.05_t':[float(stats.t.isf(.05/n,df))],
                      'max_t_positive':[float(t.max())], 'max_t_xyz_mm':[';'.join(f'{v:.1f}' for v in nib.affines.apply_affine(ref.affine,np.argwhere(common)[int(np.argmax(t))]))],
                      'strongest_positive_p_uncorrected':[float(p1.min())], 'strongest_positive_p_bonferroni':[float(padj.min())], 'significant_voxels_fwe_0_05':[int((padj<=.05).sum())]})
    vox.to_csv(OUT/'wholebrain_summary.csv',index=False)
    pd.DataFrame([{'roi_definition':json.dumps(ROI),'roi_voxels':r,'n_participants':len(xr),'mean_effect':roi_mean,'sd_between_participants':roi_sd,'se':roi_se,
                   'ci95_low':float(roi_ci[0]),'ci95_high':float(roi_ci[1]),'t':float(roi_t),'df':df,'one_sided_p_descriptive':roi_p,
                   'participants_positive_roi_mean':int((xr>0).sum()),'participant_roi_means_median':float(np.median(xr))}]).to_csv(OUT/'vmPFC_roi_summary.csv',index=False)
    pd.DataFrame({'participant_id':meta.participant_id,'roi_mean_effect':data[:,roi].mean(axis=1)}).to_csv(OUT/'participant_roi_means.csv',index=False)
    # Render whole-brain mean with ROI outline, plus participant ROI distribution.
    fig=plt.figure(figsize=(12,4.8))
    display=plotting.plot_stat_map(OUT/'group_mean_effect.nii.gz',display_mode='z',cut_coords=[-6,0,6,12],
        threshold=None, cmap='cold_hot', colorbar=True, title='Mean modeled gain effect (unthresholded)',
        figure=fig, resampling_interpolation='continuous', black_bg=False, annotate=True, draw_cross=False)
    display.add_contours(nib.Nifti1Image(roi.astype(np.uint8),ref.affine),levels=[.5],colors='cyan',linewidths=1)
    display.savefig(FIG/'group_mean_slices.png',dpi=180)
    display.close()
    plt.close(fig)
    peak_coord=nib.affines.apply_affine(ref.affine,np.argwhere(common)[int(np.argmax(t))])
    fig=plt.figure(figsize=(8,6))
    fwe_thr=float(stats.t.isf(.05/n,df))
    display=plotting.plot_stat_map(OUT/'group_t_positive.nii.gz',display_mode='ortho',cut_coords=peak_coord,
        threshold=fwe_thr,cmap='hot',colorbar=True,title='Positive whole-brain Bonferroni FWE (α=.05)',
        figure=fig,resampling_interpolation='nearest',black_bg=False,annotate=True,draw_cross=False)
    display.add_contours(nib.Nifti1Image(roi.astype(np.uint8),ref.affine),levels=[.5],colors='cyan',linewidths=1)
    display.savefig(FIG/'wholebrain_fwe_positive.png',dpi=180)
    display.close()
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.2,5),constrained_layout=True)
    ax.axhline(0,color='0.5',lw=1)
    jitter=np.linspace(-.12,.12,len(xr))
    ax.scatter(jitter,xr,s=28,alpha=.7,color='#315a7d',edgecolor='none')
    ax.errorbar([0],[roi_mean],yerr=[[roi_mean-roi_ci[0]],[roi_ci[1]-roi_mean]],fmt='o',color='#b3452e',capsize=5,lw=2,label='Mean ± 95% t CI')
    ax.set(xlim=(-.28,.28),xticks=[0],xticklabels=['vmPFC ROI'],ylabel='Participant mean modeled gain effect',title='Participant variation in vmPFC')
    ax.legend(frameon=False,loc='best')
    fig.savefig(FIG/'vmPFC_roi_distribution.png',dpi=180)
    plt.close(fig)
    # Threshold map and statistical rendering for inferential localization.
    sig=padj<=.05
    save_map(np.where(sig,t,0),'wholebrain_fwe_t_positive.nii.gz')
    with open(OUT/'run_metadata.json','w') as f:
        json.dump({'n_participants':len(paths),'n_analyzed_voxels':n,'reference_shape':ref.shape,'affine':ref.affine.tolist(),
          'method':'one-sample t, one-sided positive; Bonferroni over shared nonzero support','df':df,'fwe_alpha':.05,
          'roi':ROI,'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,
          'nilearn':__import__('nilearn').__version__,'pandas':pd.__version__,'nibabel':nib.__version__,'inputs_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in paths},
          'participants_tsv_sha256':sha256(INPUT/'participants.tsv'),'sources_json_sha256':sha256(INPUT/'sources.json'),
          'protocol_sha256':sha256(ROOT/'protocol.md'),'analysis_script_sha256':sha256(Path(__file__))},f,indent=2)
    print(json.dumps({'participants':len(paths),'voxels':n,'roi_voxels':r,'roi_mean':roi_mean,'roi_ci95':[float(roi_ci[0]),float(roi_ci[1])],
                      'roi_p_descriptive':roi_p,'wholebrain_min_p_fwe':float(padj.min()),'significant_voxels':int(sig.sum())},indent=2))
if __name__=='__main__': main()
