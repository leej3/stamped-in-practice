"""Read-only verification of trial evidence; writes only into this review folder."""
from pathlib import Path
from collections import Counter
import base64
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from urllib.parse import parse_qs, urlparse

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
TRIAL = BASE / "alignment-trial-01"
PROJECT = TRIAL / "project"
EVIDENCE = TRIAL / "evidence"
SKILLS = TRIAL / "skills"
commands = json.loads((OUT / "commands.json").read_text()) if (OUT / "commands.json").exists() else []
if (OUT / "checks.json").exists():
    (OUT / "checks-first-host-python-attempt.json").write_bytes((OUT / "checks.json").read_bytes())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def data(path):
    return json.loads(path.read_text())

def run(argv):
    result = subprocess.run(argv, capture_output=True, text=True,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                                 "GIT_OPTIONAL_LOCKS": "0"})
    record = {"argv": list(map(str, argv)), "exit_code": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    commands.append(record)
    return record

checks = {}
ready = data(BASE / "alignment-ready-state.json")
before = data(EVIDENCE / "before-manifest.json")
after = data(EVIDENCE / "after-manifest.json")
before_map = {x["path"]: x["sha256"] for x in before["files"]}
after_map = {x["path"]: x["sha256"] for x in after["files"]}
checks["ready_equals_before_manifest"] = ready["files"] == before_map
checks["ready_prompt_hash_matches"] = ready["prompt_sha256"] == digest(BASE / "alignment-trial-prompt.txt")
invocation = data(BASE / "alignment-invocation.json")
checks["invocation_message_hash_matches"] = invocation["message_sha256"] == hashlib.sha256(invocation["message"].encode()).hexdigest()
checks["invocation_equals_prompt_except_trailing_newline"] = invocation["message"].rstrip("\n") == (BASE / "alignment-trial-prompt.txt").read_text().rstrip("\n")
checks["project_manifest_mismatches"] = [name for name, expected in after_map.items()
    if not (PROJECT / name).is_file() or digest(PROJECT / name) != expected]
actual_files = {str(p.relative_to(PROJECT)) for p in PROJECT.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(PROJECT).parts}
checks["project_file_count"] = len(actual_files)
checks["unmanifested_project_files"] = sorted(actual_files - after_map.keys())
checks["preserved_supplied_scientific_files"] = {name: digest(PROJECT / name) == before_map[name]
    for name in ["input/paired-assay.csv", "code/analyze.py", "results/summary.csv", "figures/paired-assay.png", "REPORT.md"]}
checks["changed_original_files"] = [name for name, h in before_map.items() if digest(PROJECT / name) != h]
checks["before_copy_mismatches"] = [name for name, h in before_map.items() if digest(EVIDENCE / "before-delivery" / name) != h]
for label, manifest in [("before", before_map), ("after", after_map)]:
    with tarfile.open(EVIDENCE / (label + "-delivery.tar.gz")) as archive:
        archive_map = {m.name.removeprefix("./"): hashlib.sha256(archive.extractfile(m).read()).hexdigest()
                       for m in archive.getmembers() if m.isfile()}
    checks[label + "_archive_matches_manifest"] = archive_map == manifest

snapshot = data(BASE / "alignment-skill-snapshot.json")["files"]
captured_snapshot = {x["path"]: x["sha256"] for x in data(EVIDENCE / "skill-snapshot-manifest.json")["files"]}
checks["skill_snapshot_inventory_equal"] = snapshot == captured_snapshot
checks["skill_snapshot_mismatches"] = [name for name, h in snapshot.items() if digest(SKILLS / name) != h]
checks["git_head"] = run(["git", "-C", str(PROJECT), "rev-parse", "HEAD"])["stdout"].strip()
checks["git_status"] = run(["git", "-C", str(PROJECT), "status", "--short"])["stdout"]
checks["git_status_equals_after_manifest"] = checks["git_status"] == after["git_status"]
tracked = run(["git", "-C", str(PROJECT), "ls-tree", "-r", "--name-only", "HEAD"])["stdout"].splitlines()
checks["baseline_tracked_content_matches_before"] = {}
for name in tracked:
    result = subprocess.run(["git", "-C", str(PROJECT), "show", "HEAD:" + name], capture_output=True)
    commands.append({"argv": ["git", "-C", str(PROJECT), "show", "HEAD:" + name],
                     "exit_code": result.returncode, "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
                     "stderr": result.stderr.decode()})
    checks["baseline_tracked_content_matches_before"][name] = hashlib.sha256(result.stdout).hexdigest() == before_map[name]
checks["runs"] = {}
fresh = data(EVIDENCE / "2026-10-16-2-fresh-rerun.json")
for index, name in enumerate(["verification-20261016", "supplied-environment-20261016"]):
    directory = PROJECT / "runs" / name
    receipt = data(directory / "run.json")
    checks["runs"][name] = {
        "receipt_matches_fresh_rerun_report": receipt == fresh["runs"][index],
        "analysis_exit_code": receipt["analysis_exit_code"],
        "verification_exit_code": receipt["verification_exit_code"],
        "snapshot_mismatches": [n for n, h in receipt["source_sha256"].items() if digest(directory / "source" / n) != h],
        "source_mismatches": [n for n, h in receipt["source_sha256"].items() if digest(PROJECT / n) != h],
        "output_mismatches": [n for n, h in receipt["output_sha256"].items() if digest(directory / n) != h],
        "csv_byte_identical_to_supplied": (directory / "results/summary.csv").read_bytes() == (PROJECT / "results/summary.csv").read_bytes(),
        "png_byte_identical_to_supplied": (directory / "figures/paired-assay.png").read_bytes() == (PROJECT / "figures/paired-assay.png").read_bytes(),
        "command": receipt["command"],
        "environment": receipt["environment"],
    }
responses = []
checks["responses"] = {}
encoder = SKILLS / "stamped-conventions/scripts/encode_response.py"
for stem in ["2026-10-16", "2026-10-16-2"]:
    response_path = EVIDENCE / (stem + "-response.json")
    response = data(response_path)
    responses.append(response)
    record = run([sys.executable, "-B", str(encoder), "validate", str(response_path)])
    missing_evidence = []
    for key, item in response["responses"].items():
        for ev in item.get("evidence", []):
            if ev["uri"].startswith("/") and not Path(ev["uri"].split("#")[0]).exists():
                missing_evidence.append([key, ev["uri"]])
    encoded = run([sys.executable, "-B", str(encoder), "encode", str(response_path)])
    table = run([sys.executable, "-B", str(encoder), "table", str(response_path)])
    checks["responses"][stem] = {
        "answer_count": len(response["responses"]),
        "validator_exit_code": record["exit_code"], "validator_stdout": record["stdout"],
        "capture_hash_matches": digest(Path(response["object"]["capture"]["uri"])) == response["object"]["capture"]["sha256"],
        "counts_by_category": {cat: dict(Counter(v["status"] for k, v in response["responses"].items() if k.startswith("stamped-checklist:" + cat + "/"))) for cat in ["must", "should", "may"]},
        "missing_evidence_paths": missing_evidence,
        "regenerated_url_equals_supplied": encoded["stdout"].strip() == (EVIDENCE / (stem + "-url.txt")).read_text().strip(),
        "regenerated_table_equals_supplied": table["stdout"].strip() == (EVIDENCE / (stem + "-table.md")).read_text().strip(),
    }
changes = {k: [v["status"], responses[1]["responses"][k]["status"]]
           for k, v in responses[0]["responses"].items() if v["status"] != responses[1]["responses"][k]["status"]}
checks["response_changes"] = changes
checks["recorded_changes_match"] = changes == {x["item"]: [x["before"], x["after"]] for x in data(EVIDENCE / "item-differences.json")}
checks["rebuilt_lock_byte_equal"] = (EVIDENCE / "rebuilt-requirements.lock.txt").read_bytes() == (PROJECT / "requirements.lock.txt").read_bytes()
try:
    from PIL import Image, ImageChops
    supplied_image = Image.open(PROJECT / "figures/paired-assay.png").convert("RGBA")
    checks["pixels"] = {}
    for name in checks["runs"]:
        generated = Image.open(PROJECT / "runs" / name / "figures/paired-assay.png").convert("RGBA")
        checks["pixels"][name] = {"supplied_size": supplied_image.size, "generated_size": generated.size,
            "pixels_equal": supplied_image.tobytes() == generated.tobytes(),
            "different_pixels": sum(a != b for a, b in zip(supplied_image.getdata(), generated.getdata()))}
except ImportError as error:
    checks["pixels"] = {"review_environment_limit": str(error)}
checks["retained_venv_metadata"] = run([str(EVIDENCE / "verification-venv/bin/python"), "-B", "-c",
    "import sys,json,importlib.metadata; print(json.dumps({'executable':sys.executable,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'packages':{n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','matplotlib']}}))"])
checks["checklist_pin_validation"] = run([sys.executable, "-B", str(SKILLS / "stamped-conventions/scripts/vendor_checklist.py"), "--check"])
sources = [BASE / name for name in ["alignment-ready-state.json", "alignment-skill-snapshot.json", "alignment-invocation.json", "alignment-trial-prompt.txt"]]
sources += sorted(p for p in EVIDENCE.iterdir() if p.is_file())
sources += [PROJECT / name for name in after_map]
sources += [SKILLS / name for name in snapshot]
sources += [EVIDENCE / "verification-venv/pyvenv.cfg"]
source_hashes = {str(p.relative_to(BASE)): {"sha256": digest(p), "size": p.stat().st_size} for p in sources}
(OUT / "source-hashes.json").write_text(json.dumps(source_hashes, indent=2) + "\n")
(OUT / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
(OUT / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
print(json.dumps(checks, indent=2))
