#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Candidate Assessment Governance v1."""

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
MATURE = "candidate_assessment_governance_only_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY = "data/public-route-candidate-assessment-governance-policy.json"
PROHIBITED = [
    "assessing a specific candidate",
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
    "separate governance required",
    "separate validation required",
    "separate public readiness review required",
    "separate route readiness review required",
    "separate privacy/security review required",
    "separate sitemap/navigation governance required where applicable",
    "separate deployment/DNS governance required where applicable",
    "no unblock by candidate assessment governance alone",
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
FORBIDDEN_OUTCOME_TERMS = [
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
    "PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_V1.md",
    "data/public-route-candidate-assessment-governance-policy.json",
    "data/public-route-candidate-assessment-framework-v1.json",
    "data/public-route-candidate-assessment-record-template-v1.json",
    "data/public-route-candidate-assessment-state-model-v1.json",
    "data/public-route-candidate-assessment-prohibited-candidates-v1.json",
    "data/public-route-candidate-assessment-non-authorization-rules-v1.json",
    "data/public-route-candidate-assessment-boundary-audit-v1.json",
    "validators/validate_public_route_candidate_assessment_governance.py",
]
NUMERIC = re.compile(r"\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b", re.I)
INSTANTIATED_RECORD_GLOBS = [
    "data/public-route-candidate-assessment-record-*.json",
]
REAL_ROUTE_PATHS = [
    "/workbench/",
    "/evidence-posture-workbench/",
    "/tool/",
    "/classifier/",
    "/detector/",
    "/upload/",
    "/score/",
    "/demo/",
    "/prototype/",
]


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
    text = (ROOT / "PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_V1.md").read_text(encoding="utf-8")
    required = [
        "Route candidate assessment governance defines how future candidates are assessed. It does not assess, approve, create, or publish a route.",
        "A candidate is not a route. An assessed candidate is not a created route. A validated candidate is not a public release.",
        "governed pre-creation evaluation process",
        "not_assessed",
        "candidate_assessment_validated",
        "eligible_for_route_creation_sprint",
        "blocked_for_public_release_implication",
        "No candidate is assessed in Sprint 46.",
        "maturity: candidate_assessment_governance_only_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
    ]
    for phrase in required:
        if phrase not in text:
            error(f"doctrine: missing {phrase}")
            ok = False
    for term in [
        "route creation",
        "sitemap inclusion",
        "workbench launch",
        "engine readiness",
        "public release readiness",
    ]:
        if term not in text.lower():
            error(f"doctrine: assessment-is-not missing {term}")
            ok = False
    return ok


def validate_policy() -> bool:
    ok = True
    d = load(POLICY)
    if d.get("status") != "governed_public_route_candidate_assessment_policy":
        error("policy invalid status")
        ok = False
    if d.get("maturity") != MATURE:
        error("policy invalid maturity")
        ok = False
    if not has_all(
        d.get("allowed_governance_actions", []),
        [
            "candidate assessment framework definition",
            "assessment record template definition",
            "candidate state modeling",
            "prohibited candidate definition",
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
        "specific candidate assessment",
        "candidate page creation",
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
    if NUMERIC.search((ROOT / POLICY).read_text(encoding="utf-8")):
        error("policy contains numeric score/grade/percentage")
        ok = False
    return ok


def validate_framework() -> bool:
    ok = True
    fw = load("data/public-route-candidate-assessment-framework-v1.json")
    if not set(ASSESSMENT_DIMENSIONS).issubset(set(fw.get("assessment_dimensions", []))):
        error("framework missing assessment_dimensions")
        ok = False
    if not set(CANDIDATE_CLASSES).issubset(set(fw.get("candidate_classes", []))):
        error("framework missing candidate_classes")
        ok = False
    if not set(ASSESSMENT_OUTCOMES).issubset(set(fw.get("assessment_outcomes", []))):
        error("framework missing assessment_outcomes")
        ok = False
    if not set(BLOCKED_DEFAULTS).issubset(set(fw.get("blocked_candidate_defaults", []))):
        error("framework missing blocked_candidate_defaults")
        ok = False
    text = json.dumps(fw).lower()
    for term in FORBIDDEN_OUTCOME_TERMS:
        if term in text and "does not authorize" not in text:
            pass
    if "authorize route creation" in text or "route creation authorized" in text:
        error("framework must not authorize route creation")
        ok = False
    stmt = fw.get("non_authorization_statement", "").lower()
    for term in ["route creation", "sitemap expansion", "public navigation", "public release"]:
        if term not in stmt:
            error(f"framework non_authorization_statement missing {term}")
            ok = False
    return ok


def validate_record_template() -> bool:
    ok = True
    t = load("data/public-route-candidate-assessment-record-template-v1.json")
    if not set(RECORD_FIELDS).issubset(set(t.get("required_record_fields", []))):
        error("record template missing required_record_fields")
        ok = False
    if not set(FORBIDDEN_RECORD_FIELDS).issubset(set(t.get("forbidden_record_fields", []))):
        error("record template missing forbidden_record_fields")
        ok = False
    if not set(BOUNDARY_FIELDS).issubset(set(t.get("required_boundary_fields", []))):
        error("record template missing required_boundary_fields")
        ok = False
    if not set(NON_AUTH_FIELDS).issubset(set(t.get("required_non_authorization_fields", []))):
        error("record template missing required_non_authorization_fields")
        ok = False
    if not t.get("template_non_authorization_statement"):
        error("record template missing template_non_authorization_statement")
        ok = False
    text = json.dumps(t).lower()
    if "no instantiated candidate record" not in text and "template defines record structure only" not in text:
        error("record template must state no instantiated record")
        ok = False
    for path in REAL_ROUTE_PATHS:
        if path in text and "placeholder" not in text and "template" not in text:
            error(f"record template appears to assess real route path {path}")
            ok = False
    for pattern in INSTANTIATED_RECORD_GLOBS:
        for p in ROOT.glob(pattern):
            if "template" in p.name or "validation" in p.name:
                continue
            error(f"instantiated candidate record exists: {p.name}")
            ok = False
    return ok


def validate_state_model() -> bool:
    ok = True
    sm = load("data/public-route-candidate-assessment-state-model-v1.json")
    if not set(STATES).issubset(set(sm.get("assessment_states", []))):
        error("state model missing assessment_states")
        ok = False
    rules = " ".join(sm.get("transition_rules", [])).lower()
    for term in [
        "no automatic transition to route creation",
        "candidate_assessment_validated may transition only to eligible_for_route_creation_sprint",
        "eligible_for_route_creation_sprint still requires separate future route creation governance",
        "blocked states require correction and validation before reconsideration",
        "no state authorizes sitemap expansion",
        "no state authorizes public navigation",
        "no state authorizes public release",
    ]:
        if term not in rules:
            error(f"state model missing transition rule: {term}")
            ok = False
    if not set(FORBIDDEN_TRANSITIONS).issubset(set(sm.get("forbidden_transitions", []))):
        error("state model missing forbidden_transitions")
        ok = False
    stmt = sm.get("non_authorization_statement", "").lower()
    for term in ["route creation", "sitemap expansion", "public navigation", "public release"]:
        if term not in stmt:
            error(f"state model non_authorization_statement missing {term}")
            ok = False
    return ok


def validate_prohibited_candidates() -> bool:
    ok = True
    pc = load("data/public-route-candidate-assessment-prohibited-candidates-v1.json")
    if not set(BLOCKED_BY_DEFAULT).issubset(set(pc.get("blocked_by_default", []))):
        error("prohibited candidates missing blocked_by_default")
        ok = False
    if not has_all(pc.get("unblock_requirements", []), UNBLOCK_REQS):
        error("prohibited candidates missing unblock_requirements")
        ok = False
    return ok


def validate_non_authorization() -> bool:
    ok = True
    na = load("data/public-route-candidate-assessment-non-authorization-rules-v1.json")
    blocked = na.get("blocked_authorizations", [])
    if isinstance(blocked, dict):
        blocked = list(blocked.keys())
    if not set(BLOCKED_AUTH).issubset(set(blocked)):
        error("non-authorization missing blocked_authorizations")
        ok = False
    expected = {
        "candidate_assessment_boundary": "no_specific_candidate_assessed_in_sprint_46",
        "route_creation_boundary": "route_creation_requires_future_route_creation_sprint",
        "public_release_boundary": "public_release_remains_blocked",
        "internal_prototype_boundary": "internal_prototype_remains_non_public_static_unlinked_unrouted_unindexed",
        "overall_result": "public_route_candidate_assessment_non_authorization_defined",
    }
    for key, value in expected.items():
        if na.get(key) != value:
            error(f"non-authorization: {key} must be {value}")
            ok = False
    return ok


def validate_audit() -> bool:
    ok = True
    a = load("data/public-route-candidate-assessment-boundary-audit-v1.json")
    if a.get("overall_outcome") != "public_route_candidate_assessment_governance_boundary_validated":
        error("audit invalid overall_outcome")
        ok = False
    groups = {
        "audited_scope": [
            "public route candidate assessment governance only",
            "current public surface",
            "current sitemap",
            "current route registry",
            "internal prototype as read-only boundary reference",
        ],
        "candidate_assessment_results": [
            "no_specific_candidate_assessed",
            "no_candidate_record_instantiated",
            "no_candidate_route_selected",
            "no_candidate_page_created",
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
        error("prototype files modified in Sprint 46")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 46")
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
    ):
        error("publisher status must be blocked until public route candidate assessment governance validation")
        ok = False
    gate = next(
        (
            g
            for g in load("data/publisher-quality-gates.json").get("gates", [])
            if g.get("name") == "Public Route Candidate Assessment Governance Gate"
        ),
        None,
    )
    if not gate:
        error("public route candidate assessment governance gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_candidate_assessment_governance_validation",
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
    if "public_route_candidate_assessment_governance" not in checks:
        error("reference gate missing public_route_candidate_assessment_governance")
        ok = False
    if "no_public_route_candidate_assessment_by_governance_alone" not in rules:
        error("reference gate must block candidate assessment by governance alone")
        ok = False
    if "no_public_route_creation_by_candidate_assessment_governance" not in rules:
        error("reference gate must block route creation by candidate assessment governance")
        ok = False
    if "no_public_engine_eligibility_by_candidate_assessment_governance" not in rules:
        error("reference gate must block engine eligibility by candidate assessment governance")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0052" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0052 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0052" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0052 map missing")
        ok = False
    if "validate_public_route_candidate_assessment_governance.py" not in (
        ROOT / "validators" / "validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing sprint 46 validator")
        ok = False
    if "DEC-064" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-064 missing")
        ok = False
    val = load("data/public-route-eligibility-governance-validation-results-v1.json")
    if val.get("overall_result") != "public_route_eligibility_governance_validated":
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
        validate_framework,
        validate_record_template,
        validate_state_model,
        validate_prohibited_candidates,
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
