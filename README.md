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

- **6 criteria satisfied** — neurologic weakness, sensory loss,
  medication trial, physical therapy, treatment duration, and symptom
  duration are all directly documented, each with the exact supporting
  sentence and page number a reviewer can check in seconds.
- **2 criteria not_found** — no prior imaging is on file, and the
  provider's note explicitly denies bowel/bladder dysfunction (which
  this criterion requires as *positive* evidence, not a denial).
- **1 criterion unknown** — the reflex exam was "deferred due to
  patient guarding," meaning it was never actually performed. The
  system correctly distinguishes "this exam wasn't done" from "this
  exam was done and found nothing" — a real judgment call, not just
  pattern matching. (Earlier in development the model got this wrong
  and called it `not_found`; the prompt instructions were fixed to
  correct it.)

### The outcome a reviewer sees

**Decision: HUMAN_REVIEW** — triggered by the one `unknown` criterion,
which by design takes precedence over the two `not_found` criteria. A
person needs to look at *why* the reflex exam wasn't performed before
this case can be routed anywhere else — a judgment call the system
correctly refuses to make on its own.

Opening the reviewer UI, a reviewer sees this decision immediately at
the top, then can scan all 10 criteria in seconds — for the 6
satisfied ones, the exact quote and page number are right there to
verify, instead of re-reading 4 pages of clinical notes by hand.
