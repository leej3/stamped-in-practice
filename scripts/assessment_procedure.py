#!/usr/bin/env python3
"""Seal and check the common procedure before a formal comparison.

The seal is an explicitly supplied SHA-256 identity, not a signature. Commit the
manifest before use and retain its digest with the comparison's registration.
Skills may change between rounds; the task, controls and assessment may not.
"""
import argparse
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import tomllib

from research_conditions import CONDITIONS, assignment
from study_seed import blob, entries, git, study_pin, NEUTRAL_PROTOCOL, NEUTRAL_COMMON

ROOT = Path(__file__).resolve().parents[1]
FIXED_FILES = (
    "assessment-version.json", "judge-prompt.md", "prompt.md", "comparison-plan.md",
    "conditions.json", "pixi.toml",
    "scripts/assessment_procedure.py", "scripts/assessment.py",
    "scripts/prepare_launch.py", "scripts/launch_native_probe.py",
    "scripts/study_seed.py", "scripts/research_conditions.py",
    "scripts/prepare_checkout.py", "scripts/commit_provenance_hook.py", "scripts/readiness.py",
    "scripts/worker_end_state.py", "scripts/judge_workspace.py",
)
REPLAY = {"scope": "inspection-remote-retrieval-one-fresh-replay",
          "maximum_attempts": 1, "source": "exact-local-result-commit",
          "entrypoint": "object-documented", "remove_shipped_outputs": True,
          "rtol": 1e-6, "timeout_seconds": 7200, "max_get_gb": 5.0}
NEUTRAL_JUDGE = "prompts/neutral-judge.md"
NEUTRAL_FILES = tuple(name for name in FIXED_FILES if name != "judge-prompt.md") + (
    NEUTRAL_COMMON, NEUTRAL_JUDGE, "scripts/delivery_snapshot.py")
NEUTRAL_REPLAY = dict(REPLAY, source="original-complete-delivery",
                      scope="inspection-retrieval-conditional-complete-delivery-replay",
                      unsupported_capture_replay="not-checked; never substitute HEAD",
                      environment="complete stopped delivery; no automatic repair",
                      outputs="explicit documented generated files; protect supplied inputs")
NEUTRAL_THREAD_ENV = {name: "1" for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}
OPERATIONAL_JUDGE = "prompts/neutral-judge-operational.md"
OPERATIONAL_FILES = NEUTRAL_FILES + (OPERATIONAL_JUDGE, "scripts/aggregate_comparison.py",
                                    "scripts/scientific_judgment.py")
OPERATIONAL_RUNTIME = {
    "kind": "canonical-capture-complete-operational-copy-v1",
    "git_optional_locks": "0",
    "git_config": {"annex.merge-annex-branches": "false", "annex.alwayscommit": "false"},
    "permitted_metadata_paths": ["content/workspace/.git/annex/keysdb/" + name
                                  for name in ("db", "db-shm", "db-wal")],
    "canonical_validation": "exact-before-and-after",
    "operational_retention": "complete-final-bytes-and-full-delta",
    "database_logical_equivalence": "not-claimed",
    "replay_source": "fresh-complete-copy-of-canonical",
}


def is_neutral(manifest):
    return manifest.get("version") in (3, 4)


def git_config_overlay(inherited, settings):
    """Append Git configuration without dropping existing selectors or overlays."""
    environment = inherited.copy()
    try:
        count = int(environment.get("GIT_CONFIG_COUNT", "0"))
    except ValueError as error:
        raise SystemExit("Invalid inherited GIT_CONFIG_COUNT") from error
    if count < 0 or any("GIT_CONFIG_KEY_" + str(i) not in environment or
                        "GIT_CONFIG_VALUE_" + str(i) not in environment for i in range(count)):
        raise SystemExit("Incomplete inherited Git configuration overlay")
    for index, (key, value) in enumerate(settings.items(), count):
        environment["GIT_CONFIG_KEY_" + str(index)] = key
        environment["GIT_CONFIG_VALUE_" + str(index)] = value
    environment["GIT_CONFIG_COUNT"] = str(count + len(settings))
    return environment


def operational_environment(inherited):
    environment = git_config_overlay(inherited, OPERATIONAL_RUNTIME["git_config"])
    environment["GIT_OPTIONAL_LOCKS"] = OPERATIONAL_RUNTIME["git_optional_locks"]
    return environment

def neutral_environment(manifest, inherited, role):
    environment = inherited.copy()
    binary = Path(manifest).resolve().parent / ".pixi/envs/default/bin"
    if not (binary / "python").is_file():
        raise SystemExit("Prepared common resource environment is unavailable")
    pixi = shutil.which("pixi", path=inherited.get("PATH"))
    paths = [str(binary)] + ([str(Path(pixi).absolute().parent)] if pixi else []) + os.defpath.split(os.pathsep)
    environment["PATH"] = os.pathsep.join(dict.fromkeys(paths))
    environment.update(NEUTRAL_THREAD_ENV)
    if role == "judge":
        environment.update(GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    return environment

def duct_identity(executable):
    if not executable or not Path(executable).is_file():
        raise SystemExit("Requested outer execution capture requires --duct-executable")
    path = Path(executable).resolve()
    version = subprocess.check_output([str(path), "--version"], text=True).strip()
    return {"sha256": sha256(path.read_bytes()), "version": version,
            "scope": "outer local native session; detached/remote work may be unmeasured"}


def judge_template_name(manifest):
    if manifest.get("version") == 4:
        return OPERATIONAL_JUDGE
    return NEUTRAL_JUDGE if is_neutral(manifest) else "judge-prompt.md"


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def default_host_config(coordinator=ROOT):
    return Path.home() / ".config" / coordinator.name / "launch.json"


def assessment_modules_match(status):
    """Optional development evals need not be installed for frozen judging."""
    for line in status.splitlines():
        fields = line.split()
        if line[:1] == b"-" and len(fields) >= 2 and fields[1] == b"evals":
            continue
        if line[:1] != b" ":
            return False
    return True


def require_equal(actual, expected, label):
    if actual != expected:
        raise SystemExit("Formal procedure drift: " + label)


def relative_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(p in ("..", ".git") for p in path.parts):
        raise SystemExit("Expected a repository-relative file path: " + value)
    return path.as_posix()


def committed_file(repo, revision, name):
    name = relative_path(name)
    found = list(entries(repo, revision, name))
    if len(found) != 1 or found[0][0] not in ("100644", "100755") or found[0][3] != name:
        raise SystemExit("Freeze requires a regular committed file: " + name)
    return blob(repo, revision, name)


def ensure_commit(repo, revision, repository="origin"):
    """Retrieve an exact pinned object without expanding the source history."""
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision):
        raise SystemExit("Expected a full pinned commit identity")
    if not isinstance(repository, str) or not repository.strip():
        raise SystemExit("Pinned commit repository must name a Git repository or remote")
    command = ["git", "cat-file", "-e", revision + "^{commit}"]
    if subprocess.run(command, cwd=repo, capture_output=True).returncode == 0:
        return
    subprocess.run(["git", "fetch", "--no-tags", "--depth", "1", "--", repository, revision],
                   cwd=repo, check=True)
    subprocess.run(command, cwd=repo, check=True)


