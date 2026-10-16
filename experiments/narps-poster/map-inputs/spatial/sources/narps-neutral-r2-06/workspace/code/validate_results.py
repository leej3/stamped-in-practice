#!/usr/bin/env python3
"""Independent numerical cross-check of saved group summaries."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
import nibabel as nib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
x=pd.read_csv(OUT/'participant_roi_means.csv').roi_mean_effect.to_numpy(dtype=float)
saved=pd.read_csv(OUT/'vmPFC_roi_summary.csv').iloc[0]
n=len(x); mean=float(np.mean(x)); sd=float(np.std(x,ddof=1)); se=sd/np.sqrt(n)
t=mean/se; p=float(stats.t.sf(t,n-1)); ci=stats.t.interval(.95,n-1,loc=mean,scale=se)
recalc={'n':n,'mean':mean,'sd':sd,'se':float(se),'t':float(t),'df':n-1,'p_one_sided':p,'ci95_low':float(ci[0]),'ci95_high':float(ci[1]),
        'max_abs_difference_from_saved':float(max(abs(mean-saved.mean_effect),abs(t-saved.t),abs(p-saved.one_sided_p_descriptive),abs(ci[0]-saved.ci95_low),abs(ci[1]-saved.ci95_high)))}
assert recalc['max_abs_difference_from_saved']<1e-6
pmap=nib.load(OUT/'wholebrain_bonferroni_p.nii.gz').get_fdata()
summary=pd.read_csv(OUT/'wholebrain_summary.csv').iloc[0]
nonzero=pmap[pmap>0]
assert int(np.sum(nonzero<=.05))==int(summary.significant_voxels_fwe_0_05)
assert int(np.sum(nonzero>0))==int(summary.n_voxels)
recalc['wholebrain_voxels']=int(len(nonzero)); recalc['wholebrain_fwe_significant_voxels']=int(np.sum(nonzero<=.05))
(OUT/'validation_roi_recalculation.json').write_text(json.dumps(recalc,indent=2)+'\n')
print(json.dumps(recalc,indent=2))
