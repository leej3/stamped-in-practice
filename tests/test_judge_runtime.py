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
def projected_judge(tmp_path, monkeypatch, frozen_runner):
    calls, source, runtime = frozen_runner
    worker = tmp_path / 'worker'
    worker.mkdir()
    (worker / 'result.csv').write_text('x\n1\n')
    (worker / 'run.py').write_text("from pathlib import Path\nPath('result.csv').write_text('x\\n1\\n')\n")
    receipt = delivery_snapshot.save_delivery(worker, tmp_path / 'canonical', {})
    canonical = Path(receipt['capture']['uri'])
    stop = tmp_path / 'worker-stop.json'
    stop.write_text(json.dumps({'capture': receipt['capture']}))
    output, profile, target = (tmp_path / name for name in ('judgment', 'profile', 'operational'))
    for path in (output, profile, target):
        path.mkdir()
    pin_path = Path(os.environ['STAMPED_ASSESSMENT_PIN'])
    frozen = {'version': 4, 'protocol': procedure.NEUTRAL_PROTOCOL,
              'assessment': json.loads(pin_path.read_text()),
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
                                            {'target_commit': None}, frozen)
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
