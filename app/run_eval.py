"""
Eval suite: runs the real pipeline (real Claude API calls) against every
case in eval_cases.py and scores the result against ground truth.

This measures whether the AI evidence-finding step can be trusted, not
just whether the code runs. Three things are scored:

- per-criterion status accuracy (did find_evidence get the right status)
- decision accuracy (did decide_authorization reach the right outcome)
- hallucination count (satisfied status assigned where ground truth says
  not_found or unknown - this must always be 0. It is the guardrail
  check: the model must never invent evidence, especially on off-topic
  documents that contain no clinical content at all)

Run with: python3 app/run_eval.py
Requires ANTHROPIC_API_KEY - set it in a .env file in the project root,
or as a real environment variable.
"""

import json

from dotenv import load_dotenv

load_dotenv()

from extract_text import extract_pages
from policy import load_policy
from evidence import evaluate_all_criteria
from decision import decide_authorization
from eval_cases import EVAL_CASES

POLICY_PATH = "policies/lumbar_mri.json"
EVAL_REPORT_PATH = "output/eval_report.json"

criteria = load_policy(POLICY_PATH)
case_reports = []

for case in EVAL_CASES:
    pages = extract_pages(case["pdf_path"])
    results = evaluate_all_criteria(criteria, pages)
    decision = decide_authorization(results, criteria)

    status_by_criterion = {r["criterion_id"]: r["status"] for r in results}
    concern_by_criterion = {r["criterion_id"]: r.get("concern_present") for r in results}

    mismatches = []
    hallucinations = []
    for criterion_id, expected_status in case["expected_status"].items():
        actual_status = status_by_criterion.get(criterion_id)
        if actual_status != expected_status:
            mismatches.append(
                {
                    "criterion_id": criterion_id,
                    "expected": expected_status,
                    "actual": actual_status,
                }
            )
        if actual_status == "satisfied" and expected_status in ("not_found", "unknown"):
            hallucinations.append(criterion_id)

    concern_mismatches = []
    for criterion_id, expected_concern in case.get("expected_concern", {}).items():
        actual_concern = concern_by_criterion.get(criterion_id)
        if actual_concern != expected_concern:
            concern_mismatches.append(
                {
                    "criterion_id": criterion_id,
                    "expected": expected_concern,
                    "actual": actual_concern,
                }
            )

    decision_correct = decision["decision"] == case["expected_decision"]

    case_reports.append(
        {
            "name": case["name"],
            "pdf_path": case["pdf_path"],
            "criteria_total": len(case["expected_status"]),
            "criteria_correct": len(case["expected_status"]) - len(mismatches),
            "mismatches": mismatches,
            "concern_mismatches": concern_mismatches,
            "hallucinations": hallucinations,
            "expected_decision": case["expected_decision"],
            "actual_decision": decision["decision"],
            "decision_correct": decision_correct,
        }
    )

total_criteria = sum(c["criteria_total"] for c in case_reports)
total_correct = sum(c["criteria_correct"] for c in case_reports)
total_hallucinations = sum(len(c["hallucinations"]) for c in case_reports)
total_concern_mismatches = sum(len(c["concern_mismatches"]) for c in case_reports)
decisions_correct = sum(1 for c in case_reports if c["decision_correct"])

summary = {
    "cases_total": len(case_reports),
    "decisions_correct": decisions_correct,
    "criterion_accuracy": round(total_correct / total_criteria, 3),
    "total_hallucinations": total_hallucinations,
    "total_concern_mismatches": total_concern_mismatches,
}

print("=== Per-case results ===")
for c in case_reports:
    status = (
        "PASS"
        if c["decision_correct"] and not c["mismatches"] and not c["concern_mismatches"]
        else "FAIL"
    )
    print(
        f"[{status}] {c['name']}: decision={c['actual_decision']} "
        f"(expected {c['expected_decision']}), "
        f"criteria {c['criteria_correct']}/{c['criteria_total']} correct, "
        f"hallucinations={len(c['hallucinations'])}"
    )
    for m in c["mismatches"]:
        print(f"    {m['criterion_id']}: expected {m['expected']}, got {m['actual']}")
    for m in c["concern_mismatches"]:
        print(f"    {m['criterion_id']}.concern_present: expected {m['expected']}, got {m['actual']}")

print()
print("=== Summary ===")
print(summary)

with open(EVAL_REPORT_PATH, "w") as f:
    json.dump({"summary": summary, "cases": case_reports}, f, indent=2)
print(f"Wrote {EVAL_REPORT_PATH}")
