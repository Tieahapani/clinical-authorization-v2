"""
Milestone 8: audit record.

Every pipeline run appends one record to an audit log - what packet
was reviewed, against which policy version, what evidence was found
for each criterion, what problems that evidence raised (findings),
what decision the deterministic engine reached, and when. Pure data
assembly and file I/O - no LLM calls, no decision logic. Append-only,
so past records are never edited or lost, which is the point of an
audit trail.

"findings" is a deterministic summary of which criteria kept this case
from a clean approval, with a severity so a reviewer can scan for the
most important ones first:

- concern_present (a red flag actually present)     -> high
- unknown (the system couldn't safely judge this)    -> medium
- not_found (evidence is simply missing)             -> low

Severity here is a fixed, explainable rule, not a model judgment - see
decision.py for how the same statuses drive the decision itself.
"""

import json
import uuid
from datetime import datetime, timezone

from evidence import MODEL
from policy import POLICY_VERSION

AUDIT_LOG_PATH = "output/audit_log.jsonl"

SEVERITY_BY_STATUS = {
    "not_found": "low",
    "unknown": "medium",
}
CONCERN_PRESENT_SEVERITY = "high"


def build_findings(results):
    findings = []
    for r in results:
        if r.get("concern_present") is True:
            issue, severity = "concern_present", CONCERN_PRESENT_SEVERITY
        elif r["status"] in SEVERITY_BY_STATUS:
            issue, severity = r["status"], SEVERITY_BY_STATUS[r["status"]]
        else:
            continue

        evidence_refs = [r["page_number"]] if r.get("page_number") is not None else []
        findings.append(
            {
                "criterion_id": r["criterion_id"],
                "issue": issue,
                "severity": severity,
                "evidence_refs": evidence_refs,
            }
        )
    return findings


def build_audit_record(pdf_path, results, decision):
    return {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case": pdf_path,
        "actor": "rule_engine",
        "model": MODEL,
        "policy_version": POLICY_VERSION,
        "results": results,
        "findings": build_findings(results),
        "decision": decision["decision"],
        "reasons": decision["reasons"],
    }


def append_audit_record(record, path=AUDIT_LOG_PATH):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
