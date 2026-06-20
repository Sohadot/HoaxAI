#!/usr/bin/env python3
"""Validate Hoax.ai Evidence Posture Workbench Dry-Run Harness v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING,
    validate_no_extra_public_html,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "refusal_principle", "allowed_dry_run_actions", "prohibited_actions",
    "dry_run_scope", "case_safety_policy", "result_maturity_policy",
    "non_authorization_rules", "last_reviewed",
}

CASES_TOP = {"case_set_id", "name", "version", "status", "maturity", "cases", "last_reviewed"}

EXPECTED_TOP = {
    "expected_results_id", "name", "version", "status", "maturity",
    "expected_results", "last_reviewed",
}

RESULTS_TOP = {
    "dry_run_id", "name", "version", "status", "maturity", "dry_run_results",
    "overall_result", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "EVIDENCE_POSTURE_WORKBENCH_DRY_RUN_HARNESS.md",
    "data/evidence-posture-workbench-dry-run-policy.json",
    "data/evidence-posture-workbench-dry-run-cases.json",
    "data/evidence-posture-workbench-dry-run-expected-results.json",
    "data/evidence-posture-workbench-dry-run-results-v1.json",
    "validators/validate_evidence_posture_workbench_dry_run.py",
]

PROHIBITED_ACTIONS = [
    "interface_creation", "prototype_creation", "public_workbench", "public_engine",
    "public_classifier", "public_tool", "upload", "scoring", "fake_real_output",
    "forms", "analytics", "api", "monetization", "new_routes", "sitemap_expansion",
    "dns", "cloudflare", "custom_domain_launch", "external_factual_claims",
    "subject_accusation", "real_world_examples",
]

FORBIDDEN_RESULT_TERMS = [
    "engine_ready", "public_engine_ready", "classifier_ready", "tool_ready",
    "upload_ready", "scoring_ready", "production_ready", "public_release_ready",
    "impossible_to_imitate", "final_language_complete",
]

CASE_FAMILIES_REQUIRED = [
    "allowed_artifact_description",
    "incomplete_provenance",
    "missing_source_context",
    "not_assessable_required",
    "subject_accusation_refusal",
    "fake_real_verdict_refusal",
    "score_request_refusal",
    "identity_judgment_refusal",
    "high_stakes_determination_refusal",
    "evidence_free_certainty_refusal",
    "out_of_scope_tool_request_refusal",
    "output_boundary_enforcement",
]

REAL_WORLD_FORBIDDEN = re.compile(
    r"\b(https?://|www\.|upload://|\.jpg|\.png|\.mp4|\.pdf|"
    r"google|facebook|twitter|microsoft|apple|amazon|"
    r"president|election|congress|parliament|ceo\b)",
    re.I,
)

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
CASE_ID_PATTERN = re.compile(r"^WB-DRY-CASE-\d{4}$")
STATE_ID_PATTERN = re.compile(r"^WB-STATE-\d{4}$")
OUTPUT_ID_PATTERN = re.compile(r"^WB-OUTPUT-\d{4}$")
REFUSAL_ID_PATTERN = re.compile(r"^WB-REFUSAL-\d{4}$")

ALLOWED_DRY_RUN_OUTCOMES = {
    "governance_behavior_passed",
    "refusal_behavior_passed",
    "not_assessable_behavior_passed",
    "output_boundary_behavior_passed",
    "state_transition_behavior_passed",
}

READINESS_IMPLIED = re.compile(
    r"\b(engine_ready|classifier_ready|tool_ready|upload_ready|"
    r"scoring_ready|production_ready|public_release_ready)\b",
    re.I,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_governance_ids() -> tuple[set[str], set[str], set[str]]:
    states = {
        s["state_id"]
        for s in load_json(ROOT / "data" / "evidence-posture-workbench-state-model.json").get("states", [])
    }
    outputs = {
        o["output_id"]
        for o in load_json(ROOT / "data" / "evidence-posture-workbench-output-boundary.json").get(
            "allowed_output_families", []
        )
    }
    refusals = {
        r["refusal_id"]
        for r in load_json(ROOT / "data" / "evidence-posture-workbench-refusal-model.json").get(
            "refusal_families", []
        )
    }
    return states, outputs, refusals


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-workbench-dry-run-policy.json"
    policy = load_json(path)
    if set(policy) != POLICY_TOP:
        error(f"dry-run policy: unexpected top-level keys")
        ok = False
    if policy.get("status") != "governed_evidence_posture_workbench_dry_run_policy":
        error("dry-run policy: invalid status")
        ok = False
    if policy.get("maturity") != "dry_run_only_no_workbench_no_engine_no_classifier_no_tool":
        error("dry-run policy: invalid maturity")
        ok = False
    prohibited_raw = policy.get("prohibited_actions", [])
    prohibited = " ".join(str(a) for a in prohibited_raw).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"dry-run policy: missing prohibited action {action}")
            ok = False
    for term in FORBIDDEN_RESULT_TERMS:
        forbidden = policy.get("result_maturity_policy", {}).get("forbidden_result_terms", [])
        if term not in forbidden:
            error(f"dry-run policy: result maturity must forbid {term}")
            ok = False
    if not policy.get("case_safety_policy", {}).get("all_cases_fictional"):
        error("dry-run policy: all_cases_fictional must be true")
        ok = False
    text = path.read_text(encoding="utf-8")
    if NUMERIC_SCORE_PATTERN.search(text):
        error("dry-run policy: numeric score or grade found")
        ok = False
    return ok


def validate_cases() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-dry-run-cases.json")
    if set(data) != CASES_TOP:
        error("dry-run cases: unexpected top-level keys")
        ok = False
    cases = data.get("cases", [])
    if len(cases) != 12:
        error(f"dry-run cases: expected 12, found {len(cases)}")
        ok = False
    ids: set[str] = set()
    families: set[str] = set()
    for case in cases:
        cid = case.get("case_id", "")
        if not CASE_ID_PATTERN.match(cid):
            error(f"dry-run cases: invalid case_id {cid}")
            ok = False
        if cid in ids:
            error(f"dry-run cases: duplicate case_id {cid}")
            ok = False
        ids.add(cid)
        if case.get("real_world_status") != "fictional_no_real_world_reference":
            error(f"{cid}: real_world_status must be fictional_no_real_world_reference")
            ok = False
        if case.get("data_collection_status") != "no_data_collected":
            error(f"{cid}: data_collection_status must be no_data_collected")
            ok = False
        families.add(case.get("case_family", ""))
        blob = json.dumps(case).lower()
        if REAL_WORLD_FORBIDDEN.search(blob):
            error(f"{cid}: forbidden real-world pattern in case content")
            ok = False
        if re.search(r"\b\d+\s*%\b", blob) and "score_request" not in case.get("case_family", ""):
            error(f"{cid}: numeric percentage in non-score-refusal case")
            ok = False
    missing = set(CASE_FAMILIES_REQUIRED) - families
    if missing:
        error(f"dry-run cases: missing case families {sorted(missing)}")
        ok = False
    return ok


def validate_expected_results(states: set[str], outputs: set[str], refusals: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-dry-run-expected-results.json")
    if set(data) != EXPECTED_TOP:
        error("expected results: unexpected top-level keys")
        ok = False
    expected = data.get("expected_results", [])
    if len(expected) != 12:
        error(f"expected results: expected 12, found {len(expected)}")
        ok = False
    case_ids = {
        c["case_id"]
        for c in load_json(ROOT / "data" / "evidence-posture-workbench-dry-run-cases.json").get("cases", [])
    }
    seen_cases: set[str] = set()
    for exp in expected:
        cid = exp.get("case_id", "")
        if cid not in case_ids:
            error(f"expected results: unknown case_id {cid}")
            ok = False
        if cid in seen_cases:
            error(f"expected results: duplicate case_id {cid}")
            ok = False
        seen_cases.add(cid)
        est = exp.get("expected_state", "")
        if est not in states:
            error(f"expected results: invalid expected_state {est} for {cid}")
            ok = False
        out = exp.get("expected_output_family")
        if out is not None and out not in outputs:
            error(f"expected results: invalid expected_output_family {out} for {cid}")
            ok = False
        ref = exp.get("expected_refusal_family")
        if ref is not None and ref not in refusals:
            error(f"expected results: invalid expected_refusal_family {ref} for {cid}")
            ok = False
        if READINESS_IMPLIED.search(json.dumps(exp)):
            error(f"expected results: readiness implication in {cid}")
            ok = False
    if seen_cases != case_ids:
        error("expected results: must have exactly one result per case")
        ok = False
    return ok


def validate_dry_run_results(states: set[str], outputs: set[str], refusals: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-dry-run-results-v1.json")
    if set(data) != RESULTS_TOP:
        error("dry-run results: unexpected top-level keys")
        ok = False
    if data.get("overall_result") != "evidence_posture_workbench_dry_run_passed_with_conditions":
        error("dry-run results: invalid overall_result")
        ok = False
    results = data.get("dry_run_results", [])
    if len(results) != 12:
        error(f"dry-run results: expected 12, found {len(results)}")
        ok = False
    expected_by_case = {
        e["case_id"]: e
        for e in load_json(ROOT / "data" / "evidence-posture-workbench-dry-run-expected-results.json").get(
            "expected_results", []
        )
    }
    seen: set[str] = set()
    for res in results:
        cid = res.get("case_id", "")
        if cid in seen:
            error(f"dry-run results: duplicate case_id {cid}")
            ok = False
        seen.add(cid)
        if res.get("observed_state") not in states:
            error(f"dry-run results: invalid observed_state for {cid}")
            ok = False
        out = res.get("observed_output_family")
        if out is not None and out not in outputs:
            error(f"dry-run results: invalid observed_output_family for {cid}")
            ok = False
        ref = res.get("observed_refusal_family")
        if ref is not None and ref not in refusals:
            error(f"dry-run results: invalid observed_refusal_family for {cid}")
            ok = False
        if res.get("boundary_checks_result") != "passed":
            error(f"dry-run results: boundary_checks_result must be passed for {cid}")
            ok = False
        if res.get("forbidden_output_blocks_result") != "passed":
            error(f"dry-run results: forbidden_output_blocks_result must be passed for {cid}")
            ok = False
        if res.get("non_authorization_result") != "non_authorization_preserved":
            error(f"dry-run results: non_authorization must be preserved for {cid}")
            ok = False
        outcome = res.get("dry_run_outcome", "")
        if outcome not in ALLOWED_DRY_RUN_OUTCOMES:
            error(f"dry-run results: invalid dry_run_outcome {outcome} for {cid}")
            ok = False
        exp = expected_by_case.get(cid, {})
        if res.get("observed_state") != exp.get("expected_state"):
            error(f"dry-run results: observed_state mismatch for {cid}")
            ok = False
        if res.get("observed_output_family") != exp.get("expected_output_family"):
            error(f"dry-run results: observed_output_family mismatch for {cid}")
            ok = False
        if res.get("observed_refusal_family") != exp.get("expected_refusal_family"):
            error(f"dry-run results: observed_refusal_family mismatch for {cid}")
            ok = False
        notes = res.get("notes", "")
        if len(notes) > 200:
            error(f"dry-run results: notes too long (user-facing prose) for {cid}")
            ok = False
        blob = json.dumps(res).lower()
        if READINESS_IMPLIED.search(blob):
            error(f"dry-run results: readiness implication for {cid}")
            ok = False
        for term in FORBIDDEN_RESULT_TERMS:
            if term in blob:
                error(f"dry-run results: forbidden term {term} in {cid}")
                ok = False
    if seen != set(expected_by_case):
        error("dry-run results: must have exactly one result per case")
        ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    if not validate_no_extra_public_html(error):
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    allowed = {
        PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION,
        PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT,
        PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
        "blocked_until_public_reference_production_batch_1",
        "blocked_until_public_reference_production_batch_1_validation",
        "blocked_until_public_reference_production_batch_2_validation",
        "blocked_until_public_reference_production_batch_3_validation",
        "blocked_until_evidence_posture_standard_v1_validation",
        "blocked_until_evidence_posture_protocol_v1_draft_validation",
        "blocked_until_public_interface_thesis_evidence_field_validation",
        "blocked_until_evidence_field_static_interface_embodiment_v1_validation",
        "blocked_until_evidence_field_visual_system_accessibility_hardening_validation",
        "blocked_until_controlled_domain_connection_decision",
        "blocked_until_engine_boundary_and_public_reference_seo_authority_map_validation",
        "blocked_until_evidence_posture_engine_model_v0_validation",
        "blocked_until_output_language_guardrail_model_v1_validation",
        "blocked_until_internal_non_public_engine_prototype_charter_validation",
    }
    if pub.get("current_publisher_status") not in allowed:
        error(f"publisher status must be one of {sorted(allowed)}")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Evidence Posture Workbench Dry-Run Harness Gate"),
        None,
    )
    if not gate:
        error("Evidence Posture Workbench Dry-Run Harness Gate missing")
        ok = False
    else:
        if gate.get("bypassable") is True:
            error("dry-run harness gate must not be bypassable")
            ok = False
        if gate.get("required_before_workbench_specification") is not True:
            error("dry-run harness gate must be required before workbench specification")
            ok = False
        if gate.get("required_before_workbench_prototype") is not True:
            error("dry-run harness gate must be required before workbench prototype")
            ok = False
        if gate.get("required_before_engine_governance") is not True:
            error("dry-run harness gate must be required before engine governance")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "workbench_dry_run" not in checks and "dry_run_harness" not in checks:
        error("reference-expansion-gate: workbench dry-run harness required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_dry_run_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by dry-run alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    workbench_blocked = [
        "publisher_blocked_until_workbench_specification_layer",
        "publisher_blocked_until_workbench_interface_blueprint_governance",
        "publisher_blocked_until_workbench_interface_blueprint_validation",
        "publisher_blocked_until_non_public_static_workbench_prototype_governance",
        "publisher_blocked_until_non_public_static_workbench_prototype_v1",
        "publisher_blocked_until_non_public_static_workbench_prototype_validation",
        "publisher_blocked_until_non_public_static_workbench_prototype_refinement",
        "publisher_blocked_until_non_public_static_workbench_prototype_refinement_validation",
        "publisher_blocked_until_non_public_static_workbench_visual_system_hardening",
        "publisher_blocked_until_non_public_static_workbench_visual_system_hardening_validation",
        "publisher_blocked_until_non_public_static_workbench_visual_system_baseline_lock",
        "publisher_blocked_until_non_public_static_workbench_visual_system_baseline_lock_validation",
        "publisher_blocked_until_non_public_static_workbench_public_readiness_boundary_governance",
        "publisher_blocked_until_non_public_static_workbench_public_readiness_boundary_validation",
        "publisher_blocked_until_public_route_eligibility_governance",
        "publisher_blocked_until_public_route_eligibility_governance_validation",
        "publisher_blocked_until_public_route_candidate_assessment_governance",
    ]
    if not any(b in blocked for b in workbench_blocked):
        error("reference-expansion-gate: publisher blocked until workbench progression")
        ok = False
    return ok


def validate_source_registry() -> bool:
    ok = True
    locations = {s.get("location") for s in load_json(ROOT / "data" / "source-registry.json").get("sources", [])}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing {loc}")
            ok = False
    return ok


def validate_cross_file() -> bool:
    ok = True
    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_evidence_posture_workbench_dry_run.py" not in content:
        error("validate_all.py must include workbench dry-run validator")
        ok = False
    doc = (ROOT / "EVIDENCE_POSTURE_WORKBENCH_DRY_RUN_HARNESS.md").read_text(encoding="utf-8")
    if "A dry-run harness tests governance behavior without becoming the behavior." not in doc:
        error("dry-run harness doc: missing governing principle sentence")
        ok = False
    if "The workbench must learn to refuse before it learns to respond." not in doc:
        error("dry-run harness doc: missing refusal principle sentence")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/evidence-posture-workbench-dry-run-policy.json",
        "data/evidence-posture-workbench-dry-run-cases.json",
        "data/evidence-posture-workbench-dry-run-expected-results.json",
        "data/evidence-posture-workbench-dry-run-results-v1.json",
        "data/evidence-posture-workbench-governance-policy.json",
        "data/evidence-posture-workbench-input-model.json",
        "data/evidence-posture-workbench-output-boundary.json",
        "data/evidence-posture-workbench-state-model.json",
        "data/evidence-posture-workbench-refusal-model.json",
        "data/evidence-posture-workbench-non-authorization-rules.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
    ]
    for rel in parse_paths:
        try:
            load_json(ROOT / rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"{rel} parse failed: {exc}")
            return 1

    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    states, outputs, refusals = load_governance_ids()

    checks = [
        validate_policy,
        validate_cases,
        lambda: validate_expected_results(states, outputs, refusals),
        lambda: validate_dry_run_results(states, outputs, refusals),
        validate_public_safety,
        validate_publisher_governance,
        validate_source_registry,
        validate_cross_file,
    ]
    ok = True
    for fn in checks:
        if not fn():
            ok = False

    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
