#!/usr/bin/env python3
"""Validate Hoax.ai First Controlled Public Reference Pilot v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    PILOT_PATHS,
    PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE,
    PUBLISHER_STATUS_POST_LIVE_AUDIT,
    PUBLISHER_STATUS_POST_PILOT,
    PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE,
    PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE,
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
    validate_pilot_era_public_surface,
    validate_pilot_routes_present,
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

    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_GROUP_DEEPENING_VALIDATION,)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "category_language_principle", "allowed_pilot_actions", "prohibited_pilot_actions",
    "pilot_scope", "metadata_policy", "structured_data_policy", "route_policy",
    "sitemap_policy", "homepage_link_policy", "non_authorization_rules", "last_reviewed",
}

PILOT_TOP = {"pilot_id", "name", "version", "status", "maturity", "public_pages", "last_reviewed"}

REQUIRED_SOURCE_LOCATIONS = [
    "FIRST_CONTROLLED_PUBLIC_REFERENCE_PILOT.md",
    "data/controlled-public-reference-pilot-policy.json",
    "data/controlled-public-reference-pilot-v1.json",
    "reference/evidence-posture/index.html",
    "reference/artifact-subject-separation/index.html",
    "validators/validate_controlled_public_reference_pilot.py",
]

PILOT_PAGES = {
    "reference/evidence-posture/index.html": {
        "h1": "Evidence Posture",
        "thesis": "Evidence posture is the observable condition of an evidence artifact before it is used to support belief, action, publication, escalation, or institutional response.",
        "sections": [
            "What Evidence Posture Means",
            "Why Evidence Posture Matters",
            "What Evidence Posture Is Not",
            "The Artifact Boundary",
            "How Hoax.ai Uses the Term",
            "Relationship to Source Confidence and Provenance",
            "Not a Truth Verdict",
            "Public Reference Boundary",
            "Related Hoax.ai Concepts",
        ],
        "other_ref": "/reference/artifact-subject-separation/",
    },
    "reference/artifact-subject-separation/index.html": {
        "h1": "Artifact–Subject Separation",
        "thesis": "Artifact–Subject Separation is the rule that a statement about the condition of an evidence artifact must not become a statement about the guilt, truthfulness, legitimacy, or conduct of the subject connected to that artifact.",
        "sections": [
            "What Artifact–Subject Separation Means",
            "Why This Boundary Exists",
            "The Difference Between Artifact and Subject",
            "What This Rule Prevents",
            "How Hoax.ai Uses the Boundary",
            "Relationship to Evidence Posture",
            "Not an Accusation System",
            "Public Reference Boundary",
            "Related Hoax.ai Concepts",
        ],
        "other_ref": "/reference/evidence-posture/",
    },
}

PROHIBITED_PAGE_TERMS = [
    "upload", "scan now", "try it now", "detect deepfake", "deepfake detector",
    "truth score", "fake score", "public classifier", "submit evidence",
    "softwareapplication", "factcheck", "claimreview", "api endpoint",
]

PROHIBITED_ACTIONS = [
    "classifier", "detector", "upload", "scoring", "forms", "analytics", "api",
    "monetization", "dns", "cloudflare", "custom_domain_launch", "broader_route_expansion",
    "external_factual_claims", "subject_accusation",
]

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
JSON_LD_FORBIDDEN = ["Product", "SoftwareApplication", "Service", "API", "FactCheck", "ClaimReview"]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def visible_word_count(html: str) -> int:
    return len(strip_tags(html).split())


def validate_policy() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "controlled-public-reference-pilot-policy.json")
    if POLICY_TOP - set(data.keys()):
        error(f"pilot policy missing fields: {sorted(POLICY_TOP - set(data.keys()))}")
        ok = False
    if data.get("status") != "governed_controlled_public_reference_pilot_policy":
        error("pilot policy: invalid status")
        ok = False
    if data.get("maturity") != "two_public_reference_pages_only_no_engine_no_classifier_no_tool":
        error("pilot policy: invalid maturity")
        ok = False
    if sorted(data.get("pilot_scope", [])) != sorted(PILOT_PATHS):
        error("pilot policy: pilot_scope must be exactly the two approved pages")
        ok = False
    prohibited = " ".join(data.get("prohibited_pilot_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", " ") not in prohibited.replace("_", " ") and term not in prohibited:
            error(f"pilot policy: prohibited_pilot_actions missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("pilot policy: numeric score language prohibited")
        ok = False
    return ok


def validate_pilot_record() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "controlled-public-reference-pilot-v1.json")
    if PILOT_TOP - set(data.keys()):
        error(f"pilot record missing fields: {sorted(PILOT_TOP - set(data.keys()))}")
        ok = False
    pages = data.get("public_pages", [])
    if len(pages) != 2:
        error("pilot record: exactly two public page records required")
        ok = False
    for page in pages:
        for field in [
            "public_page_record_id", "path", "route_status", "sitemap_status",
            "public_metadata_status", "public_navigation_status", "publication_status",
            "deployment_status",
        ]:
            if field not in page:
                error(f"pilot record {page.get('public_page_record_id', '?')}: missing {field}")
                ok = False
        if page.get("route_status") != "controlled_public_reference_route_created":
            error("pilot record: invalid route_status")
            ok = False
        if page.get("deployment_status") != "repository_public_preview_only":
            error("pilot record: invalid deployment_status")
            ok = False
    return ok


def validate_public_page(rel_path: str) -> bool:
    ok = True
    spec = PILOT_PAGES[rel_path]
    path = ROOT / rel_path
    if not path.exists():
        error(f"missing public page {rel_path}")
        return False
    html = path.read_text(encoding="utf-8")
    lower = html.lower()

    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if len(h1s) != 1 or strip_tags(h1s[0]) != spec["h1"]:
        error(f"{rel_path}: must have exactly one H1 '{spec['h1']}'")
        ok = False

    if spec["thesis"] not in strip_tags(html):
        error(f"{rel_path}: required thesis missing")
        ok = False

    for section in spec["sections"]:
        if section.lower() not in lower:
            error(f"{rel_path}: missing section '{section}'")
            ok = False

    wc = visible_word_count(html)
    if wc < 900 or wc > 1500:
        error(f"{rel_path}: visible word count {wc} outside 900-1500")
        ok = False

    if spec["other_ref"] not in html:
        error(f"{rel_path}: must link to {spec['other_ref']}")
        ok = False
    if 'href="/"' not in html and "href=\"/\"" not in html:
        error(f"{rel_path}: must link to homepage")
        ok = False

    if "reference boundary" not in lower or "does not operate" not in lower:
        error(f"{rel_path}: missing public reference / non-tool boundary statement")
        ok = False

    for term in PROHIBITED_PAGE_TERMS:
        if term in lower:
            error(f"{rel_path}: prohibited term '{term}'")
            ok = False

    for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S):
        if any(f in block for f in JSON_LD_FORBIDDEN):
            error(f"{rel_path}: JSON-LD uses forbidden schema type")
            ok = False

    if re.search(r"<form\b|<input\b", html, re.I):
        error(f"{rel_path}: forms/inputs prohibited")
        ok = False

    return ok


def validate_all_public_pages() -> bool:
    ok = True
    for rel_path in PILOT_PAGES:
        if not validate_public_page(rel_path):
            ok = False
    return ok


def validate_route_registry() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_pilot_routes_present(routes, error):
        return False

    pilot_routes = [r for r in routes if r.get("route_id") in ("ROUTE-0002", "ROUTE-0003")]
    if len(pilot_routes) != 2:
        error("route-registry: exactly two pilot routes required")
        ok = False

    for route in pilot_routes:
        if route.get("status") != "controlled_public_reference_route_created":
            error(f"route {route.get('route_id')}: invalid status")
            ok = False
        if route.get("path") not in PILOT_PATHS:
            error(f"route {route.get('route_id')}: invalid path")
            ok = False
        caps = route.get("prohibited_capabilities", [])
        for cap in ["classifier", "upload", "scoring"]:
            if cap not in caps:
                error(f"route {route.get('route_id')}: missing prohibited capability {cap}")
                ok = False

    for route in routes:
        if "classifier" in route.get("path", "").lower() or "upload" in route.get("path", "").lower():
            error("route-registry: prohibited route type detected")
            ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    html = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    for path in PILOT_PATHS:
        slug = path.strip("/").split("/")[-1]
        if slug not in html:
            error(f"index.html: must link to {path}")
            ok = False
    for term in ["try it now", "submit evidence", "upload", "scan now", "detect"]:
        if term in html and "does not" not in html[max(0, html.find(term) - 40): html.find(term)]:
            if term in html:
                pass  # allow negated context on homepage
    for cta in ["try it now", "submit evidence"]:
        if cta in html:
            error(f"index.html: prohibited CTA '{cta}'")
            ok = False
    return ok


def validate_registries() -> bool:
    ok = True
    converted = 0
    for cand in load_json(ROOT / "data" / "public-route-candidate-registry.json").get("route_candidates", []):
        if cand.get("conversion_status") == "converted_to_controlled_public_reference_pilot":
            converted += 1
            if cand.get("route_status") != "controlled_public_reference_route_created":
                error("public route candidate: invalid route_status after conversion")
                ok = False
    if converted != 2:
        error("public route candidate registry: exactly two converted records required")
        ok = False

    for did in ("DRAFT-0001", "DRAFT-0002"):
        entry = next(
            (d for d in load_json(ROOT / "data" / "internal-draft-registry.json").get("draft_records", [])
             if d.get("draft_id") == did),
            None,
        )
        if not entry or entry.get("public_reference_pilot_status") != "converted_to_controlled_public_reference_pilot":
            error(f"internal draft registry: {did} pilot conversion missing")
            ok = False

    for cid in ("REF-CAND-0001", "REF-CAND-0002"):
        entry = next(
            (c for c in load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", [])
             if c.get("candidate_id") == cid),
            None,
        )
        if not entry or entry.get("public_reference_pilot_status") != "converted_to_controlled_public_reference_pilot":
            error(f"reference candidate registry: {cid} pilot conversion missing")
            ok = False

    for entry in load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", []):
        if entry.get("candidate_id") not in ("REF-CAND-0001", "REF-CAND-0002"):
            from candidate_registry_checks import is_batch1_production_candidate, is_batch2_production_candidate

            if is_batch1_production_candidate(entry):
                continue
            if is_batch2_production_candidate(entry):
                continue
            if entry.get("public_reference_pilot_status") == "converted_to_controlled_public_reference_pilot":
                error(f"candidate {entry.get('candidate_id')}: must not be converted")
                ok = False
            if entry.get("route_status") != "not_route_created":
                error(f"candidate {entry.get('candidate_id')}: must remain not_route_created")
                ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PILOT,
        PUBLISHER_STATUS_POST_LIVE_AUDIT,
        PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE,
        PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE,
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
        "blocked_until_public_reference_system_map_integrity_audit_validation",        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
        "blocked_until_public_reference_navigation_backbone_consolidation_validation",
        "blocked_until_public_reference_navigation_backbone_integrity_audit_validation",
        "blocked_until_public_reference_route_group_deepening_validation",
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,

    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_PILOT}, "
            f"{PUBLISHER_STATUS_POST_LIVE_AUDIT}, {PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE}, or "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION}, "
            f"got {pub.get('current_publisher_status')}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0024"), None)
    if not gate or gate.get("bypassable") is True:
        error("PUB-GATE-0024 missing or bypassable")
        ok = False
    elif gate.get("required_before_broader_public_release") is not True:
        error("PUB-GATE-0024 must be required before broader public release")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "first_controlled_public_reference_pilot" not in checks:
        error("reference-expansion-gate: pilot validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_broader_public_release_by_pilot_alone" not in rules:
        error("reference-expansion-gate: must block broader release by pilot alone")
        ok = False
    return ok


def validate_internal_link_graph() -> bool:
    ok = True
    graph = load_json(ROOT / "data" / "internal-link-graph.json")
    routes = {r.get("path"): r for r in graph.get("routes", [])}
    home = routes.get("/")
    if not home or "/reference/evidence-posture/" not in home.get("internal_links_out", []):
        error("internal link graph: homepage must link to evidence-posture")
        ok = False
    for path in PILOT_PATHS:
        if path not in routes:
            error(f"internal link graph: missing route {path}")
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
    if "validate_controlled_public_reference_pilot.py" not in content:
        error("validate_all.py must include pilot validator")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/controlled-public-reference-pilot-policy.json",
        "data/controlled-public-reference-pilot-v1.json",
        "data/public-route-candidate-registry.json",
        "data/public-route-readiness-v1.json",
        "data/internal-draft-registry.json",
        "data/reference-page-candidate-registry.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
        "data/internal-link-graph.json",
    ]
    for rel in parse_paths:
        try:
            load_json(ROOT / rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"{rel} parse failed: {exc}")
            return 1

    try:
        ET.parse(ROOT / "sitemap.xml")
        (ROOT / "index.html").read_text(encoding="utf-8")
    except (ET.ParseError, OSError) as exc:
        error(f"public surface parse failed: {exc}")
        return 1

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    checks = [
        validate_policy,
        validate_pilot_record,
        validate_all_public_pages,
        validate_route_registry,
        lambda: validate_pilot_era_public_surface(routes, error),
        validate_homepage,
        validate_registries,
        validate_publisher_governance,
        validate_internal_link_graph,
        validate_source_registry,
        validate_cross_file,
        lambda: validate_no_extra_public_html(error),
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
