"""Independently retrieve a published coordinator bundle; never execute science."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile
import time

p = argparse.ArgumentParser(description=__doc__)
for name in ('branch', 'commit', 'original', 'manifest-sha256', 'archive-sha256',
             'scientific-retrieval', 'evidence'):
    p.add_argument('--' + name, required=True)
a = p.parse_args()
out = Path(a.evidence)
out.mkdir(parents=True, exist_ok=False)
recipient = out / 'recipient'
shutil.copyfile(__file__, out / 'verification.py')
px = ['pixi', 'run', '--as-is', '--manifest-path',
      '/Users/johnlee/code/CON/stamped-in-practice/pixi.toml']
commands = []

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def command(label, args, cwd=None):
    start = time.monotonic()
    result = subprocess.run(args, cwd=cwd or out, capture_output=True,
                            env=dict(os.environ, GIT_TERMINAL_PROMPT='0'), timeout=1800)
    stem = f'{len(commands) + 1:03d}-{label}'
    for name, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (out / (stem + '.' + name)).write_bytes(data)
    commands.append(dict(label=label, argv=args, cwd=str(cwd or out),
        returncode=result.returncode, elapsed_seconds=time.monotonic() - start,
        stdout=stem + '.stdout', stderr=stem + '.stderr'))
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if result.returncode:
        raise RuntimeError(f'{label}: exit {result.returncode}; see {stem}.stderr')
    return result.stdout

def git(label, *args):
    return command(label, ['git', '-C', str(recipient), *args])

summary = dict(success=False, original=a.original, retention_commit=a.commit,
               scientific_execution=False, worker_credit=False,
               started_at=datetime.now(timezone.utc).isoformat())
try:
    prior_path = Path(a.scientific_retrieval)
    prior = json.loads(prior_path.read_text())
    assert prior.get('passed', prior.get('success')) is True
    assert prior.get('target', prior.get('result_commit')) == a.original
    shutil.copyfile(prior_path, out / 'prior-scientific-retrieval.json')
    summary['scientific_payload_verification'] = {
        'scope': 'Previously verified independently; unchanged original Git tree below retention additions.',
        'source': str(prior_path), 'sha256': sha(prior_path)}
    command('init', ['git', 'init', str(recipient)])
    git('origin', 'remote', 'add', 'origin', 'git@github.com:leej3/stamped-in-practice.git')
    git('fetch-retention', 'fetch', '--no-tags', 'origin', a.branch)
    assert git('identity', 'rev-parse', 'FETCH_HEAD').decode().strip() == a.commit
    git('checkout', 'checkout', '--detach', a.commit)
    assert not (recipient / '.git/objects/info/alternates').exists()
    assert not (recipient / '.git/shallow').exists()
    assert git('parent', 'show', '-s', '--format=%P', a.commit).decode().strip() == a.original
    changed = git('changed-paths', 'diff-tree', '--no-commit-id', '--name-only', '-r',
                  a.commit).decode().splitlines()
    assert changed and all(x.startswith('coordinator/retention-01/') for x in changed)
    assert not git('science-tree-unchanged', 'diff', a.original, a.commit, '--', '.',
                   ':(exclude)coordinator/retention-01').strip()
    git('fetch-annex', 'fetch', '--no-tags', 'origin', 'git-annex:git-annex')
    git('ignore-github-content', 'config', 'remote.origin.annex-ignore', 'true')
    command('annex-init', px + ['git', '-C', str(recipient), 'annex', 'init',
                               'independent retained-object verification'])
    git('annex-origin', 'remote', 'add', 'con-hub',
        'https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git')
    git('annex-endpoint', 'config', 'remote.con-hub.annexurl',
        'annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp')
    prefix = 'coordinator/retention-01'
    inventory = [json.loads(line) for line in command('annex-inventory', px +
        ['git', '-C', str(recipient), 'annex', 'find', '--anything', '--json', '--', prefix]).splitlines()]
    assert inventory and all(not (recipient / x['file']).exists() for x in inventory)
    command('fetch-bundle-content', px + ['git', '-C', str(recipient), 'annex', 'get',
            '--from', 'con-hub', '--jobs', '3', '--json', '--', prefix])
    bundle = recipient / prefix
    manifest_path = bundle / 'package-manifest.json'
    archive = bundle / 'package.tar.gz'
    assert sha(manifest_path) == a.manifest_sha256
    assert sha(archive) == a.archive_sha256
    manifest = json.loads(manifest_path.read_text())
    receipt = json.loads((bundle / 'bundle-receipt.json').read_text())
    assert manifest['scientific_object']['result_commit'] == a.original
    assert receipt['archive']['sha256'] == a.archive_sha256
    with tarfile.open(archive, 'r:gz') as tar:
        raw_members = tar.getmembers()
        members = {m.name.rstrip('/'): m for m in raw_members}
        assert len(members) == len(raw_members), 'Duplicate archive member'
        expected = {x['package_path'] for x in manifest['files']} | {
            'evidence', 'package-manifest.json', 'package-plan.json', 'package_retention.py'}
        assert set(members) == expected
        for row in manifest['files']:
            m = members[row['package_path']]
            if row['kind'] == 'directory':
                assert m.isdir()
            elif row['kind'] == 'symlink':
                assert m.issym() and m.linkname == row['target']
            else:
                assert m.isfile() or m.islnk()
                h = hashlib.sha256(); size = 0
                with tar.extractfile(m) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        h.update(chunk); size += len(chunk)
                assert h.hexdigest() == row['sha256'] and size == row['size']
                assert stat.S_IMODE(m.mode) == row['mode']
        for name in ['package-manifest.json', 'package-plan.json', 'package_retention.py']:
            assert tar.extractfile(name).read() == (bundle / name).read_bytes()
    for row in receipt['indexable']:
        assert sha(bundle / row['path']) == row['sha256']
    assert all((recipient / row['file']).is_file() for row in inventory)
    summary.update(success=True, source_access='GitHub SSH and con-hub; no local object alternates',
        changed_paths=changed, scientific_git_tree_unchanged=True,
        all_bundle_payloads_initially_absent=True, annex_paths=len(inventory),
        archive_sha256=a.archive_sha256, archive_bytes=archive.stat().st_size,
        manifest_sha256=a.manifest_sha256, archive_entries_verified=len(manifest['files']),
        indexable_files_verified=len(receipt['indexable']), recipient=str(recipient))
except Exception as error:
    summary['error'] = f'{type(error).__name__}: {error}'
finally:
    summary['finished_at'] = datetime.now(timezone.utc).isoformat()
    (out / 'result.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
raise SystemExit(0 if summary['success'] else 1)
