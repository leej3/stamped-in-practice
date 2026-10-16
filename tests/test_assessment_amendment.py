"""An assessment amendment must not rewrite or weaken research identities."""
import copy
import json

import pytest

from test_assessment_procedure import comparison
import assessment_procedure as procedure
from test_launch import commit, fake_cli


@pytest.fixture
def amendment(comparison):
    args, original = comparison
    updated = copy.deepcopy(original)
    changed = args.repo / "scripts/assessment_procedure.py"
    changed.write_text(changed.read_text() + "\n# synthetic assessment adapter\n")
    updated["fixed_files"]["scripts/assessment_procedure.py"] = procedure.sha256(changed.read_bytes())
    updated["coordinator_commit"] = commit(args.repo, "test: freeze synthetic assessment amendment")
    stop = args.repo.parent / "stop.json"
    stop.write_text('{"synthetic":true}\n')
    updated.update(version=2, assessment_amendment={
        "scope": "assessment-only", "research_procedure_json": args.output.read_text(),
        "research_procedure_sha256": procedure.sha256(args.output.read_bytes()),
        "retained_objects": [{"run": "retained-01", "seed_commit": "1" * 40,
                              "result_commit": "2" * 40,
                              "worker_end_state_sha256": procedure.sha256(stop.read_bytes())}]})
    return args, original, updated, stop


def test_new_execution_and_original_research_both_validated(amendment):
    args, original, updated, _ = amendment
    procedure.check_sources(updated, args.repo, args.study)
    procedure.check_worker_sources(updated, args.repo, args.study, args.base)
    with pytest.raises(SystemExit, match="working scripts/assessment_procedure.py"):
        procedure.check_sources(original, args.repo, args.study, args.base)
    changed = args.repo / "scripts/assessment_procedure.py"
    changed.write_text(changed.read_text() + "\n# unsealed drift\n")
    with pytest.raises(SystemExit, match="working scripts/assessment_procedure.py"):
        procedure.check_sources(updated, args.repo, args.study)


def test_amendment_cannot_authorize_research(amendment):
    args, _, updated, _ = amendment
    with pytest.raises(SystemExit, match="cannot authorize research"):
        procedure.check_settings(updated, args)
    args.role = "judge"
    args.capture_execution = False
    procedure.check_settings(updated, args)


@pytest.mark.parametrize("field", ["prompt.md", "judge-prompt.md", "comparison-plan.md",
                                    "conditions.json", "pixi.toml", "scripts/assessment.py",
                                    "scripts/worker_end_state.py", "scripts/study_seed.py"])
def test_research_and_judging_instructions_stay_fixed(amendment, field):
    _, _, updated, _ = amendment
    updated["fixed_files"][field] = "0" * 64
    with pytest.raises(SystemExit, match="amendment preserves"):
        procedure.research_procedure(updated)


@pytest.mark.parametrize("field", ["conditions", "study", "resources", "starting_environment",
                                    "host_identity", "settings", "replay"])
def test_stable_design_boundaries(amendment, field):
    _, _, updated, _ = amendment
    updated[field] = None
    with pytest.raises(SystemExit, match="amendment preserves"):
        procedure.research_procedure(updated)


def test_original_seal_bytes_cannot_be_rewritten(amendment):
    _, _, updated, _ = amendment
    updated["assessment_amendment"]["research_procedure_json"] += "\n"
    with pytest.raises(SystemExit, match="original research seal digest"):
        procedure.research_procedure(updated)


def test_retained_identity_and_stop_receipt_are_enforced(amendment):
    _, _, updated, stop = amendment
    seed = {"run": "retained-01"}
    procedure.check_retained_target(updated, seed, "1" * 40, "2" * 40, stop)
    with pytest.raises(SystemExit, match="cannot be relabeled"):
        procedure.check_retained_target(updated, {"run": "other"}, "1" * 40, "2" * 40, stop)
    with pytest.raises(SystemExit, match="retained worker seed"):
        procedure.check_retained_target(updated, seed, "3" * 40, "2" * 40, stop)
    with pytest.raises(SystemExit, match="retained scientific result"):
        procedure.check_retained_target(updated, seed, "1" * 40, "3" * 40, stop)
    stop.write_text('{"changed":true}\n')
    with pytest.raises(SystemExit, match="original stop receipt"):
        procedure.check_retained_target(updated, seed, "1" * 40, "2" * 40, stop)


def test_unregistered_research_source_drift_rejected(amendment):
    args, _, updated, _ = amendment
    (args.repo / "prompt.md").write_text("Changed scientific request\n")
    changed = commit(args.repo, "test: change research instructions")
    with pytest.raises(SystemExit, match="selected coordinator revision"):
        procedure.check_worker_sources(updated, args.repo, args.study, changed)


@pytest.mark.parametrize("field", ["seed_commit", "result_commit"])
def test_matching_retained_row_does_not_hide_a_later_collision(amendment, field):
    _, _, updated, stop = amendment
    first = updated["assessment_amendment"]["retained_objects"][0]
    later = dict(first, run="retained-02", seed_commit="3" * 40,
                 result_commit="4" * 40)
    later[field] = first[field]
    updated["assessment_amendment"]["retained_objects"].append(later)
    with pytest.raises(SystemExit, match="cannot be relabeled"):
        procedure.check_retained_target(updated, {"run": "retained-01"},
                                         "1" * 40, "2" * 40, stop)


def test_future_run_requires_original_research_source_validation(amendment):
    args, _, updated, stop = amendment
    procedure.check_retained_target(updated, {"run": "future-02"}, "3" * 40, "4" * 40, stop)
    procedure.check_worker_sources(updated, args.repo, args.study, args.base)
    (args.repo / "scripts/study_seed.py").write_text("Changed input construction\n")
    changed = commit(args.repo, "test: alter future research source")
    with pytest.raises(SystemExit, match="selected coordinator revision"):
        procedure.check_worker_sources(updated, args.repo, args.study, changed)


def test_amendment_load_roundtrip_and_original_seal_unchanged(amendment, tmp_path):
    args, original, updated, _ = amendment
    path = tmp_path / "assessment-seal.json"
    path.write_text(json.dumps(updated))
    loaded = procedure.load_procedure(path, procedure.sha256(path.read_bytes()))
    assert procedure.research_procedure(loaded) == original
    assert procedure.load_procedure(args.output, args.procedure_sha256) == original
