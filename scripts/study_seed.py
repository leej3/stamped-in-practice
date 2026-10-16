"""Export committed study inputs into a parentless, independent Git object store."""
import hashlib
import json
import os
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
