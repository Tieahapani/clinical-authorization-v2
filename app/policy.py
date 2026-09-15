"""
Milestone 3: load policy criteria from JSON into a reusable data
structure.

No matching, no LLM calls, no decision logic - just loading.
"""

import json

POLICY_PATH = "policies/lumbar_mri.json"

# Bumped by hand whenever policies/lumbar_mri.json changes in a way that
# affects criteria, groups, or is_concern_criterion flags - lets the
# audit log record which version of the policy a case was evaluated
# against.
POLICY_VERSION = "1.0.0"


def load_policy(path):
    with open(path) as f:
        return json.load(f)


def main():
    criteria = load_policy(POLICY_PATH)
    for criterion in criteria:
        print(f"{criterion['id']}: {criterion['description']}")


if __name__ == "__main__":
    main()
