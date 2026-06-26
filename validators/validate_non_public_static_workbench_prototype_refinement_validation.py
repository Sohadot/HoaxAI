#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Prototype Refinement Validation v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING,
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

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
INDEX_PATH = PROTO_DIR / "index.html"
CSS_PATH = PROTO_DIR / "prototype.css"
PROTO_REL = "_internal_prototypes/evidence-posture-workbench"

ALLOWED_FILES = {"index.html", "prototype.css"}

POLICY_REQUIRED = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "identity_principle", "allowed_validation_actions", "prohibited_actions",
    "validation_scope", "correction_policy", "non_authorization_rules", "last_reviewed",
}

RESULTS_REQUIRED = {
    "validation_id", "name", "version", "status", "maturity", "validation_dimensions",
    "refinement_artifact_results", "prototype_file_results", "public_isolation_result",
    "static_safety_result", "visual_identity_result", "accessibility_performance_result",
    "governance_alignment_result", "overall_result", "last_reviewed",
}

VISUAL_REQUIRED = {
    "visual_validation_id", "name", "version", "status", "maturity",
    "evidence_chamber_result", "evidence_field_background_result", "refinement_trait_results",
    "forbidden_pattern_results", "originality_boundary", "overall_result", "last_reviewed",
}

ISOLATION_REQUIRED = {
    "isolation_audit_id", "name", "version", "status", "maturity",
    "internal_prototype_location", "route_registry_result", "sitemap_result",
    "homepage_link_result", "reference_page_link_result", "language_page_link_result",
    "public_navigation_result", "public_surface_result", "overall_outcome", "last_reviewed",
}

STATIC_AUDIT_REQUIRED = {
    "static_audit_id", "name", "version", "status", "maturity",
    "html_safety_results", "css_safety_results", "capability_block_results",
    "content_safety_results", "file_scope_results", "overall_outcome", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_REFINEMENT_VALIDATION_V1.md",
    "data/non-public-static-workbench-prototype-refinement-validation-policy.json",
    "data/non-public-static-workbench-prototype-refinement-validation-results-v1.json",
    "data/non-public-static-workbench-prototype-refinement-visual-identity-validation-v1.json",
    "data/non-public-static-workbench-prototype-refinement-public-isolation-audit-v1.json",
    "data/non-public-static-workbench-prototype-refinement-static-safety-audit-v1.json",
    "validators/validate_non_public_static_workbench_prototype_refinement_validation.py",
]

PROHIBITED_ACTIONS = [
    "new_prototype_files", "prototype_expansion", "public_route_creation", "sitemap_expansion",
    "public_navigation_link", "interface_behavior", "javascript", "forms", "inputs", "upload",
    "scoring", "fake_real_output", "generated_output", "engine", "classifier", "detector",
    "api", "analytics", "storage", "network_calls", "monetization", "dns", "cloudflare",
    "custom_domain_launch", "deployment_changes", "external_factual_claims", "subject_accusation",
]

REFINEMENT_TRAITS = [
    "evidence_chamber_strengthened", "governed_evidence_field_strengthened",
    "artifact_first_structure_strengthened", "boundary_first_layout_strengthened",
    "provenance_shadow_strengthened", "missing_context_as_absence_strengthened",
    "not_assessable_restraint_strengthened", "refusal_as_governance_strengthened",
    "output_envelope_containment_strengthened", "verification_path_legibility_strengthened",
    "anti_detector_differentiation_preserved",
]

FORBIDDEN_PATTERNS = [
    "detector_dashboard", "scanner_ui", "central_upload_box", "red_green_fake_real_result_logic",
    "truth_meter", "risk_score", "probability_gauge", "forensic_game_visuals", "policing_dashboard",
    "saas_analytics_dashboard", "product_landing_page_cta_layout", "try_it_now_pattern",
    "black_cyber_dashboard_default",
]

HTML_SAFETY_KEYS = [
    "no_script_tags", "no_forms", "no_inputs", "no_textarea", "no_file_inputs", "no_buttons",
    "no_upload_controls", "no_generated_output_regions", "no_external_scripts", "no_external_libraries",
]

