from pathlib import Path
import datetime,hashlib,json,subprocess,sys
G=Path(__file__).resolve().parent
B=G.parent
W=Path('/Users/johnlee/.local/share/wt-utils/worktrees/73e0/stamped-in-practice')
expected_record='f7ba4d297ffdf472c5d696352dbe0773e8e7c9ebb99e9719d8fee444c0eca6ae'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(G/'series.json')==expected_record
series=json.loads((G/'series.json').read_bytes());assert len(series['judgment_dispatch_order'])==32
O=B/'assessment-series'/series['series_id']/'queue-01';O.mkdir(parents=True,exist_ok=False)
records=[]
for batch in range(1,12):
    assert sha(G/'series.json')==expected_record
    assert sha(G/'dispatch_series.py')=='7361029f47b552c7275b6e1c3eae40032a08c3a74dc42cea8a86a768d3c82198'
    argv=[sys.executable,str(G/'dispatch_series.py'),'--record',str(G/'series.json'),'--batch',str(batch),'--checkout',str(W),'--state',str(B)]
    record={'batch':batch,'argv':argv,'dispatcher_sha256':sha(G/'dispatch_series.py'),'series_record_sha256':expected_record,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (O/f'batch-{batch:02d}-command.json').write_text(json.dumps(record,indent=2)+'\n')
    with (O/f'batch-{batch:02d}.stdout').open('xb') as out,(O/f'batch-{batch:02d}.stderr').open('xb') as err:
        result=subprocess.run(argv,cwd=W,stdout=out,stderr=err)
    record.update(returncode=result.returncode,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());records.append(record)
    (O/'completed-batches.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record),flush=True)
    if result.returncode:raise SystemExit('Dispatcher error; inspect retained failure before continuing allocated queue.')
(O/'result.json').write_text(json.dumps({'status':'all32-assigned-launchers-finished','batches':records},indent=2)+'\n')
