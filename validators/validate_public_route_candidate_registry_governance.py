#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Candidate Registry Governance v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "registry_governance_only_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY = "data/public-route-candidate-registry-governance-policy.json"
PROHIBITED = [
    "registering an actual candidate",
    "candidate record instantiation",
    "candidate assessment",
    "candidate route selection",
    "candidate page creation",
    "public route creation",
    "public route approval",
    "sitemap expansion",
    "public navigation link",
    "public workbench creation",
    "prototype modification",
    "prototype exposure",
    "engine",
    "classifier",
    "detector",
    "upload",
    "scoring",
    "fake/real output",
    "generated output",
    "forms",
    "inputs",
    "api",
    "analytics",
    "storage",
    "network calls",
    "monetization",
    "dns",
    "cloudflare",
    "custom domain launch",
    "deployment changes",
    "public release authorization",
    "external factual claims",
    "subject accusation",
    "python cache file commit",
]
ENTRY_FIELDS = [
    "candidate_id",
    "candidate_name",
    "proposed_route_path",
    "proposed_route_title",
    "candidate_class",
    "route_type",
    "public_purpose",
    "explicit_non_purpose",
    "claim_boundary",
    "source_boundary",
    "structured_data_boundary",
    "sitemap_intention",
    "navigation_intention",
    "internal_linking_intention",
    "public_surface_risk",
    "operational_implication_risk",
    "internal_prototype_exposure_risk",
    "artifact_subject_separation_posture",
    "evidence_posture_boundary",
    "anti_detector_language_posture",
    "privacy_security_posture",
    "accessibility_baseline",
    "deployment_DNS_boundary",
    "monetization_boundary",
    "public_release_boundary",
    "assessment_required",
    "current_candidate_state",
    "required_next_gate",
    "non_authorization_statement",
    "date_recorded",
]
FORBIDDEN_ENTRY_FIELDS = [
    "route_created",
    "route_approved",
    "sitemap_entry_created",
    "public_navigation_added",
    "public_workbench_created",
    "engine_enabled",
    "classifier_enabled",
    "upload_enabled",
    "scoring_enabled",
    "API_enabled",
    "analytics_enabled",
    "deployment_enabled",
    "DNS_enabled",
    "Cloudflare_enabled",
    "custom_domain_launched",
    "monetization_enabled",
    "public_release_enabled",
]
BOUNDARY_FIELDS = [
    "no_route_creation_by_registry_entry",
    "no_candidate_assessment_by_registry_entry",
    "no_sitemap_expansion_by_registry_entry",
    "no_public_navigation_by_registry_entry",
    "no_public_workbench_by_registry_entry",
    "no_engine_classifier_upload_scoring_by_registry_entry",
    "no_public_release_by_registry_entry",
]
NON_AUTH_FIELDS = [
    "registry_entry_does_not_authorize_route_creation",
    "registry_entry_does_not_authorize_candidate_assessment",
    "registry_entry_does_not_authorize_sitemap",
    "registry_entry_does_not_authorize_navigation",
    "registry_entry_does_not_authorize_engine",
    "registry_entry_does_not_authorize_classifier",
    "registry_entry_does_not_authorize_upload",
    "registry_entry_does_not_authorize_scoring",
    "registry_entry_does_not_authorize_API",
    "registry_entry_does_not_authorize_analytics",
    "registry_entry_does_not_authorize_deployment",
    "registry_entry_does_not_authorize_DNS_Cloudflare",
    "registry_entry_does_not_authorize_custom_domain_launch",
    "registry_entry_does_not_authorize_public_release",
]
TEMPLATE_BOUNDARY_RULES = [
    "template_is_not_an_entry",
    "template_does_not_create_candidate_id",
    "template_does_not_select_route",
    "template_does_not_assess_candidate",
    "template_does_not_create_route",
    "template_does_not_add_sitemap",
    "template_does_not_add_navigation",
    "template_does_not_expose_prototype",
]
TEMPLATE_NON_AUTH = [
    "no_candidate_registration_by_template",
    "no_candidate_assessment_by_template",
    "no_route_creation_by_template",
    "no_sitemap_expansion_by_template",
    "no_public_navigation_by_template",
    "no_engine_classifier_upload_scoring_by_template",
    "no_deployment_DNS_custom_domain_by_template",
    "no_public_release_by_template",
]
REGISTRY_STATES = [
    "registry_not_created",
    "registry_governance_defined",
    "registry_governance_validated",
    "entry_not_allowed",
    "entry_required_governance",
    "entry_template_defined",
    "entry_ready_for_future_recording",
    "candidate_recorded",
    "candidate_record_requires_assessment",
    "candidate_under_assessment",
    "candidate_assessment_validated",
    "eligible_for_route_creation_sprint",
    "blocked_for_missing_required_fields",
    "blocked_for_public_surface_risk",
    "blocked_for_operational_implication",
    "blocked_for_internal_prototype_exposure",
    "blocked_for_sitemap_or_navigation_gap",
    "blocked_for_engine_classifier_upload_scoring_implication",
    "blocked_for_public_release_implication",
]
TRANSITION_RULES = [
    "no automatic transition to candidate registration",
    "registry_governance_validated may transition only to future_candidate_registration_governance",
    "candidate_recorded requires separate future candidate registration sprint",
    "candidate_record_requires_assessment requires separate future candidate assessment sprint",
    "candidate_assessment_validated may transition only to eligible_for_route_creation_sprint",
    "eligible_for_route_creation_sprint still requires separate future route creation governance",
    "no state authorizes sitemap expansion",
    "no state authorizes public navigation",
    "no state authorizes public release",
]
FORBIDDEN_TRANSITIONS = [
    "registry_governance_defined_to_candidate_recorded",
    "registry_governance_validated_to_candidate_recorded",
    "entry_template_defined_to_candidate_recorded",
    "candidate_recorded_to_public_route_created",
    "candidate_recorded_to_sitemap_entry_created",
    "candidate_recorded_to_public_navigation_added",
    "candidate_recorded_to_engine_enabled",
    "candidate_recorded_to_classifier_enabled",
    "candidate_recorded_to_upload_enabled",
    "candidate_recorded_to_scoring_enabled",
    "candidate_recorded_to_API_enabled",
    "candidate_recorded_to_deployment",
    "candidate_recorded_to_DNS_Cloudflare",
    "candidate_recorded_to_public_release",
]
IDENTITY_FIELDS = [
    "candidate_id",
    "candidate_name",
    "proposed_route_path",
    "proposed_route_title",
    "candidate_class",
    "route_type",
]
BOUNDARY_REQ_FIELDS = [
    "public_purpose",
    "explicit_non_purpose",
    "claim_boundary",
    "source_boundary",
    "structured_data_boundary",
    "artifact_subject_separation_posture",
    "evidence_posture_boundary",
    "anti_detector_language_posture",
]
RISK_FIELDS = [
    "public_surface_risk",
    "operational_implication_risk",
    "internal_prototype_exposure_risk",
    "privacy_security_posture",
    "accessibility_baseline",
    "deployment_DNS_boundary",
    "monetization_boundary",
    "public_release_boundary",
]
STATUS_FIELDS = [
    "sitemap_intention",
    "navigation_intention",
    "internal_linking_intention",
    "assessment_required",
    "current_candidate_state",
    "required_next_gate",
    "non_authorization_statement",
    "date_recorded",
]
BLOCKED_AUTH = [
    "no_candidate_registered",
    "no_candidate_assessed",
    "no_candidate_record_instantiated",
    "no_public_route_authorized",
    "no_sitemap_expansion_authorized",
    "no_public_navigation_authorized",
    "no_public_workbench_authorized",
    "no_engine_authorized",
    "no_classifier_authorized",
    "no_detector_authorized",
    "no_upload_authorized",
    "no_scoring_authorized",
    "no_fake_real_output_authorized",
    "no_API_authorized",
    "no_analytics_authorized",
    "no_DNS_authorized",
    "no_Cloudflare_authorized",
    "no_custom_domain_launch_authorized",
    "no_deployment_authorized",
    "no_monetization_authorized",
    "no_public_tool_authorized",
    "no_public_release_authorized",
]
SOURCE_LOCS = [
    "PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_V1.md",
    "data/public-route-candidate-registry-governance-policy.json",
    "data/public-route-candidate-registry-schema-v1.json",
    "data/public-route-candidate-registry-entry-template-v1.json",
    "data/public-route-candidate-registry-state-model-v1.json",
    "data/public-route-candidate-registry-entry-requirements-v1.json",
    "data/public-route-candidate-registry-non-authorization-rules-v1.json",
    "data/public-route-candidate-registry-boundary-audit-v1.json",
    "validators/validate_public_route_candidate_registry_governance.py",
]
NUMERIC = re.compile(r"\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b", re.I)
INSTANTIATED_ENTRY_GLOBS = ["data/public-route-candidate-registry-entry-*.json"]
SKIP_ENTRY_SUFFIXES = ("template", "validation", "schema", "governance", "requirements", "non-authorization", "boundary-audit", "state-model")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def has_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower() in text or item.lower().replace("_", " ") in text for item in required)


