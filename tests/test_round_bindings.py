"""Synthetic Git objects and receipts; no study execution or admission changes."""
import copy
import json
import os
from pathlib import Path
import subprocess

import pytest

from test_neutral_aggregation import allocation, bundle, collect, contract
from test_aggregate_comparison import agg, artifact, bind_outputs, rewrite
from assessment_procedure import gitmodules_digest


class Sources:
    def __init__(self, root):
        self.root = root
        root.mkdir()
        self.git("init", "-q")
        self.write("prompts/neutral-worker-common.md", "Synthetic fixed worker prompt\n")
        self.modules = ('[submodule "skills"]\n path = skills\n url = https://example.test/skills.git\n'
                        ' branch = round-one\n[submodule "assessment"]\n path = assessment\n'
                        ' url = https://example.test/assessor.git\n branch = frozen\n')
        self.write(".gitmodules", self.modules)
        self.skill = "b" * 40
        self.git("add", ".")
        self.git("update-index", "--add", "--cacheinfo", "160000," + "a" * 40 + ",skills")
        self.original = self.commit()
        self.write(".gitmodules", self.modules.replace("round-one", "round-two"))
        self.git("add", ".gitmodules")
        self.git("update-index", "--add", "--cacheinfo", "160000," + self.skill + ",skills")
        self.current = self.commit()

    def git(self, *args):
        env = dict(os.environ, GIT_AUTHOR_NAME="Synthetic test", GIT_COMMITTER_NAME="Synthetic test",
                   GIT_AUTHOR_EMAIL="fixture@example.test", GIT_COMMITTER_EMAIL="fixture@example.test")
        return subprocess.check_output(["git", "-C", str(self.root), *args], env=env).decode().strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self):
        return self.git("commit-tree", self.git("write-tree"), "-m", "Synthetic source fixture")


def bound_bundle(tmp_path, allocation, contract, *, round_id=2, explicit=False):
    allocation = copy.deepcopy(allocation)
    allocation["rounds"].sort(key=lambda r: r["round"] != round_id)
    group = allocation["rounds"][0]
    if explicit:
        group["launch_order"].sort(key=lambda r: r["condition"] != "stamped-explicit")
    index, original = bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    judgment = run["judgments"]["primary"]
    sources = Sources(tmp_path / "source-repository")
    procedure = json.loads(original)
    prompt = (sources.root / "prompts/neutral-worker-common.md").read_bytes()
    procedure.update(coordinator_commit=sources.original,
        gitmodules_sha256=gitmodules_digest(sources.modules.encode()),
        fixed_files={"prompts/neutral-worker-common.md": agg.sha256(prompt)})
    seal = artifact(tmp_path, "procedure.json", procedure)
    original = (tmp_path / "procedure.json").read_bytes()
    index["comparison_provenance"] = {"assessment_seal": seal,
                                      "research_procedure_sha256": seal["sha256"]}
    rewrite(tmp_path, run["worker_input"], lambda v: v.update(
        coordinator_commit=sources.current, common_prompt_sha256=agg.sha256(prompt),
        skills_commit=sources.skill if explicit else None))
    rewrite(tmp_path, run["worker_end_state"], lambda v: v["seed_identities"].update(
        common_prompt_sha256=agg.sha256(prompt)))
    rewrite(tmp_path, run["worker_native"]["procedure_status"],
            lambda v: v.update(procedure_sha256=seal["sha256"]))
    status = json.loads(agg.artifact(run["worker_native"]["procedure_status"], tmp_path))
    rewrite(tmp_path, run["worker_native"]["result"], lambda v: (
        v.update(procedure=status), v["worker_end_state"].update(sha256=run["worker_end_state"]["sha256"])))
    rewrite(tmp_path, judgment["native"]["procedure_status"], lambda v: v.update(
        procedure_sha256=seal["sha256"], worker_end_state_sha256=run["worker_end_state"]["sha256"]))
    judge_status = json.loads(agg.artifact(judgment["native"]["procedure_status"], tmp_path))
    rewrite(tmp_path, judgment["native"]["result"], lambda v: v.update(procedure=judge_status))
    bind_outputs(tmp_path, judgment)
    allocation_hash = agg.sha256(json.dumps(allocation).encode())
    receipt = {"round": round_id, "comparison_id": allocation["comparison_id"],
        "original_allocation_sha256": allocation_hash, "research_procedure_sha256": seal["sha256"],
        "coordinator_source_commit": sources.current, "research_guidance_commit": sources.skill,
        "study_input_tree": procedure["study"]["input_tree"],
        "worker_assignments": group["launch_order"], "assigned_judgments": group["judgment_dispatch_order"],
        "research_guidance_repository": "https://example.test/skills.git",
        "research_guidance_branch": "round-two"}
    config = {"schema_version": 1, "comparison_id": allocation["comparison_id"],
        "allocation_sha256": allocation_hash, "research_procedure_sha256": seal["sha256"],
        "rounds": [{"round": round_id, "coordinator_source_commit": sources.current,
            "research_guidance_commit": sources.skill,
            "source_skill_binding": artifact(tmp_path, "source-skill-binding.json", receipt),
            "authorization": [artifact(tmp_path, "authorization.md", "Synthetic authorization\n")]}]}
    return allocation, index, original, config, sources


