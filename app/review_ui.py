"""
Milestone 7: read-only reviewer interface.

Pure consumer of already-generated pipeline output - reads JSON files
on disk, joins them, and displays them. Makes no API calls and does
not run any part of the pipeline itself.

Run with: streamlit run app/review_ui.py
Requires output/evidence_report.json and output/decision.json to
already exist (generate them with: python3 app/run_evidence_demo.py).
"""

import json

import streamlit as st

from review_data import merge_criteria_with_evidence

EVIDENCE_REPORT_PATH = "output/evidence_report.json"
DECISION_PATH = "output/decision.json"
POLICY_PATH = "policies/lumbar_mri.json"
CASE_NAME = "samples/sample.pdf"

STATUS_DISPLAY = {
    "satisfied": ("✅", "success", "Clear supporting evidence found."),
    "not_found": ("❌", "error", "Evidence not found in submitted documentation."),
    "unknown": ("❓", "warning", "The system could not safely determine this - needs human review."),
}

st.set_page_config(page_title="Prior Authorization Review")

with open(EVIDENCE_REPORT_PATH) as f:
    evidence_report = json.load(f)

with open(DECISION_PATH) as f:
    decision = json.load(f)

with open(POLICY_PATH) as f:
    criteria = json.load(f)

merged_criteria = merge_criteria_with_evidence(criteria, evidence_report)

st.title("Prior Authorization Review")
st.caption(f"Case: {CASE_NAME}")

st.subheader(f"Decision: {decision['decision'].upper()}")
if decision["reasons"]:
    for reason in decision["reasons"]:
        st.write(f"Reason: {reason}")
else:
    st.write("All criteria satisfied.")

st.divider()
st.subheader("Criteria")

for item in merged_criteria:
    icon, style, meaning = STATUS_DISPLAY[item["status"]]

    with st.container(border=True):
        st.markdown(f"**{icon} {item['id']} — {item['status']}**")
        st.write(item["description"])
        getattr(st, style)(meaning)

        if item["status"] == "satisfied":
            st.write(f"Page {item['page_number']}: \"{item['quote']}\"")
            if item.get("concern_present") is True:
                st.warning(
                    "A red flag / warning sign is actually present here - "
                    "needs human review, not an automatic bypass."
                )
