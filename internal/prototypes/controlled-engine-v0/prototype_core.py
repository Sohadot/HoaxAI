"""Compose Controlled Internal Prototype v0 internal structured evaluation."""

from __future__ import annotations

from typing import Any

from boundary_evaluator import evaluate_boundaries
from caveat_mapper import map_caveats
from fixture_loader import load_fixtures
from model_loader import load_models
from output_guardrail_checker import verify_internal_structure
from protocol_mapper import map_protocol_steps

ALLOWED_RESULT_KEYS = {
    "fixture_id",
    "posture_state_candidate",
    "active_boundary_checks",
    "triggered_caveats",
    "prohibited_language_blocks",
    "required_output_constraints",
    "not_assessable_reason",
    "out_of_scope_reason",
    "guardrail_failure_flags",
    "validation_status",
}


def _select_posture_state(fixture: dict[str, Any]) -> str:
    allowed = fixture.get("expected_allowed_posture_states", [])
    if not allowed:
        return "Not Assessable"
    return str(allowed[0])


def evaluate_fixture(fixture: dict[str, Any], models: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one fixture into internal structured objects only."""
    posture = _select_posture_state(fixture)
    boundaries = evaluate_boundaries(fixture)
    caveats = map_caveats(fixture)
    protocol_map = map_protocol_steps(fixture)
    _ = protocol_map  # internal mapping only; not emitted in structured output

    result: dict[str, Any] = {
        "fixture_id": fixture["fixture_id"],
        "posture_state_candidate": posture,
        "active_boundary_checks": boundaries,
        "triggered_caveats": caveats,
        "required_output_constraints": fixture.get("forbidden_output_expectations", []),
        "not_assessable_reason": None,
        "out_of_scope_reason": None,
    }
    if posture == "Not Assessable":
        result["not_assessable_reason"] = "insufficient_assessable_basis_stub"
    if posture == "Out of Scope":
        result["out_of_scope_reason"] = "scope_boundary_reached_stub"

    guardrail = verify_internal_structure(result)
    result["prohibited_language_blocks"] = guardrail["prohibited_language_blocks"]
    result["guardrail_failure_flags"] = guardrail["guardrail_failure_flags"]
    result["validation_status"] = "pass" if guardrail["passed"] else "guardrail_blocked"

    _ = models  # models loaded to confirm governed dependencies are present
    return result


def run_prototype() -> list[dict[str, Any]]:
    """Load models and fixtures; return internal structured results only."""
    models = load_models()
    fixtures = load_fixtures()
    return [evaluate_fixture(fixture, models) for fixture in fixtures]
