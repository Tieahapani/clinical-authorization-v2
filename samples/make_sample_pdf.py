"""
One-off helper to generate a synthetic, obviously-fake multi-page PDF
so we have something to test extract_text.py and evidence.py against.

Not part of the app itself - just a way to create test data.
"""

import pymupdf

doc = pymupdf.open()

page1 = doc.new_page()
page1.insert_text(
    (72, 72),
    "REFERRAL LETTER\n\n"
    "Date: 01/15/2026 (fake)\n"
    "To: Radiology Prior Authorization Department\n"
    "Re: Patient Jane Synthetic-Doe, DOB 01/01/1990 (fake)\n\n"
    "Patient is referred for lumbar spine MRI due to persistent low back\n"
    "pain radiating to the left leg, ongoing for approximately 8 weeks.\n"
    "Please see attached clinical documentation.",
)

page2 = doc.new_page()
page2.insert_text(
    (72, 72),
    "PHYSICIAN EXAM NOTE\n\n"
    "Chief complaint: Low back pain with left leg radiation, duration 8 weeks.\n\n"
    "Neurological exam:\n"
    "Motor strength is 4-/5 in the left lower extremity (L5 distribution).\n"
    "Sensory exam reveals decreased sensation to light touch along the\n"
    "lateral left calf and dorsum of the left foot.\n"
    "Deep tendon reflexes deferred due to patient guarding; unable to\n"
    "reliably assess.\n"
    "Patient denies any bowel or bladder incontinence or retention.\n"
    "Patient denies fever, unexplained weight loss, recent trauma, or\n"
    "history of cancer.",
)

page3 = doc.new_page()
page3.insert_text(
    (72, 72),
    "MEDICATION AND TREATMENT HISTORY\n\n"
    "Conservative treatment: ibuprofen 600mg TID, documented for 6 weeks.\n"
    "Also trialed cyclobenzaprine 5mg at bedtime for muscle spasm.\n"
    "No prior lumbar spine imaging on file.",
)

page4 = doc.new_page()
page4.insert_text(
    (72, 72),
    "PHYSICAL THERAPY NOTES\n\n"
    "Physical therapy: 8 sessions completed over 6 weeks, no significant\n"
    "improvement noted.\n"
    "Patient continues to report left leg pain despite therapy.",
)

doc.save("samples/sample.pdf")
doc.close()

print("Wrote samples/sample.pdf")
