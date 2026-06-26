#!/usr/bin/env python3
"""Validate Hoax.ai public reference live surface audit enforcement."""

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
)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "visibility_principle", "allowed_audit_actions", "prohibited_audit_actions",
    "audit_scope", "live_surface_policy", "correction_policy", "non_authorization_rules",
    "last_reviewed",
}

AUDIT_TOP = {
    "audit_id", "name", "version", "status", "maturity", "audited_surface",
    "audit_records", "overall_outcome", "last_reviewed",
}

RESULTS_TOP = {
    "validation_id", "name", "version", "status", "maturity", "validation_dimensions",
    "page_results", "sitemap_result", "route_registry_result", "internal_link_graph_result",
    "metadata_result", "structured_data_result", "forbidden_capability_result",
    "overall_result", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "PUBLIC_REFERENCE_VALIDATION_AND_LIVE_SURFACE_AUDIT.md",
    "data/public-reference-live-surface-policy.json",
    "data/public-reference-live-surface-audit-v1.json",
    "data/public-reference-validation-results-v1.json",
    "validators/validate_public_reference_live_surface.py",
]

SURFACE_RECORD_IDS = ["LIVE-SURFACE-0001", "LIVE-SURFACE-0002", "LIVE-SURFACE-0003"]

DIMENSION_COUNT = 20

PILOT_PAGES = {
    "reference/evidence-posture/index.html": {
        "h1": "Evidence Posture",
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
    "upload your", "scan now", "try it now", "detect deepfake", "deepfake detector",
    "truth score", "fake score", "public classifier", "submit evidence",
    "softwareapplication", "factcheck", "claimreview", "api endpoint",
    "saas platform", "sign up to detect",
]

PROHIBITED_ACTIONS = [
    "new_pages", "new_routes", "sitemap_expansion", "public_engine", "public_classifier",
    "public_tool", "upload", "scoring", "forms", "analytics", "api", "monetization",
    "dns", "cloudflare", "custom_domain_launch", "external_factual_claims", "broader_publication",
]

JSON_LD_FORBIDDEN = ["Product", "SoftwareApplication", "Service", "API", "FactCheck", "ClaimReview"]
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)


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
    data = load_json(ROOT / "data" / "public-reference-live-surface-policy.json")
    if POLICY_TOP - set(data.keys()):
        error(f"live surface policy missing fields: {sorted(POLICY_TOP - set(data.keys()))}")
        ok = False
    if data.get("status") != "governed_public_reference_live_surface_policy":
        error("live surface policy: invalid status")
        ok = False
    if data.get("maturity") != "live_surface_validation_only_no_engine_no_classifier_no_broader_publication":
        error("live surface policy: invalid maturity")
        ok = False
    prohibited = " ".join(data.get("prohibited_audit_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", " ") not in prohibited.replace("_", " ") and term not in prohibited:
            error(f"live surface policy: prohibited_audit_actions missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("live surface policy: numeric score language prohibited")
        ok = False
    return ok


def validate_audit_record() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "public-reference-live-surface-audit-v1.json")
    if AUDIT_TOP - set(data.keys()):
        error(f"live surface audit missing fields: {sorted(AUDIT_TOP - set(data.keys()))}")
        ok = False
    records = data.get("audit_records", [])
    if len(records) != 3:
        error("live surface audit: exactly 3 surface records required")
        ok = False
    seen = set()
    for rec in records:
        sid = rec.get("surface_record_id", "?")
        seen.add(sid)
        if not rec.get("expected_live_url"):
            error(f"audit record {sid}: expected_live_url required")
            ok = False
        if not rec.get("non_authorization_statement"):
            error(f"audit record {sid}: non_authorization_statement required")
            ok = False
        if sid == "LIVE-SURFACE-0001":
            if rec.get("outcome") != "existing_public_preview_surface":
                error("homepage audit outcome invalid")
                ok = False
        elif sid in ("LIVE-SURFACE-0002", "LIVE-SURFACE-0003"):
            if rec.get("outcome") != "controlled_public_reference_page_validated":
                error(f"audit record {sid}: invalid outcome")
                ok = False
    if seen != set(SURFACE_RECORD_IDS):
        error("live surface audit: missing required surface record IDs")
        ok = False
    if data.get("overall_outcome") != "live_surface_validated_controlled_reference_pilot":
        error("live surface audit: invalid overall_outcome")
        ok = False
    return ok


def validate_validation_results() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "public-reference-validation-results-v1.json")
    if RESULTS_TOP - set(data.keys()):
        error(f"validation results missing fields: {sorted(RESULTS_TOP - set(data.keys()))}")
        ok = False
    dims = data.get("validation_dimensions", [])
    if len(dims) != DIMENSION_COUNT:
        error(f"validation results: expected {DIMENSION_COUNT} dimensions, got {len(dims)}")
        ok = False
    for dim in dims:
        if dim.get("result") not in ("pass", "pass_expected_local"):
            error(f"validation dimension {dim.get('dimension_id')}: must pass")
            ok = False
    pages = data.get("page_results", [])
    if len(pages) != 3:
        error("validation results: exactly 3 page results required")
        ok = False
    if data.get("overall_result") != "live_surface_validated_controlled_reference_pilot":
        error("validation results: invalid overall_result")
        ok = False
    if data.get("broader_publication_readiness") == "authorized":
        error("validation results: must not authorize broader publication")
        ok = False
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("validation results: numeric scores prohibited")
        ok = False
    return ok


