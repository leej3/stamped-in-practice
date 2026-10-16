"""Capture local repair commands without executing native models or duct."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
label, *command = sys.argv[1:]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
log = root / (label + ".log")
log.write_bytes(result.stdout)
record = {"command": command, "cwd": str(Path.cwd()), "started_at": started,
          "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "returncode": result.returncode, "log": str(log)}
(root / (label + ".json")).write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
print(result.stdout.decode(errors="replace"))
raise SystemExit(result.returncode)
