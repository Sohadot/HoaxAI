#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Prototype Governance v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
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

POLICY_REQUIRED = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "static_boundary_principle", "allowed_governance_actions", "prohibited_actions",
    "non_public_definition", "prototype_non_purpose", "non_authorization_rules", "last_reviewed",
}

SCOPE_REQUIRED = {
    "scope_id", "name", "version", "status", "maturity", "allowed_future_scope",
    "prohibited_future_scope", "prototype_surface_status", "current_public_surface",
    "non_authorization_statement", "last_reviewed",
}

LOCATION_REQUIRED = {
    "location_policy_id", "name", "version", "status", "maturity",
    "allowed_future_prototype_location", "location_rules", "prohibited_locations",
    "publication_blockers", "non_authorization_statement", "last_reviewed",
}

VISUAL_REQUIRED = {
    "visual_contract_id", "name", "version", "status", "maturity",
    "validated_identity_inputs", "required_visual_direction", "allowed_visual_explorations",
    "forbidden_visual_patterns", "background_identity_rules", "non_authorization_statement",
    "last_reviewed",
}

SAFETY_REQUIRED = {
    "safety_boundary_id", "name", "version", "status", "maturity", "safety_rules",
    "blocked_capabilities", "blocked_content_patterns", "blocked_publication_patterns",
    "non_authorization_statement", "last_reviewed",
}

GATES_REQUIRED = {
    "gate_set_id", "name", "version", "status", "maturity", "review_gates",
    "non_authorization_statement", "last_reviewed",
}

MASTER_REQUIRED = {
    "governance_id", "name", "version", "status", "maturity", "blueprint_validation_ref",
    "scope_ref", "location_policy_ref", "visual_identity_contract_ref",
    "safety_boundaries_ref", "review_gates_ref", "allowed_next_phase",
    "prohibited_capabilities", "non_authorization_statement", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_GOVERNANCE.md",
    "data/non-public-static-workbench-prototype-governance-policy.json",
    "data/non-public-static-workbench-prototype-scope.json",
    "data/non-public-static-workbench-prototype-location-policy.json",
    "data/non-public-static-workbench-prototype-visual-identity-contract.json",
    "data/non-public-static-workbench-prototype-safety-boundaries.json",
    "data/non-public-static-workbench-prototype-review-gates.json",
    "data/non-public-static-workbench-prototype-governance-v1.json",
    "validators/validate_non_public_static_workbench_prototype_governance.py",
]

ALLOWED_FUTURE_LOCATION = "_internal_prototypes/evidence-posture-workbench/"

PROHIBITED_ACTIONS = [
    "prototype_file_creation", "prototype_directory_creation", "interface_creation",
    "public_workbench", "public_engine", "public_classifier", "public_tool", "upload",
    "scoring", "fake_real_output", "forms", "analytics", "api", "monetization",
    "new_routes", "sitemap_expansion", "dns", "cloudflare", "custom_domain_launch",
    "deployment_changes", "external_factual_claims", "subject_accusation",
]

ALLOWED_FUTURE_SCOPE = [
    "static visual exploration", "evidence chamber layout exploration",
    "evidence field background exploration", "zone layout exploration",
    "component placement exploration", "state display exploration",
    "refusal display exploration", "output envelope containment exploration",
    "verification path layout exploration",
]

PROHIBITED_FUTURE_SCOPE = [
    "operational interface", "public workbench", "public route", "public navigation",
    "sitemap entry", "form input", "file upload", "engine behavior",
    "classifier behavior", "scoring behavior", "fake/real output", "API behavior",
    "analytics", "storage", "network calls", "monetization", "deployment change",
]

REQUIRED_PUBLIC_SURFACE = [
    "homepage root", "/reference/evidence-posture/",
    "/reference/artifact-subject-separation/", "/language/",
]

PROHIBITED_LOCATIONS = [
    "/workbench/", "/evidence-posture-workbench/", "/tool/", "/classifier/",
    "/detector/", "/upload/", "/score/", "/api/", "/demo/", "/prototype/ as public route",
]

PUBLICATION_BLOCKERS = [
    "sitemap inclusion", "route registry activation", "public navigation link",
    "homepage CTA", "upload control", "scoring display", "fake/real result",
    "engine wording", "classifier wording", "detector wording",
]

VALIDATED_IDENTITY_INPUTS = [
    "interface_blueprint_validated", "conceptual_identity_validated_with_maturity_boundary",
    "evidence_field_background_direction_validated",
]

REQUIRED_VISUAL_DIRECTION = [
    "evidence_chamber_not_detector", "governed_evidence_field_not_generic_black_dashboard",
    "artifact_first", "boundary_first", "posture_before_verdict", "provenance_shadow",
    "missing_context_as_absence", "not_assessable_as_protected_restraint",
    "refusal_as_governance", "output_envelope_containment", "no_verdict_gravity",
]

