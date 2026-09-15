"""
Manual smoke test (not part of pytest) - calls the real Claude API
once per criterion, against samples/sample.pdf, then applies the
deterministic decision engine to the resulting evidence report.

Run with: python3 app/run_evidence_demo.py [path/to/sample.pdf]
Defaults to samples/sample.pdf if no path is given.
Requires ANTHROPIC_API_KEY - set it in a .env file in the project root,
or as a real environment variable.
"""

import json
import sys

from dotenv import load_dotenv

load_dotenv()

from extract_text import extract_pages
from policy import load_policy
from evidence import evaluate_all_criteria
from decision import decide_authorization

EVIDENCE_OUTPUT_PATH = "output/evidence_report.json"
DECISION_OUTPUT_PATH = "output/decision.json"

sample_path = sys.argv[1] if len(sys.argv) > 1 else "samples/sample.pdf"

pages = extract_pages(sample_path)
criteria = load_policy("policies/lumbar_mri.json")

results = evaluate_all_criteria(criteria, pages)
for result in results:
    print(result)

with open(EVIDENCE_OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"Wrote {EVIDENCE_OUTPUT_PATH}")

outcome = decide_authorization(results, criteria)
print(outcome)

with open(DECISION_OUTPUT_PATH, "w") as f:
    json.dump(outcome, f, indent=2)
print(f"Wrote {DECISION_OUTPUT_PATH}")
