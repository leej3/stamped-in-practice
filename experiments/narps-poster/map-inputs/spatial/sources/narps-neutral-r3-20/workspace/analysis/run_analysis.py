#!/usr/bin/env python3
"""Group inference for supplied NARPS equal-indifference gain-effect maps."""
from __future__ import annotations
import argparse, json, hashlib, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy import ndimage
from scipy.stats import false_discovery_control
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nilearn import plotting, datasets, image

SEED = 20261016
N_PERM = 5000

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default='input')
    ap.add_argument('--results',default='results')
    ap.add_argument('--figures',default='figures')
    args=ap.parse_args(); inp=Path(args.input); out=Path(args.results); figs=Path(args.figures)
    out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True)
    participants=pd.read_csv(inp/'participants.tsv',sep='\t')
    sources=json.loads((inp/'sources.json').read_text())
    participants=participants.loc[participants.group.eq('equalIndifference')].copy()
    participants=participants.sort_values('participant_id')
    rows=[]; imgs=[]; ids=[]; ref=None
    for row in participants.itertuples():
        p=inp/'data'/f'{row.participant_id}_hypo1_cope.nii.gz'
        if not p.exists():
            rows.append(dict(participant_id=row.participant_id, included=False, reason='map missing'))
            continue
        expected=sources['files'][f'data/{p.name}']['sha256']
        actual=sha256(p)
        if actual != expected: raise ValueError(f'Input checksum mismatch: {p.name}')
        im=nib.load(p); dat=np.asarray(im.dataobj,dtype=np.float64)
        geom=(im.shape, np.round(im.affine,6))
        if ref is None: ref=(im.shape,np.round(im.affine,6))
        if im.shape != ref[0] or not np.array_equal(np.round(im.affine,6),ref[1]):
            rows.append(dict(participant_id=row.participant_id,included=False,reason='geometry mismatch'))
            continue
        finite=np.isfinite(dat); nz=finite & (dat!=0)
        imgs.append(dat); ids.append(row.participant_id)
        rows.append(dict(participant_id=row.participant_id,included=True,reason='',finite_voxels=int(finite.sum()),nonzero_voxels=int(nz.sum()),
                         finite_nonzero_min=float(np.min(dat[nz])),finite_nonzero_max=float(np.max(dat[nz])),
                         finite_nonzero_mean=float(np.mean(dat[nz])),finite_nonzero_sd=float(np.std(dat[nz],ddof=1))))
    pd.DataFrame(rows).to_csv(out/'participant_qc.tsv',sep='\t',index=False)
    Xall=np.stack(imgs,axis=0)
    # Treat shared zero-filled voxels as outside the modeled support, not observations of zero.
    mask=np.all(np.isfinite(Xall)&(Xall!=0),axis=0)
    X=Xall[:,mask]
    if X.shape[0] != 54: raise ValueError(f'Expected 54 included maps, got {X.shape[0]}')
    n,V=X.shape; df=n-1
    means=X.mean(axis=0); sd=X.std(axis=0,ddof=1); se=sd/np.sqrt(n)
    t_obs=means/se
    p_unc=stats.t.sf(t_obs,df)
    q= false_discovery_control(p_unc,method='bh')
    # Sign-flip max-t: signs are permuted at the independent participant level.
    # Batch to bound memory. Variance can be recovered from sum of squares because signs preserve it.
    rng=np.random.default_rng(SEED); maxima=np.empty(N_PERM,dtype=np.float64)
    ss=(X*X).sum(axis=0)
    for start in range(0,N_PERM,100):
        b=min(100,N_PERM-start)
        signs=rng.choice(np.array([-1.0,1.0]),size=(b,n))
        pm=signs@X/n
        pv=np.maximum((ss[None,:]-n*pm*pm)/(n-1),0.0)
        pt=np.divide(pm,np.sqrt(pv/n),out=np.zeros_like(pm),where=pv>0)
        maxima[start:start+b]=np.max(pt,axis=1)
    # Independent spot check: compare selected sign-flip t values to SciPy's direct one-sample test.
    checks=[]
    for j in range(3):
        s=rng.choice(np.array([-1.0,1.0]),size=n)
        for v in (0,V//2,V-1):
            direct=stats.ttest_1samp(X[:,v]*s,0.0).statistic
            m=float((s@X[:,v])/n)
            vv=float(max((ss[v]-n*m*m)/(n-1),0.0))
            derived=float(m/np.sqrt(vv/n))
            if not np.isclose(direct,derived,rtol=1e-10,atol=1e-10):
                raise AssertionError(f'Permutation t check failed at sample {j}, voxel {v}')
            checks.append({'sign_draw':j,'voxel_index':v,'direct_t':float(direct),'derived_t':derived})
    p_max=(1+np.sum(maxima[:,None]>=t_obs[None,:],axis=0))/(N_PERM+1)
    idx=int(np.argmax(t_obs)); coords=np.array(np.where(mask)).T
    sig_fwer=p_max<=.05
    sig_fdr=q<=.05
    sigvol=np.zeros(mask.shape,dtype=bool); sigvol[mask]=sig_fwer
    labels,nclusters=ndimage.label(sigvol,structure=np.ones((3,3,3),dtype=int))
    clusters=[]
    compact_label=labels[mask]
    for label_id in range(1,nclusters+1):
        # Locate cluster peak by matching its voxels in the compact analysis-domain array.
        cflat=np.flatnonzero(compact_label==label_id)
        peak_local=cflat[np.argmax(t_obs[cflat])]
        clusters.append({'voxels':int(len(cflat)),'peak_t':float(t_obs[peak_local]),
                         'peak_mni_mm':[float(v) for v in nib.affines.apply_affine(ref[1],coords[peak_local])]})
    # This empirical adjusted p is voxelwise max-stat family-wise error control.
    ijk=coords[idx]; mni=nib.affines.apply_affine(ref[1],ijk).tolist()
    # Transparent anatomical approximation for descriptive vmPFC summaries only.
    # The whole-brain map, not this ROI, determines support for the hypothesis.
    roi_center=np.array([0.0,44.0,-12.0]); roi_radius=15.0
    xyz=nib.affines.apply_affine(ref[1],coords)
    roi=(np.linalg.norm(xyz-roi_center[None,:],axis=1)<=roi_radius)
    if not roi.any(): raise ValueError('vmPFC sphere has no overlap with analysis mask')
    ridx=int(np.argmax(t_obs[roi])); roi_flat=np.flatnonzero(roi)[ridx]
    roi_peak_ijk=coords[roi_flat]; roi_peak_mni=xyz[roi_flat]
    roi_means=X[:,roi].mean(axis=1)
    roi_mean=float(roi_means.mean()); roi_se=float(roi_means.std(ddof=1)/np.sqrt(n))
    # One-sided parametric CI is included as effect-size context; separate from permutation p.
    tcrit=stats.t.ppf(.975,df)
    summary={
      'n_expected':int(len(participants)),'n_included':int(n),'n_excluded':int(len(participants)-n),
      'included_ids':ids,'analysis_mask_voxels':int(V),'mask_rule':'intersection across maps of finite and nonzero voxels (shared zero-filled background omitted)',
      'shape':list(ref[0]),'affine':ref[1].tolist(),'voxel_size_mm':nib.load(inp/'data'/f'{ids[0]}_hypo1_cope.nii.gz').header.get_zooms()[:3],
      'group_model':'one-sample equal-weight t test across participant effect estimates, df=53',
      'primary_correction':'one-sided sign-flip max-t whole-brain FWER, Monte Carlo',
      'permutations':N_PERM,'seed':SEED,'max_t_corrected_p_at_positive_peak':float(p_max[idx]),
      'fwer_significant_voxels':int(sig_fwer.sum()),'fwer_significant_clusters_26_neighbor':clusters,
      'fdr_bh_significant_voxels_secondary':int(sig_fdr.sum()),
      'independent_statistic_checks':checks,
      'fdr_bh_q_at_positive_peak':float(q[idx]),'uncorrected_one_sided_p_at_positive_peak':float(p_unc[idx]),
      'positive_peak_t':float(t_obs[idx]),'positive_peak_mean_effect':float(means[idx]),
      'positive_peak_ci95_t_based':[float(means[idx]-tcrit*se[idx]),float(means[idx]+tcrit*se[idx])],
      'positive_peak_mni_mm':[float(x) for x in mni], 'positive_peak_ijk':[int(x) for x in ijk],
      'vmPFC_operational_definition':'15 mm radius sphere centered at MNI (0, 44, -12); descriptive only, not used to determine support',
      'vmPFC_sphere_voxels':int(roi.sum()),'vmPFC_sphere_mean_effect':roi_mean,
      'vmPFC_sphere_mean_ci95_t_based':[float(roi_mean-tcrit*roi_se),float(roi_mean+tcrit*roi_se)],
      'vmPFC_sphere_mean_t':float(roi_mean/roi_se),
      'vmPFC_sphere_mean_one_sided_p':float(stats.t.sf(roi_mean/roi_se,df)),
      'vmPFC_sphere_peak_t':float(t_obs[roi_flat]),'vmPFC_sphere_peak_mni_mm':[float(x) for x in roi_peak_mni],
      'vmPFC_sphere_peak_fwer_maxT_p':float(p_max[roi_flat]),
      'max_t_null_95th_percentile':float(np.quantile(maxima,.95)),
      'whole_brain_mean_of_voxelwise_group_means':float(np.mean(means)),
      'median_voxelwise_bh_q':float(np.median(q)),
      'runtime':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,'pandas':pd.__version__,'nibabel':nib.__version__,'nilearn':__import__('nilearn').__version__,'matplotlib':matplotlib.__version__},
      'input_sha256':{i:sha256(inp/'data'/f'{i}_hypo1_cope.nii.gz') for i in ids},
      'participants_sha256':sha256(inp/'participants.tsv'),
      'sources_manifest_sha256':sha256(inp/'sources.json'),
      'analysis_code_sha256':sha256(Path(__file__)),
      'protocol_sha256':sha256(Path('protocol.md')),
      'pixi_manifest_sha256':sha256(Path('pixi.toml')),
      'pixi_lock_sha256':sha256(Path('pixi.lock'))}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,default=lambda o:list(o) if hasattr(o,'__iter__') else str(o))+'\n')
    # Save the unthresholded mean effect, t and FWER/FDR p maps in original grid.
    meanvol=np.zeros(mask.shape); tvol=np.zeros(mask.shape); pvol=np.ones(mask.shape); qvol=np.ones(mask.shape)
    meanvol[mask]=means; tvol[mask]=t_obs; pvol[mask]=p_max; qvol[mask]=q
    for name,data in [('group_mean_effect',meanvol),('group_t',tvol),('group_p_fwer_maxT',pvol),('group_q_bh',qvol)]:
        nib.save(nib.Nifti1Image(data.astype(np.float32),ref[1]),out/f'{name}.nii.gz')
    voxel=pd.DataFrame({'mean_effect':means,'t':t_obs,'p_one_sided':p_unc,'q_bh':q,'p_fwer_maxT':p_max})
    voxel.to_csv(out/'voxelwise_results.tsv.gz',sep='\t',index=False,compression='gzip')
    pd.DataFrame({'permutation_max_t':maxima}).to_csv(out/'max_t_null.tsv',sep='\t',index=False)
    pd.DataFrame({'participant_id':ids,'vmPFC_sphere_mean_effect':roi_means}).to_csv(out/'vmPFC_participant_summary.tsv',sep='\t',index=False)
    # Primary display: unthresholded mean map with group t statistic, plus maxT threshold.
    mean_img=nib.Nifti1Image(meanvol.astype(np.float32),ref[1]); t_img=nib.Nifti1Image(tvol.astype(np.float32),ref[1])
    fig=plt.figure(figsize=(12,5))
    d1=plotting.plot_stat_map(mean_img,display_mode='ortho',cut_coords=tuple(mni),
        title='Mean gain-effect estimate (unthresholded)',threshold=None,colorbar=True,
        cmap='cold_hot',vmin=-0.15,vmax=0.15,figure=fig,axes=(.02,.08,.47,.84),black_bg=False)
    d2=plotting.plot_stat_map(t_img,display_mode='ortho',cut_coords=tuple(mni),
        title='Group t statistic thresholded at one-sided max-T FWER .05',
        threshold=float(np.quantile(maxima,.95)),colorbar=True,cmap='cold_hot',figure=fig,axes=(.52,.08,.46,.84),black_bg=False)
    fig.suptitle('NARPS equal-indifference group: potential gain effect',fontsize=14)
    fig.savefig(figs/'whole_brain_group.png',dpi=180,bbox_inches='tight'); plt.close(fig)
    # Participant variation at positive peak; participant estimates rather than pseudo-observations.
    vals=roi_means
    fig,ax=plt.subplots(figsize=(7,4.2))
    rng=np.random.default_rng(SEED); ax.scatter(rng.normal(0,.055,n),vals,s=22,alpha=.72,color='#276FBF',edgecolor='white',linewidth=.3)
    ax.axhline(0,color='black',linewidth=1,linestyle='--')
    ax.axhline(roi_mean,color='#C23B22',linewidth=2,label=f'mean = {roi_mean:.3g}')
    ax.fill_between([-.18,.18],roi_mean-tcrit*roi_se,roi_mean+tcrit*roi_se,color='#C23B22',alpha=.15,label='95% t interval')
    ax.set(xlim=(-.2,.2),xlabel='Jitter (display only)',ylabel='Mean effect estimate within sphere',title='Participant-level mean effects in descriptive vmPFC sphere\n(MNI center 0, 44, −12 mm; radius 15 mm)')
    ax.set_xticks([]); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(figs/'peak_participant_effects.png',dpi=180); plt.close(fig)
    print(json.dumps({k:summary[k] for k in ['n_included','n_excluded','analysis_mask_voxels','fwer_significant_voxels','fwer_significant_clusters_26_neighbor','fdr_bh_significant_voxels_secondary','positive_peak_t','positive_peak_mean_effect','positive_peak_ci95_t_based','positive_peak_mni_mm','max_t_corrected_p_at_positive_peak','fdr_bh_q_at_positive_peak','vmPFC_sphere_voxels','vmPFC_sphere_mean_effect','vmPFC_sphere_mean_ci95_t_based','vmPFC_sphere_mean_one_sided_p','vmPFC_sphere_peak_t','vmPFC_sphere_peak_mni_mm','vmPFC_sphere_peak_fwer_maxT_p']},indent=2))
if __name__=='__main__': main()