def validate_public_page(rel_path: str) -> bool:
    ok = True
    spec = PILOT_PAGES[rel_path]
    path = ROOT / rel_path
    html = path.read_text(encoding="utf-8")
    lower = html.lower()

    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if len(h1s) != 1 or strip_tags(h1s[0]) != spec["h1"]:
        error(f"{rel_path}: invalid H1")
        ok = False

    for section in spec["sections"]:
        if section.lower() not in lower:
            error(f"{rel_path}: missing section '{section}'")
            ok = False

    wc = visible_word_count(html)
    if wc < 900 or wc > 1500:
        error(f"{rel_path}: word count {wc} outside 900-1500")
        ok = False

    if spec["other_ref"] not in html or 'href="/"' not in html:
        error(f"{rel_path}: missing required internal links")
        ok = False

    if "reference boundary" not in lower or "does not operate" not in lower:
        error(f"{rel_path}: missing boundary statements")
        ok = False

    for term in PROHIBITED_PAGE_TERMS:
        if term in lower:
            error(f"{rel_path}: prohibited term '{term}'")
            ok = False

    if re.search(r"<form\b|<input\b", html, re.I):
        error(f"{rel_path}: forms prohibited")
        ok = False

    for block in re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S,
    ):
        if any(f in block for f in JSON_LD_FORBIDDEN):
            error(f"{rel_path}: forbidden JSON-LD type")
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
    for cta in ["try it now", "submit evidence", "upload your", "scan now"]:
        if cta in html:
            error(f"index.html: prohibited CTA '{cta}'")
            ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_LIVE_AUDIT}, "
            f"{PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE}, or "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN}, or "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION}, or "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT}, or "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0025"), None)
    if not gate or gate.get("bypassable") is True:
        error("PUB-GATE-0025 missing or bypassable")
        ok = False
    elif gate.get("required_before_public_release") is not True:
        error("PUB-GATE-0025 must be required before broader public release")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "public_reference_live_surface" not in checks and "live_surface" not in checks:
        error("reference-expansion-gate: live surface validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_broader_public_release_by_audit_alone" not in rules:
        error("reference-expansion-gate: must block broader release by audit alone")
        ok = False
    return ok


def validate_internal_link_graph() -> bool:
    ok = True
    graph = load_json(ROOT / "data" / "internal-link-graph.json")
    routes = {r.get("path"): r for r in graph.get("routes", [])}
    home = routes.get("/")
    if not home:
        error("internal link graph: homepage missing")
        ok = False
    else:
        out = home.get("internal_links_out", [])
        if "/reference/evidence-posture/" not in out or "/reference/artifact-subject-separation/" not in out:
            error("internal link graph: homepage missing reference links")
            ok = False
    for path in PILOT_PATHS:
        if path not in routes:
            error(f"internal link graph: missing {path}")
            ok = False
    return ok


def validate_reference_directories() -> bool:
    ok = True
    ref_root = ROOT / "reference"
    if not ref_root.is_dir():
        error("reference/: directory missing")
        return False
    allowed_dirs = {
        "evidence-posture",
        "artifact-subject-separation",
        "source-confidence",
        "provenance-gap",
        "not-assessable",
        "output-boundary",
        "synthetic-fragility",
        "evidence-chain",
        "context-collapse",
        "claim-source-traceability",
        "attribution-boundary",
        "claim-drift",
        "evidence-limitation",
        "interpretation-risk",
    }
    found = {d.name for d in ref_root.iterdir() if d.is_dir()}
    if found != allowed_dirs:
        error(f"reference/: unexpected directories {found}")
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
    if "validate_public_reference_live_surface.py" not in content:
        error("validate_all.py must include live surface validator")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/public-reference-live-surface-policy.json",
        "data/public-reference-live-surface-audit-v1.json",
        "data/public-reference-validation-results-v1.json",
        "data/controlled-public-reference-pilot-v1.json",
        "data/public-route-candidate-registry.json",
        "data/route-registry.json",
        "data/internal-link-graph.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
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

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    checks = [
        validate_policy,
        validate_audit_record,
        validate_validation_results,
        validate_reference_directories,
        validate_homepage,
        lambda: all(validate_public_page(p) for p in PILOT_PAGES),
        lambda: validate_pilot_era_public_surface(routes, error),
        validate_internal_link_graph,
        validate_publisher_governance,
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
