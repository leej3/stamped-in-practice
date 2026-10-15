"""Retrieve or verify the frozen NARPS package without regenerating inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def run(*args, capture=False):
    result = subprocess.run(args, cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def mirror(contract):
    run("git", "annex", "init", "NARPS formal study")
    remote = contract["remote_name"]
    if remote not in run("git", "remote", capture=True).splitlines():
        run("git", "remote", "add", remote, contract["git_url"])
    require(run("git", "remote", "get-url", remote, capture=True) == contract["git_url"],
            "Existing CON Hub remote differs from retrieval.json")
    key = "remote." + remote + ".annexurl"
    current = subprocess.run(["git", "config", "--get", key], cwd=ROOT,
                             text=True, capture_output=True)
    require(current.returncode in (0, 1) and
            (current.returncode == 1 or current.stdout.strip() == contract["annex_url"]),
            "Existing CON Hub annex endpoint differs from retrieval.json")
    run("git", "config", key, contract["annex_url"])
    run("git", "config", "remote." + remote + ".skipFetchAll", "true")
    run("git", "annex", "info", remote, "--json", capture=True)
    require(run("git", "config", "--get", "remote." + remote + ".annex-uuid",
                capture=True) == contract["remote_uuid"], "Unexpected CON Hub annex UUID")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--metadata-only", action="store_true")
    modes.add_argument("--verify-only", action="store_true")
    parser.add_argument("--path", action="append", help="Input-relative map path; repeat to select maps")
    args = parser.parse_args()
    package = ROOT / "input"
    source = json.loads((ROOT / "source-version.json").read_text())
    require(digest(package / "sources.json") == source["input_sources_sha256"],
            "Frozen input source manifest differs")
    manifest = json.loads((package / "sources.json").read_text())
    contract = json.loads((ROOT / "retrieval.json").read_text())
    maps = {item["path"].removeprefix("input/"): item for item in contract["files"]}
    expected_maps = {name for name in manifest["files"] if name.endswith(".nii.gz")}
    require(set(maps) == expected_maps and len(maps) == 54, "Expected exactly 54 declared maps")
    inventory = {str(path.relative_to(package)) for path in package.rglob("*")
                 if path.is_symlink() or path.is_file()}
    require(inventory == set(manifest["files"]) | {"sources.json"}, "Input inventory differs")
    for name, item in maps.items():
        path = package / name
        require(path.is_symlink() and path.readlink().name == item["annex_key"],
                "Frozen annex link differs: " + name)
        require(all(item[key] == manifest["files"][name][key] for key in ("sha256", "bytes")),
                "Retrieval manifest differs: " + name)
        require(item["upstream_url"] == manifest["files"][name]["url"],
                "Upstream input URL differs: " + name)
    selected = set(args.path) if args.path else set(maps)
    require(selected <= set(maps), "Select input-relative map paths from input/sources.json")
    missing = [name for name in sorted(selected) if not (package / name).is_file()]
    if missing and not (args.metadata_only or args.verify_only):
        mirror(contract)
        for name in missing:
            key = maps[name]["annex_key"]
            # Direct transfer works without importing the old annex location history.
            run("git", "annex", "transferkey", key, "--from", contract["remote_name"])
            run("git", "annex", "setpresentkey", key, contract["remote_uuid"], "1")
    verify = set(manifest["files"]) - set(maps)
    if not args.metadata_only:
        verify |= selected
    for name in sorted(verify):
        path, expected = package / name, manifest["files"][name]
        require(path.is_file(), "Missing payload; run pixi run get-input: " + name)
        require(path.stat().st_size == expected["bytes"] and digest(path) == expected["sha256"],
                "Input content differs: " + name)
    print(json.dumps({"input_tree": source["input_tree"], "annex_links_checked": len(maps),
                      "payloads_verified": 0 if args.metadata_only else len(selected),
                      "regular_files_verified": len(set(manifest["files"]) - set(maps)),
                      "scientific_analysis_executed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