FORBIDDEN_VISUAL = [
    "detector dashboard", "scanner UI", "central upload box",
    "red/green fake-real result logic", "truth meter", "risk score",
    "probability gauge", "forensic game visuals", "policing dashboard",
    "SaaS analytics dashboard", "product landing-page CTA layout", "try-it-now pattern",
]

SAFETY_RULES = [
    "no real-world cases", "no user input", "no upload", "no scoring",
    "no fake/real verdict", "no generated output", "no subject accusation",
    "no identity judgment", "no high-stakes determination", "no API", "no analytics",
    "no network calls", "no storage", "no public route", "no sitemap", "no public navigation",
]

BLOCKED_CAPABILITIES = [
    "prototype_implementation_in_sprint_33", "interface_implementation", "public_engine",
    "public_classifier", "public_tool", "upload", "scoring", "API", "forms", "analytics",
    "storage", "network_calls", "public_routes", "sitemap_expansion", "deployment_change",
    "DNS", "Cloudflare", "custom_domain_launch",
]

BLOCKED_CONTENT = [
    "real people", "real companies", "real institutions", "real brands",
    "political events", "current events", "accusations", "external factual claims",
    "generated user-facing analysis", "fake/real output", "numeric score",
    "verified/certified claim",
]

PROHIBITED_MASTER_CAPS = [
    "prototype_implementation_in_sprint_33", "public_engine", "public_classifier",
    "public_tool", "workbench_interface", "upload", "scoring", "fake_real_output",
    "API", "forms", "analytics", "monetization", "DNS", "Cloudflare",
    "custom_domain_launch", "new_public_routes", "sitemap_expansion", "deployment_change",
]

GATE_IDS = [f"NP-PROTO-GATE-{i:04d}" for i in range(1, 12)]

