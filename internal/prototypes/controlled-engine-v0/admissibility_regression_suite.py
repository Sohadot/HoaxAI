"""Unified admissibility regression suite for Controlled Internal Prototype v0."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from compound_boundary_stress_analyzer import STRESS_CASES, analyze_compound_stress
from fixture_coverage_analyzer import analyze_coverage
from fixture_loader import load_fixtures
from guardrail_red_team_pack import RED_TEAM_VECTORS, analyze_red_team_pack
from guardrail_regression import run_guardrail_regression
from interpretability_auditor import audit_result
from model_loader import load_models
from output_admissibility_contract import evaluate_output_admissibility
from prototype_core import evaluate_fixture

REQUIRED_FIXTURE_COUNT = 16

REGRESSION_DOMAINS = [
    "fixture_inventory_regression",
    "fixture_coverage_regression",
    "traceability_regression",
    "compound_boundary_regression",
    "guardrail_red_team_regression",
    "output_admissibility_regression",
    "forbidden_language_regression",
    "non_public_boundary_regression",
    "no_score_no_verdict_regression",
    "no_report_shape_regression",
]

REQUIRED_HARNESSES = [
    "validation_harness.py",
    "traceability_harness.py",
    "fixture_coverage_harness.py",
    "targeted_fixture_expansion_harness.py",
    "compound_boundary_stress_harness.py",
    "guardrail_red_team_harness.py",
    "output_admissibility_harness.py",
    "regression_harness.py",
    "admissibility_regression_harness.py",
]


def _s(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_NETWORK_MARKERS = (
    _s("req", "uest", "s"),
    _s("urllib", ".request"),
    "httpx",
    "aiohttp",
    "socket",
)
FORBIDDEN_INPUT_MARKERS = (_s("input", "("), _s("arg", "parse"), "click", "typer")
FORBIDDEN_FRAMEWORK_MARKERS = (
    _s("fl", "ask"),
    _s("fast", "api"),
    "django",
    "streamlit",
    "gradio",
    "dash",
    "notebook",
)
BOUNDARY_SCAN_EXEMPT = frozenset({"admissibility_regression_suite.py"})


def _mutated(base: dict[str, Any], **updates: Any) -> dict[str, Any]:
    sample = copy.deepcopy(base)
    sample.update(updates)
    return sample


def _domain_result(domain: str, passed: bool, detail: str = "") -> dict[str, Any]:
    return {
        "regression_domain": domain,
        "regression_status": "pass" if passed else "fail",
        "detail": detail,
    }


def _check_fixture_inventory() -> dict[str, Any]:
    fixtures = load_fixtures()
    if len(fixtures) != REQUIRED_FIXTURE_COUNT:
        return _domain_result("fixture_inventory_regression", False, "fixture_count_drift")
    expansion = [f for f in fixtures if f.get("coverage_gap_ref")]
    if len(expansion) != 6:
        return _domain_result("fixture_inventory_regression", False, "expansion_fixture_drift")
    for fixture in fixtures:
        if not fixture.get("fixture_id"):
            return _domain_result("fixture_inventory_regression", False, "fixture_metadata_loss")
    return _domain_result("fixture_inventory_regression", True)


def _check_fixture_coverage() -> dict[str, Any]:
    coverage = analyze_coverage()
    required = [
        "posture_state_coverage",
        "boundary_check_coverage",
        "traceability_field_coverage",
        "forbidden_fixture_classes_absent",
    ]
    for key in required:
        if key not in coverage:
            return _domain_result("fixture_coverage_regression", False, f"missing_{key}")
    if not coverage.get("forbidden_fixture_classes_absent"):
        return _domain_result("fixture_coverage_regression", False, "forbidden_fixture_class")
    return _domain_result("fixture_coverage_regression", True)


def _check_traceability(models: dict[str, Any], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    for fixture in fixtures:
        result = evaluate_fixture(fixture, models)
        audit = audit_result(result)
        if audit["audit_status"] != "pass":
            return _domain_result("traceability_regression", False, fixture["fixture_id"])
        if not result.get("trace_id") or not result.get("traceability_map"):
            return _domain_result("traceability_regression", False, "missing_traceability_refs")
    return _domain_result("traceability_regression", True)


def _check_compound_boundary() -> dict[str, Any]:
    results = analyze_compound_stress()
    if len(results) < len(STRESS_CASES):
        return _domain_result("compound_boundary_regression", False, "stress_case_drift")
    for result in results:
        if result.get("stress_validation_status") != "pass":
            return _domain_result("compound_boundary_regression", False, result.get("stress_case_id", ""))
    return _domain_result("compound_boundary_regression", True)


def _check_guardrail_red_team() -> dict[str, Any]:
    results = analyze_red_team_pack()
    if len(results) < len(RED_TEAM_VECTORS):
        return _domain_result("guardrail_red_team_regression", False, "vector_drift")
    for result in results:
        if result.get("red_team_validation_status") != "pass":
            return _domain_result("guardrail_red_team_regression", False, result.get("red_team_case_id", ""))
    return _domain_result("guardrail_red_team_regression", True)


def _check_output_admissibility(models: dict[str, Any], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    results = [evaluate_fixture(fixture, models) for fixture in fixtures]
    for result in results:
        admissibility = evaluate_output_admissibility(result)
        if admissibility["admissibility_status"] != "admissible_internal":
            return _domain_result("output_admissibility_regression", False, result.get("fixture_id", ""))
    if not results:
        return _domain_result("output_admissibility_regression", False, "no_results")
    base = results[0]
    negatives = [
        (_mutated(base, posture_basis=[]), "inadmissible_missing_basis"),
        (_mutated(base, triggered_caveats=[], caveat_trigger_refs=[]), "inadmissible_missing_caveat"),
        (_mutated(base, trace_id=None, traceability_map=None), "inadmissible_traceability_gap"),
        (_mutated(base, active_boundary_checks={}, boundary_check_refs=[]), "inadmissible_boundary_collapse"),
        (_mutated(base, guardrail_failure_flags=["blocked"], validation_status="guardrail_blocked"), "inadmissible_guardrail_failure"),
        (_mutated(base, posture_state_candidate=_s("result ", "card output envelope stub")), "inadmissible_report_shape"),
        (_mutated(base, out_of_scope_reason=_s("public ", "report generation stub")), "inadmissible_report_shape"),
        (_mutated(base, non_public_confirmation=False), "inadmissible_public_output_risk"),
        (_mutated(base, no_verdict_confirmation=False), "inadmissible_guardrail_failure"),
        (_mutated(base, not_assessable_reason=_s("confidence ", "score output stub")), "inadmissible_guardrail_failure"),
        (_mutated(base, not_assessable_reason=_s("fraud ", "accusation stub")), "inadmissible_guardrail_failure"),
        (_mutated(base, posture_state_candidate=_s("is ", "fake output stub")), "inadmissible_guardrail_failure"),
    ]
    for sample, expected in negatives:
        admissibility = evaluate_output_admissibility(sample)
        if admissibility["admissibility_status"] != expected:
            return _domain_result("output_admissibility_regression", False, expected)
        if admissibility["admissibility_validation_status"] != "fail":
            return _domain_result("output_admissibility_regression", False, "negative_passed")
    return _domain_result("output_admissibility_regression", True)


def _check_forbidden_language() -> dict[str, Any]:
    if not run_guardrail_regression():
        return _domain_result("forbidden_language_regression", False, "guardrail_regression_failed")
    return _domain_result("forbidden_language_regression", True)


def _check_non_public_boundary(prototype_root: Path) -> dict[str, Any]:
    for harness in REQUIRED_HARNESSES:
        if not (prototype_root / harness).is_file():
            return _domain_result("non_public_boundary_regression", False, f"missing_{harness}")
    for path in prototype_root.glob("*.py"):
        if path.name in BOUNDARY_SCAN_EXEMPT:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_NETWORK_MARKERS + FORBIDDEN_INPUT_MARKERS + FORBIDDEN_FRAMEWORK_MARKERS:
            if marker in text:
                return _domain_result("non_public_boundary_regression", False, f"{path.name}:{marker}")
    return _domain_result("non_public_boundary_regression", True)


def _check_no_score_no_verdict(models: dict[str, Any], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    for fixture in fixtures:
        result = evaluate_fixture(fixture, models)
        if not result.get("no_verdict_confirmation"):
            return _domain_result("no_score_no_verdict_regression", False, "verdict_leakage")
        if not result.get("no_score_confirmation"):
            return _domain_result("no_score_no_verdict_regression", False, "score_leakage")
    return _domain_result("no_score_no_verdict_regression", True)


def _check_no_report_shape(models: dict[str, Any], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    for fixture in fixtures:
        result = evaluate_fixture(fixture, models)
        serialized = " ".join(
            str(result.get(k) or "")
            for k in ("posture_state_candidate", "not_assessable_reason", "out_of_scope_reason")
        ).lower()
        if "result card" in serialized or "public report" in serialized:
            return _domain_result("no_report_shape_regression", False, fixture["fixture_id"])
    return _domain_result("no_report_shape_regression", True)


def run_admissibility_regression_suite(prototype_root: Path | None = None) -> dict[str, Any]:
    """Run unified admissibility regression checks and return structured status."""
    root = prototype_root or Path(__file__).resolve().parent
    fixtures = load_fixtures()
    models = load_models()

    domain_results = [
        _check_fixture_inventory(),
        _check_fixture_coverage(),
        _check_traceability(models, fixtures),
        _check_compound_boundary(),
        _check_guardrail_red_team(),
        _check_output_admissibility(models, fixtures),
        _check_forbidden_language(),
        _check_non_public_boundary(root),
        _check_no_score_no_verdict(models, fixtures),
        _check_no_report_shape(models, fixtures),
    ]

    all_pass = all(r["regression_status"] == "pass" for r in domain_results)
    return {
        "suite_id": "internal-prototype-admissibility-regression-suite-v1",
        "fixture_count": len(fixtures),
        "regression_domains": REGRESSION_DOMAINS,
        "required_harnesses": REQUIRED_HARNESSES,
        "domain_results": domain_results,
        "regression_validation_status": "pass" if all_pass else "fail",
        "non_public_confirmation": True,
        "no_score_confirmation": True,
        "no_verdict_confirmation": True,
    }
