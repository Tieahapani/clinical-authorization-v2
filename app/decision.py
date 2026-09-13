"""
Milestone 6: deterministic decision engine.

Takes the evidence report (one status per criterion, from evidence.py)
and applies fixed rules to produce one workflow outcome. No LLM calls,
no judgment calls happen here - only plain logic on data we already have.

Rules:
- all criteria satisfied  -> approve
- any criterion unknown   -> human_review (the system could not safely
                              determine whether evidence satisfies the
                              criterion - this needs a person's judgment,
                              not just more paperwork)
- otherwise, any criterion
  not_found                -> request_information (evidence is simply
                              missing - ask the provider to supply it)

unknown takes precedence over not_found when both occur.
"""


def decide_authorization(results):
    unknown = [r for r in results if r["status"] == "unknown"]
    not_found = [r for r in results if r["status"] == "not_found"]

    if unknown:
        reasons = [f"{r['criterion_id']}: unknown" for r in unknown]
        return {"decision": "human_review", "reasons": reasons}

    if not_found:
        reasons = [f"{r['criterion_id']}: not_found" for r in not_found]
        return {"decision": "request_information", "reasons": reasons}

    return {"decision": "approve", "reasons": []}
