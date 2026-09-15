"""
One-off helper to generate synthetic, obviously-fake multi-page PDFs
so we have something to test extract_text.py and evidence.py against.

Not part of the app itself - just a way to create test data.

Each function below builds one packet designed to push the decision
engine toward a different outcome:

- make_baseline_pdf        -> mixed evidence (original sample.pdf)
- make_clean_approve_pdf   -> every criterion clearly satisfied -> approve
- make_missing_info_pdf    -> several criteria genuinely absent -> human_review
- make_ambiguous_pdf       -> deferred/vague/contradictory notes -> human_review
- make_offtopic_pdf        -> not a medical document at all -> tests that the
                              model does not hallucinate clinical evidence
                              out of unrelated text
- make_partial_groups_pdf  -> only ONE neuro finding and ONE conservative
                              care type documented (not all of either) ->
                              still approve, since decision.py treats each
                              of those as an any-one-of group
"""

import pymupdf


def make_baseline_pdf(path="samples/sample.pdf"):
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

    doc.save(path)
    doc.close()
    print(f"Wrote {path}")


def make_clean_approve_pdf(path="samples/sample_clean_approve.pdf"):
    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text(
        (72, 72),
        "REFERRAL LETTER\n\n"
        "Date: 02/01/2026 (fake)\n"
        "Re: Patient John Synthetic-Roe, DOB 05/05/1975 (fake)\n\n"
        "Patient is referred for lumbar spine MRI due to persistent low back\n"
        "pain radiating to the right leg, ongoing for 10 weeks.",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (72, 72),
        "PHYSICIAN EXAM NOTE\n\n"
        "Neurological exam:\n"
        "Motor strength is 3/5 in the right lower extremity, consistent with\n"
        "L5 radiculopathy.\n"
        "Sensory exam shows decreased sensation to light touch in the right\n"
        "L5 dermatome (dorsum of the right foot).\n"
        "Right ankle reflex is absent compared to a normal left ankle reflex,\n"
        "an asymmetric finding.\n"
        "Patient denies any bowel or bladder incontinence or retention.\n"
        "Patient denies fever, unexplained weight loss, recent trauma, or\n"
        "history of cancer.",
    )

    page3 = doc.new_page()
    page3.insert_text(
        (72, 72),
        "MEDICATION AND IMAGING HISTORY\n\n"
        "Conservative treatment: naproxen 500mg BID for 7 weeks, and\n"
        "methocarbamol for muscle spasm.\n"
        "Symptom duration is 10 weeks, per patient report and referral letter.\n"
        "Lumbar spine X-ray performed on 12/20/2025 showed mild degenerative\n"
        "disc changes at L4-L5, no fracture.",
    )

    page4 = doc.new_page()
    page4.insert_text(
        (72, 72),
        "PHYSICAL THERAPY NOTES\n\n"
        "Physical therapy: 10 sessions completed over 7 weeks, minimal\n"
        "improvement in pain or function.",
    )

    doc.save(path)
    doc.close()
    print(f"Wrote {path}")


def make_missing_info_pdf(path="samples/sample_missing_info.pdf"):
    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text(
        (72, 72),
        "REFERRAL LETTER\n\n"
        "Date: 03/10/2026 (fake)\n"
        "Re: Patient Alex Synthetic-Lee, DOB 09/09/1988 (fake)\n\n"
        "Patient is referred for lumbar spine MRI due to low back pain.\n"
        "Duration of symptoms is not specified in this letter.",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (72, 72),
        "PHYSICIAN EXAM NOTE\n\n"
        "Chief complaint: Low back pain, no radiation reported. Symptom\n"
        "duration is documented as 2 weeks, per patient report.\n\n"
        "Neurological exam: Full strength (5/5) in both lower extremities,\n"
        "bilaterally symmetric. Sensation is intact to light touch throughout\n"
        "both lower extremities. Deep tendon reflexes are 2+ and symmetric\n"
        "bilaterally. Patient denies bowel or bladder changes. Patient denies\n"
        "fever, unexplained weight loss, trauma, or history of cancer.",
    )

    page3 = doc.new_page()
    page3.insert_text(
        (72, 72),
        "TREATMENT NOTE\n\n"
        "Patient has not tried any medication for this pain and has not\n"
        "started physical therapy - both are confirmed absent by patient\n"
        "interview today. No prior imaging of the lumbar spine has ever been\n"
        "performed, confirmed by chart review.",
    )

    doc.save(path)
    doc.close()
    print(f"Wrote {path}")


