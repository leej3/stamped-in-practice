"""Prospective v4 boundary fixtures; no formal study data or judgment prose."""
import copy
import json
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import assessment_procedure as procedure
import delivery_snapshot as delivery
import judge_workspace as judge
import aggregate_comparison as agg
from test_neutral_aggregation import bundle, allocation, contract
from test_aggregate_comparison import artifact, rewrite, bind_outputs


def copies(tmp_path):
    root = tmp_path / 'synthetic-worker'
    (root / '.git/annex/keysdb').mkdir(parents=True)
    (root / '.git/refs/heads').mkdir(parents=True)
    (root / '.git/objects').mkdir()
    (root / '.git/HEAD').write_text('ref: refs/heads/main\n')
    (root / '.git/refs/heads/main').write_text('a' * 40 + '\n')
    for name in ('config', 'index'):
        (root / '.git' / name).write_bytes(b'synthetic ' + name.encode())
    for name in ('db', 'db-shm', 'db-wal'):
        (root / '.git/annex/keysdb' / name).write_bytes(b'original ' + name.encode())
    (root / 'result.csv').write_text('x,y\n1,2\n')
    (root / '.gitignore').write_text('ignored.txt\n')
    (root / 'ignored.txt').write_text('ignored scientific bytes')
    (root / 'untracked.txt').write_text('untracked evidence')
    (root / 'link').symlink_to('result.csv')
    receipt = delivery.save_delivery(root, tmp_path / 'source-capture', {})
    source = Path(receipt['capture']['uri'])
    canonical = delivery.materialize_capture(source, tmp_path / 'canonical')
    operational = delivery.materialize_capture(source, tmp_path / 'operational')
    target = Path(operational['target'])
    identity = judge._target_identity(target, operational['manifest'], canonical['manifest'])
    return source, Path(canonical['manifest']), Path(operational['manifest']), target, identity


@pytest.mark.parametrize('change', ['none', 'database', 'sidecar-add-remove'])
def test_full_retention_distinguishes_metadata_and_canonical(tmp_path, change):
    source, canonical, operational, target, identity = copies(tmp_path)
    original_v3_identity = judge._target_identity(target, operational)
    if change == 'database':
        (target / '.git/annex/keysdb/db').write_bytes(b'mutated database')
    elif change == 'sidecar-add-remove':
        (target / '.git/annex/keysdb/db-shm').unlink()
        (target / '.git/annex/keysdb/db-wal').write_bytes(b'new wal state')
    if change != 'none':
        with pytest.raises(ValueError):
            delivery.validate_capture(operational)
        with pytest.raises(ValueError):
            judge.validate_target(target, identity)
        with pytest.raises(ValueError):
            judge.validate_target(target, original_v3_identity)
    result = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    assert result['canonical_unchanged'] and result['protected_unchanged']
    assert result['target_unchanged'] == (change == 'none')
    assert result['operational_metadata_changed'] == (change != 'none')
    assert result['logical_database_equivalence'] == 'not-claimed'
    final = Path(result['final_capture']['path'])
    delivery.validate_capture(final, result['final_capture']['sha256'])
    assert (final.parent / 'content/workspace/content/workspace/.git/annex/keysdb/db').read_bytes() == (target / '.git/annex/keysdb/db').read_bytes()
    assert (canonical.parent / 'content/workspace/.git/annex/keysdb/db').read_bytes() == b'original db'
    delivery.validate_capture(source)
    delivery.validate_capture(canonical)


@pytest.mark.parametrize('name', ['result.csv', 'ignored.txt', 'untracked.txt', '.git/HEAD',
    '.git/config', '.git/index', '.git/refs/heads/main', '.git/objects/new',
    '.git/annex/keysdb/unexpected', 'new-science.txt'])
def test_every_nonmatching_path_change_fails_and_is_retained(tmp_path, name):
    _, _, _, target, identity = copies(tmp_path)
    (target / name).write_bytes(b'changed')
    result = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    assert not result['protected_unchanged']
    assert not result['target_unchanged']
    assert result['rejected_changes'] == [{'change': 'added' if name in (
        '.git/objects/new', '.git/annex/keysdb/unexpected', 'new-science.txt') else 'modified',
        'path': 'content/workspace/' + name}]
    final = Path(result['final_capture']['path'])
    assert (final.parent / 'content/workspace/content/workspace' / name).read_bytes() == b'changed'


