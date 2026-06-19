#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Candidate Assessment Governance Validation v1."""

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
    validate_public_surface,
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "validation_only_candidate_assessment_governance_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY_STATUS = "governed_public_route_candidate_assessment_governance_validation_policy"
POLICY = "data/public-route-candidate-assessment-governance-validation-policy.json"
DIMENSIONS = [
    "Candidate Assessment Governance Policy Integrity",
    "Candidate Assessment Definition Integrity",
    "Candidate Assessment Is Not Route Creation",
    "Candidate Assessment Is Not Candidate Approval",
    "Assessment Framework Integrity",
    "Assessment Dimension Integrity",
    "Candidate Class Integrity",
    "Assessment Outcome Integrity",
    "Blocked Candidate Default Integrity",
    "Record Template Integrity",
    "Required Record Field Integrity",
    "Forbidden Record Field Integrity",
    "Boundary Field Integrity",
    "Non-Authorization Field Integrity",
    "State Model Integrity",
    "Assessment State Integrity",
    "Transition Rule Integrity",
    "Forbidden Transition Integrity",
    "Prohibited Candidate Defaults Integrity",
    "Unblock Requirement Integrity",
    "Non-Authorization Rules Integrity",
    "Candidate Assessment Boundary Integrity",
    "Route Creation Boundary Integrity",
    "Public Release Boundary Integrity",
    "Internal Prototype Boundary Integrity",
    "Public Route Eligibility Dependency",
    "Public-Readiness Boundary Dependency",
    "Visual Baseline Lock Dependency",
    "No Specific Candidate Assessed",
    "No Candidate Record Instantiated",
    "No Candidate Route Selected",
    "No Candidate Page Created",
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
    "assessing a specific candidate",
    "candidate record instantiation",
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
ASSESSMENT_DIMENSIONS = [
    "proposed_route_path",
    "route_title",
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
]
CANDIDATE_CLASSES = [
    "Reference Route Candidate",
    "Governance Route Candidate",
    "Language Route Candidate",
    "Methodology Route Candidate",
    "Static Explanatory Route Candidate",
    "Public Workbench Route Candidate",
    "Diagnostic Route Candidate",
    "Tool Route Candidate",
    "Engine Route Candidate",
    "Upload Route Candidate",
    "API Route Candidate",
]
ASSESSMENT_OUTCOMES = [
    "not_assessed",
    "assessment_required",
    "candidate_assessment_ready",
    "candidate_under_assessment",
    "candidate_assessment_validated",
    "eligible_for_route_creation_sprint",
    "blocked_for_public_surface_risk",
    "blocked_for_operational_implication",
    "blocked_for_internal_prototype_exposure",
    "blocked_for_claim_or_source_gap",
    "blocked_for_sitemap_or_navigation_gap",
    "blocked_for_engine_classifier_upload_scoring_implication",
    "blocked_for_deployment_or_DNS_implication",
    "blocked_for_public_release_implication",
]
BLOCKED_DEFAULTS = [
    "public_workbench_candidate_blocked_by_default",
    "diagnostic_candidate_blocked_by_default",
    "tool_candidate_blocked_by_default",
    "engine_candidate_blocked_by_default",
    "classifier_candidate_blocked_by_default",
    "upload_candidate_blocked_by_default",
    "scoring_candidate_blocked_by_default",
    "API_candidate_blocked_by_default",
    "analytics_candidate_blocked_by_default",
    "monetization_candidate_blocked_by_default",
    "deployment_candidate_blocked_by_default",
    "DNS_custom_domain_candidate_blocked_by_default",
]
RECORD_FIELDS = [
    "candidate_id",
    "proposed_route_path",
    "proposed_route_title",
    "candidate_class",
    "public_purpose",
    "explicit_non_purpose",
    "route_type",
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
    "assessment_outcome",
    "required_next_gate",
]
FORBIDDEN_RECORD_FIELDS = [
    "route_created",
    "sitemap_entry_created",
    "public_navigation_added",
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
    "public_release_enabled",
]
BOUNDARY_FIELDS = [
    "no_route_creation_by_assessment",
    "no_sitemap_expansion_by_assessment",
    "no_public_navigation_by_assessment",
    "no_public_workbench_by_assessment",
    "no_engine_classifier_upload_scoring_by_assessment",
    "no_public_release_by_assessment",
]
NON_AUTH_FIELDS = [
    "assessment_does_not_authorize_route_creation",
    "assessment_does_not_authorize_sitemap",
    "assessment_does_not_authorize_navigation",
    "assessment_does_not_authorize_engine",
    "assessment_does_not_authorize_classifier",
    "assessment_does_not_authorize_upload",
    "assessment_does_not_authorize_scoring",
    "assessment_does_not_authorize_API",
    "assessment_does_not_authorize_analytics",
    "assessment_does_not_authorize_deployment",
    "assessment_does_not_authorize_DNS_Cloudflare",
    "assessment_does_not_authorize_custom_domain_launch",
    "assessment_does_not_authorize_public_release",
]
STATES = ASSESSMENT_OUTCOMES
TRANSITION_RULES = [
    "no_automatic_transition_to_route_creation",
    "candidate_assessment_validated_only_to_eligible_for_route_creation_sprint",
    "eligible_for_route_creation_sprint_requires_separate_future_route_creation_governance",
    "blocked_states_require_correction_and_validation_before_reconsideration",
    "no_state_authorizes_sitemap_expansion",
    "no_state_authorizes_public_navigation",
    "no_state_authorizes_public_release",
]
FORBIDDEN_TRANSITIONS = [
    "candidate_assessment_validated_to_public_route_created",
    "candidate_assessment_validated_to_sitemap_entry_created",
    "candidate_assessment_validated_to_public_navigation_added",
    "candidate_assessment_validated_to_engine_enabled",
    "candidate_assessment_validated_to_classifier_enabled",
    "candidate_assessment_validated_to_upload_enabled",
    "candidate_assessment_validated_to_scoring_enabled",
    "candidate_assessment_validated_to_API_enabled",
    "candidate_assessment_validated_to_deployment",
    "candidate_assessment_validated_to_DNS_Cloudflare",
    "candidate_assessment_validated_to_public_release",
]
BLOCKED_BY_DEFAULT = [
    "public_workbench_route_candidate",
    "diagnostic_route_candidate",
    "tool_route_candidate",
    "engine_route_candidate",
    "classifier_route_candidate",
    "upload_route_candidate",
    "scoring_route_candidate",
    "API_route_candidate",
    "analytics_route_candidate",
    "monetization_route_candidate",
    "deployment_route_candidate",
    "DNS_custom_domain_route_candidate",
]
UNBLOCK_REQS = [
    "separate_governance_required",
    "separate_validation_required",
    "separate_public_readiness_review_required",
    "separate_route_readiness_review_required",
    "separate_privacy_security_review_required",
    "sitemap_navigation_governance_required_where_applicable",
    "deployment_DNS_governance_required_where_applicable",
    "no_unblock_by_candidate_assessment_governance_alone",
]
BLOCKED_AUTH = [
    "no_candidate_assessed",
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
    "PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION_V1.md",
    "data/public-route-candidate-assessment-governance-validation-policy.json",
    "data/public-route-candidate-assessment-governance-validation-results-v1.json",
    "data/public-route-candidate-assessment-framework-validation-v1.json",
    "data/public-route-candidate-assessment-record-template-validation-v1.json",
    "data/public-route-candidate-assessment-state-model-validation-v1.json",
    "data/public-route-candidate-assessment-prohibited-candidates-validation-v1.json",
    "data/public-route-candidate-assessment-non-authorization-validation-v1.json",
    "data/public-route-candidate-assessment-public-isolation-audit-v1.json",
    "data/public-route-candidate-assessment-static-safety-audit-v1.json",
    "validators/validate_public_route_candidate_assessment_governance_validation.py",
]
NUMERIC = re.compile(r"\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b", re.I)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def has_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower() in text or item.lower().replace("_", " ") in text for item in required)