def gitmodules_digest(content):
    """The working skills branch hint does not select its pinned Git revision."""
    parsed = subprocess.check_output(["git", "config", "--null", "--file", "-", "--list"],
                                     input=content)
    values = {}
    for entry in parsed.split(b"\0"):
        if not entry:
            continue
        key, _, value = entry.partition(b"\n")
        if key == b"submodule.skills.branch":
            continue
        if key in values:
            raise SystemExit("Formal .gitmodules cannot have duplicate configuration keys")
        values[key] = value
    return sha256(b"\0".join(key + b"\n" + values[key] for key in sorted(values)))


def guidance_object(study, revision, name):
    """Pin only explicitly selected scientific guidance, including annex keys."""
    name = relative_path(name)
    if not name.startswith("coordinator-guidance/"):
        raise SystemExit("Selected guidance must be under the study's coordinator-guidance/")
    found = list(entries(study, revision, name))
    if len(found) != 1 or found[0][1] != "blob" or found[0][3] != name:
        raise SystemExit("Select a committed guidance file, not a directory: " + name)
    mode, kind, oid, _ = found[0]
    content = blob(study, revision, name)
    record = {"mode": mode, "git_blob": oid}
    if mode in ("100644", "100755"):
        record.update(sha256=sha256(content), size=len(content))
    elif mode == "120000":
        parts = PurePosixPath(content.decode()).parts
        if not all(part in parts for part in (".git", "annex", "objects")) or len(parts) < 2 or parts[-1] != parts[-2]:
            raise SystemExit("Only content-addressed annex links are allowed in selected guidance: " + name)
        key = parts[-1]
        match = re.fullmatch(r"SHA256E?-s([0-9]+)--([0-9a-f]{64})(?:\..*)?", key)
        if not match:
            raise SystemExit("Selected annex guidance requires a SHA256/SHA256E key: " + name)
        record.update(annex_key=key, sha256=match[2], size=int(match[1]))
    else:
        raise SystemExit("Unsupported selected guidance mode: " + name)
    return record


def guidance_content(study, revision, name, expected):
    require_equal(guidance_object(study, revision, name), expected, "scientific guidance " + name)
    if "annex_key" in expected:
        try:
            location = git(study, "annex", "contentlocation", expected["annex_key"])
        except subprocess.CalledProcessError:
            raise SystemExit("Selected annex guidance is unavailable; retrieve its pinned key before judging: " + name)
        content = (study / location).read_bytes()
    else:
        content = blob(study, revision, name)
    require_equal(sha256(content), expected["sha256"], "scientific guidance payload " + name)
    require_equal(len(content), expected["size"], "scientific guidance payload size " + name)
    return content


def profile_digest(profile):
    config = tomllib.loads((profile / "config.toml").read_text())
    # Exact-path trust and disabled host-skill paths vary across fresh clones.
    # Hook bytes are pinned separately; the native preflight checks visibility.
    config.get("hooks", {}).pop("state", None)
    projects = config.get("projects", {})
    for path, settings in list(projects.items()):
        if Path(path).is_absolute() and settings == {"trust_level": "trusted"}:
            del projects[path]
    overrides = config.get("skills", {}).pop("config", [])
    if any(item.get("enabled") is not False for item in overrides):
        raise SystemExit("Formal profile may only disable host skill overrides")
    for section in ("hooks", "skills", "projects"):
        if config.get(section) == {}:
            config.pop(section)
    return sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode())


def model_contract(profile, model):
    """Ignore cache refresh/account metadata; pin the selected runtime contract."""
    cache = profile / "models_cache.json"
    if not cache.is_file():
        return {"model": model, "sha256": None}
    models = json.loads(cache.read_text()).get("models", [])
    selected = [item for item in models if item.get("slug") == model]
    if len(selected) != 1:
        raise SystemExit("Model cache must contain exactly one selected model contract: " + model)
    incidental = {"display_name", "description", "visibility", "priority", "supported_in_api",
                  "availability_nux", "available_access_programs", "upgrade",
                  "additional_speed_tiers", "service_tiers"}
    contract = {key: value for key, value in selected[0].items() if key not in incidental}
    if "supported_reasoning_levels" in contract:
        contract["supported_reasoning_levels"] = sorted(item["effort"] for item in contract["supported_reasoning_levels"])
    if "input_modalities" in contract:
        contract["input_modalities"] = sorted(contract["input_modalities"])
    return {"model": model, "sha256": sha256(json.dumps(contract, sort_keys=True,
                            separators=(",", ":")).encode())}


def host_identity(args):
    """Only identities are portable; credentials and local paths stay on host."""
    identity = {name + "_sha256": sha256(Path(getattr(args, name)).read_bytes())
                for name in ("cli", "approved_hooks", "trust_sync", "resolver")}
    profile = Path(args.codex_home)
    identity["profile_settings_sha256"] = profile_digest(profile)
    identity["model_contract"] = model_contract(profile, args.model)
    return identity