def corrected(tmp_path, contract, fixture):
    allocation, index, original, config, sources = fixture
    return collect(tmp_path, allocation, contract, index, original,
        round_binding_config=config, round_binding_base=tmp_path,
        allocation_sha256=config["allocation_sha256"], source_repository=sources.root)


@pytest.mark.parametrize("round_id", [2, 3])
@pytest.mark.parametrize("explicit", [False, True])
def test_explicit_round_binding_preserves_default_and_raw_receipts(tmp_path, allocation, contract, round_id, explicit):
    fixture = bound_bundle(tmp_path, allocation, contract, round_id=round_id, explicit=explicit)
    a, index, original, _, _ = fixture
    before = {p: p.read_bytes() for p in tmp_path.glob("*.json")}
    rejected = collect(tmp_path, a, contract, index, original)
    assert not rejected["items"] and "coordinator_commit" in rejected["issues"][0]["message"]
    accepted = corrected(tmp_path, contract, fixture)
    assert not accepted["issues"] and len(accepted["items"]) == 31
    assert len(accepted["judgments"]) == 96
    assert before == {p: p.read_bytes() for p in before}


@pytest.mark.parametrize("failure", ["authorization", "receipt-source", "receipt-round", "receipt-skill",
    "receipt-allocation", "receipt-input", "receipt-workers", "receipt-judges", "duplicate-round",
    "unknown-round", "receipt-hash", "config-allocation", "config-procedure", "source-skill"])
def test_forged_or_unbound_round_configuration_rejected(tmp_path, allocation, contract, failure):
    fixture = bound_bundle(tmp_path, allocation, contract)
    _, _, _, config, _ = fixture
    row = config["rounds"][0]
    if failure == "authorization":
        (tmp_path / "authorization.md").write_text("Changed authorization")
    elif failure == "receipt-hash":
        row["source_skill_binding"]["sha256"] = "0" * 64
    elif failure.startswith("receipt-"):
        key, value = {"source": ("coordinator_source_commit", "0" * 40),
            "round": ("round", 1), "skill": ("research_guidance_commit", "0" * 40),
            "allocation": ("original_allocation_sha256", "0" * 64),
            "input": ("study_input_tree", "0" * 40),
            "workers": ("worker_assignments", []), "judges": ("assigned_judgments", [])}[failure[8:]]
        rewrite(tmp_path, row["source_skill_binding"], lambda v: v.update({key: value}))
    elif failure == "duplicate-round":
        config["rounds"].append(copy.deepcopy(row))
    elif failure == "unknown-round":
        row["round"] = 99
    elif failure == "config-allocation":
        config["allocation_sha256"] = "0" * 64
    elif failure == "config-procedure":
        config["research_procedure_sha256"] = "0" * 64
    else:
        row["research_guidance_commit"] = "0" * 40
        rewrite(tmp_path, row["source_skill_binding"], lambda v: v.update(research_guidance_commit="0" * 40))
    with pytest.raises(ValueError):
        corrected(tmp_path, contract, fixture)


