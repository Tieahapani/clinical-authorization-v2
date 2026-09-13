import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from policy import load_policy

POLICY_PATH = Path(__file__).resolve().parent.parent / "policies" / "lumbar_mri.json"

EXPECTED_IDS = [
    "NRC.weakness",
    "NRC.sensory_loss",
    "NRC.reflex_change",
    "NRC.bowel_bladder",
    "CM.medication",
    "CM.physical_therapy",
    "CM.duration",
    "SX.duration",
    "IMG.prior_imaging",
    "RF.red_flag",
]


def test_load_policy_returns_ten_criteria():
    criteria = load_policy(str(POLICY_PATH))
    assert len(criteria) == 10


def test_expected_criterion_ids_present():
    criteria = load_policy(str(POLICY_PATH))
    ids = [c["id"] for c in criteria]
    assert ids == EXPECTED_IDS


def test_each_criterion_has_id_and_description():
    criteria = load_policy(str(POLICY_PATH))
    for c in criteria:
        assert "id" in c
        assert "description" in c
