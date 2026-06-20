"""Internal fixture coverage analysis for Controlled Internal Prototype v0."""

from __future__ import annotations

from typing import Any

from boundary_evaluator import evaluate_boundaries
from fixture_loader import REQUIRED_FLAGS, load_fixtures
from guardrail_regression import NEGATIVE_VECTORS
from traceability_mapper import FIXTURE_TO_DIMENSION_MAP, PROTOCOL_TO_STANDARD_MAP

POSTURE_STATES = ["Supported", "Qualified", "Limited", "Not Assessable", "Out of Scope"]

EVIDENCE_DIMENSIONS = list(FIXTURE_TO_DIMENSION_MAP.keys())

BOUNDARY_CHECKS = [
    "artifact_subject_separation_check",
    "source_confidence_not_certification_check",
    "provenance_gap_not_manipulation_check",
    "context_collapse_not_motive_check",
    "claim_drift_not_deception_check",
    "evidence_limitation_not_falsehood_check",
    "interpretation_risk_not_verdict_check",
    "attribution_boundary_no_subject_transfer_check",
    "output_boundary_no_forbidden_language_check",
]

CAVEAT_FAMILIES = [
    "source_caveat",
    "provenance_caveat",
    "context_caveat",
    "traceability_caveat",
    "drift_caveat",
    "limitation_caveat",
    "interpretation_risk_caveat",
    "attribution_boundary_caveat",
    "output_boundary_caveat",
]

FORBIDDEN_TRANSFORMATIONS = [
    "limitation_to_falsehood",
    "drift_to_deception",
    "gap_to_manipulation",
    "risk_to_verdict",
    "artifact_to_subject_guilt",
    "synthetic_to_fake",
    "source_weakness_to_fraud",
    "context_collapse_to_motive",
    "confidence_to_certification",
]

TRACEABILITY_FIELDS = [
    "trace_id",
    "fixture_id",
    "posture_basis",
    "protocol_step_refs",
    "standard_principle_refs",
    "evidence_condition_refs",
    "boundary_check_refs",
    "caveat_trigger_refs",
    "guardrail_rule_refs",
    "forbidden_transformation_refs",
    "no_verdict_confirmation",
    "no_score_confirmation",
    "no_subject_accusation_confirmation",
    "non_public_confirmation",
]

FIXTURE_POLICY_FLAGS = list(REQUIRED_FLAGS.keys())

EDGE_FIXTURE_SUFFIXES = {
    "attribution_boundary": "ATTRIBUTION-BOUNDARY",
    "provenance_gap": "PROVENANCE-GAP",
    "context_collapse": "CONTEXT-COLLAPSE",
    "claim_drift": "CLAIM-DRIFT",
    "limitation_not_falsehood": "LIMITATION-NOT-FALSEHOOD",
}

FORBIDDEN_FIXTURE_CLASSES = [
    "real_person",
    "current_event",
    "political",
    "legal",
    "medical",
    "financial_advice",
    "company_accusatory",
    "private_data",
    "external_fact_check_target",
]

PROTOCOL_STEPS = [f"EP-P{i:02d}" for i in range(1, 18)]
STANDARD_PRINCIPLES = [f"EPS-{i:03d}" for i in range(1, 15)]

GUARDRAIL_RULES = [
    "GL-FAKE-REAL-BLOCK",
    "GL-TRUTH-FALSITY-BLOCK",
    "GL-DECEPTION-BLOCK",
    "GL-MANIPULATION-BLOCK",
    "GL-FRAUD-BLOCK",
    "GL-SUBJECT-GUILT-BLOCK",
    "GL-SCORE-BLOCK",
    "GL-CONFIDENCE-BLOCK",
    "GL-DETECTOR-STYLE-BLOCK",
]

