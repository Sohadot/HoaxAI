#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Visual System Hardening Validation v1."""

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
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK,
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
MATURE = "validation_only_hardened_static_internal_visual_system_no_engine_no_classifier_no_public_route"

VALIDATION_DIMENSIONS = [
    "Visual Hardening Policy Integrity", "Token Contract Integrity", "Pattern Registry Integrity",
    "Anti-Pattern Audit Integrity", "Boundary Audit Integrity", "Allowed File Scope Integrity",
    "Prototype File Count Integrity", "Static HTML Integrity", "Static CSS Integrity", "CSS Token Presence",
    "Evidence Field Hardening", "Evidence Chamber Hardening", "Boundary Rail Hardening",
    "Provenance Shadow Hardening", "Missing Context Absence Hardening", "Not-Assessable Restraint Hardening",
    "Refusal Gate Hardening", "Output Envelope Hardening", "Verification Path Hardening",
    "Anti-Detector Identity Preservation", "Anti-Upload Dashboard Preservation", "Anti-Scoring Dashboard Preservation",
    "Anti-SaaS Dashboard Preservation", "No JavaScript", "No Forms or Inputs", "No Upload Surface",
    "No Scoring Surface", "No Fake/Real Verdict Surface", "No Generated Output Surface",
    "No API/Network/Storage Behavior", "No Analytics", "Public Route Exclusion", "Sitemap Exclusion",
    "Public Navigation Exclusion", "Homepage Link Exclusion", "Reference Page Link Exclusion",
    "Language Page Link Exclusion", "Accessibility and Semantic Structure", "Mobile/Responsive Stability",
    "No Real-World Content", "No External Factual Claims", "Non-Authorization Rule Integrity",
    "Publisher Gate Alignment", "Reference Expansion Gate Alignment", "Python Cache Exclusion",
]
TOKEN_FAMILIES = [
    "background_field", "chamber_surface", "chamber_edge", "graphite_text", "muted_text",
    "boundary_accent", "provenance_line", "provenance_shadow", "absence_field",
    "not_assessable_surface", "refusal_surface", "output_envelope_surface",
    "verification_path_line", "subtle_rule", "focus_ring", "mobile_spacing",
]
TOKEN_PRINCIPLES = [
    "tokens_are_local_to_prototype_css", "tokens_are_conceptual_not_decorative",
    "tokens_support_governed_evidence_field", "tokens_support_evidence_chamber_identity",
    "tokens_do_not_imply_scoring_verdict_upload_classifier_or_detector",
    "tokens_do_not_depend_on_external_assets",
]
FORBIDDEN_TOKEN_PATTERNS = [
    "black_cyber_dashboard_default", "neon_detector_palette", "red_green_verdict_system",
    "score_severity_palette", "upload_dashboard_cta_palette", "saas_analytics_gradient_system",
    "external_font_dependency", "external_url_dependency",
]
PATTERNS = [
    "Evidence Field", "Evidence Chamber", "Boundary Rail", "Provenance Shadow",
    "Missing Context Absence", "Not-Assessable Restraint", "Refusal Gate",
    "Output Envelope", "Verification Path",
]
ANTIPATTERNS = [
    "detector_dashboard_blocked", "scanner_ui_blocked", "upload_dashboard_blocked",
    "red_green_fake_real_interface_blocked", "truth_meter_blocked", "risk_gauge_blocked",
    "probability_meter_blocked", "forensic_game_interface_blocked", "policing_dashboard_blocked",
    "saas_analytics_dashboard_blocked", "product_landing_page_cta_blocked",
    "try_it_now_interface_blocked", "black_cyber_dashboard_default_blocked",
]
REQUIRED_CLASSES = [
    "evidence-field", "evidence-chamber", "chamber-frame", "boundary-rail",
    "provenance-shadow", "missing-context-absence", "not-assessable-restraint",
    "refusal-gate", "output-envelope", "verification-path",
]
REQUIRED_ZONES = [
    "Workbench Boundary Header", "Artifact Context Zone", "Source and Provenance Context Zone",
    "Missing Information Zone", "State Routing Zone", "Refusal and Boundary Zone",
    "Output Envelope Preview Zone", "Verification Questions Zone",
]
REQUIRED_CONCEPTS = [
    "Evidence Chamber", "Governed Evidence Field", "Artifact–Subject Boundary",
    "Provenance Shadow", "Missing Context", "Not Assessable", "Refusal Gate",
    "Output Envelope", "Verification Path",
]
REQUIRED_SOURCE_LOCATIONS = [
    "NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING_VALIDATION_V1.md",
    "data/non-public-static-workbench-visual-system-hardening-validation-policy.json",
    "data/non-public-static-workbench-visual-system-hardening-validation-results-v1.json",
    "data/non-public-static-workbench-visual-system-token-validation-v1.json",
    "data/non-public-static-workbench-visual-system-pattern-validation-v1.json",
    "data/non-public-static-workbench-visual-system-antipattern-validation-v1.json",
    "data/non-public-static-workbench-visual-system-public-isolation-audit-v1.json",
    "data/non-public-static-workbench-visual-system-static-safety-audit-v1.json",
    "validators/validate_non_public_static_workbench_visual_system_hardening_validation.py",
]
POLICY_REQUIRED = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "identity_principle", "allowed_validation_actions", "prohibited_actions",
    "validation_scope", "correction_policy", "non_authorization_rules", "last_reviewed",
}
PROHIBITED_ACTIONS = [
    "modifying prototype files", "new prototype files", "prototype expansion", "public route creation",
    "sitemap expansion", "public navigation link", "interface behavior", "javascript", "forms",
    "inputs", "upload", "scoring", "fake/real output", "generated output", "engine",
    "classifier", "detector", "api", "analytics", "storage", "network calls", "monetization",
    "dns", "cloudflare", "custom domain launch", "deployment changes", "external factual claims",
    "subject accusation", "python cache file commit",
]
NEGATION_CONTEXT = re.compile(r"\b(does not|do not|no|not|without)\b", re.I)
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
READINESS_FORBIDDEN = re.compile(
    r"\b(prototype.?expansion.?ready|public.?workbench.?ready|engine.?ready|classifier.?ready|"
    r"tool.?ready|deployment.?ready|public.?release.?ready|production.?ready)\b",
    re.I,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def text_contains_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower().replace("_", " ") in text or item.lower() in text for item in required)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-visual-system-hardening-validation-policy.json"
    data = load_json(path)
    if not POLICY_REQUIRED.issubset(data):
        error("validation policy: missing required top-level fields")
        ok = False
    if data.get("status") != "governed_non_public_static_workbench_visual_system_hardening_validation_policy":
        error("validation policy: invalid status")
        ok = False
    if data.get("maturity") != MATURE:
        error("validation policy: invalid maturity")
        ok = False
    if not text_contains_all(data.get("prohibited_actions", []), PROHIBITED_ACTIONS):
        error("validation policy: missing prohibited actions")
        ok = False
    correction = data.get("correction_policy", "").lower()
    for term in ["prototype files", "add files", "routes", "sitemap", "public links", "js", "forms", "inputs", "upload", "scoring", "engine", "classifier", "api", "analytics", "deployment", "python cache"]:
        if term not in correction:
            error(f"validation policy: correction_policy must block {term}")
            ok = False
    blocked = " ".join(data.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in ["public_workbench", "engine", "classifier", "upload", "scoring", "api", "routes", "sitemap", "deployment", "dns", "cloudflare", "custom_domain_launch", "public_tool_behavior", "prototype_expansion", "production_readiness", "python_cache_commit"]:
        if term.lower() not in blocked and term.lower().replace("_", " ") not in blocked:
            error(f"validation policy: non_authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("validation policy: numeric score, grade, percentage, or SEO score found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-visual-system-hardening-validation-results-v1.json"
    data = load_json(path)
    dims = [d.get("dimension") for d in data.get("validation_dimensions", [])]
    if dims != VALIDATION_DIMENSIONS:
        error("validation results: expected all 45 validation dimensions in order")
        ok = False
    if data.get("overall_result") != "non_public_static_visual_system_hardening_validated":
        error("validation results: invalid overall_result")
        ok = False
    if data.get("python_cache_result") != "python_cache_excluded":
        error("validation results: python_cache_result must be python_cache_excluded")
        ok = False
    text = path.read_text(encoding="utf-8")
    if NUMERIC_SCORE_PATTERN.search(text) or READINESS_FORBIDDEN.search(text):
        error("validation results: prohibited score or readiness implication found")
        ok = False
    return ok


def validate_token_validation() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-token-validation-v1.json")
    if data.get("status") != "non_public_static_visual_system_token_validated":
        error("token validation: invalid status")
        ok = False
    if data.get("maturity") != "token_validation_only_no_public_interface_no_engine":
        error("token validation: invalid maturity")
        ok = False
    if data.get("overall_result") != "token_system_validated":
        error("token validation: invalid overall_result")
        ok = False
    for key in TOKEN_FAMILIES:
        if key not in data.get("token_family_results", {}):
            error(f"token validation: missing family {key}")
            ok = False
    for key in TOKEN_PRINCIPLES:
        if key not in data.get("token_principle_results", {}):
            error(f"token validation: missing principle {key}")
            ok = False
    for key in FORBIDDEN_TOKEN_PATTERNS:
        if key not in data.get("forbidden_token_pattern_results", {}):
            error(f"token validation: missing forbidden token pattern {key}")
            ok = False
    if data.get("css_observation_result") != "css_tokens_observed_without_external_dependencies":
        error("token validation: invalid css_observation_result")
        ok = False
    return ok


def validate_pattern_validation() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-pattern-validation-v1.json")
    if data.get("status") != "non_public_static_visual_pattern_system_validated":
        error("pattern validation: invalid status")
        ok = False
    if data.get("maturity") != "pattern_validation_only_no_engine_no_classifier_no_public_route":
        error("pattern validation: invalid maturity")
        ok = False
    if data.get("overall_result") != "pattern_system_validated":
        error("pattern validation: invalid overall_result")
        ok = False
    names = [p.get("pattern_name") for p in data.get("pattern_results", [])]
    if names != PATTERNS:
        error("pattern validation: expected exactly 9 required patterns")
        ok = False
    op = data.get("operational_boundary_results", {})
    for key in ["engine", "classifier", "upload", "scoring", "fake_real_output", "API", "routes", "sitemap", "deployment", "DNS", "Cloudflare", "public_tool_behavior"]:
        expected = "no_pattern_authorizes_" + key
        if expected not in op:
            error(f"pattern validation: missing operational boundary {expected}")
            ok = False
    return ok


def validate_antipattern_validation() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-antipattern-validation-v1.json")
    if data.get("status") != "non_public_static_visual_antipatterns_validated":
        error("anti-pattern validation: invalid status")
        ok = False
    if data.get("maturity") != "antipattern_validation_only_no_detector_no_dashboard_no_public_tool":
        error("anti-pattern validation: invalid maturity")
        ok = False
    if data.get("overall_result") != "visual_antipattern_blocking_validated":
        error("anti-pattern validation: invalid overall_result")
        ok = False
    for key in ANTIPATTERNS:
        if key not in data.get("blocked_antipattern_results", {}):
            error(f"anti-pattern validation: missing {key}")
            ok = False
    if data.get("css_language_result") != "css_language_preserves_evidence_field_not_detector_dashboard":
        error("anti-pattern validation: invalid css_language_result")
        ok = False
    if data.get("html_language_result") != "html_language_preserves_evidence_chamber_not_detector_tool":
        error("anti-pattern validation: invalid html_language_result")
        ok = False
    return ok


def validate_isolation_and_static_audits() -> bool:
    ok = True
    iso = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-public-isolation-audit-v1.json")
    expected = {
        "route_registry_result": "not_registered_as_public_route",
        "sitemap_result": "not_in_sitemap",
        "homepage_link_result": "not_linked_from_homepage",
        "reference_page_link_result": "not_linked_from_reference_pages",
        "language_page_link_result": "not_linked_from_language_page",
        "public_navigation_result": "not_linked_from_public_navigation",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "overall_outcome": "hardening_public_isolation_validated",
    }
    for key, value in expected.items():
        if iso.get(key) != value:
            error(f"public isolation audit: {key} must be {value}")
            ok = False
    stat = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-static-safety-audit-v1.json")
    if stat.get("overall_outcome") != "hardening_static_safety_validated":
        error("static safety audit: invalid overall_outcome")
        ok = False
    for group, keys in {
        "html_safety_results": ["no_script_tags", "no_forms", "no_inputs", "no_textarea", "no_file_inputs", "no_buttons", "no_upload_controls", "no_generated_output_regions", "no_external_scripts", "no_external_libraries"],
        "css_safety_results": ["no_imports", "no_external_urls", "no_upload_dropzone_styling", "no_scoring_gauge_styling", "no_red_green_verdict_styling", "no_detector_scanner_naming", "evidence_field_classes_present", "chamber_boundary_classes_present", "provenance_shadow_classes_present", "output_envelope_classes_present", "responsive_rules_present", "visual_tokens_present"],
        "capability_block_results": ["no_engine", "no_classifier", "no_detector", "no_upload", "no_scoring", "no_fake_real", "no_api", "no_analytics", "no_storage", "no_network_calls", "no_deployment_change"],
        "content_safety_results": ["no_real_people", "no_real_companies", "no_real_institutions", "no_real_brands", "no_current_events", "no_political_events", "no_accusations", "no_external_factual_claims", "no_generated_analysis", "no_verified_certified_claims"],
        "file_scope_results": ["only_index_and_css_in_prototype_directory", "no_additional_prototype_files", "no_new_prototype_directories"],
        "python_cache_results": ["no_pycache_tracked", "no_pyc_staged", "no_python_cache_committed"],
    }.items():
        for key in keys:
            if key not in stat.get(group, {}):
                error(f"static safety audit: missing {group}.{key}")
                ok = False
    return ok


def validate_prototype_read_only_state() -> bool:
    ok = True
    if not PROTO_DIR.is_dir():
        error("prototype directory missing")
        return False
    files = {p.name for p in PROTO_DIR.iterdir() if p.is_file()}
    if files != ALLOWED_FILES:
        error("prototype directory must contain only index.html and prototype.css")
        ok = False
    html = INDEX_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    html_lower = html.lower()
    css_lower = css.lower()
    if 'href="prototype.css"' not in html and "href='prototype.css'" not in html:
        error("index.html must link only to prototype.css using a relative link")
        ok = False
    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        error("index.html: expected exactly one H1")
        ok = False
    if "Evidence Posture Workbench — Static Prototype" not in html:
        error("index.html: H1 text changed")
        ok = False
    for zone in REQUIRED_ZONES:
        if zone not in html:
            error(f"index.html: missing zone {zone}")
            ok = False
    for concept in REQUIRED_CONCEPTS:
        if concept not in html:
            error(f"index.html: missing concept {concept}")
            ok = False
    for cls in REQUIRED_CLASSES:
        if cls not in html_lower or cls not in css_lower:
            error(f"prototype files: missing visual class {cls}")
            ok = False
    for pattern, label in [(r"<script\b", "script"), (r"<form\b", "form"), (r"<input\b", "input"), (r"<textarea\b", "textarea"), (r"<button\b", "button"), (r"type\s*=\s*['\"]file['\"]", "file input")]:
        if re.search(pattern, html, re.I):
            error(f"index.html: prohibited {label}")
            ok = False
    for term in ["generated-output", "fake real", "fake/real", "percentage", "probability", "detector", "scanner", "api", "network", "storage", "analytics", "public route"]:
        if term in html_lower:
            error(f"index.html: prohibited language {term}")
            ok = False
    for term in ["score", "scoring", "engine", "classifier", "upload"]:
        for m in re.finditer(rf"\b{term}\b", html_lower):
            start = max(0, m.start() - 80)
            if not NEGATION_CONTEXT.search(html_lower[start:m.start()]):
                error(f"index.html: prohibited {term} outside negation")
                ok = False
                break
    if "@import" in css_lower or "url(" in css_lower:
        error("prototype.css: imports or URL dependencies are not allowed")
        ok = False
    for family in TOKEN_FAMILIES:
        if "--" + family.replace("_", "-") not in css_lower:
            error(f"prototype.css: missing token {family}")
            ok = False
    if "@media" not in css_lower or "max-width" not in css_lower:
        error("prototype.css: responsive/mobile-safe rule required")
        ok = False
    for forbidden in ["upload-dropzone", "score-gauge", "risk-gauge", "probability-meter", "verdict-green", "verdict-red", "fake-real", "detector-dashboard", "scanner"]:
        if forbidden in css_lower:
            error(f"prototype.css: forbidden styling {forbidden}")
            ok = False
    if "#000" in css_lower or "#000000" in css_lower:
        error("prototype.css: black cyber dashboard default not allowed")
        ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    for route in routes:
        if "internal_prototypes" in route.get("path", "").lower() or PROTO_REL.lower() in route.get("path", "").lower():
            error("route-registry: prototype must not be registered")
            ok = False
    locs = [el.text.strip().lower() for el in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if el.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error("sitemap.xml: expected exactly PUBLIC_SITEMAP_URL_COUNT URLs")
        ok = False
    if any("internal_prototypes" in loc or "evidence-posture-workbench" in loc for loc in locs):
        error("sitemap.xml: prototype must not be included")
        ok = False
    link_pattern = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for rel in ["index.html", "reference/evidence-posture/index.html", "reference/artifact-subject-separation/index.html", "language/index.html"]:
        if link_pattern.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel}: must not link to prototype")
            ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK,
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
    ):
        error(f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK}")
        ok = False
    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if g.get("name") == "Non-Public Static Workbench Visual System Hardening Validation Gate"), None)
    if not gate:
        error("Non-Public Static Workbench Visual System Hardening Validation Gate missing")
        ok = False
    else:
        for field in ["required_before_non_public_static_workbench_visual_system_baseline_lock", "required_before_any_interface_prototype_expansion", "required_before_engine_governance"]:
            if gate.get(field) is not True:
                error(f"validation gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("validation gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in ["public engine", "public classifier", "public tool", "public route", "sitemap", "navigation", "upload", "scoring", "api", "forms", "analytics", "deployment", "dns", "cloudflare", "custom domain launch"]:
            if term not in notes:
                error(f"validation gate notes must mention {term}")
                ok = False
    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_visual_system_hardening_validation" not in checks:
        error("reference-expansion-gate: hardening validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_hardening_validation_alone" not in rules:
        error("reference-expansion-gate: hardening validation must not grant public engine eligibility")
        ok = False
    return ok


def validate_source_registry_and_cross_file() -> bool:
    ok = True
    locations = {s.get("location") for s in load_json(ROOT / "data" / "source-registry.json").get("sources", [])}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing {loc}")
            ok = False
    if "validate_non_public_static_workbench_visual_system_hardening_validation.py" not in (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py must include hardening validation validator")
        ok = False
    if "DEC-057" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-057 missing")
        ok = False
    ledger = load_json(ROOT / "data" / "evidence-ledger.json")
    cmap = load_json(ROOT / "data" / "claim-source-map.json")
    if not any(c.get("claim_id") == "CLAIM-0045" for c in ledger.get("claims", [])):
        error("evidence-ledger: CLAIM-0045 missing")
        ok = False
    if not any(c.get("claim_id") == "CLAIM-0045" for c in cmap.get("claim_source_links", [])):
        error("claim-source-map: CLAIM-0045 missing")
        ok = False
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.splitlines()
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.splitlines()
    for rel in tracked + staged:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error("python cache files must not be tracked or staged")
            ok = False
            break
    return ok


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-visual-system-hardening-validation-policy.json",
        "data/non-public-static-workbench-visual-system-hardening-validation-results-v1.json",
        "data/non-public-static-workbench-visual-system-token-validation-v1.json",
        "data/non-public-static-workbench-visual-system-pattern-validation-v1.json",
        "data/non-public-static-workbench-visual-system-antipattern-validation-v1.json",
        "data/non-public-static-workbench-visual-system-public-isolation-audit-v1.json",
        "data/non-public-static-workbench-visual-system-static-safety-audit-v1.json",
        "data/non-public-static-workbench-visual-system-hardening-policy.json",
        "data/non-public-static-workbench-visual-system-token-contract-v1.json",
        "data/non-public-static-workbench-visual-system-pattern-registry-v1.json",
        "data/non-public-static-workbench-visual-system-antipattern-audit-v1.json",
        "data/non-public-static-workbench-visual-system-boundary-audit-v1.json",
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
        "sitemap.xml", "index.html", "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html", "language/index.html",
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
        validate_policy, validate_results, validate_token_validation, validate_pattern_validation,
        validate_antipattern_validation, validate_isolation_and_static_audits, validate_prototype_read_only_state,
        validate_public_safety, validate_governance, validate_source_registry_and_cross_file,
    ]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

