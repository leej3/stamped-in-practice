from pathlib import Path
import json,hashlib,datetime
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1'); G=B/'round-03-assessment-registration-01'; S=B/'assessment-series/narps-neutral-r3-operational-v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
series=json.loads((G/'series.json').read_text()); queue=S/'queue-01/result.json'; assert queue.is_file()
rows=[]
for slot in series['judgment_dispatch_order']:
 p=S/'judgments'/slot['judgment']; c=p/'completion.json'; n=p/'attempt-01/native/result.json'; cc=json.loads(c.read_text()); nn=json.loads(n.read_text())
 rows.append({'slot':slot['judgment'],'run':slot['run'],'role':slot['role'],'completion':str(c),'completion_sha256':sha(c),'native_result':str(n),'native_result_sha256':sha(n),'native_returncode':nn['returncode'],'launcher_returncode':cc['returncode'],'started_at':nn['started_at'],'finished_at':nn['finished_at'],'elapsed_seconds':nn['elapsed_seconds']})
assert len(rows)==32 and len({r['slot'] for r in rows})==32
out={'series_id':series['series_id'],'round':3,'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assigned':32,'native_completed':32,'unstarted':0,'active':0,'series_sha256':sha(G/'series.json'),'assessment_procedure_sha256':sha(G/'assessment-procedure.json'),'queue_result':str(queue),'queue_result_sha256':sha(queue),'rows':rows,'scope':'Completion/control identities only; all fixed assigned attempts retained without retry, repair, replacement or grade interpretation.'}
p=S/'all-completed-01.json'
with p.open('x') as f: json.dump(out,f,indent=2); f.write('\n')
print(json.dumps({'path':str(p),'sha256':sha(p),'completed':len(rows)}))
