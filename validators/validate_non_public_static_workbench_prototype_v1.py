#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Prototype v1."""

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
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT,
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
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
INDEX_PATH = PROTO_DIR / "index.html"
CSS_PATH = PROTO_DIR / "prototype.css"
PROTO_REL = "_internal_prototypes/evidence-posture-workbench"

POLICY_REQUIRED = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "identity_principle", "allowed_prototype_actions", "prohibited_actions",
    "prototype_location", "static_only_policy", "non_public_policy",
    "non_authorization_rules", "last_reviewed",
}

MANIFEST_REQUIRED = {
    "prototype_id", "name", "version", "status", "maturity", "location", "files",
    "source_governance_refs", "visual_identity_refs", "allowed_next_phase",
    "prohibited_capabilities", "non_authorization_statement", "last_reviewed",
}

SURFACE_REQUIRED = {
    "surface_map_id", "name", "version", "status", "maturity", "prototype_surface",
    "public_surface_status", "route_status", "sitemap_status", "navigation_status",
    "current_public_surface", "non_authorization_statement", "last_reviewed",
}

CONTENT_REQUIRED = {
    "content_contract_id", "name", "version", "status", "maturity",
    "required_visible_statements", "allowed_static_content_patterns",
    "prohibited_static_content_patterns", "fictional_placeholder_policy",
    "non_authorization_statement", "last_reviewed",
}

AUDIT_REQUIRED = {
    "audit_id", "name", "version", "status", "maturity", "audited_files",
    "boundary_results", "public_surface_results", "capability_block_results",
    "overall_outcome", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_V1.md",
    "data/non-public-static-workbench-prototype-v1-policy.json",
    "data/non-public-static-workbench-prototype-v1-manifest.json",
    "data/non-public-static-workbench-prototype-v1-surface-map.json",
    "data/non-public-static-workbench-prototype-v1-static-content-contract.json",
    "data/non-public-static-workbench-prototype-v1-boundary-audit.json",
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
    "validators/validate_non_public_static_workbench_prototype_v1.py",
]

MANIFEST_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
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
    r"\bdetect(?:or|ion)?\b(?!or)",  # allow "detector" in negation context handled separately
]

