"""Write the final index, audit it, and bind exact execution receipts for handoff.
Requires all 11 stopped-batch retention closures; does not open source outputs.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):
 b=p.read_bytes();return {'path':str(p),'size':len(b),'sha256':sha(b)}
assert all((BASE/f'round-01-judge-batch-{n:02d}/retention-closed.json').exists() for n in range(1,12))
receipts=[]
for script,stem in [('summarize_closed_judge_retention_v3.py','judge-retention-final-01.index'),('audit_final_judge_coverage.py','judge-retention-final-01.audit')]:
 p=HERE/script;argv=[sys.executable,'-B',str(p)];start=datetime.now(timezone.utc).isoformat();r=subprocess.run(argv,capture_output=True)
 for suffix,data in [('stdout.log',r.stdout),('stderr.log',r.stderr)]:
  out=BASE/(stem+'.'+suffix)
  with out.open('xb') as stream:stream.write(data)
  receipts.append(ref(out))
 out=BASE/(stem+'.execution.json')
 with out.open('x') as stream:stream.write(json.dumps({'argv':argv,'script':ref(p),'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'returncode':r.returncode},indent=2)+'\n')
 receipts.append(ref(out));print(r.stdout.decode(),flush=True)
 if r.returncode:print(json.dumps({'attention':'Final metadata aggregation/audit failed; receipts retained','stem':stem,'returncode':r.returncode}),flush=True);sys.exit(r.returncode)
summary=BASE/'judge-retention-final-01/summary.json';audit=BASE/'judge-retention-final-01.audit.json'
handoff={'schema':'stopped-judge-retention-final-handoff-v1','created_at':datetime.now(timezone.utc).isoformat(),'summary':ref(summary),'manifest':ref(BASE/'judge-retention-final-01/manifest.json'),'supporting_files':ref(BASE/'judge-retention-final-01/supporting-files.json'),'coverage_audit':ref(audit),'execution_receipts':receipts,'finishing_script':ref(Path(__file__)),'research_child_coverage':{'summary':ref(BASE/'research-child-coverage-01/summary.json'),'manifest':ref(BASE/'research-child-coverage-01/manifest.json')},'scope':'Local preservation evidence handoff only; publication and scientific validity are owned separately. Original raw, processed shadow, failed screening receipt and any additive resolutions remain distinct.'}
out=BASE/'judge-retention-final-01.handoff.json'
with out.open('x') as stream:stream.write(json.dumps(handoff,indent=2)+'\n')
print(json.dumps({'handoff':ref(out)},indent=2))
