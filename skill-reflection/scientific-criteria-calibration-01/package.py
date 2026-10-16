from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import tarfile

P = Path(__file__).resolve().parent
T = P / 'content'
sha = lambda data: hashlib.sha256(data).hexdigest()
def inventory(root):
    rows = []
    def visit(path):
        info = path.lstat()
        row = {'path': str(path.relative_to(root)), 'mode': stat.S_IMODE(info.st_mode)}
        if stat.S_ISLNK(info.st_mode):
            row.update(kind='symlink', target=os.readlink(path))
        elif stat.S_ISREG(info.st_mode):
            data = path.read_bytes()
            row.update(kind='file', bytes=len(data), sha256=sha(data))
        elif stat.S_ISDIR(info.st_mode):
            row.update(kind='directory')
        else:
            raise ValueError('Unsupported special file: ' + str(path))
        rows.append(row)
        if row['kind'] == 'directory':
            for child in sorted(path.iterdir()):
                visit(child)
    for child in sorted(root.iterdir()):
        visit(child)
    return rows
before = inventory(T)
(P / 'source-manifest.json').write_text(json.dumps({'source': str(T), 'entries': before,
    'exclusions': [], 'scope': 'Every trial path, including Git metadata, replay environment and failed commands; literal symlink text retained.'}, indent=2) + '\n')
archive = P / 'calibration.tar.gz'
with tarfile.open(archive, 'w:gz', dereference=False, format=tarfile.PAX_FORMAT) as tar:
    for row in before:
        tar.add(T / row['path'], arcname=row['path'], recursive=False)
assert before == inventory(T), 'Source changed during archive creation'
expected = {row['path']: row for row in before}
seen = set()
with tarfile.open(archive, 'r:gz') as tar:
    for member in tar:
        assert member.name in expected and member.name not in seen
        row = expected[member.name]
        seen.add(member.name)
        assert member.mode == row['mode'], member.name
        if row['kind'] == 'file':
            assert member.isfile() and member.size == row['bytes']
            handle = tar.extractfile(member)
            assert handle is not None
            assert sha(handle.read()) == row['sha256'], member.name
        elif row['kind'] == 'symlink':
            assert member.issym() and member.linkname == row['target'], member.name
        else:
            assert member.isdir(), member.name
assert seen == set(expected)
assert before == inventory(T), 'Source changed during verification'
receipt = {'verified': True, 'archive': archive.name, 'archive_sha256': sha(archive.read_bytes()),
           'archive_bytes': archive.stat().st_size, 'members': len(before),
           'regular_bytes': sum(row.get('bytes', 0) for row in before),
           'source_manifest_sha256': sha((P / 'source-manifest.json').read_bytes()),
           'all_members_hash_mode_link_verified': True, 'source_before_archive_after_equal': True,
           'exclusions': [], 'remote_payload_status': 'Hub upload and independent payload retrieval pending; neither attempted.'}
(P / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
