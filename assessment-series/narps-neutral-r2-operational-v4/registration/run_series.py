"""Run fixed assigned batches in order with authorized max10 overlap."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys, time
G = Path(__file__).resolve().parent
B = G.parent
W = Path('/Users/johnlee/.local/share/wt-utils/worktrees/73e0/stamped-in-practice')
EXPECTED_RECORD = 'b440c946d35f299a2d64ccf1f8a0fc54587e6fa11aae079db975cbb014c0b848'
EXPECTED_DISPATCHER = '14b05a1975c017485bacf6c9d0aeb4ab33f72faee184ec8aa976cc93bd9b6d65'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(G/'series.json') == EXPECTED_RECORD
assert sha(G/'dispatch_series.py') == EXPECTED_DISPATCHER
series=json.loads((G/'series.json').read_bytes())
assert len(series['judgment_dispatch_order']) == 32
assert series['maximum_simultaneous_native_sessions'] == 10
S = B/'assessment-series'/series['series_id']
O = S/'queue-01'; O.mkdir(parents=True,exist_ok=False)
def active():
    return [p.parent.name for p in sorted((S/'judgments').glob('*/dispatch.json'))
            if not p.with_name('completion.json').exists()]
processes, records, next_batch = [], [], 1
with (O/'concurrency-events.jsonl').open('x') as events:
    last = None
    while next_batch <= 11 or processes or active():
        for process,out,err,row in list(processes):
            code = process.poll()
            if code is not None:
                out.close();err.close()
                row.update(returncode=code,finished_at=now());records.append(row)
                (O/'completed-batches.json').write_text(json.dumps(records,indent=2)+'\n')
                processes.remove((process,out,err,row))
                if code: raise SystemExit('Dispatcher error; retain and report without retry.')
        current = active()
        state = tuple(current)
        if state != last:
            events.write(json.dumps({'at':now(),'active_launcher_count':len(current),'slots':current})+'\n')
            events.flush();last=state
        selected=series['judgment_dispatch_order'][3*(next_batch-1):3*next_batch]
        if next_batch <= 11 and len(current)+len(selected) <= 10:
            assert sha(G/'series.json') == EXPECTED_RECORD
            assert sha(G/'dispatch_series.py') == EXPECTED_DISPATCHER
            argv=[sys.executable,str(G/'dispatch_series.py'),'--record',str(G/'series.json'),
                  '--batch',str(next_batch),'--checkout',str(W),'--state',str(B)]
            row={'batch':next_batch,'argv':argv,'dispatcher_sha256':EXPECTED_DISPATCHER,
                 'series_record_sha256':EXPECTED_RECORD,'started_at':now(),
                 'active_before_dispatch':current,'authorized_maximum':10}
            (O/f'batch-{next_batch:02d}-command.json').write_text(json.dumps(row,indent=2)+'\n')
            out=(O/f'batch-{next_batch:02d}.stdout').open('xb')
            err=(O/f'batch-{next_batch:02d}.stderr').open('xb')
            process=subprocess.Popen(argv,cwd=W,stdout=out,stderr=err)
            processes.append((process,out,err,row))
            print(json.dumps({'batch':next_batch,'pid':process.pid,'at':row['started_at']}),flush=True)
            # Reserve the selected slots until every dispatch receipt exists.
            while not all((S/'judgments'/s['judgment']/'dispatch.json').exists() for s in selected) and process.poll() is None:
                time.sleep(1)
            next_batch += 1
        else:
            time.sleep(2)
assert all((S/f'batch-{i:02d}/result.json').exists() for i in range(1,12))
(O/'result.json').write_text(json.dumps({'status':'all32-assigned-launchers-finished',
    'maximum_simultaneous_native_sessions':10,'batches':records},indent=2)+'\n')
