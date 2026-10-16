#!/usr/bin/env python3
"""One-sample group inference on supplied NARPS AO86 participant effect maps."""
from __future__ import annotations
import hashlib, json, os, platform, sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy import stats
from nilearn import plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
SEED = 20261016
N_PERM = 9999
ALPHA = 0.05


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def main():
    meta=json.loads((INPUT/'sources.json').read_text())
    participants=pd.read_csv(INPUT/'participants.tsv',sep='\t')
    if participants.participant_id.duplicated().any(): raise ValueError('duplicate participant IDs')
    if len(participants)!=54 or set(participants.group)!={'equalIndifference'}: raise ValueError('unexpected cohort')
    paths=[]; rows=[]
    for pid in participants.participant_id:
        rel=f'data/{pid}_hypo1_cope.nii.gz'
        p=INPUT/rel
        if not p.exists(): raise FileNotFoundError(p)
        if sha256(p)!=meta['files'][rel]['sha256']: raise ValueError(f'hash mismatch {pid}')
        im=nib.load(str(p)); arr=im.get_fdata(dtype=np.float32)
        if len(im.shape)!=3 or not np.isfinite(arr).all(): raise ValueError(f'invalid image {pid}')
        if paths and (im.shape!=ref.shape or not np.allclose(im.affine,ref.affine,atol=1e-5)): raise ValueError('image geometry mismatch')
        if not paths: ref=im
        paths.append(p)
        rows.append({'participant_id':pid,'group':participants.set_index('participant_id').loc[pid,'group'],
                     'age':participants.set_index('participant_id').loc[pid,'age'],
                     'gender':participants.set_index('participant_id').loc[pid,'gender'],
                     'sha256':sha256(p),'finite_voxels':int(np.isfinite(arr).sum()),
                     'nonzero_voxels':int(np.count_nonzero(arr)), 'map_mean_all_voxels':float(arr.mean()),
                     'map_sd_all_voxels':float(arr.std()),'map_min':float(arr.min()),'map_max':float(arr.max())})
    # Zero-filled voxels outside the common upstream analysis support are not observations.
    stack=np.stack([nib.load(str(p)).get_fdata(dtype=np.float32) for p in paths],axis=0)
    mask=np.all(np.isfinite(stack)&(stack!=0),axis=0)
    if not mask.any(): raise ValueError('empty common support')
    X=stack[:,mask].astype(np.float64)
    n, v=X.shape
    # Independent, two-sided descriptive t statistics; primary direction is positive.
    mean=X.mean(axis=0); sd=X.std(axis=0,ddof=1)
    t_obs=mean/(sd/np.sqrt(n))
    p_unc=stats.t.sf(t_obs,n-1)
    # Independent literature-defined vmPFC ROI: 5 mm sphere, MNI [2, 46, -8].
    # This reported vmPFC locus is external to the present maps (Bartra et al. 2013).
    ijk=np.indices(ref.shape).reshape(3,-1).T
    xyz=nib.affines.apply_affine(ref.affine,ijk)
    roi_full=(np.linalg.norm(xyz-np.array([2.,46.,-8.]),axis=1)<=5.).reshape(ref.shape)
    roi=roi_full&mask
    if roi.sum()==0: raise ValueError('vmPFC anatomical proxy has no overlap with analysis mask')
    # Primary max-t sign-flip correction, positive one-sided familywise inference.
    rng=np.random.default_rng(SEED)
    max_null=np.empty(N_PERM,dtype=np.float64)
    # Batched multiplication limits memory while preserving exact studentized statistic.
    batch=100
    for start in range(0,N_PERM,batch):
        b=min(batch,N_PERM-start)
        signs=rng.choice(np.array([-1.,1.]),size=(b,n))
        sums=signs@X
        ss=np.sum(X*X,axis=0)[None,:]
        denom=np.sqrt(np.maximum(n*ss-sums*sums,0))
        # Exact one-sample t under participant sign flips.
        tperm=np.divide(sums*np.sqrt(n-1),denom,out=np.zeros_like(sums),where=denom>0)
        max_null[start:start+b]=np.max(tperm,axis=1)
    p_fwe=(1+np.sum(max_null[:,None]>=t_obs[None,:],axis=0))/(N_PERM+1)
    sig=(p_fwe<=ALPHA)&(t_obs>0)
    sig_vol=np.zeros(ref.shape,dtype=bool); sig_vol[mask]=sig
    # Confidence interval for descriptive ROI mean, with participant as sampling unit.
    roi_data=stack[:,roi]
    roi_sub=roi_data.mean(axis=1)
    roi_mean=float(roi_sub.mean()); roi_sd=float(roi_sub.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
    roi_ci=stats.t.interval(0.95,n-1,loc=roi_mean,scale=roi_se)
    roi_t,roi_p2=stats.ttest_1samp(roi_sub,0)
    roi_p1=float(stats.t.sf(roi_t,n-1))
    # Independent numerical check: compare one randomly selected voxel against scipy's one-sample t-test.
    check_idx=int(np.argmax(t_obs))
    check=stats.ttest_1samp(X[:,check_idx],0,alternative='greater')
    if not np.isclose(check.statistic,t_obs[check_idx],rtol=1e-10,atol=1e-10): raise AssertionError('SciPy t check failed')
    # Validate custom sign-flip studentization against SciPy for fixed patterns.
    sign_checks=np.vstack([np.ones(n),np.where(np.arange(n)%2,1.,-1.),rng.choice(np.array([-1.,1.]),size=n)])
    perm_formula=[]; perm_scipy=[]
    for s in sign_checks:
        sv=s@X[:,check_idx]
        denom_check=np.sqrt(max(n*np.sum(X[:,check_idx]**2)-sv**2,0))
        perm_formula.append(sv*np.sqrt(n-1)/denom_check)
        perm_scipy.append(float(stats.ttest_1samp(X[:,check_idx]*s,0).statistic))
    if not np.allclose(perm_formula,perm_scipy,rtol=1e-10,atol=1e-10): raise AssertionError('SciPy sign-flip check failed')
    # save analysis mask and image-space group estimates
    def save_vol(values,name,dtype=np.float32):
        vol=np.zeros(ref.shape,dtype=dtype); vol[mask]=values
        out=nib.Nifti1Image(vol,ref.affine,ref.header); out.set_data_dtype(dtype); nib.save(out,str(OUT/name))
    save_vol(mean,'mean_effect.nii.gz')
    save_vol(t_obs,'t_positive.nii.gz')
    save_vol(p_fwe,'p_fwe_positive.nii.gz')
    save_vol(sig.astype(np.uint8),'significant_fwe_mask.nii.gz',np.uint8)
    nib.save(nib.Nifti1Image(mask.astype(np.uint8),ref.affine,ref.header),str(OUT/'analysis_mask.nii.gz'))
    # compact tables and machine-readable summary
    pd.DataFrame(rows).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
    pd.DataFrame({'participant_id':participants.participant_id,'vmPFC_proxy_mean_effect':roi_sub}).to_csv(OUT/'vmPFC_participant_estimates.tsv',sep='\t',index=False)
    peak=None
    if sig.any():
        inds=np.argwhere(mask)
        # voxel with smallest corrected p among discoveries
        candidates=np.flatnonzero(sig); k=candidates[np.argmin(p_fwe[candidates])]
        ijk=inds[k]; xyz=nib.affines.apply_affine(ref.affine,ijk)
        peak={'ijk':ijk.tolist(),'xyz_mni_mm':[float(a) for a in xyz],
              'mean_effect_estimate':float(mean[k]),'t':float(t_obs[k]),'p_uncorrected_one_sided':float(p_unc[k]),'p_fwe_one_sided':float(p_fwe[k]),'in_vmPFC_proxy':bool(roi[tuple(ijk)])}
    summary={'N':n,'exclusions':[],'participant_map_count':len(paths),'analysis_mask_voxels':int(mask.sum()),'map_shape':list(ref.shape),'voxel_sizes_mm':[float(x) for x in ref.header.get_zooms()],
      'analysis_mask_rule':'finite, nonzero common support across all 54 participant maps',
      'vmPFC_roi':'Independent literature-defined 5 mm sphere centered MNI [2, 46, -8] (Bartra et al., 2013); sphere clipped to common analysis support.', 'vmPFC_roi_voxels_in_analysis_mask':int(roi.sum()),
      'primary_test':'one-sample positive group mean; participant sign-flip permutation max-t over common-support voxels', 'permutations':N_PERM,'seed':SEED,'pseudocount':'(1 + number of null maxima >= observed t) / (N_PERM + 1)','alpha_fwe':ALPHA,
      'positive_fwe_significant_voxels':int(sig.sum()),'any_positive_fwe_discovery_in_vmPFC_proxy':bool(np.any(sig_vol&roi)), 'smallest_fwe_p':float(p_fwe.min()),'peak_discovery':peak,
      'vmPFC_proxy_mean':roi_mean,'vmPFC_proxy_sd_between_participants':roi_sd,'vmPFC_proxy_95ci_t':[float(roi_ci[0]),float(roi_ci[1])],'vmPFC_proxy_t':float(roi_t),'vmPFC_proxy_p_one_sided_uncorrected':roi_p1,'vmPFC_proxy_p_two_sided_uncorrected':float(roi_p2),
      'numerical_check':'SciPy one-sample t-test agrees at maximum observed voxel; custom signed-t formula matches SciPy for three fixed sign patterns at the same voxel','max_t_check_voxel_index':check_idx,'max_t_scipy_t':float(check.statistic),'max_t_manual_t':float(t_obs[check_idx]),'sign_flip_check_t_scipy':[float(x) for x in perm_scipy],'sign_flip_check_t_formula':[float(x) for x in perm_formula],
      'versions':{'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'nibabel':nib.__version__,'nilearn':__import__('nilearn').__version__,'pandas':pd.__version__,'platform':platform.platform()},
      'input_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in paths},'participant_table_sha256':sha256(INPUT/'participants.tsv'),'source_manifest_sha256':sha256(INPUT/'sources.json')}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    np.save(OUT/'max_t_null.npy',max_null)
    # Figure 1: participant variation in anatomical ROI.
    fig,ax=plt.subplots(figsize=(6.2,4.0),constrained_layout=True)
    jitter=np.random.default_rng(SEED+1).normal(0,.045,n)
    ax.scatter(jitter,roi_sub,s=26,alpha=.72,color='#245b78',edgecolor='white',linewidth=.35,zorder=3)
    ax.errorbar([0],[roi_mean],yerr=[[roi_mean-roi_ci[0]],[roi_ci[1]-roi_mean]],fmt='D',color='#b3432f',markersize=7,capsize=5,lw=2,zorder=4,label='Mean and 95% t CI')
    ax.axhline(0,color='0.4',lw=1,ls='--'); ax.set_xlim(-.25,.25); ax.set_xticks([])
    ax.set_ylabel('Gain-effect estimate (upstream normalized regressor units)')
    ax.set_title('Participant estimates in independent vmPFC sphere (N=54)')
    ax.legend(frameon=False,loc='best'); fig.savefig(FIG/'vmPFC_roi_estimates.png',dpi=180); plt.close(fig)
    # Figure 2: only whole-brain FWE-significant positive voxels, displayed over MNI template.
    mean_sig=np.zeros(ref.shape,dtype=np.float32); mean_sig[mask]=np.where(sig,mean,0)
    stat_img=nib.Nifti1Image(mean_sig,ref.affine,ref.header)
    display=plotting.plot_glass_brain(stat_img,display_mode='lyrz',threshold=1e-12,colorbar=True,
          title='Positive gain effect: whole-brain max-t FWE p ≤ .05',plot_abs=False,
          cmap='cold_hot',vmax=float(np.max(mean[sig])) if sig.any() else None,output_file=str(FIG/'wholebrain_fwe.png'))
    display.close()
    # machine readable permutation details
    with open(OUT/'analysis_log.txt','w') as f:
        f.write('Command: python analysis/group_analysis.py\n')
        f.write(f'Input: {len(paths)} source-listed participant cope maps; all checks passed.\n')
        f.write(f'Common support: {mask.sum()} voxels; vmPFC proxy overlap: {roi.sum()} voxels.\n')
        f.write(f'Permutation max-t: {N_PERM} random sign flips, seed {SEED}; positive one-sided.\n')
        f.write(f'Discoveries at FWE alpha .05: {sig.sum()}\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