def skip_instantiated(path: Path) -> bool:
    name = path.name.lower()
    return any(part in name for part in SKIP_ENTRY_SUFFIXES)


def validate_doctrine() -> bool:
    ok = True
    text = (ROOT / "PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_V1.md").read_text(encoding="utf-8")
    required = [
        "A candidate registry governs how candidates may be recorded. It does not create, assess, approve, or publish candidates.",
        "A registry entry is not a route. A registered candidate is not an assessed candidate. A governed registry is not launch permission.",
        "governed internal record system",
        "registry_not_created",
        "candidate_recorded",
        "eligible_for_route_creation_sprint",
        "blocked_for_public_release_implication",
        "Sprint 48 records no candidate entry.",
        "maturity: registry_governance_only_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
    ]
    for phrase in required:
        if phrase not in text:
            error(f"doctrine: missing {phrase}")
            ok = False
    for term in [
        "public route creation",
        "sitemap inclusion",
        "workbench launch",
        "engine readiness",
        "public release readiness",
    ]:
        if term not in text.lower():
            error(f"doctrine: registry-is-not missing {term}")
            ok = False
    return ok


def validate_policy() -> bool:
    ok = True
    d = load(POLICY)
    if d.get("status") != "governed_public_route_candidate_registry_policy":
        error("policy invalid status")
        ok = False
    if d.get("maturity") != MATURE:
        error("policy invalid maturity")
        ok = False
    if not has_all(
        d.get("allowed_governance_actions", []),
        [
            "registry governance definition",
            "registry schema definition",
            "registry entry template definition",
            "registry state modeling",
            "entry requirement definition",
            "non-authorization rule definition",
            "boundary audit creation",
            "publisher gate update",
            "reference gate update",
            "validation only",
        ],
    ):
        error("policy missing allowed governance actions")
        ok = False
    if not has_all(d.get("prohibited_actions", []), PROHIBITED):
        error("policy missing prohibited actions")
        ok = False
    blocked = " ".join(d.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in [
        "candidate registration",
        "candidate assessment",
        "candidate record instantiation",
        "public route creation",
        "sitemap expansion",
        "public navigation",
        "public workbench",
        "engine",
        "classifier",
        "upload",
        "scoring",
        "api",
        "analytics",
        "deployment",
        "dns",
        "cloudflare",
        "custom domain launch",
        "monetization",
        "public tool behavior",
        "prototype modification",
        "prototype exposure",
        "production readiness",
        "public release",
        "python cache commit",
    ]:
        if term not in blocked:
            error(f"policy non-authorization missing {term}")
            ok = False
    zero = str(d.get("registry_zero_state", "")).lower()
    if "no candidates are registered" not in zero and "no candidate" not in zero:
        error("policy registry_zero_state must state no candidates registered")
        ok = False
    if NUMERIC.search((ROOT / POLICY).read_text(encoding="utf-8")):
        error("policy contains numeric score/grade/percentage")
        ok = False
    return ok


def validate_schema() -> bool:
    ok = True
    s = load("data/public-route-candidate-registry-schema-v1.json")
    if not set(ENTRY_FIELDS).issubset(set(s.get("required_entry_fields", []))):
        error("schema missing required_entry_fields")
        ok = False
    if not set(FORBIDDEN_ENTRY_FIELDS).issubset(set(s.get("forbidden_entry_fields", []))):
        error("schema missing forbidden_entry_fields")
        ok = False
    if not set(BOUNDARY_FIELDS).issubset(set(s.get("required_boundary_fields", []))):
        error("schema missing required_boundary_fields")
        ok = False
    if not set(NON_AUTH_FIELDS).issubset(set(s.get("required_non_authorization_fields", []))):
        error("schema missing required_non_authorization_fields")
        ok = False
    zs = s.get("registry_zero_state", {})
    for key in [
        "no_candidate_entries_exist",
        "no_candidate_ids_created",
        "no_candidate_records_instantiated",
        "no_candidate_pages_created",
    ]:
        if zs.get(key) is not True:
            error(f"schema registry_zero_state missing {key}")
            ok = False
    return ok


def validate_entry_template() -> bool:
    ok = True
    t = load("data/public-route-candidate-registry-entry-template-v1.json")
    if not set(ENTRY_FIELDS).issubset(set(t.get("template_fields", []))):
        error("entry template missing template_fields")
        ok = False
    if not set(TEMPLATE_BOUNDARY_RULES).issubset(set(t.get("template_boundary_rules", []))):
        error("entry template missing template_boundary_rules")
        ok = False
    if not set(TEMPLATE_NON_AUTH).issubset(set(t.get("template_non_authorization_rules", []))):
        error("entry template missing template_non_authorization_rules")
        ok = False
    if t.get("template_zero_state") != "no_instantiated_entry_exists":
        error("entry template template_zero_state must be no_instantiated_entry_exists")
        ok = False
    for pattern in INSTANTIATED_ENTRY_GLOBS:
        for p in ROOT.glob(pattern):
            if skip_instantiated(p):
                continue
            error(f"instantiated registry entry exists: {p.name}")
            ok = False
    return ok


def validate_state_model() -> bool:
    ok = True
    sm = load("data/public-route-candidate-registry-state-model-v1.json")
    if not set(REGISTRY_STATES).issubset(set(sm.get("registry_states", []))):
        error("state model missing registry_states")
        ok = False
    rules = " ".join(sm.get("transition_rules", [])).lower()
    for term in TRANSITION_RULES:
        if term.lower() not in rules:
            error(f"state model missing transition rule: {term}")
            ok = False
    if not set(FORBIDDEN_TRANSITIONS).issubset(set(sm.get("forbidden_transitions", []))):
        error("state model missing forbidden_transitions")
        ok = False
    stmt = sm.get("non_authorization_statement", "").lower()
    for term in [
        "candidate registration",
        "route creation",
        "sitemap expansion",
        "public navigation",
        "public release",
    ]:
        if term not in stmt:
            error(f"state model non_authorization_statement missing {term}")
            ok = False
    return ok


def validate_entry_requirements() -> bool:
    ok = True
    r = load("data/public-route-candidate-registry-entry-requirements-v1.json")
    if not set(IDENTITY_FIELDS).issubset(set(r.get("required_identity_fields", []))):
        error("entry requirements missing required_identity_fields")
        ok = False
    if not set(BOUNDARY_REQ_FIELDS).issubset(set(r.get("required_boundary_fields", []))):
        error("entry requirements missing required_boundary_fields")
        ok = False
    if not set(RISK_FIELDS).issubset(set(r.get("required_risk_fields", []))):
        error("entry requirements missing required_risk_fields")
        ok = False
    if not set(STATUS_FIELDS).issubset(set(r.get("required_status_fields", []))):
        error("entry requirements missing required_status_fields")
        ok = False
    if r.get("blocked_missing_field_policy") != "missing_any_required_field_blocks_candidate_registration":
        error("entry requirements invalid blocked_missing_field_policy")
        ok = False
    if not r.get("non_authorization_statement"):
        error("entry requirements missing non_authorization_statement")
        ok = False
    return ok


def validate_non_authorization() -> bool:
    ok = True
    na = load("data/public-route-candidate-registry-non-authorization-rules-v1.json")
    if not set(BLOCKED_AUTH).issubset(set(na.get("blocked_authorizations", []))):
        error("non-authorization missing blocked_authorizations")
        ok = False
    expected = {
        "registry_boundary": "registry_governance_only_no_entries",
        "candidate_registration_boundary": "candidate_registration_requires_future_registration_sprint",
        "candidate_assessment_boundary": "candidate_assessment_requires_future_assessment_sprint",
        "route_creation_boundary": "route_creation_requires_future_route_creation_sprint",
        "public_release_boundary": "public_release_remains_blocked",
        "internal_prototype_boundary": "internal_prototype_remains_non_public_static_unlinked_unrouted_unindexed",
        "overall_result": "public_route_candidate_registry_non_authorization_defined",
    }
    for key, value in expected.items():
        if na.get(key) != value:
            error(f"non-authorization: {key} must be {value}")
            ok = False
    return ok


def validate_audit() -> bool:
    ok = True
    a = load("data/public-route-candidate-registry-boundary-audit-v1.json")
    if a.get("overall_outcome") != "public_route_candidate_registry_governance_boundary_validated":
        error("audit invalid overall_outcome")
        ok = False
    groups = {
        "audited_scope": [
            "public route candidate registry governance only",
            "current public surface",
            "current sitemap",
            "current route registry",
            "internal prototype as read-only boundary reference",
        ],
        "registry_results": [
            "registry_governance_created",
            "no_populated_registry_created",
            "no_candidate_entries_created",
            "no_candidate_ids_created",
            "no_candidate_records_instantiated",
            "no_candidate_pages_created",
        ],
        "candidate_results": [
            "no_candidate_registered",
            "no_candidate_assessed",
            "no_candidate_selected",
            "no_candidate_approved",
        ],
        "route_surface_results": [
            "no_public_route_created",
            "no_route_registry_entry_added",
            "no_sitemap_entry_added",
            "no_public_navigation_added",
            "no_public_workbench_created",
        ],
        "prototype_boundary_results": [
            "prototype_files_not_modified",
            "internal_prototype_not_exposed",
            "internal_prototype_not_linked",
            "internal_prototype_not_routed",
            "internal_prototype_not_sitemap_listed",
        ],
        "public_surface_results": [
            "public_surface_unchanged_four_urls",
            "homepage_unchanged_for_route_links",
            "reference_pages_unchanged_for_route_links",
            "language_page_unchanged_for_route_links",
        ],
        "capability_block_results": [
            "no_engine",
            "no_classifier",
            "no_detector",
            "no_upload",
            "no_scoring",
            "no_fake_real",
            "no_api",
            "no_analytics",
            "no_storage",
            "no_network_calls",
            "no_deployment_change",
            "no_DNS_change",
            "no_Cloudflare_change",
            "no_custom_domain_launch",
            "no_public_release",
        ],
        "python_cache_results": [
            "no_pycache_tracked",
            "no_pyc_staged",
            "no_python_cache_committed",
        ],
    }
    for key, req in groups.items():
        if not set(req).issubset(set(a.get(key, []))):
            error(f"audit missing {key}")
            ok = False
    return ok


def validate_files_public() -> bool:
    ok = True
    if not all((ROOT / x).is_file() for x in LOCKED_FILES):
        error("prototype files missing")
        return False
    if {x.name for x in PROTO_DIR.iterdir() if x.is_file()} != {"index.html", "prototype.css"}:
        error("prototype dir has extra files")
        ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files modified in Sprint 48")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 48")
        ok = False
    routes = load("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    route_text = json.dumps(routes).lower()
    if "evidence-posture-workbench" in route_text or "internal_prototypes" in route_text:
        error("prototype registered as route")
        ok = False
    locs = [e.text.strip().lower() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT or any("evidence-posture-workbench" in x or "internal_prototypes" in x for x in locs):
        error("sitemap mismatch or prototype leak")
        ok = False
    pat = re.compile(
        r"internal_prototypes|evidence-posture-workbench|/workbench/|/tool/|/classifier/|/detector/|/upload/|/score/|/demo/|/prototype/",
        re.I,
    )
    for rel in [
        "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "language/index.html",
    ]:
        if pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel} links to prototype or blocked route")
            ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll exists")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    pub = load("data/publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
        "blocked_until_public_reference_system_map_surface_validation",        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,

    ):
        error("publisher status must be blocked until public route candidate registry governance validation")
        ok = False
    gate = next(
        (
            g
            for g in load("data/publisher-quality-gates.json").get("gates", [])
            if g.get("name") == "Public Route Candidate Registry Governance Gate"
        ),
        None,
    )
    if not gate:
        error("public route candidate registry governance gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_candidate_registry_governance_validation",
            "required_before_any_candidate_registry_entry",
            "required_before_any_candidate_assessment",
            "required_before_any_public_route",
            "required_before_any_public_route_creation_sprint",
            "required_before_any_sitemap_expansion",
            "required_before_any_public_navigation",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"gate {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in [
            "candidate registration",
            "candidate assessment",
            "public engine",
            "public classifier",
            "public tool",
            "public route",
            "sitemap",
            "navigation",
            "upload",
            "scoring",
            "api",
            "forms",
            "analytics",
            "deployment",
            "dns",
            "cloudflare",
            "custom domain launch",
            "public release",
        ]:
            if term not in notes:
                error(f"gate notes missing {term}")
                ok = False
    exp = load("data/reference-expansion-gate.json")
    checks = " ".join(exp.get("required_pre_release_checks", [])).lower()
    rules = " ".join(exp.get("release_eligibility_rules", [])).lower()
    if "public_route_candidate_registry_governance" not in checks:
        error("reference gate missing public_route_candidate_registry_governance")
        ok = False
    if "no_candidate_registry_entries_by_registry_governance_alone" not in rules:
        error("reference gate must block candidate registry entries by registry governance alone")
        ok = False
    if "no_public_route_candidate_assessment_by_registry_governance_alone" not in rules:
        error("reference gate must block candidate assessment by registry governance alone")
        ok = False
    if "no_public_route_creation_by_registry_governance_alone" not in rules:
        error("reference gate must block route creation by registry governance alone")
        ok = False
    if "no_public_engine_eligibility_by_registry_governance" not in rules:
        error("reference gate must block engine eligibility by registry governance")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0054" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0054 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0054" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0054 map missing")
        ok = False
    if "validate_public_route_candidate_registry_governance.py" not in (
        ROOT / "validators" / "validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing sprint 48 validator")
        ok = False
    if "DEC-066" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-066 missing")
        ok = False
    val = load("data/public-route-candidate-assessment-governance-validation-results-v1.json")
    if val.get("overall_result") != "public_route_candidate_assessment_governance_validated":
        error("Sprint 47 assessment governance validation must show governance validated")
        ok = False
    return ok