@pytest.mark.parametrize('change', ['symlink', 'database-link', 'database-mode', 'wrapper-mode', 'manifest', 'external'])
def test_no_link_mode_manifest_or_external_exemption(tmp_path, change):
    _, _, operational, target, identity = copies(tmp_path)
    if change == 'symlink':
        (target / 'link').unlink()
        (target / 'link').symlink_to('ignored.txt')
    elif change == 'database-link':
        (target / '.git/annex/keysdb/db').unlink()
        (target / '.git/annex/keysdb/db').symlink_to('../../../../result.csv')
    elif change == 'database-mode':
        (target / '.git/annex/keysdb/db').chmod(0o600)
    elif change == 'wrapper-mode':
        operational.parent.chmod(0o700)
    elif change == 'manifest':
        operational.write_bytes(operational.read_bytes() + b' ')
    else:
        (operational.parent / 'content/external/new').write_bytes(b'new external evidence')
    result = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    assert not result['protected_unchanged']
    assert result['rejected_changes']


@pytest.mark.parametrize('change', ['bytes', 'wrapper', 'identity'])
def test_canonical_is_always_exact(tmp_path, change):
    _, canonical, _, target, identity = copies(tmp_path)
    if change == 'bytes':
        (canonical.parent / 'content/workspace/.git/annex/keysdb/db').write_bytes(b'changed')
    elif change == 'wrapper':
        canonical.parent.chmod(0o700)
    else:
        identity['capture']['sha256'] = '0' * 64
    with pytest.raises((SystemExit, ValueError)):
        judge.retain_operational_target(target, identity, tmp_path / 'retained')


def test_overlay_preserves_prior_values_and_repository_selectors():
    original = {'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.hooksPath',
                'GIT_CONFIG_VALUE_0': '/some/hooks', 'GIT_DIR': '/selected/git', 'OTHER': 'keep'}
    environment = procedure.operational_environment(original)
    assert all(environment[k] == v for k, v in original.items() if k != 'GIT_CONFIG_COUNT')
    assert environment['GIT_CONFIG_COUNT'] == '3'
    assert environment['GIT_CONFIG_KEY_1'] == 'annex.merge-annex-branches'
    assert environment['GIT_CONFIG_VALUE_1'] == 'false'
    assert environment['GIT_CONFIG_KEY_2'] == 'annex.alwayscommit'
    assert environment['GIT_OPTIONAL_LOCKS'] == '0'
    assert original['GIT_CONFIG_COUNT'] == '1'
    for invalid in ({'GIT_CONFIG_COUNT': '-1'}, {'GIT_CONFIG_COUNT': 'bad'}, {'GIT_CONFIG_COUNT': '1'}):
        with pytest.raises(SystemExit):
            procedure.operational_environment(invalid)


@pytest.mark.parametrize('change', [None, 'pointer', 'external-admin'])
def test_retained_external_git_dependencies_are_not_reinterpreted(tmp_path, change):
    worker, admin = tmp_path / 'worker', tmp_path / 'git-admin'
    worker.mkdir()
    admin.mkdir()
    (admin / 'HEAD').write_text('a' * 40 + '\n')
    (worker / '.git').write_text(f'gitdir: {admin}\n')
    receipt = delivery.save_delivery(worker, tmp_path / 'source', {},
        declared_artifacts=[{'path': str(admin), 'provenance': 'Explicit synthetic dependency'}])
    assert receipt['capture_status'] == 'complete'
    source = Path(receipt['capture']['uri'])
    canonical = delivery.materialize_capture(source, tmp_path / 'canonical')
    operational = delivery.materialize_capture(source, tmp_path / 'operational')
    target = Path(operational['target'])
    identity = judge._target_identity(target, operational['manifest'], canonical['manifest'])
    assert identity['target_commit'] == 'a' * 40
    if change == 'pointer':
        (target / '.git').write_text('gitdir: /different/external/path\n')
    elif change == 'external-admin':
        (Path(operational['manifest']).parent / 'content/external/0000/HEAD').write_text('b' * 40 + '\n')
    result = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    assert result['capture_status'] == 'complete'
    assert result['protected_unchanged'] == (change is None)
    assert result['target_unchanged'] == (change is None)
    final = Path(result['final_capture']['path'])
    retained = json.loads(final.read_bytes())
    assert retained['kind'] == 'retained-container'
    assert retained['policy']['git_dependencies'] == delivery.OPAQUE_GIT_POLICY
    assert (final.parent / 'content/workspace/manifest.json').read_bytes() == source.read_bytes()
    delivery.validate_capture(canonical['manifest'])


def full_original(original):
    original = copy.deepcopy(original)
    original['fixed_files'] = dict.fromkeys((*procedure.NEUTRAL_FILES, 'requirements.json'), '4' * 64)
    original.update(resources={'path': 'requirements.json', 'sha256': '4' * 64},
        starting_environment={}, host_identity={}, settings={}, replay=procedure.NEUTRAL_REPLAY,
        gitmodules_sha256='5' * 64, role_hosts={'research': {}, 'judge': {}})
    return original


