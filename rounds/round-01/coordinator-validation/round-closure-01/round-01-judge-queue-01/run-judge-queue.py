"""Run the fixed assigned judging groups sequentially, preserving every attempt."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
B = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--round', type=int, required=True)
a = parser.parse_args()
plan = json.loads((B / f'dataset/rounds/round-{a.round:02d}/plan.json').read_text())
assert plan['maximum_simultaneous_native_sessions'] == 3
assert len(plan['assigned_judgments']) == 32
for wave in range(1, 9):
    stop = json.loads((B / f'round-{a.round:02d}-wave-{wave:02d}/stop-validation.json').read_text())
    assert len(stop['runs']) == 3
out = B / f'round-{a.round:02d}-judge-queue-01'
out.mkdir(exist_ok=False)
def save(name, value):
    with (out / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
driver = B / 'launch-judgments.py'
sha = hashlib.sha256(driver.read_bytes()).hexdigest()
(out / 'run-judge-queue.py').write_bytes(Path(__file__).read_bytes())
(out / 'launch-judgments.py').write_bytes(driver.read_bytes())
rows = []
for batch in range(1, 12):
    assert hashlib.sha256(driver.read_bytes()).hexdigest() == sha
    command = [sys.executable, str(driver), '--round', str(a.round), '--batch', str(batch)]
    row = {'batch': batch, 'command': command, 'started_at': now(), 'dispatcher_sha256': sha}
    save(f'batch-{batch:02d}-launch.json', row)
    print(json.dumps({'batch': batch, 'state': 'dispatching'}), flush=True)
    with (out / f'batch-{batch:02d}.stdout').open('xb') as stdout, (out / f'batch-{batch:02d}.stderr').open('xb') as stderr:
        result = subprocess.run(command, stdout=stdout, stderr=stderr)
    row.update(returncode=result.returncode, finished_at=now())
    save(f'batch-{batch:02d}-result.json', row)
    rows.append(row)
    print(json.dumps({'batch': batch, 'state': 'finished', 'dispatcher_returncode': result.returncode}), flush=True)
    # A dispatcher/gate error stops orchestration; completed native attempt
    # outcomes never select replacements or block the next assigned group.
    if result.returncode:
        save('result.json', {'status': 'dispatcher-error', 'batches': rows})
        raise SystemExit(result.returncode)
save('result.json', {'status': 'assigned-queue-complete', 'batches': rows})
