from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
D = P.parent / 'dataset'
R = P / 'fresh-git-01'
R.mkdir(exist_ok=False)
commands = []
def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, capture_output=True)
    number = len(commands)
    (P / ('git-check-%02d.stdout' % number)).write_bytes(result.stdout)
    (P / ('git-check-%02d.stderr' % number)).write_bytes(result.stderr)
    commands.append({'argv': argv, 'cwd': str(cwd), 'returncode': result.returncode,
                     'stdout': 'git-check-%02d.stdout' % number, 'stderr': 'git-check-%02d.stderr' % number})
    (P / 'git-check-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert result.returncode == 0
    return result.stdout
run(['git', 'init', '--bare', '.'], R)
run(['git', 'fetch', '--depth=1', '--no-tags', 'https://github.com/leej3/stamped-in-practice.git', 'refs/heads/codex/iteration-narps-neutral-v1'], R)
head = '42e66e56d585023bcb1a003c11676943683c4970'
assert run(['git', 'rev-parse', 'FETCH_HEAD'], R).decode().strip() == head
assert not (R / 'objects/info/alternates').exists()
paths = subprocess.check_output(['git', 'diff', '--name-only', '87e837e80bbda6b2801a08fd4090488c64c0c9e1', head], cwd=D, text=True).splitlines()
rows = []
for path in paths:
    local = subprocess.check_output(['git', 'show', head + ':' + path], cwd=D)
    received = subprocess.check_output(['git', 'show', head + ':' + path], cwd=R)
    assert local == received, path
    mode = subprocess.check_output(['git', 'ls-tree', head, '--', path], cwd=R, text=True).split()[0]
    rows.append({'path': path, 'mode': mode, 'git_blob_sha256': hashlib.sha256(received).hexdigest(), 'git_blob_bytes': len(received)})
result = {'verified': True, 'commit': head, 'files': rows, 'empty_git_store_no_alternates': True,
          'annex_payloads_retrieved': False, 'scope': 'Independent remote Git blobs and annex pointer identity only; the new calibration payload remain Hub-pending.'}
(P / 'git-publication-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'verified': True, 'commit': head, 'paths': len(rows)}))
