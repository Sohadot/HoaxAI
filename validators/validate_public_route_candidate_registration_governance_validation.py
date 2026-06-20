#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Candidate Registration Governance Validation v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    validate_public_surface,
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "validation_only_candidate_registration_governance_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY_STATUS = "governed_public_route_candidate_registration_governance_validation_policy"
POLICY = "data/public-route-candidate-registration-governance-validation-policy.json"
DIMENSIONS = [
    "Candidate Registration Governance Policy Integrity",
    "Candidate Registration Definition Integrity",
    "Registration Is Not Candidate Registration Execution",
    "Registration Is Not Candidate Assessment",
    "Registration Is Not Route Creation",
    "Registration Zero-State Integrity",
    "Registration Process Integrity",
    "Registration Step Integrity",
    "Blocked Step Integrity",
    "Prerequisite Result Integrity",
    "Registration Eligibility Gate Integrity",
    "Required-Before-Registration Integrity",
    "Blocked-Without-Gate Integrity",
    "Gate Non-Authorization Integrity",
    "Registration Record Template Integrity",
    "Required Registration Field Integrity",
    "Forbidden Registration Field Integrity",
    "Required Boundary Field Integrity",
    "Required Non-Authorization Field Integrity",
    "Template Zero-State Integrity",
    "Registration State Model Integrity",
    "Registration State Integrity",
    "Transition Rule Integrity",
    "Forbidden Transition Integrity",
    "Registration Non-Authorization Rules Integrity",
    "Registration Boundary Integrity",
    "Candidate Assessment Boundary Integrity",
    "Route Creation Boundary Integrity",
    "Public Release Boundary Integrity",
    "Internal Prototype Boundary Integrity",
    "Candidate Registry Governance Validation Dependency",
    "Candidate Assessment Governance Validation Dependency",
    "Route Eligibility Governance Validation Dependency",
    "Public-Readiness Boundary Dependency",
    "Visual Baseline Lock Dependency",
    "No Populated Registry Created",
    "No Candidate Entry Created",
    "No Candidate ID Created",
    "No Candidate Record Instantiated",
    "No Registration Record Instantiated",
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
    "candidate ID creation",
    "candidate record instantiation",
    "registration record instantiation",
    "candidate assessment",
    "candidate route selection",
    "candidate approval",
    "candidate page creation",
    "public route creation",
    "public route approval",
    "sitemap expansion",
    "public navigation link",
    "public workbench creation",
    "prototype modification",
    "prototype exposure",
    "JavaScript",
    "forms",
    "inputs",
    "upload",
    "scoring",
    "fake/real output",
    "generated output",
    "engine",
    "classifier",
    "detector",
    "API",
    "analytics",
    "storage",
    "network calls",
    "monetization",
    "DNS",
    "Cloudflare",
    "custom domain launch",
    "deployment changes",
    "public release authorization",
    "external factual claims",
    "subject accusation",
    "Python cache file commit",
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
REGISTRATION_FIELDS = [
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
FORBIDDEN_REGISTRATION_FIELDS = [
    "candidate_registered",
    "candidate_assessed",
    "candidate_approved",
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
    "no_route_creation_by_registration",
    "no_candidate_assessment_by_registration",
    "no_sitemap_expansion_by_registration",
    "no_public_navigation_by_registration",
    "no_public_workbench_by_registration",
    "no_engine_classifier_upload_scoring_by_registration",
    "no_public_release_by_registration",
]
NON_AUTH_FIELDS = [
    "registration_governance_does_not_register_candidate",
    "registration_does_not_authorize_assessment",
    "registration_does_not_authorize_route_creation",
    "registration_does_not_authorize_sitemap",
    "registration_does_not_authorize_navigation",
    "registration_does_not_authorize_engine",
    "registration_does_not_authorize_classifier",
    "registration_does_not_authorize_upload",
    "registration_does_not_authorize_scoring",
    "registration_does_not_authorize_API",
    "registration_does_not_authorize_analytics",
    "registration_does_not_authorize_deployment",
    "registration_does_not_authorize_DNS_Cloudflare",
    "registration_does_not_authorize_custom_domain_launch",
    "registration_does_not_authorize_public_release",
]
REGISTRATION_STEPS = [
    "confirm_registry_governance_validated",
    "confirm_registration_governance_validated",
    "confirm_approved_schema_available",
    "confirm_approved_template_available",
    "confirm_candidate_identity_fields_complete",
    "confirm_candidate_boundary_fields_complete",
    "confirm_candidate_risk_fields_complete",
    "confirm_candidate_status_fields_complete",
    "confirm_non_authorization_statement_present",
    "confirm_public_surface_risk_reviewed",
    "confirm_internal_prototype_exposure_risk_reviewed",
    "declare_sitemap_intention_without_execution",
    "declare_navigation_intention_without_execution",
    "declare_assessment_requirement_without_execution",
    "declare_required_next_gate",
    "run_candidate_registration_validator",
    "preserve_public_release_block",
]
BLOCKED_STEPS = [
    "create_public_route",
    "add_sitemap_entry",
    "add_public_navigation",
    "assess_candidate",
    "approve_candidate",
    "expose_internal_prototype",
    "enable_engine",
    "enable_classifier",
    "enable_upload",
    "enable_scoring",
    "enable_API",
    "enable_analytics",
    "deploy",
    "change_DNS_Cloudflare",
    "launch_custom_domain",
    "monetize",
    "authorize_public_release",
]
BLOCKED_STEP_KEYS = [f"{step}_blocked" for step in BLOCKED_STEPS]
PREREQ_RESULTS = [
    "public_route_candidate_registry_governance_validated",
    "registry_schema_validated",
    "registry_entry_template_validated",
    "registry_entry_requirements_validated",
    "registry_non_authorization_validated",
    "registry_public_isolation_validated",
    "registry_static_safety_validated",
]
REQUIRED_BEFORE = [
    "registry_governance_validation_passed",
    "registration_governance_validation_required",
    "candidate_identity_fields_required",
    "candidate_boundary_fields_required",
    "candidate_risk_fields_required",
    "candidate_status_fields_required",
    "non_authorization_statement_required",
    "public_surface_review_required",
    "prototype_exposure_review_required",
    "dedicated_registration_validator_required",
    "source_registry_update_required",
    "evidence_ledger_update_only_if_claim_added",
]
BLOCKED_WITHOUT_KEYS = [
    "candidate_entry_creation_blocked",
    "candidate_ID_creation_blocked",
    "candidate_record_instantiation_blocked",
    "candidate_assessment_blocked",
    "candidate_approval_blocked",
    "public_route_creation_blocked",
    "sitemap_expansion_blocked",
    "public_navigation_blocked",
    "public_release_blocked",
]
GATE_NON_AUTH = [
    "gate_does_not_register_candidate",
    "gate_does_not_assess_candidate",
    "gate_does_not_create_route",
    "gate_does_not_add_sitemap",
    "gate_does_not_add_navigation",
    "gate_does_not_authorize_public_release",
]
REGISTRATION_STATES = [
    "registration_governance_not_defined",
    "registration_governance_defined",
    "registration_governance_validated",
    "candidate_registration_not_allowed",
    "candidate_registration_requires_future_sprint",
    "candidate_registration_ready_for_future_recording",
    "candidate_registered",
    "registered_candidate_requires_assessment",
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
TRANSITION_RULE_KEYS = [
    "no_automatic_transition_to_candidate_registered",
    "registration_governance_validated_only_to_future_candidate_registration_sprint",
    "candidate_registration_ready_for_future_recording_requires_separate_future_registration_sprint",
    "candidate_registered_requires_dedicated_registration_validator_in_future_sprint",
    "registered_candidate_requires_assessment_requires_separate_future_assessment_sprint",
    "candidate_assessment_validated_only_to_eligible_for_route_creation_sprint",
    "eligible_for_route_creation_sprint_requires_separate_future_route_creation_governance",
    "no_state_authorizes_sitemap_expansion",
    "no_state_authorizes_public_navigation",
    "no_state_authorizes_public_release",
]
FORBIDDEN_TRANSITIONS = [
    "registration_governance_defined_to_candidate_registered",
    "registration_governance_validated_to_candidate_registered",
    "candidate_registration_ready_for_future_recording_to_candidate_registered",
    "candidate_registered_to_public_route_created",
    "candidate_registered_to_sitemap_entry_created",
    "candidate_registered_to_public_navigation_added",
    "candidate_registered_to_engine_enabled",
    "candidate_registered_to_classifier_enabled",
    "candidate_registered_to_upload_enabled",
    "candidate_registered_to_scoring_enabled",
    "candidate_registered_to_API_enabled",
    "candidate_registered_to_deployment",
    "candidate_registered_to_DNS_Cloudflare",
    "candidate_registered_to_public_release",
]
BLOCKED_AUTH = [
    "no_candidate_registered",
    "no_candidate_entry_created",
    "no_candidate_ID_created",
    "no_candidate_assessed",
    "no_candidate_approved",
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
    "PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION_V1.md",
    "data/public-route-candidate-registration-governance-validation-policy.json",
    "data/public-route-candidate-registration-governance-validation-results-v1.json",
    "data/public-route-candidate-registration-process-validation-v1.json",
    "data/public-route-candidate-registration-eligibility-gate-validation-v1.json",
    "data/public-route-candidate-registration-record-template-validation-v1.json",
    "data/public-route-candidate-registration-state-model-validation-v1.json",
    "data/public-route-candidate-registration-non-authorization-validation-v1.json",
    "data/public-route-candidate-registration-public-isolation-audit-v1.json",
    "data/public-route-candidate-registration-static-safety-audit-v1.json",
    "validators/validate_public_route_candidate_registration_governance_validation.py",
]
INSTANTIATED_RECORD_GLOBS = ["data/public-route-candidate-registration-record-*.json"]
SKIP_RECORD_SUFFIXES = (
    "template",
    "validation",
    "governance",
    "process",
    "eligibility",
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
    return any(part in name for part in SKIP_RECORD_SUFFIXES)


def validate_doctrine() -> bool:
    ok = True
    text = (ROOT / "PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION_V1.md").read_text(encoding="utf-8")
    for phrase in [
        "Public route candidate registration governance must be validated before any candidate registration sprint can be authorized.",
        "Validation of registration governance does not register a candidate, assess a candidate, create a route, or authorize public release.",
        "governance validation layer that checks whether candidate registration governance correctly defines",
        "Sprint 50 candidate registration governance",
        "maturity: validation_only_candidate_registration_governance_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
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
            "candidate registration governance validation",
            "registration process validation",
            "registration eligibility gate validation",
            "registration record template validation",
            "registration state model validation",
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
        "instantiate registration records",
        "assess candidates",
        "select candidate routes",
        "approve candidates",
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
        "candidate id creation",
        "candidate record instantiation",
        "registration record instantiation",
        "candidate assessment",
        "candidate approval",
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
    data = load("data/public-route-candidate-registration-governance-validation-results-v1.json")
    names = [x.get("name") for x in data.get("validation_dimensions", [])]
    if names != DIMENSIONS:
        error("validation results: all 77 dimensions must exist in order")
        ok = False
    if any(x.get("result") != "pass" for x in data.get("validation_dimensions", [])):
        error("validation results: every dimension must pass")
        ok = False
    if data.get("overall_result") != "public_route_candidate_registration_governance_validated":
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


def validate_process_validation() -> bool:
    ok = True
    pv = load("data/public-route-candidate-registration-process-validation-v1.json")
    if pv.get("status") != "public_route_candidate_registration_process_validated":
        error("process validation: invalid status")
        ok = False
    if pv.get("maturity") != "process_validation_only_no_candidate_registered":
        error("process validation: invalid maturity")
        ok = False
    if pv.get("overall_result") != "registration_process_validated":
        error("process validation: invalid overall_result")
        ok = False
    if pv.get("process_non_authorization_result") != "process_does_not_register_candidate":
        error("process validation: invalid process_non_authorization_result")
        ok = False
    for key in REGISTRATION_STEPS:
        if pv.get("registration_step_results", {}).get(key) != "pass":
            error(f"process validation: missing registration step {key}")
            ok = False
    for key in BLOCKED_STEP_KEYS:
        if pv.get("blocked_step_results", {}).get(key) != "pass":
            error(f"process validation: missing blocked step {key}")
            ok = False
    for key in PREREQ_RESULTS:
        if pv.get("prerequisite_result_validation", {}).get(key) != "pass":
            error(f"process validation: missing prerequisite {key}")
            ok = False
    return ok


def validate_eligibility_gate_validation() -> bool:
    ok = True
    gv = load("data/public-route-candidate-registration-eligibility-gate-validation-v1.json")
    if gv.get("status") != "public_route_candidate_registration_eligibility_gate_validated":
        error("eligibility gate validation: invalid status")
        ok = False
    if gv.get("maturity") != "gate_validation_only_no_candidate_registered":
        error("eligibility gate validation: invalid maturity")
        ok = False
    if gv.get("overall_result") != "registration_eligibility_gate_validated":
        error("eligibility gate validation: invalid overall_result")
        ok = False
    for key in REQUIRED_BEFORE:
        if gv.get("required_before_registration_results", {}).get(key) != "pass":
            error(f"eligibility gate validation: missing required_before {key}")
            ok = False
    for key in BLOCKED_WITHOUT_KEYS:
        if gv.get("blocked_without_gate_results", {}).get(key) != "pass":
            error(f"eligibility gate validation: missing blocked_without {key}")
            ok = False
    for key in GATE_NON_AUTH:
        if gv.get("gate_non_authorization_results", {}).get(key) != "pass":
            error(f"eligibility gate validation: missing gate_non_authorization {key}")
            ok = False
    return ok


def validate_record_template_validation() -> bool:
    ok = True
    t = load("data/public-route-candidate-registration-record-template-validation-v1.json")
    if t.get("status") != "public_route_candidate_registration_record_template_validated":
        error("record template validation: invalid status")
        ok = False
    if t.get("maturity") != "template_validation_only_no_registration_record_instantiated":
        error("record template validation: invalid maturity")
        ok = False
    if t.get("overall_result") != "registration_record_template_validated":
        error("record template validation: invalid overall_result")
        ok = False
    if t.get("template_zero_state_result") != "no_registration_record_instantiated":
        error("record template validation: invalid template_zero_state_result")
        ok = False
    for key in REGISTRATION_FIELDS:
        if t.get("required_registration_field_results", {}).get(key) != "pass":
            error(f"record template validation: missing required field {key}")
            ok = False
    for key in FORBIDDEN_REGISTRATION_FIELDS:
        if t.get("forbidden_registration_field_results", {}).get(key) != "pass":
            error(f"record template validation: missing forbidden field {key}")
            ok = False
    for key in BOUNDARY_FIELDS:
        if t.get("required_boundary_field_results", {}).get(key) != "pass":
            error(f"record template validation: missing boundary field {key}")
            ok = False
    for key in NON_AUTH_FIELDS:
        if t.get("required_non_authorization_field_results", {}).get(key) != "pass":
            error(f"record template validation: missing non-authorization field {key}")
            ok = False
    return ok


def validate_state_model_validation() -> bool:
    ok = True
    sm = load("data/public-route-candidate-registration-state-model-validation-v1.json")
    if sm.get("status") != "public_route_candidate_registration_state_model_validated":
        error("state model validation: invalid status")
        ok = False
    if sm.get("maturity") != "state_model_validation_only_no_candidate_registered":
        error("state model validation: invalid maturity")
        ok = False
    if sm.get("overall_result") != "registration_state_model_validated":
        error("state model validation: invalid overall_result")
        ok = False
    if sm.get("non_authorization_result") != "state_model_does_not_register_candidates_or_create_routes":
        error("state model validation: invalid non_authorization_result")
        ok = False
    for key in REGISTRATION_STATES:
        if sm.get("registration_state_results", {}).get(key) != "pass":
            error(f"state model validation: missing state {key}")
            ok = False
    for key in TRANSITION_RULE_KEYS:
        if sm.get("transition_rule_results", {}).get(key) != "pass":
            error(f"state model validation: missing transition rule {key}")
            ok = False
    for key in FORBIDDEN_TRANSITIONS:
        if sm.get("forbidden_transition_results", {}).get(key) != "pass":
            error(f"state model validation: missing forbidden transition {key}")
            ok = False
    return ok


def validate_non_authorization_validation() -> bool:
    ok = True
    na = load("data/public-route-candidate-registration-non-authorization-validation-v1.json")
    if na.get("status") != "public_route_candidate_registration_non_authorization_validated":
        error("non-authorization validation: invalid status")
        ok = False
    if na.get("maturity") != "non_authorization_validation_only_no_candidate_no_route_no_release":
        error("non-authorization validation: invalid maturity")
        ok = False
    if na.get("overall_result") != "registration_non_authorization_validated":
        error("non-authorization validation: invalid overall_result")
        ok = False
    for key in BLOCKED_AUTH:
        if na.get("blocked_authorization_results", {}).get(key) != "pass":
            error(f"non-authorization validation: missing {key}")
            ok = False
    expected = {
        "registration_boundary_result": "registration_governance_only_no_candidate_registered",
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
    a = load("data/public-route-candidate-registration-public-isolation-audit-v1.json")
    expected = {
        "route_registry_result": "no_new_public_routes",
        "sitemap_result": "sitemap_unchanged_four_urls",
        "homepage_link_result": "no_workbench_prototype_candidate_registry_or_registration_link_from_homepage",
        "reference_page_link_result": "no_workbench_prototype_candidate_registry_or_registration_link_from_reference_pages",
        "language_page_link_result": "no_workbench_prototype_candidate_registry_or_registration_link_from_language_page",
        "public_navigation_result": "no_public_navigation_added",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "internal_prototype_result": "internal_prototype_not_exposed",
        "registration_result": "no_candidate_registered",
        "candidate_result": "no_candidate_assessed_or_selected",
        "overall_outcome": "registration_public_isolation_validated",
    }
    for key, value in expected.items():
        if a.get(key) != value:
            error(f"isolation audit: {key} must be {value}")
            ok = False
    return ok


def validate_static_audit() -> bool:
    ok = True
    a = load("data/public-route-candidate-registration-static-safety-audit-v1.json")
    if a.get("overall_outcome") != "registration_static_safety_validated":
        error("static audit: invalid overall_outcome")
        ok = False
    groups = {
        "prototype_file_results": [
            "prototype_files_not_modified_in_sprint_51",
            "only_index_and_css_in_prototype_directory",
            "no_additional_prototype_files",
            "no_new_prototype_directories",
        ],
        "registration_results": [
            "no_candidate_registered",
            "no_candidate_entry_created",
            "no_candidate_ID_created",
            "no_candidate_record_instantiated",
            "no_registration_record_instantiated",
        ],
        "candidate_results": [
            "no_candidate_assessed",
            "no_candidate_selected",
            "no_candidate_approved",
            "no_candidate_page_created",
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
        error("prototype files modified in Sprint 51")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 51")
        ok = False
    for pattern in INSTANTIATED_RECORD_GLOBS:
        for p in ROOT.glob(pattern):
            if skip_instantiated(p):
                continue
            error(f"instantiated registration record exists: {p.name}")
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
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
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
        "blocked_until_internal_prototype_admissibility_regression_suite_validation",
    ):
        error("publisher status must be blocked until public route candidate registration authorization governance")
        ok = False
    gate = next(
        (
            g
            for g in load("data/publisher-quality-gates.json").get("gates", [])
            if g.get("name") == "Public Route Candidate Registration Governance Validation Gate"
        ),
        None,
    )
    if not gate:
        error("public route candidate registration governance validation gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_candidate_registration_authorization_governance",
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
    if "public_route_candidate_registration_governance_validation" not in checks:
        error("reference gate missing public_route_candidate_registration_governance_validation")
        ok = False
    if "no_candidate_registration_by_registration_governance_validation_alone" not in rules:
        error("reference gate must block candidate registration by validation alone")
        ok = False
    if "no_public_route_candidate_assessment_by_registration_governance_validation_alone" not in rules:
        error("reference gate must block candidate assessment by validation alone")
        ok = False
    if "no_public_route_creation_by_registration_governance_validation" not in rules:
        error("reference gate must block route creation by validation alone")
        ok = False
    if "no_public_engine_eligibility_by_registration_governance_validation" not in rules:
        error("reference gate must block engine eligibility by registration governance validation")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0057" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0057 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0057" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0057 map missing")
        ok = False
    if "validate_public_route_candidate_registration_governance_validation.py" not in (
        ROOT / "validators" / "validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing sprint 51 validator")
        ok = False
    if "DEC-069" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-069 missing")
        ok = False
    audit = load("data/public-route-candidate-registration-boundary-audit-v1.json")
    if audit.get("overall_outcome") != "public_route_candidate_registration_governance_boundary_validated":
        error("Sprint 50 boundary audit must show governance validated")
        ok = False
    val = load("data/public-route-candidate-registry-governance-validation-results-v1.json")
    if val.get("overall_result") != "public_route_candidate_registry_governance_validated":
        error("Sprint 49 registry governance validation must show governance validated")
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
        "data/public-route-candidate-registration-governance-validation-results-v1.json",
        "data/public-route-candidate-registration-process-validation-v1.json",
        "data/public-route-candidate-registration-eligibility-gate-validation-v1.json",
        "data/public-route-candidate-registration-record-template-validation-v1.json",
        "data/public-route-candidate-registration-state-model-validation-v1.json",
        "data/public-route-candidate-registration-non-authorization-validation-v1.json",
        "data/public-route-candidate-registration-public-isolation-audit-v1.json",
        "data/public-route-candidate-registration-static-safety-audit-v1.json",
        "data/public-route-candidate-registration-governance-policy.json",
        "data/public-route-candidate-registration-process-v1.json",
        "data/public-route-candidate-registration-eligibility-gate-v1.json",
        "data/public-route-candidate-registration-record-template-v1.json",
        "data/public-route-candidate-registration-state-model-v1.json",
        "data/public-route-candidate-registration-non-authorization-rules-v1.json",
        "data/public-route-candidate-registration-boundary-audit-v1.json",
        "data/public-route-candidate-registry-governance-validation-results-v1.json",
        "data/public-route-candidate-registry-schema-validation-v1.json",
        "data/public-route-candidate-registry-entry-template-validation-v1.json",
        "data/public-route-candidate-registry-entry-requirements-validation-v1.json",
        "data/public-route-candidate-registry-non-authorization-validation-v1.json",
        "data/public-route-candidate-registry-public-isolation-audit-v1.json",
        "data/public-route-candidate-registry-static-safety-audit-v1.json",
        "data/public-route-candidate-assessment-governance-validation-results-v1.json",
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
        validate_results,
        validate_process_validation,
        validate_eligibility_gate_validation,
        validate_record_template_validation,
        validate_state_model_validation,
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
