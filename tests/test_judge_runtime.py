"""Exercise the role projection without launching native agents or changing seals."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import assessment
import assessment_procedure as procedure
import delivery_snapshot
import launch_native_probe as launch
from test_assessment_runner import frozen_runner


@pytest.fixture
def projected_judge(tmp_path, monkeypatch, frozen_runner, request):
    calls, source, runtime = frozen_runner
    worker = tmp_path / 'worker'
    worker.mkdir()
    (worker / 'result.csv').write_text('x\n1\n')
    (worker / 'run.py').write_text("from pathlib import Path\nPath('result.csv').write_text('x\\n1\\n')\n")
    if getattr(request, 'param', None) == 'git-object':
        for arguments in (['init', '-b', 'main'], ['add', '.'],
                ['-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Projection fixture',
                 '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'test: synthetic probe delivery']):
            process = subprocess.Popen(['git', '-C', str(worker), *arguments],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=30)
            assert process.returncode == 0, (stdout, stderr)
    receipt = delivery_snapshot.save_delivery(worker, tmp_path / 'canonical', {})
    canonical = Path(receipt['capture']['uri'])
    stop = tmp_path / 'worker-stop.json'
    stop.write_text(json.dumps({'capture': receipt['capture']}))
    output, profile, target = (tmp_path / name for name in ('judgment', 'profile', 'operational'))
    for path in (output, profile, target):
        path.mkdir()
    if getattr(request, 'param', None) == 'git-object':
        shutil.copytree(worker, target, dirs_exist_ok=True)
    for name in ('assess-alignment-with-stamped-principles', 'stamped-conventions'):
        skill = source / 'skills' / name
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nversion: 0.1.0\n---\n')
    pin_path = Path(os.environ['STAMPED_ASSESSMENT_PIN'])
    frozen = {'version': 4, 'protocol': procedure.NEUTRAL_PROTOCOL,
              'assessment': json.loads(pin_path.read_text()),
              'settings': {'judge': {'model': 'fixture-model'}},
              'fixed_files': {'scripts/assessment.py': procedure.sha256(Path(assessment.__file__).read_bytes()),
                              'coordinator-only': 'UNRELATED_FIXED_FILE_SENTINEL'},
              'replay': copy.deepcopy(procedure.NEUTRAL_REPLAY),
              'conditions': ['ALLOCATION_CONDITION_SENTINEL'],
              'assessment_amendment': {'allocation_json': 'ALLOCATION_SENTINEL',
                                       'research_procedure_json': 'RESEARCH_SEAL_SENTINEL'},
              'retained_runs': [{'run': 'OTHER_OBJECT_SENTINEL'}]}
    args = SimpleNamespace(protocol=procedure.NEUTRAL_PROTOCOL, checkout=target,
        assessment_source=source, assessment_pin=pin_path, canonical_capture=canonical,
        delivery_capture=canonical, worker_end_state=stop)
    inherited = dict(os.environ, STAMPED_PROCEDURE='/COORDINATOR_SEAL_SENTINEL/procedure.json',
        STAMPED_PROCEDURE_SHA256='FULL_SEAL_DIGEST_SENTINEL',
        STAMPED_OTHER_JUDGE='/OTHER_JUDGMENT_SENTINEL/report.md')
    environment = launch.judge_environment(inherited, args, output, profile,
                                            {'target_commit': json.loads(canonical.read_bytes())['head_commit']}, frozen)
    for key, value in environment.items():
        if key.startswith('STAMPED_'):
            monkeypatch.setenv(key, value)
    monkeypatch.delenv('STAMPED_PROCEDURE', raising=False)
    monkeypatch.delenv('STAMPED_PROCEDURE_SHA256', raising=False)
    return frozen, environment, calls, source, output, runtime


def test_projection_and_advertised_paths_exclude_coordinator_records(projected_judge):
    frozen, environment, *_ = projected_judge
    path = Path(environment['STAMPED_JUDGE_RUNTIME'])
    runtime = procedure.load_judge_runtime(path, environment['STAMPED_JUDGE_RUNTIME_SHA256'], environment)
    advertised = {key: value for key, value in environment.items() if key.startswith('STAMPED_')}
    text = json.dumps(advertised) + path.read_text() + Path(environment['STAMPED_ASSESSMENT_PIN']).read_text()
    assert 'SENTINEL' not in text
    assert set(advertised) == procedure.JUDGE_BINDINGS | {'STAMPED_JUDGE_RUNTIME', 'STAMPED_JUDGE_RUNTIME_SHA256'}
    assert runtime['bindings']['STAMPED_JUDGE_OUTPUT'] == environment['STAMPED_JUDGE_OUTPUT']
    assert runtime['assessment'] == frozen['assessment']
    assert frozen['assessment_amendment']['allocation_json'] == 'ALLOCATION_SENTINEL'
    assert 'STAMPED_PROCEDURE' not in advertised


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(allocation='SENTINEL'),
    lambda r: r['assessment'].update(allocation='SENTINEL'),
    lambda r: r['assessment']['sha256'].update(other='SENTINEL'),
    lambda r: r['fixed_files'].update(other='SENTINEL'),
    lambda r: r['replay'].update(other='SENTINEL'),
    lambda r: r['bindings'].update(STAMPED_PROCEDURE='/SENTINEL'),
])
def test_runtime_rejects_extra_fields_even_with_matching_digest(projected_judge, mutation):
    _, environment, *_ = projected_judge
    path = Path(environment['STAMPED_JUDGE_RUNTIME'])
    runtime = json.loads(path.read_bytes())
    mutation(runtime)
    path.write_text(json.dumps(runtime))
    with pytest.raises(SystemExit):
        procedure.load_judge_runtime(path, procedure.sha256(path.read_bytes()), environment)


@pytest.mark.parametrize('mutation', ['digest', 'target', 'receipt', 'runner'])
def test_runtime_rejects_drift_before_helper_dispatch(projected_judge, monkeypatch, mutation):
    _, environment, calls, *_ = projected_judge
    path = Path(environment['STAMPED_JUDGE_RUNTIME'])
    if mutation == 'digest':
        path.write_bytes(path.read_bytes() + b' ')
    elif mutation == 'target':
        monkeypatch.setenv('STAMPED_JUDGE_TARGET', '/other-object')
    elif mutation == 'receipt':
        Path(environment['STAMPED_WORKER_STOP_RECEIPT']).write_text('{}')
    else:
        runtime = json.loads(path.read_text())
        runtime['fixed_files']['scripts/assessment.py'] = '0' * 64
        path.write_text(json.dumps(runtime))
        monkeypatch.setenv('STAMPED_JUDGE_RUNTIME_SHA256', procedure.sha256(path.read_bytes()))
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'check'])
    with pytest.raises(SystemExit):
        assessment.main()
    assert calls == []


def test_full_seal_is_not_a_runtime_fallback(projected_judge, monkeypatch):
    monkeypatch.setenv('STAMPED_PROCEDURE', '/coordinator/full-procedure.json')
    with pytest.raises(SystemExit, match='Full coordinator'):
        assessment.runtime_context()


def test_projected_check_and_response_dispatch(projected_judge, monkeypatch):
    _, _, calls, source, output, runtime = projected_judge
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'check'])
    assessment.main()
    assert (runtime / 'pixi.lock').read_text() == 'fixture lock\n'
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'response', 'template', '-o', 'response.json'])
    with pytest.raises(SystemExit) as status:
        assessment.main()
    assert status.value.code == 7
    command, kwargs = calls[-1]
    assert command[6] == source / 'skills/stamped-conventions/scripts/encode_response.py'
    assert kwargs == {'cwd': output}


def test_projected_captured_replay_executes_and_preserves_one_attempt(projected_judge, monkeypatch):
    _, environment, calls, source, output, _ = projected_judge
    actual = Path(assessment.__file__).resolve().parents[1] / 'assessment/skills/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py'
    helper = source / 'skills/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py'
    helper.parent.mkdir(parents=True)
    shutil.copyfile(actual, helper)
    arguments = ['--path', environment['STAMPED_JUDGE_TARGET'], '--entry', f'{sys.executable} run.py',
                 '--outputs', 'result.csv', '--workdir', 'replay', '--output', 'replay.json']
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'fresh-rerun', *arguments])
    with pytest.raises(SystemExit) as status:
        assessment.main()
    assert status.value.code == 7
    command, kwargs = calls[-1]
    process = subprocess.Popen([sys.executable, *map(str, command[6:])], env=environment,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, stderr = process.communicate(timeout=30)
    assert process.returncode == 0, (stdout, stderr)
    assert json.loads((output / 'replay.json').read_text())['status'] == 'met'
    assert (output / 'formal-replay-attempt.json').is_file()
    with pytest.raises(SystemExit, match='already consumed'):
        assessment.main()


@pytest.mark.parametrize('collision', ['directory', 'file', 'dangling-link', 'output', 'overlap'])
def test_replay_path_preflight_preserves_evidence_and_attempt(projected_judge, monkeypatch, collision):
    _, environment, _, _, output, _ = projected_judge
    workdir, report = output / 'replay', output / 'replay.json'
    if collision == 'directory':
        workdir.mkdir()
        (workdir / 'kept').write_text('unchanged')
    elif collision == 'file':
        workdir.write_text('unchanged')
    elif collision == 'dangling-link':
        workdir.symlink_to(output / 'missing')
    elif collision == 'output':
        report.write_text('unchanged')
    else:
        report = workdir / 'report.json'
    runtime = assessment.runtime_context()
    arguments = ['--path', environment['STAMPED_JUDGE_TARGET'], '--entry', 'never executed',
                 '--outputs', 'result.csv', '--workdir', str(workdir), '--output', str(report)]
    with pytest.raises(SystemExit, match='new separate paths'):
        procedure.replay_arguments(runtime, arguments, Path(environment['STAMPED_JUDGE_TARGET']), output)
    assert not (output / 'formal-replay-attempt.json').exists()
    records = list(output.glob('formal-replay-preflight-*.json'))
    assert len(records) == 1
    assert json.loads(records[0].read_text())['status'] == 'rejected-before-attempt'
    if collision == 'directory':
        assert (workdir / 'kept').read_text() == 'unchanged'
    elif collision == 'file':
        assert workdir.read_text() == 'unchanged'
    elif collision == 'dangling-link':
        assert workdir.is_symlink()
    elif collision == 'output':
        assert report.read_text() == 'unchanged'
    arguments[-3], arguments[-1] = str(output / 'fresh-replay'), str(output / 'fresh-report.json')
    assert procedure.replay_arguments(runtime, arguments, Path(environment['STAMPED_JUDGE_TARGET']), output) == arguments
    with pytest.raises(SystemExit, match='already consumed'):
        procedure.replay_arguments(runtime, arguments, Path(environment['STAMPED_JUDGE_TARGET']), output)


@pytest.mark.parametrize('field,value', [
    ('capture', None), ('capture', {'uri': '/other-object', 'sha256': '0' * 64}),
    ('commit', 'a' * 40), ('captured_at', '2000-01-01T00:00:00Z'),
])
def test_formal_response_requires_exact_capture_and_head(projected_judge, monkeypatch, field, value):
    _, _, calls, _, output, _ = projected_judge
    response = copy.deepcopy(assessment.runtime_context()['response_identity'])
    response['responses'] = {'sentinel': {'status': 'unmet', 'reason': 'untouched'}}
    if value is None:
        del response['object'][field]
    else:
        response['object'][field] = value
    path = output / 'response.json'
    path.write_text(json.dumps(response))
    before = path.read_bytes()
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'validate', 'response.json'])
    with pytest.raises(SystemExit, match='response'):
        assessment.main()
    assert calls == []
    assert path.read_bytes() == before


@pytest.mark.parametrize('field', ['skill', 'version', 'harness', 'model', 'date', 'dependencies'])
def test_formal_response_requires_projected_assessor_metadata(projected_judge, field):
    runtime = assessment.runtime_context()
    response = copy.deepcopy(runtime['response_identity'])
    response['assessor'].pop(field)
    with pytest.raises(SystemExit, match='missing assessor'):
        assessment.validate_response_identity(response, runtime)


def test_metadata_template_keeps_frozen_verdicts_and_validates_identity(projected_judge, monkeypatch):
    import importlib.util
    _, environment, calls, source, output, _ = projected_judge
    skill = Path(assessment.__file__).resolve().parents[1] / 'assessment/skills/stamped-conventions'
    module_path = skill / 'scripts/encode_response.py'
    spec = importlib.util.spec_from_file_location('actual_frozen_response', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    blank = module.template(module.Checklist())
    original_run = assessment.subprocess.run
    def run(command, **kwargs):
        if command[:2] == ['pixi', 'run'] and command[-1] == 'template':
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(blank), stderr='')
        return original_run(command, **kwargs)
    monkeypatch.setattr(assessment.subprocess, 'run', run)
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'template', '-o', 'response.json'])
    with pytest.raises(SystemExit) as status:
        assessment.main()
    assert status.value.code == 0
    response = json.loads((output / 'response.json').read_text())
    assert response['responses'] == blank['responses']
    assert response['scope'] is None
    runtime = assessment.runtime_context()
    assessment.validate_response_identity(response, runtime)
    assert response['object'] == dict(blank['object'], **runtime['response_identity']['object'])
    assert response['assessor']['version'] == '0.1.0'
    assert response['assessor']['dependencies'][1].endswith(runtime['assessment']['source_commit'])
    for action in (['validate'], ['response', 'validate']):
        monkeypatch.setattr(sys, 'argv', ['assessment.py', *action, 'response.json'])
        with pytest.raises(SystemExit) as status:
            assessment.main()
        assert status.value.code == 7  # Generic frozen validator still runs.
    monkeypatch.setattr(sys, 'argv', ['assessment.py', 'template', '-o', 'response.json'])
    before = (output / 'response.json').read_bytes()
    with pytest.raises(SystemExit, match='new file'):
        assessment.main()
    assert (output / 'response.json').read_bytes() == before


@pytest.mark.parametrize('kind', ['dangling-link', 'outside'])
def test_metadata_template_rejects_unsafe_destination_before_helper(projected_judge, kind):
    _, _, calls, _, output, _ = projected_judge
    target = output / 'response.json'
    if kind == 'dangling-link':
        target.symlink_to(output / 'missing.json')
    else:
        target = output.parent / 'outside.json'
    with pytest.raises(SystemExit, match='new file'):
        assessment.response_template(['-o', str(target)], assessment.runtime_context(), [], output)
    assert calls == []
    assert not target.exists()


@pytest.mark.parametrize('projected_judge', ['git-object'], indirect=True)
def test_actual_frozen_probe_draft_stays_separate_from_formal_response(projected_judge):
    _, environment, _, _, output, _ = projected_judge
    root = Path(assessment.__file__).resolve().parents[1] / 'assessment/skills'
    encoder = root / 'stamped-conventions/scripts/encode_response.py'
    probes = root / 'assess-alignment-with-stamped-principles/scripts/run_probes.py'
    def execute(script, arguments):
        process = subprocess.Popen([sys.executable, str(script), *arguments], cwd=output,
            env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=30)
        assert process.returncode == 0, (stdout, stderr)
        return stdout
    response = json.loads(execute(encoder, ['template']))
    runtime = assessment.runtime_context()
    for section, fields in runtime['response_identity'].items():
        response[section].update(fields)
    response['scope'] = 'Synthetic helper composition test; all items remain not checked.'
    path = output / 'response.json'
    path.write_text(json.dumps(response))
    before = path.read_bytes()
    # Reproduce the observed composition defect using the unchanged frozen CLI.
    collision = output / 'overwritten-response.json'
    collision.write_bytes(before)
    common = [environment['STAMPED_JUDGE_TARGET'], '--kind', 'study', '--only', 'tree-clean']
    execute(probes, [*common, '-o', 'collision-probes.json', '--response', str(collision)])
    changed = json.loads(collision.read_bytes())
    assert 'capture' not in changed['object']
    with pytest.raises(SystemExit, match='missing object.capture'):
        assessment.validate_response_identity(changed, runtime)
    # The future prompt's separate-draft route preserves the formal response.
    execute(probes, [*common, '-o', 'probes.json', '--response', 'probe-draft.json'])
    assert (output / 'probe-draft.json').is_file()
    assert path.read_bytes() == before
    assessment.validate_response_identity(json.loads(path.read_bytes()), runtime)
    assert json.loads(path.read_bytes())['responses'] == response['responses']
    execute(encoder, ['validate', str(path)])
