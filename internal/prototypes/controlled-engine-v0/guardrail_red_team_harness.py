"""Local guardrail red-team harness for Controlled Internal Prototype v0."""

from __future__ import annotations

import sys
from pathlib import Path

PROTOTYPE_ROOT = Path(__file__).resolve().parent
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

from fixture_loader import load_fixtures  # noqa: E402
from guardrail_red_team_pack import RED_TEAM_VECTORS, analyze_red_team_pack  # noqa: E402

MIN_VECTORS = 16
MAX_FIXTURE_COUNT = 16
REQUIRED_RESULT_FIELDS = [
    "red_team_case_id",
    "vector_class",
    "pressure_target",
    "forbidden_language_target",
    "expected_guardrail_block",
    "required_caveat_preservation",
    "required_traceability_refs",
    "non_verdict_confirmation",
    "non_score_confirmation",
    "non_public_confirmation",
]


def main() -> int:
    fixtures = load_fixtures()
    if len(fixtures) != MAX_FIXTURE_COUNT:
        return 1

    results = analyze_red_team_pack()
    if len(results) < MIN_VECTORS:
        return 1
    if len(results) != len(RED_TEAM_VECTORS):
        return 1

    for result in results:
        for field in REQUIRED_RESULT_FIELDS:
            if field not in result:
                return 1
        if result.get("red_team_validation_status") != "pass":
            return 1
        if result.get("collapse_prevention_status") != "pass":
            return 1
        if not result.get("guardrail_blocked"):
            return 1
        if not result.get("non_verdict_confirmation"):
            return 1
        if not result.get("non_score_confirmation"):
            return 1
        if not result.get("non_public_confirmation"):
            return 1

    print("controlled internal guardrail red-team validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