def amended(original, allocation, run):
    updated = copy.deepcopy(original)
    updated.update(version=4, operational_runtime=copy.deepcopy(procedure.OPERATIONAL_RUNTIME),
        assessment_amendment={'scope': 'assessment-only',
            'research_procedure_json': json.dumps(original),
            'research_procedure_sha256': agg.sha256(json.dumps(original).encode()),
            'allocation_json': json.dumps(allocation),
            'allocation_sha256': agg.sha256(json.dumps(allocation).encode()),
            'retained_objects': [{'run': run['run_id'], 'seed_commit': run['seed_commit'],
                'result_commit': run['result_commit'],
                'worker_end_state_sha256': run['worker_end_state']['sha256'],
                'delivery_capture_sha256': run['delivery_capture']['sha256']}]})
    updated['fixed_files'].update(dict.fromkeys(set(procedure.OPERATIONAL_FILES) - set(procedure.NEUTRAL_FILES), '6' * 64))
    return updated


def retained_pair(tmp_path, allocation, contract, head='a' * 40):
    index, original = bundle(tmp_path, allocation, contract, head=head)
    run = index['runs'][0]
    seal = amended(full_original(json.loads(original)), allocation, run)
    first = seal['assessment_amendment']['retained_objects'][0]
    second_stop = tmp_path / 'second-stop.json'
    second_stop.write_text('{"different_original_delivery": true}\n')
    second = dict(first, run=allocation['rounds'][0]['launch_order'][1]['run'],
        worker_end_state_sha256=agg.sha256(second_stop.read_bytes()), delivery_capture_sha256='b' * 64)
    seal['assessment_amendment']['retained_objects'].append(second)
    return seal, ((first, tmp_path / run['worker_end_state']['path']), (second, second_stop))


@pytest.mark.parametrize('head', ['a' * 40, None])
@pytest.mark.parametrize('reverse', [False, True])
def test_v4_shared_git_identities_bind_each_original_capture(tmp_path, allocation, contract, head, reverse):
    seal, pair = retained_pair(tmp_path, allocation, contract, head)
    if reverse:
        seal['assessment_amendment']['retained_objects'].reverse()
    for row, stop in pair:
        procedure.check_retained_target(seal, {'run': row['run']}, row['seed_commit'],
            row['result_commit'], stop, row['delivery_capture_sha256'])


@pytest.mark.parametrize('head', ['a' * 40, None])
@pytest.mark.parametrize('selected', [0, 1])
@pytest.mark.parametrize('field', ['stop', 'capture'])
def test_v4_shared_commits_do_not_allow_cross_run_delivery_swaps(tmp_path, allocation, contract, head, selected, field):
    seal, pair = retained_pair(tmp_path, allocation, contract, head)
    row, stop = pair[selected]
    other, other_stop = pair[1 - selected]
    # A shared seed does not permit one delivery to be attributed to its peer.
    label = 'stop receipt' if field == 'stop' else 'delivery capture'
    with pytest.raises(SystemExit, match='retained original ' + label):
        procedure.check_retained_target(seal, {'run': row['run']}, row['seed_commit'],
            row['result_commit'], other_stop if field == 'stop' else stop,
            other['delivery_capture_sha256'] if field == 'capture' else row['delivery_capture_sha256'])


@pytest.mark.parametrize('head,field,value', [
    ('a' * 40, 'seed_commit', 'c' * 40), ('a' * 40, 'result_commit', 'c' * 40),
    ('a' * 40, 'result_commit', None), (None, 'result_commit', 'c' * 40),
])
def test_v4_shared_git_identity_does_not_relax_exact_git_binding(tmp_path, allocation, contract, head, field, value):
    seal, pair = retained_pair(tmp_path, allocation, contract, head)
    original, stop = pair[0]
    row = dict(original, **{field: value})
    with pytest.raises(SystemExit, match='retained worker seed|retained scientific result'):
        procedure.check_retained_target(seal, {'run': row['run']}, row['seed_commit'],
            row['result_commit'], stop, row['delivery_capture_sha256'])


@pytest.mark.parametrize('allocated', [False, True])
def test_v4_unlisted_runs_cannot_reuse_registered_delivery(tmp_path, allocation, contract, allocated):
    seal, pair = retained_pair(tmp_path, allocation, contract)
    row, stop = pair[0]
    run = allocation['rounds'][0]['launch_order'][2]['run'] if allocated else 'unregistered'
    with pytest.raises(SystemExit, match='unregistered retained object'):
        procedure.check_retained_target(seal, {'run': run}, row['seed_commit'],
            row['result_commit'], stop, row['delivery_capture_sha256'])


@pytest.mark.parametrize('conflicting', [False, True])
def test_v4_duplicate_run_identity_is_rejected_before_admission(tmp_path, allocation, contract, conflicting):
    seal, pair = retained_pair(tmp_path, allocation, contract)
    row, stop = pair[0]
    duplicate = dict(row)
    if conflicting:
        duplicate['delivery_capture_sha256'] = 'c' * 64
    seal['assessment_amendment']['retained_objects'].append(duplicate)
    with pytest.raises(SystemExit, match='Retained run must be unique'):
        procedure.check_retained_target(seal, {'run': row['run']}, row['seed_commit'],
            row['result_commit'], stop, row['delivery_capture_sha256'])


