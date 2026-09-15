"""
Milestone 6: deterministic decision engine.

Takes the evidence report (one status per criterion, from evidence.py)
plus the policy criteria (for each criterion's group, from policy.py)
and applies fixed rules to produce one workflow outcome. No LLM calls,
no judgment calls happen here - only plain logic on data we already have.

Criteria are grouped in the policy (see policies/lumbar_mri.json) so
that criteria representing alternative ways to satisfy the same
requirement - for example, any one of four neuro findings, or either
medication or physical therapy for conservative care - don't each have
to be individually satisfied. A group is met if at least one of its
members is satisfied. A criterion with no listed group is its own
singleton group, so it is unaffected by grouping and must be satisfied
on its own.

Rules:
- any criterion satisfied with concern_present = true -> human_review
  (a red flag / warning sign is actually present in the record - this
  never bypasses review and never triggers an automatic denial, it just
  means a person needs to look closely, per real prior-authorization
  practice)
- any group with no satisfied member -> human_review (a person needs to
  look at this case - either the system couldn't safely judge the
  evidence for every member of that group, or the evidence is simply
  missing)
- every group has at least one satisfied member, and no concern present
  -> approve
"""


def decide_authorization(results, criteria=None):
    criteria = criteria or []
    group_by_id = {c["id"]: c.get("group", c["id"]) for c in criteria}

    concerns = [r for r in results if r.get("concern_present") is True]
    if concerns:
        reasons = [f"{r['criterion_id']}: concern_present" for r in concerns]
        return {"decision": "human_review", "reasons": reasons}

    groups = {}
    for r in results:
        group = group_by_id.get(r["criterion_id"], r["criterion_id"])
        groups.setdefault(group, []).append(r)

    reasons = []
    for members in groups.values():
        if any(m["status"] == "satisfied" for m in members):
            continue
        reasons.extend(f"{m['criterion_id']}: {m['status']}" for m in members)

    if reasons:
        return {"decision": "human_review", "reasons": reasons}

    return {"decision": "approve", "reasons": []}