NEGATION_CONTEXT = re.compile(r"\b(does not|do not|no|not|without)\b", re.I)
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade)\b", re.I)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-prototype-v1-policy.json"
    policy = load_json(path)
    if not POLICY_REQUIRED.issubset(set(policy)):
        error("prototype v1 policy: missing required top-level fields")
        ok = False
    if policy.get("status") != "governed_non_public_static_workbench_prototype_v1_policy":
        error("prototype v1 policy: invalid status")
        ok = False
    if policy.get("maturity") != "static_internal_prototype_only_no_engine_no_classifier_no_tool_no_public_route":
        error("prototype v1 policy: invalid maturity")
        ok = False
    if policy.get("prototype_location") != f"{PROTO_REL}/":
        error("prototype v1 policy: invalid prototype_location")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for term in ["javascript", "forms", "inputs", "upload", "scoring", "public_route_creation"]:
        if term.replace("_", " ") not in prohibited and term not in prohibited:
            error(f"prototype v1 policy: missing prohibited action {term}")
            ok = False
    blocked = " ".join(policy.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in ["public_workbench", "workbench_engine", "production_readiness"]:
        if term.replace("_", " ") not in blocked and term not in blocked:
            error(f"prototype v1 policy: non_authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("prototype v1 policy: numeric score found")
        ok = False
    return ok


def validate_manifest() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-v1-manifest.json")
    if not MANIFEST_REQUIRED.issubset(set(data)):
        error("manifest: missing required top-level fields")
        ok = False
    if data.get("status") != "non_public_static_workbench_prototype_v1_created":
        error("manifest: invalid status")
        ok = False
    if data.get("location") != f"{PROTO_REL}/":
        error("manifest: invalid location")
        ok = False
    if sorted(data.get("files", [])) != sorted(MANIFEST_FILES):
        error("manifest: files must be exactly index.html and prototype.css")
        ok = False
    next_phase = data.get("allowed_next_phase", "")
    if "Sprint 35" not in next_phase or "Prototype Validation" not in next_phase:
        error("manifest: allowed_next_phase must be Sprint 35 Prototype Validation")
        ok = False
    caps = {c.lower() for c in data.get("prohibited_capabilities", [])}
    for cap in ["public_route", "sitemap_entry", "engine", "classifier", "upload", "scoring"]:
        if cap.lower() not in caps:
            error(f"manifest: missing prohibited capability {cap}")
            ok = False
    return ok


def validate_surface_map() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-v1-surface-map.json")
    if not SURFACE_REQUIRED.issubset(set(data)):
        error("surface map: missing required top-level fields")
        ok = False
    if data.get("route_status") != "not_registered_as_public_route":
        error("surface map: invalid route_status")
        ok = False
    if data.get("sitemap_status") != "not_in_sitemap":
        error("surface map: invalid sitemap_status")
        ok = False
    if data.get("navigation_status") != "not_linked_from_public_navigation":
        error("surface map: invalid navigation_status")
        ok = False
    return ok


def validate_content_contract() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-v1-static-content-contract.json")
    if not CONTENT_REQUIRED.issubset(set(data)):
        error("content contract: missing required top-level fields")
        ok = False
    if not data.get("fictional_placeholder_policy"):
        error("content contract: missing fictional_placeholder_policy")
        ok = False
    return ok


def validate_boundary_audit() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-prototype-v1-boundary-audit.json")
    if not AUDIT_REQUIRED.issubset(set(data)):
        error("boundary audit: missing required top-level fields")
        ok = False
    if data.get("overall_outcome") != "non_public_static_workbench_prototype_v1_boundary_validated":
        error("boundary audit: invalid overall_outcome")
        ok = False
    for key in [
        "static_only_passed", "no_js_passed", "no_forms_inputs_passed", "no_upload_passed",
        "no_scoring_passed", "no_fake_real_passed", "no_generated_output_passed",
        "no_real_world_content_passed", "no_external_claims_passed",
        "evidence_field_identity_passed", "non_public_surface_passed",
    ]:
        if data.get("boundary_results", {}).get(key) != "pass":
            error(f"boundary audit: {key} must pass")
            ok = False
    for key in [
        "no_route_registry_entry", "no_sitemap_entry", "no_homepage_link",
        "no_public_reference_links", "no_public_navigation",
    ]:
        if data.get("public_surface_results", {}).get(key) != "pass":
            error(f"boundary audit public surface: {key} must pass")
            ok = False
    for key in [
        "no_engine", "no_classifier", "no_detector", "no_api", "no_analytics",
        "no_storage", "no_network_calls", "no_deployment_change",
    ]:
        if data.get("capability_block_results", {}).get(key) != "pass":
            error(f"boundary audit capability: {key} must pass")
            ok = False
    return ok


def validate_prototype_files() -> bool:
    ok = True
    if not PROTO_DIR.is_dir():
        error(f"prototype directory must exist: {PROTO_REL}/")
        return False
    if not INDEX_PATH.is_file():
        error("index.html must exist")
        ok = False
    if not CSS_PATH.is_file():
        error("prototype.css must exist")
        ok = False

    extra = [
        p for p in PROTO_DIR.iterdir()
        if p.is_file() and p.name not in {"index.html", "prototype.css"}
    ]
    if extra:
        error(f"unexpected files in prototype directory: {[p.name for p in extra]}")
        ok = False

    if not INDEX_PATH.is_file():
        return ok

    html = INDEX_PATH.read_text(encoding="utf-8")
    html_lower = html.lower()

    if 'href="prototype.css"' not in html and "href='prototype.css'" not in html:
        error("index.html must link to prototype.css with relative link")
        ok = False

    h1_count = len(re.findall(r"<h1\b", html, re.I))
    if h1_count != 1:
        error(f"index.html: expected exactly one H1, found {h1_count}")
        ok = False
    if "Evidence Posture Workbench — Static Prototype" not in html:
        error("index.html: missing required H1 text")
        ok = False

    for stmt in REQUIRED_STATEMENTS:
        if stmt not in html:
            error(f"index.html: missing required statement")
            ok = False

    for zone in REQUIRED_ZONES:
        if zone not in html:
            error(f"index.html: missing zone {zone}")
            ok = False

    for concept in REQUIRED_CONCEPTS:
        if concept not in html:
            error(f"index.html: missing concept {concept}")
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
        context = html_lower[start:m.start()]
        if not NEGATION_CONTEXT.search(context):
            error("index.html: prohibited scoring language outside negation")
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
    if re.search(r"@font-face", css_lower):
        error("prototype.css: external font import not allowed")
        ok = False

    forbidden_classes = [
        "detector-dashboard", "upload-dropzone", "score-gauge",
        "fake-real", "verdict-green", "verdict-red", "saas-dashboard",
    ]
    for cls in forbidden_classes:
        if cls in css_lower:
            error(f"prototype.css: forbidden styling pattern {cls}")
            ok = False

    required_concepts = [
        "evidence-field", "chamber", "boundary", "provenance", "output-envelope",
    ]
    for concept in required_concepts:
        if concept.replace("-", "") not in css_lower.replace("-", ""):
            error(f"prototype.css: missing concept {concept}")
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

    proto_path = f"/{PROTO_REL}/"
    proto_rel = PROTO_REL.lower()
    for route in routes:
        path = route.get("path", "").lower()
        if "internal_prototypes" in path or proto_rel in path:
            error("route-registry: prototype must not be registered as public route")
            ok = False

    try:
        locs = []
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
    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION}, "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT}, or "
            f"{PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Non-Public Static Workbench Prototype v1 Gate"),
        None,
    )
    if not gate:
        error("Non-Public Static Workbench Prototype v1 Gate missing")
        ok = False
    else:
        for field in [
            "required_before_non_public_static_workbench_prototype_validation",
            "required_before_any_interface_prototype_expansion",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"prototype v1 gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is True:
            error("prototype v1 gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        if "not authorize" not in notes and "does not authorize" not in notes:
            error("prototype v1 gate notes must state non-authorization")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_prototype_v1" not in checks:
        error("reference-expansion-gate: prototype v1 required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_static_prototype_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by static prototype alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    if "publisher_blocked_until_non_public_static_workbench_prototype_validation" not in blocked:
        error("reference-expansion-gate: publisher blocked until prototype validation")
        ok = False
    if "publisher_blocked_until_non_public_static_workbench_prototype_refinement_validation" not in blocked:
        error("reference-expansion-gate: publisher blocked until prototype refinement validation")
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
    if "validate_non_public_static_workbench_prototype_v1.py" not in content:
        error("validate_all.py must include prototype v1 validator")
        ok = False
    doc = (ROOT / "NON_PUBLIC_STATIC_WORKBENCH_PROTOTYPE_V1.md").read_text(encoding="utf-8")
    if "A static prototype may show future form. It must not create future function." not in doc:
        error("prototype doc: missing governing principle")
        ok = False
    if "DEC-051" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-051 missing")
        ok = False

    html = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else ""
    contract = load_json(ROOT / "data" / "non-public-static-workbench-prototype-v1-static-content-contract.json")
    for stmt in contract.get("required_visible_statements", []):
        if stmt not in html:
            error("content contract statements must appear in index.html")
            ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-prototype-v1-policy.json",
        "data/non-public-static-workbench-prototype-v1-manifest.json",
        "data/non-public-static-workbench-prototype-v1-surface-map.json",
        "data/non-public-static-workbench-prototype-v1-static-content-contract.json",
        "data/non-public-static-workbench-prototype-v1-boundary-audit.json",
        "data/non-public-static-workbench-prototype-governance-v1.json",
        "data/non-public-static-workbench-prototype-location-policy.json",
        "data/non-public-static-workbench-prototype-visual-identity-contract.json",
        "data/non-public-static-workbench-prototype-safety-boundaries.json",
        "data/non-public-static-workbench-prototype-review-gates.json",
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

    if not INDEX_PATH.is_file() or not CSS_PATH.is_file():
        error("prototype files must exist")
        return 1

    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    checks = [
        validate_policy,
        validate_manifest,
        validate_surface_map,
        validate_content_contract,
        validate_boundary_audit,
        validate_prototype_files,
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