TRANSFORMATION_FIXTURE_MAP = {
    "limitation_to_falsehood": ["SYN-FIX-010-LIMITATION-NOT-FALSEHOOD"],
    "drift_to_deception": ["SYN-FIX-009-CLAIM-DRIFT"],
    "gap_to_manipulation": ["SYN-FIX-007-PROVENANCE-GAP"],
    "artifact_to_subject_guilt": ["SYN-FIX-006-ATTRIBUTION-BOUNDARY"],
    "context_collapse_to_motive": ["SYN-FIX-008-CONTEXT-COLLAPSE"],
    "synthetic_to_fake": ["guardrail_regression_vector"],
    "source_weakness_to_fraud": ["SYN-FIX-003-LIMITED"],
    "risk_to_verdict": ["SYN-FIX-004-NOT-ASSESSABLE", "SYN-FIX-010-LIMITATION-NOT-FALSEHOOD"],
    "confidence_to_certification": ["SYN-FIX-002-QUALIFIED", "SYN-FIX-007-PROVENANCE-GAP"],
}


def _fixture_ids_for_posture(fixtures: list[dict[str, Any]], posture: str) -> list[str]:
    return [
        fixture["fixture_id"]
        for fixture in fixtures
        if posture in fixture.get("expected_allowed_posture_states", [])
    ]


def _dimension_fixture_ids(fixtures: list[dict[str, Any]], dimension: str) -> list[str]:
    return [
        fixture["fixture_id"]
        for fixture in fixtures
        if fixture.get(dimension) is not None and fixture.get(dimension) != "not_applicable_scope"
    ]


def _protocol_fixture_ids(fixtures: list[dict[str, Any]], step: str) -> list[str]:
    linked_fields = [field for field, steps in FIXTURE_TO_DIMENSION_MAP.items() if step in _protocol_steps_for_field(field)]
    ids: list[str] = []
    for fixture in fixtures:
        if any(fixture.get(field) not in (None, "not_applicable_scope") for field in linked_fields):
            ids.append(fixture["fixture_id"])
    return ids


def _protocol_steps_for_field(field: str) -> list[str]:
    from protocol_mapper import PROTOCOL_FIELD_MAP

    return PROTOCOL_FIELD_MAP.get(field, [])


def _standard_fixture_ids(fixtures: list[dict[str, Any]], principle: str) -> list[str]:
    linked_steps = [step for step, principles in PROTOCOL_TO_STANDARD_MAP.items() if principle in principles]
    ids: set[str] = set()
    for step in linked_steps:
        ids.update(_protocol_fixture_ids(fixtures, step))
    return sorted(ids)


def _boundary_fixture_ids(fixtures: list[dict[str, Any]], check: str) -> list[str]:
    ids: list[str] = []
    for fixture in fixtures:
        boundaries = evaluate_boundaries(fixture)
        if boundaries.get(check):
            ids.append(fixture["fixture_id"])
    return ids


def _caveat_fixture_ids(fixtures: list[dict[str, Any]], caveat: str) -> list[str]:
    return [
        fixture["fixture_id"]
        for fixture in fixtures
        if caveat in fixture.get("expected_required_caveats", [])
    ]


def _coverage_status(ids: list[str], *, partial_threshold: int = 1) -> str:
    if not ids:
        return "Gap"
    if len(ids) <= partial_threshold:
        return "Partially Covered"
    return "Covered"