CSS_SAFETY_KEYS = [
    "no_imports", "no_external_urls", "no_upload_dropzone_styling", "no_scoring_gauge_styling",
    "no_red_green_verdict_styling", "no_detector_scanner_naming", "evidence_field_classes_present",
    "chamber_boundary_classes_present", "provenance_shadow_classes_present",
    "output_envelope_classes_present", "responsive_rules_present",
]

CAPABILITY_BLOCK_KEYS = [
    "no_engine", "no_classifier", "no_detector", "no_upload", "no_scoring", "no_fake_real",
    "no_api", "no_analytics", "no_storage", "no_network_calls", "no_deployment_change",
]

CONTENT_SAFETY_KEYS = [
    "no_real_people", "no_real_companies", "no_real_institutions", "no_real_brands",
    "no_current_events", "no_political_events", "no_accusations", "no_external_factual_claims",
    "no_generated_analysis", "no_verified_certified_claims",
]

FILE_SCOPE_KEYS = [
    "only_index_and_css_in_prototype_directory", "no_additional_prototype_files",
    "no_new_prototype_directories", "only_allowed_files_modified",
]

REQUIRED_ZONES = [
    "Workbench Boundary Header", "Artifact Context Zone",
    "Source and Provenance Context Zone", "Missing Information Zone",
    "State Routing Zone", "Refusal and Boundary Zone",
    "Output Envelope Preview Zone", "Verification Questions Zone",
]

REQUIRED_CONCEPTS = [
    "Evidence Chamber", "Governed Evidence Field", "Artifact–Subject Boundary",
    "Provenance Shadow", "Missing Context", "Not Assessable", "Refusal Gate",
    "Output Envelope", "Verification Path",
]

REQUIRED_STATEMENTS = [
    "Internal static prototype. Non-public web surface. No engine. No classifier. No upload. No scoring. No verdict.",
    "This static prototype explores the Evidence Chamber interface direction.",
    "Evidence is structured before it is believed, escalated, published, or judged.",
]

STRENGTHENED_HTML_MARKERS = [
    "governed reasoning chamber",
    "artifact-first structure",
    "confidence-limiting absence",
    "structural condition",
    "protected restraint",
    "refusal is governance",
    "contained, limited, and non-verdict",
    "inquiry paths",
]

STRENGTHENED_CSS_CLASSES = [
    "evidence-chamber-frame", "governed-evidence-field", "provenance-shadow",
    "missing-context-absence", "not-assessable-restraint", "refusal-gate", "output-envelope",
]

PROHIBITED_HTML_PATTERNS = [
    (r"<script\b", "script tag"), (r"<form\b", "form element"), (r"<input\b", "input element"),
    (r"<textarea\b", "textarea element"), (r"type\s*=\s*['\"]file['\"]", "file input"),
    (r"<button\b", "button element"),
]

PROHIBITED_CONTENT = [
    r"\btry it now\b", r"\bsubmit evidence\b", r"\bupload now\b",
    r"\bfake\b.*\breal\b", r"\breal score\b", r"\b\d+\s*%\b", r"\bverified\b", r"\bcertified\b",
]

NEGATION_CONTEXT = re.compile(r"\b(does not|do not|no|not|without)\b", re.I)
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
READINESS_FORBIDDEN = re.compile(
    r"\b(prototype.?expansion.?ready|public.?workbench.?ready|engine.?ready|classifier.?ready|"
    r"tool.?ready|deployment.?ready|public.?release.?ready|production.?ready)\b",
    re.I,
)

