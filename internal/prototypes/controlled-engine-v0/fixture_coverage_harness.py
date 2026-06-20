"""Local fixture coverage harness for Controlled Internal Prototype v0."""

from __future__ import annotations

import sys
from pathlib import Path

PROTOTYPE_ROOT = Path(__file__).resolve().parent
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

from fixture_coverage_analyzer import (  # noqa: E402
    EDGE_FIXTURE_SUFFIXES,
    POSTURE_STATES,
    TRACEABILITY_FIELDS,
    analyze_coverage,
)

REQUIRED_CATEGORIES = [
    "posture_state_coverage",
    "evidence_condition_dimension_coverage",
    "protocol_step_coverage",
    "standard_principle_coverage",
    "boundary_check_coverage",
    "caveat_family_coverage",
    "guardrail_rule_coverage",
    "forbidden_transformation_coverage",
    "traceability_field_coverage",
    "fixture_policy_coverage",
    "regression_vector_coverage",
]


def main() -> int:
    coverage = analyze_coverage()
    for category in REQUIRED_CATEGORIES:
        if category not in coverage:
            return 1

    for posture in POSTURE_STATES:
        if not coverage["posture_state_coverage"].get(posture, {}).get("fixture_ids"):
            return 1

    for edge_name, suffix in EDGE_FIXTURE_SUFFIXES.items():
        edge_id = coverage["edge_fixture_ids"].get(edge_name)
        if not edge_id or not str(edge_id).endswith(suffix):
            return 1

    if len(coverage.get("traceability_field_coverage", {})) < len(TRACEABILITY_FIELDS):
        return 1

    if not coverage.get("forbidden_fixture_classes_absent"):
        return 1

    print("controlled internal fixture coverage validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
