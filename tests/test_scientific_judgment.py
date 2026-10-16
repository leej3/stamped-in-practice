import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scientific_judgment import ADEQUACY, parse_record, validate_record


CAPTURE = "a" * 64


def prepare(tmp_path, category="supported"):
    # Adequacy and the scientific hypothesis can legitimately differ.
    report = "# Scientific assessment\nThe positive hypothesis is not supported.\nThe checks support the bounded interpretation.\n"
    (tmp_path / "report.md").write_text(report)
    record = {
        "schema_version": 1, "delivery_capture_sha256": CAPTURE,
        "scientific_adequacy": category,
        "report": {"path": "report.md", "sha256": hashlib.sha256(report.encode()).hexdigest()},
        "adequacy_evidence": {"quote": "The checks support the bounded interpretation.",
                              "start_line": 3, "end_line": 3},
        "hypothesis_conclusion": {"quote": "The positive hypothesis is not supported.",
                                  "start_line": 2, "end_line": 2},
    }
    path = tmp_path / "scientific-judgment.json"
    path.write_text(json.dumps(record))
    return path, record


@pytest.mark.parametrize("category", ADEQUACY)
def test_explicit_category_and_verbatim_hypothesis_remain_separate(tmp_path, category):
    path, record = prepare(tmp_path, category)
    result = validate_record(path, tmp_path, CAPTURE)
    assert result["adequacy"]["category"] == category
    assert result["conclusion"] == record["hypothesis_conclusion"]
    assert result["structured_scientific"]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_null_conclusion_is_not_inferred(tmp_path):
    path, record = prepare(tmp_path)
    record["hypothesis_conclusion"] = None
    path.write_text(json.dumps(record))
    assert "conclusion" not in validate_record(path, tmp_path, CAPTURE)


@pytest.mark.parametrize("change,match", [
    (lambda r: r.update(delivery_capture_sha256="b" * 64), "different original"),
    (lambda r: r["report"].update(sha256="b" * 64), "report hash"),
    (lambda r: r.update(scientific_adequacy="positive result"), "Invalid scientific"),
    (lambda r: r["adequacy_evidence"].update(start_line=2, end_line=2), "cited report lines"),
    (lambda r: r["adequacy_evidence"].update(quote="Invented rationale"), "cited report lines"),
    (lambda r: r["hypothesis_conclusion"].update(end_line=200), "line range"),
    (lambda r: r["report"].update(path="../report.md"), "inside the judge"),
])
def test_invalid_bindings_reject(tmp_path, change, match):
    path, record = prepare(tmp_path)
    change(record)
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match=match):
        validate_record(path, tmp_path, CAPTURE)


def test_duplicate_fields_reject(tmp_path):
    path, _ = prepare(tmp_path)
    raw = path.read_text().replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        parse_record(raw)


@pytest.mark.parametrize("excerpt", ["adequacy_evidence", "hypothesis_conclusion"])
@pytest.mark.parametrize("field", ["start_line", "end_line"])
def test_decimal_line_numbers_have_a_clear_validation_error(tmp_path, excerpt, field):
    path, record = prepare(tmp_path)
    record[excerpt][field] = float(record[excerpt][field])
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="JSON integer notation"):
        validate_record(path, tmp_path, CAPTURE)


def test_symlinked_report_or_record_reject(tmp_path):
    path, record = prepare(tmp_path)
    (tmp_path / "alias.md").symlink_to("report.md")
    record["report"]["path"] = "alias.md"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="symlinks"):
        validate_record(path, tmp_path, CAPTURE)
    alias = tmp_path / "alias.json"
    alias.symlink_to(path.name)
    with pytest.raises(ValueError, match="symlinks"):
        validate_record(alias, tmp_path, CAPTURE)


def test_changed_report_rejects_even_with_the_same_quoted_text(tmp_path):
    path, _ = prepare(tmp_path)
    with (tmp_path / "report.md").open("a") as stream:
        stream.write("An unbound later revision.\n")
    with pytest.raises(ValueError, match="report hash"):
        validate_record(path, tmp_path, CAPTURE)
