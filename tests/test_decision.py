import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from decision import decide_authorization


def result(criterion_id, status):
    return {"criterion_id": criterion_id, "status": status, "page_number": None, "quote": None}


def test_all_satisfied_approves():
    results = [result("A", "satisfied"), result("B", "satisfied")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "approve"
    assert outcome["reasons"] == []


def test_not_found_triggers_request_information():
    results = [result("A", "satisfied"), result("B", "not_found")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "request_information"
    assert outcome["reasons"] == ["B: not_found"]


def test_unknown_triggers_human_review():
    results = [result("A", "satisfied"), result("B", "unknown")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["B: unknown"]


def test_not_found_and_unknown_together_human_review_wins():
    results = [result("A", "not_found"), result("B", "unknown")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["B: unknown"]


def test_empty_results_approves():
    outcome = decide_authorization([])
    assert outcome["decision"] == "approve"
    assert outcome["reasons"] == []
