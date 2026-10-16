from pathlib import Path
import hashlib, importlib.util, json, sys
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
P=B/'repaired-series-registration-01';OUT=Path(__file__).resolve().parent
SOURCE=Path('/Users/johnlee/.local/share/wt-utils/worktrees/73e0/stamped-in-practice/scripts')
sys.path.insert(0,str(SOURCE));import assessment_procedure as procedure
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
seal=read(P/'assessment-procedure.json');rows=seal['assessment_amendment']['retained_objects'];sources={r['run']:r for r in read(P/'original-object-sources.json')};results=[]
def check(label,row,run=None,stop=None,capture=None,seed=None,head='original',expected=True):
    src=sources[row['run']]
    stop=Path(stop or src['worker_stop']['path']);capture=capture or row['delivery_capture_sha256']
    error=None
    try: procedure.check_retained_target(seal, {'run':run or row['run']},seed or row['seed_commit'],row['result_commit'] if head=='original' else head,stop,capture)
    except SystemExit as e:error=str(e)
    actual=error is None
    results.append({'case':label,'original_run':row['run'],'selected_run':run or row['run'],'expected_accepted':expected,'accepted':actual,'error':error})
    assert actual==expected,results[-1]
for row in rows:
    src=sources[row['run']]
    assert sha(src['worker_stop']['path'])==row['worker_end_state_sha256']
    assert sha(src['delivery_capture']['path'])==row['delivery_capture_sha256']
    check('exact-original',row)
    check('unlisted-run',row,run='unlisted-neutral-run',expected=False)
    check('wrong-seed',row,seed='0'*40,expected=False)
    check('wrong-head',row,head='0'*40,expected=False)
    check('null-head',row,head=None,expected=row['result_commit'] is None)
    for other in rows:
        if row['run']==other['run']:continue
        osrc=sources[other['run']]
        assert row['worker_end_state_sha256']!=other['worker_end_state_sha256']
        assert row['delivery_capture_sha256']!=other['delivery_capture_sha256']
        check('swapped-stop:'+other['run'],row,stop=osrc['worker_stop']['path'],expected=False)
        check('swapped-capture:'+other['run'],row,capture=other['delivery_capture_sha256'],expected=False)
        check('cross-run-label:'+other['run'],row,run=other['run'],expected=False)
T=B/'assessment-operational-live-trial-02';T1=B/'assessment-operational-live-trial-01'
tseal=read(T/'assessment-procedure-v4.json');trow=tseal['assessment_amendment']['retained_objects'][0];tseed=read(T1/'research-launch-01/input-boundary.json');tstop=T1/'research-launch-01/native/worker-end-state.json'
procedure.check_retained_target(tseal,tseed,trow['seed_commit'],trow['result_commit'],tstop,trow['delivery_capture_sha256'])
record={'verified':True,'scope':'Admission-only read-only calls against exact original registered identities. No native launch, science or object mutation. All original failed-preparation seals remain unchanged; this validates the new separately recorded seal.','source':str(SOURCE/'assessment_procedure.py'),'source_sha256':sha(SOURCE/'assessment_procedure.py'),'tested_seal_sha256':sha(P/'assessment-procedure.json'),'original_object_count':len(rows),'case_count':len(results),'positive_cases':sum(r['accepted'] for r in results),'negative_cases':sum(not r['accepted'] for r in results),'T2_bridge':{'guard_accepts_exact_closed_trial_identity':True,'native_runtime_source_unchanged_claim':False,'scope':'Only the changed admission function was evaluated with exact T2 identities; no native replay repeated.','seal_sha256':sha(T/'assessment-procedure-v4.json'),'verification_sha256':sha(T/'verification.json')},'results':results}
(OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='results'},indent=2))