GATE_NAMES = [
    "Prototype Location Gate", "Non-Public Route Gate", "Static-Only Gate",
    "No Input/Upload Gate", "No Scoring/Verdict Gate", "No Engine/Classifier Gate",
    "Evidence Field Visual Identity Gate", "Accessibility/Performance Gate",
    "No Public Navigation Gate", "No Sitemap Expansion Gate",
    "No Deployment/DNS/Cloudflare Gate",
]

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
GATE_ID_PATTERN = re.compile(r"^NP-PROTO-GATE-\d{4}$")
AUTHORIZE_PATTERN = re.compile(
    r"\b(authorizes|enables|permits)\s+(engine|classifier|upload|scoring|route|sitemap|deployment|dns|cloudflare)",
    re.I,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-prototype-governance-policy.json"
    policy = load_json(path)
    if not POLICY_REQUIRED.issubset(set(policy)):
        error("governance policy: missing required top-level fields")
        ok = False
    if policy.get("status") != "governed_non_public_static_workbench_prototype_policy":
        error("governance policy: invalid status")
        ok = False
    if policy.get("maturity") != "prototype_governance_only_no_prototype_no_interface_no_engine_no_classifier_no_tool":
        error("governance policy: invalid maturity")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"governance policy: missing prohibited action {action}")
            ok = False
    blocked = " ".join(policy.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in [
        "prototype_implementation", "interface_implementation", "workbench_engine",
        "workbench_classifier", "upload", "scoring", "api", "new_public_routes",
        "sitemap_expansion", "deployment_change", "dns", "cloudflare",
        "custom_domain_launch", "public_tool_behavior",
    ]:
        if term.replace("_", " ") not in blocked and term not in blocked:
            error(f"governance policy: non_authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("governance policy: numeric score found")
        ok = False
    return ok


def validate_scope() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-scope.json")
    if not SCOPE_REQUIRED.issubset(set(data)):
        error("scope: missing required top-level fields")
        ok = False
    allowed = " ".join(data.get("allowed_future_scope", [])).lower()
    for item in ALLOWED_FUTURE_SCOPE:
        if item.lower() not in allowed:
            error(f"scope: missing allowed future scope {item}")
            ok = False
    prohibited = " ".join(data.get("prohibited_future_scope", [])).lower()
    for item in PROHIBITED_FUTURE_SCOPE:
        if item.lower() not in prohibited:
            error(f"scope: missing prohibited future scope {item}")
            ok = False
    if data.get("current_public_surface") != REQUIRED_PUBLIC_SURFACE:
        error("scope: current_public_surface must remain unchanged")
        ok = False
    if data.get("prototype_surface_status") != "no_prototype_created":
        error("scope: prototype_surface_status must be no_prototype_created")
        ok = False
    return ok


def validate_location_policy() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-location-policy.json")
    if not LOCATION_REQUIRED.issubset(set(data)):
        error("location policy: missing required top-level fields")
        ok = False
    if data.get("allowed_future_prototype_location") != ALLOWED_FUTURE_LOCATION:
        error(f"location policy: allowed location must be {ALLOWED_FUTURE_LOCATION}")
        ok = False
    proto_dir = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
    if not proto_dir.exists():
        pass  # governance sprint did not require directory; prototype may be created in Sprint 34+
    rules = " ".join(data.get("location_rules", [])).lower()
    for rule in ["future-allowed only", "must not be created in sprint 33", "sitemap", "nojekyll"]:
        if rule.replace("_", " ") not in rules and rule not in rules:
            error(f"location policy: missing location rule containing {rule}")
            ok = False
    for loc in PROHIBITED_LOCATIONS:
        if loc not in data.get("prohibited_locations", []):
            error(f"location policy: missing prohibited location {loc}")
            ok = False
    blockers = " ".join(data.get("publication_blockers", [])).lower()
    for blocker in PUBLICATION_BLOCKERS:
        if blocker.lower() not in blockers:
            error(f"location policy: missing publication blocker {blocker}")
            ok = False
    return ok


def validate_visual_contract() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-visual-identity-contract.json")
    if not VISUAL_REQUIRED.issubset(set(data)):
        error("visual identity contract: missing required top-level fields")
        ok = False
    for inp in VALIDATED_IDENTITY_INPUTS:
        if inp not in data.get("validated_identity_inputs", []):
            error(f"visual contract: missing validated input {inp}")
            ok = False
    for direction in REQUIRED_VISUAL_DIRECTION:
        if direction not in data.get("required_visual_direction", []):
            error(f"visual contract: missing required direction {direction}")
            ok = False
    forbidden = " ".join(data.get("forbidden_visual_patterns", [])).lower()
    for pat in FORBIDDEN_VISUAL:
        if pat.lower() not in forbidden:
            error(f"visual contract: missing forbidden pattern {pat}")
            ok = False
    bg_rules = " ".join(data.get("background_identity_rules", [])).lower()
    if "black cyber" not in bg_rules and "black cyber ui" not in bg_rules:
        error("visual contract: background rules must reject black cyber UI")
        ok = False
    if "conceptual layer" not in bg_rules:
        error("visual contract: background must be conceptual layer")
        ok = False
    return ok


def validate_safety_boundaries() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-safety-boundaries.json")
    if not SAFETY_REQUIRED.issubset(set(data)):
        error("safety boundaries: missing required top-level fields")
        ok = False
    rules = " ".join(data.get("safety_rules", [])).lower()
    for rule in SAFETY_RULES:
        if rule.lower() not in rules:
            error(f"safety boundaries: missing rule {rule}")
            ok = False
    caps = {c.lower() for c in data.get("blocked_capabilities", [])}
    for cap in BLOCKED_CAPABILITIES:
        if cap.lower() not in caps:
            error(f"safety boundaries: missing blocked capability {cap}")
            ok = False
    content = " ".join(data.get("blocked_content_patterns", [])).lower()
    for pat in BLOCKED_CONTENT:
        if pat.lower() not in content:
            error(f"safety boundaries: missing blocked content {pat}")
            ok = False
    return ok


def validate_review_gates() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-review-gates.json")
    if not GATES_REQUIRED.issubset(set(data)):
        error("review gates: missing required top-level fields")
        ok = False
    gates = data.get("review_gates", [])
    if len(gates) != 11:
        error(f"review gates: expected 11 gates, found {len(gates)}")
        ok = False
    seen_ids: set[str] = set()
    for i, gate in enumerate(gates):
        gid = gate.get("gate_id", "")
        if not GATE_ID_PATTERN.match(gid):
            error(f"review gates: invalid gate_id {gid}")
            ok = False
        if gid in seen_ids:
            error(f"review gates: duplicate gate_id {gid}")
            ok = False
        seen_ids.add(gid)
        if gate.get("required_before_future_prototype_creation") is not True:
            error(f"{gid}: required_before_future_prototype_creation must be true")
            ok = False
        expected_name = GATE_NAMES[i] if i < len(GATE_NAMES) else None
        if expected_name and gate.get("gate_name") != expected_name:
            error(f"{gid}: gate_name must be {expected_name}")
            ok = False
        stmt = gate.get("non_authorization_statement", "").lower()
        if AUTHORIZE_PATTERN.search(stmt):
            error(f"{gid}: gate non_authorization_statement authorizes prohibited behavior")
            ok = False
    if seen_ids != set(GATE_IDS):
        error(f"review gates: expected IDs {GATE_IDS}")
        ok = False
    return ok


def validate_master_governance() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-governance-v1.json")
    if not MASTER_REQUIRED.issubset(set(data)):
        error("master governance: missing required top-level fields")
        ok = False
    if data.get("status") != "non_public_static_workbench_prototype_governance_created":
        error("master governance: invalid status")
        ok = False
    if data.get("maturity") != "prototype_governance_only_no_prototype_no_interface_no_engine_no_classifier_no_tool":
        error("master governance: invalid maturity")
        ok = False
    next_phase = data.get("allowed_next_phase", "")
    if "Sprint 34" not in next_phase or "Non-Public Static Workbench Prototype" not in next_phase:
        error("master governance: allowed_next_phase must be Sprint 34 Non-Public Static Workbench Prototype v1")
        ok = False
    caps = {c.lower() for c in data.get("prohibited_capabilities", [])}
    for cap in PROHIBITED_MASTER_CAPS:
        if cap.lower() not in caps:
            error(f"master governance: missing prohibited capability {cap}")
            ok = False
    validation = load_json(ROOT / "data" / "evidence-posture-workbench-interface-blueprint-validation-results-v1.json")
    if validation.get("overall_result") != "interface_blueprint_validated":
        error("blueprint validation prerequisite must be interface_blueprint_validated")
        ok = False
    identity = load_json(
        ROOT / "data" / "evidence-posture-workbench-interface-conceptual-identity-validation-v1.json"
    )
    if identity.get("overall_result") != "conceptual_identity_validated_with_maturity_boundary":
        error("conceptual identity prerequisite must be validated with maturity boundary")
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
    for rel in ["workbench/index.html", "prototype/index.html"]:
        if (ROOT / rel).exists():
            error(f"prototype file must not exist: {rel}")
            ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
        "blocked_until_controlled_internal_prototype_v0_implementation_sprint",
        "blocked_until_controlled_internal_prototype_v0_validation",
        "blocked_until_controlled_internal_prototype_v0_hardening_validation",
        "blocked_until_internal_prototype_traceability_interpretability_audit_validation",
        "blocked_until_internal_prototype_fixture_coverage_matrix_validation",
        "blocked_until_targeted_synthetic_fixture_expansion_v1_validation",
        "blocked_until_internal_prototype_compound_boundary_stress_test_validation",
        "blocked_until_internal_prototype_guardrail_red_team_pack_validation",
        "blocked_until_internal_prototype_release_blocker_board_validation",
    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Non-Public Static Workbench Prototype Governance Gate"),
        None,
    )
    if not gate:
        error("Non-Public Static Workbench Prototype Governance Gate missing")
        ok = False
    else:
        for field in [
            "required_before_non_public_static_workbench_prototype",
            "required_before_workbench_prototype",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"prototype governance gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is True:
            error("prototype governance gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        if "not authorize" not in notes and "does not authorize" not in notes:
            error("prototype governance gate notes must state non-authorization")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_prototype_governance" not in checks:
        error("reference-expansion-gate: prototype governance required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_prototype_governance_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by prototype governance alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    proto_blocked = [
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
    if not any(b in blocked for b in proto_blocked):
        error("reference-expansion-gate: publisher blocked until prototype progression")
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
    if "validate_non_public_static_workbench_prototype_governance.py" not in content:
        error("validate_all.py must include prototype governance validator")
        ok = False
    doc = (ROOT / "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_GOVERNANCE.md").read_text(encoding="utf-8")
    if "Prototype governance defines what may be built later. It must not build it now." not in doc:
        error("governance doc: missing governing principle")
        ok = False
    if "A non-public prototype may explore interface form, but it must not create operational capability." not in doc:
        error("governance doc: missing static-boundary principle")
        ok = False
    if ALLOWED_FUTURE_LOCATION not in doc:
        error("governance doc: missing allowed future prototype location")
        ok = False
    if "DEC-051" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-051 missing")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-prototype-governance-policy.json",
        "data/non-public-static-workbench-prototype-scope.json",
        "data/non-public-static-workbench-prototype-location-policy.json",
        "data/non-public-static-workbench-prototype-visual-identity-contract.json",
        "data/non-public-static-workbench-prototype-safety-boundaries.json",
        "data/non-public-static-workbench-prototype-review-gates.json",
        "data/non-public-static-workbench-prototype-governance-v1.json",
        "data/evidence-posture-workbench-interface-blueprint-validation-results-v1.json",
        "data/evidence-posture-workbench-interface-conceptual-identity-validation-v1.json",
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

    checks = [
        validate_policy,
        validate_scope,
        validate_location_policy,
        validate_visual_contract,
        validate_safety_boundaries,
        validate_review_gates,
        validate_master_governance,
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
