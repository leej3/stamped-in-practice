"""Export committed study inputs into a parentless, independent Git object store."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath

import tomlkit

from research_conditions import RESEARCH_SKILLS, assignment, supplied_skills


def git(repo, *args, text=True):
    return subprocess.check_output(["git", "-C", str(repo), *map(str, args)], text=text).strip() if text else subprocess.check_output(["git", "-C", str(repo), *map(str, args)])


def blob(repo, ref, path):
    return git(repo, "show", f"{ref}:{path}", text=False)


def entries(repo, ref, prefix):
    for entry in git(repo, "ls-tree", "-rz", ref, "--", prefix, text=False).split(b"\0"):
        if entry:
            header, path = entry.split(b"\t", 1)
            mode, kind, oid = header.decode().split()
            yield mode, kind, oid, path.decode()


def worker_manifest(content):
    document = tomlkit.parse(content.decode())
    # The coordinator's operational tasks invoke files deliberately not supplied.
    document.pop("tasks", None)
    for feature in document.get("feature", {}).values():
        feature.pop("tasks", None)
    return tomlkit.dumps(document).encode()


def study_pin(repo, base, study):
    study = study.resolve()
    try:
        path = study.relative_to(repo.resolve()).as_posix()
    except ValueError:
        raise SystemExit("Research --study must be an installed coordinator submodule")
    lines = list(entries(repo, base, path))
    if len(lines) != 1 or lines[0][0] != "160000" or lines[0][3] != path:
        raise SystemExit("--study is not a submodule at the coordinator's selected --base")
    ref = lines[0][2]
    if git(study, "rev-parse", "--show-toplevel") != str(study):
        raise SystemExit("Install the selected study submodule before launch")
    git(study, "cat-file", "-e", ref + "^{commit}")
    readiness = "coordinator-guidance/readiness.json"
    if list(entries(study, ref, readiness)):
        status = json.loads(blob(study, ref, readiness))
        if status.get("ready") is not True:
            raise SystemExit("Study is not ready: " + status.get("reason", readiness))
    return path, ref


def annex_locations(study, key):
    result = subprocess.run(
        ["git", "-C", str(study), "annex", "whereis", "--json", "--key", key],
        capture_output=True, text=True)
    try:
        locations = json.loads(result.stdout)
    except json.JSONDecodeError:
        result.check_returncode()
        raise
    # A valid key without published location history has no known copies.
    # git-annex reports that metadata result with exit 1, not a command error.
    empty_locations = (isinstance(locations, dict) and result.returncode == 1
                       and locations.get("command") == "whereis"
                       and locations.get("key") == key
                       and locations.get("note") == "0 copies"
                       and locations.get("success") is False
                       and locations.get("whereis") == []
                       and locations.get("error-messages") == [])
    if not empty_locations:
        result.check_returncode()
    return locations


def export_inputs(study, ref, checkout):
    inventory = []
    annex_ready = False
    for mode, kind, oid, path in entries(study, ref, "input"):
        name = PurePosixPath(path)
        if name.parts[0] != "input" or any(part in ("..", ".git") for part in name.parts):
            raise SystemExit("Unexpected study input path")
        target = checkout / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if kind != "blob":
            raise SystemExit("Study input must contain files, not nested submodules")
        content = git(study, "cat-file", "blob", oid, text=False)
        record = {"path": path, "git_blob": oid, "mode": mode}
        if mode == "120000":
            link = content.decode()
            parts = PurePosixPath(link).parts
            # Retain annex identity without copying the study's git-annex history.
            if ".git" not in parts or "annex" not in parts or "objects" not in parts or len(parts) < 2 or parts[-1] != parts[-2]:
                raise SystemExit("Only annex payload links are allowed in study input")
            key = parts[-1]
            if not key or "/" in key or key in (".", ".."):
                raise SystemExit("Invalid input annex key")
            if not annex_ready:
                # A Git-only study clone may lack both an annex UUID and a
                # published metadata branch. Initialize only this repository;
                # this neither retrieves payloads nor initializes submodules.
                if not git(study, "config", "--get", "--default", "", "annex.uuid"):
                    git(study, "annex", "init", "coordinator-study-inputs")
                annex_ready = True
            # Original links may encode a different worktree depth; rebuild the
            # relative link for this independent repository, keeping the key.
            object_path = git(study, "annex", "examinekey", "--format=${hashdirmixed}${key}/${key}", key)
            annex_target = checkout / ".git/annex/objects" / object_path
            target.symlink_to(os.path.relpath(annex_target, target.parent))
            record["annex_key"] = key
            locations = annex_locations(study, key)
            record["urls"] = sorted(set(locations.get("urls", [])) |
                                    {url for location in locations.get("whereis", [])
                                     for url in location.get("urls", [])})
        elif mode in ("100644", "100755"):
            if len(content) > 100 * 1024:
                raise SystemExit("Large study inputs must be annexed before launch: " + path)
            target.write_bytes(content)
            target.chmod(0o755 if mode == "100755" else 0o644)
            record["sha256"] = hashlib.sha256(content).hexdigest()
        else:
            raise SystemExit("Unsupported study input mode")
        inventory.append(record)
    prompt = checkout / "input/study-task.md"
    if not prompt.is_file() or prompt.is_symlink():
        raise SystemExit("Study input/study-task.md must be a committed text file")
    if not (checkout / "input/sources.json").is_file():
        raise SystemExit("Study input/sources.json is required for source provenance")
    return inventory


def make_seed(repo, base, study, checkout, branch, condition, provenance):
    """Copy only selected blobs; never fetch the coordinator or study history."""
    study_path, ref = study_pin(repo, base, study)
    selected = None
    if list(entries(repo, base, "conditions.json")):
        selected = assignment(blob(repo, base, "conditions.json"), condition)
        condition = selected["condition"]
    elif condition not in ("baseline", "skills"):
        raise SystemExit("Selected coordinator revision predates the four-condition design")
    if checkout.exists():
        raise SystemExit("Worker destination already exists; preserve it and choose another")
    checkout.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", branch, str(checkout)], check=True, stdout=subprocess.DEVNULL)
    git(checkout, "config", "core.hooksPath", str(checkout / ".git/hooks"))
    source_manifest = blob(repo, base, "pixi.toml")
    (checkout / "pixi.toml").write_bytes(worker_manifest(source_manifest))
    (checkout / ".gitignore").write_text(".pixi/\npixi.lock\n__pycache__/\n*.pyc\n.codex/\n.entire/\n.local/\n")
    (checkout / ".gitattributes").write_text("* annex.backend=SHA256E\n* annex.largefiles=(largerthan=100kb)\n*.md annex.largefiles=nothing\n*.toml annex.largefiles=nothing\npixi.lock annex.largefiles=nothing\n")
    inventory = export_inputs(study, ref, checkout)
    receipt = {"version": 1, "coordinator_commit": base, "study_path": study_path,
               "study_commit": ref, "study_input_tree": git(study, "rev-parse", ref + ":input"),
               "study_url": git(study, "remote", "get-url", "origin"),
               "source_manifest_sha256": hashlib.sha256(source_manifest).hexdigest(),
               "condition": condition, "run": branch.removeprefix("codex/").replace("/", "-"),
               "inputs": inventory}
    if selected:
        receipt.update(version=2, assignment=selected)
    assigned_skills = supplied_skills(receipt)
    if assigned_skills:
        skills = list(entries(repo, base, "skills"))
        if len(skills) != 1 or skills[0][0] != "160000":
            raise SystemExit("Treatment requires a pinned skills submodule")
        skill_ref = skills[0][2]
        modules = checkout / ".gitmodules"
        original = blob(repo, base, ".gitmodules").decode()
        # Read the URL from the selected revision, not a changed worktree config.
        scratch = checkout / ".git/source-modules"
        scratch.write_text(original)
        url = git(checkout, "config", "-f", scratch, "--get", "submodule.skills.url")
        modules.write_text('[submodule "skills"]\n\tpath = skills\n\turl = ' + url + '\n')
        for name in assigned_skills:
            path = checkout / ".agents/skills" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to("../../skills/skills/" + name)
        receipt["skills_commit"] = skill_ref
        receipt["skills_url"] = url
    (checkout / "worker-input.json").write_text(json.dumps(receipt, indent=2) + "\n")
    git(checkout, "add", "--all")
    if assigned_skills:
        git(checkout, "update-index", "--add", "--cacheinfo", "160000," + skill_ref + ",skills")
    # Resolve at creation time; never copy attribution from a previous run.
    trailers = subprocess.check_output([str(provenance)], text=True).strip()
    git(checkout, "commit", "-m", "chore(study): seed independent research inputs\n\n" + trailers)
    remote = git(repo, "remote", "get-url", "--push", "origin")
    if not remote.startswith("git@github.com:"):
        raise SystemExit("Coordinator must have a configured SSH GitHub push remote")
    git(checkout, "remote", "add", "origin", remote)
    # Never fetch other experiment branches through a default wildcard refspec.
    git(checkout, "config", "remote.origin.fetch", f"+refs/heads/{branch}:refs/remotes/origin/{branch}")
    if assigned_skills:
        git(checkout, "submodule", "update", "--init", "--depth", "1", "--", "skills")
    audit_seed(checkout)
    return receipt


def audit_seed(checkout):
    """Fail before launch if coordinator history or unassigned files were supplied."""
    receipt = json.loads((checkout / "worker-input.json").read_text())
    parents = git(checkout, "rev-list", "--parents", "-n", "1", "HEAD").split()
    if len(parents) != 1:
        raise SystemExit("Research must start at a parentless input snapshot")
    allowed = {row["path"] for row in receipt["inputs"]} | {
        "pixi.toml", ".gitignore", ".gitattributes", "worker-input.json"}
    assigned_skills = supplied_skills(receipt)
    if assigned_skills:
        allowed |= {".gitmodules", "skills"}
        allowed |= {".agents/skills/" + name for name in assigned_skills}
    actual = {row[3] for row in entries(checkout, "HEAD", ".")}
    if actual != allowed:
        raise SystemExit("Worker tree differs from the input/resource/skill allowlist")
    if (checkout / ".git/objects/info/alternates").exists():
        raise SystemExit("Worker must have an independent Git object store")
    if not assigned_skills and any((checkout / p).exists() for p in ("skills", "assessment", ".agents/skills", ".codex/skills")):
        raise SystemExit("Worker has unassigned readable study skills before launch")
    if subprocess.run(["git", "-C", str(checkout), "diff", "--quiet", "HEAD", "--"], check=False).returncode:
        raise SystemExit("Worker inputs/resources changed after the committed seed")
    if git(checkout, "ls-files", "--others", "--exclude-standard"):
        raise SystemExit("Worker has extra untracked files before research launch")
    return receipt


def research_prompt(checkout, capture_execution=False):
    """Render retained assignment; legacy snapshots keep their original prompt."""
    receipt_path = checkout / "worker-input.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    selected = receipt.get("assignment")
    capture = (
        "For substantive analyses, capture complete command metadata, stdout/stderr, "
        "resource usage and run summaries with duct under `logs/`. "
        if capture_execution else ""
    )
    environment_policy = (
        "Keep the working `pixi.lock` ignored. Retain the exact final validated lock "
        "as ordinary Git on a separate `codex/env-<run>` branch, one commit above "
        "the final task commit; return to the task branch before finishing and "
        "report both commit IDs. "
        "Publishing your assigned task branch, its environment snapshot and annex "
        "artifacts through the configured remotes is authorized. "
        if selected else ""
    )
    common = (
        "\nCommon execution resources\n\n"
        "Use the root Pixi environment; add dependencies as needed. "
        + environment_policy +
        "Keep analysis outputs under `results/` in this experiment repository. "
        + capture +
        "Retain failed attempts and annex large outputs/logs.\n").encode()
    if selected:
        common += (
            "Keep task-specific installations local to this experiment repository; "
            "do not change shared user configuration.\n"
        ).encode()
    addition = selected["additional_prompt"] if selected else ""
    return ((checkout / "input/study-task.md").read_bytes() + common +
            (("\n" + addition + "\n").encode() if addition else b""))


NEUTRAL_PROTOCOL = "neutral-v1"
NEUTRAL_COMMON = "prompts/neutral-worker-common.md"


def _write_snapshot_file(destination, mode, content):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "120000":
        destination.symlink_to(content.decode())
    elif mode in ("100644", "100755"):
        destination.write_bytes(content)
        destination.chmod(0o755 if mode == "100755" else 0o644)
    else:
        raise SystemExit("Unsupported snapshot file mode: " + mode)


def neutral_inputs(study, revision, checkout):
    """Copy exact available scientific bytes without giving workers annex links."""
    sources = json.loads(blob(study, revision, "input/sources.json"))
    inventory = []
    for mode, kind, oid, path in entries(study, revision, "input"):
        if kind != "blob" or ".." in PurePosixPath(path).parts:
            raise SystemExit("Scientific inputs must be files below input/")
        content = blob(study, revision, path)
        row = {"path": path, "git_blob": oid, "source_mode": mode}
        if mode == "120000":
            parts = PurePosixPath(content.decode()).parts
            if not all(p in parts for p in (".git", "annex", "objects")) or parts[-1] != parts[-2]:
                raise SystemExit("Only annex links are supported in scientific inputs")
            key = parts[-1]
            try:
                location = git(study, "annex", "contentlocation", key)
            except subprocess.CalledProcessError as error:
                raise SystemExit("Materialize the pinned input before neutral launch: " + path) from error
            content = (study / location).read_bytes()
            match = re.fullmatch(r"(SHA256|MD5)E?-s([0-9]+)--([0-9a-f]+)(?:\..*)?", key)
            if not match or len(content) != int(match[2]) or hashlib.new(match[1].lower(), content).hexdigest() != match[3]:
                raise SystemExit("Materialized input differs from its original annex key: " + path)
            row["annex_key"] = key
            mode = "100644"
        expected = sources.get("files", {}).get(path.removeprefix("input/"), {})
        digest = hashlib.sha256(content).hexdigest()
        if expected.get("sha256", digest) != digest or expected.get("bytes", len(content)) != len(content):
            raise SystemExit("Input differs from the scientific source inventory: " + path)
        _write_snapshot_file(checkout / path, mode, content)
        row.update(sha256=digest, bytes=len(content), mode=mode)
        inventory.append(row)
    if not (checkout / "input/study-task.md").is_file():
        raise SystemExit("Scientific task is missing")
    return inventory


def snapshot_research_skills(source, revision, destination):
    """Keep full sibling skill directories, without repository/evaluation history."""
    files = []
    for mode, kind, oid, path in entries(source, revision, "skills"):
        if kind != "blob":
            raise SystemExit("Research skill snapshot cannot contain submodules")
        relative = Path(path).relative_to("skills")
        target = destination / relative
        content = blob(source, revision, path)
        _write_snapshot_file(target, mode, content)
        files.append({"path": relative.as_posix(), "mode": mode, "git_blob": oid,
                      "sha256": hashlib.sha256(content).hexdigest()})
    for row in files:
        target = destination / row["path"]
        if target.is_symlink() and not target.resolve().is_relative_to(destination.resolve()):
            raise SystemExit("Skill snapshot link escapes the pinned skill directories")
    return files


def make_neutral_seed(repo, base, study, checkout, branch, condition, provenance,
                      receipt_path, common_resources, skills_source=None):
    """Seed native capture with materialized inputs; all assignment data is external."""
    checkout, receipt_path = Path(checkout).resolve(), Path(receipt_path).resolve()
    resources = Path(common_resources).resolve()
    if receipt_path.is_relative_to(checkout) or resources.is_relative_to(checkout):
        raise SystemExit("Neutral assignment and common resources must stay outside the worker")
    if checkout.exists() or receipt_path.exists():
        raise SystemExit("Neutral seed destination exists; preserve the earlier attempt")
    if any(label in branch.lower() for label in ("baseline", "discover-general", "discover-science", "stamped-explicit")):
        raise SystemExit("Neutral worker branch must not encode its assigned condition")
    study_path, revision = study_pin(repo, base, study)
    selected = assignment(blob(repo, base, "conditions.json"), condition)
    checkout.mkdir(parents=True)
    git(checkout, "init", "--template=", "-b", branch)
    git(checkout, "config", "core.hooksPath", str(checkout / ".git/hooks"))
    (checkout / ".git/hooks").mkdir(exist_ok=True)
    (checkout / ".git/info").mkdir(exist_ok=True)
    (checkout / ".git/info/exclude").write_text(".codex/hooks.json\n.entire/\n")
    inventory = neutral_inputs(study, revision, checkout)
    annexed = [row for row in inventory if "annex_key" in row]
    if annexed:
        # This supplies input storage only. Do not create an output policy or
        # ask workers to use annex for their own artifacts.
        git(checkout, "annex", "init", "coordinator-supplied-inputs")
        for row in annexed:
            backend = row["annex_key"].split("-", 1)[0]
            git(checkout, "annex", "add", "--force", "--backend=" + backend, "--", row["path"])
            if git(checkout, "annex", "lookupkey", row["path"]) != row["annex_key"]:
                raise SystemExit("Supplied input annex identity changed: " + row["path"])
            row.update(mode="120000", link_target=os.readlink(checkout / row["path"]),
                       storage_attribution="coordinator-supplied-input")
    git(checkout, "add", "--", "input")
    trailers = subprocess.check_output([str(provenance)], text=True).strip()
    git(checkout, "commit", "-m", "chore(study): supply materialized scientific inputs\n\n" + trailers)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    common = blob(repo, base, NEUTRAL_COMMON)
    resource_bytes = resources.read_bytes()
    receipt = {"version": 3, "protocol": NEUTRAL_PROTOCOL, "coordinator_commit": base,
               "study_path": study_path, "study_commit": revision,
               "study_input_tree": git(study, "rev-parse", revision + ":input"),
               "condition": selected["condition"], "assignment": selected,
               "run": branch.removeprefix("codex/"), "seed_commit": git(checkout, "rev-parse", "HEAD"),
               "inputs": inventory, "supplied_files": list(inventory),
               "common_prompt": common.decode(), "common_prompt_sha256": hashlib.sha256(common).hexdigest(),
               "common_resources": resource_bytes.decode(),
               "common_resources_sha256": hashlib.sha256(resource_bytes).hexdigest()}
    if supplied_skills(receipt):
        source = Path(skills_source) if skills_source else repo / "skills"
        revision = git(repo, "rev-parse", base + ":skills")
        destination = receipt_path.parent / "research-skills"
        destination.mkdir()
        receipt.update(skills_commit=revision, skills_directory=str(destination),
                       skill_files=snapshot_research_skills(source, revision, destination))
        for name in supplied_skills(receipt):
            if not (destination / name / "SKILL.md").is_file():
                raise SystemExit("Missing supplied research skill: " + name)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    audit_neutral_seed(checkout, receipt_path)
    return receipt


def _neutral_visible_files(checkout):
    return {p.relative_to(checkout).as_posix(): p for p in checkout.rglob("*")
            if p.relative_to(checkout).parts[0] != ".git" and (p.is_file() or p.is_symlink())}


def retain_neutral_preparation(checkout, receipt_path):
    """Record native coordinator configuration as supplied, never worker-created."""
    receipt = json.loads(receipt_path.read_text())
    supplied = {row["path"] for row in receipt["supplied_files"]}
    for name, path in _neutral_visible_files(checkout).items():
        if name in supplied:
            continue
        if not name.startswith((".codex/", ".entire/")) or path.is_symlink():
            raise SystemExit("Unexpected file introduced during neutral native preparation: " + name)
        content = path.read_bytes()
        receipt["supplied_files"].append({"path": name, "sha256": hashlib.sha256(content).hexdigest(),
                                        "bytes": len(content), "mode": "100644",
                                        "source": "coordinator-native-preparation"})
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    return audit_neutral_seed(checkout, receipt_path)


def audit_neutral_seed(checkout, receipt_path):
    receipt = json.loads(Path(receipt_path).read_text())
    if receipt.get("version") != 3 or receipt.get("protocol") != NEUTRAL_PROTOCOL:
        raise SystemExit("Unsupported neutral input receipt")
    if Path(receipt_path).resolve().is_relative_to(checkout.resolve()):
        raise SystemExit("Neutral assignment receipt is inside the worker")
    if git(checkout, "rev-parse", "HEAD") != receipt["seed_commit"]:
        raise SystemExit("Neutral input seed commit changed")
    if git(checkout, "rev-list", "--parents", "-n", "1", "HEAD").split() != [receipt["seed_commit"]]:
        raise SystemExit("Neutral input seed must have no parent history")
    if (checkout / ".git/objects/info/alternates").exists():
        raise SystemExit("Neutral worker shares a Git object store")
    expected = {row["path"]: row for row in receipt["supplied_files"]}
    visible = _neutral_visible_files(checkout)
    if set(visible) != set(expected):
        raise SystemExit("Neutral worker contains files outside the supplied input/config boundary")
    for name, path in visible.items():
        row = expected[name]
        if path.is_symlink() and (not row.get("annex_key") or
                os.readlink(path) != row.get("link_target") or
                not path.resolve().is_relative_to((checkout / ".git/annex/objects").resolve())):
            raise SystemExit("Neutral supplied input link changed: " + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise SystemExit("Neutral supplied bytes changed: " + name)
    for row in receipt.get("skill_files", []):
        path = Path(receipt["skills_directory"]) / row["path"]
        data = os.readlink(path).encode() if row["mode"] == "120000" else path.read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise SystemExit("Supplied research skill bytes changed")
    return receipt


def neutral_research_prompt(checkout, receipt_path):
    receipt = json.loads(Path(receipt_path).read_text())
    common = receipt["common_prompt"].replace("$COMMON_RESOURCES", receipt["common_resources"])
    addition = receipt["assignment"]["additional_prompt"]
    return ((checkout / "input/study-task.md").read_bytes() + b"\n" + common.encode() +
            (("\n" + addition + "\n").encode() if addition else b""))
