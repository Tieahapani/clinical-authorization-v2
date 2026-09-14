# Prior Authorization Document Intelligence

A document intelligence project that uses an LLM to find evidence inside clinical documents and maps that evidence to predefined review criteria.

The project focuses on one narrow example: **lumbar spine MRI prior authorization**.

Instead of asking an LLM to make the final decision, the system separates the workflow into two parts:

- **LLM:** reads the documents and finds relevant evidence.
- **Deterministic code:** verifies the evidence and applies explicit workflow rules.

The result is a reviewer-facing summary that shows:

**criterion → status → page → exact supporting evidence**

> **Disclaimer:** This is a portfolio project built with synthetic patient data and simplified educational criteria. It is not a clinical system, medical device, or real payer policy implementation, and should not be used for medical or coverage decisions.

---

## The Problem

A prior authorization review can involve multiple documents containing information relevant to a requested service.

For example, a reviewer evaluating a lumbar spine MRI request may need to look through physician notes, treatment history, and physical therapy records to determine whether specific review criteria are documented.

The relevant information may be spread across different pages and written in different ways.

This project explores a simple question:

> **Can an LLM find the relevant evidence and show a reviewer exactly where it came from, while keeping the final workflow logic outside the model?**

---

## How It Works

```text
Synthetic PDF packet
        |
        v
1. Extract text page by page
   app/extract_text.py
        |
        v
2. Load review criteria
   app/policy.py
   policies/lumbar_mri.json
        |
        v
3. Find evidence for each criterion using an LLM
   app/evidence.py
        |
        v
4. Verify returned quotes against the source page
        |
        v
5. Apply deterministic decision rules
   app/decision.py
        |
        v
6. Present the results to the reviewer
   app/review_ui.py
```

The language model is used for **document understanding**, not for making the final workflow decision.

---

## Evidence Results

Each review criterion receives one of three statuses:

| Status | Meaning |
|---|---|
| `satisfied` | Clear supporting evidence was found |
| `not_found` | Supporting evidence was not found in the submitted documentation |
| `unknown` | The available documentation is not clear enough to make a reliable determination |

When a criterion is `satisfied`, the system also returns the page number and exact supporting text.

For example:

```json
{
  "criterion_id": "NRC.weakness",
  "status": "satisfied",
  "page_number": 2,
  "quote": "Motor strength is 4-/5 in the left lower extremity."
}
```

The returned quote is checked against the extracted text from the cited page before it is accepted.

This gives the reviewer a direct path from:

```text
criterion
    ↓
status
    ↓
page
    ↓
source evidence
```

---

## Decision Logic

After all criteria have been evaluated, a separate deterministic function applies the workflow rules.

| Evidence results | Outcome |
|---|---|
| All criteria are `satisfied` | `APPROVE` |
| One or more criteria are `not_found` | `REQUEST_INFORMATION` |
| One or more criteria are `unknown` | `HUMAN_REVIEW` |

If both `not_found` and `unknown` are present, `HUMAN_REVIEW` takes precedence.

The LLM does **not** make this final decision.

This separation keeps the workflow logic explicit and independently testable.

---

## Reviewer UI

The reviewer interface displays the final recommendation along with the evidence found for each criterion.

![Prior Authorization Review UI](docs/review_ui_screenshot.jpg)

For satisfied criteria, the reviewer can see the supporting quote and page number without manually searching through the entire packet.

---

# Demo Case: Jane Synthetic-Doe

The repository includes a fully synthetic example that demonstrates the pipeline from document ingestion to reviewer output.

### Case

**Patient:** Jane Synthetic-Doe  
**Date of birth:** 01/01/1990  
**Requested service:** Lumbar spine MRI  
**Presenting complaint:** Low back pain radiating to the left leg for 8 weeks  
**Input:** `samples/sample.pdf`

The sample is a four-page synthetic packet containing:

- Referral information
- Physician examination notes
- Medication and treatment history
- Physical therapy notes

The packet intentionally contains a mixture of **clear, missing, and uncertain information** so that the pipeline exercises more than a simple all-criteria-satisfied case.

---

## What the System Finds

The demo policy evaluates multiple criteria against the submitted documentation.

### Satisfied

Several criteria have clear supporting evidence in the packet, including findings related to:

- Neurologic weakness
- Sensory findings
- Medication treatment
- Physical therapy
- Treatment duration
- Symptom duration

For these criteria, the reviewer receives both the source page and the supporting text.

Example:

