from pathlib import Path
import collections,datetime,hashlib,json,shutil,statistics,subprocess
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset';M=Path('/Users/johnlee/code/CON/stamped-in-practice');O=D/'rounds/round-01/synthesis'
O.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def copy(src,dst):
 if src.is_dir():shutil.copytree(src,dst)
 else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
copy(B/'round-01-extraction-final-01',O/'extraction')
copy(B/'round-01-figures-final-01',O/'figures')
copy(B/'round-01-attrition-final-01',O/'attrition')
(O/'figures/.gitattributes').write_text('*.png annex.largefiles=nothing\n')
(O/'attrition/.gitattributes').write_text('*.png annex.largefiles=nothing\n*.pdf annex.largefiles=nothing\n')
code=O/'code';code.mkdir()
for name in ['aggregate_comparison.py','comparison_figures.py','render_round_summary.py','render_assessment_attrition.py']:copy(M/'scripts'/name,code/name)
for name in ['assessment-version.json','pixi.toml']:copy(M/name,code/name)
copy(Path(__file__),code/'prepare-synthesis.py')
A=O/'extraction/analysis'
def rows(n):return [json.loads(s) for s in (A/(n+'.jsonl')).read_text().splitlines()]
judgments=[r for r in rows('judgments') if r['round']==1];runs=[r for r in rows('runs') if r['round']==1];byrun={r['run_id']:r for r in runs};primary={r['run_id']:r for r in judgments if r['role']=='primary'}
assert len(judgments)==32 and len(runs)==24 and sum(r['response_status']=='valid' for r in judgments)==21
issues=rows('issues');assert len(issues)==11 and all(r['message']=='Malformed provenance: target_unchanged: True was expected' for r in issues)
conditions=[]
for c in ['baseline','discover-general','discover-science','stamped-explicit']:
 js=[r for r in judgments if r['condition']==c];ps=[r for r in js if r['role']=='primary'];valid=[r for r in ps if r['response_status']=='valid'];ds=[r for r in js if r['role']=='duplicate'];ops=[r for r in rows('operations') if r['stage']=='worker' and r['condition']==c and r['round']==1];sc=collections.Counter(r['adequacy'] for r in valid)
 conditions.append({'condition':c,'workers':len(ps),'primary_valid':len(valid),'duplicate_assigned':len(ds),'duplicate_valid':sum(r['response_status']=='valid' for r in ds),'primary_adequacy':dict(sc),'worker_duration_s':{'median':statistics.median(r['duration_s'] for r in ops),'min':min(r['duration_s'] for r in ops),'max':max(r['duration_s'] for r in ops)},'input_tokens_median':statistics.median(next(m['value'] for m in r['metrics'] if m['name']=='input_tokens') for r in ops),'output_tokens_median':statistics.median(next(m['value'] for m in r['metrics'] if m['name']=='output_tokens') for r in ops)})
pairs=[]
for r in judgments:
 p=primary[r['run_id']]
 if r['role']=='duplicate' and r['response_status']=='valid' and p['response_status']=='valid':
  dr=[x for x in rows('disagreement') if x['run_id']==r['run_id']];pairs.append({'run_id':r['run_id'],'primary_adequacy':p['adequacy'],'duplicate_adequacy':r['adequacy'],'item_comparisons':len(dr),'item_disagreements':sum(x['exact_disagreement'] for x in dr)})
summary={'scope':'Original frozen round-one series; admitted primary outcomes only, unavailable measurements retained. No regrading or overall score.','assigned_workers':24,'assigned_judgments':32,'valid_judgments':21,'invalid_judgments':11,'conditions':conditions,'duplicate_pairs':pairs,'checklist_status_counts':{k:dict(collections.Counter(r['status'] for r in rows('items') if r['role']=='primary' and r['item_id']==k)) for k in sorted({r['item_id'] for r in rows('items')})},'source_index_sha256':sha(O/'extraction/index.json'),'source_judgments_sha256':sha(A/'judgments.jsonl')}
write(O/'summary.json',summary)
T=O/'tables';T.mkdir()
for n in ['runs','judgments','items','counts','disagreement','operations','effort']:
 selected=[r for r in rows(n) if r.get('run_id') in byrun]
 (T/(n+'.jsonl')).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in selected))
(O/'condition-summary.tsv').write_text('condition\tworkers\tusable_primary\tusable_duplicate\tsupported_primary\tqualified_primary\tmedian_worker_seconds\tmedian_input_tokens\tmedian_output_tokens\n'+''.join(f"{r['condition']}\t6\t{r['primary_valid']}\t{r['duplicate_valid']}\t{r['primary_adequacy'].get('supported',0)}\t{r['primary_adequacy'].get('qualified',0)}\t{r['worker_duration_s']['median']:.6f}\t{r['input_tokens_median']}\t{r['output_tokens_median']}\n" for r in conditions))
# Preserve completed control evidence without recopying experiment payload caches.
C=D/'rounds/round-01/coordinator-validation/round-closure-01';C.mkdir()
for p in B.glob('judge-retention-final-01*'):copy(p,C/p.name)
for name in ['judge-preservation-helpers-01','judge-retention-passes-01','round-01-judge-queue-01','judge-native-publication-index-03','round-01-synthesis-root-review-01','attrition-figure-review-01']:copy(B/name,C/name)
for name in ['round-01-judge-queue-01.stdout','round-01-judge-queue-01.stderr','run-judge-queue.py']:
 if (B/name).exists():copy(B/name,C/name)
for p in sorted(B.glob('round-01-judge-batch-*/retention-closed.json')):copy(p,C/'batch-closures'/p.parent.name/p.name)
for i in [3,4,5]:
 src=B/f'register-support-{i:02d}';dest=D/f'rounds/round-01/support-publication/closed-{i:02d}/registration';dest.mkdir()
 for p in src.iterdir():
  if p.is_file():copy(p,dest/p.name)
# Complete latest exact-label supplements remain outside original responses.
for run in ['narps-neutral-r1-07-j02','narps-neutral-r1-21-j01']:
 p=B/'judgment-extractions'/run/'manual-extraction-supplement.json';copy(p,C/'manual-extraction'/run/p.name)
write(O/'validation.json',{'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=M,text=True).strip(),'expected_aggregation_exit':2,'actual_aggregation_exit':json.loads((O/'extraction/command.json').read_text())['returncode'],'only_expected_target_integrity_issues':True,'assigned32':True,'retention_commit_scope':'Snapshot of coordinator registry at extraction; later support descendants do not alter original capture or response identities.','figures_visual_review':'All actual-data PNGs inspected: labels/legends legible, fixed denominators and missingness visible, no clipping. Synthetic attrition preview kept only in review evidence.','sources':[{'path':str(p.relative_to(O)),'sha256':sha(p)} for p in sorted(O.rglob('*')) if p.is_file()]})
print(json.dumps({'summary':summary,'output':str(O)}))
