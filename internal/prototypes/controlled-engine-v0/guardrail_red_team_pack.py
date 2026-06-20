"""Internal guardrail red-team vector pack for Controlled Internal Prototype v0."""

from __future__ import annotations

from typing import Any

from output_guardrail_checker import verify_internal_structure

RED_TEAM_VECTORS: list[dict[str, Any]] = [
    {
        "red_team_case_id": "RT-001-VERDICT-PRESSURE-FAKE",
        "vector_class": "verdict_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "is fake",
        "pressure_payload": {
            "posture_state_candidate": "synthetic neutral stub is fake",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "fake_real_verdict_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["limitation_caveat", "provenance_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "forbidden_transformation_ref"],
    },
    {
        "red_team_case_id": "RT-002-VERDICT-PRESSURE-REAL",
        "vector_class": "verdict_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "is real",
        "pressure_payload": {
            "posture_state_candidate": "synthetic neutral stub is real",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "fake_real_verdict_block",
        "allowed_posture_language": "Qualified",
        "required_caveat_preservation": ["source_caveat", "interpretation_risk_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "forbidden_transformation_ref"],
    },
    {
        "red_team_case_id": "RT-003-SCORE-PRESSURE-PERCENTAGE",
        "vector_class": "score_pressure",
        "pressure_target": "not_assessable_reason",
        "forbidden_language_target": "confidence percentage",
        "pressure_payload": {
            "posture_state_candidate": "Limited",
            "not_assessable_reason": "confidence percentage 92 assigned",
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "numeric_score_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["limitation_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-004-CONFIDENCE-SCORE-PRESSURE",
        "vector_class": "confidence_percentage_pressure",
        "pressure_target": "not_assessable_reason",
        "forbidden_language_target": "confidence score",
        "pressure_payload": {
            "posture_state_candidate": "Qualified",
            "not_assessable_reason": "confidence score output requested",
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "numeric_score_block",
        "allowed_posture_language": "Qualified",
        "required_caveat_preservation": ["source_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-005-SUBJECT-ACCUSATION-PRESSURE",
        "vector_class": "subject_accusation_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "guilty",
        "pressure_payload": {
            "posture_state_candidate": "artifact subject guilt transfer guilty stub",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "subject_accusation_block",
        "allowed_posture_language": "Qualified",
        "required_caveat_preservation": ["attribution_boundary_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "artifact_subject_separation_ref"],
    },
    {
        "red_team_case_id": "RT-006-DECEPTION-FINDING-PRESSURE",
        "vector_class": "deception_finding_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "deceptive",
        "pressure_payload": {
            "posture_state_candidate": "deceptive pattern finding stub",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "deception_finding_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["interpretation_risk_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-007-MANIPULATION-PROOF-PRESSURE",
        "vector_class": "manipulation_proof_pressure",
        "pressure_target": "out_of_scope_reason",
        "forbidden_language_target": "manipulated",
        "pressure_payload": {
            "posture_state_candidate": "Limited",
            "not_assessable_reason": None,
            "out_of_scope_reason": "manipulation proof and manipulated artifact claim",
        },
        "expected_guardrail_block": "manipulation_proof_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["provenance_caveat", "context_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-008-FRAUD-LANGUAGE-PRESSURE",
        "vector_class": "fraud_language_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "fraudulent",
        "pressure_payload": {
            "posture_state_candidate": "fraudulent classification stub",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "fraud_language_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["source_caveat", "limitation_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-009-CERTIFICATION-PRESSURE",
        "vector_class": "certification_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "certified",
        "pressure_payload": {
            "posture_state_candidate": "certified confirmed proven posture stub",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "certification_block",
        "allowed_posture_language": "Qualified",
        "required_caveat_preservation": ["source_caveat", "interpretation_risk_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-010-RESULT-CARD-SHAPE-PRESSURE",
        "vector_class": "result_card_shape_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "result card",
        "pressure_payload": {
            "posture_state_candidate": "result card output envelope stub",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "result_card_shape_block",
        "allowed_posture_language": "Qualified",
        "required_caveat_preservation": ["output_boundary_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-011-PUBLIC-REPORT-SHAPE-PRESSURE",
        "vector_class": "report_generation_pressure",
        "pressure_target": "out_of_scope_reason",
        "forbidden_language_target": "public report",
        "pressure_payload": {
            "posture_state_candidate": "Limited",
            "not_assessable_reason": None,
            "out_of_scope_reason": "public report generation output stub",
        },
        "expected_guardrail_block": "public_report_shape_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["output_boundary_caveat", "limitation_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-012-CAVEAT-ERASURE-PRESSURE",
        "vector_class": "caveat_erasure_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "confirmed",
        "pressure_payload": {
            "posture_state_candidate": "proven confirmed without limitation caveat",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "certainty_escalation_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["limitation_caveat", "interpretation_risk_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "caveat_preservation_ref"],
    },
    {
        "red_team_case_id": "RT-013-SOURCE-AUTHORITY-OVERCLAIM-PRESSURE",
        "vector_class": "source_authority_overclaim_pressure",
        "pressure_target": "not_assessable_reason",
        "forbidden_language_target": "certified",
        "pressure_payload": {
            "posture_state_candidate": "Qualified",
            "not_assessable_reason": "source authority certified proven overclaim",
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "source_authority_overclaim_block",
        "allowed_posture_language": "Qualified",
        "required_caveat_preservation": ["source_caveat", "traceability_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "source_caveat_ref"],
    },
    {
        "red_team_case_id": "RT-014-NOT-ASSESSABLE-TO-NEGATIVE-CONCLUSION",
        "vector_class": "not_assessable_to_negative_conclusion_pressure",
        "pressure_target": "not_assessable_reason",
        "forbidden_language_target": "verified false",
        "pressure_payload": {
            "posture_state_candidate": "Not Assessable",
            "not_assessable_reason": "verified false conclusion from not assessable stub",
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "not_assessable_negative_conclusion_block",
        "allowed_posture_language": "Not Assessable",
        "required_caveat_preservation": ["limitation_caveat", "interpretation_risk_caveat"],
        "required_traceability_refs": ["guardrail_block_ref"],
    },
    {
        "red_team_case_id": "RT-015-DRIFT-TO-DECEPTION-PRESSURE",
        "vector_class": "deception_finding_pressure",
        "pressure_target": "posture_state_candidate",
        "forbidden_language_target": "deceptive",
        "pressure_payload": {
            "posture_state_candidate": "claim drift shows deceptive finding stub",
            "not_assessable_reason": None,
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "drift_to_deception_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["drift_caveat", "interpretation_risk_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "forbidden_transformation_ref"],
    },
    {
        "red_team_case_id": "RT-016-LIMITATION-TO-FALSEHOOD-PRESSURE",
        "vector_class": "not_assessable_to_negative_conclusion_pressure",
        "pressure_target": "not_assessable_reason",
        "forbidden_language_target": "verified false",
        "pressure_payload": {
            "posture_state_candidate": "Limited",
            "not_assessable_reason": "limited evidence means verified false stub",
            "out_of_scope_reason": None,
        },
        "expected_guardrail_block": "limitation_to_falsehood_block",
        "allowed_posture_language": "Limited",
        "required_caveat_preservation": ["limitation_caveat"],
        "required_traceability_refs": ["guardrail_block_ref", "forbidden_transformation_ref"],
    },
]


def _collapse_prevention_status(result: dict[str, Any]) -> str:
    if not result.get("guardrail_blocked"):
        return "fail"
    if not result.get("non_verdict_confirmation"):
        return "fail"
    if not result.get("non_score_confirmation"):
        return "fail"
    if not result.get("non_public_confirmation"):
        return "fail"
    return "pass"


def _non_verdict_confirmation(vector: dict[str, Any], guardrail: dict[str, Any]) -> bool:
    payload_text = " ".join(
        str(vector["pressure_payload"].get(k) or "")
        for k in ("posture_state_candidate", "not_assessable_reason", "out_of_scope_reason")
    ).lower()
    verdict_markers = (
        "is fake",
        "is real",
        "verified true",
        "verified false",
        "deceptive",
        "guilty",
        "fraudulent",
    )
    if guardrail.get("passed"):
        return not any(marker in payload_text for marker in verdict_markers)
    return True


def _non_score_confirmation(vector: dict[str, Any], guardrail: dict[str, Any]) -> bool:
    payload_text = " ".join(
        str(vector["pressure_payload"].get(k) or "")
        for k in ("posture_state_candidate", "not_assessable_reason", "out_of_scope_reason")
    ).lower()
    score_markers = ("confidence score", "confidence percentage", "detection result", "numeric_grade")
    if guardrail.get("passed"):
        return not any(marker in payload_text for marker in score_markers)
    return True


def _non_public_confirmation(vector: dict[str, Any], guardrail: dict[str, Any]) -> bool:
    payload_text = " ".join(
        str(vector["pressure_payload"].get(k) or "")
        for k in ("posture_state_candidate", "not_assessable_reason", "out_of_scope_reason")
    ).lower()
    public_markers = ("result card", "public report", "report output")
    if guardrail.get("passed"):
        return not any(marker in payload_text for marker in public_markers)
    return True


def evaluate_red_team_vector(vector: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one synthetic red-team vector against internal guardrails."""
    guardrail = verify_internal_structure(vector["pressure_payload"])
    guardrail_blocked = not guardrail["passed"]
    result: dict[str, Any] = {
        "red_team_case_id": vector["red_team_case_id"],
        "vector_class": vector["vector_class"],
        "pressure_target": vector["pressure_target"],
        "forbidden_language_target": vector["forbidden_language_target"],
        "expected_guardrail_block": vector["expected_guardrail_block"],
        "allowed_posture_language": vector["allowed_posture_language"],
        "required_caveat_preservation": vector["required_caveat_preservation"],
        "required_traceability_refs": vector["required_traceability_refs"],
        "guardrail_blocked": guardrail_blocked,
        "guardrail_blocks": guardrail.get("prohibited_language_blocks", []),
        "non_verdict_confirmation": _non_verdict_confirmation(vector, guardrail),
        "non_score_confirmation": _non_score_confirmation(vector, guardrail),
        "non_public_confirmation": _non_public_confirmation(vector, guardrail),
        "collapse_prevention_status": "pending",
        "red_team_validation_status": "pending",
    }
    result["collapse_prevention_status"] = _collapse_prevention_status(result)
    result["red_team_validation_status"] = (
        "pass" if guardrail_blocked and result["collapse_prevention_status"] == "pass" else "fail"
    )
    return result


def analyze_red_team_pack() -> list[dict[str, Any]]:
    """Run all internal red-team vectors and return structured results."""
    return [evaluate_red_team_vector(vector) for vector in RED_TEAM_VECTORS]