@pytest.mark.parametrize("change", ["code", "fixed-prompt", "assessor-link", "skills-url", "assessor-branch"])
def test_round_binding_never_authorizes_other_source_changes(tmp_path, allocation, contract, change):
    fixture = bound_bundle(tmp_path, allocation, contract)
    _, _, _, config, sources = fixture
    if change == "code":
        sources.write("new-runtime.py", "raise RuntimeError('changed')\n")
    elif change == "fixed-prompt":
        sources.write("prompts/neutral-worker-common.md", "Changed fixed prompt\n")
    elif change == "assessor-link":
        sources.git("update-index", "--add", "--cacheinfo", "160000," + "c" * 40 + ",assessment")
    else:
        text = (sources.root / ".gitmodules").read_text()
        sources.write(".gitmodules", text.replace(
            "https://example.test/skills.git" if change == "skills-url" else "branch = frozen",
            "https://other.test/skills.git" if change == "skills-url" else "branch = changed"))
    for path in ("new-runtime.py", "prompts/neutral-worker-common.md", ".gitmodules"):
        if (sources.root / path).exists():
            sources.git("add", path)
    changed = sources.commit()
    config["rounds"][0]["coordinator_source_commit"] = changed
    rewrite(tmp_path, config["rounds"][0]["source_skill_binding"],
            lambda v: v.update(coordinator_source_commit=changed))
    with pytest.raises(ValueError):
        corrected(tmp_path, contract, fixture)


@pytest.mark.parametrize("failure", ["worker-source", "worker-skills", "worker-input", "judge-capture",
    "judge-pin", "target-changed", "response-capture", "output-binding"])
def test_round_binding_preserves_downstream_checks(tmp_path, allocation, contract, failure):
    fixture = bound_bundle(tmp_path, allocation, contract, explicit=True)
    _, index, _, _, _ = fixture
    run = index["runs"][0]
    j = run["judgments"]["primary"]
    if failure.startswith("worker-"):
        key, value = {"source": ("coordinator_commit", "0" * 40),
            "skills": ("skills_commit", "0" * 40), "input": ("study_input_tree", "0" * 40)}[failure[7:]]
        rewrite(tmp_path, run["worker_input"], lambda v: v.update({key: value}))
    elif failure in ("judge-capture", "judge-pin", "target-changed"):
        def change(v):
            if failure == "judge-capture": v["target"]["capture"]["sha256"] = "0" * 64
            elif failure == "judge-pin": v["assessment_pin"]["source_commit"] = "0" * 40
            else: v["target_unchanged"] = False
        rewrite(tmp_path, j["native"]["result"], change)
        bind_outputs(tmp_path, j)
    elif failure == "response-capture":
        rewrite(tmp_path, j["response"], lambda v: v["object"]["capture"].update(sha256="0" * 64))
        bind_outputs(tmp_path, j)
    else:
        rewrite(tmp_path, j["output_binding"], lambda v: v.update(native_result_sha256="0" * 64))
    result = corrected(tmp_path, contract, fixture)
    assert result["issues"] and not result["items"]


def test_binding_is_scoped_to_its_round(tmp_path, allocation, contract):
    fixture = bound_bundle(tmp_path, allocation, contract)
    a, _, _, config, _ = fixture
    row = config["rounds"][0]
    row["round"] = 3
    assigned = next(r for r in a["rounds"] if r["round"] == 3)
    rewrite(tmp_path, row["source_skill_binding"], lambda v: v.update(
        round=3, worker_assignments=assigned["launch_order"],
        assigned_judgments=assigned["judgment_dispatch_order"]))
    result = corrected(tmp_path, contract, fixture)
    assert not result["items"] and "coordinator_commit" in result["issues"][0]["message"]


@pytest.mark.parametrize("explicit", [False, True])
def test_optional_index_skill_only_binds_supplied_guidance(tmp_path, allocation, contract, explicit):
    fixture = bound_bundle(tmp_path, allocation, contract, explicit=explicit)
    fixture[1]["runs"][0]["skill_commit"] = "f" * 40
    result = corrected(tmp_path, contract, fixture)
    if explicit:
        assert not result["items"] and "indexed supplied research skills" in result["issues"][0]["message"]
    else:
        assert len(result["items"]) == 31 and not result["issues"]