def launch_settings(args):
    return {name: getattr(args, name) for name in
            ("model", "effort", "seconds", "review_seconds", "capture_execution")}


def load_procedure(path, expected_sha256):
    content = Path(path).read_bytes()
    if not expected_sha256:
        raise SystemExit("Formal mode requires --procedure-sha256 from the registered seal")
    require_equal(sha256(content), expected_sha256, "procedure manifest SHA-256")
    manifest = json.loads(content)
    if manifest.get("version") not in (1, 2, 3, 4) or manifest.get("status") != "sealed":
        raise SystemExit("Formal mode requires a supported sealed procedure")
    require_equal(manifest["conditions"], list(CONDITIONS), "four research conditions")
    neutral = is_neutral(manifest)
    require_equal(manifest["replay"], NEUTRAL_REPLAY if neutral else REPLAY, "supported replay scope")
    files = OPERATIONAL_FILES if manifest["version"] == 4 else NEUTRAL_FILES if neutral else FIXED_FILES
    expected = set(files) | {relative_path(manifest["resources"]["path"])}
    require_equal(set(manifest["fixed_files"]), expected, "complete fixed-file boundary")
    if manifest["version"] in (2, 4):
        research_procedure(manifest)
    elif "assessment_amendment" in manifest:
        raise SystemExit("Assessment amendments require a version 2 or 4 seal")
    if neutral:
        require_equal(manifest.get("protocol"), NEUTRAL_PROTOCOL, "neutral protocol identity")
        require_equal(set(manifest["role_hosts"]), {"research", "judge"}, "role-specific host identities")
        if not re.fullmatch(r"[0-9a-f]{64}", manifest.get("common_resources_sha256", "")):
            raise SystemExit("Neutral procedure requires frozen common resource content")
    return manifest


# Only judge-owned objects and helper locations are advertised to the role.
# Coordinator seals, allocation and other deliveries never belong here.
JUDGE_BINDINGS = {
    "STAMPED_JUDGE_OUTPUT", "STAMPED_JUDGE_TARGET", "STAMPED_JUDGE_COMMIT",
    "STAMPED_ASSESSMENT_RUNNER", "STAMPED_ASSESSMENT_PYTHON",
    "STAMPED_ASSESSMENT_SOURCE", "STAMPED_ASSESSMENT_PIN",
    "STAMPED_DELIVERY_MANIFEST", "STAMPED_OPERATIONAL_MANIFEST",
    "STAMPED_SCIENTIFIC_JUDGMENT_VALIDATOR", "STAMPED_WORKER_STOP_RECEIPT",
    "STAMPED_ASSESSMENT_VERSION",
}


def judge_runtime_projection(manifest, bindings):
    """Project an already coordinator-validated seal; never copy whole sections."""
    pin = manifest["assessment"]
    projected = {
        "kind": "judge-runtime-projection", "schema_version": 1, "role": "judge",
        "version": manifest["version"],
        "assessment": {key: copy.deepcopy(pin[key]) for key in
            ("version", "source_commit", "environment_commit", "environment_repository", "sha256")
            if key in pin},
        "fixed_files": {"scripts/assessment.py": manifest["fixed_files"]["scripts/assessment.py"]},
        "replay": copy.deepcopy(NEUTRAL_REPLAY if is_neutral(manifest) else REPLAY),
        "bindings": {key: bindings[key] for key in sorted(JUDGE_BINDINGS) if key in bindings},
        "worker_stop_receipt_sha256": sha256(Path(bindings["STAMPED_WORKER_STOP_RECEIPT"]).read_bytes()),
    }
    if is_neutral(manifest):
        projected["protocol"] = manifest["protocol"]
        from delivery_snapshot import validate_capture
        identity = validate_capture(Path(bindings["STAMPED_DELIVERY_MANIFEST"]))
        projected["delivery_capture_sha256"] = identity["capture"]["sha256"]
    validate_judge_runtime(projected)
    return projected


def validate_judge_runtime(runtime):
    """Validate a closed runtime schema without importing coordinator records."""
    neutral = is_neutral(runtime)
    expected = {"kind", "schema_version", "role", "version", "assessment", "fixed_files",
                "replay", "bindings", "worker_stop_receipt_sha256"}
    if neutral:
        expected |= {"protocol", "delivery_capture_sha256"}
    require_equal(set(runtime), expected, "judge runtime fields")
    require_equal((runtime["kind"], runtime["schema_version"], runtime["role"]),
                  ("judge-runtime-projection", 1, "judge"), "judge runtime schema")
    if runtime["version"] not in (1, 2, 3, 4):
        raise SystemExit("Unsupported judge runtime procedure version")
    require_equal(runtime["replay"], NEUTRAL_REPLAY if neutral else REPLAY, "judge replay contract")
    if neutral:
        require_equal(runtime["protocol"], NEUTRAL_PROTOCOL, "judge protocol")
    pin = runtime["assessment"]
    required_pin = {"source_commit", "environment_commit", "sha256"}
    if not required_pin <= set(pin) <= required_pin | {"version", "environment_repository"}:
        raise SystemExit("Unsupported judge assessment pin fields")
    require_equal(set(pin["sha256"]), {"pixi.toml", "pixi.lock"}, "judge environment files")
    require_equal(set(runtime["fixed_files"]), {"scripts/assessment.py"}, "judge runner files")
    for key in ("source_commit", "environment_commit"):
        if not isinstance(pin[key], str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", pin[key]):
            raise SystemExit("Invalid judge assessment commit")
    digests = [*pin["sha256"].values(), *runtime["fixed_files"].values(),
               runtime["worker_stop_receipt_sha256"]]
    if neutral:
        digests.append(runtime["delivery_capture_sha256"])
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in digests):
        raise SystemExit("Invalid judge runtime digest")
    required = JUDGE_BINDINGS - {"STAMPED_DELIVERY_MANIFEST", "STAMPED_OPERATIONAL_MANIFEST",
        "STAMPED_SCIENTIFIC_JUDGMENT_VALIDATOR", "STAMPED_ASSESSMENT_VERSION"}
    if neutral:
        required |= {"STAMPED_DELIVERY_MANIFEST", "STAMPED_ASSESSMENT_VERSION"}
    if runtime["version"] == 4:
        required |= {"STAMPED_OPERATIONAL_MANIFEST", "STAMPED_SCIENTIFIC_JUDGMENT_VALIDATOR"}
    require_equal(set(runtime["bindings"]), required, "judge runtime bindings")
    for key, value in runtime["bindings"].items():
        if key == "STAMPED_JUDGE_COMMIT":
            if value and not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
                raise SystemExit("Invalid judge target commit")
        elif not isinstance(value, str) or not Path(value).is_absolute():
            raise SystemExit("Judge runtime paths must be absolute")
    return runtime