@pytest.mark.parametrize('version', [1, 3])
def test_original_protocols_keep_retained_admission_passthrough(version):
    procedure.check_retained_target({'version': version}, {}, None, None, None)


def operational_bundle(tmp_path, allocation, contract, mutation='database'):
    index, original_bytes = bundle(tmp_path, allocation, contract, head='a' * 40)
    run = index['runs'][0]
    original = full_original(json.loads(original_bytes))
    original_bytes = json.dumps(original).encode()
    original_digest = agg.sha256(original_bytes)
    source, canonical, operational, target, identity = copies(tmp_path)
    capture = {'path': str(source), 'sha256': agg.sha256(source.read_bytes())}
    run['delivery_capture'] = capture
    manifest = json.loads(source.read_bytes())
    def stop_update(v):
        v['capture'] = dict(uri=str(source), sha256=capture['sha256'])
        v.update({key: manifest[key] for key in ('head_commit', 'capture_status', 'errors', 'omissions')})
    rewrite(tmp_path, run['worker_end_state'], stop_update)
    rewrite(tmp_path, run['worker_native']['procedure_status'], lambda v: v.update(procedure_sha256=original_digest))
    worker_status = agg.parse_json(agg.artifact(run['worker_native']['procedure_status'], tmp_path))
    def worker_update(v):
        v['procedure'] = worker_status
        v['worker_end_state'].update(sha256=run['worker_end_state']['sha256'], capture=dict(uri=str(source), sha256=capture['sha256']))
    rewrite(tmp_path, run['worker_native']['result'], worker_update)
    if mutation:
        (target / ('.git/annex/keysdb/db' if mutation == 'database' else mutation)).write_bytes(b'changed')
    integrity = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    seal = amended(original, allocation, run)
    seal_ref = artifact(tmp_path, 'v4-seal.json', seal)
    selection = {'assessment_seal': seal_ref, 'research_procedure_sha256': original_digest}
    index['comparison_provenance'] = selection
    judgment = run['judgments']['primary']
    rewrite(tmp_path, judgment['native']['procedure_status'], lambda v: v.update(
        procedure_sha256=seal_ref['sha256'], research_procedure_sha256=original_digest,
        worker_end_state_sha256=run['worker_end_state']['sha256'], operational_runtime=procedure.OPERATIONAL_RUNTIME))
    status = agg.parse_json(agg.artifact(judgment['native']['procedure_status'], tmp_path))
    def judge_update(v):
        v.update(procedure=status, target=identity, operational_integrity=integrity,
            operational_runtime=procedure.OPERATIONAL_RUNTIME,
            git_config_overlay={'inherited_count': 0, 'effective_count': 2,
                                'appended': procedure.OPERATIONAL_RUNTIME['git_config'], 'GIT_OPTIONAL_LOCKS': '0'})
        v.update({k: integrity[k] for k in ('target_unchanged', 'canonical_unchanged', 'operational_metadata_changed')})
    rewrite(tmp_path, judgment['native']['result'], judge_update)
    rewrite(tmp_path, judgment['response'], lambda v: v['object'].update(capture=identity['capture']))
    bind_outputs(tmp_path, judgment)
    return index, original_bytes, seal


def test_v4_gate_accepts_metadata_without_false_unchanged(tmp_path, allocation, contract):
    index, original, _ = operational_bundle(tmp_path, allocation, contract)
    selection = index['comparison_provenance']
    gate = agg.ProvenanceGate.load(original, selection, allocation, tmp_path, contract, selection['assessment_seal']['sha256'])
    run = index['runs'][0]
    check = gate.validate(run, run['judgments']['primary']['native'], tmp_path, allocation['rounds'][0]['launch_order'][0])
    assert check['assessment_version'] == 4
    assert not check['operational_integrity']['target_unchanged']
    assert check['operational_integrity']['canonical_unchanged']


def test_v4_gate_requires_declared_container_retention_policy(tmp_path, allocation, contract):
    index, original, _ = operational_bundle(tmp_path, allocation, contract)
    selection = index['comparison_provenance']
    gate = agg.ProvenanceGate.load(original, selection, allocation, tmp_path, contract,
                                  selection['assessment_seal']['sha256'])
    run = index['runs'][0]
    native = run['judgments']['primary']['native']
    def change_policy(result):
        reference = result['operational_integrity']['final_capture']
        rewrite(tmp_path, reference, lambda value: value['policy'].pop('git_dependencies'))
    rewrite(tmp_path, native['result'], change_policy)
    with pytest.raises(ValueError, match='git_dependencies'):
        gate.validate(run, native, tmp_path, allocation['rounds'][0]['launch_order'][0])


