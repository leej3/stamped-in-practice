"""Overlap existing assigned wave dispatches under authorized max10 scheduling."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys, time
B = Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
Q = Path(__file__).resolve().parent
W = Path('/Users/johnlee/.local/share/wt-utils/worktrees/9d12/stamped-in-practice')
D = B / 'round-03-dispatch-preparation-01/launch-wave.py'
EXPECTED = '0600049c9d24764fe7deb7a94d6bc2875449531100d1f504cbc6375d94a874e7'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def active():
    return [p.parent.name for p in sorted((B/'runs').glob('narps-neutral-r3-*/dispatch.json'))
            if json.loads(p.read_bytes())['status'] == 'launcher-dispatched']
assert sha(D) == EXPECTED
assert not (B/'round-03-wave-01').exists()
processes, records = [], []
next_wave = 1
with (Q/'concurrency-events.jsonl').open('x') as events:
    last = None
    while next_wave <= 8 or processes or active():
        for process, out, err, row in list(processes):
            code = process.poll()
            if code is not None:
                out.close(); err.close()
                row.update(returncode=code, finished_at=now())
                records.append(row)
                (Q/'completed-waves.json').write_text(json.dumps(records, indent=2)+'\n')
                processes.remove((process, out, err, row))
                if code:
                    raise SystemExit('Dispatcher failed; preserve existing workers and report without retry.')
        current = active()
        state = tuple(current)
        if state != last:
            event = {'at':now(), 'active_launcher_count':len(current), 'runs':current}
            events.write(json.dumps(event)+'\n'); events.flush(); last = state
        if next_wave <= 8 and len(current) + 3 <= 10:
            assert sha(D) == EXPECTED
            assert not (B/f'round-03-wave-{next_wave:02d}').exists()
            argv = [sys.executable,str(D),'--round','3','--wave',str(next_wave)]
            row = {'round':3,'wave':next_wave,'argv':argv,'started_at':now(),
                   'dispatcher_sha256':EXPECTED,'active_before_dispatch':current,
                   'authorized_maximum':10}
            (Q/f'wave-{next_wave:02d}-command.json').write_text(json.dumps(row,indent=2)+'\n')
            out=(Q/f'wave-{next_wave:02d}.stdout').open('xb')
            err=(Q/f'wave-{next_wave:02d}.stderr').open('xb')
            process=subprocess.Popen(argv,cwd=W,stdout=out,stderr=err)
            processes.append((process,out,err,row))
            print(json.dumps({'wave':next_wave,'pid':process.pid,'at':row['started_at']}),flush=True)
            # Reserve all three slots until the existing dispatcher writes its receipt.
            receipt=B/f'round-03-wave-{next_wave:02d}/dispatch.json'
            while not receipt.exists() and process.poll() is None: time.sleep(1)
            next_wave += 1
        else:
            time.sleep(2)
assert all((B/f'round-03-wave-{w:02d}/result.json').is_file() for w in range(1,9))
(Q/'result.json').write_text(json.dumps({'status':'all24-assigned-research-launchers-finished',
    'maximum_simultaneous_native_sessions':10,'waves':records},indent=2)+'\n')
