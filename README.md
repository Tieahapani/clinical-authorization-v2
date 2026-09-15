# Prior Authorization Document Intelligence

A portfolio project demonstrating document intelligence, LLM evidence
retrieval, and deterministic workflow automation for a single narrow
use case: **lumbar spine MRI prior authorization**.

This is **not** a real clinical system. It uses synthetic patient data
only and is not intended for real medical use. See `CLAUDE.md` for the
full project scope and design philosophy.

## Pipeline

```
Synthetic PDF packet
        |
        v
1. Extract text (app/extract_text.py)
        |
        v
2. Load policy criteria (app/policy.py, policies/lumbar_mri.json)
        |
        v
3. Find evidence per criterion via LLM, with quote verification
   (app/evidence.py)
        |
        v
4. Deterministic decision (app/decision.py)
        |
        v
5. Read-only reviewer interface (app/review_ui.py)
```

The decision engine groups criteria (see `policies/lumbar_mri.json`) so
that alternative ways to satisfy the same requirement - any one of four
neuro findings, either medication or physical therapy - don't each have
to be individually satisfied. It also tracks, per red-flag-style
criterion, whether the concerning finding was explicitly ruled out or
is actually present: a present concern always forces `human_review`,
never a bypass to approval. Decision outcomes are `approve` or
`human_review` only.

## Reviewer UI

![Prior Authorization Review UI](docs/review_ui_screenshot.jpg)

## Running it

```bash
pip install -r requirements.txt

# Set your Anthropic API key in a .env file:
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run the full pipeline (extraction -> evidence -> decision):
python3 app/run_evidence_demo.py

# View the results in the reviewer UI:
streamlit run app/review_ui.py

# Run the automated tests (no API calls):
python3 -m pytest tests/ -q

# Run the eval suite against ground-truth synthetic packets (real API calls):
python3 app/run_eval.py
```

## Demo Case: Jane Synthetic-Doe — Lumbar Spine MRI Prior Authorization

**Patient:** Jane Synthetic-Doe (synthetic, DOB 01/01/1990)
**Presenting complaint:** Low back pain radiating to the left leg, 8 weeks duration
**Requested service:** Lumbar spine MRI

The packet (`samples/sample.pdf`) is a 4-page synthetic submission from
the requesting provider: a referral letter, a physician exam note, a
medication/treatment history, and physical therapy notes — the kind of
multi-document bundle a payer actually receives, condensed into one PDF.

### Why this case is a good demo, not a trivial one

A demo where everything is neatly documented and the system just says
"approve" doesn't prove much — any keyword search could look competent
on easy data. This packet is deliberately realistic in a harder way:
**the documentation is good but incomplete**, which is the normal case
in real prior-auth review, not the exception.

### What the system found

Running the packet through all 10 lumbar MRI criteria:

- **7 criteria satisfied** — neurologic weakness, sensory loss,
  medication trial, physical therapy, treatment duration, symptom
  duration, and bowel/bladder dysfunction (explicitly ruled out) are
  all directly documented, each with the exact supporting sentence and
  page number a reviewer can check in seconds.
- **1 criterion not_found** — no prior imaging is on file.
- **1 criterion unknown** — the reflex exam was "deferred due to
  patient guarding," meaning it was never actually performed. The
  system correctly distinguishes "this exam wasn't done" from "this
  exam was done and found nothing" — a real judgment call, not just
  pattern matching. (Earlier in development the model got this wrong
  and called it `not_found`; the prompt instructions were fixed to
  correct it.)

### The outcome a reviewer sees

**Decision: HUMAN_REVIEW** — triggered by the `unknown` reflex-exam
criterion. A person needs to look at *why* the reflex exam wasn't
performed before this case can be routed anywhere else — a judgment
call the system correctly refuses to make on its own.

Opening the reviewer UI, a reviewer sees this decision immediately at
the top, then can scan all 10 criteria in seconds — for the 7
satisfied ones, the exact quote and page number are right there to
verify, instead of re-reading 4 pages of clinical notes by hand.

## Evaluation

Building the decision engine surfaced a question no amount of code
review answers on its own: how much can the evidence-finding step
actually be trusted? `app/run_eval.py` runs the real pipeline (real
Claude API calls, no mocking) against five ground-truth synthetic
packets (`app/eval_cases.py`) and scores three things:

- **per-criterion status accuracy** — did the model's status match
  human-judged ground truth
- **decision accuracy** — did the deterministic engine reach the right
  final outcome
- **hallucination count** — any `satisfied` where ground truth says
  `not_found`/`unknown`, which must always be 0. One packet
  (`sample_offtopic.pdf`) is a grocery list and a weather forecast -
  zero clinical content at all - specifically to check the model
  doesn't invent medical evidence out of unrelated text.

Current state: **5/5 decisions correct, 50/50 (100%) criterion
accuracy, 0 hallucinations.**

### What the eval caught along the way

The eval wasn't just a final scorecard - it caught two real bugs
before this state was reached, both fixed by moving a judgment call
out of the LLM prompt and into deterministic policy data, per the
project's core AI-vs-deterministic-code split:

1. **Denial vs. presence.** Early runs showed the model marking
   `satisfied` when a record explicitly *denied* a finding ("full
   strength, symmetric," "sensation is intact") - treating "the topic
   was discussed" as satisfying the criterion, instead of requiring
   the actual finding to be present. Fixed by making the prompt
   default to requiring presence, with an explicit exception for
   criteria whose own description allows a ruled-out reading.

2. **Over-generalized red-flag logic.** `RF.red_flag` and
   `NRC.bowel_bladder` are genuinely dual-meaning criteria - "possible
   cauda equina concern" is right in the second one's description - so
   `satisfied` there means either "ruled out" or "actually present,"
   and a present concern forces `human_review` regardless of anything
   else, matching real prior-authorization practice (a red flag is a
   signal for closer review, never a bypass to approval). But when
   this dual reading was left for the model to infer per call, it
   started applying the same logic to `NRC.weakness` - a criterion
   where a positive finding is supposed to *support* approval - and
   incorrectly forced `human_review` on a clean-approve case. The fix
   was to stop asking the model which criteria are red-flag-style and
   make it a deterministic fact in the policy file instead
   (`"is_concern_criterion": true`, checked and enforced in code in
   `app/evidence.py`, never left to the model's judgment).

The eval also justified a model change: switching `evidence.py` from
`claude-opus-5` to `claude-sonnet-5` measurably cut hallucinations on
this same eval (3/40 -> 1/40 on one run), while costing less per call.
