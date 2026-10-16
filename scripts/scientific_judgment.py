"""Validate an explicit scientific judgment without interpreting its prose."""
import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ADEQUACY = ("supported", "qualified", "not supported", "unable to assess")
SHA256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
TEXT = {"type": "string", "minLength": 1}


def object_schema(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


EXCERPT = object_schema({
    "quote": TEXT,
    "start_line": {"type": "integer", "minimum": 1},
    "end_line": {"type": "integer", "minimum": 1},
})
SCHEMA = object_schema({
    "schema_version": {"const": 1, "type": "integer"},
    "delivery_capture_sha256": SHA256,
    "scientific_adequacy": {"enum": list(ADEQUACY)},
    "report": object_schema({"path": TEXT, "sha256": SHA256}),
    "adequacy_evidence": EXCERPT,
    "hypothesis_conclusion": {"anyOf": [EXCERPT, {"type": "null"}]},
})
SCHEMA["$schema"] = "https://json-schema.org/draft/2020-12/schema"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_record(data):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("Nonfinite JSON value: " + value)

    value = json.loads(data, object_pairs_hook=unique_pairs,
                       parse_constant=invalid_constant)
    errors = list(Draft202012Validator(SCHEMA).iter_errors(value))
    if errors:
        raise ValueError("Invalid scientific judgment: " + "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '(root)'}: {error.message}"
            for error in errors))
    return value


def workspace_file(workspace, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Judgment artifacts must use paths inside the judge workspace")
    current = workspace
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Judgment artifacts must not use symlinks")
    if not current.is_file():
        raise ValueError("Judgment artifact is not a regular file: " + str(path))
    return current


def validate_excerpt(excerpt, report):
    """Bind a literal text quote to one-based physical report lines."""
    lines = report.splitlines()
    start, end = excerpt["start_line"], excerpt["end_line"]
    if type(start) is not int or type(end) is not int:
        raise ValueError("Excerpt line numbers must use JSON integer notation")
    if not 1 <= start <= end <= len(lines):
        raise ValueError("Excerpt line range is outside the report")
    context = "\n".join(lines[start - 1:end])
    if excerpt["quote"] not in context:
        raise ValueError("Excerpt quote does not occur in its cited report lines")


def validate_record(record_path, workspace, capture_sha256):
    """Return aggregation fields bound to the record, report and original capture.

    The judge's explicit category is authoritative. Neither the category nor a
    hypothesis conclusion is inferred from the narrative. Older assessment
    versions retain their existing extraction procedure.
    """
    workspace = Path(workspace).resolve(strict=True)
    path = Path(record_path)
    if path.is_absolute():
        try:
            path = path.relative_to(workspace)
        except ValueError as error:
            raise ValueError("Scientific record is outside the judge workspace") from error
    path = workspace_file(workspace, path)
    raw = path.read_bytes()
    record = parse_record(raw)
    if record["delivery_capture_sha256"] != capture_sha256:
        raise ValueError("Scientific judgment names a different original delivery capture")
    report_path = workspace_file(workspace, record["report"]["path"])
    report_raw = report_path.read_bytes()
    if digest(report_raw) != record["report"]["sha256"]:
        raise ValueError("Scientific report hash differs from the explicit judgment")
    report = report_raw.decode("utf-8")
    validate_excerpt(record["adequacy_evidence"], report)
    conclusion = record["hypothesis_conclusion"]
    if conclusion is not None:
        validate_excerpt(conclusion, report)
    fields = {
        "structured_scientific": {"path": str(path), "sha256": digest(raw)},
        "scientific_report": {"path": str(report_path), "sha256": digest(report_raw)},
        "adequacy": {"extraction_status": "explicit",
                     "category": record["scientific_adequacy"],
                     "excerpt": record["adequacy_evidence"]},
    }
    if conclusion is not None:
        fields["conclusion"] = conclusion
    return fields


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("schema", help="Print the exact required record schema")
    check = subparsers.add_parser("validate", help="Validate a judge-authored record")
    check.add_argument("record", type=Path)
    check.add_argument("--workspace", type=Path, default=Path.cwd())
    identity = check.add_mutually_exclusive_group(required=True)
    identity.add_argument("--delivery-manifest", type=Path)
    identity.add_argument("--capture-sha256")
    args = parser.parse_args()
    if args.command == "schema":
        result = SCHEMA
    else:
        capture = (digest(args.delivery_manifest.read_bytes()) if args.delivery_manifest
                   else args.capture_sha256)
        result = validate_record(args.record, args.workspace, capture)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
