"""
Ground truth for the eval suite.

Each case names a synthetic packet (see samples/make_sample_pdf.py) and
the status we expect find_evidence to return for every policy criterion,
plus the decision we expect decide_authorization to reach from those
statuses. Ground truth was written by re-reading each packet against the
policy criteria descriptions - it is a human judgment call, same as a
real reviewer would make, not something derived from the code under test.

"expected_concern" is optional and only set for criteria where the
packet deliberately shows a red flag / warning sign being explicitly
ruled out (concern_present should be False) - it lets the eval catch a
regression where the model reports "satisfied" but forgets to say
whether the concerning finding was ruled out or is actually present.

Note: NRC.bowel_bladder is written as a red-flag-style criterion too
("possible cauda equina concern" in its own description), so an
explicit denial there ("patient denies bowel or bladder changes")
correctly comes back "satisfied" with concern_present=False, the same
as RF.red_flag - not "not_found". Confirmed empirically: the model
does this consistently on unambiguous denials.
"""

EVAL_CASES = [
    {
        "name": "clean_approve",
        "pdf_path": "samples/sample_clean_approve.pdf",
        "expected_status": {
            "NRC.weakness": "satisfied",
            "NRC.sensory_loss": "satisfied",
            "NRC.reflex_change": "satisfied",
            "NRC.bowel_bladder": "satisfied",
            "CM.medication": "satisfied",
            "CM.physical_therapy": "satisfied",
            "CM.duration": "satisfied",
            "SX.duration": "satisfied",
            "IMG.prior_imaging": "satisfied",
            "RF.red_flag": "satisfied",
        },
        "expected_concern": {
            "NRC.bowel_bladder": False,
            "RF.red_flag": False,
        },
        "expected_decision": "approve",
    },
    {
        "name": "missing_info",
        "pdf_path": "samples/sample_missing_info.pdf",
        "expected_status": {
            "NRC.weakness": "not_found",
            "NRC.sensory_loss": "not_found",
            "NRC.reflex_change": "not_found",
            "NRC.bowel_bladder": "satisfied",
            "CM.medication": "not_found",
            "CM.physical_therapy": "not_found",
            "CM.duration": "not_found",
            "SX.duration": "not_found",
            "IMG.prior_imaging": "not_found",
            "RF.red_flag": "satisfied",
        },
        "expected_concern": {
            "NRC.bowel_bladder": False,
            "RF.red_flag": False,
        },
        "expected_decision": "human_review",
    },
    {
        "name": "ambiguous",
        "pdf_path": "samples/sample_ambiguous.pdf",
        "expected_status": {
            "NRC.weakness": "unknown",
            "NRC.sensory_loss": "unknown",
            "NRC.reflex_change": "unknown",
            "NRC.bowel_bladder": "unknown",
            "CM.medication": "unknown",
            "CM.physical_therapy": "unknown",
            "CM.duration": "unknown",
            "SX.duration": "unknown",
            "IMG.prior_imaging": "not_found",
            "RF.red_flag": "unknown",
        },
        "expected_decision": "human_review",
    },
    {
        "name": "partial_groups",
        "pdf_path": "samples/sample_partial_groups.pdf",
        "expected_status": {
            "NRC.weakness": "satisfied",
            "NRC.sensory_loss": "not_found",
            "NRC.reflex_change": "not_found",
            "NRC.bowel_bladder": "satisfied",
            "CM.medication": "not_found",
            "CM.physical_therapy": "satisfied",
            "CM.duration": "satisfied",
            "SX.duration": "satisfied",
            "IMG.prior_imaging": "satisfied",
            "RF.red_flag": "satisfied",
        },
        "expected_concern": {
            "NRC.bowel_bladder": False,
            "RF.red_flag": False,
        },
        "expected_decision": "approve",
    },
    {
        "name": "offtopic",
        "pdf_path": "samples/sample_offtopic.pdf",
        "expected_status": {
            "NRC.weakness": "not_found",
            "NRC.sensory_loss": "not_found",
            "NRC.reflex_change": "not_found",
            "NRC.bowel_bladder": "not_found",
            "CM.medication": "not_found",
            "CM.physical_therapy": "not_found",
            "CM.duration": "not_found",
            "SX.duration": "not_found",
            "IMG.prior_imaging": "not_found",
            "RF.red_flag": "not_found",
        },
        "expected_decision": "human_review",
    },
]
