import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import evidence
from evidence import build_prompt, verify_quote, evaluate_all_criteria

PAGES = [
    {"page_number": 1, "text": "Motor strength is 4-/5 in the left lower extremity."},
    {"page_number": 2, "text": "Physical therapy: 8 sessions completed."},
]

CRITERION = {"id": "NRC.weakness", "description": "Evidence of neurologic weakness is documented."}


def test_build_prompt_includes_criterion_and_page_labels():
    prompt = build_prompt(CRITERION, PAGES)
    assert "NRC.weakness" in prompt
    assert "Evidence of neurologic weakness is documented." in prompt
    assert "[PAGE 1]" in prompt
    assert "[PAGE 2]" in prompt
    assert "Motor strength is 4-/5 in the left lower extremity." in prompt


def test_verify_quote_exact_match():
    assert verify_quote("Motor strength is 4-/5 in the left lower extremity.", PAGES, 1) is True


def test_verify_quote_with_different_whitespace():
    messy_quote = "Motor strength   is 4-/5\nin the left lower extremity."
    assert verify_quote(messy_quote, PAGES, 1) is True


def test_verify_quote_not_present_on_page():
    assert verify_quote("Patient reports no weakness at all.", PAGES, 1) is False


def test_verify_quote_present_but_wrong_page():
    assert verify_quote("Motor strength is 4-/5 in the left lower extremity.", PAGES, 2) is False


def test_verify_quote_missing_page_number():
    assert verify_quote("Motor strength is 4-/5 in the left lower extremity.", PAGES, None) is False


def test_evaluate_all_criteria_calls_find_evidence_per_criterion(monkeypatch):
    criteria = [
        {"id": "A", "description": "criterion A"},
        {"id": "B", "description": "criterion B"},
    ]
    calls = []

    def fake_find_evidence(criterion, _pages):
        calls.append(criterion["id"])
        return {"criterion_id": criterion["id"], "status": "not_found", "page_number": None, "quote": None}

    monkeypatch.setattr(evidence, "find_evidence", fake_find_evidence)

    results = evaluate_all_criteria(criteria, PAGES)

    assert calls == ["A", "B"]
    assert [r["criterion_id"] for r in results] == ["A", "B"]
