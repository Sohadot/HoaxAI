#!/usr/bin/env python3
"""Validate Hoax.ai Public Category Language Layer v1."""

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
)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "language_principle", "allowed_language_layer_actions", "prohibited_language_layer_actions",
    "language_scope", "term_status_policy", "relation_policy", "route_policy",
    "metadata_policy", "non_authorization_rules", "last_reviewed",
}

TERM_REGISTRY_TOP = {
    "registry_id", "name", "version", "status", "maturity", "terms", "last_reviewed",
}

RELATION_MAP_TOP = {
    "relation_map_id", "name", "version", "status", "maturity", "relations", "last_reviewed",
}

LAYER_TOP = {
    "layer_id", "name", "version", "status", "maturity", "public_route", "public_page_record",
    "term_registry_ref", "relation_map_ref", "linked_public_reference_pages",
    "prohibited_capabilities", "non_authorization_statement", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "PUBLIC_CATEGORY_LANGUAGE_LAYER.md",
    "data/public-category-language-policy.json",
    "data/category-language-term-registry.json",
    "data/category-language-relation-map.json",
    "data/public-category-language-layer-v1.json",
    "language/index.html",
    "validators/validate_public_category_language_layer.py",
]

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
    "engine", "classifier", "tool", "upload", "scoring", "fake_real_output", "forms",
    "analytics", "api", "monetization", "dns", "cloudflare", "custom_domain_launch",
    "individual_term_routes", "broader_route_expansion", "external_factual_claims",
    "subject_accusation",
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
    data = load_json(ROOT / "data" / "public-category-language-policy.json")
    if POLICY_TOP - set(data.keys()):
        error(f"language policy missing fields: {sorted(POLICY_TOP - set(data.keys()))}")
        ok = False
    if data.get("status") != "governed_public_category_language_policy":
        error("language policy: invalid status")
        ok = False
    if data.get("maturity") != "one_public_language_route_no_engine_no_classifier_no_tool":
        error("language policy: invalid maturity")
        ok = False
    allowed = " ".join(data.get("allowed_language_layer_actions", [])).lower()
    if "one public language route" not in allowed.replace("_", " "):
        error("language policy: must allow exactly one public language route")
        ok = False
    prohibited = " ".join(data.get("prohibited_language_layer_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", " ") not in prohibited.replace("_", " ") and term not in prohibited:
            error(f"language policy: prohibited action missing {term}")
            ok = False
    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in ["engine", "classifier", "upload", "scoring", "individual_term", "broader_publication"]:
        if term.replace("_", " ") not in non_auth.replace("_", " "):
            error(f"language policy: non_authorization_rules missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(json.dumps(data)):
        error("language policy: numeric scores prohibited")
        ok = False
    return ok


def validate_term_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "category-language-term-registry.json")
    if TERM_REGISTRY_TOP - set(data.keys()):
        error(f"term registry missing fields: {sorted(TERM_REGISTRY_TOP - set(data.keys()))}")
        ok = False
    terms = data.get("terms", [])
    if len(terms) != 14:
        error(f"term registry: expected 14 terms, found {len(terms)}")
        ok = False
    ids: set[str] = set()
    for term in terms:
        tid = term.get("term_id", "")
        if not TERM_ID_PATTERN.match(tid):
            error(f"term registry: invalid term_id {tid}")
            ok = False
        if tid in ids:
            error(f"term registry: duplicate term_id {tid}")
            ok = False
        ids.add(tid)
        status = term.get("public_status")
        if tid in ("LANG-TERM-0001", "LANG-TERM-0002"):
            if status != "public_reference_anchor":
                error(f"{tid}: must be public_reference_anchor")
                ok = False
            if term.get("public_page_allowed") is not True:
                error(f"{tid}: public_page_allowed must be true")
                ok = False
        elif tid in (
            "LANG-TERM-0003", "LANG-TERM-0004", "LANG-TERM-0005", "LANG-TERM-0006",
            "LANG-TERM-0007", "LANG-TERM-0008", "LANG-TERM-0009", "LANG-TERM-0010",
            "LANG-TERM-0011", "LANG-TERM-0012", "LANG-TERM-0013", "LANG-TERM-0014",
        ):
            if status != "public_reference_anchor":
                error(f"{tid}: must be public_reference_anchor")
                ok = False
            if term.get("public_page_allowed") is not True:
                error(f"{tid}: public_page_allowed must be true")
                ok = False
            if not term.get("route_path"):
                error(f"{tid}: production anchor must have route_path")
                ok = False
        else:
            if status != "language_node_no_public_route_yet":
                error(f"{tid}: must be language_node_no_public_route_yet")
                ok = False
            if term.get("public_page_allowed") is not False:
                error(f"{tid}: public_page_allowed must be false")
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
    return ok


def validate_relation_map() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "category-language-relation-map.json")
    if RELATION_MAP_TOP - set(data.keys()):
        error(f"relation map missing fields: {sorted(RELATION_MAP_TOP - set(data.keys()))}")
        ok = False
    relations = data.get("relations", [])
    if len(relations) != 13:
        error(f"relation map: expected 13 relations, found {len(relations)}")
        ok = False
    term_ids = {t.get("term_id") for t in load_json(ROOT / "data" / "category-language-term-registry.json").get("terms", [])}
    rel_ids: set[str] = set()
    for rel in relations:
        rid = rel.get("relation_id", "")
        if not REL_ID_PATTERN.match(rid):
            error(f"relation map: invalid relation_id {rid}")
            ok = False
        if rid in rel_ids:
            error(f"relation map: duplicate relation_id {rid}")
            ok = False
        rel_ids.add(rid)
        if rel.get("source_term_id") not in term_ids or rel.get("target_term_id") not in term_ids:
            error(f"{rid}: references unknown term ID")
            ok = False
        if rel.get("public_display_allowed") is not True:
            error(f"{rid}: public_display_allowed must be true")
            ok = False
        if "authorize" in rel.get("route_implication", "").lower() and "no_route" not in rel.get("route_implication", "").lower():
            error(f"{rid}: route_implication must not authorize routes")
            ok = False
        if "authorize" in rel.get("engine_implication", "").lower() and "no_engine" not in rel.get("engine_implication", "").lower():
            error(f"{rid}: engine_implication must not authorize engine")
            ok = False
        combined = " ".join(
            str(rel.get(k, "")) for k in ["relation_statement", "relation_type"]
        ).lower()
        for bad in ["verdict output", "detection service", "upload workflow"]:
            if bad in combined:
                error(f"{rid}: prohibited implication {bad}")
                ok = False
    return ok


