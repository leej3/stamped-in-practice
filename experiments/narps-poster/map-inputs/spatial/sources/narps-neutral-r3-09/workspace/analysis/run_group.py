#!/usr/bin/env python3
"""Group analysis of supplied NARPS AO86 participant gain contrast maps."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import ndimage, stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'input'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
SEED = 20261016


def load_inputs():
    participants = pd.read_csv(INPUT / 'participants.tsv', sep='\t')
    sources = json.loads((INPUT / 'sources.json').read_text())
    files = sources['files']
    if len(participants) != 54:
        raise ValueError(f'Expected 54 participants; got {len(participants)}')
    if participants.participant_id.duplicated().any():
        raise ValueError('Duplicate participant IDs')
    if set(participants.group) != {'equalIndifference'}:
        raise ValueError('Unexpected group in participants.tsv')
    arrays=[]; paths=[]; ref=None; qcs=[]
    for row in participants.itertuples():
        matches=[k for k,v in files.items() if v.get('participant_id')==row.participant_id]
        if len(matches)!=1: raise ValueError(f'{row.participant_id}: expected exactly one source map')
        rel=matches[0]; p=INPUT/rel
        if not p.is_file(): raise FileNotFoundError(p)
        info=files[rel]
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest != info['sha256'] or p.stat().st_size != info['bytes']:
            raise ValueError(f'Checksum/size mismatch: {rel}')
        img=nib.load(str(p)); arr=img.get_fdata(dtype=np.float32)
        if ref is None: ref=img
        if arr.shape != ref.shape or not np.allclose(img.affine,ref.affine,atol=1e-5):
            raise ValueError(f'Shape/affine mismatch: {rel}')
        finite=np.isfinite(arr)
        qcs.append({'participant_id':row.participant_id,'finite_fraction':float(finite.mean()),
                    'nonzero_fraction':float((finite & (arr!=0)).mean()),
                    'nonzero_mean':float(arr[finite & (arr!=0)].mean()),
                    'nonzero_sd':float(arr[finite & (arr!=0)].std()),
                    'nonzero_min':float(arr[finite & (arr!=0)].min()),
                    'nonzero_max':float(arr[finite & (arr!=0)].max())})
        arrays.append(arr); paths.append(rel)
    stack=np.stack(arrays)
    mask=np.all(np.isfinite(stack) & (stack!=0),axis=0)
    if mask.sum()<10000: raise ValueError(f'Unexpectedly small common-support mask: {mask.sum()}')
    X=stack[:,mask].astype(np.float64)
    if not np.isfinite(X).all(): raise ValueError('Nonfinite values in common support')
    return participants, sources, ref, stack, mask, X, pd.DataFrame(qcs)


def tmap(X):
    n=X.shape[0]
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=1)
    t=np.divide(mu*np.sqrt(n),sd,out=np.zeros_like(mu),where=sd>0)
    return mu, sd, t


def permutation_max_t(X, n_perm, seed, chunk=12000):
    """Monte Carlo sign flips; max positive one-sided t controls whole-map FWE."""
    rng=np.random.default_rng(seed); n,p=X.shape
    signs=rng.choice(np.array([-1.,1.]),size=(n_perm,n))
    ss=np.einsum('ij,ij->j',X,X)
    maxima=np.empty(n_perm,dtype=np.float64)
    for start in range(0,p,chunk):
        stop=min(start+chunk,p); block=X[:,start:stop]
        means=(signs @ block)/n
        den=np.sqrt(np.maximum((ss[start:stop][None,:]-n*means*means)/(n-1),0)/n)
        tt=np.divide(means,den,out=np.zeros_like(means),where=den>0)
        maxima=np.maximum(maxima,tt.max(axis=1)) if start else tt.max(axis=1)
    return maxima


def xyz(affine, ijk):
    return nib.affines.apply_affine(affine,np.asarray(ijk))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--permutations',type=int,default=5000)
    ap.add_argument('--seed',type=int,default=SEED)
    ap.add_argument('--pilot',action='store_true')
    args=ap.parse_args()
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    t0=time.time()
    participants,sources,ref,stack,mask,X,qc=load_inputs()
    if args.pilot:
        # Small deterministic execution check, separate from confirmatory outputs.
        XX=X[:12]
        mu,sd,t=tmap(XX)
        null=permutation_max_t(XX,199,args.seed,chunk=5000)
        record={'pilot_n':12,'pilot_voxels':int(mask.sum()),'pilot_permutations':199,
                'pilot_max_t_observed':float(t.max()),'pilot_max_t_null_95':float(np.quantile(null,.95)),
                'pilot_finite':bool(np.isfinite(null).all()),'elapsed_seconds':time.time()-t0}
        (OUT/'pilot.json').write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(record,indent=2)); return
    if args.permutations<999: raise ValueError('Use >=999 permutations for full inference')
    n=X.shape[0]; mu,sd,obs_t=tmap(X)
    maxima=permutation_max_t(X,args.permutations,args.seed)
    threshold=float(np.quantile(maxima,.95,method='higher'))
    # Compute corrected voxel p values in blocks to keep memory bounded.
    p_fwe=np.empty_like(obs_t)
    for start in range(0,len(obs_t),12000):
        stop=min(start+12000,len(obs_t))
        p_fwe[start:stop]=(1+(maxima[:,None]>=obs_t[None,start:stop]).sum(axis=0))/(args.permutations+1)
    sig=obs_t>=threshold
    # Coordinate mask for approximate vmPFC localization, defined without reference to outcomes.
    ijk=np.column_stack(np.where(mask)); mm=xyz(ref.affine,ijk)
    roi=(np.abs(mm[:,0])<=20)&(mm[:,1]>=20)&(mm[:,1]<=60)&(mm[:,2]>=-20)&(mm[:,2]<=5)
    if roi.sum()==0: raise ValueError('Empty vmPFC coordinate envelope')
    roi_mean=X[:,roi].mean(axis=1)
    roi_avg=float(roi_mean.mean()); roi_sd=float(roi_mean.std(ddof=1)); roi_sem=roi_sd/np.sqrt(n)
    ci=stats.t.interval(.95,n-1,loc=roi_avg,scale=roi_sem)
    t_roi,p_roi=stats.ttest_1samp(roi_mean,0)
    # Whole-brain significant clusters, using face connectivity for conservative anatomical contiguity.
    sigvol=np.zeros(mask.shape,bool); sigvol[mask]=sig
    labels,nlab=ndimage.label(sigvol,structure=ndimage.generate_binary_structure(3,1))
    clusters=[]
    for lab in range(1,nlab+1):
        inds=np.argwhere(labels==lab); vals=obs_t[labels[mask]==lab] if False else None
        coords=inds; coord_mm=xyz(ref.affine,coords)
        index=np.ravel_multi_index(inds.T,mask.shape)
        # map flat volume indices into compact vector indices
        rank=np.full(mask.shape,-1,int); rank[mask]=np.arange(mask.sum())
        compact=rank[tuple(inds.T)]; peak_local=int(np.argmax(obs_t[compact])); peak_ijk=inds[peak_local]
        clusters.append({'cluster':lab,'voxels':int(len(inds)),'peak_t':float(obs_t[compact[peak_local]]),
                         'peak_mni_mm':[round(float(v),1) for v in xyz(ref.affine,peak_ijk)],
                         'peak_voxel_ijk':[int(v) for v in peak_ijk],
                         'vmPFC_overlap_voxels':int(roi[np.isin(np.flatnonzero(mask),index)].sum())})
    clusters.sort(key=lambda c:-c['voxels'])
    p_max=(1+int((maxima>=obs_t.max()).sum()))/(args.permutations+1)
    summary={'analysis':'one-sample positive mean; participant sign-flip max-t whole-brain FWE',
      'N':n,'participant_ids':participants.participant_id.tolist(),'maps_included':n,
      'shape':list(ref.shape),'affine':ref.affine.tolist(),'voxel_size_mm':[float(np.linalg.norm(ref.affine[:3,i])) for i in range(3)],
      'common_nonzero_support_voxels':int(mask.sum()),'mask_definition':'finite and nonzero in all 54 participants',
      'permutations':args.permutations,'seed':args.seed,'direction':'positive, one-sided','alpha':.05,
      'max_t_threshold_95pct':threshold,'max_t_observed_whole_brain':float(obs_t.max()),
      'max_t_whole_brain_fwe_p_monte_carlo':p_max,
      'minimum_monte_carlo_p':1/(args.permutations+1),'significant_voxels':int(sig.sum()),
      'clusters_6_connected':clusters,'roi_definition_mni_mm':{'x':[-20,20],'y':[20,60],'z':[-20,5]},
      'roi_voxels':int(roi.sum()),'roi_participant_mean_estimate':roi_avg,'roi_between_participant_sd':roi_sd,
      'roi_mean_95pct_t_ci':[float(ci[0]),float(ci[1])],'roi_one_sample_t':float(t_roi),'roi_two_sided_uncorrected_p':float(p_roi),
      'roi_whole_brain_significant_voxels':int((sig & roi).sum()),
      'permutation_max_t_null_95pct':threshold,'permutation_max_t_null_99pct':float(np.quantile(maxima,.99,method='higher')),
      'max_t_null_mean':float(maxima.mean()),'elapsed_seconds':time.time()-t0,
      'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,
      'nibabel':nib.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__}
    (OUT/'group_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    qc.to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
    pd.DataFrame({'max_t':maxima}).to_csv(OUT/'permutation_max_t.tsv.gz',sep='\t',index=False,compression='gzip')
    # T, mean and corrected p maps retain the common support only.
    for name, vals in [('mean_effect',mu),('group_t',obs_t),('whole_brain_fwe_p',p_fwe)]:
        vol=np.zeros(mask.shape,np.float32); vol[mask]=vals.astype(np.float32)
        nib.save(nib.Nifti1Image(vol,ref.affine,ref.header),str(OUT/f'{name}.nii.gz'))
    # Figure 1: full-brain max-T significant voxels with thresholded t-stat display.
    from nilearn import plotting
    support_img=nib.Nifti1Image(mask.astype(np.float32),ref.affine,ref.header)
    display=plotting.plot_stat_map(OUT/'group_t.nii.gz',bg_img=support_img,threshold=threshold,
        cut_coords=(0,-96,-4),display_mode='ortho',cmap='hot',symmetric_cbar=False,
        title='Positive gain effect: whole-brain max-T FWE; t > %.2f' % threshold,colorbar=True,annotate=True,draw_cross=False)
    display.savefig(FIG/'whole_brain_fwe.png',dpi=180); display.close()
    # Figure 2: ROI distribution by participant, with mean and t interval.
    fig,ax=plt.subplots(figsize=(7.2,4.4))
    ax.scatter(np.arange(1,n+1),roi_mean,s=23,color='#35618f',alpha=.8)
    ax.axhline(0,color='black',lw=1)
    ax.axhline(roi_avg,color='#bc4b36',lw=2,label='Group mean')
    ax.fill_between([1,n],[ci[0],ci[0]],[ci[1],ci[1]],color='#bc4b36',alpha=.15,label='95% t interval')
    ax.set(xlabel='Participant (sorted by ID)',ylabel='Mean gain contrast estimate in vmPFC envelope',
           title='Participant-level ROI summaries (descriptive)')
    ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/'vmPFC_participant_estimates.png',dpi=180); plt.close(fig)
    # Coverage check visualization.
    coverage=np.sum(np.isfinite(stack)&(stack!=0),axis=0)
    fig,ax=plt.subplots(figsize=(6.5,4.2)); ax.hist(coverage.ravel(),bins=np.arange(-.5,55.5,1),color='#477a70')
    ax.set(xlabel='Number of participant maps with finite nonzero estimate',ylabel='Voxel count',
           title='Spatial support and zero padding')
    fig.tight_layout(); fig.savefig(FIG/'coverage_qc.png',dpi=180); plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