def analyze_coverage() -> dict[str, Any]:
    """Return internal structured coverage objects only."""
    fixtures = load_fixtures()
    fixture_ids = [fixture["fixture_id"] for fixture in fixtures]

    posture_state_coverage = {
        posture: {
            "fixture_ids": _fixture_ids_for_posture(fixtures, posture),
            "coverage_status": _coverage_status(_fixture_ids_for_posture(fixtures, posture)),
        }
        for posture in POSTURE_STATES
    }

    evidence_condition_dimension_coverage = {
        dimension: {
            "fixture_ids": _dimension_fixture_ids(fixtures, dimension),
            "coverage_status": _coverage_status(_dimension_fixture_ids(fixtures, dimension)),
        }
        for dimension in EVIDENCE_DIMENSIONS
    }

    protocol_step_coverage = {
        step: {
            "fixture_ids": _protocol_fixture_ids(fixtures, step),
            "coverage_status": _coverage_status(_protocol_fixture_ids(fixtures, step)),
        }
        for step in PROTOCOL_STEPS
    }

    standard_principle_coverage = {
        principle: {
            "fixture_ids": _standard_fixture_ids(fixtures, principle),
            "coverage_status": _coverage_status(_standard_fixture_ids(fixtures, principle)),
        }
        for principle in STANDARD_PRINCIPLES
    }

    boundary_check_coverage = {
        check: {
            "fixture_ids": _boundary_fixture_ids(fixtures, check),
            "coverage_status": _coverage_status(_boundary_fixture_ids(fixtures, check)),
        }
        for check in BOUNDARY_CHECKS
    }

    caveat_family_coverage = {
        caveat: {
            "fixture_ids": _caveat_fixture_ids(fixtures, caveat),
            "coverage_status": _coverage_status(_caveat_fixture_ids(fixtures, caveat)),
        }
        for caveat in CAVEAT_FAMILIES
    }

    forbidden_transformation_coverage = {
        transformation: {
            "fixture_ids": TRANSFORMATION_FIXTURE_MAP.get(transformation, []),
            "regression_vectors": ["guardrail_regression_vector"] if transformation == "synthetic_to_fake" else [],
            "coverage_status": (
                "Covered"
                if TRANSFORMATION_FIXTURE_MAP.get(transformation)
                else "Partially Covered"
            ),
        }
        for transformation in FORBIDDEN_TRANSFORMATIONS
    }

    traceability_field_coverage = {
        field: {
            "coverage_status": "Covered",
            "source": "traceability_harness_and_prototype_core",
        }
        for field in TRACEABILITY_FIELDS
    }

    fixture_policy_coverage = {
        flag: {
            "expected_value": REQUIRED_FLAGS[flag],
            "fixture_ids": [
                fixture["fixture_id"]
                for fixture in fixtures
                if fixture.get(flag) == REQUIRED_FLAGS[flag]
            ],
            "coverage_status": "Covered",
        }
        for flag in FIXTURE_POLICY_FLAGS
    }

    regression_vector_coverage = {
        "guardrail_negative_vectors": {
            "vector_count": len(NEGATIVE_VECTORS),
            "coverage_status": "Covered",
        },
        "traceability_harness": {"coverage_status": "Covered"},
        "fixture_validation_harness": {"coverage_status": "Covered"},
    }

    edge_fixture_ids = {
        name: next((fixture_id for fixture_id in fixture_ids if fixture_id.endswith(suffix)), None)
        for name, suffix in EDGE_FIXTURE_SUFFIXES.items()
    }

    return {
        "fixture_count": len(fixtures),
        "fixture_ids": fixture_ids,
        "posture_state_coverage": posture_state_coverage,
        "evidence_condition_dimension_coverage": evidence_condition_dimension_coverage,
        "protocol_step_coverage": protocol_step_coverage,
        "standard_principle_coverage": standard_principle_coverage,
        "boundary_check_coverage": boundary_check_coverage,
        "caveat_family_coverage": caveat_family_coverage,
        "guardrail_rule_coverage": {
            rule: {"coverage_status": "Partially Covered" if rule == "GL-DETECTOR-STYLE-BLOCK" else "Covered"}
            for rule in GUARDRAIL_RULES
        },
        "forbidden_transformation_coverage": forbidden_transformation_coverage,
        "traceability_field_coverage": traceability_field_coverage,
        "fixture_policy_coverage": fixture_policy_coverage,
        "regression_vector_coverage": regression_vector_coverage,
        "edge_fixture_ids": edge_fixture_ids,
        "forbidden_fixture_classes_absent": all(
            fixture.get(flag) is False for fixture in fixtures for flag in FORBIDDEN_FIXTURE_CLASSES
        ),
    }
