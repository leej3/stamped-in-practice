from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

base = Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
batch = base / 'round-02-delivery-packaging-02'
repo = Path('/Users/johnlee/code/CON/stamped-in-practice')
source = batch / 'pinned-source/package_delivery.py'
source_pin = '90d4b4e24daa0bcfcfeb08b4a5dfcb2e6dcf72d5'
source_sha = 'b238d0f5e929d7dc2403255456c0d5393cfe6640842bc5607dbf50cec2016bdc'
validator_sha = '4929694dbeccfe546689b29886e2f9da6da7ecb90c50ea7f61ad91f15f72b111'

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def save(path, obj):
    with Path(path).open('x') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write('\n')

assert sha(source) == source_sha
assert sha(source.with_name('delivery_snapshot.py')) == validator_sha
pixi = shutil.which('pixi')
nice = shutil.which('nice')
assert pixi and nice
rows = []
started = now()
for suffix in [f'{i:02d}' for i in range(1,25)]:
    run = 'narps-neutral-r2-' + suffix
    native = base / 'runs' / run / 'attempt-01/native'
    native_result = native / 'result.json'
    raw_result = native_result.read_bytes()
    record = json.loads(raw_result)
    stop = record['worker_end_state']
    assert record.get('finished_at') and record.get('returncode') is not None
    assert stop['path'] == 'worker-end-state.json'
    capture = native / 'original-delivery/manifest.json'
    end_state = native / 'worker-end-state.json'
    assert stop['capture']['uri'] == str(capture)
    retention = base / 'runs' / run / 'retention'
    retention.mkdir(exist_ok=True)
    output = retention / 'delivery-package-01'
    assert not output.exists()
    command = [nice, '-n', '10', pixi, 'run', '--manifest-path', str(repo / 'pixi.toml'),
               '--locked', 'python', str(source), '--capture', str(capture),
               '--end-state', str(end_state), '--expected-capture-sha256', stop['capture']['sha256'],
               '--expected-end-state-sha256', stop['sha256'], '--output', str(output)]
    launch = {'run_id': run, 'started_at': now(), 'command': command, 'cwd': str(repo),
              'helper_commit': source_pin, 'helper_sha256': source_sha,
              'frozen_validator_sha256': validator_sha, 'native_result_sha256': hashlib.sha256(raw_result).hexdigest(),
              'expected_capture_sha256': stop['capture']['sha256'], 'expected_end_state_sha256': stop['sha256'],
              'original_head_commit': stop['head_commit'], 'driver_source_sha256': sha(__file__),
              'coordinator_manifest_sha256': sha(repo / 'pixi.toml'),
              'coordinator_lock_sha256': sha(repo / 'pixi.lock')}
    launch_path = retention / 'delivery-package-01-launch.json'
    stdout_path = retention / 'delivery-package-01-stdout.log'
    stderr_path = retention / 'delivery-package-01-stderr.log'
    save(launch_path, launch)
    print(json.dumps({'run_id': run, 'state': 'started', 'at': now()}), flush=True)
    with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
        completed = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr)
    result = json.loads((output / 'result.json').read_text()) if (output / 'result.json').exists() else None
    row = {'run_id': run, 'finished_at': now(), 'returncode': completed.returncode,
           'result': result, 'launch_sha256': sha(launch_path), 'stdout_sha256': sha(stdout_path),
           'stderr_sha256': sha(stderr_path), 'native_result_unchanged': sha(native_result) == launch['native_result_sha256']}
    if output.exists():
        row['package_index_sha256'] = sha(output / 'index.json') if (output / 'index.json').exists() else None
        archive = output / 'delivery.tar.gz'
        if archive.exists():
            row['archive_sha256'] = sha(archive)
            row['archive_bytes'] = archive.stat().st_size
    save(retention / 'delivery-package-01-execution.json', row)
    rows.append(row)
    print(json.dumps({'run_id': run, 'state': 'finished', 'returncode': completed.returncode,
                      'capture_status': result and result['capture_status'],
                      'archive_verified': result and result['archive_verified'],
                      'archive_bytes': row.get('archive_bytes')}), flush=True)
    for path in [launch_path, stdout_path, stderr_path, retention / 'delivery-package-01-execution.json']:
        path.chmod(0o444)
    if (completed.returncode != 0 or not result or result['status'] != 'packaged' or
            not result['archive_verified'] or not row['native_result_unchanged']):
        save(batch / 'result.json', {'status': 'stopped-on-error', 'started_at': started, 'finished_at': now(), 'runs': rows})
        sys.exit(1)
save(batch / 'result.json', {'status': 'complete', 'started_at': started, 'finished_at': now(), 'runs': rows})
