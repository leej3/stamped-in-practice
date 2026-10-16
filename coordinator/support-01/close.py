"""Bind successful run01 package, commands, checks and source snapshots."""
import hashlib
import json
import os
from pathlib import Path
import stat

root = Path(__file__).resolve().parent
assert json.loads((root / 'execution.json').read_bytes())['returncode'] == 0
assert json.loads((root / 'tests-result.json').read_bytes())['returncode'] == 0
result = json.loads((root / 'result.json').read_bytes())
assert result['status'] == 'verified' and not result['published']
legacy = Path('/Users/johnlee/code/CON/stamped-in-practice/scripts/package_retention.py')
assert legacy.read_bytes() == (root / 'sources/package_retention.py').read_bytes()
proof = {'schema': 'neutral-support-package-proof-index-v1', 'status': 'verified',
         'run': result['run'], 'coordinator_support_commit': None, 'published': False,
         'archive': result['support_archive'],
         'source_root': str(root.parent / 'runs' / result['run']),
         'original_source_unchanged': True,
         'frozen_legacy_packager_unchanged': True,
         'staging_bound_by': 'support-archive-inventory.json',
         'staging_mode_notice': 'Staging retains original source modes; its modes were not changed to mark metadata read-only.',
         'files': []}
for directory, dirs, files in os.walk(root, followlinks=False):
    if Path(directory) == root:
        dirs.remove('staging')
    for name in sorted(files):
        p = Path(directory) / name
        assert p.is_file() and not p.is_symlink()
        assert p.name != 'proof-index.json'
        proof['files'].append({'path': p.relative_to(root).as_posix(),
              'size': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
proof['files'].sort(key=lambda x: x['path'])
with (root / 'proof-index.json').open('x') as stream:
    stream.write(json.dumps(proof, indent=2, sort_keys=True) + '\n')
for row in proof['files']:
    (root / row['path']).chmod(0o444)
(root / 'proof-index.json').chmod(0o444)
print(json.dumps({'proof_index': str(root / 'proof-index.json'),
                  'sha256': hashlib.sha256((root / 'proof-index.json').read_bytes()).hexdigest(),
                  'files': len(proof['files'])}))