def validate_layer_record() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "public-category-language-layer-v1.json")
    if LAYER_TOP - set(data.keys()):
        error(f"layer record missing fields: {sorted(LAYER_TOP - set(data.keys()))}")
        ok = False
    if data.get("public_route") != LANGUAGE_PATH:
        error("layer record: public_route must be /language/")
        ok = False
    if data.get("status") != "public_category_language_layer_created":
        error("layer record: invalid status")
        ok = False
    if data.get("maturity") != "one_public_language_route_no_engine_no_classifier_no_tool":
        error("layer record: invalid maturity")
        ok = False
    linked = set(data.get("linked_public_reference_pages", []))
    expected = {"/reference/evidence-posture/", "/reference/artifact-subject-separation/"}
    if linked != expected:
        error("layer record: linked_public_reference_pages mismatch")
        ok = False
    return ok


def validate_language_page() -> bool:
    ok = True
    path = ROOT / LANGUAGE_PAGE
    if not path.exists():
        error(f"{LANGUAGE_PAGE}: missing")
        return False
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

    for link in ['href="/"', "/reference/evidence-posture/", "/reference/artifact-subject-separation/"]:
        if link not in html:
            error(f"{LANGUAGE_PAGE}: missing link {link}")
            ok = False

    wc = visible_word_count(html)
    if wc < 900 or wc > 1500:
        error(f"{LANGUAGE_PAGE}: word count {wc} outside 900-1500")
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

    if "<svg" in lower:
        if "<title" not in lower and "figcaption" not in lower:
            error(f"{LANGUAGE_PAGE}: SVG missing accessible fallback")
            ok = False

    return ok


def validate_route_registry() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    lang = next((r for r in routes if r.get("path") == LANGUAGE_PATH), None)
    if not lang:
        error("route-registry: /language/ route missing")
        ok = False
    elif lang.get("status") != "controlled_public_category_language_route_created":
        error("route-registry: /language/ invalid status")
        ok = False
    elif lang.get("page_type") != "public_category_language":
        error("route-registry: /language/ invalid page_type")
        ok = False

    lang_routes = [r for r in routes if r.get("page_type") == "public_category_language" or LANGUAGE_PATH in r.get("path", "")]
    if len(lang_routes) != 1:
        error("route-registry: exactly one language route required")
        ok = False

    for route in routes:
        path = route.get("path", "").lower()
        for bad in ["classifier", "upload", "scoring", "/api"]:
            if bad in path:
                error(f"route-registry: prohibited route {path}")
                ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    html = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    if "/language/" not in html and "language" not in html:
        error("index.html: must link to /language/")
        ok = False
    for cta in ["try it now", "submit evidence", "upload your", "scan now"]:
        if cta in html:
            error(f"index.html: prohibited CTA '{cta}'")
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
        error("internal link graph: /language/ route missing")
        ok = False
    else:
        out = lang.get("internal_links_out", [])
        for target in ["/", "/reference/evidence-posture/", "/reference/artifact-subject-separation/"]:
            if target not in out:
                error(f"internal link graph: /language/ missing link to {target}")
                ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE}, "
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
    gate = next((g for g in gates if "Public Category Language Layer" in g.get("name", "")), None)
    if not gate:
        error("Public Category Language Layer Gate missing")
        ok = False
    elif gate.get("bypassable") is True:
        error("Public Category Language Layer Gate must not be bypassable")
        ok = False
    elif gate.get("required_before_engine_governance") is not True:
        error("Public Category Language Layer Gate must be required before engine governance")
        ok = False
    elif gate.get("required_before_broader_public_release") is not True:
        error("Public Category Language Layer Gate must be required before broader public release")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "public_category_language" not in checks and "category_language" not in checks:
        error("reference-expansion-gate: category language layer required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_broader_public_release_by_language_layer_alone" not in rules:
        error("reference-expansion-gate: must block broader release by language layer alone")
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
    if "validate_public_category_language_layer.py" not in content:
        error("validate_all.py must include category language validator")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
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
        validate_term_registry,
        validate_relation_map,
        validate_layer_record,
        validate_language_page,
        validate_route_registry,
        validate_homepage,
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