def load_judge_runtime(path, expected_sha256, environment):
    content = Path(path).read_bytes()
    if not expected_sha256:
        raise SystemExit("Judge runtime requires its launch digest")
    require_equal(sha256(content), expected_sha256, "judge runtime SHA-256")
    runtime = validate_judge_runtime(json.loads(content))
    for key, value in runtime["bindings"].items():
        require_equal(environment.get(key), value, "judge runtime binding " + key)
    receipt = json.loads(Path(environment["STAMPED_WORKER_STOP_RECEIPT"]).read_bytes())
    require_equal(sha256(Path(environment["STAMPED_WORKER_STOP_RECEIPT"]).read_bytes()),
                  runtime["worker_stop_receipt_sha256"], "judge worker-stop receipt")
    if is_neutral(runtime):
        require_equal(receipt["capture"]["sha256"], runtime["delivery_capture_sha256"],
                      "judge captured delivery binding")
    return runtime


def research_procedure(manifest):
    """Resolve the exact original research seal in an assessment-only amendment."""
    if manifest.get("version") in (1, 3):
        return manifest
    if manifest.get("version") == 4:
        return operational_research_procedure(manifest)
    amendment = manifest.get("assessment_amendment", {})
    require_equal(amendment.get("scope"), "assessment-only", "amendment scope")
    original = amendment.get("research_procedure_json")
    if not isinstance(original, str):
        raise SystemExit("Assessment amendment requires the original research seal bytes")
    require_equal(sha256(original.encode()), amendment.get("research_procedure_sha256"),
                  "original research seal digest")
    research = json.loads(original)
    require_equal(research.get("version"), 1, "original research seal version")
    require_equal(research.get("status"), "sealed", "original research seal status")
    require_equal(set(research["fixed_files"]),
                  set(FIXED_FILES) | {relative_path(research["resources"]["path"])},
                  "original complete fixed-file boundary")
    for key in ("comparison_id", "conditions", "study", "resources", "starting_environment",
                "host_identity", "settings", "replay", "gitmodules_sha256"):
        require_equal(manifest[key], research[key], "amendment preserves " + key)
    assessment_changes = {"assessment-version.json", "scripts/assessment_procedure.py",
                          "scripts/prepare_launch.py", "scripts/launch_native_probe.py"}
    for name in set(research["fixed_files"]) - assessment_changes:
        require_equal(manifest["fixed_files"][name], research["fixed_files"][name],
                      "amendment preserves " + name)
    for key in ("environment_commit", "environment_repository", "sha256"):
        require_equal(manifest["assessment"].get(key), research["assessment"].get(key),
                      "amendment preserves assessor " + key)
    retained = amendment.get("retained_objects")
    if not isinstance(retained, list) or not retained:
        raise SystemExit("Assessment amendment requires retained object identities")
    seen = set()
    for item in retained:
        if set(item) != {"run", "seed_commit", "result_commit", "worker_end_state_sha256"}:
            raise SystemExit("Invalid retained object identity fields")
        if not isinstance(item["run"], str) or not item["run"] or item["run"] in seen:
            raise SystemExit("Retained run identities must be unique")
        seen.add(item["run"])
        for field in ("seed_commit", "result_commit"):
            if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", item[field]):
                raise SystemExit("Invalid retained commit identity")
        if not re.fullmatch(r"[0-9a-f]{64}", item["worker_end_state_sha256"]):
            raise SystemExit("Invalid retained stop receipt digest")
    return research


