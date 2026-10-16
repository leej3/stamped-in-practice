#!/usr/bin/env python3
"""Render round-one development evidence from validated, unaltered extraction tables."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle
import numpy as np

CONDITIONS = ['baseline', 'discover-general', 'discover-science', 'stamped-explicit']
LABELS = ['Baseline', 'General discovery', 'Science discovery', 'Explicit STAMPED']
COLORS = ['#4c6177', '#268785', '#be8440', '#87629c']
STATES = ['met', 'partial', 'unmet', 'not-checked', 'not-applicable', 'unavailable']
STATE_COLORS = ['#4f9a86', '#e5bb6d', '#c67a73', '#c6cbd1', '#f2f1ed', '#ffffff']


def load(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def save(fig, output, name):
    for extension in ['png', 'svg', 'pdf']:
        fig.savefig(output / f'{name}.{extension}', dpi=180, facecolor='white')
    plt.close(fig)


def clean(ax):
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', type=Path, required=True)
    parser.add_argument('--estimates', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.hashsalt': 'narps-round-one-development'})
    runs = sorted((r for r in load(args.tables / 'runs.jsonl') if r['round'] == 1),
                  key=lambda r: r['run_id'])
    assert len(runs) == 12 and all(r['worker_completion'] == 'completed' for r in runs)
    assert [r['condition'] for r in runs] == sum(([c] * 3 for c in CONDITIONS), [])
    ids = [r['run_id'] for r in runs]
    judgments = {j['run_id']: j for j in load(args.tables / 'judgments.jsonl')
                 if j['round'] == 1 and j['role'] == 'primary'}
    assert len(judgments) == 12 and all(j['response_status'] == 'valid' for j in judgments.values())
    assert all(j['extraction_status'] == 'explicit' for j in judgments.values())
    items = [i for i in load(args.tables / 'comparable_items.jsonl')
             if i['run_id'] in ids and i['role'] == 'primary']
    raw_items = [i for i in load(args.tables / 'items.jsonl')
                 if i['run_id'] in ids and i['role'] == 'primary']
    keys = sorted({i['item_id'] for i in raw_items},
                  key=lambda k: (['must', 'should', 'may'].index(k.split(':')[1].split('/')[0]), k))
    assert len(keys) == 31 and len(raw_items) == 12 * 31
    available = {(i['run_id'], i['item_id']): i['status'] for i in items}
    matrix = np.array([[STATES.index(available.get((run, key), 'unavailable')) for key in keys] for run in ids])
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.subplots_adjust(left=.19, right=.98, top=.82, bottom=.22)
    ax.imshow(matrix, cmap=ListedColormap(STATE_COLORS), vmin=-.5, vmax=5.5, aspect='auto')
    for y, x in np.argwhere(matrix == 5):
        ax.add_patch(Rectangle((x-.5, y-.5), 1, 1, fill=False, hatch='////', edgecolor='#65717c', lw=0))
    ax.set_xticks(range(31), [k.split(':')[1].replace('must/', 'M').replace('should/', 'S').replace('may/', 'm') for k in keys], rotation=90)
    labels = []
    for r in runs:
        j = judgments[r['run_id']]
        version = 'original' if j['procedure_sha256'].startswith('c6f01') else 'amended'
        labels.append(f"{r['run_id'][-2:]}   {LABELS[CONDITIONS.index(r['condition'])]}  [{version}]")
    ax.set_yticks(range(12), labels, fontsize=9)
    for cut in [2.5, 5.5, 8.5]: ax.axhline(cut, color='white', lw=3)
    for cut in [16.5, 25.5]: ax.axvline(cut, color='white', lw=3)
    ax.set_title('Checklist evidence by worker and item', loc='left', fontsize=17, pad=35)
    ax.text(0, 1.025, 'First-assigned primary ratings; no overall score. Original and amended assessor versions remain distinct.', transform=ax.transAxes, fontsize=10)
    handles = [Patch(facecolor=color, label=state, edgecolor='#65717c' if state == 'unavailable' else 'none', hatch='////' if state == 'unavailable' else '') for state, color in zip(STATES, STATE_COLORS)]
    fig.legend(handles=handles, loc='lower center', ncol=6, frameon=False, bbox_to_anchor=(.58,.075), fontsize=10)
    fig.text(.19,.025,'M = MUST (17); S = SHOULD (9); m = MAY (5). Hatching marks unavailable measurement evidence, not a worker failure.\nRound 1 is development evidence; common workflow mandates and assessor changes limit assistance comparisons.', fontsize=9)
    save(fig,args.output,'checklist-evidence')

    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    fig.subplots_adjust(left=.25,right=.97,top=.86,bottom=.17)
    adequacy_colors = {'supported':'#4f9a86','qualified':'#e5bb6d','not supported':'#c67a73','unable to assess':'#c6cbd1'}
    for y,r in enumerate(runs):
        j=judgments[r['run_id']];cat=j['adequacy'];assert cat in adequacy_colors
        ax.barh(y,1,color=adequacy_colors[cat],height=.7)
        suffix='  *' if j.get('scientific_dependency',{}).get('status')=='uncertain' else ''
        ax.text(.03,y,cat+suffix,va='center',fontsize=11)
        ax.text(1.03,y,'No corrected positive vmPFC finding',va='center',fontsize=9)
    ax.set_yticks(range(12),labels,fontsize=9);ax.invert_yaxis();ax.set_xlim(0,2.1);ax.set_xticks([])
    for spine in ax.spines.values():spine.set_visible(False)
    ax.set_title('Scientific adequacy and reported hypothesis outcome',loc='left',fontsize=16,pad=22)
    ax.text(.03,1.025,'Independent primary judgment',transform=ax.transAxes,fontsize=10)
    ax.text(.51,1.025,'Worker-reported conclusion',transform=ax.transAxes,fontsize=10)
    fig.text(.25,.055,'* Independent replay evidence was unavailable; its contribution to confidence is uncertain. Raw judgments are unchanged.\n“Supported” rates the adequacy of the analysis and bounded conclusion; it does not mean the positive hypothesis was supported.\nThree workers per condition; exploratory development evidence with version and workflow limitations.',fontsize=8.8)
    save(fig,args.output,'scientific-outcomes')

    operations=load(args.tables/'operations.jsonl')
    duration={o['run_id']:o['duration_s']/60 for o in operations if o['run_id'] in ids and o['actor']=='worker' and o['stage']=='worker'}
    assert set(duration)==set(ids)
    fig,ax=plt.subplots(figsize=(9.5,6))
    fig.subplots_adjust(left=.1,right=.97,top=.86,bottom=.23)
    summaries=[]
    for x,c in enumerate(CONDITIONS):
        selected=[r for r in runs if r['condition']==c];values=[duration[r['run_id']] for r in selected]
        for dx,r,v in zip([-.16,0,.16],selected,values):
            ax.scatter(x+dx,v,s=75,color=COLORS[x],zorder=3)
            ax.annotate(r['run_id'][-2:],(x+dx,v),xytext=(5,5),textcoords='offset points',fontsize=9)
        median=float(np.median(values));ax.hlines(median,x-.27,x+.27,color=COLORS[x],lw=2.5)
        summaries.append({'condition':c,'n':3,'median_worker_minutes':median,'min_worker_minutes':min(values),'max_worker_minutes':max(values)})
    ax.set_xticks(range(4),LABELS);ax.set_ylabel('Native worker session elapsed minutes');ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.2);clean(ax)
    ax.set_title('Worker effort varied substantially within assistance conditions',loc='left',fontsize=15,pad=20)
    fig.text(.1,.07,'Each dot is one completed worker; short lines show medians (n = 3 per condition).\nWall time includes model waiting and any nested reviews; child time is not added again.\nThis excludes judge/coordinator work and does not estimate provider compute, billing or causal skill effects.',fontsize=10)
    save(fig,args.output,'worker-effort')
    (args.output/'worker-effort-summary.json').write_text(json.dumps(summaries,indent=2)+'\n')

    estimates=json.loads(args.estimates.read_text())['rows'];assert [e['run_id'] for e in estimates]==ids
    fig,ax=plt.subplots(figsize=(12,7))
    fig.subplots_adjust(left=.33,right=.97,top=.86,bottom=.2)
    for y,e in enumerate(estimates):
        mean=e['reported_roi_mean'];lo=e['reported_ci95_lower'];hi=e['reported_ci95_upper'];assert lo<=mean<=hi
        color=COLORS[CONDITIONS.index(e['condition'])]
        ax.errorbar(mean,y,xerr=[[mean-lo],[hi-mean]],fmt='o',color=color,capsize=4,ms=6,lw=1.6)
    ax.axvline(0,color='#606972',lw=1,ls='--');ax.set_yticks(range(12),[e['run_id'][-2:]+'  '+e['roi_label'] for e in estimates],fontsize=9);ax.invert_yaxis();ax.grid(axis='x',alpha=.17);clean(ax)
    ax.set_xlabel('Reported participant-average regional gain coefficient (upstream model units)')
    ax.set_title('Reported regional estimates differ across analysis choices',loc='left',fontsize=14,pad=20)
    fig.text(.33,.075,'Worker-reported means and 95% intervals from the same 54 maps; anatomical regions differ.\nThese descriptive intervals are not the whole-brain-corrected hypothesis tests or assistance-effect intervals.\nNo pooled estimate: the rows are alternative analyses of shared data, not independent study replications.',fontsize=9.5)
    fig.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(COLORS,LABELS)], loc='upper center',ncol=4,frameon=False,bbox_to_anchor=(.6,.98),fontsize=9)
    save(fig,args.output,'reported-regional-estimates')
    sources=[args.tables/n for n in ['runs.jsonl','judgments.jsonl','items.jsonl','comparable_items.jsonl','operations.jsonl']]+[args.estimates,Path(__file__)]
    (args.output/'figure-provenance.json').write_text(json.dumps({'scope':'Round-one development evidence; no regrading or outcome selection.','sources':[{'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]},indent=2)+'\n')


if __name__=='__main__':main()
