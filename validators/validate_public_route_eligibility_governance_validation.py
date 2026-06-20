#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Eligibility Governance Validation v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    validate_public_surface,
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "validation_only_route_eligibility_governance_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY_STATUS = "governed_public_route_eligibility_governance_validation_policy"
DIMENSIONS = [
    "Eligibility Governance Policy Integrity",
    "Eligibility Definition Integrity",
    "Eligibility Is Not Route Creation",
    "Eligibility Criteria Integrity",
    "Blocked Criteria Integrity",
    "Sitemap Eligibility Boundary Integrity",
    "Navigation Eligibility Boundary Integrity",
    "Public Workbench Boundary Integrity",
    "Internal Prototype Boundary Integrity",
    "Prerequisite Map Integrity",
    "Missing Prerequisite Policy Integrity",
    "Non-Authorization Rules Integrity",
    "Route Creation Boundary Integrity",
    "Public Release Boundary Integrity",
    "Candidate State Model Integrity",
    "State Transition Discipline",
    "Forbidden Transition Integrity",
    "Public-Readiness Boundary Dependency",
    "Visual Baseline Lock Dependency",
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
    "route_eligible",
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
SOURCE_LOCS = [
    "PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION_V1.md",
    "data/public-route-eligibility-governance-validation-policy.json",
    "data/public-route-eligibility-governance-validation-results-v1.json",
    "data/public-route-eligibility-criteria-validation-v1.json",
    "data/public-route-eligibility-prerequisite-validation-v1.json",
    "data/public-route-eligibility-non-authorization-validation-v1.json",
    "data/public-route-eligibility-state-model-validation-v1.json",
    "data/public-route-eligibility-public-isolation-audit-v1.json",
    "data/public-route-eligibility-static-safety-audit-v1.json",
    "validators/validate_public_route_eligibility_governance_validation.py",
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
    text = (ROOT / "PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION_V1.md").read_text(encoding="utf-8")
    for phrase in [
        "Public route eligibility governance must be validated before any route can become an eligibility candidate.",
        "Eligibility validation confirms governance discipline; it does not authorize route creation.",
        "Public route eligibility governance validation is a governance validation layer",
        "Sprint 44 public route eligibility governance",
        "maturity: validation_only_route_eligibility_governance_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
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
    d = load("data/public-route-eligibility-governance-validation-policy.json")
    if d.get("status") != POLICY_STATUS:
        error("validation policy: invalid status")
        ok = False
    if d.get("maturity") != MATURE:
        error("validation policy: invalid maturity")
        ok = False
    if not has_all(
        d.get("allowed_validation_actions", []),
        [
            "route eligibility governance validation",
            "criteria validation",
            "prerequisite validation",
            "non-authorization validation",
            "state model validation",
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
    if NUMERIC.search(
        (ROOT / "data/public-route-eligibility-governance-validation-policy.json").read_text(encoding="utf-8")
    ):
        error("validation policy: numeric score found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    data = load("data/public-route-eligibility-governance-validation-results-v1.json")
    names = [x.get("name") for x in data.get("validation_dimensions", [])]
    if names != DIMENSIONS:
        error("validation results: all 51 dimensions must exist in order")
        ok = False
    if any(x.get("result") != "pass" for x in data.get("validation_dimensions", [])):
        error("validation results: every dimension must pass")
        ok = False
    if data.get("overall_result") != "public_route_eligibility_governance_validated":
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


def validate_criteria_validation() -> bool:
    ok = True
    c = load("data/public-route-eligibility-criteria-validation-v1.json")
    if c.get("status") != "public_route_eligibility_criteria_validated":
        error("criteria validation: invalid status")
        ok = False
    if c.get("maturity") != "criteria_validation_only_no_route_creation":
        error("criteria validation: invalid maturity")
        ok = False
    if c.get("overall_result") != "eligibility_criteria_validated":
        error("criteria validation: invalid overall_result")
        ok = False
    required_criteria = [
        "route_public_purpose_defined",
        "route_non_purpose_defined",
        "route_type_classified",
        "route_claim_boundary_defined",
        "route_source_policy_alignment_defined",
        "route_structured_data_boundary_defined",
        "public_surface_risk_review_required",
        "non_operational_implication_review_required",
        "artifact_subject_separation_required",
        "evidence_posture_boundary_required",
        "anti_detector_language_required",
        "sitemap_eligibility_review_required",
        "navigation_eligibility_review_required",
        "route_readiness_validation_required",
        "deployment_governance_required_before_deployment",
        "DNS_Cloudflare_governance_required_before_custom_domain",
    ]
    cr = c.get("criteria_results", {})
    for key in required_criteria:
        if cr.get(key) != "pass":
            error(f"criteria validation: missing or failing {key}")
            ok = False
    blocked = [
        "route_implies_engine_blocked",
        "route_implies_classifier_blocked",
        "route_implies_upload_blocked",
        "route_implies_scoring_blocked",
        "route_implies_fake_real_verdict_blocked",
        "route_implies_API_blocked",
        "route_implies_analytics_blocked",
        "route_exposes_internal_prototype_blocked",
        "route_bypasses_sitemap_governance_blocked",
        "route_bypasses_navigation_governance_blocked",
        "route_bypasses_public_readiness_boundary_blocked",
        "route_bypasses_route_readiness_validation_blocked",
    ]
    br = c.get("blocked_criteria_results", {})
    for key in blocked:
        if br.get(key) != "pass":
            error(f"criteria validation: blocked criteria missing {key}")
            ok = False
    for field in [
        "sitemap_boundary_result",
        "navigation_boundary_result",
        "public_workbench_boundary_result",
        "internal_prototype_boundary_result",
    ]:
        if not c.get(field):
            error(f"criteria validation: missing {field}")
            ok = False
    return ok


def validate_prerequisite_validation() -> bool:
    ok = True
    p = load("data/public-route-eligibility-prerequisite-validation-v1.json")
    if p.get("status") != "public_route_eligibility_prerequisites_validated":
        error("prerequisite validation: invalid status")
        ok = False
    if p.get("overall_result") != "eligibility_prerequisites_validated":
        error("prerequisite validation: invalid overall_result")
        ok = False
    groups = [
        "baseline_governance_prerequisites",
        "public_readiness_prerequisites",
        "route_boundary_prerequisites",
        "content_quality_prerequisites",
        "source_claim_prerequisites",
        "technical_quality_prerequisites",
        "accessibility_prerequisites",
        "SEO_structured_data_prerequisites",
        "sitemap_prerequisites",
        "navigation_prerequisites",
        "deployment_prerequisites",
        "DNS_Cloudflare_prerequisites",
        "engine_classifier_upload_scoring_prerequisites",
    ]
    gr = p.get("prerequisite_group_results", {})
    for key in groups:
        if gr.get(key) != "pass":
            error(f"prerequisite validation: group missing {key}")
            ok = False
    statements = [
        "locked_visual_baseline_validated",
        "public_readiness_boundary_validated",
        "route_purpose_required",
        "route_non_purpose_required",
        "route_type_required",
        "claim_boundary_required",
        "source_policy_required_if_claims_exist",
        "route_readiness_validation_required",
        "sitemap_governance_required_before_sitemap_entry",
        "navigation_governance_required_before_public_link",
        "deployment_governance_required_before_deployment",
        "DNS_Cloudflare_governance_required_before_custom_domain",
        "separate_engine_governance_required_before_engine",
        "separate_classifier_governance_required_before_classifier",
        "separate_upload_governance_required_before_upload",
        "separate_scoring_governance_required_before_scoring",
    ]
    sr = p.get("prerequisite_statement_results", {})
    for key in statements:
        if sr.get(key) != "pass":
            error(f"prerequisite validation: statement missing {key}")
            ok = False
    if p.get("missing_prerequisite_policy_result") != "missing_any_required_prerequisite_blocks_route_eligibility":
        error("prerequisite validation: invalid missing policy")
        ok = False
    return ok


def validate_non_authorization_validation() -> bool:
    ok = True
    na = load("data/public-route-eligibility-non-authorization-validation-v1.json")
    if na.get("overall_result") != "eligibility_non_authorization_validated":
        error("non-authorization validation: invalid overall_result")
        ok = False
    blocked = [
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
    br = na.get("blocked_authorization_results", {})
    for key in blocked:
        if br.get(key) != "pass":
            error(f"non-authorization validation: missing {key}")
            ok = False
    expected = {
        "route_creation_boundary_result": "route_creation_requires_future_route_creation_sprint",
        "public_release_boundary_result": "public_release_remains_blocked",
        "internal_prototype_boundary_result": "internal_prototype_remains_non_public_static_unlinked_unrouted_unindexed",
    }
    for key, value in expected.items():
        if na.get(key) != value:
            error(f"non-authorization validation: {key} must be {value}")
            ok = False
    return ok


def validate_state_model_validation() -> bool:
    ok = True
    sm = load("data/public-route-eligibility-state-model-validation-v1.json")
    if sm.get("overall_result") != "eligibility_state_model_validated":
        error("state model validation: invalid overall_result")
        ok = False
    states = [
        "not_considered",
        "governance_required",
        "boundary_defined",
        "eligibility_candidate",
        "eligibility_under_review",
        "eligibility_validated",
        "eligible_for_route_creation_sprint",
        "blocked_for_public_surface_risk",
        "blocked_for_operational_implication",
        "blocked_for_source_gap",
        "blocked_for_sitemap_or_navigation_gap",
        "blocked_for_engine_classifier_upload_scoring_implication",
    ]
    sr = sm.get("state_results", {})
    for key in states:
        if sr.get(key) != "pass":
            error(f"state model validation: state missing {key}")
            ok = False
    transitions = [
        "no_automatic_transition_to_route_creation",
        "eligibility_validated_only_to_eligible_for_route_creation_sprint",
        "eligible_for_route_creation_sprint_requires_separate_future_route_creation_governance",
        "blocked_states_require_correction_and_validation_before_reconsideration",
    ]
    tr = sm.get("transition_rule_results", {})
    for key in transitions:
        if tr.get(key) != "pass":
            error(f"state model validation: transition missing {key}")
            ok = False
    forbidden = [
        "eligibility_validated_to_public_route_created_blocked",
        "eligibility_validated_to_sitemap_entry_created_blocked",
        "eligibility_validated_to_public_navigation_added_blocked",
        "eligibility_validated_to_engine_enabled_blocked",
        "eligibility_validated_to_classifier_enabled_blocked",
        "eligibility_validated_to_upload_enabled_blocked",
        "eligibility_validated_to_scoring_enabled_blocked",
        "eligibility_validated_to_deployment_blocked",
        "eligibility_validated_to_public_release_blocked",
    ]
    fr = sm.get("forbidden_transition_results", {})
    for key in forbidden:
        if fr.get(key) != "pass":
            error(f"state model validation: forbidden transition missing {key}")
            ok = False
    return ok


def validate_audits() -> bool:
    ok = True
    iso = load("data/public-route-eligibility-public-isolation-audit-v1.json")
    expected_iso = {
        "route_registry_result": "no_new_public_routes",
        "sitemap_result": "sitemap_unchanged_four_urls",
        "homepage_link_result": "no_workbench_or_prototype_link_from_homepage",
        "reference_page_link_result": "no_workbench_or_prototype_link_from_reference_pages",
        "language_page_link_result": "no_workbench_or_prototype_link_from_language_page",
        "public_navigation_result": "no_public_navigation_added",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "internal_prototype_result": "internal_prototype_not_exposed",
        "overall_outcome": "eligibility_public_isolation_validated",
    }
    for key, value in expected_iso.items():
        if iso.get(key) != value:
            error(f"isolation audit: {key} must be {value}")
            ok = False
    safety = load("data/public-route-eligibility-static-safety-audit-v1.json")
    if safety.get("overall_outcome") != "eligibility_static_safety_validated":
        error("static safety audit: invalid overall_outcome")
        ok = False
    for key, required in {
        "prototype_file_results": [
            "prototype_files_not_modified_in_sprint_45",
            "only_index_and_css_in_prototype_directory",
            "no_additional_prototype_files",
            "no_new_prototype_directories",
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
    }.items():
        if not set(required).issubset(set(safety.get(key, {}).keys())):
            error(f"static safety audit: missing {key}")
            ok = False
    return ok


def validate_files_public() -> bool:
    ok = True
    if not all((ROOT / x).is_file() for x in LOCKED_FILES):
        error("prototype files missing")
        return False
    if {x.name for x in PROTO_DIR.iterdir() if x.is_file()} != {"index.html", "prototype.css"}:
        error("prototype directory must contain only index.html and prototype.css")
        ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files modified in Sprint 45")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 45")
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
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench|/workbench/|/tool/|/classifier/", re.I)
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
    ):
        error("publisher status must be blocked until public route candidate assessment governance")
        ok = False
    gate = next(
        (
            g
            for g in load("data/publisher-quality-gates.json").get("gates", [])
            if g.get("name") == "Public Route Eligibility Governance Validation Gate"
        ),
        None,
    )
    if not gate:
        error("public route eligibility governance validation gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_candidate_assessment_governance",
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
    exp = load("data/reference-expansion-gate.json")
    checks = " ".join(exp.get("required_pre_release_checks", [])).lower()
    rules = " ".join(exp.get("release_eligibility_rules", [])).lower()
    if "public_route_eligibility_governance_validation" not in checks:
        error("reference gate missing public_route_eligibility_governance_validation")
        ok = False
    if "no_public_route_creation_by_eligibility_validation_alone" not in rules:
        error("reference gate must block route creation by eligibility validation alone")
        ok = False
    if "no_public_engine_eligibility_by_route_eligibility_validation" not in rules:
        error("reference gate must block engine eligibility by route eligibility validation")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0051" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0051 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0051" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0051 map missing")
        ok = False
    if "validate_public_route_eligibility_governance_validation.py" not in (
        ROOT / "validators" / "validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing sprint 45 validator")
        ok = False
    if "DEC-063" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-063 missing")
        ok = False
    audit = load("data/public-route-eligibility-boundary-audit-v1.json")
    if audit.get("overall_outcome") != "public_route_eligibility_governance_boundary_validated":
        error("Sprint 44 boundary audit must show governance validated")
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
        "data/public-route-eligibility-governance-validation-policy.json",
        "data/public-route-eligibility-governance-validation-results-v1.json",
        "data/public-route-eligibility-criteria-validation-v1.json",
        "data/public-route-eligibility-prerequisite-validation-v1.json",
        "data/public-route-eligibility-non-authorization-validation-v1.json",
        "data/public-route-eligibility-state-model-validation-v1.json",
        "data/public-route-eligibility-public-isolation-audit-v1.json",
        "data/public-route-eligibility-static-safety-audit-v1.json",
        "data/public-route-eligibility-governance-policy.json",
        "data/public-route-eligibility-criteria-v1.json",
        "data/public-route-eligibility-prerequisite-map-v1.json",
        "data/public-route-eligibility-non-authorization-rules-v1.json",
        "data/public-route-eligibility-candidate-state-model-v1.json",
        "data/public-route-eligibility-boundary-audit-v1.json",
        "data/non-public-static-workbench-public-readiness-boundary-validation-results-v1.json",
        "data/non-public-static-workbench-visual-system-baseline-lock-validation-results-v1.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
    ]
    for rel in parse:
        try:
            load(rel)
        except Exception as exc:
            error(f"{rel} parse failed: {exc}")
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
            error(f"{rel} missing")
            return 1
    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap parse failed: {exc}")
        return 1
    ok = all(
        fn()
        for fn in [
            validate_doctrine,
            validate_policy,
            validate_results,
            validate_criteria_validation,
            validate_prerequisite_validation,
            validate_non_authorization_validation,
            validate_state_model_validation,
            validate_audits,
            validate_files_public,
            validate_governance,
            validate_cache,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