DIMENSION_COUNT = 43


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-prototype-refinement-validation-policy.json"
    policy = load_json(path)
    if not POLICY_REQUIRED.issubset(set(policy)):
        error("refinement validation policy: missing required top-level fields")
        ok = False
    if policy.get("status") != "governed_non_public_static_workbench_prototype_refinement_validation_policy":
        error("refinement validation policy: invalid status")
        ok = False
    if policy.get("maturity") != "validation_only_refined_static_internal_prototype_no_engine_no_classifier_no_public_route":
        error("refinement validation policy: invalid maturity")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"refinement validation policy: missing prohibited action {action}")
            ok = False
    correction = policy.get("correction_policy", "").lower()
    for term in ["files", "routes", "sitemap", "js", "forms", "upload", "scoring", "engine"]:
        if term not in correction:
            error(f"refinement validation policy: correction_policy must block {term}")
            ok = False
    blocked = " ".join(policy.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in ["public_workbench", "prototype_expansion", "production_readiness"]:
        if term.replace("_", " ") not in blocked and term not in blocked:
            error(f"refinement validation policy: non_authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("refinement validation policy: numeric score found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-prototype-refinement-validation-results-v1.json"
    data = load_json(path)
    if not RESULTS_REQUIRED.issubset(set(data)):
        error("refinement validation results: missing required top-level fields")
        ok = False
    if len(data.get("validation_dimensions", [])) != DIMENSION_COUNT:
        error(f"refinement validation results: expected {DIMENSION_COUNT} dimensions")
        ok = False
    if data.get("overall_result") != "non_public_static_prototype_refinement_validated":
        error("refinement validation results: invalid overall_result")
        ok = False
    if READINESS_FORBIDDEN.search(path.read_text(encoding="utf-8")):
        error("refinement validation results: must not imply expansion or readiness")
        ok = False
    return ok


def validate_visual_identity() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-prototype-refinement-visual-identity-validation-v1.json"
    data = load_json(path)
    if not VISUAL_REQUIRED.issubset(set(data)):
        error("refinement visual identity validation: missing required top-level fields")
        ok = False
    if data.get("status") != "non_public_static_prototype_refinement_visual_identity_validated":
        error("refinement visual identity validation: invalid status")
        ok = False
    if data.get("overall_result") != "refinement_visual_identity_validated":
        error("refinement visual identity validation: invalid overall_result")
        ok = False
    traits = data.get("refinement_trait_results", {})
    for trait in REFINEMENT_TRAITS:
        if trait not in traits:
            error(f"refinement visual identity validation: missing trait {trait}")
            ok = False
    forbidden = data.get("forbidden_pattern_results", {})
    for pattern in FORBIDDEN_PATTERNS:
        if pattern not in forbidden:
            error(f"refinement visual identity validation: missing forbidden pattern {pattern}")
            ok = False
    boundary = data.get("originality_boundary", "").lower()
    if "does not claim" not in boundary:
        error("refinement visual identity validation: originality_boundary must disclaim readiness")
        ok = False
    return ok


def validate_isolation_audit() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-refinement-public-isolation-audit-v1.json")
    if not ISOLATION_REQUIRED.issubset(set(data)):
        error("refinement isolation audit: missing required top-level fields")
        ok = False
    expected = {
        "internal_prototype_location": f"{PROTO_REL}/",
        "route_registry_result": "not_registered_as_public_route",
        "sitemap_result": "not_in_sitemap",
        "homepage_link_result": "not_linked_from_homepage",
        "reference_page_link_result": "not_linked_from_reference_pages",
        "language_page_link_result": "not_linked_from_language_page",
        "public_navigation_result": "not_linked_from_public_navigation",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "overall_outcome": "refinement_public_isolation_validated",
    }
    for key, val in expected.items():
        if data.get(key) != val:
            error(f"refinement isolation audit: {key} must be {val}")
            ok = False
    return ok


def validate_static_audit() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-refinement-static-safety-audit-v1.json")
    if not STATIC_AUDIT_REQUIRED.issubset(set(data)):
        error("refinement static safety audit: missing required top-level fields")
        ok = False
    if data.get("overall_outcome") != "refinement_static_safety_validated":
        error("refinement static safety audit: invalid overall_outcome")
        ok = False
    for key in HTML_SAFETY_KEYS:
        if data.get("html_safety_results", {}).get(key) != "pass":
            error(f"refinement static safety audit: html {key} must pass")
            ok = False
    for key in CSS_SAFETY_KEYS:
        if data.get("css_safety_results", {}).get(key) != "pass":
            error(f"refinement static safety audit: css {key} must pass")
            ok = False
    for key in CAPABILITY_BLOCK_KEYS:
        if data.get("capability_block_results", {}).get(key) != "pass":
            error(f"refinement static safety audit: capability {key} must pass")
            ok = False
    for key in CONTENT_SAFETY_KEYS:
        if data.get("content_safety_results", {}).get(key) != "pass":
            error(f"refinement static safety audit: content {key} must pass")
            ok = False
    for key in FILE_SCOPE_KEYS:
        if data.get("file_scope_results", {}).get(key) != "pass":
            error(f"refinement static safety audit: file scope {key} must pass")
            ok = False
    return ok


def validate_prototype_files() -> bool:
    ok = True
    if not PROTO_DIR.is_dir():
        error(f"prototype directory must exist: {PROTO_REL}/")
        return False
    files = {p.name for p in PROTO_DIR.iterdir() if p.is_file()}
    if files != ALLOWED_FILES:
        error(f"prototype directory must contain only {sorted(ALLOWED_FILES)}")
        ok = False
    if not INDEX_PATH.is_file():
        return ok

    html = INDEX_PATH.read_text(encoding="utf-8")
    html_lower = html.lower()

    if 'href="prototype.css"' not in html and "href='prototype.css'" not in html:
        error("index.html must link to prototype.css with relative link")
        ok = False

    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        error("index.html: expected exactly one H1")
        ok = False
    if "Evidence Posture Workbench — Static Prototype" not in html:
        error("index.html: missing required H1 text")
        ok = False

    for stmt in REQUIRED_STATEMENTS:
        if stmt not in html:
            error("index.html: missing required statement")
            ok = False
    for zone in REQUIRED_ZONES:
        if zone not in html:
            error(f"index.html: missing zone {zone}")
            ok = False
    for concept in REQUIRED_CONCEPTS:
        if concept not in html:
            error(f"index.html: missing concept {concept}")
            ok = False
    for marker in STRENGTHENED_HTML_MARKERS:
        if marker not in html_lower:
            error(f"index.html: missing strengthened language: {marker}")
            ok = False

    for pattern, label in PROHIBITED_HTML_PATTERNS:
        if re.search(pattern, html, re.I):
            error(f"index.html: prohibited {label}")
            ok = False
    for pattern in PROHIBITED_CONTENT:
        for match in re.finditer(pattern, html_lower):
            start = max(0, match.start() - 80)
            if not NEGATION_CONTEXT.search(html_lower[start:match.start()]):
                error(f"index.html: prohibited content pattern {pattern}")
                ok = False
                break
    for m in re.finditer(r"\bscore(?:ing|s)?\b", html_lower):
        start = max(0, m.start() - 80)
        if not NEGATION_CONTEXT.search(html_lower[start:m.start()]):
            error("index.html: prohibited scoring language outside negation")
            ok = False
            break
    for term in ["detector", "scanner", "api", "analytics", "storage", "network", "classify", "detect", "scan"]:
        for m in re.finditer(rf"\b{term}\b", html_lower):
            start = max(0, m.start() - 80)
            if not NEGATION_CONTEXT.search(html_lower[start:m.start()]):
                error(f"index.html: prohibited {term} language outside negation")
                ok = False
                break
    return ok


def validate_prototype_css() -> bool:
    ok = True
    if not CSS_PATH.is_file():
        return ok
    css = CSS_PATH.read_text(encoding="utf-8")
    css_lower = css.lower()

    if "@import" in css_lower:
        error("prototype.css: @import not allowed")
        ok = False
    if re.search(r"url\s*\(\s*['\"]https?://", css_lower):
        error("prototype.css: external URL dependencies not allowed")
        ok = False

    for cls in STRENGTHENED_CSS_CLASSES:
        if cls not in css_lower:
            error(f"prototype.css: missing strengthened class {cls}")
            ok = False

    for concept in ["evidence-field", "chamber", "boundary", "provenance", "output-envelope"]:
        if concept.replace("-", "") not in css_lower.replace("-", ""):
            error(f"prototype.css: missing concept {concept}")
            ok = False

    forbidden = [
        "detector-dashboard", "upload-dropzone", "score-gauge", "fake-real",
        "verdict-green", "verdict-red", "saas-dashboard", "scanner",
    ]
    for cls in forbidden:
        if cls in css_lower:
            error(f"prototype.css: forbidden styling pattern {cls}")
            ok = False

    if "@media" not in css_lower:
        error("prototype.css: responsive/mobile rules required")
        ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False

    for route in routes:
        path = route.get("path", "").lower()
        if "internal_prototypes" in path or PROTO_REL.lower() in path:
            error("route-registry: prototype must not be registered as public route")
            ok = False

    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text.strip().lower() for el in root.findall(".//sm:loc", ns) if el.text]
        if not locs:
            locs = [el.text.strip().lower() for el in root.findall(".//{*}loc") if el.text]
        for loc in locs:
            if "internal_prototypes" in loc:
                error("sitemap.xml: prototype must not be included")
                ok = False
    except (ET.ParseError, OSError) as exc:
        error(f"sitemap.xml parse failed: {exc}")
        ok = False

    link_pattern = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for path in [
        ROOT / "index.html", ROOT / "language" / "index.html",
        ROOT / "reference" / "evidence-posture" / "index.html",
        ROOT / "reference" / "artifact-subject-separation" / "index.html",
    ]:
        if path.is_file() and link_pattern.search(path.read_text(encoding="utf-8")):
            error(f"{path.relative_to(ROOT)}: must not link to prototype")
            ok = False

    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
    ):
        error(f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING}")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Non-Public Static Workbench Prototype Refinement Validation Gate"),
        None,
    )
    if not gate:
        error("Non-Public Static Workbench Prototype Refinement Validation Gate missing")
        ok = False
    else:
        for field in [
            "required_before_non_public_static_workbench_visual_system_hardening",
            "required_before_any_interface_prototype_expansion",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"refinement validation gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is True:
            error("refinement validation gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        if "not authorize" not in notes and "does not authorize" not in notes:
            error("refinement validation gate notes must state non-authorization")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_prototype_refinement_validation" not in checks:
        error("reference-expansion-gate: refinement validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_refinement_validation_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by refinement validation alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    if "publisher_blocked_until_non_public_static_workbench_visual_system_hardening" not in blocked:
        error("reference-expansion-gate: publisher blocked until visual system hardening")
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
    if "validate_non_public_static_workbench_prototype_refinement_validation.py" not in content:
        error("validate_all.py must include refinement validation validator")
        ok = False
    doc = (ROOT / "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_REFINEMENT_VALIDATION_V1.md").read_text(encoding="utf-8")
    if "A refinement must be validated before it becomes the new prototype baseline." not in doc:
        error("refinement validation doc: missing governing principle")
        ok = False
    if "DEC-055" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-055 missing")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-prototype-refinement-validation-policy.json",
        "data/non-public-static-workbench-prototype-refinement-validation-results-v1.json",
        "data/non-public-static-workbench-prototype-refinement-visual-identity-validation-v1.json",
        "data/non-public-static-workbench-prototype-refinement-public-isolation-audit-v1.json",
        "data/non-public-static-workbench-prototype-refinement-static-safety-audit-v1.json",
        "data/non-public-static-workbench-prototype-refinement-policy.json",
        "data/non-public-static-workbench-prototype-refinement-plan-v1.json",
        "data/non-public-static-workbench-prototype-refinement-changelog-v1.json",
        "data/non-public-static-workbench-prototype-refinement-boundary-audit-v1.json",
        "data/non-public-static-workbench-prototype-v1-manifest.json",
        "data/non-public-static-workbench-prototype-v1-surface-map.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
    ]
    for rel in parse_paths:
        try:
            load_json(ROOT / rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"{rel} parse failed: {exc}")
            return 1

    for rel in [
        "sitemap.xml", "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "language/index.html",
        "_internal_prototypes/evidence-posture-workbench/index.html",
        "_internal_prototypes/evidence-posture-workbench/prototype.css",
    ]:
        if not (ROOT / rel).is_file():
            error(f"{rel} must exist and be readable")
            return 1

    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    checks = [
        validate_policy, validate_results, validate_visual_identity,
        validate_isolation_audit, validate_static_audit, validate_prototype_files,
        validate_prototype_css, validate_public_safety, validate_publisher_governance,
        validate_source_registry, validate_cross_file,
    ]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