```text
Neurologic Weakness
SATISFIED

Page 2

"Motor strength is 4-/5 in the left lower extremity."
```

---

### Not Found

Some criteria do not have supporting evidence in the submitted packet.

For example, prior imaging documentation is not present.

These criteria are returned as:

```text
NOT_FOUND
```

This means evidence was **not found in the submitted documentation**. It does not claim that the information does not exist elsewhere.

---

### Unknown

The packet also contains an intentionally ambiguous example.

The physician note states that the reflex examination was:

> "deferred due to patient guarding"

The system should not interpret this as a normal reflex result because the examination was not completed.

It therefore returns:

```text
UNKNOWN
```

This demonstrates an important distinction in the pipeline:

> **Evidence that is missing and evidence that cannot be reliably interpreted are not treated as the same thing.**

---

## Demo Outcome

For the included sample case, the deterministic decision engine produces:

### `HUMAN_REVIEW`

At least one criterion is `unknown`, so the case is routed for human review.

This takes precedence over criteria marked `not_found`.

The important part is that the model itself does not decide:

```text
"HUMAN_REVIEW"
```

Instead:

```text
Clinical documents
        ↓
LLM finds evidence
        ↓
Structured criterion statuses
        ↓
Deterministic rules
        ↓
HUMAN_REVIEW
```

The reviewer can then inspect the evidence behind each result rather than relying on an unexplained model output.

---

## Running the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Anthropic API key

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Do not commit `.env` or API keys to GitHub.

### 3. Run the evidence pipeline

```bash
python3 app/run_evidence_demo.py
```

This runs:

```text
PDF extraction
      ↓
evidence retrieval
      ↓
quote verification
      ↓
decision logic
```

### 4. Open the reviewer interface

```bash
streamlit run app/review_ui.py
```

### 5. Run the tests

```bash
python3 -m pytest tests/ -q
```

The automated tests do not require LLM API calls.

---

## Project Structure

```text
clinical-authorization-v2/
│
├── app/
│   ├── extract_text.py
│   ├── policy.py
│   ├── evidence.py
│   ├── decision.py
│   ├── run_evidence_demo.py
│   └── review_ui.py
│
├── policies/
│   └── lumbar_mri.json
│
├── samples/
│   └── sample.pdf
│
├── output/
│   ├── evidence_report.json
│   └── decision.json
│
├── docs/
│   └── review_ui_screenshot.jpg
│
├── tests/
├── CLAUDE.md
├── README.md
└── requirements.txt
```

---

## Why This Architecture?

The main design decision in this project is separating **probabilistic document understanding** from **deterministic workflow behavior**.

### LLM

Used where understanding language is useful:

```text
"Motor strength is 4-/5..."
             ↓
Evidence for neurologic weakness
```

### Deterministic code

Used where behavior should be explicit:

```text
unknown criterion exists
             ↓
HUMAN_REVIEW
```

This makes it possible to test the workflow rules independently from the model and makes each result easier to inspect.

---

## Current Limitations

This is a small portfolio prototype, not a production healthcare application.

Current limitations include:

- All patient information is synthetic.
- The review criteria are simplified educational examples, not an actual payer medical policy.
- The project currently focuses only on a lumbar spine MRI example.
- LLMs can misinterpret clinical text even when a returned quote is valid.
- Quote verification confirms that the cited text exists, but does not guarantee that the model interpreted it correctly.
- The current evaluation set is small and synthetic.
- The application is not designed to process real protected health information.

**Do not upload real patient records.**

---

## Next Steps

Planned improvements include:

- Upload synthetic PDFs directly through the reviewer interface
- Run the full pipeline from the UI
- Build a larger synthetic evaluation set
- Measure evidence retrieval accuracy
- Compare multiple models on the same evaluation set
- Track latency and cost per case
- Add structured audit records
- Improve navigation from evidence results to the source PDF

---

## What This Project Demonstrates

Although prior authorization is the example workflow, the broader engineering pattern is:

```text
Unstructured documents
        ↓
LLM-assisted understanding
        ↓
Structured, source-backed evidence
        ↓
Deterministic workflow logic
        ↓
Human-verifiable result
```

The same approach can be applied to other document-heavy workflows where information needs to be extracted, verified, and turned into structured actions.

---

## Safety

This repository is for educational and portfolio purposes only.

- All included patient information is synthetic.
- The included review criteria are synthetic educational examples.
- The application is not a medical device.
- It does not provide medical advice.
- It is not intended to make real prior authorization or coverage decisions.
- It should not be used with real patient information.