@pytest.mark.parametrize('mutation', ['result.csv', '.git/index', '.git/refs/heads/main'])
def test_v4_gate_rejects_substantive_or_lineage_changes(tmp_path, allocation, contract, mutation):
    index, original, _ = operational_bundle(tmp_path, allocation, contract, mutation)
    selection = index['comparison_provenance']
    gate = agg.ProvenanceGate.load(original, selection, allocation, tmp_path, contract, selection['assessment_seal']['sha256'])
    run = index['runs'][0]
    with pytest.raises(ValueError):
        gate.validate(run, run['judgments']['primary']['native'], tmp_path, allocation['rounds'][0]['launch_order'][0])


@pytest.mark.parametrize('field', ['seed_commit', 'result_commit', 'worker_end_state_sha256', 'delivery_capture_sha256'])
def test_v4_requires_prebound_original_identities(tmp_path, allocation, contract, field):
    index, original, seal = operational_bundle(tmp_path, allocation, contract)
    seal['assessment_amendment']['retained_objects'][0][field] = '0' * (40 if field.endswith('commit') else 64)
    gate = agg.ProvenanceGate(json.loads(original), agg.sha256(original), seal,
        index['comparison_provenance']['assessment_seal']['sha256'])
    run = index['runs'][0]
    with pytest.raises(ValueError):
        gate.validate(run, run['judgments']['primary']['native'], tmp_path, allocation['rounds'][0]['launch_order'][0])


@pytest.mark.parametrize('v4_digest', [True, False])
def test_original_gate_cannot_consume_v4_receipt(tmp_path, allocation, contract, v4_digest):
    index, original, _ = operational_bundle(tmp_path, allocation, contract, mutation=None)
    run = index['runs'][0]
    native = run['judgments']['primary']['native']
    if not v4_digest:
        rewrite(tmp_path, native['procedure_status'], lambda v: v.update(procedure_sha256=agg.sha256(original)))
        status = agg.parse_json(agg.artifact(native['procedure_status'], tmp_path))
        rewrite(tmp_path, native['result'], lambda v: v.update(procedure=status))
    gate = agg.ProvenanceGate(json.loads(original), agg.sha256(original), json.loads(original), agg.sha256(original))
    with pytest.raises(ValueError):
        gate.validate(run, native, tmp_path, allocation['rounds'][0]['launch_order'][0])


@pytest.mark.parametrize('field', ['assessment', 'study', 'settings', 'replay', 'role_hosts', 'conditions'])
def test_v4_amendment_preserves_frozen_boundaries(tmp_path, allocation, contract, field):
    _, _, seal = operational_bundle(tmp_path, allocation, contract)
    seal[field] = {'changed': True}
    with pytest.raises(SystemExit):
        procedure.operational_research_procedure(seal)


def test_v4_amendment_rejects_research_changes_and_allocation_rewrite(tmp_path, allocation, contract):
    _, original, seal = operational_bundle(tmp_path, allocation, contract)
    assert procedure.operational_research_procedure(seal) == json.loads(original)
    changed = copy.deepcopy(seal)
    changed['fixed_files']['prompts/neutral-judge.md'] = '0' * 64
    with pytest.raises(SystemExit):
        procedure.operational_research_procedure(changed)
    seal['assessment_amendment']['allocation_json'] += ' '
    with pytest.raises(SystemExit):
        procedure.operational_research_procedure(seal)


def test_v4_replay_uses_canonical_and_preserves_prior_git_overlay(tmp_path, monkeypatch):
    import assessment
    source, canonical, operational, target, _ = copies(tmp_path)
    # A minimal comparison helper is enough to exercise copy and subprocess routing.
    helper = tmp_path / 'helper.py'
    helper.write_text("import hashlib\nTABLE_SUFFIXES=('.csv',)\ndef _collect(root, patterns):\n return {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in patterns if (root/p).exists()}\ndef _numeric_close(*args): return False\n")
    monkeypatch.setenv('STAMPED_DELIVERY_MANIFEST', str(canonical))
    monkeypatch.setenv('STAMPED_JUDGE_TARGET', str(target))
    monkeypatch.setenv('STAMPED_WORKER_STOP_RECEIPT', str(source.parent.parent / 'worker-end-state.json'))
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    monkeypatch.setenv('GIT_CONFIG_KEY_0', 'test.keep')
    monkeypatch.setenv('GIT_CONFIG_VALUE_0', 'kept')
    # The inspection copy differs; the replay must still start from canonical bytes.
    (target / 'result.csv').write_text('inspection copy must not be replay source')
    code = ('import os,pathlib; assert os.environ["GIT_CONFIG_VALUE_0"]=="kept"; '
            'assert os.environ["GIT_CONFIG_COUNT"]=="4"; '
            'assert os.environ["GIT_CONFIG_KEY_1"]=="annex.merge-annex-branches"; '
            'assert os.environ["GIT_CONFIG_KEY_2"]=="annex.alwayscommit"; '
            'assert os.environ["GIT_CONFIG_KEY_3"]=="core.hooksPath"; '
            'pathlib.Path("result.csv").write_text("x,y\\n1,2\\n")')
    import shlex
    args = ['--path', str(target), '--entry', shlex.join([sys.executable, '-c', code]),
            '--outputs', 'result.csv', '--workdir', str(tmp_path / 'replay'),
            '--output', str(tmp_path / 'replay-result.json')]
    assert assessment.captured_replay(args, helper, operational=True) == 0
    result = json.loads((tmp_path / 'replay-result.json').read_text())
    assert result['status'] == 'met'
    assert result['source'] == str(canonical.parent / 'content/workspace')
    assert (target / 'result.csv').read_text() == 'inspection copy must not be replay source'
    delivery.validate_capture(canonical)


