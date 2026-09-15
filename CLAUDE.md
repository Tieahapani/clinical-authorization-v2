# Prior Authorization Document Intelligence

## Project purpose

This is a portfolio side project demonstrating:

- document intelligence
- structured extraction
- LLM evidence retrieval
- deterministic workflow automation
- human review
- evaluation
- auditability

The project is being built for learning and to demonstrate
Forward Deployed Engineer-style problem solving.

I am NOT a medical professional.

This project must use synthetic patient data only.

This is NOT intended for real clinical use and should not be presented
as a medical device or production healthcare system.

---

# The problem

In prior authorization, a payer may receive many pages of medical
documents.

A reviewer needs to determine whether those documents contain evidence
that satisfies predefined policy criteria.

The difficult part is finding the relevant evidence inside the documents.

This project demonstrates how an AI system can help find that evidence
while keeping consequential workflow decisions deterministic.

---

# Scope

We are intentionally building ONE narrow workflow:

Lumbar Spine MRI Prior Authorization

We are NOT building:

- a complete healthcare platform
- multiple medical specialties
- claims processing
- FHIR integration
- X12 integration
- provider portals
- insurance billing
- autonomous medical decision making
- autonomous denial of care

Do not expand the scope unless I explicitly request it.

---

# Core workflow

The system should eventually work like this:

Synthetic PDF packet
        |
        v
1. Extract text
        |
        v
2. Identify pages/documents
        |
        v
3. Load policy criteria
        |
        v
4. Find evidence for each criterion
        |
        v
5. Return criterion + page + exact quote
        |
        v
6. Deterministic decision
        |
        +--> approve
        |
        +--> human_review
        |
        v
7. Reviewer interface
        |
        v
8. Audit record

---

# Most important product behavior

The main value of the system is NOT simply returning:

    weakness = satisfied

The system should return:

    criterion: Neurologic weakness
    status: satisfied
    page: 2
    evidence:
      "Motor strength is 4-/5 in the left lower extremity."

The user should be able to move from:

criterion
→ status
→ page
→ exact supporting evidence

The goal is to help a reviewer VERIFY evidence instead of searching
through a long packet manually.

---

# AI vs deterministic code

This separation is extremely important.

## AI / model responsibilities

The model may:

- read clinical text
- understand different wording
- identify evidence relevant to a predefined criterion
- return the source page
- return an exact supporting quote
- identify ambiguous evidence

The model should NOT:

- invent medical criteria
- invent evidence
- independently approve care
- independently deny care
- make eligibility decisions
- silently infer missing values

---

## Deterministic code responsibilities

Normal code should handle:

- loading policy criteria
- validating required fields
- deciding whether all required criteria are satisfied
- deciding whether information is missing
- routing ambiguous cases to human review
- generating audit records

Simple principle:

    language understanding → model

    workflow consequence → deterministic code

---

# Initial policy

Start with ONLY three simplified criteria.

These are educational synthetic criteria, not authoritative medical
guidelines.

## Criterion 1

ID:
NRC.weakness

Description:
Evidence of neurologic weakness is documented.

---

## Criterion 2

ID:
CM.medication

Description:
Conservative medication treatment is documented.

---

## Criterion 3

ID:
CM.physical_therapy

Description:
Physical therapy is documented.

---

# Criterion statuses

For the first version, use only:

- satisfied
- not_found
- unknown

Definitions:

## satisfied

Clear supporting evidence exists in the packet.

Must include:

- page
- exact quote

## not_found

Relevant evidence was searched for but could not be found.

Do not invent a quote.

## unknown

The system cannot safely determine the result.

Examples:

- unreadable text
- ambiguous statement
- insufficient context

Important:

    unknown != not_found

Never automatically convert unknown into missing evidence.

---

# First decision rules

Keep the first decision engine intentionally simple.

If all required criteria are satisfied:

    approve

If one or more criteria are not_found or unknown:

    human_review

These are workflow recommendations for a synthetic demo,
not real medical decisions.

---

# Architecture philosophy

Prefer:

- simple Python
- clear functions
- explicit data structures
- small files
- understandable code
- tests
- observable intermediate output

Avoid:

- agent frameworks unless clearly necessary
- excessive abstractions
- complicated dependency injection
- microservices
- unnecessary databases
- premature optimization
- clever code that is difficult to explain

This is a portfolio project.

I need to understand every major component well enough to explain it
in an interview.

---

# Development process

For every milestone:

1. Inspect the existing code first.
2. Explain the problem in beginner-friendly language.
3. Explain what files you propose to create or change.
4. Explain why.
5. Do not make large architectural changes without discussing them.
6. Implement the smallest working version.
7. Run it.
8. Test it.
9. Explain the result to me.
10. Tell me what I should understand for an interview.

When something fails, do not hide it.

Show:

- what failed
- why it failed
- how you know
- what the smallest reasonable fix is

---

# Important constraint

Do not over-engineer the project.

If I request something that adds significant complexity but does not
materially improve the document-intelligence/FDE demonstration,
tell me before implementing it.

One polished workflow is more valuable than many incomplete workflows.

---

# Current milestone

We are starting from scratch.

Milestone 1 is ONLY:

    one synthetic text/PDF document
        ↓
    Python extracts its text
        ↓
    we can inspect the extracted pages

Do NOT build:

- policy evaluation
- LLM calls
- decision logic
- reviewer UI
- audit system

yet.

We will add those incrementally.