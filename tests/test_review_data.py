import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from review_data import merge_criteria_with_evidence

CRITERIA = [
    {"id": "A", "description": "Criterion A description."},
    {"id": "B", "description": "Criterion B description."},
]

EVIDENCE_REPORT = [
    {"criterion_id": "A", "status": "satisfied", "page_number": 1, "quote": "quote A"},
    {"criterion_id": "B", "status": "not_found", "page_number": None, "quote": None},
]


def test_correct_criterion_to_description_matching():
    merged = merge_criteria_with_evidence(CRITERIA, EVIDENCE_REPORT)

    assert merged == [
        {"id": "A", "description": "Criterion A description.", "status": "satisfied", "page_number": 1, "quote": "quote A", "concern_present": None},
        {"id": "B", "description": "Criterion B description.", "status": "not_found", "page_number": None, "quote": None, "concern_present": None},
    ]


def test_missing_criterion_in_evidence_report_raises():
    incomplete_evidence = [EVIDENCE_REPORT[0]]  # criterion B has no evidence entry

    with pytest.raises(ValueError, match="Missing evidence for: \\['B'\\]"):
        merge_criteria_with_evidence(CRITERIA, incomplete_evidence)


def test_unrecognized_criterion_id_in_evidence_report_raises():
    extra_evidence = EVIDENCE_REPORT + [
        {"criterion_id": "Z", "status": "satisfied", "page_number": 1, "quote": "unexpected"}
    ]

    with pytest.raises(ValueError, match="Unrecognized evidence IDs: \\['Z'\\]"):
        merge_criteria_with_evidence(CRITERIA, extra_evidence)
