import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from decision import decide_authorization


def result(criterion_id, status, concern_present=None):
    return {
        "criterion_id": criterion_id,
        "status": status,
        "page_number": None,
        "quote": None,
        "concern_present": concern_present,
    }


def test_all_satisfied_approves():
    results = [result("A", "satisfied"), result("B", "satisfied")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "approve"
    assert outcome["reasons"] == []


def test_not_found_triggers_human_review():
    results = [result("A", "satisfied"), result("B", "not_found")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["B: not_found"]


def test_unknown_triggers_human_review():
    results = [result("A", "satisfied"), result("B", "unknown")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["B: unknown"]


def test_not_found_and_unknown_together_both_listed():
    results = [result("A", "not_found"), result("B", "unknown")]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["A: not_found", "B: unknown"]


def test_empty_results_approves():
    outcome = decide_authorization([])
    assert outcome["decision"] == "approve"
    assert outcome["reasons"] == []


def test_concern_present_triggers_human_review_even_if_all_satisfied():
    results = [
        result("A", "satisfied"),
        result("RF.red_flag", "satisfied", concern_present=True),
    ]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["RF.red_flag: concern_present"]


def test_concern_ruled_out_does_not_block_approval():
    results = [
        result("A", "satisfied"),
        result("RF.red_flag", "satisfied", concern_present=False),
    ]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "approve"
    assert outcome["reasons"] == []


def test_concern_present_takes_priority_over_not_found_reasons():
    results = [
        result("RF.red_flag", "satisfied", concern_present=True),
        result("B", "not_found"),
    ]
    outcome = decide_authorization(results)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["RF.red_flag: concern_present"]


NEURO_CRITERIA = [
    {"id": "NRC.weakness", "description": "d", "group": "neuro_finding"},
    {"id": "NRC.sensory_loss", "description": "d", "group": "neuro_finding"},
]


def test_one_satisfied_member_meets_the_whole_group():
    results = [
        result("NRC.weakness", "satisfied"),
        result("NRC.sensory_loss", "not_found"),
    ]
    outcome = decide_authorization(results, NEURO_CRITERIA)
    assert outcome["decision"] == "approve"
    assert outcome["reasons"] == []


def test_group_with_no_satisfied_member_triggers_human_review():
    results = [
        result("NRC.weakness", "not_found"),
        result("NRC.sensory_loss", "unknown"),
    ]
    outcome = decide_authorization(results, NEURO_CRITERIA)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["NRC.weakness: not_found", "NRC.sensory_loss: unknown"]


def test_criterion_with_no_group_listed_is_its_own_singleton_group():
    ungrouped_criteria = [{"id": "IMG.prior_imaging", "description": "d"}]
    results = [result("IMG.prior_imaging", "not_found")]
    outcome = decide_authorization(results, ungrouped_criteria)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["IMG.prior_imaging: not_found"]


def test_grouping_does_not_bypass_a_separate_ungrouped_criterion():
    mixed_criteria = NEURO_CRITERIA + [{"id": "IMG.prior_imaging", "description": "d"}]
    results = [
        result("NRC.weakness", "satisfied"),
        result("NRC.sensory_loss", "not_found"),
        result("IMG.prior_imaging", "not_found"),
    ]
    outcome = decide_authorization(results, mixed_criteria)
    assert outcome["decision"] == "human_review"
    assert outcome["reasons"] == ["IMG.prior_imaging: not_found"]
