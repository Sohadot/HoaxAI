#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Prototype Refinement v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION,
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,

    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
INDEX_PATH = PROTO_DIR / "index.html"
CSS_PATH = PROTO_DIR / "prototype.css"
PROTO_REL = "_internal_prototypes/evidence-posture-workbench"

ALLOWED_FILES = {
    "index.html",
    "prototype.css",
}

POLICY_REQUIRED = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "identity_principle", "allowed_refinement_actions", "prohibited_actions",
    "allowed_files", "refinement_scope", "non_authorization_rules", "last_reviewed",
}

PLAN_REQUIRED = {
    "refinement_plan_id", "name", "version", "status", "maturity", "allowed_files",
    "refinement_targets", "forbidden_changes", "expected_outcome", "last_reviewed",
}

CHANGELOG_REQUIRED = {
    "changelog_id", "name", "version", "status", "maturity", "changed_files",
    "refinement_entries", "unchanged_boundaries", "last_reviewed",
}

AUDIT_REQUIRED = {
    "audit_id", "name", "version", "status", "maturity", "audited_files",
    "boundary_results", "visual_identity_results", "public_surface_results",
    "capability_block_results", "overall_outcome", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_REFINEMENT_V1.md",
    "data/non-public-static-workbench-prototype-refinement-policy.json",
    "data/non-public-static-workbench-prototype-refinement-plan-v1.json",
    "data/non-public-static-workbench-prototype-refinement-changelog-v1.json",
    "data/non-public-static-workbench-prototype-refinement-boundary-audit-v1.json",
    "validators/validate_non_public_static_workbench_prototype_refinement.py",
]

PROHIBITED_ACTIONS = [
    "new_prototype_files", "prototype_expansion", "public_route_creation", "sitemap_expansion",
    "public_navigation_link", "interface_behavior", "javascript", "forms", "inputs", "upload",
    "scoring", "fake_real_output", "generated_output", "engine", "classifier", "detector",
    "api", "analytics", "storage", "network_calls", "monetization", "dns", "cloudflare",
    "custom_domain_launch", "deployment_changes", "external_factual_claims", "subject_accusation",
]

REFINEMENT_TARGETS = [
    "evidence_chamber_clarity", "governed_evidence_field_depth", "artifact_first_structure",
    "boundary_first_layout", "provenance_shadow_visibility", "missing_context_as_absence",
    "not_assessable_protected_restraint", "refusal_as_governance", "output_envelope_containment",
    "verification_path_legibility", "accessibility_semantics", "responsive_stability",
    "anti_detector_differentiation", "anti_upload_dashboard_differentiation",
    "anti_scoring_dashboard_differentiation",
]

FORBIDDEN_CHANGES = [
    "new_files", "new_routes", "sitemap_expansion", "public_links", "javascript", "forms",
    "inputs", "upload", "scoring", "fake_real_output", "generated_output", "engine_behavior",
    "classifier_behavior", "api", "analytics", "deployment_change",
]

REFINEMENT_ENTRIES = [
    "html_semantic_refinement", "evidence_chamber_language_refinement",
    "artifact_boundary_clarity_refinement", "static_zone_copy_refinement",
    "css_evidence_field_refinement", "css_boundary_rail_refinement",
    "css_provenance_shadow_refinement", "css_responsive_refinement",
]

UNCHANGED_BOUNDARIES = [
    "no_new_prototype_files", "no_public_route", "no_sitemap_entry", "no_public_navigation",
    "no_js", "no_forms", "no_inputs", "no_upload", "no_scoring", "no_fake_real",
    "no_engine", "no_classifier", "no_api", "no_analytics", "no_deployment_change",
]

BOUNDARY_KEYS = [
    "only_allowed_files_modified", "no_additional_prototype_files", "static_only_preserved",
    "no_js_preserved", "no_forms_inputs_preserved", "no_upload_preserved", "no_scoring_preserved",
    "no_fake_real_preserved", "no_generated_output_preserved", "no_real_world_content_preserved",
    "no_external_claims_preserved",
]

