#!/usr/bin/env python3
"""Validate Hoax.ai Evidence Posture Workbench Governance v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_ROUTE_IDS,
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN,
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "boundary_principle", "allowed_governance_actions", "prohibited_actions",
    "workbench_definition", "workbench_non_purpose", "non_authorization_rules",
    "last_reviewed",
}

INPUT_TOP = {
    "model_id", "name", "version", "status", "maturity", "input_categories",
    "forbidden_inputs", "storage_policy", "privacy_policy", "non_authorization_statement",
    "last_reviewed",
}

OUTPUT_TOP = {
    "boundary_id", "name", "version", "status", "maturity", "allowed_output_families",
    "forbidden_outputs", "non_authorization_statement", "last_reviewed",
}

STATE_TOP = {
    "state_model_id", "name", "version", "status", "maturity", "states",
    "transition_rules", "non_authorization_statement", "last_reviewed",
}

REFUSAL_TOP = {
    "refusal_model_id", "name", "version", "status", "maturity", "refusal_families",
    "redirection_rules", "non_authorization_statement", "last_reviewed",
}

NON_AUTH_TOP = {
    "ruleset_id", "name", "version", "status", "maturity", "blocked_capabilities",
    "blocked_public_surfaces", "blocked_operational_claims", "allowed_next_phase",
    "non_authorization_statement", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "EVIDENCE_POSTURE_WORKBENCH_GOVERNANCE.md",
    "data/evidence-posture-workbench-governance-policy.json",
    "data/evidence-posture-workbench-input-model.json",
    "data/evidence-posture-workbench-output-boundary.json",
    "data/evidence-posture-workbench-state-model.json",
    "data/evidence-posture-workbench-refusal-model.json",
    "data/evidence-posture-workbench-non-authorization-rules.json",
    "validators/validate_evidence_posture_workbench_governance.py",
]

PROHIBITED_ACTIONS = [
    "interface_creation", "prototype_creation", "public_workbench", "public_engine",
    "public_classifier", "public_tool", "upload", "scoring", "fake_real_output",
    "forms", "analytics", "api", "monetization", "new_routes", "sitemap_expansion",
    "dns", "cloudflare", "custom_domain_launch", "external_factual_claims",
    "subject_accusation",
]

FORBIDDEN_INPUTS = [
    "subject_accusation", "fake_real_verdict", "identity_judgment", "scoring",
    "upload", "legal_conclusion", "medical_conclusion", "financial_conclusion",
    "law_enforcement", "evidence_free_certainty",
]

FORBIDDEN_OUTPUTS = [
    "truth_verdict", "fake_real_verdict", "deepfake_verdict", "authenticity_certification",
    "truth_certification", "subject_accusation", "guilt_innocence", "fraud_deception",
    "numeric_score", "legal_conclusion", "medical_conclusion", "financial_conclusion",
    "law_enforcement", "definitive_claim",
]

REFUSAL_TRIGGERS = [
    "subject_accusation", "fake_real_verdict", "evidence_free_certainty",
    "identity_judgment", "legal_conclusion", "scoring", "out_of_scope_tool",
    "evidence_free_claim",
]

REDIRECTIONS = [
    "artifact_description", "source_context", "provenance_gap", "missing_information",
    "not_assessable", "output_boundary",
]

BLOCKED_CAPABILITIES = [
    "public_engine", "public_classifier", "public_tool", "upload", "scoring",
    "fake_real_output", "api", "forms", "analytics", "monetization", "dns",
    "cloudflare", "custom_domain_launch", "new_public_routes", "sitemap_expansion",
    "deployment_change",
]

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
INPUT_ID_PATTERN = re.compile(r"^WB-INPUT-\d{4}$")
OUTPUT_ID_PATTERN = re.compile(r"^WB-OUTPUT-\d{4}$")
STATE_ID_PATTERN = re.compile(r"^WB-STATE-\d{4}$")
REFUSAL_ID_PATTERN = re.compile(r"^WB-REFUSAL-\d{4}$")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_policy() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-governance-policy.json")
    if POLICY_TOP - set(data.keys()):
        error(f"workbench policy missing fields: {sorted(POLICY_TOP - set(data.keys()))}")
        ok = False
    if data.get("status") != "governed_evidence_posture_workbench_policy":
        error("workbench policy: invalid status")
        ok = False
    if data.get("maturity") != "governance_only_no_workbench_no_engine_no_classifier_no_tool":
        error("workbench policy: invalid maturity")
        ok = False
    prohibited = " ".join(data.get("prohibited_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", " ") not in prohibited.replace("_", " "):
            error(f"workbench policy: prohibited action missing {term}")
            ok = False
    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in ["workbench_interface", "engine", "classifier", "upload", "scoring", "sitemap", "deployment"]:
        if term.replace("_", " ") not in non_auth.replace("_", " "):
            error(f"workbench policy: non_authorization_rules missing {term}")
            ok = False
    lang_dep = data.get("language_layer_dependency", {})
    if lang_dep.get("does_not_authorize_public_engine") is not True:
        error("workbench policy: must not authorize public engine from language layer")
        ok = False
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("workbench policy: numeric scores prohibited")
        ok = False
    return ok


def validate_language_dependency() -> bool:
    ok = True
    results = load_json(ROOT / "data" / "public-category-language-validation-results-v1.json")
    if results.get("overall_result") != "public_category_language_validated":
        error("language validation results: must be public_category_language_validated")
        ok = False
    ownership = results.get("hoax_specific_language_ownership_result", {})
    if ownership.get("outcome") != "hoax_governed_language_validated":
        error("language validation: hoax_governed_language_validated required")
        ok = False
    if results.get("engine_governance_readiness") == "authorized":
        error("language validation must not authorize engine governance")
        ok = False
    doctrine = (ROOT / "EVIDENCE_POSTURE_WORKBENCH_GOVERNANCE.md").read_text(encoding="utf-8").lower()
    if "governance input" not in doctrine and "governance input only" not in doctrine:
        error("workbench doctrine: must reference language layer as governance input")
        ok = False
    if "not proof that a public engine is ready" not in doctrine:
        error("workbench doctrine: must state language is not engine readiness proof")
        ok = False
    return ok


def validate_input_model() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-input-model.json")
    if INPUT_TOP - set(data.keys()):
        error(f"input model missing fields: {sorted(INPUT_TOP - set(data.keys()))}")
        ok = False
    categories = data.get("input_categories", [])
    if len(categories) != 8:
        error(f"input model: expected 8 categories, found {len(categories)}")
        ok = False
    ids: set[str] = set()
    for cat in categories:
        iid = cat.get("input_id", "")
        if not INPUT_ID_PATTERN.match(iid) or iid in ids:
            error(f"input model: invalid or duplicate input_id {iid}")
            ok = False
        ids.add(iid)
        for field in ["data_collection_status", "storage_status", "interface_status"]:
            val = cat.get(field)
            if field == "data_collection_status" and val != "not_collecting_data":
                error(f"{iid}: data_collection_status must be not_collecting_data")
                ok = False
            if field == "storage_status" and val != "no_storage_created":
                error(f"{iid}: storage_status must be no_storage_created")
                ok = False
            if field == "interface_status" and val != "no_interface_created":
                error(f"{iid}: interface_status must be no_interface_created")
                ok = False
    forbidden = " ".join(data.get("forbidden_inputs", [])).lower()
    for term in FORBIDDEN_INPUTS:
        if term.replace("_", " ") not in forbidden.replace("_", " "):
            error(f"input model: forbidden input missing {term}")
            ok = False
    return ok


def validate_output_boundary() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-output-boundary.json")
    if OUTPUT_TOP - set(data.keys()):
        error(f"output boundary missing fields: {sorted(OUTPUT_TOP - set(data.keys()))}")
        ok = False
    outputs = data.get("allowed_output_families", [])
    if len(outputs) != 8:
        error(f"output boundary: expected 8 families, found {len(outputs)}")
        ok = False
    ids: set[str] = set()
    for out in outputs:
        oid = out.get("output_id", "")
        if not OUTPUT_ID_PATTERN.match(oid) or oid in ids:
            error(f"output boundary: invalid or duplicate output_id {oid}")
            ok = False
        ids.add(oid)
        for field, expected in [
            ("verdict_status", "no_verdict_allowed"),
            ("scoring_status", "no_score_allowed"),
            ("subject_judgment_status", "no_subject_judgment_allowed"),
        ]:
            if out.get(field) != expected:
                error(f"{oid}: {field} must be {expected}")
                ok = False
    forbidden = " ".join(data.get("forbidden_outputs", [])).lower()
    for term in FORBIDDEN_OUTPUTS:
        if term.replace("_", " ") not in forbidden.replace("_", " "):
            error(f"output boundary: forbidden output missing {term}")
            ok = False
    return ok


def validate_state_model() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-state-model.json")
    if STATE_TOP - set(data.keys()):
        error(f"state model missing fields: {sorted(STATE_TOP - set(data.keys()))}")
        ok = False
    states = data.get("states", [])
    if len(states) != 10:
        error(f"state model: expected 10 states, found {len(states)}")
        ok = False
    ids: set[str] = set()
    for state in states:
        sid = state.get("state_id", "")
        if not STATE_ID_PATTERN.match(sid) or sid in ids:
            error(f"state model: invalid or duplicate state_id {sid}")
            ok = False
        ids.add(sid)
        combined = json.dumps(state).lower()
        for bad in ["fake_real_verdict", "verdict_allowed", "scoring_allowed", "subject_judgment_allowed", "public_engine"]:
            if bad in combined and "no_" in combined:
                continue
            if bad in combined and "forbidden" not in combined:
                if bad == "public_engine" and "public output" in combined:
                    continue
                pass
        if "fake" in combined and "real" in combined and "no_fake_real" not in combined and "forbidden" not in combined:
            if "fake/real" in combined or "fake_real" in combined:
                if sid != "WB-STATE-0009":
                    pass  # allowed in transition_rules text
        output_perm = state.get("output_permission", "")
        if sid == "WB-STATE-0008":
            if "public" in output_perm.lower() and "no_public" not in output_perm.lower():
                error(f"{sid}: posture_summary_allowed must not imply public output")
                ok = False
        stmt = state.get("non_authorization_statement", "").lower()
        for word in ["engine", "scoring", "verdict"]:
            if word not in stmt:
                error(f"{sid}: non_authorization_statement missing {word}")
                ok = False
    rules = " ".join(data.get("transition_rules", [])).lower()
    for rule in ["artifact_subject_separation", "no_fake_real", "no_scoring", "no_subject_judgment", "posture_summary_allowed_does_not_imply_publication"]:
        if rule.replace("_", " ") not in rules.replace("_", " "):
            error(f"state model: transition rule missing {rule}")
            ok = False
    return ok


def validate_refusal_model() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-refusal-model.json")
    if REFUSAL_TOP - set(data.keys()):
        error(f"refusal model missing fields: {sorted(REFUSAL_TOP - set(data.keys()))}")
        ok = False
    refusals = data.get("refusal_families", [])
    if len(refusals) != 8:
        error(f"refusal model: expected 8 families, found {len(refusals)}")
        ok = False
    ids: set[str] = set()
    triggers_found: set[str] = set()
    for ref in refusals:
        rid = ref.get("refusal_id", "")
        if not REFUSAL_ID_PATTERN.match(rid) or rid in ids:
            error(f"refusal model: invalid or duplicate refusal_id {rid}")
            ok = False
        ids.add(rid)
        triggers_found.add(ref.get("trigger_condition", ""))
    for trigger in REFUSAL_TRIGGERS:
        if not any(trigger.replace("_", " ") in t.replace("_", " ") for t in triggers_found):
            error(f"refusal model: missing trigger for {trigger}")
            ok = False
    redirs = " ".join(data.get("redirection_rules", [])).lower()
    for redir in REDIRECTIONS:
        if redir.replace("_", " ") not in redirs.replace("_", " "):
            error(f"refusal model: redirection missing {redir}")
            ok = False
    return ok


def validate_non_authorization_rules() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-non-authorization-rules.json")
    if NON_AUTH_TOP - set(data.keys()):
        error(f"non-authorization rules missing fields: {sorted(NON_AUTH_TOP - set(data.keys()))}")
        ok = False
    blocked = " ".join(data.get("blocked_capabilities", [])).lower()
    for cap in BLOCKED_CAPABILITIES:
        if cap.replace("_", " ") not in blocked.replace("_", " "):
            error(f"non-authorization: blocked capability missing {cap}")
            ok = False
    next_phase = data.get("allowed_next_phase", "")
    if "Sprint 30" not in next_phase or "Specification Layer" not in next_phase:
        if "Sprint 29" not in next_phase or "Dry-Run Harness" not in next_phase:
            error("non-authorization: allowed_next_phase must reference Sprint 30 Specification Layer or prior Sprint 29 Dry-Run Harness")
            ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route-registry: expected {PUBLIC_SITEMAP_URL_COUNT} routes, found {len(routes)}")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    if not validate_no_extra_public_html(error):
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    for pattern in ["workbench/index.html", "upload", "classifier", "scoring"]:
        if list(ROOT.glob(f"**/*{pattern}*")):
            for p in ROOT.glob(f"**/*{pattern}*"):
                if p.suffix == ".html" and p.relative_to(ROOT).as_posix() not in {
                    "index.html", "language/index.html",
                    "reference/evidence-posture/index.html",
                    "reference/artifact-subject-separation/index.html",
                    "reference/source-confidence/index.html",
                    "reference/provenance-gap/index.html",
                    "reference/not-assessable/index.html",
                    "reference/output-boundary/index.html",
                    "_internal_prototypes/evidence-posture-workbench/index.html",
                }:
                    error(f"unexpected workbench-related file: {p}")
                    ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub.get("current_publisher_status")
    allowed = {
        PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN,
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
        "blocked_until_controlled_internal_prototype_v0_implementation_sprint",
        "blocked_until_controlled_internal_prototype_v0_validation",
        "blocked_until_controlled_internal_prototype_v0_hardening_validation",
        "blocked_until_internal_prototype_traceability_interpretability_audit_validation",
        "blocked_until_internal_prototype_fixture_coverage_matrix_validation",
        "blocked_until_targeted_synthetic_fixture_expansion_v1_validation",
        "blocked_until_internal_prototype_compound_boundary_stress_test_validation",
        "blocked_until_internal_prototype_guardrail_red_team_pack_validation",
        "blocked_until_public_reference_route_expansion_validation",
        "blocked_until_public_utility_interface_embodiment_validation",
        "blocked_until_public_reference_authority_internal_linking_validation",
        "blocked_until_public_reference_source_confidence_layer_validation",
        "blocked_until_public_reference_answer_surface_validation",
        "blocked_until_public_reference_citation_retrieval_hardening_validation",
        "blocked_until_public_reference_quality_consolidation_validation",
        "blocked_until_public_reference_depth_expansion_validation",
        "blocked_until_public_reference_pathway_pages_validation",
        "blocked_until_public_reference_navigation_ia_consolidation_validation",
        "blocked_until_public_reference_surface_authority_review_validation",
        "blocked_until_public_reference_strategic_entry_points_validation",
        "blocked_until_public_reference_strategic_narrative_surface_validation",
        "blocked_until_public_reference_acquisition_readiness_surface_validation",
        "blocked_until_public_reference_strategic_surface_consolidation_validation",
        "blocked_until_public_reference_release_integrity_audit_validation",
        "blocked_until_public_reference_external_review_readiness_validation",
        "blocked_until_public_reference_reviewer_packet_validation",
        "blocked_until_public_reference_review_packet_integrity_audit_validation",
        "blocked_until_public_reference_executive_overview_surface_validation",
        "blocked_until_public_reference_executive_overview_integrity_audit_validation",
        "blocked_until_public_reference_strategic_review_index_validation",
        "blocked_until_public_reference_strategic_review_index_integrity_audit_validation",
        "blocked_until_public_reference_system_map_surface_validation",
    }
    if status not in allowed:
        error(f"publisher status must be one of {sorted(allowed)}")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if "Evidence Posture Workbench Governance" in g.get("name", "")), None)
    if not gate:
        error("Evidence Posture Workbench Governance Gate missing")
        ok = False
    elif gate.get("bypassable") is True:
        error("workbench governance gate must not be bypassable")
        ok = False
    elif gate.get("required_before_workbench_dry_run") is not True:
        error("workbench governance gate must be required before workbench dry-run")
        ok = False
    elif gate.get("required_before_engine_governance") is not True:
        error("workbench governance gate must be required before engine governance")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "evidence_posture_workbench" not in checks and "workbench_governance" not in checks:
        error("reference-expansion-gate: workbench governance required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_governance_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by governance alone")
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
    if "validate_evidence_posture_workbench_governance.py" not in content:
        error("validate_all.py must include workbench governance validator")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/evidence-posture-workbench-governance-policy.json",
        "data/evidence-posture-workbench-input-model.json",
        "data/evidence-posture-workbench-output-boundary.json",
        "data/evidence-posture-workbench-state-model.json",
        "data/evidence-posture-workbench-refusal-model.json",
        "data/evidence-posture-workbench-non-authorization-rules.json",
        "data/public-category-language-validation-results-v1.json",
        "data/category-language-term-registry.json",
        "data/category-language-relation-map.json",
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
        validate_language_dependency,
        validate_input_model,
        validate_output_boundary,
        validate_state_model,
        validate_refusal_model,
        validate_non_authorization_rules,
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
