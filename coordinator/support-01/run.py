"""Retain command, output and exit status for this one bounded package."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
cmd = ['nice', '-n', '10', 'pixi', 'run', '--manifest-path',
       '/Users/johnlee/code/CON/stamped-in-practice/pixi.toml', '--locked',
       'python', str(root / 'prepare.py')]
record = {'command': cmd, 'cwd': str(root),
          'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sources': [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                      for p in [root / 'run.py', root / 'prepare.py', root / 'test_support.py',
                                root / 'sources/package_retention.py', root / 'sources/package_delivery.py']]}
with (root / 'command.json').open('x') as stream:
    stream.write(json.dumps(record, indent=2) + '\n')
with (root / 'execution.stdout').open('xb') as out, (root / 'execution.stderr').open('xb') as err:
    result = subprocess.run(cmd, cwd=root, stdout=out, stderr=err)
record.update(returncode=result.returncode, finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
record['outputs'] = [{'path': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest(),
                      'size': (root / name).stat().st_size} for name in ['execution.stdout', 'execution.stderr']]
with (root / 'execution.json').open('x') as stream:
    stream.write(json.dumps(record, indent=2) + '\n')
print(json.dumps({'returncode': result.returncode, 'execution': str(root / 'execution.json')}))
raise SystemExit(result.returncode)
