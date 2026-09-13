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

MODEL = "claude-opus-5"

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
        },
        "required": ["status", "page_number", "quote"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_prompt(criterion, pages):
    labeled_pages = "\n\n".join(
        f"[PAGE {page['page_number']}]\n{page['text']}" for page in pages
    )

    return f"""You are reviewing a patient document packet against ONE policy criterion.

Criterion ID: {criterion['id']}
Criterion description: {criterion['description']}

Below is the document text, page by page:

{labeled_pages}

Decide whether this criterion is satisfied:

- status "satisfied": you found a clear, direct statement supporting this
  criterion. Copy the exact supporting sentence(s) as the quote, and give
  the page number it appears on.
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

    if status == "satisfied" and not verify_quote(quote, pages, page_number):
        status = "unknown"
        page_number = None
        quote = None

    return {
        "criterion_id": criterion["id"],
        "status": status,
        "page_number": page_number,
        "quote": quote,
    }


def evaluate_all_criteria(criteria, pages):
    return [find_evidence(criterion, pages) for criterion in criteria]
