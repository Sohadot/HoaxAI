#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Candidate Registry Governance Validation v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,

    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "validation_only_candidate_registry_governance_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY_STATUS = "governed_public_route_candidate_registry_governance_validation_policy"
POLICY = "data/public-route-candidate-registry-governance-validation-policy.json"
DIMENSIONS = [
    "Candidate Registry Governance Policy Integrity",
    "Candidate Registry Definition Integrity",
    "Registry Is Not Candidate Registration",
    "Registry Is Not Candidate Assessment",
    "Registry Is Not Route Creation",
    "Registry Zero-State Integrity",
    "Registry Schema Integrity",
    "Required Entry Field Integrity",
    "Forbidden Entry Field Integrity",
    "Required Boundary Field Integrity",
    "Required Non-Authorization Field Integrity",
    "Entry Template Integrity",
    "Template Zero-State Integrity",
    "Template Does Not Create Candidate ID",
    "Template Does Not Select Route",
    "Template Does Not Assess Candidate",
    "Template Does Not Create Route",
    "Template Does Not Add Sitemap",
    "Template Does Not Add Navigation",
    "Template Does Not Expose Prototype",
    "Registry State Model Integrity",
    "Registry State Integrity",
    "Transition Rule Integrity",
    "Forbidden Transition Integrity",
    "Entry Requirement Integrity",
    "Identity Field Requirement Integrity",
    "Boundary Field Requirement Integrity",
    "Risk Field Requirement Integrity",
    "Status Field Requirement Integrity",
    "Missing Field Policy Integrity",
    "Non-Authorization Rules Integrity",
    "Registry Boundary Integrity",
    "Candidate Registration Boundary Integrity",
    "Candidate Assessment Boundary Integrity",
    "Route Creation Boundary Integrity",
    "Public Release Boundary Integrity",
    "Internal Prototype Boundary Integrity",
    "Candidate Assessment Governance Validation Dependency",
    "Route Eligibility Governance Validation Dependency",
    "Public-Readiness Boundary Dependency",
    "Visual Baseline Lock Dependency",
    "No Populated Registry Created",
    "No Candidate Entry Created",
    "No Candidate ID Created",
    "No Candidate Record Instantiated",
    "No Candidate Page Created",
    "No Candidate Registered",
    "No Candidate Assessed",
    "No Candidate Selected",
    "No Candidate Approved",
    "Public Route Exclusion",
    "Route Registry Non-Expansion",
    "Sitemap Exclusion",
    "Public Navigation Exclusion",
    "Homepage Link Exclusion",
    "Reference Page Link Exclusion",
    "Language Page Link Exclusion",
    "Internal Prototype Non-Exposure",
    "Prototype Files Not Modified",
    "No Additional Prototype Files",
    "No JavaScript",
    "No Forms or Inputs",
    "No Upload Surface",
    "No Scoring Surface",
    "No Fake/Real Verdict Surface",
    "No API/Network/Storage Behavior",
    "No Analytics",
    "No DNS/Cloudflare/Deployment Change",
    "No Public Workbench Authorization",
    "No Public Engine Authorization",
    "No Public Classifier Authorization",
    "No Public Tool Authorization",
    "No Monetization Authorization",
    "No Public Release Authorization",
    "Public Surface Four-URL Integrity",
    "Static Safety Integrity",
    "Publisher Gate Alignment",
    "Reference Expansion Gate Alignment",
    "Evidence Ledger / Claim Map Alignment",
    "Source Registry Alignment",
    "Build Manifest Regeneration",
    "Python Cache Exclusion",
]
PROHIBITED = [
    "registering an actual candidate",
    "candidate entry creation",
    "candidate id creation",
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
    "javascript",
    "forms",
    "inputs",
    "upload",
    "scoring",
    "fake/real output",
    "generated output",
    "engine",
    "classifier",
    "detector",
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
FORBIDDEN_OVERALL = [
    "candidate_registered",
    "candidate_assessed",
    "candidate_selected",
    "candidate_approved",
    "candidate_created",
    "route_created",
    "route_approved",
    "sitemap_ready",
    "navigation_ready",
    "workbench_ready",
    "engine_ready",
    "classifier_ready",
    "deployment_ready",
    "dns_ready",
    "cloudflare_ready",
    "monetization_ready",
    "public_release_ready",
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
    "no_automatic_transition_to_candidate_registration",
    "registry_governance_validated_only_to_future_candidate_registration_governance",
    "candidate_recorded_requires_separate_future_candidate_registration_sprint",
    "candidate_record_requires_assessment_requires_separate_future_candidate_assessment_sprint",
    "candidate_assessment_validated_only_to_eligible_for_route_creation_sprint",
    "eligible_for_route_creation_sprint_requires_separate_future_route_creation_governance",
    "no_state_authorizes_sitemap_expansion",
    "no_state_authorizes_public_navigation",
    "no_state_authorizes_public_release",
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
    "PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION_V1.md",
    "data/public-route-candidate-registry-governance-validation-policy.json",
    "data/public-route-candidate-registry-governance-validation-results-v1.json",
    "data/public-route-candidate-registry-schema-validation-v1.json",
    "data/public-route-candidate-registry-entry-template-validation-v1.json",
    "data/public-route-candidate-registry-state-model-validation-v1.json",
    "data/public-route-candidate-registry-entry-requirements-validation-v1.json",
    "data/public-route-candidate-registry-non-authorization-validation-v1.json",
    "data/public-route-candidate-registry-public-isolation-audit-v1.json",
    "data/public-route-candidate-registry-static-safety-audit-v1.json",
    "validators/validate_public_route_candidate_registry_governance_validation.py",
]
INSTANTIATED_ENTRY_GLOBS = ["data/public-route-candidate-registry-entry-*.json"]
SKIP_ENTRY_SUFFIXES = (
    "template",
    "validation",
    "schema",
    "governance",
    "requirements",
    "non-authorization",
    "boundary-audit",
    "state-model",
)
NUMERIC = re.compile(r"\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b", re.I)


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
    text = (ROOT / "PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION_V1.md").read_text(encoding="utf-8")
    for phrase in [
        "Public route candidate registry governance must be validated before any candidate can be registered.",
        "Validating registry governance does not create a registry entry, register a candidate, assess a candidate, create a route, or authorize public release.",
        "governance validation layer that checks whether candidate registry governance correctly defines",
        "Sprint 48 candidate registry governance",
        "maturity: validation_only_candidate_registry_governance_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
    ]:
        if phrase not in text:
            error(f"doctrine: missing {phrase}")
            ok = False
    for dim in DIMENSIONS:
        if dim not in text:
            error(f"doctrine: missing dimension {dim}")
            ok = False
    return ok


def validate_policy() -> bool:
    ok = True
    d = load(POLICY)
    if d.get("status") != POLICY_STATUS:
        error("validation policy: invalid status")
        ok = False
    if d.get("maturity") != MATURE:
        error("validation policy: invalid maturity")
        ok = False
    if not has_all(
        d.get("allowed_validation_actions", []),
        [
            "candidate registry governance validation",
            "registry schema validation",
            "entry template validation",
            "registry state model validation",
            "entry requirements validation",
            "non-authorization validation",
            "public isolation validation",
            "static safety validation",
            "publisher gate validation",
            "reference gate validation",
            "python cache exclusion validation",
            "validation only",
        ],
    ):
        error("validation policy: missing allowed actions")
        ok = False
    if not has_all(d.get("prohibited_actions", []), PROHIBITED):
        error("validation policy: missing prohibited actions")
        ok = False
    correction = d.get("correction_policy", "").lower()
    for term in [
        "register a candidate",
        "create candidate entries",
        "create candidate ids",
        "instantiate candidate records",
        "assess candidates",
        "select candidate routes",
        "create routes",
        "approve routes",
        "add sitemap entries",
        "add public links",
        "expose the prototype",
        "modify prototype files",
        "add js",
        "add forms",
        "add inputs",
        "add upload",
        "add scoring",
        "add engine behavior",
        "add classifier behavior",
        "add api",
        "add analytics",
        "add deployment changes",
        "dns/cloudflare/custom domain",
        "add monetization",
        "authorize public release",
        "commit python cache files",
    ]:
        if term not in correction:
            error(f"validation policy: correction policy missing {term}")
            ok = False
    blocked = " ".join(d.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in [
        "candidate registration",
        "candidate entry creation",
        "candidate record instantiation",
        "candidate assessment",
        "public route creation",
        "route approval",
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
            error(f"validation policy: non-authorization missing {term}")
            ok = False
    if NUMERIC.search((ROOT / POLICY).read_text(encoding="utf-8")):
        error("validation policy: numeric score found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    data = load("data/public-route-candidate-registry-governance-validation-results-v1.json")
    names = [x.get("name") for x in data.get("validation_dimensions", [])]
    if names != DIMENSIONS:
        error("validation results: all 82 dimensions must exist in order")
        ok = False
    if any(x.get("result") != "pass" for x in data.get("validation_dimensions", [])):
        error("validation results: every dimension must pass")
        ok = False
    if data.get("overall_result") != "public_route_candidate_registry_governance_validated":
        error("validation results: invalid overall_result")
        ok = False
    overall = data.get("overall_result", "").lower()
    for term in FORBIDDEN_OVERALL:
        if term in overall:
            error(f"validation results: overall_result implies {term}")
            ok = False
    if data.get("python_cache_result") != "python_cache_excluded":
        error("validation results: python_cache_result must be python_cache_excluded")
        ok = False
    return ok


def validate_schema_validation() -> bool:
    ok = True
    sv = load("data/public-route-candidate-registry-schema-validation-v1.json")
    if sv.get("status") != "public_route_candidate_registry_schema_validated":
        error("schema validation: invalid status")
        ok = False
    if sv.get("maturity") != "schema_validation_only_no_candidate_registered":
        error("schema validation: invalid maturity")
        ok = False
    if sv.get("overall_result") != "registry_schema_validated":
        error("schema validation: invalid overall_result")
        ok = False
    for key in ENTRY_FIELDS:
        if sv.get("required_entry_field_results", {}).get(key) != "pass":
            error(f"schema validation: missing required field {key}")
            ok = False
    for key in FORBIDDEN_ENTRY_FIELDS:
        if sv.get("forbidden_entry_field_results", {}).get(key) != "pass":
            error(f"schema validation: missing forbidden field {key}")
            ok = False
    for key in BOUNDARY_FIELDS:
        if sv.get("required_boundary_field_results", {}).get(key) != "pass":
            error(f"schema validation: missing boundary field {key}")
            ok = False
    for key in NON_AUTH_FIELDS:
        if sv.get("required_non_authorization_field_results", {}).get(key) != "pass":
            error(f"schema validation: missing non-authorization field {key}")
            ok = False
    for key in [
        "no_candidate_entries_exist",
        "no_candidate_ids_created",
        "no_candidate_records_instantiated",
        "no_candidate_pages_created",
    ]:
        if sv.get("registry_zero_state_result", {}).get(key) != "pass":
            error(f"schema validation: missing registry zero state {key}")
            ok = False
    return ok


def validate_entry_template_validation() -> bool:
    ok = True
    t = load("data/public-route-candidate-registry-entry-template-validation-v1.json")
    if t.get("status") != "public_route_candidate_registry_entry_template_validated":
        error("entry template validation: invalid status")
        ok = False
    if t.get("maturity") != "template_validation_only_no_entry_instantiated":
        error("entry template validation: invalid maturity")
        ok = False
    if t.get("overall_result") != "registry_entry_template_validated":
        error("entry template validation: invalid overall_result")
        ok = False
    if t.get("template_zero_state_result") != "no_instantiated_entry_exists":
        error("entry template validation: invalid template_zero_state_result")
        ok = False
    for key in ENTRY_FIELDS:
        if t.get("template_field_results", {}).get(key) != "pass":
            error(f"entry template validation: missing template field {key}")
            ok = False
    for key in TEMPLATE_BOUNDARY_RULES:
        if t.get("template_boundary_rule_results", {}).get(key) != "pass":
            error(f"entry template validation: missing boundary rule {key}")
            ok = False
    for key in TEMPLATE_NON_AUTH:
        if t.get("template_non_authorization_rule_results", {}).get(key) != "pass":
            error(f"entry template validation: missing non-authorization rule {key}")
            ok = False
    return ok


def validate_state_model_validation() -> bool:
    ok = True
    sm = load("data/public-route-candidate-registry-state-model-validation-v1.json")
    if sm.get("status") != "public_route_candidate_registry_state_model_validated":
        error("state model validation: invalid status")
        ok = False
    if sm.get("maturity") != "state_model_validation_only_no_candidate_registered":
        error("state model validation: invalid maturity")
        ok = False
    if sm.get("overall_result") != "registry_state_model_validated":
        error("state model validation: invalid overall_result")
        ok = False
    if sm.get("non_authorization_result") != "state_model_does_not_register_candidates_or_create_routes":
        error("state model validation: invalid non_authorization_result")
        ok = False
    for key in REGISTRY_STATES:
        if sm.get("registry_state_results", {}).get(key) != "pass":
            error(f"state model validation: missing state {key}")
            ok = False
    for key in TRANSITION_RULES:
        if sm.get("transition_rule_results", {}).get(key) != "pass":
            error(f"state model validation: missing transition rule {key}")
            ok = False
    for key in FORBIDDEN_TRANSITIONS:
        if sm.get("forbidden_transition_results", {}).get(key) != "pass":
            error(f"state model validation: missing forbidden transition {key}")
            ok = False
    return ok


def validate_entry_requirements_validation() -> bool:
    ok = True
    er = load("data/public-route-candidate-registry-entry-requirements-validation-v1.json")
    if er.get("status") != "public_route_candidate_registry_entry_requirements_validated":
        error("entry requirements validation: invalid status")
        ok = False
    if er.get("maturity") != "requirements_validation_only_no_candidate_registered":
        error("entry requirements validation: invalid maturity")
        ok = False
    if er.get("overall_result") != "registry_entry_requirements_validated":
        error("entry requirements validation: invalid overall_result")
        ok = False
    if er.get("non_authorization_result") != "requirements_do_not_register_candidates":
        error("entry requirements validation: invalid non_authorization_result")
        ok = False
    if er.get("blocked_missing_field_policy_result") != "missing_any_required_field_blocks_candidate_registration":
        error("entry requirements validation: invalid blocked_missing_field_policy_result")
        ok = False
    for key in IDENTITY_FIELDS:
        if er.get("identity_field_results", {}).get(key) != "pass":
            error(f"entry requirements validation: missing identity field {key}")
            ok = False
    for key in BOUNDARY_REQ_FIELDS:
        if er.get("boundary_field_results", {}).get(key) != "pass":
            error(f"entry requirements validation: missing boundary field {key}")
            ok = False
    for key in RISK_FIELDS:
        if er.get("risk_field_results", {}).get(key) != "pass":
            error(f"entry requirements validation: missing risk field {key}")
            ok = False
    for key in STATUS_FIELDS:
        if er.get("status_field_results", {}).get(key) != "pass":
            error(f"entry requirements validation: missing status field {key}")
            ok = False
    return ok


def validate_non_authorization_validation() -> bool:
    ok = True
    na = load("data/public-route-candidate-registry-non-authorization-validation-v1.json")
    if na.get("status") != "public_route_candidate_registry_non_authorization_validated":
        error("non-authorization validation: invalid status")
        ok = False
    if na.get("maturity") != "non_authorization_validation_only_no_candidate_no_route_no_release":
        error("non-authorization validation: invalid maturity")
        ok = False
    if na.get("overall_result") != "registry_non_authorization_validated":
        error("non-authorization validation: invalid overall_result")
        ok = False
    for key in BLOCKED_AUTH:
        if na.get("blocked_authorization_results", {}).get(key) != "pass":
            error(f"non-authorization validation: missing {key}")
            ok = False
    expected = {
        "registry_boundary_result": "registry_governance_only_no_entries",
        "candidate_registration_boundary_result": "candidate_registration_requires_future_registration_sprint",
        "candidate_assessment_boundary_result": "candidate_assessment_requires_future_assessment_sprint",
        "route_creation_boundary_result": "route_creation_requires_future_route_creation_sprint",
        "public_release_boundary_result": "public_release_remains_blocked",
        "internal_prototype_boundary_result": "internal_prototype_remains_non_public_static_unlinked_unrouted_unindexed",
    }
    for key, value in expected.items():
        if na.get(key) != value:
            error(f"non-authorization validation: {key} must be {value}")
            ok = False
    return ok


def validate_isolation_audit() -> bool:
    ok = True
    a = load("data/public-route-candidate-registry-public-isolation-audit-v1.json")
    expected = {
        "route_registry_result": "no_new_public_routes",
        "sitemap_result": "sitemap_unchanged_four_urls",
        "homepage_link_result": "no_workbench_prototype_candidate_or_registry_link_from_homepage",
        "reference_page_link_result": "no_workbench_prototype_candidate_or_registry_link_from_reference_pages",
        "language_page_link_result": "no_workbench_prototype_candidate_or_registry_link_from_language_page",
        "public_navigation_result": "no_public_navigation_added",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "internal_prototype_result": "internal_prototype_not_exposed",
        "registry_result": "no_populated_registry_created",
        "candidate_result": "no_candidate_registered_or_assessed",
        "overall_outcome": "registry_public_isolation_validated",
    }
    for key, value in expected.items():
        if a.get(key) != value:
            error(f"isolation audit: {key} must be {value}")
            ok = False
    return ok


def validate_static_audit() -> bool:
    ok = True
    a = load("data/public-route-candidate-registry-static-safety-audit-v1.json")
    if a.get("overall_outcome") != "registry_static_safety_validated":
        error("static audit: invalid overall_outcome")
        ok = False
    groups = {
        "prototype_file_results": [
            "prototype_files_not_modified_in_sprint_49",
            "only_index_and_css_in_prototype_directory",
            "no_additional_prototype_files",
            "no_new_prototype_directories",
        ],
        "registry_results": [
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
        "public_surface_results": [
            "no_new_public_html_route",
            "no_new_sitemap_url",
            "no_new_public_navigation_link",
            "route_registry_not_expanded",
            "public_surface_four_urls_preserved",
        ],
        "capability_block_results": [
            "no_public_route",
            "no_public_workbench",
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
            "no_monetization",
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
            error(f"static audit missing {key}")
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
        error("prototype files modified in Sprint 49")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 49")
        ok = False
    for pattern in INSTANTIATED_ENTRY_GLOBS:
        for p in ROOT.glob(pattern):
            if skip_instantiated(p):
                continue
            error(f"instantiated registry entry exists: {p.name}")
            ok = False
    routes = load("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    if "evidence-posture-workbench" in json.dumps(routes).lower() or "internal_prototypes" in json.dumps(routes).lower():
        error("route-registry: prototype must not be registered")
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
            error(f"{rel}: must not link to prototype or blocked route")
            ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    pub = load("data/publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
        "blocked_until_public_reference_system_map_integrity_audit_validation",        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
        "blocked_until_public_reference_navigation_backbone_consolidation_validation",
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,

    ):
        error("publisher status must be blocked until public route candidate registration governance")
        ok = False
    gate = next(
        (
            g
            for g in load("data/publisher-quality-gates.json").get("gates", [])
            if g.get("name") == "Public Route Candidate Registry Governance Validation Gate"
        ),
        None,
    )
    if not gate:
        error("public route candidate registry governance validation gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_candidate_registration_governance",
            "required_before_any_candidate_registry_entry",
            "required_before_any_candidate_registration",
            "required_before_any_candidate_assessment",
            "required_before_any_public_route",
            "required_before_any_public_route_creation_sprint",
            "required_before_any_sitemap_expansion",
            "required_before_any_public_navigation",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"validation gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("validation gate must not be bypassable")
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
    if "public_route_candidate_registry_governance_validation" not in checks:
        error("reference gate missing public_route_candidate_registry_governance_validation")
        ok = False
    if "no_candidate_registry_entries_by_validation_alone" not in rules:
        error("reference gate must block registry entries by validation alone")
        ok = False
    if "no_candidate_registration_by_validation_alone" not in rules:
        error("reference gate must block candidate registration by validation alone")
        ok = False
    if "no_public_route_candidate_assessment_by_validation_alone" not in rules:
        error("reference gate must block candidate assessment by validation alone")
        ok = False
    if "no_public_route_creation_by_validation_alone" not in rules:
        error("reference gate must block route creation by validation alone")
        ok = False
    if "no_public_engine_eligibility_by_registry_governance_validation" not in rules:
        error("reference gate must block engine eligibility by registry governance validation")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0055" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0055 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0055" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0055 map missing")
        ok = False
    if "validate_public_route_candidate_registry_governance_validation.py" not in (
        ROOT / "validators" / "validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing sprint 49 validator")
        ok = False
    if "DEC-067" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-067 missing")
        ok = False
    audit = load("data/public-route-candidate-registry-boundary-audit-v1.json")
    if audit.get("overall_outcome") != "public_route_candidate_registry_governance_boundary_validated":
        error("Sprint 48 boundary audit must show governance validated")
        ok = False
    val = load("data/public-route-candidate-assessment-governance-validation-results-v1.json")
    if val.get("overall_result") != "public_route_candidate_assessment_governance_validated":
        error("Sprint 47 assessment validation must show governance validated")
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
        "data/public-route-candidate-registry-governance-validation-results-v1.json",
        "data/public-route-candidate-registry-schema-validation-v1.json",
        "data/public-route-candidate-registry-entry-template-validation-v1.json",
        "data/public-route-candidate-registry-state-model-validation-v1.json",
        "data/public-route-candidate-registry-entry-requirements-validation-v1.json",
        "data/public-route-candidate-registry-non-authorization-validation-v1.json",
        "data/public-route-candidate-registry-public-isolation-audit-v1.json",
        "data/public-route-candidate-registry-static-safety-audit-v1.json",
        "data/public-route-candidate-registry-governance-policy.json",
        "data/public-route-candidate-registry-schema-v1.json",
        "data/public-route-candidate-registry-entry-template-v1.json",
        "data/public-route-candidate-registry-state-model-v1.json",
        "data/public-route-candidate-registry-entry-requirements-v1.json",
        "data/public-route-candidate-registry-non-authorization-rules-v1.json",
        "data/public-route-candidate-registry-boundary-audit-v1.json",
        "data/public-route-candidate-assessment-governance-validation-results-v1.json",
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
        validate_results,
        validate_schema_validation,
        validate_entry_template_validation,
        validate_state_model_validation,
        validate_entry_requirements_validation,
        validate_non_authorization_validation,
        validate_isolation_audit,
        validate_static_audit,
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
