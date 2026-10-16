"""Bounded configured support preservation; external neutral scope override.

Reads only closed run evidence and immutable proof files. No Git writes, science
execution, credential access, symlink extraction or original-source mutations.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tarfile
import types

ROOT = Path(__file__).resolve().parent
B2 = ROOT.parent
CONFIG = json.loads((ROOT / 'config.json').read_bytes())
RUN = CONFIG['run']
SOURCE = B2 / 'runs' / RUN
STOP = 'attempt-01/native/worker-end-state.json'
CAPTURE = 'attempt-01/native/original-delivery'
DELIVERY = 'retention/delivery-package-01'
EXCLUDED = [CAPTURE + '/content', DELIVERY + '/delivery.tar.gz']


def require(value, message):
    if not value:
        raise ValueError(message)


def load_module(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


legacy = load_module('legacy_retention', ROOT / 'sources/package_retention.py')
delivery = load_module('reviewed_delivery', ROOT / 'sources/package_delivery.py')


def read(path):
    return json.loads(path.read_bytes())


def write(path, obj):
    with path.open('x') as stream:
        stream.write(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def record(path):
    return {'path': str(path), 'size': path.stat().st_size,
            'sha256': legacy.digest(path)}


def inventory(root, prefix):
    rows = delivery.inventory_capture(root)
    return [{**row, 'path': prefix + row['path'][len('original-delivery'):]}
            for row in rows]


def is_excluded(path):
    return any(path == p or path.startswith(p + '/') for p in EXCLUDED)


def check_identity(item):
    actual = record(Path(item['path']))
    require(actual == item, 'Proof identity changed: ' + item['path'])


def select_closed(assigned, closures):
    require(assigned, 'No registered judgments for run')
    selected = []
    for assignment in assigned:
        matches = [(path, closure, judge) for path, closure in closures
                   for judge in closure['judgments'] if judge['assignment'] == assignment]
        require(len(matches) == 1, 'Assigned judgment lacks exactly one closed preservation receipt')
        path, closure, judge = matches[0]
        require(closure['preservation_complete'] and judge['preservation_verified'],
                'Assigned judge preservation incomplete')
        selected.append(matches[0])
    return selected


def write_archive(path, stage, rows):
    with path.open('xb') as output, gzip.GzipFile(fileobj=output, mode='wb',
            filename='', mtime=0, compresslevel=6) as zipped:
        with tarfile.open(fileobj=zipped, mode='w|', format=tarfile.PAX_FORMAT) as archive:
            for row in rows:
                member = tarfile.TarInfo(row['path'])
                member.mode = row['mode']
                member.uid = member.gid = member.mtime = 0
                if row['kind'] == 'directory':
                    member.type = tarfile.DIRTYPE
                    archive.addfile(member)
                elif row['kind'] == 'symlink':
                    member.type = tarfile.SYMTYPE
                    member.linkname = row['link_target']
                    archive.addfile(member)
                else:
                    member.size = row['size']
                    parent, name = delivery._parent(stage, row['path'])
                    try:
                        stream, metadata = delivery._file(parent, name)
                        with stream:
                            archive.addfile(member, stream)
                            delivery._stable(parent, name, metadata, stream)
                    finally:
                        os.close(parent)


def verify_archive(path, rows):
    """Independent header and streamed-byte check; never extract any path."""
    expected = {row['path']: row for row in rows}
    require(len(expected) == len(rows), 'Duplicate expected members')
    observed = set()
    total = 0
    with gzip.open(path, 'rb') as zipped, tarfile.open(
            fileobj=zipped, mode='r|', ignore_zeros=True) as archive:
        for member in archive:
            name = str(delivery._relative(member.name))
            require(name not in observed and name in expected,
                    'Duplicate or unexpected member: ' + name)
            observed.add(name)
            row = expected[name]
            require(member.mode == row['mode'], 'Mode mismatch: ' + name)
            if row['kind'] == 'directory' and member.isdir():
                require(member.size == 0, 'Directory has payload: ' + name)
                continue
            if row['kind'] == 'symlink' and member.issym():
                require(member.size == 0 and member.linkname == row['link_target']
                        and hashlib.sha256(os.fsencode(member.linkname)).hexdigest()
                        == row['sha256'], 'Literal link mismatch: ' + name)
                continue
            require(row['kind'] == 'file' and member.isfile() and not member.islnk(),
                    'Kind mismatch: ' + name)
            require(member.size == row['size'], 'Size mismatch: ' + name)
            with archive.extractfile(member) as stream:
                require(delivery._digest(stream) == row['sha256'],
                        'Byte mismatch: ' + name)
            total += member.size
    require(observed == set(expected), 'Missing archive member')
    return {'verified': True, 'members': len(observed), 'regular_file_bytes': total,
            'checks': ['exact member set', 'kinds', 'modes', 'streamed SHA256',
                       'literal symlink targets', 'gzip integrity'], 'extracted': False}


def prepare():
    require(not (ROOT / 'staging').exists(), 'Never overwrite staging or failed attempts')
    before = inventory(SOURCE, 'evidence')
    write(ROOT / 'source-before.json', before)
    stop = read(SOURCE / STOP)
    native = read(SOURCE / 'attempt-01/native/result.json')
    manifest_path = SOURCE / CAPTURE / 'manifest.json'
    manifest = read(manifest_path)
    index_path = SOURCE / DELIVERY / 'index.json'
    index = read(index_path)
    require(stop['capture_status'] == 'complete' and not stop['errors'], 'Incomplete original capture')
    require(native['returncode'] == 0 and native['finished_at'] and not native['timed_out'],
            'Worker is not naturally closed')
    require(stop['head_commit'] == native['worker_end_state']['head_commit']
            == manifest['head_commit'] == index['worker_head_commit'], 'Original HEAD mismatch')
    require(legacy.digest(SOURCE / STOP) == native['worker_end_state']['sha256']
            == index['end_state_sha256'], 'Stop identity mismatch')
    capture_sha = legacy.digest(manifest_path)
    require(capture_sha == stop['capture']['sha256']
            == native['worker_end_state']['capture']['sha256']
            == index['capture_sha256'], 'Capture identity mismatch')
    require(manifest['capture_status'] == 'complete' and not manifest['errors'], 'Capture has errors')
    archive = SOURCE / DELIVERY / 'delivery.tar.gz'
    archive_row = next(x for x in index['files'] if x['path'] == 'delivery.tar.gz')
    require(archive.stat().st_size == archive_row['bytes'] and
            legacy.digest(archive) == archive_row['sha256'], 'Archive differs from reviewed index')
    archive_rows = read(SOURCE / DELIVERY / 'archive-inventory.json')
    original_archive_verification = delivery.verify_archive(archive, archive_rows,
            capture_sha, legacy.digest(SOURCE / STOP))
    write(ROOT / 'original-archive-reverification.json', original_archive_verification)

    pubroot = B2 / CONFIG['publication_directory']
    publication = read(pubroot / 'publication-summary.json')
    fresh_path = pubroot / publication['independent_retrieval_proof']
    require(legacy.digest(fresh_path) == publication['independent_retrieval_proof_sha256'],
            'Cold retrieval proof binding differs')
    published = next(x for x in publication['runs'] if x['run_id'] == RUN)
    retrieved = next(x for x in read(fresh_path)['runs'] if x['run_id'] == RUN)
    require(publication['success'] and retrieved['success']
            and retrieved['archive_absent_before_get'] and retrieved['verification']['verified'],
            'Original archive lacks successful independent retrieval')
    require(published['actual_archive_sha256'] == retrieved['actual_archive_sha256']
            == archive_row['sha256'] and published['actual_archive_bytes']
            == retrieved['actual_archive_bytes'] == archive_row['bytes'], 'Published archive mismatch')
    require(published['package_index_sha256'] == retrieved['package_index_sha256']
            == legacy.digest(index_path), 'Reviewed package index mismatch')
    require(published['capture_sha256'] == retrieved['capture_sha256'] == capture_sha
            and published['commit'] == retrieved['commit'], 'Published capture/commit mismatch')
    key = f"SHA256E-s{archive_row['bytes']}--{archive_row['sha256']}.tar.gz"
    require(published['archive_key'] == retrieved['archive_key'] == key, 'Annex key mismatch')
    reconstruction = {
        'code_remote': 'git@github.com:leej3/stamped-in-practice.git',
        'published_commit': published['commit'], 'archive_path': 'coordinator/delivery-01/delivery.tar.gz',
        'archive_sha256': archive_row['sha256'], 'archive_size': archive_row['bytes'],
        'annex_key': key, 'package_index_sha256': legacy.digest(index_path),
        'independent_retrieval_proof_sha256': legacy.digest(fresh_path),
        'retrieval_guide': 'https://github.com/leej3/stamped-in-practice/blob/main/RETRIEVAL.md',
        'annex_remote_name': 'con-hub',
        'annex_git_url': 'https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git',
        'annex_url': 'annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp',
    }
    original_by_path = {x['path']: x for x in archive_rows}
    mappings = []
    for row in before:
        relative = '.' if row['path'] == 'evidence' else row['path'].removeprefix('evidence/')
        item = {'source_entry': row, 'source_relative_path': relative}
        if relative == EXCLUDED[0] or relative.startswith(EXCLUDED[0] + '/'):
            member = 'original-delivery/' + relative.removeprefix(CAPTURE + '/')
            require({**row, 'path': member} == original_by_path[member],
                    'Excluded entry differs from archive member: ' + relative)
            item.update(disposition='existing-published-archive-member', archive_member=member,
                        reconstruction='original-delivery-reconstruction.json')
        elif relative == EXCLUDED[1]:
            require(row['kind'] == 'file' and row['sha256'] == archive_row['sha256']
                    and row['size'] == archive_row['bytes'], 'Duplicate archive identity mismatch')
            item.update(disposition='existing-published-archive',
                        reconstruction='original-delivery-reconstruction.json')
        else:
            item.update(disposition='retained', support_archive_member=row['path'])
        mappings.append(item)

    registered_path = B2 / 'dataset/rounds/round-01/plan.json'
    registered = read(registered_path)
    assigned = [x for x in registered['assigned_judgments'] if x['run'] == RUN]
    closures = [(path, read(path)) for path in sorted(B2.glob('round-01-judge-batch-*/retention-closed.json'))]
    selected = select_closed(assigned, closures)
    closure_paths = sorted({path for path, _, _ in selected})
    for path, closure, judge in selected:
        check_identity(closure['registered_plan'])
        require(closure['preservation_complete'] and judge['preservation_verified'],
                'Assigned judge preservation incomplete')
        for proof in [judge['main_capture_manifest'], judge['main_integrity_audit'],
                      judge['main_verification'], judge['main_script'], *judge['external_receipts'],
                      *closure['helper_files_at_closure']]:
            check_identity(proof)

    evidence = [DELIVERY + '/' + p for p in ['index.json', 'archive-inventory.json',
                'verification.json', 'worker-end-state.json']] + [CAPTURE + '/manifest.json']
    plan = {'version': 1, 'source': str(SOURCE), 'worker_stop': STOP,
            'scientific_result': stop['head_commit'],
            'exclude': [{'path': p, 'reason': 'Exact duplicate of independently retrieved published original delivery; complete member mapping retained in neutral addendum.',
                         'reconstruct_from': reconstruction, 'evidence': evidence} for p in EXCLUDED]}
    write(ROOT / 'package-plan.json', plan)
    legacy.package(ROOT / 'package-plan.json', ROOT / 'staging')
    stage = ROOT / 'staging'
    included = [x for x in before if not is_excluded(x['path'].removeprefix('evidence/'))]
    # Legacy copier preserves file modes, but not directory/link modes. Restore
    # only the staged equivalents, then independently compare the full inventory.
    for row in sorted(included, key=lambda x: x['path'].count('/'), reverse=True):
        path = stage / row['path']
        if row['kind'] == 'directory':
            path.chmod(row['mode'])
        elif row['kind'] == 'symlink':
            os.chmod(path, row['mode'], follow_symlinks=False)
    require(inventory(stage / 'evidence', 'evidence') == included, 'Full copied inventory differs')
    require(inventory(SOURCE, 'evidence') == before, 'Original source changed during copy')
    write(stage / 'source-inventory.json', before)
    write(stage / 'path-mapping.json', mappings)
    write(stage / 'original-delivery-reconstruction.json', reconstruction)

    # Explicit supplemental metadata only, not recipient/publisher cache trees.
    proof_paths = [registered_path, *closure_paths]
    for _, closure, _ in selected:
        proof_paths += [Path(x['path']) for x in closure['helper_files_at_closure']]
    for directory in [pubroot, pubroot / 'fresh-check-01',
                      B2 / CONFIG['browsable_directory'],
                      B2 / CONFIG['browsable_directory'] / 'fresh-check-01']:
        proof_paths += sorted(p for p in directory.iterdir() if p.is_file() and not p.is_symlink())
    extras = []
    for source in sorted(set(proof_paths)):
        original = record(source)
        destination = stage / 'closure' / source.relative_to(B2)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        destination.chmod(stat.S_IMODE(source.stat().st_mode))
        require(record(source) == original and legacy.digest(destination) == original['sha256'],
                'Supplemental proof changed during copy: ' + str(source))
        extras.append({**original, 'package_path': destination.relative_to(stage).as_posix()})
    write(stage / 'supplemental-proof-index.json', extras)
    for source in [Path(__file__), ROOT / 'sources/package_retention.py',
                   ROOT / 'sources/package_delivery.py', ROOT / 'test_support.py',
                   ROOT / 'tests-result.json', ROOT / 'command.json', ROOT / 'config.json',
                   ROOT / 'adaptation.patch']:
        destination = stage / 'coordinator-sources' / source.name
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, destination)
        require(legacy.digest(destination) == legacy.digest(source), 'Source snapshot mismatch')
    neutral = {
        'schema': 'neutral-complete-support-package-v1', 'run': RUN, 'status': 'staged-verified',
        'authority': 'This neutral addendum OVERRIDES the legacy package-manifest.json scientific_object block in its entirety. The legacy scientific_result/result_commit names refer only to the actual stopped seed HEAD. The absent legacy worktree field and artifact_count=0 do not describe neutral delivery completeness or artifact count.',
        'worker_identity': {'actual_worker_head': stop['head_commit'],
            'starting_seed_head': native['starting_commit'],
            'capture_manifest_sha256': capture_sha, 'capture_status': 'complete',
            'capture_manifest_entry_count': len(manifest['entries']),
            'stop_receipt_sha256': legacy.digest(SOURCE / STOP),
            'coordinator_support_commit': None},
        'scope': 'Complete run-tree support preservation, including all attempts, raw native and processed transcripts, skill availability/use/supplements, outer execution/Duct records, errors and the full assigned-judge subtree. Only the two mapped copies of the published original-delivery payload are omitted. All other run-tree entries remain byte/mode/link exact. No scientific result or judgment is inferred from retention integrity.',
        'source_root': str(SOURCE), 'source_entries_including_root': len(before),
        'retained_source_entries_including_root': len(included),
        'excluded_source_entries': len(before) - len(included),
        'exclusion_paths': EXCLUDED, 'complete_path_mapping': 'path-mapping.json',
        'source_root_mapping': {'source': '.', 'support_archive_member': 'evidence'},
        'assigned_judgments': assigned,
        'closed_judge_proofs': ['closure/' + p.relative_to(B2).as_posix() for p in closure_paths],
        'judge_target_as_found': 'Every existing judgment and as-found-target subtree is retained exactly; retention integrity is independent of formal assessment admission.',
        'additional_proofs': 'supplemental-proof-index.json',
        'legacy_manifest': 'package-manifest.json', 'legacy_plan': 'package-plan.json',
        'mode_scope': 'Exact regular-file, directory and literal-symlink permission modes; no ownership/timestamp/xattr equivalence claimed.',
        'source_before_copy_after_equal': True,
        'central_extraction_records': 'Outside this run-tree archive. Coordinator will bind later readable extraction copies and native-publication proof in the final descendant.',
        'retrieval_guide': reconstruction['retrieval_guide'],
        'scientific_execution': False, 'scientific_grading': False,
        'original_source_mutations': False, 'published': False,
    }
    write(stage / 'NEUTRAL-SCOPE-OVERRIDE.json', neutral)
    rows = inventory(stage, 'stage')
    rows = [{**x, 'path': x['path'][len('stage/'):]} for x in rows if x['path'] != 'stage']
    write(ROOT / 'support-archive-inventory.json', rows)
    write_archive(ROOT / 'support.tar.gz', stage, rows)
    verification = verify_archive(ROOT / 'support.tar.gz', rows)
    current = [{**x, 'path': x['path'][len('stage/'):]} for x in inventory(stage, 'stage')
               if x['path'] != 'stage']
    require(current == rows, 'Stage changed while archiving')
    require(inventory(SOURCE, 'evidence') == before, 'Original source changed while archiving')
    for item in extras:
        check_identity({k: item[k] for k in ['path', 'size', 'sha256']})
    write(ROOT / 'verification.json', {**verification, 'source_before_copy_after_equal': True,
            'staging_before_after_equal': True, 'supplemental_proofs_unchanged': True,
            'original_archive_reverified': True, 'excluded_path_mapping_complete': True})
    result = {'status': 'verified', 'run': RUN, 'support_archive': record(ROOT / 'support.tar.gz'),
        'archive_inventory': record(ROOT / 'support-archive-inventory.json'),
        'neutral_scope_override': record(stage / 'NEUTRAL-SCOPE-OVERRIDE.json'),
        'path_mapping': record(stage / 'path-mapping.json'), 'verification': record(ROOT / 'verification.json'),
        'source_entries': len(before), 'retained_source_entries': len(included),
        'excluded_entries': len(before)-len(included), 'archive_members': len(rows),
        'original_worker_head': stop['head_commit'], 'capture_manifest_sha256': capture_sha,
        'coordinator_support_commit': None, 'published': False}
    write(ROOT / 'result.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    try:
        prepare()
    except Exception as error:
        write(ROOT / 'failure.json', {'status': 'failed', 'error': repr(error)})
        raise