def operational_research_procedure(manifest):
    """Admit only a separately sealed, retained-object assessment of neutral-v1."""
    amendment = manifest.get("assessment_amendment", {})
    require_equal(amendment.get("scope"), "assessment-only", "amendment scope")
    original = amendment.get("research_procedure_json")
    allocation_bytes = amendment.get("allocation_json")
    if not isinstance(original, str) or not isinstance(allocation_bytes, str):
        raise SystemExit("Operational assessment requires original procedure and allocation bytes")
    require_equal(sha256(original.encode()), amendment.get("research_procedure_sha256"), "original research digest")
    require_equal(sha256(allocation_bytes.encode()), amendment.get("allocation_sha256"), "original allocation digest")
    research, allocation = json.loads(original), json.loads(allocation_bytes)
    require_equal(research.get("version"), 3, "original neutral research version")
    require_equal(research.get("status"), "sealed", "original neutral research status")
    require_equal(research.get("protocol"), NEUTRAL_PROTOCOL, "original neutral protocol")
    require_equal(set(research["fixed_files"]), set(NEUTRAL_FILES) | {relative_path(research["resources"]["path"])},
                  "original neutral fixed-file boundary")
    require_equal(set(manifest["fixed_files"]), set(research["fixed_files"]) | (set(OPERATIONAL_FILES) - set(NEUTRAL_FILES)),
                  "operational fixed-file boundary")
    for key in ("comparison_id", "conditions", "study", "resources", "starting_environment", "host_identity",
                "settings", "replay", "gitmodules_sha256", "protocol", "role_hosts", "common_resources_sha256", "assessment"):
        require_equal(manifest.get(key), research.get(key), "operational assessment preserves " + key)
    changes = {"scripts/assessment_procedure.py", "scripts/prepare_launch.py", "scripts/launch_native_probe.py",
               "scripts/judge_workspace.py", "scripts/delivery_snapshot.py", "scripts/assessment.py"}
    for name in set(research["fixed_files"]) - changes:
        require_equal(manifest["fixed_files"][name], research["fixed_files"][name], "operational assessment preserves " + name)
    require_equal(manifest.get("operational_runtime"), OPERATIONAL_RUNTIME, "operational runtime contract")
    require_equal(allocation.get("comparison_id"), research["comparison_id"], "allocated comparison")
    require_equal(allocation.get("conditions"), research["conditions"], "allocated conditions")
    assigned = [row["run"] for group in allocation.get("rounds", []) for row in group["launch_order"]]
    if not assigned or len(assigned) != len(set(assigned)):
        raise SystemExit("Operational assessment requires unique original allocated runs")
    retained, seen = amendment.get("retained_objects"), set()
    if not isinstance(retained, list) or not retained:
        raise SystemExit("Operational assessment requires retained complete-delivery identities")
    for item in retained:
        if set(item) != {"run", "seed_commit", "result_commit", "worker_end_state_sha256", "delivery_capture_sha256"}:
            raise SystemExit("Invalid retained complete-delivery identity fields")
        if item["run"] not in assigned or item["run"] in seen:
            raise SystemExit("Retained run must be unique and originally allocated")
        seen.add(item["run"])
        for field in ("seed_commit", "result_commit"):
            if field == "result_commit" and item[field] is None:
                continue
            if not isinstance(item[field], str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", item[field]):
                raise SystemExit("Invalid retained commit identity")
        for field in ("worker_end_state_sha256", "delivery_capture_sha256"):
            if not isinstance(item[field], str) or not re.fullmatch(r"[0-9a-f]{64}", item[field]):
                raise SystemExit("Invalid retained delivery digest")
    return research


def check_worker_sources(manifest, coordinator, study, base):
    """Validate old research identities without pretending old code is executing."""
    original = research_procedure(manifest)
    check_sources(original, coordinator, study, base,
                  validate_working=manifest.get("version") in (1, 3))


def check_retained_target(manifest, seed, seed_commit, result_commit, stop_receipt, capture_sha256=None):
    if manifest.get("version") in (1, 3):
        return
    research_procedure(manifest)
    matched = False
    for item in manifest["assessment_amendment"]["retained_objects"]:
        # Neutral deliveries can share an untouched Git seed/HEAD. Version 4
        # binds the allocated run to its exact stop and capture below instead.
        if (manifest.get("version") != 4 and item["run"] != seed.get("run") and
                (item["seed_commit"] == seed_commit or
                 (result_commit is not None and item["result_commit"] == result_commit))):
            raise SystemExit("A retained object cannot be relabeled as a new run")
        if item["run"] == seed.get("run"):
            require_equal(seed_commit, item["seed_commit"], "retained worker seed")
            require_equal(result_commit, item["result_commit"], "retained scientific result")
            require_equal(sha256(Path(stop_receipt).read_bytes()), item["worker_end_state_sha256"],
                          "retained original stop receipt")
            if manifest.get("version") == 4:
                require_equal(capture_sha256, item["delivery_capture_sha256"], "retained original delivery capture")
            matched = True
    if manifest.get("version") == 4 and not matched:
        raise SystemExit("Operational assessment cannot add an unregistered retained object")


def check_sources(manifest, coordinator, study, base=None, *, validate_working=True):
    """Read committed identities; reject changed executing code or configuration."""
    ensure_commit(coordinator, manifest["coordinator_commit"])
    environment = manifest["starting_environment"]
    ensure_commit(coordinator, environment["commit"], environment.get("repository", "origin"))
    pin = manifest["assessment"]
    ensure_commit(coordinator, pin["environment_commit"], pin.get("environment_repository", "origin"))
    ensure_commit(study, manifest["study"]["commit"])
    for name, digest in manifest["fixed_files"].items():
        require_equal(sha256(committed_file(coordinator, manifest["coordinator_commit"], name)),
                      digest, "sealed source " + name)
        if validate_working:
            require_equal(sha256((coordinator / name).read_bytes()), digest, "working " + name)
        if base:
            require_equal(sha256(committed_file(coordinator, base, name)), digest,
                          "selected coordinator revision " + name)
    configurations = [committed_file(coordinator, manifest["coordinator_commit"], ".gitmodules")]
    if validate_working:
        configurations.append((coordinator / ".gitmodules").read_bytes())
    for content in configurations:
        require_equal(gitmodules_digest(content), manifest["gitmodules_sha256"], "submodule source configuration")
    if base:
        require_equal(gitmodules_digest(committed_file(coordinator, base, ".gitmodules")),
                      manifest["gitmodules_sha256"], "selected submodule source configuration")
    require_equal(json.loads(blob(coordinator, manifest["coordinator_commit"], "assessment-version.json")),
                  manifest["assessment"], "assessor source/runtime pin")
    selected = manifest["study"]["commit"]
    if base:
        path, selected = study_pin(coordinator, base, study)
        require_equal(path, manifest["study"]["path"], "study identity")
        ensure_commit(study, selected)
    require_equal(git(study, "rev-parse", selected + ":input"), manifest["study"]["input_tree"],
                  "scientific inputs")
    # Unrelated preparation artifacts and old judgments are outside this set.
    for name, expected in manifest["study"]["guidance_objects"].items():
        for revision in {selected, manifest["study"]["commit"]}:
            require_equal(guidance_object(study, revision, name), expected, "scientific guidance " + name)
    for name, digest in environment["sha256"].items():
        require_equal(sha256(committed_file(coordinator, environment["commit"], name)), digest,
                      "immutable starting environment " + name)
    for name, digest in pin["sha256"].items():
        require_equal(sha256(committed_file(coordinator, pin["environment_commit"], name)), digest,
                      "assessor environment " + name)


def check_host(manifest, args):
    if is_neutral(manifest):
        role = getattr(args, "role", "research")
        require_equal(host_identity(args), manifest["role_hosts"][role]["identity"],
                      role + " native runtime/profile/hook resources")
        for name, path in (("pixi.toml", args.env_manifest),
                           ("pixi.lock", Path(args.env_manifest).with_name("pixi.lock"))):
            require_equal(sha256(Path(path).read_bytes()), manifest["role_hosts"][role]["environment"][name],
                          role + " prepared resource environment " + name)
        require_equal(manifest["role_hosts"][role]["thread_environment"], NEUTRAL_THREAD_ENV, "common thread settings")
        require_equal(duct_identity(getattr(args, "duct_executable", None)) if args.capture_execution else None,
                      manifest["role_hosts"][role]["duct"], "outer execution capture")
        if role == "research":
            require_equal(sha256(Path(args.common_resources).read_bytes()),
                          manifest["common_resources_sha256"], "common optional resources")
        return
    require_equal(host_identity(args), manifest["host_identity"], "native runtime/profile/hook resources")
    environment = manifest["starting_environment"]
    for name, path in (("pixi.toml", args.env_manifest),
                       ("pixi.lock", Path(args.env_manifest).with_name("pixi.lock"))):
        require_equal(sha256(Path(path).read_bytes()), environment["sha256"][name],
                      "prepared starting " + name)


def check_settings(manifest, args):
    if manifest.get("version") in (2, 4) and args.role != "judge":
        raise SystemExit("An assessment-only amendment cannot authorize research launches")
    require_equal(launch_settings(args), manifest["settings"][args.role], args.role + " settings")


def check_readiness(manifest, path):
    if not path:
        raise SystemExit("Formal mode requires --resource-readiness from a completed host check")
    receipt = json.loads(Path(path).read_text())
    require_equal(receipt.get("requirements_sha256"), manifest["resources"]["sha256"],
                  "readiness requirements")
    if receipt.get("schema_version") != 1 or receipt.get("ready") is not True or receipt.get("complete") is not True:
        raise SystemExit("Formal resources are not ready; inspect the readiness receipt")
    return receipt


def check_native(manifest, cli, profile, role="research"):
    identity = manifest["role_hosts"][role]["identity"] if is_neutral(manifest) else manifest["host_identity"]
    require_equal(sha256(cli.read_bytes()), identity["cli_sha256"], "native CLI")
    require_equal(profile_digest(profile), identity["profile_settings_sha256"],
                  "native profile settings")
    expected = identity["model_contract"]
    require_equal(model_contract(profile, expected["model"]), expected, "native model contract")


def check_seed(manifest, seed):
    require_equal(seed.get("study_path"), manifest["study"]["path"], "worker study identity")
    require_equal(seed.get("study_input_tree"), manifest["study"]["input_tree"], "worker input tree")
    if is_neutral(manifest):
        require_equal(seed.get("protocol"), NEUTRAL_PROTOCOL, "worker protocol")
        require_equal(seed.get("common_prompt_sha256"), manifest["fixed_files"][NEUTRAL_COMMON],
                      "neutral common instructions")
        require_equal(seed.get("common_resources_sha256"), manifest["common_resources_sha256"],
                      "neutral common resources")
    else:
        require_equal(seed.get("source_manifest_sha256"), manifest["fixed_files"]["pixi.toml"],
                      "worker starting environment declarations")
    selected = seed.get("assignment", {})
    require_equal(selected.get("config_sha256"), manifest["fixed_files"]["conditions.json"],
                  "worker condition instructions")
    if selected.get("condition") not in CONDITIONS:
        raise SystemExit("Formal mode requires a worker from the four-condition design")


def retain_inputs(manifest, coordinator, study, destination):
    """Materialize verified Git blobs; relative guidance links stay in this copy."""
    destination.mkdir(parents=True, exist_ok=False)
    for name in (judge_template_name(manifest), "assessment-version.json"):
        content = committed_file(coordinator, manifest["coordinator_commit"], name)
        require_equal(sha256(content), manifest["fixed_files"][name], name)
        (destination / name).parent.mkdir(parents=True, exist_ok=True)
        (destination / name).write_bytes(content)
    for name, expected in manifest["study"]["guidance_objects"].items():
        content = guidance_content(study, manifest["study"]["commit"], name, expected)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o755 if expected["mode"] == "100755" else 0o644)
    return destination


