"""Bounded, low-frequency stopped-control monitoring; no active output access.
Runs preservation only after the driver's finalized-dispatch gate and stops for
attention on any preservation/audit failure. It never launches a judge.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda d:hashlib.sha256(d).hexdigest()
plan=json.loads((BASE/'dataset/rounds/round-01/plan.json').read_bytes());assignments=sorted(plan['assigned_judgments'],key=lambda a:a['dispatch_order']);assert len(assignments)==32
root=BASE/'judge-retention-passes-01';root.mkdir(exist_ok=True)
def invoke(script,args,d,stem):
    argv=[sys.executable,'-B',str(script),*args];start=datetime.now(timezone.utc).isoformat();p=subprocess.run(argv,capture_output=True)
    (d/(stem+'.stdout.log')).write_bytes(p.stdout);(d/(stem+'.stderr.log')).write_bytes(p.stderr)
    (d/(stem+'.execution.json')).write_text(json.dumps({'argv':argv,'script_sha256':sha(script.read_bytes()),'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'returncode':p.returncode},indent=2)+'\n')
    return p
for pass_number in range(180):
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');d=root/stamp;d.mkdir()
    p=invoke(HERE/'capture_ready_stopped_judges.py',[],d,'preservation-pass')
    if p.returncode:
        print(json.dumps({'attention':'driver failure','pass':str(d),'returncode':p.returncode}),flush=True);sys.exit(1)
    response=json.loads(p.stdout);processed=response['stopped_judgments_processed']
    failures=[r for r in processed if r.get('preservation_returncode')!=0 or r.get('audit_returncode')!=0 or r.get('target_preservation_returncode',0)!=0 or r.get('target_audit_returncode',0)!=0]
    if processed:print(json.dumps({'processed':processed,'pass':str(d)}),flush=True)
    if failures:print(json.dumps({'attention':'preservation or audit failure retained','failures':failures}),flush=True);sys.exit(2)
    controls=[]
    for a in assignments:
        path=BASE/'runs'/a['run']/'judgments'/a['judgment']/'dispatch.json'
        if path.exists():
            raw=path.read_bytes();c=json.loads(raw);controls.append({'judgment':a['judgment'],'status':c.get('status'),'returncode':c.get('returncode'),'finished_utc':c.get('finished_utc'),'dispatch_path':str(path),'dispatch_sha256':sha(raw)})
    (d/'control-receipts.json').write_text(json.dumps(controls,indent=2)+'\n')
    closed=[]
    for batch in range(1,12):
        bd=BASE/f'round-01-judge-batch-{batch:02d}'
        if (bd/'retention-closed.json').exists():continue
        group=assignments[(batch-1)*3:batch*3]
        paths=[BASE/'runs'/a['run']/'judgments'/a['judgment']/'retention/late-capture-01.integrity-audit.json' for a in group]
        if not all(p.exists() for p in paths):continue
        p=invoke(HERE/'close_judge_batch_retention_v2.py',[str(batch)],d,f'close-batch-{batch:02d}')
        if p.returncode:print(json.dumps({'attention':'closure failure','batch':batch,'pass':str(d)}),flush=True);sys.exit(3)
        closed.append(json.loads(p.stdout))
    if closed:print(json.dumps({'closed_batches':closed}),flush=True)
    if all((BASE/f'round-01-judge-batch-{n:02d}'/'retention-closed.json').exists() for n in range(1,12)):
        print(json.dumps({'complete':True,'closed_batches':11,'fixed_slots':32}),flush=True);sys.exit(0)
    time.sleep(60)
print(json.dumps({'attention':'bounded three-hour window exhausted','complete':False}),flush=True)
sys.exit(4)