def test_prepare_v4_routes_judge_to_separate_operational_copy(tmp_path, allocation, contract, monkeypatch):
    import argparse
    import prepare_launch as prepare
    source, _, _, _, _ = copies(tmp_path)
    seed = {'seed_commit': 'e'*40, 'coordinator_commit': '1'*40, 'study_commit': '2'*40}
    seed_path = tmp_path / 'seed.json'
    seed_path.write_text(json.dumps(seed))
    stop = tmp_path / 'stop.json'
    stop.write_text(json.dumps({'schema_version': 2, 'kind': 'worker-end-state',
        'capture': {'sha256': agg.sha256(source.read_bytes())}, 'seed_identities': seed}))
    evidence = tmp_path / 'launch'
    evidence.mkdir()
    retained = tmp_path / 'frozen'
    (retained / 'prompts').mkdir(parents=True)
    (retained / procedure.OPERATIONAL_JUDGE).write_text('Synthetic judgment template')
    manifest = tmp_path / 'pixi.toml'
    manifest.write_text('fixture')
    manifest.with_name('pixi.lock').write_text('fixture lock')
    frozen = {'version': 4, 'study': {'rubric': 'rubric.md', 'reference': None}}
    args = argparse.Namespace(role='judge', seed_receipt=seed_path, worker_end_state=stop,
        delivery_capture=source, study=tmp_path / 'study', reference=None, env_manifest=manifest,
        judge_workspace=evidence / 'judge', resolver=tmp_path / 'resolver', codex_home=tmp_path / 'profile',
        repo=tmp_path, approved_hooks=tmp_path / 'hooks', trust_sync=tmp_path / 'trust',
        checkpoint_repo='fixture', cli=tmp_path / 'cli', seconds=0, review_seconds=0,
        model='fixture', effort='high', procedure_sha256='f'*64, capture_execution=False,
        declared_artifacts=None, prepare_only=True)
    monkeypatch.setattr(prepare, 'blob', lambda *a: b'Original synthetic task')
    monkeypatch.setattr(prepare, 'render_judge_prompt', lambda *a: evidence / 'prompt.md')
    monkeypatch.setattr(procedure, 'check_seed', lambda *a: None)
    monkeypatch.setattr(procedure, 'check_worker_sources', lambda *a: None)
    seen_retained = []
    monkeypatch.setattr(procedure, 'check_retained_target', lambda *a: seen_retained.append(a))
    monkeypatch.setattr(procedure, 'replay_instruction', lambda *a: '')
    monkeypatch.setattr(procedure, 'neutral_environment', lambda *a: {'PATH': os.defpath})
    monkeypatch.setattr(prepare.shutil, 'which', lambda *a, **kw: '/fixture/entire')
    seen_workspace = []
    def initialize(workspace, target, resolver, capture, canonical):
        identity = judge._target_identity(target, capture, canonical)
        seen_workspace.append(identity)
        return identity
    monkeypatch.setattr(prepare.judge_workspace, 'initialize', initialize)
    commands = []
    monkeypatch.setattr(prepare.subprocess, 'run', lambda command, **kw: commands.append(command))
    prepare.prepare_neutral_launch(args, 'a'*40, tmp_path, frozen, evidence, retained, tmp_path / 'launch-copies')
    assert len(commands) == 2 and seen_retained
    launch = commands[-1]
    identity = seen_workspace[0]
    assert launch[launch.index('--checkout')+1] == identity['target_path']
    assert launch[launch.index('--delivery-capture')+1] == identity['operational_capture']['uri']
    assert launch[launch.index('--canonical-capture')+1] == identity['capture']['uri']
    assert identity['schema_version'] == 3
    assert identity['capture']['sha256'] == identity['operational_capture']['sha256']
    assert identity['target_path'] != identity['canonical_target_path']
    delivery.validate_capture(source)


