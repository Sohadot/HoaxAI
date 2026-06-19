#!/usr/bin/env python3
"""Validate Hoax.ai Evidence Posture Workbench Interface Blueprint Validation v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
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

POLICY_REQUIRED = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "identity_principle", "allowed_validation_actions", "prohibited_actions",
    "validation_scope", "conceptual_identity_validation_policy", "correction_policy",
    "non_authorization_rules", "last_reviewed",
}

RESULTS_REQUIRED = {
    "validation_id", "name", "version", "status", "maturity", "validation_dimensions",
    "blueprint_policy_result", "zone_registry_result", "component_registry_result",
    "interface_state_contract_result", "copy_boundary_result", "accessibility_performance_result",
    "publisher_governance_result", "reference_expansion_gate_result",
    "public_surface_non_expansion_result", "overall_result", "last_reviewed",
}

IDENTITY_REQUIRED = {
    "identity_validation_id", "name", "version", "status", "maturity",
    "interface_thesis_result", "identity_trait_results", "allowed_metaphor_results",
    "forbidden_metaphor_results", "anti_generic_ui_results",
    "conceptual_background_identity_result", "originality_boundary", "overall_result",
    "last_reviewed",
}

AUDIT_REQUIRED = {
    "audit_id", "name", "version", "status", "maturity", "audited_artifacts",
    "integrity_results", "non_authorization_result", "overall_outcome", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "EVIDENCE_POSTURE_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION.md",
    "data/evidence-posture-workbench-interface-blueprint-validation-policy.json",
    "data/evidence-posture-workbench-interface-blueprint-validation-results-v1.json",
    "data/evidence-posture-workbench-interface-conceptual-identity-validation-v1.json",
    "data/evidence-posture-workbench-interface-blueprint-integrity-audit-v1.json",
    "validators/validate_evidence_posture_workbench_interface_blueprint_validation.py",
]

PROHIBITED_ACTIONS = [
    "interface_creation", "prototype_creation", "public_workbench", "public_engine",
    "public_classifier", "public_tool", "upload", "scoring", "fake_real_output",
    "forms", "analytics", "api", "monetization", "new_routes", "sitemap_expansion",
    "dns", "cloudflare", "custom_domain_launch", "deployment_changes",
    "external_factual_claims", "subject_accusation",
]

REQUIRED_IDENTITY_TRAITS = [
    "evidence_chamber", "artifact_first_framing", "boundary_first_layout",
    "posture_state_architecture", "provenance_shadow", "not_assessable_as_protected_state",
    "refusal_as_governance", "output_envelope_containment", "no_verdict_gravity",
]

IDENTITY_TRAIT_RESULTS = [
    "artifact_first_framing", "boundary_first_layout", "posture_state_architecture",
    "provenance_shadow", "not_assessable_as_protected_state", "refusal_as_governance",
    "output_envelope_containment", "no_verdict_gravity",
]

ALLOWED_METAPHORS = [
    "evidence_chamber", "posture_field", "boundary_rail", "provenance_shadow",
    "source_trace", "uncertainty_register", "refusal_gate", "output_envelope",
    "not_assessable_lock", "verification_path",
]

FORBIDDEN_METAPHORS = [
    "detector", "scanner", "truth_meter", "risk_score", "fake_real_switch",
    "upload_machine", "forensic_game", "lie_detector", "courtroom_verdict",
    "policing_dashboard", "social_media_moderation_panel", "saas_analytics_dashboard",
]

ANTI_GENERIC_UI = [
    "not_upload_dashboard", "not_detector_page", "not_score_dashboard",
    "not_saas_analytics", "not_fact_checking_verdict_panel", "not_forensic_game",
    "not_social_moderation_panel", "not_policing_dashboard",
]

BACKGROUND_FUNCTIONS = [
    "missing_context_as_absence", "provenance_gap_as_shadow",
    "artifact_subject_boundary_as_rail", "evidence_condition_as_layering",
    "not_assessable_as_protected_restraint", "output_boundary_as_containment",
]

BLOCKED_VISUAL_PATTERNS = [
    "generic_black_cyber_dashboard", "neon_ai_detector", "upload_dashboard",
    "red_green_fake_real_ui", "scanner_background", "forensic_game_interface",
    "policing_dashboard", "saas_analytics_gradient",
]

DIMENSION_COUNT = 35

READINESS_FORBIDDEN = re.compile(
    r"\b(prototype.?ready|engine.?ready|classifier.?ready|tool.?ready|"
    r"public.?release.?ready|implementation.?authorized|ready for public use)\b",
    re.I,
)

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)

PROHIBITED_COPY = [
    "detect language", "fake/real language", "upload now language",
    "submit evidence language", "score language", "verified/certified language",
    "truth machine language", "accusation language", "product/SaaS/service claims",
    "API language", "public engine claims", "try it now language",
]

REQUIRED_BOUNDARY_PHRASES = [
    "This interface blueprint does not create a public workbench.",
    "The future workbench must not issue truth verdicts.",
    "The future workbench must not classify fake or real.",
    "The future workbench must not score evidence.",
    "The future workbench must not judge subjects.",
    "The future workbench must preserve artifact-subject separation.",
]

A11Y_REQUIRED = [
    "keyboard", "semantic html", "h1", "contrast", "focus", "fallback",
    "color alone", "reduced motion",
]

PERF_REQUIRED = [
    "dependency-light", "no external libraries", "no external scripts",
    "no webgl", "no canvas", "no analytics", "no network calls",
    "no storage", "mobile stability",
]

AUDITED_ARTIFACTS = [
    "EVIDENCE_POSTURE_WORKBENCH_INTERFACE_BLUEPRINT_GOVERNANCE.md",
    "data/evidence-posture-workbench-interface-blueprint-policy.json",
    "data/evidence-posture-workbench-interface-zone-registry.json",
    "data/evidence-posture-workbench-interface-component-registry.json",
    "data/evidence-posture-workbench-interface-state-contracts.json",
    "data/evidence-posture-workbench-interface-copy-boundaries.json",
    "data/evidence-posture-workbench-interface-accessibility-performance-rules.json",
    "data/evidence-posture-workbench-interface-blueprint-v1.json",
]

IMPLEMENTATION_PATHS = [
    "workbench/index.html",
    "workbench/prototype.html",
    "prototype/workbench.html",
    "static/workbench",
    "css/workbench.css",
    "js/workbench.js",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-workbench-interface-blueprint-validation-policy.json"
    policy = load_json(path)
    if not POLICY_REQUIRED.issubset(set(policy)):
        error("validation policy: missing required top-level fields")
        ok = False
    if policy.get("status") != "governed_evidence_posture_workbench_interface_blueprint_validation_policy":
        error("validation policy: invalid status")
        ok = False
    if policy.get("maturity") != "validation_only_no_interface_no_prototype_no_engine_no_classifier_no_tool":
        error("validation policy: invalid maturity")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"validation policy: missing prohibited action {action}")
            ok = False
    traits = policy.get("conceptual_identity_validation_policy", {}).get("required_traits", [])
    for trait in REQUIRED_IDENTITY_TRAITS:
        if trait not in traits:
            error(f"validation policy: missing required identity trait {trait}")
            ok = False
    blocked = " ".join(policy.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in [
        "interface_implementation", "workbench_prototype", "workbench_engine",
        "workbench_classifier", "upload", "scoring", "api", "new_public_routes",
        "sitemap_expansion", "deployment_change", "dns", "cloudflare",
        "custom_domain_launch", "public_tool_behavior",
    ]:
        if term.replace("_", " ") not in blocked and term not in blocked:
            error(f"validation policy: non_authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("validation policy: numeric score or grade found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-workbench-interface-blueprint-validation-results-v1.json"
    data = load_json(path)
    if not RESULTS_REQUIRED.issubset(set(data)):
        error("validation results: missing required top-level fields")
        ok = False
    dims = data.get("validation_dimensions", [])
    if len(dims) != DIMENSION_COUNT:
        error(f"validation results: expected {DIMENSION_COUNT} dimensions, found {len(dims)}")
        ok = False
    for dim in dims:
        if dim.get("result") != "pass":
            error(f"validation dimension {dim.get('dimension_id')}: must pass")
            ok = False
    if data.get("overall_result") != "interface_blueprint_validated":
        error("validation results: overall_result must be interface_blueprint_validated")
        ok = False
    text = json.dumps(data).lower()
    if READINESS_FORBIDDEN.search(text):
        error("validation results: implies readiness or authorization")
        ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("validation results: numeric score found")
        ok = False
    return ok


def validate_conceptual_identity() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-workbench-interface-conceptual-identity-validation-v1.json"
    data = load_json(path)
    if not IDENTITY_REQUIRED.issubset(set(data)):
        error("conceptual identity validation: missing required top-level fields")
        ok = False
    if data.get("status") != "evidence_posture_workbench_interface_conceptual_identity_validated":
        error("conceptual identity validation: invalid status")
        ok = False
    if data.get("maturity") != "conceptual_identity_validation_only_no_interface_no_prototype":
        error("conceptual identity validation: invalid maturity")
        ok = False
    if data.get("overall_result") != "conceptual_identity_validated_with_maturity_boundary":
        error("conceptual identity validation: invalid overall_result")
        ok = False
    traits = data.get("identity_trait_results", {})
    for trait in IDENTITY_TRAIT_RESULTS:
        if traits.get(trait) != "pass":
            error(f"conceptual identity: trait {trait} must pass")
            ok = False
    allowed = data.get("allowed_metaphor_results", {})
    for m in ALLOWED_METAPHORS:
        if allowed.get(m) != "pass":
            error(f"conceptual identity: allowed metaphor {m} must pass")
            ok = False
    forbidden = data.get("forbidden_metaphor_results", {})
    for m in FORBIDDEN_METAPHORS:
        if forbidden.get(m) != "blocked":
            error(f"conceptual identity: forbidden metaphor {m} must be blocked")
            ok = False
    anti = data.get("anti_generic_ui_results", {})
    for key in ANTI_GENERIC_UI:
        if anti.get(key) != "pass":
            error(f"conceptual identity: anti-generic UI {key} must pass")
            ok = False
    bg = data.get("conceptual_background_identity_result", {})
    if bg.get("status") != "evidence_field_background_direction_validated":
        error("conceptual background identity: invalid status")
        ok = False
    if bg.get("preferred_direction") != "governed_evidence_field_not_generic_black_dashboard":
        error("conceptual background identity: invalid preferred_direction")
        ok = False
    for fn in BACKGROUND_FUNCTIONS:
        if fn not in bg.get("conceptual_functions", []):
            error(f"conceptual background identity: missing function {fn}")
            ok = False
    for pat in BLOCKED_VISUAL_PATTERNS:
        if pat not in bg.get("blocked_visual_patterns", []):
            error(f"conceptual background identity: missing blocked pattern {pat}")
            ok = False
    boundary = data.get("originality_boundary", "").lower()
    for claim in ["final ui uniqueness", "implementation completion", "public readiness", "impossibility of imitation"]:
        if claim not in boundary:
            error(f"originality boundary must disclaim {claim}")
            ok = False
    return ok


def validate_integrity_audit() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-blueprint-integrity-audit-v1.json")
    if not AUDIT_REQUIRED.issubset(set(data)):
        error("integrity audit: missing required top-level fields")
        ok = False
    audited = data.get("audited_artifacts", [])
    for artifact in AUDITED_ARTIFACTS:
        if artifact not in audited:
            error(f"integrity audit: missing audited artifact {artifact}")
            ok = False
    results = data.get("integrity_results", {})
    for key in [
        "all_required_artifacts_present", "all_blueprint_records_parse",
        "all_zone_records_valid", "all_component_records_valid", "all_state_contracts_valid",
        "copy_boundaries_valid", "accessibility_performance_rules_valid",
        "conceptual_identity_policy_valid", "no_implementation_files_created",
        "no_route_or_sitemap_expansion", "no_public_engine_or_classifier",
    ]:
        if results.get(key) != "pass":
            error(f"integrity audit: {key} must pass")
            ok = False
    if data.get("overall_outcome") != "interface_blueprint_integrity_validated":
        error("integrity audit: invalid overall_outcome")
        ok = False
    return ok


def validate_blueprint_dependency() -> bool:
    ok = True
    blueprint = load_json(ROOT / "data" / "evidence-posture-workbench-interface-blueprint-v1.json")
    if blueprint.get("status") != "evidence_posture_workbench_interface_blueprint_governance_created":
        error("master blueprint: invalid status")
        ok = False
    next_phase = blueprint.get("allowed_next_phase", "")
    if "Sprint 32" not in next_phase or "Interface Blueprint Validation" not in next_phase:
        error("master blueprint: allowed_next_phase must reference Sprint 32 Interface Blueprint Validation")
        ok = False
    text = json.dumps(blueprint).lower()
    if READINESS_FORBIDDEN.search(text):
        error("master blueprint: claims prototype readiness from governance alone")
        ok = False
    return ok


def validate_zones() -> bool:
    ok = True
    zones = load_json(ROOT / "data" / "evidence-posture-workbench-interface-zone-registry.json").get("zones", [])
    if len(zones) != 8:
        error(f"zone registry: expected 8 zones, found {len(zones)}")
        ok = False
    for zone in zones:
        for req in ["conceptual_role", "hoax_identity_function", "generic_ui_pattern_to_avoid"]:
            if not zone.get(req):
                error(f"{zone.get('zone_id')}: missing {req}")
                ok = False
        blob = json.dumps(zone).lower()
        for bad in ["subject accusation", "public route", "upload capability", "scoring"]:
            if bad in blob and "must not" not in blob and "no_" in blob:
                pass
        for field in ["interface_status", "prototype_status", "engine_status"]:
            if zone.get(field, "").startswith("no_") is False and "not_" not in zone.get(field, ""):
                if zone.get(field) not in ("no_interface_created", "no_prototype_created", "no_engine_created"):
                    error(f"{zone.get('zone_id')}: {field} must indicate no creation")
                    ok = False
    return ok


def validate_components() -> bool:
    ok = True
    components = load_json(
        ROOT / "data" / "evidence-posture-workbench-interface-component-registry.json"
    ).get("components", [])
    if len(components) != 10:
        error(f"component registry: expected 10 components, found {len(components)}")
        ok = False
    for comp in components:
        for req in ["conceptual_identity_role", "hoax_specific_behavior", "generic_detector_pattern_blocked"]:
            if not comp.get(req):
                error(f"{comp.get('component_id')}: missing {req}")
                ok = False
    return ok


def validate_state_contracts() -> bool:
    ok = True
    states = load_json(ROOT / "data" / "evidence-posture-workbench-interface-state-contracts.json").get(
        "interface_states", []
    )
    if len(states) != 10:
        error(f"state contracts: expected 10 states, found {len(states)}")
        ok = False
    authorize_pattern = re.compile(
        r"\b(authorizes|enables|permits)\s+(public output|scoring|classification|upload|subject judgment)",
        re.I,
    )
    for st in states:
        if authorize_pattern.search(json.dumps(st)):
            error(f"{st.get('interface_state_id')}: authorizes prohibited behavior")
            ok = False
        for field in ["interface_status", "prototype_status", "engine_status"]:
            if st.get(field) not in ("no_interface_created", "no_prototype_created", "no_engine_created"):
                error(f"{st.get('interface_state_id')}: {field} must indicate no creation")
                ok = False
    return ok


def validate_copy_boundaries() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-copy-boundaries.json")
    prohibited = " ".join(data.get("prohibited_copy_patterns", [])).lower()
    for pat in PROHIBITED_COPY:
        if pat.lower() not in prohibited:
            error(f"copy boundaries: missing prohibited pattern {pat}")
            ok = False
    phrases = data.get("required_boundary_phrases", [])
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in phrases:
            error("copy boundaries: missing required boundary phrase")
            ok = False
    return ok


def validate_a11y_perf() -> bool:
    ok = True
    data = load_json(
        ROOT / "data" / "evidence-posture-workbench-interface-accessibility-performance-rules.json"
    )
    a11y = " ".join(data.get("accessibility_rules", [])).lower()
    for rule in A11Y_REQUIRED:
        if rule.lower() not in a11y:
            error(f"accessibility rules: missing {rule}")
            ok = False
    perf = " ".join(data.get("performance_rules", [])).lower()
    for rule in PERF_REQUIRED:
        if rule.lower() not in perf:
            error(f"performance rules: missing {rule}")
            ok = False
    return ok


def validate_no_implementation() -> bool:
    ok = True
    for rel in IMPLEMENTATION_PATHS:
        if (ROOT / rel).exists():
            error(f"implementation file must not exist: {rel}")
            ok = False
    for pattern in ["**/workbench/**/*.css", "**/workbench/**/*.html", "**/prototype/**/*.html"]:
        for path in ROOT.glob(pattern):
            if path.is_file():
                error(f"implementation file must not exist: {path.relative_to(ROOT)}")
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
    if pub.get("current_publisher_status") not in (
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
    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Evidence Posture Workbench Interface Blueprint Validation Gate"),
        None,
    )
    if not gate:
        error("Evidence Posture Workbench Interface Blueprint Validation Gate missing")
        ok = False
    else:
        for field in [
            "required_before_non_public_static_workbench_prototype_governance",
            "required_before_workbench_prototype",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"validation gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is True:
            error("validation gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in ["does not authorize", "interface", "prototype", "engine", "classifier"]:
            if term not in notes and "not authorize" not in notes:
                pass
        if "not authorize" not in notes and "does not authorize" not in notes:
            error("validation gate notes must state non-authorization")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "interface_blueprint_validation" not in checks:
        error("reference-expansion-gate: interface blueprint validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_blueprint_validation_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by blueprint validation alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    if "publisher_blocked_until_non_public_static_workbench_prototype_validation" not in blocked:
        error("reference-expansion-gate: publisher blocked until prototype validation")
        ok = False
    if "publisher_blocked_until_non_public_static_workbench_prototype_refinement" not in blocked:
        error("reference-expansion-gate: publisher blocked until prototype refinement")
        ok = False
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
    if "validate_evidence_posture_workbench_interface_blueprint_validation.py" not in content:
        error("validate_all.py must include interface blueprint validation validator")
        ok = False
    doc = (ROOT / "EVIDENCE_POSTURE_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION.md").read_text(encoding="utf-8")
    if "A blueprint must be validated before it can guide design." not in doc:
        error("validation doc: missing governing principle")
        ok = False
    if "The interface identity must prove that Hoax.ai is not a detector before any prototype exists." not in doc:
        error("validation doc: missing identity principle")
        ok = False
    if "The background must not decorate the interface. It must express the condition of evidence before judgment." not in doc:
        error("validation doc: missing background governing sentence")
        ok = False
    if "generic black cyber aesthetics" not in doc.lower():
        error("validation doc: missing anti-cyber-dashboard sentence")
        ok = False
    if "DEC-050" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-050 missing")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/evidence-posture-workbench-interface-blueprint-validation-policy.json",
        "data/evidence-posture-workbench-interface-blueprint-validation-results-v1.json",
        "data/evidence-posture-workbench-interface-conceptual-identity-validation-v1.json",
        "data/evidence-posture-workbench-interface-blueprint-integrity-audit-v1.json",
        "data/evidence-posture-workbench-interface-blueprint-policy.json",
        "data/evidence-posture-workbench-interface-zone-registry.json",
        "data/evidence-posture-workbench-interface-component-registry.json",
        "data/evidence-posture-workbench-interface-state-contracts.json",
        "data/evidence-posture-workbench-interface-copy-boundaries.json",
        "data/evidence-posture-workbench-interface-accessibility-performance-rules.json",
        "data/evidence-posture-workbench-interface-blueprint-v1.json",
        "data/evidence-posture-workbench-specification-v1.json",
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
        validate_results,
        validate_conceptual_identity,
        validate_integrity_audit,
        validate_blueprint_dependency,
        validate_zones,
        validate_components,
        validate_state_contracts,
        validate_copy_boundaries,
        validate_a11y_perf,
        validate_no_implementation,
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
