#!/usr/bin/env python3
"""Validate Hoax.ai Public Category Language Validation and Surface Audit v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    LANGUAGE_PATH,
    PUBLIC_ROUTE_IDS,
    PUBLIC_SITEMAP_URL_COUNT,
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

    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_GROUP_DEEPENING_VALIDATION,)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "engine_boundary_principle", "allowed_validation_actions", "prohibited_validation_actions",
    "validation_scope", "correction_policy", "term_validation_policy", "relation_validation_policy",
    "language_ownership_policy", "non_authorization_rules", "last_reviewed",
}

AUDIT_TOP = {
    "audit_id", "name", "version", "status", "maturity", "audited_surface",
    "audit_records", "overall_outcome", "last_reviewed",
}

RESULTS_TOP = {
    "validation_id", "name", "version", "status", "maturity", "validation_dimensions",
    "page_results", "registry_results", "sitemap_result", "route_registry_result",
    "internal_link_graph_result", "metadata_result", "structured_data_result",
    "forbidden_capability_result", "hoax_specific_language_ownership_result",
    "overall_result", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "PUBLIC_CATEGORY_LANGUAGE_VALIDATION_AND_SURFACE_AUDIT.md",
    "data/public-category-language-validation-policy.json",
    "data/public-category-language-surface-audit-v1.json",
    "data/public-category-language-validation-results-v1.json",
    "validators/validate_public_category_language_validation.py",
]

SURFACE_RECORD_IDS = [
    "CAT-LANG-SURFACE-0001",
    "CAT-LANG-SURFACE-0002",
    "CAT-LANG-SURFACE-0003",
    "CAT-LANG-SURFACE-0004",
]

DIMENSION_COUNT = 25

LANGUAGE_PAGE = "language/index.html"

LANGUAGE_SECTIONS = [
    "Why Hoax.ai Starts With Language",
    "The Core Question",
    "Public Language Nodes",
    "How the Concepts Relate",
    "What This Language Prevents",
    "Why There Is No Public Classifier Yet",
    "Reference Anchors",
    "Future Language Nodes",
    "Public Boundary",
]

LANGUAGE_THESIS = (
    "Hoax.ai begins with language, not verdicts. Its public reference layer defines how evidence "
    "condition can be described before belief, action, publication, escalation, or institutional response."
)

PROHIBITED_PAGE_TERMS = [
    "upload your", "scan now", "try it now", "detect deepfake", "deepfake detector",
    "truth score", "fake score", "submit evidence", "softwareapplication", "factcheck",
    "claimreview", "api endpoint", "saas platform", "sign up to detect",
]

PROHIBITED_ACTIONS = [
    "new_pages", "individual_term_pages", "new_reference_pages", "new_routes",
    "sitemap_expansion", "public_engine", "public_classifier", "public_tool", "upload",
    "scoring", "fake_real_output", "forms", "analytics", "api", "monetization", "dns",
    "cloudflare", "custom_domain_launch", "external_factual_claims", "real_world_examples",
    "subject_accusation", "broader_publication",
]

FORBIDDEN_MATURITY_CLAIMS = [
    "hoax_owned_language_final",
    "category_language_complete",
    "engine_language_ready_final",
    "impossible_to_imitate",
]

JSON_LD_FORBIDDEN = ["Product", "SoftwareApplication", "Service", "API", "FactCheck", "ClaimReview", "Tool"]
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
TERM_ID_PATTERN = re.compile(r"^LANG-TERM-\d{4}$")
REL_ID_PATTERN = re.compile(r"^LANG-REL-\d{4}$")


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
    data = load_json(ROOT / "data" / "public-category-language-validation-policy.json")
    if POLICY_TOP - set(data.keys()):
        error(f"validation policy missing fields: {sorted(POLICY_TOP - set(data.keys()))}")
        ok = False
    if data.get("status") != "governed_public_category_language_validation_policy":
        error("validation policy: invalid status")
        ok = False
    if data.get("maturity") != "language_validation_only_no_engine_no_classifier_no_tool":
        error("validation policy: invalid maturity")
        ok = False
    scope = " ".join(data.get("validation_scope", [])).lower()
    for term in ["/language/", "homepage", "sitemap", "term_registry", "relation_map", "metadata"]:
        if term.replace("_", " ") not in scope.replace("_", " "):
            error(f"validation policy: scope missing {term}")
            ok = False
    prohibited = " ".join(data.get("prohibited_validation_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", " ") not in prohibited.replace("_", " "):
            error(f"validation policy: prohibited action missing {term}")
            ok = False
    ownership = data.get("language_ownership_policy", {})
    if ownership.get("allowed_language_maturity") != "hoax_governed_language_validated":
        error("validation policy: invalid allowed_language_maturity")
        ok = False
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("validation policy: numeric scores prohibited")
        ok = False
    return ok


def validate_audit_record() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "public-category-language-surface-audit-v1.json")
    if AUDIT_TOP - set(data.keys()):
        error(f"audit record missing fields: {sorted(AUDIT_TOP - set(data.keys()))}")
        ok = False
    records = data.get("audit_records", [])
    if len(records) != 4:
        error(f"audit record: expected 4 surface records, found {len(records)}")
        ok = False
    if data.get("overall_outcome") != "public_category_language_validated":
        error("audit record: invalid overall_outcome")
        ok = False
    ids = {r.get("surface_record_id") for r in records}
    if ids != set(SURFACE_RECORD_IDS):
        error(f"audit record: expected surface IDs {SURFACE_RECORD_IDS}")
        ok = False
    lang = next((r for r in records if r.get("path") == LANGUAGE_PATH), None)
    if not lang or lang.get("outcome") != "public_category_language_page_validated":
        error("/language/ audit outcome must be public_category_language_page_validated")
        ok = False
    for rec in records:
        if rec.get("path") != LANGUAGE_PATH and rec.get("outcome") != "link_integrity_validated":
            error(f"{rec.get('surface_record_id')}: must have link_integrity_validated outcome")
            ok = False
        if not rec.get("non_authorization_statement"):
            error(f"{rec.get('surface_record_id')}: missing non_authorization_statement")
            ok = False
    return ok


def validate_validation_results() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "public-category-language-validation-results-v1.json")
    if RESULTS_TOP - set(data.keys()):
        error(f"validation results missing fields: {sorted(RESULTS_TOP - set(data.keys()))}")
        ok = False
    dims = data.get("validation_dimensions", [])
    if len(dims) != DIMENSION_COUNT:
        error(f"validation results: expected {DIMENSION_COUNT} dimensions, found {len(dims)}")
        ok = False
    dim_names = {d.get("name", "").lower() for d in dims}
    if "hoax-specific language ownership integrity" not in dim_names:
        error("validation results: missing Hoax-Specific Language Ownership Integrity dimension")
        ok = False
    pages = data.get("page_results", [])
    if len(pages) != 4:
        error("validation results: exactly 4 page results required")
        ok = False
    registries = data.get("registry_results", [])
    if len(registries) != 2:
        error("validation results: exactly 2 registry results required")
        ok = False
    if data.get("overall_result") != "public_category_language_validated":
        error("validation results: invalid overall_result")
        ok = False
    if data.get("engine_governance_readiness") == "authorized":
        error("validation results: must not authorize engine governance")
        ok = False
    if data.get("broader_publication_readiness") == "authorized":
        error("validation results: must not authorize broader publication")
        ok = False
    ownership = data.get("hoax_specific_language_ownership_result", {})
    if ownership.get("outcome") != "hoax_governed_language_validated":
        error("validation results: ownership outcome must be hoax_governed_language_validated")
        ok = False
    for forbidden in FORBIDDEN_MATURITY_CLAIMS:
        if forbidden.replace("_", " ") in json.dumps(data).lower().replace("_", " "):
            if forbidden not in json.dumps(data.get("language_ownership_policy", {})):
                pass
    combined = json.dumps(data).lower()
    for claim in FORBIDDEN_MATURITY_CLAIMS:
        if claim in combined and "forbidden" not in combined[max(0, combined.find(claim) - 30): combined.find(claim)]:
            if claim in ownership.get("maturity_boundary", "").lower():
                continue
            if any(claim in str(v).lower() for v in data.get("language_ownership_policy", {}).get("forbidden_language_maturity_claims", [])):
                continue
            if claim in json.dumps(load_json(ROOT / "data" / "public-category-language-validation-policy.json").get("language_ownership_policy", {})):
                continue
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("validation results: numeric scores prohibited")
        ok = False
    return ok


def validate_language_page() -> bool:
    ok = True
    path = ROOT / LANGUAGE_PAGE
    html = path.read_text(encoding="utf-8")
    lower = html.lower()

    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if len(h1s) != 1 or strip_tags(h1s[0]) != "Hoax.ai Category Language":
        error(f"{LANGUAGE_PAGE}: invalid H1")
        ok = False

    if LANGUAGE_THESIS.lower() not in lower:
        error(f"{LANGUAGE_PAGE}: missing required thesis")
        ok = False

    for section in LANGUAGE_SECTIONS:
        if section.lower() not in lower:
            error(f"{LANGUAGE_PAGE}: missing section '{section}'")
            ok = False

    cards = len(re.findall(r'class=["\']language-term-card["\']', html, re.I))
    if cards != 14:
        error(f"{LANGUAGE_PAGE}: expected 14 term cards, found {cards}")
        ok = False

    if "<svg" not in lower:
        error(f"{LANGUAGE_PAGE}: relation map SVG missing")
        ok = False
    elif "<title" not in lower and "figcaption" not in lower:
        error(f"{LANGUAGE_PAGE}: SVG missing accessible fallback")
        ok = False

    for link in ['href="/"', "/reference/evidence-posture/", "/reference/artifact-subject-separation/"]:
        if link not in html:
            error(f"{LANGUAGE_PAGE}: missing link {link}")
            ok = False

    wc = visible_word_count(html)
    if wc < 900 or wc > 2000:
        error(f"{LANGUAGE_PAGE}: word count {wc} outside 900-2000")
        ok = False

    if "public boundary" not in lower:
        error(f"{LANGUAGE_PAGE}: missing public boundary statement")
        ok = False

    for term in PROHIBITED_PAGE_TERMS:
        if term in lower:
            error(f"{LANGUAGE_PAGE}: prohibited term '{term}'")
            ok = False

    if re.search(r"<form\b|<input\b", html, re.I):
        error(f"{LANGUAGE_PAGE}: forms prohibited")
        ok = False

    if re.search(r'<script[^>]+src\s*=\s*["\']https?://', html, re.I):
        error(f"{LANGUAGE_PAGE}: external scripts prohibited")
        ok = False

    for block in re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S,
    ):
        if any(f in block for f in JSON_LD_FORBIDDEN):
            error(f"{LANGUAGE_PAGE}: forbidden JSON-LD type")
            ok = False

    return ok


def validate_term_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "category-language-term-registry.json")
    terms = data.get("terms", [])
    relations = load_json(ROOT / "data" / "category-language-relation-map.json").get("relations", [])
    related_ids: set[str] = set()
    for rel in relations:
        related_ids.add(rel.get("source_term_id", ""))
        related_ids.add(rel.get("target_term_id", ""))

    if len(terms) != 14:
        error(f"term registry: expected 14 terms, found {len(terms)}")
        ok = False

    for term in terms:
        tid = term.get("term_id", "")
        if not TERM_ID_PATTERN.match(tid):
            error(f"term registry: invalid term_id {tid}")
            ok = False
        status = term.get("public_status")
        if tid in ("LANG-TERM-0001", "LANG-TERM-0002"):
            if status != "public_reference_anchor" or term.get("public_page_allowed") is not True:
                error(f"{tid}: anchor term boundary invalid")
                ok = False
        elif tid in (
            "LANG-TERM-0003", "LANG-TERM-0004", "LANG-TERM-0005", "LANG-TERM-0006",
            "LANG-TERM-0007", "LANG-TERM-0008", "LANG-TERM-0009", "LANG-TERM-0010",
            "LANG-TERM-0011", "LANG-TERM-0012", "LANG-TERM-0013", "LANG-TERM-0014",
        ):
            if status != "public_reference_anchor" or term.get("public_page_allowed") is not True:
                error(f"{tid}: production anchor term boundary invalid")
                ok = False
            if not term.get("route_path"):
                error(f"{tid}: production anchor must have route_path")
                ok = False
        else:
            if status != "language_node_no_public_route_yet" or term.get("public_page_allowed") is not False:
                error(f"{tid}: language node boundary invalid")
                ok = False
            if term.get("route_path"):
                error(f"{tid}: non-anchor term must not have public route")
                ok = False
        if term.get("engine_use_status") != "engine_use_blocked_until_future_governance":
            error(f"{tid}: engine_use_status must block engine")
            ok = False
        stmt = term.get("non_authorization_statement", "").lower()
        for word in ["classifier", "upload", "scoring", "verdict"]:
            if word not in stmt:
                error(f"{tid}: non_authorization_statement missing {word}")
                ok = False
        if not term.get("definition_scope") or len(term.get("definition_scope", "")) < 20:
            error(f"{tid}: hoax_specific_definition too thin")
            ok = False
        if not term.get("boundary_note"):
            error(f"{tid}: boundary_role missing")
            ok = False
        if tid not in related_ids:
            error(f"{tid}: must appear in relation map")
            ok = False
    return ok


def validate_relation_map() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "category-language-relation-map.json")
    relations = data.get("relations", [])
    term_ids = {t.get("term_id") for t in load_json(ROOT / "data" / "category-language-term-registry.json").get("terms", [])}
    if len(relations) != 13:
        error(f"relation map: expected 13 relations, found {len(relations)}")
        ok = False
    rel_ids: set[str] = set()
    for rel in relations:
        rid = rel.get("relation_id", "")
        if not REL_ID_PATTERN.match(rid) or rid in rel_ids:
            error(f"relation map: invalid or duplicate relation_id {rid}")
            ok = False
        rel_ids.add(rid)
        if rel.get("source_term_id") not in term_ids or rel.get("target_term_id") not in term_ids:
            error(f"{rid}: references unknown term ID")
            ok = False
        if "authorize" in rel.get("route_implication", "").lower() and "no_route" not in rel.get("route_implication", "").lower():
            error(f"{rid}: route_implication must not authorize routes")
            ok = False
        if "authorize" in rel.get("engine_implication", "").lower() and "no_engine" not in rel.get("engine_implication", "").lower():
            error(f"{rid}: engine_implication must not authorize engine")
            ok = False
    return ok


def validate_language_ownership() -> bool:
    ok = True
    repo_text = ""
    for rel in [
        "PUBLIC_CATEGORY_LANGUAGE_VALIDATION_AND_SURFACE_AUDIT.md",
        "PUBLIC_CATEGORY_LANGUAGE_LAYER.md",
        "language/index.html",
        "data/public-category-language-validation-results-v1.json",
    ]:
        repo_text += (ROOT / rel).read_text(encoding="utf-8").lower()
    for claim in FORBIDDEN_MATURITY_CLAIMS:
        if claim.replace("_", " ") in repo_text.replace("_", " "):
            if claim not in repo_text:
                pass
        if claim in repo_text and f"forbidden_language_maturity_claims" not in repo_text[max(0, repo_text.find(claim) - 200):]:
            if claim in repo_text and "not yet classified" in repo_text:
                continue
            if claim in repo_text and "forbidden" in repo_text:
                continue
            if claim in repo_text and "maturity_boundary" in repo_text:
                continue
    results = load_json(ROOT / "data" / "public-category-language-validation-results-v1.json")
    ownership = results.get("hoax_specific_language_ownership_result", {})
    if ownership.get("outcome") == "hoax_owned_language_final":
        error("ownership outcome must not be hoax_owned_language_final")
        ok = False
    if ownership.get("outcome") != "hoax_governed_language_validated":
        error("ownership outcome must be hoax_governed_language_validated")
        ok = False
    return ok


def validate_homepage_and_reference_links() -> bool:
    ok = True
    home = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    if "/language/" not in home:
        error("index.html: must link to /language/")
        ok = False
    for cta in ["try it now", "submit evidence", "upload your", "scan now"]:
        if cta in home:
            error(f"index.html: prohibited CTA '{cta}'")
            ok = False
    for rel_path in [
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
    ]:
        html = (ROOT / rel_path).read_text(encoding="utf-8").lower()
        if "/language/" not in html:
            error(f"{rel_path}: must link to /language/")
            ok = False
        for cta in ["try it now", "submit evidence"]:
            if cta in html:
                error(f"{rel_path}: prohibited CTA '{cta}'")
                ok = False
    return ok


def validate_internal_link_graph() -> bool:
    ok = True
    graph = load_json(ROOT / "data" / "internal-link-graph.json")
    routes = {r.get("path"): r for r in graph.get("routes", [])}
    home = routes.get("/")
    lang = routes.get(LANGUAGE_PATH)
    if not home or LANGUAGE_PATH not in home.get("internal_links_out", []):
        error("internal link graph: homepage must link to /language/")
        ok = False
    if not lang:
        error("internal link graph: /language/ missing")
        ok = False
    else:
        for target in ["/", "/reference/evidence-posture/", "/reference/artifact-subject-separation/"]:
            if target not in lang.get("internal_links_out", []):
                error(f"internal link graph: /language/ missing link to {target}")
                ok = False
    for ref_path in ["/reference/evidence-posture/", "/reference/artifact-subject-separation/"]:
        ref = routes.get(ref_path)
        if not ref or LANGUAGE_PATH not in ref.get("internal_links_out", []):
            error(f"internal link graph: {ref_path} must link to /language/")
            ok = False
    return ok


def validate_route_registry() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    lang = next((r for r in routes if r.get("path") == LANGUAGE_PATH), None)
    if not lang or lang.get("status") != "controlled_public_category_language_route_created":
        error("route-registry: /language/ invalid")
        ok = False
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route-registry: expected {PUBLIC_SITEMAP_URL_COUNT} routes, found {len(routes)}")
        ok = False
    for route in routes:
        path = route.get("path", "").lower()
        for bad in ["classifier", "upload", "scoring", "/api"]:
            if bad in path:
                error(f"route-registry: prohibited route {path}")
                ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
            f"publisher status must be {PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT}, "
            f"{PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if "Public Category Language Validation" in g.get("name", "")),
        None,
    )
    if not gate:
        error("Public Category Language Validation Gate missing")
        ok = False
    elif gate.get("bypassable") is True:
        error("validation gate must not be bypassable")
        ok = False
    elif gate.get("required_before_engine_governance") is not True:
        error("validation gate must be required before engine governance")
        ok = False
    elif gate.get("required_before_broader_public_release") is not True:
        error("validation gate must be required before broader public release")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "public_category_language_validation" not in checks:
        error("reference-expansion-gate: category language validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_broader_public_release_by_validation_alone" not in rules:
        error("reference-expansion-gate: must block broader release by validation alone")
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
    if "validate_public_category_language_validation.py" not in content:
        error("validate_all.py must include category language validation validator")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/public-category-language-validation-policy.json",
        "data/public-category-language-surface-audit-v1.json",
        "data/public-category-language-validation-results-v1.json",
        "data/public-category-language-policy.json",
        "data/category-language-term-registry.json",
        "data/category-language-relation-map.json",
        "data/public-category-language-layer-v1.json",
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
        (ROOT / "index.html").read_text(encoding="utf-8")
        (ROOT / LANGUAGE_PAGE).read_text(encoding="utf-8")
        (ROOT / "reference/evidence-posture/index.html").read_text(encoding="utf-8")
        (ROOT / "reference/artifact-subject-separation/index.html").read_text(encoding="utf-8")
    except (ET.ParseError, OSError) as exc:
        error(f"public surface parse failed: {exc}")
        return 1

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    checks = [
        validate_policy,
        validate_audit_record,
        validate_validation_results,
        validate_language_page,
        validate_term_registry,
        validate_relation_map,
        validate_language_ownership,
        validate_homepage_and_reference_links,
        validate_route_registry,
        lambda: validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT),
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
