"""Check the committed design package, without network or imaging computation."""
import csv
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sources = json.loads((root / "input/sources.json").read_text())
ready = json.loads((root / "coordinator-guidance/readiness.json").read_text())
assert ready["ready"] is False, "Replace this design check when validating readiness"
assert sources["payload_retrieval_verified"] is False
for item in sources["dataset"]["metadata"]:
    payload = (root / "input" / item["path"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == item["sha256"], item["path"]
subjects = sources["dataset"]["subjects"]
images = sources["dataset"]["images"]
assert len(images) == len(subjects) * 3
assert len({x["path"] for x in images}) == len(images)
for image in images:
    assert image["annex_key"].startswith(("MD5E-", "SHA256E-"))
for subject in subjects:
    for run in sources["dataset"]["runs"]:
        path = root / f"input/upstream/sub-{subject}/func/sub-{subject}_task-flanker_run-{run}_events.tsv"
        rows = list(csv.DictReader(path.open(), delimiter="\t"))
        assert rows and all(float(r["duration"]) >= 0 for r in rows)
        assert all(float(r["onset"]) >= 0 for r in rows)
        assert {"congruent_correct", "incongruent_correct"} <= {r["trial_type"] for r in rows}
print(json.dumps({"design_consistent": True, "images_identified": len(images),
                  "subjects": subjects, "launch_ready": False,
                  "payload_retrieval_checked": False}))
