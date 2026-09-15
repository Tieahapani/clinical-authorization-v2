"""
Milestone 4: find evidence for one policy criterion using an LLM.

The model may read the document and identify evidence. It may NOT
invent quotes, approve/deny anything, or decide workflow outcomes -
that stays in deterministic code (see build_prompt's instructions and
verify_quote below).
"""

from typing import cast

import anthropic
from anthropic.types import ToolParam

MODEL = "claude-sonnet-5"

SUBMIT_EVIDENCE_TOOL = {
    "name": "submit_evidence",
    "description": (
        "Report whether the given criterion is satisfied by the document, "
        "and if so, the exact supporting page and quote."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["satisfied", "not_found", "unknown"],
            },
            "page_number": {
                "type": ["integer", "null"],
                "description": "Required when status is 'satisfied'. Otherwise null.",
            },
            "quote": {
                "type": ["string", "null"],
                "description": (
                    "Required when status is 'satisfied'. Must be copied "
                    "exactly from the cited page - do not paraphrase. "
                    "Otherwise null."
                ),
            },
            "concern_present": {
                "type": ["boolean", "null"],
                "description": (
                    "Only meaningful for a red-flag-style criterion, where "
                    "'satisfied' can mean two different things: the "
                    "concerning finding was explicitly ruled out (false), "
                    "or the concerning finding is actually present (true) "
                    "and needs closer human review, not a bypass to "
                    "approval. Required (true or false) when status is "
                    "'satisfied' and the criterion asks about a red flag "
                    "or warning sign. Null for every other case."
                ),
            },
        },
        "required": ["status", "page_number", "quote", "concern_present"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_prompt(criterion, pages):
    labeled_pages = "\n\n".join(
        f"[PAGE {page['page_number']}]\n{page['text']}" for page in pages
    )

    is_concern_criterion = criterion.get("is_concern_criterion", False)

    if is_concern_criterion:
        satisfied_rule = """- status "satisfied": the documentation clearly addresses this warning
  sign either way - either it explicitly states the warning sign is
  ABSENT / ruled out, or it shows the warning sign IS actually present.
  Copy the exact supporting sentence(s) as the quote, and give the page
  number it appears on. Then set concern_present:
    - ruled out / absent -> concern_present = false
    - actually present -> concern_present = true. This is not
      automatically a denial or an approval - it means this case needs
      a human reviewer's attention, so flag it honestly rather than
      treating it the same as a clean rule-out."""
    else:
        satisfied_rule = """- status "satisfied": you found a clear, direct statement that the
  actual finding named by the criterion IS PRESENT in the record - not
  merely that the topic was discussed. Copy the exact supporting
  sentence(s) as the quote, and give the page number it appears on.
  Leave concern_present null - this criterion is not a red-flag/warning
  -sign criterion, so concern_present is never used for it.
  A statement that explicitly denies, rules out, or reports a
  normal/negative result for this finding means the finding is NOT
  present - use "not_found" for that criterion, not "satisfied". For
  example, "sensation is intact" or "full strength, symmetric" report
  the absence of the finding, not evidence of it."""

    return f"""You are reviewing a patient document packet against ONE policy criterion.

Criterion ID: {criterion['id']}
Criterion description: {criterion['description']}

Below is the document text, page by page:

{labeled_pages}

Decide whether this criterion is satisfied:

{satisfied_rule}
- status "not_found": you read the document and this specific evidence is
  simply not present.
- status "unknown": the document is ambiguous, contradictory, unreadable,
  or you are not confident enough to say satisfied or not_found.

If you are unsure whether something counts as evidence, prefer "unknown"
over guessing "not_found". Do not invent or paraphrase a quote - if you
cannot copy an exact supporting sentence, do not use "satisfied".

If an exam or assessment was deferred, not performed, or its result was
not recorded, that is "unknown" - not "not_found". Only use "not_found"
when the exam or documentation was actually completed and clearly shows
no relevant finding.

If the document text above is not a clinical/medical record at all (for
example a grocery list, a weather forecast, or any other unrelated
content), you must not invent or infer medical evidence from it. Use
"not_found" in that case - never "satisfied".

Call the submit_evidence tool with your answer."""


def verify_quote(quote, pages, page_number):
    if quote is None or page_number is None:
        return False

    page = next((p for p in pages if p["page_number"] == page_number), None)
    if page is None:
        return False

    normalize = lambda s: " ".join(s.split())
    return normalize(quote) in normalize(page["text"])


def find_evidence(criterion, pages):
    client = anthropic.Anthropic()
    prompt = build_prompt(criterion, pages)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[cast(ToolParam, SUBMIT_EVIDENCE_TOOL)],
        tool_choice={"type": "tool", "name": "submit_evidence"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = tool_use.input

    status = result["status"]
    page_number = result.get("page_number")
    quote = result.get("quote")
    concern_present = result.get("concern_present")

    if not criterion.get("is_concern_criterion", False):
        concern_present = None

    if status == "satisfied" and not verify_quote(quote, pages, page_number):
        status = "unknown"
        page_number = None
        quote = None
        concern_present = None

    return {
        "criterion_id": criterion["id"],
        "status": status,
        "page_number": page_number,
        "quote": quote,
        "concern_present": concern_present,
    }


def evaluate_all_criteria(criteria, pages):
    return [find_evidence(criterion, pages) for criterion in criteria]