def replay_instruction(manifest):
    if is_neutral(manifest):
        return ("\nFrozen captured-delivery replay scope: " + json.dumps(manifest["replay"], sort_keys=True) +
                "\nUse fresh-rerun --path \"$STAMPED_JUDGE_TARGET\" --entry from the original documentation "
                "with explicit --outputs for generated files and --workdir/--output under STAMPED_JUDGE_OUTPUT. "
                "One attempt copies the complete stopped delivery, removes only selected outputs, and uses "
                "the documented entrypoint without repair. Unsupported external pointers or unsafe output "
                "selection are not-checked; never substitute a Git-only clone or infer scientific failure.\n")
    return ("\nFrozen formal replay scope: " + json.dumps(manifest["replay"], sort_keys=True) +
            "\nUse fresh-rerun --path \"$STAMPED_JUDGE_TARGET\" with an explicit --entry from the "
            "object's documentation, and --workdir and --output under STAMPED_JUDGE_OUTPUT. "
            "The wrapper permits one attempt, including an unsuccessful attempt.\n")


def worker_credit_instruction(receipt):
    return ("\nWorker-stop evidence: " + str(receipt.resolve()) + " (SHA-256 " +
            sha256(receipt.read_bytes()) + ").\n"
            "Assess the scientific artifact contents normally. Grade the worker's versioning, "
            "tracking and publication practices at the recorded worker stop. Attribute later "
            "coordinator commits, annex conversion, publication and retention separately; those "
            "actions do not establish worker compliance. The submitted artifacts must match "
            "the recorded stop inventory.\n")