def validate_cache() -> bool:
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines() + subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error(f"python cache tracked/staged: {rel}")
            return False
    return True


def main() -> int:
    parse = [
        POLICY,
        "data/public-route-candidate-registry-schema-v1.json",
        "data/public-route-candidate-registry-entry-template-v1.json",
        "data/public-route-candidate-registry-state-model-v1.json",
        "data/public-route-candidate-registry-entry-requirements-v1.json",
        "data/public-route-candidate-registry-non-authorization-rules-v1.json",
        "data/public-route-candidate-registry-boundary-audit-v1.json",
        "data/public-route-candidate-assessment-governance-validation-results-v1.json",
        "data/public-route-candidate-assessment-framework-validation-v1.json",
        "data/public-route-candidate-assessment-record-template-validation-v1.json",
        "data/public-route-candidate-assessment-state-model-validation-v1.json",
        "data/public-route-candidate-assessment-non-authorization-validation-v1.json",
        "data/public-route-eligibility-governance-validation-results-v1.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
    ]
    for rel in parse:
        try:
            load(rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"parse failed {rel}: {exc}")
            return 1
    for rel in [
        "sitemap.xml",
        "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "language/index.html",
        *LOCKED_FILES,
    ]:
        if not (ROOT / rel).is_file():
            error(f"missing file {rel}")
            return 1
        (ROOT / rel).read_text(encoding="utf-8")

    checks = [
        validate_doctrine,
        validate_policy,
        validate_schema,
        validate_entry_template,
        validate_state_model,
        validate_entry_requirements,
        validate_non_authorization,
        validate_audit,
        validate_files_public,
        validate_governance,
        validate_cache,
    ]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
