"""
Milestone 7: pure data-joining logic for the reviewer UI.

Joins policy criteria (id + description) with the evidence report
(id + status + page + quote), by criterion ID. No Streamlit, no I/O -
fully testable with plain dicts/lists.
"""


def merge_criteria_with_evidence(criteria, evidence_report):
    evidence_by_id = {e["criterion_id"]: e for e in evidence_report}
    criteria_ids = {c["id"] for c in criteria}
    evidence_ids = set(evidence_by_id.keys())

    missing_evidence = criteria_ids - evidence_ids
    unrecognized_evidence = evidence_ids - criteria_ids

    if missing_evidence or unrecognized_evidence:
        raise ValueError(
            "Criterion ID mismatch between policy and evidence report. "
            f"Missing evidence for: {sorted(missing_evidence)}. "
            f"Unrecognized evidence IDs: {sorted(unrecognized_evidence)}."
        )

    merged = []
    for criterion in criteria:
        evidence = evidence_by_id[criterion["id"]]
        merged.append({
            "id": criterion["id"],
            "description": criterion["description"],
            "status": evidence["status"],
            "page_number": evidence.get("page_number"),
            "quote": evidence.get("quote"),
        })

    return merged