from test_assessment_procedure import comparison
from test_launch import fake_cli, commit


def test_synthetic_v4_seal_binds_original_bytes_and_cannot_launch_research(comparison, tmp_path):
    args, _ = comparison
    root = Path(__file__).resolve().parents[1]
    for name in procedure.NEUTRAL_FILES:
        path = args.repo / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((root / name).read_bytes())
    args.base = commit(args.repo, 'test: add synthetic neutral source boundary')
    args.protocol = 'neutral-v1'
    args.common_resources = tmp_path / 'common-resources.md'
    args.common_resources.write_text('Optional synthetic common resources')
    args.output = tmp_path / 'original-neutral-seal.json'
    procedure.seal(args)
    original_bytes = args.output.read_bytes()
    original = procedure.load_procedure(args.output, procedure.sha256(original_bytes))
    for name in set(procedure.OPERATIONAL_FILES) - set(procedure.NEUTRAL_FILES):
        path = args.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((root / name).read_bytes())
    args.base = commit(args.repo, 'test: add prospective assessment-only fixture')
    args.research_procedure = args.output
    args.research_procedure_sha256 = procedure.sha256(original_bytes)
    args.allocation = tmp_path / 'allocation.json'
    args.allocation.write_text(json.dumps({'comparison_id': args.comparison_id,
        'conditions': list(procedure.CONDITIONS), 'rounds': [{'launch_order': [{'run': 'synthetic-run'}]}]}))
    args.allocation_sha256 = procedure.sha256(args.allocation.read_bytes())
    args.retained_objects = tmp_path / 'retained.json'
    args.retained_objects.write_text(json.dumps([{'run': 'synthetic-run', 'seed_commit': 'a'*40,
        'result_commit': None, 'worker_end_state_sha256': 'b'*64, 'delivery_capture_sha256': 'c'*64}]))
    args.output = tmp_path / 'amended-neutral-seal.json'
    args.role = 'judge'
    procedure.seal(args)
    amended = procedure.load_procedure(args.output, procedure.sha256(args.output.read_bytes()))
    assert amended['version'] == 4
    assert procedure.research_procedure(amended) == original
    assert amended['assessment_amendment']['research_procedure_json'].encode() == original_bytes
    assert amended['assessment_amendment']['allocation_json'].encode() == args.allocation.read_bytes()
    assert amended['assessment'] == original['assessment']
    procedure.check_settings(amended, args)
    args.role = 'research'
    with pytest.raises(SystemExit, match='cannot authorize research'):
        procedure.check_settings(amended, args)


def structured_outputs(tmp_path, index):
    run = index['runs'][0]
    supplied = run['judgments']['primary']
    report = 'The analysis is coherent.\nThe positive hypothesis is not supported.\n'
    supplied['scientific_report'] = artifact(tmp_path, 'science.md', report)
    excerpt = {'quote': 'The analysis is coherent.', 'start_line': 1, 'end_line': 1}
    conclusion = {'quote': 'The positive hypothesis is not supported.', 'start_line': 2, 'end_line': 2}
    structured = {'schema_version': 1, 'delivery_capture_sha256': run['delivery_capture']['sha256'],
        'scientific_adequacy': 'supported', 'report': dict(supplied['scientific_report']),
        'adequacy_evidence': excerpt, 'hypothesis_conclusion': conclusion}
    supplied['structured_scientific'] = artifact(tmp_path, 'scientific-judgment.json', structured)
    supplied['adequacy'] = {'extraction_status': 'explicit', 'category': 'supported', 'excerpt': excerpt}
    supplied['conclusion'] = conclusion
    bind_outputs(tmp_path, supplied)
    rewrite(tmp_path, supplied['output_binding'], lambda v: v['outputs'].update(
        structured_scientific=supplied['structured_scientific']))
    return supplied


def aggregate_operational(tmp_path, allocation, contract, index, original):
    return agg.aggregate(allocation,index,tmp_path,contract,original,
        index['comparison_provenance']['assessment_seal']['sha256'])


def test_structured_category_uses_explicit_field_with_independent_conclusion(tmp_path, allocation, contract):
    index, original, _ = operational_bundle(tmp_path, allocation, contract)
    structured_outputs(tmp_path, index)
    tables = aggregate_operational(tmp_path, allocation, contract, index, original)
    assert not tables['issues']
    observed = next(j for j in tables['judgments'] if j['response_status'] == 'valid')
    assert observed['adequacy'] == 'supported'
    assert observed['conclusion'] == 'The positive hypothesis is not supported.'
    assert len(tables['items']) == 31


