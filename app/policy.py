"""
Milestone 3: load policy criteria from JSON into a reusable data
structure.

No matching, no LLM calls, no decision logic - just loading.
"""

import json

POLICY_PATH = "policies/lumbar_mri.json"


def load_policy(path):
    with open(path) as f:
        return json.load(f)


def main():
    criteria = load_policy(POLICY_PATH)
    for criterion in criteria:
        print(f"{criterion['id']}: {criterion['description']}")


if __name__ == "__main__":
    main()