VISUAL_KEYS = [
    "evidence_chamber_strengthened", "governed_evidence_field_strengthened",
    "artifact_first_structure_strengthened", "boundary_first_layout_strengthened",
    "provenance_shadow_strengthened", "missing_context_as_absence_strengthened",
    "not_assessable_restraint_strengthened", "refusal_as_governance_strengthened",
    "output_envelope_containment_strengthened", "anti_detector_pattern_preserved",
]

PUBLIC_SURFACE_KEYS = [
    "no_route_registry_entry", "no_sitemap_entry", "no_homepage_link",
    "no_public_reference_links", "no_language_page_link", "no_public_navigation",
]

CAPABILITY_KEYS = [
    "no_engine", "no_classifier", "no_detector", "no_api", "no_analytics",
    "no_storage", "no_network_calls", "no_deployment_change",
]

REQUIRED_ZONES = [
    "Workbench Boundary Header",
    "Artifact Context Zone",
    "Source and Provenance Context Zone",
    "Missing Information Zone",
    "State Routing Zone",
    "Refusal and Boundary Zone",
    "Output Envelope Preview Zone",
    "Verification Questions Zone",
]

REQUIRED_CONCEPTS = [
    "Evidence Chamber",
    "Governed Evidence Field",
    "Artifact–Subject Boundary",
    "Provenance Shadow",
    "Missing Context",
    "Not Assessable",
    "Refusal Gate",
    "Output Envelope",
    "Verification Path",
]

REQUIRED_STATEMENTS = [
    "Internal static prototype. Non-public web surface. No engine. No classifier. No upload. No scoring. No verdict.",
    "This static prototype explores the Evidence Chamber interface direction.",
    "Evidence is structured before it is believed, escalated, published, or judged.",
]

STRENGTHENED_HTML_MARKERS = [
    "governed reasoning chamber",
    "Artifact-first structure",
    "confidence-limiting absence",
    "structural condition",
    "protected restraint",
    "Refusal is governance",
    "contained, limited, and non-verdict",
    "inquiry paths",
]

REQUIRED_CSS_CONCEPTS = [
    "evidence-chamber-frame", "governed-evidence-field", "boundary-rail",
    "provenance-shadow", "missing-context-absence", "not-assessable-restraint",
    "refusal-gate", "output-envelope",
]

PROHIBITED_HTML_PATTERNS = [
    (r"<script\b", "script tag"),
    (r"<form\b", "form element"),
    (r"<input\b", "input element"),
    (r"<textarea\b", "textarea element"),
    (r"type\s*=\s*['\"]file['\"]", "file input"),
    (r"<button\b", "button element"),
]

PROHIBITED_CONTENT = [
    r"\btry it now\b",
    r"\bsubmit evidence\b",
    r"\bupload now\b",
    r"\bfake\b.*\breal\b",
    r"\breal score\b",
    r"\b\d+\s*%\b",
    r"\bverified\b",
    r"\bcertified\b",
]

