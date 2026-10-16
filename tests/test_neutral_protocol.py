"""Neutral seeds retain readable inputs without delivering coordinator instructions."""
import json
import os
from pathlib import Path
import sys
import subprocess

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import study_seed as seed
import assessment_procedure as procedure
from test_launch import source_repositories, fake_cli, git, commit, ROOT


@pytest.mark.parametrize("condition", ["baseline", "stamped-explicit"])
def test_neutral_seed_annexes_inputs_only_and_keeps_metadata_external(source_repositories, tmp_path, condition):
    repo, study, _, resolver, key, forbidden, skills = source_repositories
    (repo / "prompts").mkdir()
    (repo / seed.NEUTRAL_COMMON).write_bytes((ROOT / seed.NEUTRAL_COMMON).read_bytes())
    base = commit(repo, "test: add neutral common instructions")
    resources = tmp_path / "common.md"
    resources.write_text("Optional shared interpreter: /external/python\n")
    worker = tmp_path / "worker"
    receipt = tmp_path / "evidence/input.json"
    result = seed.make_neutral_seed(repo, base, study, worker, "codex/run-001", condition,
                                    resolver, receipt, resources, skills)
    assert not (worker / "worker-input.json").exists()
    assert not (worker / "pixi.toml").exists()
    assert not (worker / ".gitattributes").exists()
    assert not (worker / ".agents").exists()
    assert (worker / "input/data/annexed.bin").is_symlink()
    assert (worker / "input/data/annexed.bin").read_bytes() == (study / "input/data/annexed.bin").read_bytes()
    assert git(worker, "annex", "lookupkey", "input/data/annexed.bin") == key
    assert git(worker, "ls-tree", "HEAD", "input/data/annexed.bin").startswith("120000 blob")
    assert git(worker, "rev-list", "--parents", "HEAD").split() == [result["seed_commit"]]
    assert seed.audit_neutral_seed(worker, receipt) == result
    prompt = seed.neutral_research_prompt(worker, receipt).decode()
    assert "Optional shared interpreter: /external/python" in prompt
    assert "$COMMON_RESOURCES" not in prompt
    assert prompt.startswith((study / "input/study-task.md").read_text())
    if condition == "stamped-explicit":
        snapshot = Path(result["skills_directory"])
        assert (snapshot / "assess-alignment-with-stamped-principles/SKILL.md").is_file()
        assert not (snapshot / ".git").exists()
        assert not (snapshot / "evals").exists()
    for oid in forbidden:
        assert subprocess.run(["git", "-C", str(worker), "cat-file", "-t", oid],
                              capture_output=True).returncode != 0
    (worker / "unapproved.txt").write_text("unexpected")
    with pytest.raises(SystemExit, match="boundary"):
        seed.audit_neutral_seed(worker, receipt)


def test_common_environment_excludes_coordinator_path_and_limits_threads(tmp_path):
    manifest = tmp_path / "pixi.toml"
    binary = tmp_path / ".pixi/envs/default/bin"
    binary.mkdir(parents=True)
    (binary / "python").touch()
    environment = procedure.neutral_environment(manifest, {"PATH": "/coordinator/private/bin", "KEEP": "yes"}, "judge")
    assert environment["PATH"].split(os.pathsep) == [str(binary), *os.defpath.split(os.pathsep)]
    assert environment["KEEP"] == "yes"
    assert environment["GIT_OPTIONAL_LOCKS"] == "0"
    assert environment["PYTHONDONTWRITEBYTECODE"] == "1"
    assert all(environment[name] == "1" for name in procedure.NEUTRAL_THREAD_ENV)


def test_neutral_native_flow_retains_profile_skills_and_outer_wrapper(source_repositories, fake_cli, tmp_path):
    repo, study, _, resolver, _, _, skills = source_repositories
    (repo / "prompts").mkdir()
    (repo / seed.NEUTRAL_COMMON).write_bytes((ROOT / seed.NEUTRAL_COMMON).read_bytes())
    base = commit(repo, "test: add neutral task")
    resource = tmp_path / "common.md"
    resource.write_text("Optional scientific tools are provided externally.\n")
    worker, receipt = tmp_path / "worker", tmp_path / "preparation/input.json"
    seed.make_neutral_seed(repo, base, study, worker, "codex/run-002", "stamped-explicit",
                           resolver, receipt, resource, skills)
    prompt = tmp_path / "prompt.md"
    prompt.write_bytes(seed.neutral_research_prompt(worker, receipt))
    manifest = tmp_path / "common/pixi.toml"
    manifest.parent.mkdir()
    manifest.write_text("# fixture\n")
    binary = manifest.parent / ".pixi/envs/default/bin"
    binary.mkdir(parents=True)
    (binary / "python").symlink_to(sys.executable)
    duct = tmp_path / "fake-duct"
    duct.write_text(f"#!{sys.executable}\n" + '''
import os, sys
if '--version' in sys.argv:
    print('fixture-duct 1')
else:
    assert os.getsid(0) == os.getpid()
    assert sys.argv[1:3] == ['--mode', 'current-session']
    args = sys.argv[1:]
    # Eight option/value pairs precede the native executable.
    command = args[16:]
    assert os.environ['OMP_NUM_THREADS'] == '1'
    os.execv(command[0], command)
''')
    duct.chmod(0o755)
    cli, profile = fake_cli
    output = tmp_path / "native-evidence"
    result = subprocess.run([sys.executable, str(ROOT / "scripts/launch_native_probe.py"),
        "--checkout", str(worker), "--prompt", str(prompt), "--output", str(output),
        "--cli", str(cli), "--role", "research", "--review-seconds", "0", "--protocol", "neutral-v1",
        "--seed-receipt", str(receipt), "--env-manifest", str(manifest),
        "--capture-execution", "--duct-executable", str(duct)],
        env=dict(os.environ, CODEX_HOME=str(profile)), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    record = json.loads((output / "result.json").read_text())
    assert record["outer_capture"]["version"] == "fixture-duct 1"
    assert record["thread_environment"] == procedure.NEUTRAL_THREAD_ENV
    assert record["resource_path"].split(os.pathsep)[0] == str(binary)
    capture = json.loads(Path(record["worker_end_state"]["capture"]["uri"]).read_bytes())
    assert capture["declared_artifacts"][0]["declaration"]["kind"] == "native-session-skill-directory"
    assert capture["capture_status"] == "complete"
    assert not (worker / "worker-input.json").exists()
