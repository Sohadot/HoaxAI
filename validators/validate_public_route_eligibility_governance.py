#!/usr/bin/env python3
"""Validate Hoax.ai Public Route Eligibility Governance v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,

    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_GROUP_DEEPENING_VALIDATION,)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "eligibility_governance_only_no_route_no_sitemap_no_public_release_no_engine_no_classifier"
POLICY = "data/public-route-eligibility-governance-policy.json"
PROHIBITED = [
    "public route creation",
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
BLOCKED_AUTH = [
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
ELIGIBILITY_CRITERIA = [
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
BLOCKED_CRITERIA = [
    "route_implies_engine",
    "route_implies_classifier",
    "route_implies_upload",
    "route_implies_scoring",
    "route_implies_fake_real_verdict",
    "route_implies_API",
    "route_implies_analytics",
    "route_exposes_internal_prototype",
    "route_bypasses_sitemap_governance",
    "route_bypasses_navigation_governance",
    "route_bypasses_public_readiness_boundary",
    "route_bypasses_route_readiness_validation",
]
PREREQ_GROUPS = [
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
PREREQ_STATEMENTS = [
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
STATES = [
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
FORBIDDEN_TRANSITIONS = [
    "eligibility_validated_to_public_route_created",
    "eligibility_validated_to_sitemap_entry_created",
    "eligibility_validated_to_public_navigation_added",
    "eligibility_validated_to_engine_enabled",
    "eligibility_validated_to_classifier_enabled",
    "eligibility_validated_to_upload_enabled",
    "eligibility_validated_to_scoring_enabled",
    "eligibility_validated_to_deployment",
    "eligibility_validated_to_public_release",
]
SOURCE_LOCS = [
    "PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_V1.md",
    "data/public-route-eligibility-governance-policy.json",
    "data/public-route-eligibility-criteria-v1.json",
    "data/public-route-eligibility-prerequisite-map-v1.json",
    "data/public-route-eligibility-non-authorization-rules-v1.json",
    "data/public-route-eligibility-candidate-state-model-v1.json",
    "data/public-route-eligibility-boundary-audit-v1.json",
    "validators/validate_public_route_eligibility_governance.py",
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
    text = (ROOT / "PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_V1.md").read_text(encoding="utf-8")
    required = [
        "Public route eligibility governance defines the conditions for future consideration. It does not create public routes.",
        "A route can become eligible only after its boundary, purpose, risk, sitemap status, navigation status, and non-operational claims are governed.",
        "Public route eligibility is a pre-route governance state",
        "not_considered",
        "eligible_for_route_creation_sprint",
        "blocked_for_engine_classifier_upload_scoring_implication",
        "Sprint 44 does not add sitemap URLs",
        "Sprint 44 does not add navigation links",
        "maturity: eligibility_governance_only_no_route_no_sitemap_no_public_release_no_engine_no_classifier",
    ]
    for phrase in required:
        if phrase not in text:
            error(f"doctrine: missing {phrase}")
            ok = False
    for term in [
        "route creation",
        "sitemap inclusion",
        "public workbench launch",
        "engine readiness",
        "public release readiness",
    ]:
        if term not in text.lower():
            error(f"doctrine: eligibility-is-not missing {term}")
            ok = False
    return ok


def validate_policy() -> bool:
    ok = True
    d = load(POLICY)
    if d.get("status") != "governed_public_route_eligibility_policy":
        error("policy invalid status")
        ok = False
    if d.get("maturity") != MATURE:
        error("policy invalid maturity")
        ok = False
    if not has_all(
        d.get("allowed_governance_actions", []),
        [
            "eligibility criteria definition",
            "prerequisite mapping",
            "route state modeling",
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


def validate_criteria() -> bool:
    ok = True
    c = load("data/public-route-eligibility-criteria-v1.json")
    if not set(ELIGIBILITY_CRITERIA).issubset(set(c.get("eligibility_criteria", []))):
        error("criteria missing eligibility_criteria")
        ok = False
    if not set(BLOCKED_CRITERIA).issubset(set(c.get("blocked_criteria", []))):
        error("criteria missing blocked_criteria")
        ok = False
    for field in [
        "sitemap_eligibility_boundary",
        "navigation_eligibility_boundary",
        "public_workbench_boundary",
        "internal_prototype_boundary",
    ]:
        if not c.get(field):
            error(f"criteria missing {field}")
            ok = False
    text = json.dumps(c).lower()
    if "authorize route creation" in text or "route creation authorized" in text:
        error("criteria must not authorize route creation")
        ok = False
    return ok


def validate_prerequisite_map() -> bool:
    ok = True
    m = load("data/public-route-eligibility-prerequisite-map-v1.json")
    groups = m.get("prerequisite_groups", {})
    for g in PREREQ_GROUPS:
        if g not in groups:
            error(f"prerequisite map missing group {g}")
            ok = False
    flat = json.dumps(groups)
    for stmt in PREREQ_STATEMENTS:
        if stmt not in flat:
            error(f"prerequisite map missing {stmt}")
            ok = False
    if m.get("missing_prerequisite_policy") != "missing_any_required_prerequisite_blocks_route_eligibility":
        error("prerequisite map invalid missing_prerequisite_policy")
        ok = False
    if "authorize public route creation" in m.get("non_authorization_statement", "").lower():
        error("prerequisite map must not authorize route creation")
        ok = False
    return ok


def validate_non_authorization() -> bool:
    ok = True
    na = load("data/public-route-eligibility-non-authorization-rules-v1.json")
    if not set(BLOCKED_AUTH).issubset(set(na.get("blocked_authorizations", []))):
        error("non-authorization missing blocked_authorizations")
        ok = False
    expected = {
        "route_creation_boundary": "route_creation_requires_future_route_creation_sprint",
        "public_release_boundary": "public_release_remains_blocked",
        "internal_prototype_boundary": "internal_prototype_remains_non_public_static_unlinked_unrouted_unindexed",
        "overall_result": "public_route_eligibility_non_authorization_defined",
    }
    for key, value in expected.items():
        if na.get(key) != value:
            error(f"non-authorization: {key} must be {value}")
            ok = False
    return ok


def validate_state_model() -> bool:
    ok = True
    sm = load("data/public-route-eligibility-candidate-state-model-v1.json")
    if not set(STATES).issubset(set(sm.get("route_eligibility_states", []))):
        error("state model missing route_eligibility_states")
        ok = False
    rules = " ".join(sm.get("transition_rules", [])).lower()
    for term in [
        "no automatic transition to route creation",
        "eligibility_validated may transition only to eligible_for_route_creation_sprint",
        "eligible_for_route_creation_sprint still requires separate future route creation governance",
        "blocked states require correction and validation before reconsideration",
    ]:
        if term not in rules:
            error(f"state model missing transition rule: {term}")
            ok = False
    if not set(FORBIDDEN_TRANSITIONS).issubset(set(sm.get("forbidden_transitions", []))):
        error("state model missing forbidden_transitions")
        ok = False
    return ok


def validate_audit() -> bool:
    ok = True
    a = load("data/public-route-eligibility-boundary-audit-v1.json")
    if a.get("overall_outcome") != "public_route_eligibility_governance_boundary_validated":
        error("audit invalid overall_outcome")
        ok = False
    groups = {
        "audited_scope": [
            "public route eligibility governance only",
            "current public surface",
            "current sitemap",
            "current route registry",
            "internal prototype as read-only boundary reference",
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
        error("prototype files modified in Sprint 44")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged in Sprint 44")
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
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench|/workbench/|/tool/|/classifier/|/detector/|/upload/|/score/|/demo/|/prototype/", re.I)
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
        "blocked_until_public_reference_system_map_integrity_audit_validation",        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
        "blocked_until_public_reference_navigation_backbone_consolidation_validation",
        "blocked_until_public_reference_navigation_backbone_integrity_audit_validation",
        "blocked_until_public_reference_route_group_deepening_validation",
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,

    ):
        error("publisher status must be blocked until public route eligibility governance validation")
        ok = False
    gate = next(
        (g for g in load("data/publisher-quality-gates.json").get("gates", []) if g.get("name") == "Public Route Eligibility Governance Gate"),
        None,
    )
    if not gate:
        error("public route eligibility governance gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_eligibility_governance_validation",
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
    if "public_route_eligibility_governance" not in checks:
        error("reference gate missing public_route_eligibility_governance")
        ok = False
    if "no_public_route_eligibility_by_governance_alone" not in rules:
        error("reference gate must block route eligibility by governance alone")
        ok = False
    if "no_public_route_creation_by_governance_alone" not in rules:
        error("reference gate must block route creation by governance alone")
        ok = False
    if "no_public_engine_eligibility_by_route_eligibility_governance" not in rules:
        error("reference gate must block engine eligibility by route eligibility governance")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0050" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0050 missing")
        ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0050" for c in load("data/claim-source-map.json").get("claim_source_links", [])
    ):
        error("CLAIM-0050 map missing")
        ok = False
    if "validate_public_route_eligibility_governance.py" not in (ROOT / "validators" / "validate_all.py").read_text(
        encoding="utf-8"
    ):
        error("validate_all missing sprint 44 validator")
        ok = False
    if "DEC-062" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-062 missing")
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
        "data/public-route-eligibility-criteria-v1.json",
        "data/public-route-eligibility-prerequisite-map-v1.json",
        "data/public-route-eligibility-non-authorization-rules-v1.json",
        "data/public-route-eligibility-candidate-state-model-v1.json",
        "data/public-route-eligibility-boundary-audit-v1.json",
        "data/non-public-static-workbench-public-readiness-boundary-validation-results-v1.json",
        "data/non-public-static-workbench-public-readiness-prerequisite-validation-v1.json",
        "data/non-public-static-workbench-public-readiness-non-authorization-validation-v1.json",
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
            validate_criteria,
            validate_prerequisite_map,
            validate_non_authorization,
            validate_state_model,
            validate_audit,
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
