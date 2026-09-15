import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from audit import build_audit_record, build_findings, append_audit_record
from evidence import MODEL
from policy import POLICY_VERSION

RESULTS = [
    {"criterion_id": "A", "status": "satisfied", "page_number": 1, "quote": "q", "concern_present": None},
]
DECISION = {"decision": "approve", "reasons": []}


def test_build_audit_record_has_expected_fields():
    record = build_audit_record("samples/sample.pdf", RESULTS, DECISION)

    assert record["case"] == "samples/sample.pdf"
    assert record["actor"] == "rule_engine"
    assert record["model"] == MODEL
    assert record["policy_version"] == POLICY_VERSION
    assert record["results"] == RESULTS
    assert record["findings"] == []
    assert record["decision"] == "approve"
    assert record["reasons"] == []
    assert record["event_id"].startswith("evt_")
    assert "timestamp" in record


def test_build_audit_record_event_ids_are_unique():
    record_1 = build_audit_record("samples/sample.pdf", RESULTS, DECISION)
    record_2 = build_audit_record("samples/sample.pdf", RESULTS, DECISION)
    assert record_1["event_id"] != record_2["event_id"]


def test_build_findings_severity_by_status():
    results = [
        {"criterion_id": "A", "status": "satisfied", "page_number": 1, "quote": "q", "concern_present": None},
        {"criterion_id": "B", "status": "not_found", "page_number": None, "quote": None, "concern_present": None},
        {"criterion_id": "C", "status": "unknown", "page_number": 2, "quote": "q2", "concern_present": None},
        {"criterion_id": "D", "status": "satisfied", "page_number": 3, "quote": "q3", "concern_present": True},
    ]

    findings = build_findings(results)

    assert findings == [
        {"criterion_id": "B", "issue": "not_found", "severity": "low", "evidence_refs": []},
        {"criterion_id": "C", "issue": "unknown", "severity": "medium", "evidence_refs": [2]},
        {"criterion_id": "D", "issue": "concern_present", "severity": "high", "evidence_refs": [3]},
    ]


def test_build_findings_empty_when_all_satisfied_and_no_concern():
    results = [
        {"criterion_id": "A", "status": "satisfied", "page_number": 1, "quote": "q", "concern_present": None},
        {"criterion_id": "B", "status": "satisfied", "page_number": 2, "quote": "q2", "concern_present": False},
    ]
    assert build_findings(results) == []


def test_append_audit_record_writes_one_json_line(tmp_path):
    log_path = tmp_path / "audit_log.jsonl"
    record = build_audit_record("samples/sample.pdf", RESULTS, DECISION)

    append_audit_record(record, path=log_path)

    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_append_audit_record_is_append_only(tmp_path):
    log_path = tmp_path / "audit_log.jsonl"
    record_1 = build_audit_record("samples/sample.pdf", RESULTS, DECISION)
    record_2 = build_audit_record("samples/sample_clean_approve.pdf", RESULTS, DECISION)

    append_audit_record(record_1, path=log_path)
    append_audit_record(record_2, path=log_path)

    lines = log_path.read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["case"] == "samples/sample.pdf"
    assert json.loads(lines[1])["case"] == "samples/sample_clean_approve.pdf"