def make_partial_groups_pdf(path="samples/sample_partial_groups.pdf"):
    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text(
        (72, 72),
        "REFERRAL LETTER\n\n"
        "Date: 05/12/2026 (fake)\n"
        "Re: Patient Robin Synthetic-Park, DOB 03/03/1980 (fake)\n\n"
        "Patient referred for lumbar spine MRI due to low back pain\n"
        "radiating to the left leg, ongoing for 9 weeks.",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (72, 72),
        "PHYSICIAN EXAM NOTE\n\n"
        "Neurological exam: Motor strength is 4/5 in the left lower\n"
        "extremity, a mild but clear weakness in the L5 distribution.\n"
        "Sensation is intact throughout. Deep tendon reflexes are 2+ and\n"
        "symmetric bilaterally. Patient denies bowel or bladder changes.\n"
        "Patient denies fever, unexplained weight loss, trauma, or history\n"
        "of cancer.",
    )

    page3 = doc.new_page()
    page3.insert_text(
        (72, 72),
        "TREATMENT AND IMAGING HISTORY\n\n"
        "Patient has not tried any medication for this pain.\n"
        "Physical therapy: 6 sessions completed over 6 weeks, mild\n"
        "improvement noted.\n"
        "Symptom duration is 9 weeks, per patient report and referral\n"
        "letter.\n"
        "Lumbar spine X-ray performed on 01/05/2026 showed no acute\n"
        "findings.",
    )

    doc.save(path)
    doc.close()
    print(f"Wrote {path}")


def make_offtopic_pdf(path="samples/sample_offtopic.pdf"):
    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text(
        (72, 72),
        "WEEKLY GROCERY LIST\n\n"
        "Milk, eggs, bread, spinach, chicken breast, rice, olive oil,\n"
        "tomatoes, coffee, bananas.\n\n"
        "Remember to check if the store has the discount on paper towels\n"
        "this week.",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (72, 72),
        "WEEKEND WEATHER FORECAST\n\n"
        "Saturday: Sunny, high of 72F, light breeze from the west.\n"
        "Sunday: Partly cloudy, high of 68F, chance of light rain in the\n"
        "evening.\n"
        "Good weekend for outdoor activities on Saturday.",
    )

    doc.save(path)
    doc.close()
    print(f"Wrote {path}")


def make_ambiguous_pdf(path="samples/sample_ambiguous.pdf"):
    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text(
        (72, 72),
        "REFERRAL LETTER\n\n"
        "Date: 04/22/2026 (fake)\n"
        "Re: Patient Sam Synthetic-Kim, DOB 11/11/1965 (fake)\n\n"
        "Patient referred for lumbar spine MRI for chronic low back pain.\n"
        "Symptom onset date is unclear from prior records; patient reports\n"
        "'a while now, maybe a couple months, hard to say.'",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (72, 72),
        "PHYSICIAN EXAM NOTE\n\n"
        "Neurological exam: Strength testing limited by patient effort and\n"
        "pain behavior; results inconsistent between trials and not\n"
        "considered reliable. Sensory exam deferred - patient too\n"
        "uncomfortable to complete testing today. Reflex testing not\n"
        "performed this visit. Patient gives conflicting answers about\n"
        "bladder symptoms - first denies any issue, then later mentions\n"
        "'maybe some trouble going, not sure.' Chart notes a history of\n"
        "cancer per old records, but patient states this is inaccurate and\n"
        "the notes may refer to a different patient.",
    )

    page3 = doc.new_page()
    page3.insert_text(
        (72, 72),
        "TREATMENT NOTE\n\n"
        "Patient mentions taking 'something over the counter sometimes' for\n"
        "the pain, name and dose not recorded. Physical therapy status\n"
        "unclear - patient believes a prior provider 'may have mentioned it'\n"
        "but no referral or session notes are on file.",
    )

    doc.save(path)
    doc.close()
    print(f"Wrote {path}")


if __name__ == "__main__":
    make_baseline_pdf()
    make_clean_approve_pdf()
    make_missing_info_pdf()
    make_ambiguous_pdf()
    make_offtopic_pdf()
    make_partial_groups_pdf()