NEGATION_CONTEXT = re.compile(r"\b(does not|do not|no|not|without)\b", re.I)
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-prototype-refinement-policy.json"
    policy = load_json(path)
    if not POLICY_REQUIRED.issubset(set(policy)):
        error("refinement policy: missing required top-level fields")
        ok = False
    if policy.get("status") != "governed_non_public_static_workbench_prototype_refinement_policy":
        error("refinement policy: invalid status")
        ok = False
    if policy.get("maturity") != "static_internal_refinement_only_no_engine_no_classifier_no_tool_no_public_route":
        error("refinement policy: invalid maturity")
        ok = False
    allowed = sorted(policy.get("allowed_files", []))
    expected = sorted([
        f"{PROTO_REL}/index.html",
        f"{PROTO_REL}/prototype.css",
    ])
    if allowed != expected:
        error("refinement policy: allowed_files must be exactly index.html and prototype.css")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"refinement policy: missing prohibited action {action}")
            ok = False
    blocked = " ".join(policy.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in ["public_workbench", "prototype_expansion_beyond_allowed_files", "production_readiness"]:
        if term.replace("_", " ") not in blocked and term not in blocked:
            error(f"refinement policy: non_authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("refinement policy: numeric score found")
        ok = False
    return ok


def validate_plan() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-refinement-plan-v1.json")
    if not PLAN_REQUIRED.issubset(set(data)):
        error("refinement plan: missing required top-level fields")
        ok = False
    targets = data.get("refinement_targets", [])
    for target in REFINEMENT_TARGETS:
        if target not in targets:
            error(f"refinement plan: missing target {target}")
            ok = False
    forbidden = data.get("forbidden_changes", [])
    for change in FORBIDDEN_CHANGES:
        if change not in forbidden:
            error(f"refinement plan: missing forbidden change {change}")
            ok = False
    if data.get("expected_outcome") != "non_public_static_prototype_refined_with_boundaries_preserved":
        error("refinement plan: invalid expected_outcome")
        ok = False
    return ok


def validate_changelog() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-refinement-changelog-v1.json")
    if not CHANGELOG_REQUIRED.issubset(set(data)):
        error("refinement changelog: missing required top-level fields")
        ok = False
    changed = sorted(data.get("changed_files", []))
    expected = sorted([f"{PROTO_REL}/index.html", f"{PROTO_REL}/prototype.css"])
    if changed != expected:
        error("refinement changelog: changed_files must be exactly index.html and prototype.css")
        ok = False
    entries = data.get("refinement_entries", [])
    for entry in REFINEMENT_ENTRIES:
        if entry not in entries:
            error(f"refinement changelog: missing entry {entry}")
            ok = False
    boundaries = data.get("unchanged_boundaries", [])
    for boundary in UNCHANGED_BOUNDARIES:
        if boundary not in boundaries:
            error(f"refinement changelog: missing unchanged boundary {boundary}")
            ok = False
    return ok


def validate_boundary_audit() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-refinement-boundary-audit-v1.json")
    if not AUDIT_REQUIRED.issubset(set(data)):
        error("refinement boundary audit: missing required top-level fields")
        ok = False
    if data.get("overall_outcome") != "non_public_static_prototype_refinement_boundary_validated":
        error("refinement boundary audit: invalid overall_outcome")
        ok = False
    audited = sorted(data.get("audited_files", []))
    expected = sorted([f"{PROTO_REL}/index.html", f"{PROTO_REL}/prototype.css"])
    if audited != expected:
        error("refinement boundary audit: audited_files mismatch")
        ok = False
    for key in BOUNDARY_KEYS:
        if data.get("boundary_results", {}).get(key) != "pass":
            error(f"refinement boundary audit: boundary {key} must pass")
            ok = False
    for key in VISUAL_KEYS:
        if data.get("visual_identity_results", {}).get(key) != "pass":
            error(f"refinement boundary audit: visual {key} must pass")
            ok = False
    for key in PUBLIC_SURFACE_KEYS:
        if data.get("public_surface_results", {}).get(key) != "pass":
            error(f"refinement boundary audit: public surface {key} must pass")
            ok = False
    for key in CAPABILITY_KEYS:
        if data.get("capability_block_results", {}).get(key) != "pass":
            error(f"refinement boundary audit: capability {key} must pass")
            ok = False
    return ok


def validate_prototype_directory() -> bool:
    ok = True
    if not PROTO_DIR.is_dir():
        error(f"prototype directory must exist: {PROTO_REL}/")
        return False
    files = {p.name for p in PROTO_DIR.iterdir() if p.is_file()}
    if files != ALLOWED_FILES:
        error(f"prototype directory must contain only {sorted(ALLOWED_FILES)}, got {sorted(files)}")
        ok = False
    return ok


def validate_prototype_html() -> bool:
    ok = True
    if not INDEX_PATH.is_file():
        return False
    html = INDEX_PATH.read_text(encoding="utf-8")
    html_lower = html.lower()

    h1_count = len(re.findall(r"<h1\b", html, re.I))
    if h1_count != 1:
        error(f"index.html: expected exactly one H1, found {h1_count}")
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
        if marker.lower() not in html_lower:
            error(f"index.html: missing strengthened language marker: {marker}")
            ok = False

    for pattern, label in PROHIBITED_HTML_PATTERNS:
        if re.search(pattern, html, re.I):
            error(f"index.html: prohibited {label}")
            ok = False

    for pattern in PROHIBITED_CONTENT:
        for match in re.finditer(pattern, html_lower):
            start = max(0, match.start() - 80)
            context = html_lower[start:match.start()]
            if not NEGATION_CONTEXT.search(context):
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
        return False
    css = CSS_PATH.read_text(encoding="utf-8")
    css_lower = css.lower()

    if "@import" in css_lower:
        error("prototype.css: @import not allowed")
        ok = False
    if re.search(r"url\s*\(\s*['\"]https?://", css_lower):
        error("prototype.css: external URL dependencies not allowed")
        ok = False

    for concept in REQUIRED_CSS_CONCEPTS:
        if concept not in css_lower:
            error(f"prototype.css: missing visual identity class {concept}")
            ok = False

    forbidden = [
        "detector-dashboard", "upload-dropzone", "score-gauge",
        "fake-real", "verdict-green", "verdict-red", "saas-dashboard", "scanner",
    ]
    for cls in forbidden:
        if cls in css_lower:
            error(f"prototype.css: forbidden styling pattern {cls}")
            ok = False

    if "@media" not in css_lower:
        error("prototype.css: responsive/mobile rules required")
        ok = False

    if css_lower.count("#000") > 0 or "background: #0" in css_lower.replace(" ", ""):
        if "background-color: #0" in css_lower.replace(" ", ""):
            error("prototype.css: black cyber dashboard default not allowed")
            ok = False

    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False

    proto_rel = PROTO_REL.lower()
    for route in routes:
        path = route.get("path", "").lower()
        if "internal_prototypes" in path or proto_rel in path:
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

    public_html_files = [
        ROOT / "index.html",
        ROOT / "language" / "index.html",
        ROOT / "reference" / "evidence-posture" / "index.html",
        ROOT / "reference" / "artifact-subject-separation" / "index.html",
    ]
    link_pattern = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for path in public_html_files:
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,

    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION} "
            f"or {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Non-Public Static Workbench Prototype Refinement Gate"),
        None,
    )
    if not gate:
        error("Non-Public Static Workbench Prototype Refinement Gate missing")
        ok = False
    else:
        for field in [
            "required_before_non_public_static_workbench_prototype_refinement_validation",
            "required_before_any_interface_prototype_expansion",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"refinement gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is True:
            error("refinement gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        if "not authorize" not in notes and "does not authorize" not in notes:
            error("refinement gate notes must state non-authorization")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_prototype_refinement" not in checks:
        error("reference-expansion-gate: prototype refinement required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_prototype_refinement_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by prototype refinement alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    if "publisher_blocked_until_non_public_static_workbench_prototype_refinement_validation" not in blocked:
        error("reference-expansion-gate: publisher blocked until prototype refinement validation")
        ok = False
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
    if "validate_non_public_static_workbench_prototype_refinement.py" not in content:
        error("validate_all.py must include prototype refinement validator")
        ok = False
    doc = (ROOT / "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_REFINEMENT_V1.md").read_text(encoding="utf-8")
    if "Prototype refinement may deepen conceptual form. It must not increase operational capability." not in doc:
        error("refinement doc: missing governing principle")
        ok = False
    if "DEC-054" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-054 missing")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-prototype-refinement-policy.json",
        "data/non-public-static-workbench-prototype-refinement-plan-v1.json",
        "data/non-public-static-workbench-prototype-refinement-changelog-v1.json",
        "data/non-public-static-workbench-prototype-refinement-boundary-audit-v1.json",
        "data/non-public-static-workbench-prototype-validation-results-v1.json",
        "data/non-public-static-workbench-prototype-v1-manifest.json",
        "data/non-public-static-workbench-prototype-v1-surface-map.json",
        "data/non-public-static-workbench-prototype-v1-static-content-contract.json",
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

    read_paths = [
        "sitemap.xml", "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "language/index.html",
        "_internal_prototypes/evidence-posture-workbench/index.html",
        "_internal_prototypes/evidence-posture-workbench/prototype.css",
    ]
    for rel in read_paths:
        if not (ROOT / rel).is_file():
            error(f"{rel} must exist and be readable")
            return 1

    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    checks = [
        validate_policy,
        validate_plan,
        validate_changelog,
        validate_boundary_audit,
        validate_prototype_directory,
        validate_prototype_html,
        validate_prototype_css,
        validate_public_safety,
        validate_publisher_governance,
        validate_source_registry,
        validate_cross_file,
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