def seal(args):
    coordinator = args.repo.resolve()
    base = git(coordinator, "rev-parse", args.base + "^{commit}")
    study_path, study_commit = study_pin(coordinator, base, args.study)
    resources = relative_path(args.resources)
    requirements = json.loads(committed_file(coordinator, base, resources))
    if requirements.get("schema_version") != 1 or not requirements.get("requirements"):
        raise SystemExit("--resources requires the public readiness requirements JSON")
    neutral = getattr(args, "protocol", "legacy") == NEUTRAL_PROTOCOL
    operational = neutral and bool(getattr(args, "research_procedure", None))
    files = {name: sha256(committed_file(coordinator, base, name))
             for name in (*(OPERATIONAL_FILES if operational else NEUTRAL_FILES if neutral else FIXED_FILES), resources)}
    for condition in CONDITIONS:
        assignment(blob(coordinator, base, "conditions.json"), condition)
    selected_guidance = {name for name in (args.rubric, args.reference, *args.guidance_dependency) if name}
    guidance = {name: guidance_object(args.study, study_commit, name) for name in sorted(selected_guidance)}
    environment_repository = getattr(args, "environment_repository", "origin")
    if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", args.environment_commit):
        ensure_commit(coordinator, args.environment_commit, environment_repository)
    environment_commit = git(coordinator, "rev-parse", args.environment_commit + "^{commit}")
    environment = {name: sha256(committed_file(coordinator, environment_commit, name))
                   for name in ("pixi.toml", "pixi.lock")}
    require_equal(environment["pixi.toml"], files["pixi.toml"], "starting environment snapshot manifest")
    pin = json.loads(blob(coordinator, base, "assessment-version.json"))
    require_equal(git(coordinator, "rev-parse", base + ":assessment"), pin["source_commit"],
                  "assessor gitlink")
    ensure_commit(coordinator, pin["environment_commit"], pin.get("environment_repository", "origin"))
    for name, digest in pin["sha256"].items():
        require_equal(sha256(committed_file(coordinator, pin["environment_commit"], name)), digest,
                      "assessor environment " + name)
    settings = launch_settings(args)
    manifest = {
        "version": 1, "status": "sealed", "comparison_id": args.comparison_id,
        "coordinator_commit": base, "fixed_files": files, "assessment": pin,
        "gitmodules_sha256": gitmodules_digest(committed_file(coordinator, base, ".gitmodules")),
        "study": {"path": study_path, "commit": study_commit,
                  "input_tree": git(args.study, "rev-parse", study_commit + ":input"),
                  "task_sha256": sha256(blob(args.study, study_commit, "input/study-task.md")),
                  "guidance_files": {name: record["sha256"] for name, record in guidance.items()},
                  "guidance_objects": guidance, "guidance_dependencies": sorted(args.guidance_dependency),
                  "rubric": args.rubric, "reference": args.reference},
        "resources": {"path": resources, "sha256": files[resources]},
        "starting_environment": {"commit": environment_commit, "repository": environment_repository,
                                 "sha256": environment},
        "host_identity": host_identity(args), "conditions": list(CONDITIONS),
        "settings": {"research": settings, "judge": dict(settings, capture_execution=False)},
        "replay": REPLAY,
    }
    if neutral:
        if not getattr(args, "common_resources", None):
            raise SystemExit("Neutral sealing requires --common-resources")
        judge_args = copy.copy(args)
        if getattr(args, "judge_host_config", None):
            values = json.loads(Path(args.judge_host_config).read_text())
            allowed = {"cli", "approved_hooks", "trust_sync", "resolver", "codex_home", "env_manifest",
                       "model", "effort", "seconds", "review_seconds", "capture_execution", "duct_executable"}
            if set(values) - allowed:
                raise SystemExit("Judge host config contains unsupported fields")
            for key, value in values.items():
                setattr(judge_args, key, value)
        hosts = {}
        for role, selected in (("research", args), ("judge", judge_args)):
            hosts[role] = {"identity": host_identity(selected), "environment": {
                name: sha256(Path(selected.env_manifest).with_name(name).read_bytes())
                for name in ("pixi.toml", "pixi.lock")},
                "thread_environment": NEUTRAL_THREAD_ENV,
                "duct": duct_identity(getattr(selected, "duct_executable", None))
                        if selected.capture_execution else None}
        manifest.update(version=3, protocol=NEUTRAL_PROTOCOL, role_hosts=hosts,
                        common_resources_sha256=sha256(Path(args.common_resources).read_bytes()),
                        replay=NEUTRAL_REPLAY)
        manifest["settings"]["judge"] = launch_settings(judge_args)
    if getattr(args, "research_procedure", None):
        original = Path(args.research_procedure).read_bytes()
        load_procedure(args.research_procedure, args.research_procedure_sha256)
        manifest.update(version=4 if operational else 2, assessment_amendment={
            "scope": "assessment-only", "research_procedure_json": original.decode(),
            "research_procedure_sha256": args.research_procedure_sha256,
            "retained_objects": json.loads(Path(args.retained_objects).read_text())})
        if operational:
            if not getattr(args, "allocation", None) or not getattr(args, "allocation_sha256", None):
                raise SystemExit("Operational amendment requires the original allocation and independent digest")
            allocation_bytes = Path(args.allocation).read_bytes()
            require_equal(sha256(allocation_bytes), args.allocation_sha256, "selected allocation digest")
            manifest["assessment_amendment"].update(allocation_json=allocation_bytes.decode(),
                                                   allocation_sha256=args.allocation_sha256)
            manifest["operational_runtime"] = copy.deepcopy(OPERATIONAL_RUNTIME)
        research_procedure(manifest)
    check_sources(manifest, coordinator, args.study, base)
    check_host(manifest, args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    with args.output.open("xb") as stream:
        stream.write(content)
    print(json.dumps({"status": "sealed", "procedure_sha256": sha256(content),
                      "comparison_id": args.comparison_id}))


def replay_arguments(manifest, arguments, target, output):
    """Constrain the frozen helper, without editing its source or the result."""
    if "--help" in arguments or "-h" in arguments:
        return arguments
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--entry", required=True)
    parser.add_argument("--outputs", nargs="+", required=is_neutral(manifest))
    parser.add_argument("--in-container")
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--rtol", type=float, default=REPLAY["rtol"])
    parser.add_argument("--timeout", type=int, default=REPLAY["timeout_seconds"])
    parser.add_argument("--max-get-gb", type=float, default=REPLAY["max_get_gb"])
    args = parser.parse_args(arguments)
    require_equal(args.path.resolve(), target.resolve(), "replay exact target path")
    for actual, key in ((args.rtol, "rtol"), (args.timeout, "timeout_seconds"),
                        (args.max_get_gb, "max_get_gb")):
        require_equal(actual, manifest["replay"][key], "replay " + key)
    for path in (args.workdir, args.output):
        if not path.resolve().is_relative_to(output.resolve()):
            raise SystemExit("Formal replay evidence must stay under STAMPED_JUDGE_OUTPUT")
    if (output / "formal-replay-attempt.json").exists():
        raise SystemExit("Formal replay allowance already consumed; retain this attempt")
    collisions = [str(path) for path in (args.workdir, args.output) if os.path.lexists(path)]
    overlap = args.output.resolve().is_relative_to(args.workdir.resolve())
    if collisions or overlap:
        reason = "Replay workdir/output must be new separate paths; do not mkdir the workdir"
        with tempfile.NamedTemporaryFile(mode="w", prefix="formal-replay-preflight-",
                suffix=".json", dir=output, delete=False) as stream:
            json.dump({"status": "rejected-before-attempt", "reason": reason,
                       "arguments": arguments, "existing_paths": collisions}, stream, indent=2)
            stream.write("\n")
        raise SystemExit(reason)
    if is_neutral(manifest):
        from delivery_snapshot import validate_capture
        identity = validate_capture(Path(os.environ["STAMPED_DELIVERY_MANIFEST"]))
        target_identity = {"target_commit": identity["commit"], "capture": identity["capture"]}
    else:
        target_identity = {"target_commit": git(target, "rev-parse", "HEAD")}
    # Exclusive creation counts failures as attempts and resists concurrent calls.
    try:
        with (output / "formal-replay-attempt.json").open("x") as stream:
            json.dump({"arguments": arguments, **target_identity}, stream)
    except FileExistsError:
        raise SystemExit("Formal replay allowance already consumed; retain this attempt")
    return arguments


def main():
    preliminary = argparse.ArgumentParser(add_help=False)
    preliminary.add_argument("--host-config", type=Path, default=default_host_config())
    known, _ = preliminary.parse_known_args()
    defaults = json.loads(known.host_config.read_text()) if known.host_config.is_file() else {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("seal", "check"))
    parser.add_argument("--host-config", type=Path, default=known.host_config)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--base", required=True)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--procedure", type=Path)
    parser.add_argument("--procedure-sha256")
    parser.add_argument("--comparison-id")
    parser.add_argument("--protocol", choices=("legacy", NEUTRAL_PROTOCOL), default="legacy")
    parser.add_argument("--common-resources", type=Path)
    parser.add_argument("--judge-host-config", type=Path,
                        help="Neutral protocol only: role-specific public host/settings configuration")
    parser.add_argument("--resources")
    parser.add_argument("--rubric")
    parser.add_argument("--reference")
    parser.add_argument("--guidance-dependency", action="append", default=[],
                        help="Explicit study-relative rubric/reference dependency; repeat as needed")
    parser.add_argument("--environment-commit")
    parser.add_argument("--environment-repository", default="origin",
                        help="Repository containing the starting snapshot; defaults to origin")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--research-procedure", type=Path,
                        help="Original immutable seal for an assessment-only amendment")
    parser.add_argument("--research-procedure-sha256")
    parser.add_argument("--retained-objects", type=Path,
                        help="Exact already completed worker identities for an amendment")
    parser.add_argument("--allocation", type=Path,
                        help="Original neutral allocation bytes for a version 4 assessment amendment")
    parser.add_argument("--allocation-sha256")
    for name in ("env-manifest", "cli", "codex-home", "approved-hooks", "trust-sync", "resolver"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--seconds", type=int, default=0)
    parser.add_argument("--review-seconds", type=int, default=5400)
    parser.add_argument("--capture-execution", action="store_true")
    parser.add_argument("--duct-executable", type=Path)
    parser.set_defaults(**{k: v for k, v in defaults.items() if k != "repo"})
    args = parser.parse_args()
    amendment_flags = (args.research_procedure, args.research_procedure_sha256, args.retained_objects)
    if any(amendment_flags) and (args.action != "seal" or not all(amendment_flags)):
        parser.error("Assessment amendment sealing requires all three original-seal/retention flags")
    for name in ("env_manifest", "cli", "codex_home", "approved_hooks", "trust_sync", "resolver"):
        value = getattr(args, name)
        if not value:
            parser.error("Missing --" + name.replace("_", "-") + "; configure host defaults once")
        setattr(args, name, Path(value).expanduser().resolve())
    if args.action == "seal":
        for name in ("comparison_id", "resources", "rubric", "environment_commit", "output"):
            if not getattr(args, name):
                parser.error("seal requires --" + name.replace("_", "-"))
        if args.seconds < 0 or args.review_seconds < 0:
            parser.error("Time settings must be nonnegative")
        seal(args)
    else:
        if not args.procedure:
            parser.error("check requires --procedure")
        manifest = load_procedure(args.procedure, args.procedure_sha256)
        check_sources(manifest, args.repo.resolve(), args.study.resolve(), args.base)
        check_host(manifest, args)
        print(json.dumps({"status": "formal-verified", "procedure_sha256": args.procedure_sha256}))


if __name__ == "__main__":
    main()