def validate_doctrine() -> bool:
    ok = True
    text = (ROOT / "PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION_V1.md").read_text(encoding="utf-8")
    for phrase in [
        "Public route candidate assessment governance must be validated before any specific candidate can be assessed.",
        "Validating assessment governance does not assess a candidate, approve a candidate, create a route, or authorize public release.",
        "governance validation layer that checks whether candidate assessment governance correctly defines",
        "Sprint 46 candidate assessment governance",
        "maturity: validation_only_candidate_assessment_governance_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
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
            "candidate assessment governance validation",
            "assessment framework validation",
            "record template validation",
            "state model validation",
            "prohibited candidate validation",
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
        "assess a candidate",
        "instantiate a candidate record",
        "select a candidate route",
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
        "candidate assessment",
        "candidate record instantiation",
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
    data = load("data/public-route-candidate-assessment-governance-validation-results-v1.json")
    names = [x.get("name") for x in data.get("validation_dimensions", [])]
    if names != DIMENSIONS:
        error("validation results: all 64 dimensions must exist in order")
        ok = False
    if any(x.get("result") != "pass" for x in data.get("validation_dimensions", [])):
        error("validation results: every dimension must pass")
        ok = False
    if data.get("overall_result") != "public_route_candidate_assessment_governance_validated":
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


def validate_framework_validation() -> bool:
    ok = True
    fw = load("data/public-route-candidate-assessment-framework-validation-v1.json")
    if fw.get("status") != "public_route_candidate_assessment_framework_validated":
        error("framework validation: invalid status")
        ok = False
    if fw.get("maturity") != "framework_validation_only_no_candidate_assessed":
        error("framework validation: invalid maturity")
        ok = False
    if fw.get("overall_result") != "assessment_framework_validated":
        error("framework validation: invalid overall_result")
        ok = False
    if fw.get("non_authorization_result") != "framework_does_not_assess_or_authorize_candidates":
        error("framework validation: invalid non_authorization_result")
        ok = False
    for key in ASSESSMENT_DIMENSIONS:
        if fw.get("assessment_dimension_results", {}).get(key) != "pass":
            error(f"framework validation: missing dimension {key}")
            ok = False
    for key in CANDIDATE_CLASSES:
        if fw.get("candidate_class_results", {}).get(key) != "pass":
            error(f"framework validation: missing class {key}")
            ok = False
    for key in ASSESSMENT_OUTCOMES:
        if fw.get("assessment_outcome_results", {}).get(key) != "pass":
            error(f"framework validation: missing outcome {key}")
            ok = False
    for key in BLOCKED_DEFAULTS:
        if fw.get("blocked_candidate_default_results", {}).get(key) != "pass":
            error(f"framework validation: missing blocked default {key}")
            ok = False
    return ok


def validate_record_template_validation() -> bool:
    ok = True
    t = load("data/public-route-candidate-assessment-record-template-validation-v1.json")
    if t.get("status") != "public_route_candidate_assessment_record_template_validated":
        error("record template validation: invalid status")
        ok = False
    if t.get("maturity") != "record_template_validation_only_no_record_instantiated":
        error("record template validation: invalid maturity")
        ok = False
    if t.get("overall_result") != "assessment_record_template_validated":
        error("record template validation: invalid overall_result")
        ok = False
    if t.get("template_non_authorization_result") != "template_does_not_authorize_route_creation":
        error("record template validation: invalid template_non_authorization_result")
        ok = False
    if t.get("instantiated_record_result") != "no_candidate_record_instantiated":
        error("record template validation: invalid instantiated_record_result")
        ok = False
    for key in RECORD_FIELDS:
        if t.get("required_record_field_results", {}).get(key) != "pass":
            error(f"record template validation: missing required field {key}")
            ok = False
    for key in FORBIDDEN_RECORD_FIELDS:
        if t.get("forbidden_record_field_results", {}).get(key) != "pass":
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
    sm = load("data/public-route-candidate-assessment-state-model-validation-v1.json")
    if sm.get("status") != "public_route_candidate_assessment_state_model_validated":
        error("state model validation: invalid status")
        ok = False
    if sm.get("maturity") != "state_model_validation_only_no_candidate_assessed_no_route_creation":
        error("state model validation: invalid maturity")
        ok = False
    if sm.get("overall_result") != "assessment_state_model_validated":
        error("state model validation: invalid overall_result")
        ok = False
    if sm.get("non_authorization_result") != "state_model_does_not_create_or_authorize_routes":
        error("state model validation: invalid non_authorization_result")
        ok = False
    for key in STATES:
        if sm.get("assessment_state_results", {}).get(key) != "pass":
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


def validate_prohibited_validation() -> bool:
    ok = True
    pc = load("data/public-route-candidate-assessment-prohibited-candidates-validation-v1.json")
    if pc.get("status") != "public_route_candidate_prohibited_defaults_validated":
        error("prohibited validation: invalid status")
        ok = False
    if pc.get("maturity") != "prohibited_candidate_validation_only_no_unblock":
        error("prohibited validation: invalid maturity")
        ok = False
    if pc.get("overall_result") != "prohibited_candidate_defaults_validated":
        error("prohibited validation: invalid overall_result")
        ok = False
    if pc.get("non_authorization_result") != "prohibited_candidate_validation_does_not_unblock_candidates":
        error("prohibited validation: invalid non_authorization_result")
        ok = False
    for key in BLOCKED_BY_DEFAULT:
        if pc.get("blocked_by_default_results", {}).get(key) != "pass":
            error(f"prohibited validation: missing blocked type {key}")
            ok = False
    for key in UNBLOCK_REQS:
        if pc.get("unblock_requirement_results", {}).get(key) != "pass":
            error(f"prohibited validation: missing unblock requirement {key}")
            ok = False
    return ok


def validate_non_authorization_validation() -> bool:
    ok = True
    na = load("data/public-route-candidate-assessment-non-authorization-validation-v1.json")
    if na.get("status") != "public_route_candidate_assessment_non_authorization_validated":
        error("non-authorization validation: invalid status")
        ok = False
    if na.get("maturity") != "non_authorization_validation_only_no_candidate_no_route_no_release":
        error("non-authorization validation: invalid maturity")
        ok = False
    if na.get("overall_result") != "candidate_assessment_non_authorization_validated":
        error("non-authorization validation: invalid overall_result")
        ok = False
    for key in BLOCKED_AUTH:
        if na.get("blocked_authorization_results", {}).get(key) != "pass":
            error(f"non-authorization validation: missing {key}")
            ok = False
    expected = {
        "candidate_assessment_boundary_result": "no_specific_candidate_assessed_in_sprint_47",
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
    a = load("data/public-route-candidate-assessment-public-isolation-audit-v1.json")
    expected = {
        "route_registry_result": "no_new_public_routes",
        "sitemap_result": "sitemap_unchanged_four_urls",
        "homepage_link_result": "no_workbench_prototype_or_candidate_link_from_homepage",
        "reference_page_link_result": "no_workbench_prototype_or_candidate_link_from_reference_pages",
        "language_page_link_result": "no_workbench_prototype_or_candidate_link_from_language_page",
        "public_navigation_result": "no_public_navigation_added",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "internal_prototype_result": "internal_prototype_not_exposed",
        "candidate_record_result": "no_candidate_record_instantiated",
        "overall_outcome": "candidate_assessment_public_isolation_validated",
    }
    for key, value in expected.items():
        if a.get(key) != value:
            error(f"isolation audit: {key} must be {value}")
            ok = False
    return ok


def validate_static_audit() -> bool:
    ok = True
    a = load("data/public-route-candidate-assessment-static-safety-audit-v1.json")
    if a.get("overall_outcome") != "candidate_assessment_static_safety_validated":
        error("static audit: invalid overall_outcome")
        ok = False
    groups = {
        "prototype_file_results": [
            "prototype_files_not_modified_in_sprint_47",
            "only_index_and_css_in_prototype_directory",
            "no_additional_prototype_files",
            "no_new_prototype_directories",
        ],
        "candidate_record_results": [
            "no_candidate_record_instantiated",
            "no_candidate_page_created",
            "no_specific_route_assessed",
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
        error("prototype files modified in Sprint 47")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 47")
        ok = False
    for p in ROOT.glob("data/public-route-candidate-assessment-record-*.json"):
        if p.name in {
            "public-route-candidate-assessment-record-template-v1.json",
            "public-route-candidate-assessment-record-template-validation-v1.json",
        } or "template" in p.name or "validation" in p.name:
            continue
        error(f"instantiated candidate record exists: {p.name}")
        ok = False
    routes = load("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    if "evidence-posture-workbench" in json.dumps(routes).lower() or "internal_prototypes" in json.dumps(routes).lower():
        error("route-registry: prototype must not be registered")
        ok = False
    locs = [e.text.strip().lower() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != 4 or any("evidence-posture-workbench" in x or "internal_prototypes" in x for x in locs):
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
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    ):
        error("publisher status must be blocked until public route candidate registry governance")
        ok = False
    gate = next(
        (
            g
            for g in load("data/publisher-quality-gates.json").get("gates", [])
            if g.get("name") == "Public Route Candidate Assessment Governance Validation Gate"
        ),
        None,
    )
    if not gate:
        error("public route candidate assessment governance validation gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_candidate_registry_governance",
            "required_before_any_candidate_registry_entry",
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
            "candidate assessment",
            "public release",
        ]:
            if term not in notes:
                error(f"gate notes missing {term}")
                ok = False
    exp = load("data/reference-expansion-gate.json")
    checks = " ".join(exp.get("required_pre_release_checks", [])).lower()
    rules = " ".join(exp.get("release_eligibility_rules", [])).lower()
    if "public_route_candidate_assessment_governance_validation" not in checks:
        error("reference gate missing public_route_candidate_assessment_governance_validation")
        ok = False
    if "no_public_route_candidate_registry_entries_by_validation_alone" not in rules:
        error("reference gate must block registry entries by validation alone")
        ok = False
    if "no_public_route_candidate_assessment_by_validation_alone" not in rules:
        error("reference gate must block candidate assessment by validation alone")
        ok = False
    if "no_public_route_creation_by_validation_alone" not in rules:
        error("reference gate must block route creation by validation alone")
        ok = False
    if "no_public_engine_eligibility_by_candidate_assessment_governance_validation" not in rules:
        error("reference gate must block engine eligibility by validation")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0053" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0053 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0053" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0053 map missing")
        ok = False
    if "validate_public_route_candidate_assessment_governance_validation.py" not in (
        ROOT / "validators" / "validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing sprint 47 validator")
        ok = False
    if "DEC-065" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-065 missing")
        ok = False
    audit = load("data/public-route-candidate-assessment-boundary-audit-v1.json")
    if audit.get("overall_outcome") != "public_route_candidate_assessment_governance_boundary_validated":
        error("Sprint 46 boundary audit must show governance validated")
        ok = False
    elig = load("data/public-route-eligibility-governance-validation-results-v1.json")
    if elig.get("overall_result") != "public_route_eligibility_governance_validated":
        error("Sprint 45 eligibility validation must show governance validated")
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
        "data/public-route-candidate-assessment-governance-validation-results-v1.json",
        "data/public-route-candidate-assessment-framework-validation-v1.json",
        "data/public-route-candidate-assessment-record-template-validation-v1.json",
        "data/public-route-candidate-assessment-state-model-validation-v1.json",
        "data/public-route-candidate-assessment-prohibited-candidates-validation-v1.json",
        "data/public-route-candidate-assessment-non-authorization-validation-v1.json",
        "data/public-route-candidate-assessment-public-isolation-audit-v1.json",
        "data/public-route-candidate-assessment-static-safety-audit-v1.json",
        "data/public-route-candidate-assessment-governance-policy.json",
        "data/public-route-candidate-assessment-framework-v1.json",
        "data/public-route-candidate-assessment-record-template-v1.json",
        "data/public-route-candidate-assessment-state-model-v1.json",
        "data/public-route-candidate-assessment-prohibited-candidates-v1.json",
        "data/public-route-candidate-assessment-non-authorization-rules-v1.json",
        "data/public-route-candidate-assessment-boundary-audit-v1.json",
        "data/public-route-eligibility-governance-validation-results-v1.json",
        "data/public-route-eligibility-criteria-validation-v1.json",
        "data/public-route-eligibility-prerequisite-validation-v1.json",
        "data/public-route-eligibility-non-authorization-validation-v1.json",
        "data/public-route-eligibility-state-model-validation-v1.json",
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
        validate_framework_validation,
        validate_record_template_validation,
        validate_state_model_validation,
        validate_prohibited_validation,
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
