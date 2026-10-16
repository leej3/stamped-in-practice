"""Sequential local packaging, retaining every command and any failed attempt."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import traceback
import package

BASE = Path("/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1")
NATIVE = BASE / "operational-native-publication-01"
TOOLS = Path(__file__).parent
OUT = BASE / "operational-support-packages-02"
RECON_SHA = "48aeb68956a5bb3a189b863ce4eb066d475b1cabff51736c1efef25a4eefd3dd"
PENDING_SHA = "3dd520fd12227f51ec2d847089dc944456fd1244050ab5b2784ce2d0709167dc"


def main():
    OUT.mkdir(exist_ok=False)
    commands = OUT / "commands"
    commands.mkdir()
    recon_path = NATIVE / "final-git-reconciliation.json"
    pending_path = NATIVE / "final-pending-hub-payloads.json"
    package.require(package.sha(recon_path) == RECON_SHA, "Reconciliation changed")
    package.require(package.sha(pending_path) == PENDING_SHA, "Pending inventory changed")
    package.require(package.sha(TOOLS / recon_path.name) == RECON_SHA,
                    "Reconciliation snapshot differs")
    package.require(package.sha(TOOLS / pending_path.name) == PENDING_SHA,
                    "Pending inventory snapshot differs")
    recon = json.loads(recon_path.read_text())
    records = [record for record in recon["records"]
               if not record["fully_verified_hub_publication"]]
    package.require(len(records) == 27 and len(recon["records"]) == 32,
                    "Unexpected slot counts")
    old_before = package.inventory(BASE / "operational-support-packages-01", [])
    package.save(OUT / "existing-packages-before.json", old_before)
    package.save(OUT / "run-intent.json", {
        "started_at": package.now(), "argv": sys.argv,
        "method_sha256": package.sha(Path(__file__)),
        "package_method_sha256": package.sha(TOOLS / "package.py"),
        "safe_file_method_sha256": package.sha(TOOLS / "package_delivery.py"),
        "reconciliation_sha256": RECON_SHA, "pending_inventory_sha256": PENDING_SHA,
        "free_bytes_before": shutil.disk_usage(BASE).free,
        "slot_order": [record["slot"] for record in records],
        "operation": "sequential_local_archive_only", "remote_completion": False})
    completed = []
    for record in records:
        slot = record["slot"]
        command_dir = commands / slot
        command_dir.mkdir()
        for name in ("package.py", "package_delivery.py", "run.py"):
            shutil.copy2(TOOLS / name, command_dir / name)
        index = Path(record["closed_local_bundle"]["path"])
        package.require(package.sha(index) == record["closed_local_bundle"]["sha256"],
                        "Reconciliation index changed: " + slot)
        package.require(index.stat().st_size == record["closed_local_bundle"]["bytes"],
                        "Reconciliation index size changed: " + slot)
        command = [sys.executable, str(command_dir / "package.py"),
                   str(NATIVE / "judgments" / slot), str(index), str(OUT / slot),
                   "--expected-index-sha256", record["closed_local_bundle"]["sha256"],
                   "--expected-proof-commit", record["proof_commit"]]
        package.save(command_dir / "command.json", {
            "started_at": package.now(), "argv": command,
            "cwd": str(TOOLS), "free_bytes_before": shutil.disk_usage(BASE).free})
        print(json.dumps({"state": "starting", "slot": slot,
                          "completed": len(completed), "total": len(records)}), flush=True)
        with (command_dir / "stdout").open("xb") as stdout, (
                command_dir / "stderr").open("xb") as stderr:
            process = subprocess.run(command, cwd=TOOLS, stdout=stdout, stderr=stderr)
        package.save(command_dir / "result.json", {
            "completed_at": package.now(), "returncode": process.returncode,
            "stdout_sha256": package.sha(command_dir / "stdout"),
            "stderr_sha256": package.sha(command_dir / "stderr")})
        package.require(process.returncode == 0,
                        "Package failed; attempt retained: " + slot)
        result_path = OUT / slot / "package-verification.json"
        result = json.loads(result_path.read_text())
        package.require(result["verified"] and not result["remote_completion"],
                        "Unexpected verification result")
        completed.append({"slot": slot, "package": str(OUT / slot),
                          "receipt_sha256": package.sha(result_path), **result})
        print(json.dumps({"state": "verified", "slot": slot,
                          "archive_bytes": result["archive_bytes"],
                          "completed": len(completed), "total": len(records)}), flush=True)
    package.require(old_before == package.inventory(
        BASE / "operational-support-packages-01", []), "Existing five packages changed")
    package.require(package.sha(recon_path) == RECON_SHA, "Reconciliation changed")
    package.require(package.sha(pending_path) == PENDING_SHA, "Pending inventory changed")
    package.save(OUT / "result.json", {
        "schema": "operational-support-local-package-series-v2",
        "completed_at": package.now(), "verified_packages": len(completed),
        "archive_bytes": sum(record["archive_bytes"] for record in completed),
        "regular_file_bytes": sum(record["regular_file_bytes"] for record in completed),
        "source_regular_file_bytes": sum(record["source_regular_file_bytes"]
                                         for record in completed),
        "members": sum(record["members"] for record in completed),
        "source_members": sum(record["source_members"] for record in completed),
        "external_closure_members": sum(record["external_closure_members"]
                                        for record in completed),
        "existing_five_packages_unchanged": True,
        "existing_packages_inventory_sha256": package.sha(
            OUT / "existing-packages-before.json"),
        "final_reconciliation_unchanged": True, "pending_hub_inventory_unchanged": True,
        "reconciliation_sha256": RECON_SHA, "pending_inventory_sha256": PENDING_SHA,
        "free_bytes_after": shutil.disk_usage(BASE).free,
        "remote_completion": False, "hub_transfers_held": True,
        "publication": "Not attempted. Complete local support archives remain pending "
                       "upload and independent retrieval; prior Git stages unchanged.",
        "records": completed})
    print(json.dumps({"state": "complete", "verified_packages": len(completed),
                      "result_sha256": package.sha(OUT / "result.json"),
                      "archive_bytes": sum(record["archive_bytes"]
                                           for record in completed)}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        failure = OUT / "failure.json"
        if OUT.exists() and not failure.exists():
            package.save(failure, {"failed_at": package.now(),
                                   "traceback": traceback.format_exc(),
                                   "remote_completion": False,
                                   "retention": "All existing attempts and outputs retained."})
        raise