@pytest.mark.parametrize('failure', ['missing', 'schema', 'capture', 'report', 'quote', 'category', 'conclusion'])
def test_structured_failure_only_removes_scientific_measures(tmp_path, allocation, contract, failure):
    index, original, _ = operational_bundle(tmp_path, allocation, contract)
    supplied = structured_outputs(tmp_path, index)
    if failure == 'missing':
        supplied.pop('structured_scientific')
    else:
        def change(v):
            if failure == 'schema': v['scientific_adequacy'] = 'invented label'
            if failure == 'capture': v['delivery_capture_sha256'] = '0'*64
            if failure == 'report': v['report']['sha256'] = '0'*64
            if failure == 'quote': v['adequacy_evidence']['quote'] = 'Absent literal text'
            if failure == 'category': v['scientific_adequacy'] = 'qualified'
            if failure == 'conclusion': v['hypothesis_conclusion'] = None
        rewrite(tmp_path, supplied['structured_scientific'], change)
        rewrite(tmp_path, supplied['output_binding'], lambda v: v['outputs'].update(
            structured_scientific=supplied['structured_scientific']))
    tables = aggregate_operational(tmp_path, allocation, contract, index, original)
    observed = next(j for j in tables['judgments'] if j['response_status'] == 'valid')
    assert observed['inclusion_status'] == 'eligible'
    assert observed['adequacy'] is None and observed['conclusion'] is None
    assert observed['extraction_status'] == 'invalid'
    assert len(tables['items']) == 31
    assert tables['issues'] and all(i['area'] in ('adequacy', 'conclusion') for i in tables['issues'])


@pytest.mark.parametrize('failure', ['target', 'binding'])
def test_v4_substantive_or_attribution_failure_still_invalidates_globally(tmp_path, allocation, contract, failure):
    index, original, _ = operational_bundle(tmp_path, allocation, contract,
                                          'result.csv' if failure == 'target' else 'database')
    supplied = structured_outputs(tmp_path, index)
    if failure == 'binding':
        rewrite(tmp_path, supplied['output_binding'], lambda v: v.update(native_result_sha256='0'*64))
    tables = aggregate_operational(tmp_path, allocation, contract, index, original)
    assert tables['items'] == []
    assert all(j['adequacy'] is None for j in tables['judgments'])
    assert tables['issues']


def test_retained_structure_and_report_can_be_relocated_annex_links(tmp_path, allocation, contract):
    index, original, _ = operational_bundle(tmp_path, allocation, contract)
    supplied = structured_outputs(tmp_path, index)
    for key in ('structured_scientific', 'scientific_report'):
        source = tmp_path / supplied[key]['path']
        relocated = tmp_path / ('retained-' + source.name)
        source.rename(relocated)
        pointer = tmp_path / ('annex-' + source.name)
        pointer.symlink_to(relocated.name)
        supplied[key]['path'] = pointer.name
    tables = aggregate_operational(tmp_path, allocation, contract, index, original)
    assert not tables['issues']
    assert any(j['adequacy'] == 'supported' for j in tables['judgments'])


def test_only_regular_sqlite_sidecar_additions_are_permitted(tmp_path):
    root = tmp_path / 'worker'
    (root / '.git/annex/keysdb').mkdir(parents=True)
    (root / '.git/annex/keysdb/db').write_bytes(b'original')
    receipt = delivery.save_delivery(root, tmp_path / 'capture', {})
    source = Path(receipt['capture']['uri'])
    canonical = delivery.materialize_capture(source, tmp_path / 'canonical')
    operational = delivery.materialize_capture(source, tmp_path / 'operational')
    target = Path(operational['target'])
    identity = judge._target_identity(target, operational['manifest'], canonical['manifest'])
    for name in ('db-shm', 'db-wal'):
        (target / '.git/annex/keysdb' / name).write_bytes(b'new operational metadata')
    result = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    assert result['protected_unchanged'] and result['operational_metadata_changed']
    assert len(result['permitted_metadata_changes']) == 2
    assert all(row['change'] == 'added' for row in result['permitted_metadata_changes'])


def test_incomplete_final_capture_never_passes(tmp_path):
    _, _, _, target, identity = copies(tmp_path)
    (target / '.netrc').write_text('synthetic credential-exclusion fixture; no real credential')
    result = judge.retain_operational_target(target, identity, tmp_path / 'retained')
    assert result['capture_status'] == 'partial' and result['omissions']
    assert not result['protected_unchanged'] and not result['target_unchanged']


def test_original_v3_receipt_still_requires_exact_unchanged_target(tmp_path, allocation, contract):
    index, original = bundle(tmp_path, allocation, contract)
    supplied = index['runs'][0]['judgments']['primary']
    rewrite(tmp_path, supplied['native']['result'], lambda v: v.update(target_unchanged=False))
    bind_outputs(tmp_path, supplied)
    tables = aggregate_operational(tmp_path, allocation, contract, index, original)
    assert tables['items'] == [] and tables['issues']
