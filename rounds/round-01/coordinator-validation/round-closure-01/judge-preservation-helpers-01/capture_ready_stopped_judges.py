"""One bounded pass over control receipts; preserve only finalized judge sessions.
No polling loop, active output access, judge launch, replay, or scientific grading.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda d:hashlib.sha256(d).hexdigest()
plan=json.loads((BASE/'dataset/rounds/round-01/plan.json').read_bytes())
assignments=sorted(plan['assigned_judgments'],key=lambda a:a['dispatch_order'])
assert len(assignments)==32
results=[]
def invoke(script,identifier,retention,stem):
    stdout=retention/(stem+'.stdout.log');stderr=retention/(stem+'.stderr.log');receipt=retention/(stem+'.execution.json')
    assert not stdout.exists() and not stderr.exists() and not receipt.exists(),stem
    start=datetime.now(timezone.utc).isoformat()
    process=subprocess.run([sys.executable,'-B',str(script),identifier],capture_output=True)
    stdout.write_bytes(process.stdout);stderr.write_bytes(process.stderr)
    receipt.write_text(json.dumps({'argv':[sys.executable,'-B',str(script),identifier],'script_sha256':sha(script.read_bytes()),'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'returncode':process.returncode},indent=2)+'\n')
    return process.returncode
for assignment in assignments:
    directory=BASE/'runs'/assignment['run']/'judgments'/assignment['judgment'];dispatch_path=directory/'dispatch.json'
    if not dispatch_path.exists():continue
    control=json.loads(dispatch_path.read_bytes())
    if control.get('status')!='launcher-finished':continue
    retention=directory/'retention';retention.mkdir(exist_ok=True)
    if (retention/'late-capture-01').exists() or (retention/'late-capture-01.execution.json').exists():continue
    identifier=assignment['judgment']
    code=invoke(HERE/'preserve_stopped_judge_v2.py',identifier,retention,'late-capture-01')
    audit_code=None
    if code==0:audit_code=invoke(HERE/'audit_stopped_judge_capture.py',identifier,retention,'late-capture-01.audit')
    result={'judgment':identifier,'dispatch_order':assignment['dispatch_order'],'preservation_returncode':code,'audit_returncode':audit_code,'retention':str(retention)}
    native_path=directory/'attempt-01/native/result.json'
    if native_path.exists():
        native=json.loads(native_path.read_bytes())
        result.update(launcher_returncode=control.get('returncode'),native_returncode=native.get('returncode'),launcher_target_unchanged=native.get('target_unchanged'))
        if native.get('target_unchanged') is False and not (retention/'target-as-found-01').exists():
            target_code=invoke(HERE/'preserve_changed_judge_target.py',identifier,retention,'target-as-found-01');result['target_preservation_returncode']=target_code
            if target_code==0:result['target_audit_returncode']=invoke(HERE/'audit_as_found_target.py',identifier,retention,'target-as-found-01.audit')
    results.append(result)
print(json.dumps({'stopped_judgments_processed':results,'scope':'Only finalized dispatches were allowed to expose native result or output contents. Earlier failures and all existing captures are left untouched.'},indent=2))