@pytest.mark.parametrize("field", ["fixed_files", "gitmodules_sha256"])
def test_binding_checks_frozen_bytes_even_when_source_diff_is_allowed(tmp_path, allocation, contract, field):
    a, _, original, config, sources = bound_bundle(tmp_path, allocation, contract)
    research = json.loads(original)
    if field == "fixed_files":
        research[field]["prompts/neutral-worker-common.md"] = "0" * 64
    else:
        research[field] = "0" * 64
    original = json.dumps(research).encode()
    config["research_procedure_sha256"] = agg.sha256(original)
    rewrite(tmp_path, config["rounds"][0]["source_skill_binding"],
            lambda v: v.update(research_procedure_sha256=agg.sha256(original)))
    with pytest.raises(ValueError, match="frozen file|gitmodules digest"):
        agg.round_bindings(config, tmp_path, original, a, config["allocation_sha256"], sources.root)


@pytest.mark.parametrize("change", ["allowed-keysdb", "reposize", "canonical"])
def test_operational_round_binding_keeps_protected_and_canonical_checks(
        tmp_path, allocation, contract, monkeypatch, change):
    import test_operational_assessment as operational

    allocation["rounds"].sort(key=lambda r: r["round"] != 2)
    retain = operational.judge.retain_operational_target

    def retain_with_change(target, identity, destination):
        if change == "reposize":
            (target / ".git/annex/reposize").mkdir()
            (target / ".git/annex/reposize/db").write_bytes(b"new metadata")
        return retain(target, identity, destination)

    monkeypatch.setattr(operational.judge, "retain_operational_target", retain_with_change)
    index, original, _ = operational.operational_bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    if change == "canonical":
        rewrite(tmp_path, run["judgments"]["primary"]["native"]["result"], lambda v: (
            v.update(canonical_unchanged=False), v["operational_integrity"].update(canonical_unchanged=False)))
    rewrite(tmp_path, run["worker_input"], lambda v: v.update(
        coordinator_commit="6" * 40, skills_commit=None))
    selection = index["comparison_provenance"]
    gate = agg.ProvenanceGate.load(original, selection, allocation, tmp_path, contract,
        selection["assessment_seal"]["sha256"], rounds={2: {
            "coordinator_source_commit": "6" * 40, "research_guidance_commit": "7" * 40}})
    assignment = next(r for r in agg.allocation_rows(allocation) if r["run_id"] == run["run_id"])
    args = (run, run["judgments"]["primary"]["native"], tmp_path, assignment)
    if change == "allowed-keysdb":
        assert gate.validate(*args)["assessment_version"] == 4
    else:
        with pytest.raises(ValueError, match="protected|canonical"):
            gate.validate(*args)


def test_cli_requires_independent_binding_digest(tmp_path, allocation, contract, monkeypatch):
    a, index, original, config, sources = bound_bundle(tmp_path, allocation, contract)
    artifact(tmp_path, "allocation.json", a)
    artifact(tmp_path, "index.json", index)
    artifact(tmp_path, "assessment-pin.json", contract.assessment_pin)
    binding = artifact(tmp_path, "round-bindings.json", config)
    artifact(tmp_path, "registration.json", {"comparison_id": a["comparison_id"],
        "allocation_sha256": config["allocation_sha256"], "procedure_sha256": agg.sha256(original)})
    monkeypatch.setattr(agg, "load_contract", lambda *_: contract)
    args = ["--allocation", str(tmp_path / "allocation.json"), "--index", str(tmp_path / "index.json"),
        "--assessment-pin", str(tmp_path / "assessment-pin.json"),
        "--assessment-procedure-sha256", agg.sha256(original), "--source-repository", str(sources.root),
        "--round-bindings", str(tmp_path / "round-bindings.json"), "--output", str(tmp_path / "report")]
    with pytest.raises(SystemExit):
        agg.main(args)
    with pytest.raises(SystemExit):
        agg.main([*args, "--round-bindings-sha256", "0" * 64])
    assert agg.main([*args, "--round-bindings-sha256", binding["sha256"]]) == 0
    result = json.loads((tmp_path / "report/aggregation.json").read_text())
    assert result["round_bindings"]["sha256"] == binding["sha256"]
    assert result["round_bindings"]["record"] == config
    assert result["research_procedure_sha256"] == agg.sha256(original)
