"""Evaluate internal boundary checks for Controlled Internal Prototype v0."""

from __future__ import annotations

from typing import Any


def _status_passes(value: str, pass_markers: tuple[str, ...]) -> bool:
    lower = str(value).lower()
    return any(marker in lower for marker in pass_markers)


def evaluate_boundaries(fixture: dict[str, Any]) -> dict[str, bool]:
    """Return structured boundary-check flags only."""
    return {
        "artifact_subject_separation_check": _status_passes(
            fixture.get("attribution_boundary_status", ""),
            ("separated", "boundary_reached", "within"),
        ),
        "source_confidence_not_certification_check": "certification" not in str(
            fixture.get("source_confidence", "")
        ).lower(),
        "provenance_gap_not_manipulation_check": "manipulation" not in str(
            fixture.get("provenance_status", "")
        ).lower(),
        "context_collapse_not_motive_check": "motive" not in str(
            fixture.get("context_status", "")
        ).lower(),
        "claim_drift_not_deception_check": "deception" not in str(fixture.get("drift_status", "")).lower(),
        "evidence_limitation_not_falsehood_check": "falsehood" not in str(
            fixture.get("limitation_status", "")
        ).lower(),
        "interpretation_risk_not_verdict_check": "verdict" not in str(
            fixture.get("interpretation_risk_status", "")
        ).lower(),
        "attribution_boundary_no_subject_transfer_check": _status_passes(
            fixture.get("attribution_boundary_status", ""),
            ("separated", "boundary_reached"),
        ),
        "output_boundary_no_forbidden_language_check": _status_passes(
            fixture.get("output_boundary_status", ""),
            ("within", "boundary"),
        ),
    }
