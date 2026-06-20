#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Visual System Hardening v1."""

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
ALLOWED_REL_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "static_internal_visual_hardening_only_no_engine_no_classifier_no_tool_no_public_route"

REQUIRED_POLICY = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "identity_principle", "allowed_hardening_actions", "prohibited_actions",
    "allowed_files", "visual_system_scope", "non_authorization_rules", "last_reviewed",
}
TOKEN_FAMILIES = [
    "background_field", "chamber_surface", "chamber_edge", "graphite_text", "muted_text",
    "boundary_accent", "provenance_line", "provenance_shadow", "absence_field",
    "not_assessable_surface", "refusal_surface", "output_envelope_surface",
    "verification_path_line", "subtle_rule", "focus_ring", "mobile_spacing",
]
TOKEN_PRINCIPLES = [
    "tokens are local to prototype.css", "tokens are conceptual not decorative",
    "tokens support governed evidence field", "tokens support evidence chamber identity",
    "tokens do not imply scoring, verdict, upload, classifier, or detector behavior",
    "tokens do not depend on external assets",
]
FORBIDDEN_TOKENS = [
    "black cyber dashboard default", "neon detector palette", "red green verdict system",
    "score severity palette", "upload dashboard CTA palette", "SaaS analytics gradient system",
    "external font dependency", "external URL dependency",
]
PROHIBITED_ACTIONS = [
    "new_prototype_files", "prototype_expansion", "public_route_creation", "sitemap_expansion",
    "public_navigation_link", "interface_behavior", "javascript", "forms", "inputs", "upload",
    "scoring", "fake_real_output", "generated_output", "engine", "classifier", "detector",
    "api", "analytics", "storage", "network_calls", "monetization", "dns", "cloudflare",
    "custom_domain_launch", "deployment_changes", "external_factual_claims", "subject_accusation",
]
NON_AUTH_BLOCKS = [
    "public_workbench", "engine", "classifier", "upload", "scoring", "api", "routes",
    "sitemap", "deployment", "dns", "cloudflare", "custom_domain_launch", "public_tool_behavior",
    "prototype_expansion_beyond_allowed_files", "production_readiness",
]
REQUIRED_PATTERNS = [
    "Evidence Field", "Evidence Chamber", "Boundary Rail", "Provenance Shadow",
    "Missing Context Absence", "Not-Assessable Restraint", "Refusal Gate",
    "Output Envelope", "Verification Path",
]
BLOCKED_ANTIPATTERNS = [
    "detector_dashboard", "scanner_ui", "upload_dashboard", "red_green_fake_real_interface",
    "truth_meter", "risk_gauge", "probability_meter", "forensic_game_interface",
    "policing_dashboard", "saas_analytics_dashboard", "product_landing_page_cta",
    "try_it_now_interface", "black_cyber_dashboard_default",
]
VISUAL_KEYS = [
    "evidence_field_hardened", "evidence_chamber_hardened", "boundary_rail_hardened",
    "provenance_shadow_hardened", "missing_context_absence_hardened",
    "not_assessable_restraint_hardened", "refusal_gate_hardened", "output_envelope_hardened",
    "verification_path_hardened", "anti_detector_identity_preserved",
]
FILE_SCOPE_KEYS = ["only_index_and_css_modified", "no_additional_prototype_files", "no_new_prototype_directories"]
PUBLIC_SURFACE_KEYS = [
    "no_route_registry_entry", "no_sitemap_entry", "no_homepage_link",
    "no_public_reference_links", "no_language_page_link", "no_public_navigation",
]
CAPABILITY_KEYS = [
    "no_engine", "no_classifier", "no_detector", "no_upload", "no_scoring", "no_fake_real",
    "no_api", "no_analytics", "no_storage", "no_network_calls", "no_deployment_change",
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
REQUIRED_CLASSES = [
    "evidence-field", "evidence-chamber", "chamber-frame", "boundary-rail",
    "provenance-shadow", "missing-context-absence", "not-assessable-restraint",
    "refusal-gate", "output-envelope", "verification-path",
]
REQUIRED_STATEMENTS = [
    "Internal static prototype. Non-public web surface. No engine. No classifier. No upload. No scoring. No verdict.",
    "This static prototype explores the Evidence Chamber interface direction.",
    "Evidence is structured before it is believed, escalated, published, or judged.",
]
REQUIRED_SOURCE_LOCATIONS = [
    "NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING_V1.md",
    "data/non-public-static-workbench-visual-system-hardening-policy.json",
    "data/non-public-static-workbench-visual-system-token-contract-v1.json",
    "data/non-public-static-workbench-visual-system-pattern-registry-v1.json",
    "data/non-public-static-workbench-visual-system-antipattern-audit-v1.json",
    "data/non-public-static-workbench-visual-system-boundary-audit-v1.json",
    "validators/validate_non_public_static_workbench_visual_system_hardening.py",
]
NEGATION_CONTEXT = re.compile(r"\b(does not|do not|no|not|without)\b", re.I)
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def contains_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower().replace("_", " ") in text or item.lower() in text for item in required)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-visual-system-hardening-policy.json"
    data = load_json(path)
    if not REQUIRED_POLICY.issubset(data):
        error("visual hardening policy: missing required top-level fields")
        ok = False
    if data.get("status") != "governed_non_public_static_workbench_visual_system_hardening_policy":
        error("visual hardening policy: invalid status")
        ok = False
    if data.get("maturity") != MATURE:
        error("visual hardening policy: invalid maturity")
        ok = False
    if data.get("allowed_files") != ALLOWED_REL_FILES:
        error("visual hardening policy: allowed_files must be exactly index.html and prototype.css")
        ok = False
    if not contains_all(data.get("prohibited_actions", []), PROHIBITED_ACTIONS):
        error("visual hardening policy: missing prohibited actions")
        ok = False
    blocked = data.get("non_authorization_rules", {}).get("blocked", [])
    if not contains_all(blocked, NON_AUTH_BLOCKS):
        error("visual hardening policy: missing non-authorization blocks")
        ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("visual hardening policy: numeric score, grade, percentage, or SEO score found")
        ok = False
    return ok


def validate_token_contract() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-token-contract-v1.json")
    if data.get("maturity") != MATURE:
        error("token contract: invalid maturity")
        ok = False
    if not set(TOKEN_FAMILIES).issubset(set(data.get("token_families", []))):
        error("token contract: missing token families")
        ok = False
    if not contains_all(data.get("required_token_principles", []), TOKEN_PRINCIPLES):
        error("token contract: missing token principles")
        ok = False
    if not contains_all(data.get("forbidden_token_patterns", []), FORBIDDEN_TOKENS):
        error("token contract: missing forbidden token patterns")
        ok = False
    return ok


def validate_pattern_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-pattern-registry-v1.json")
    patterns = data.get("visual_patterns", [])
    if len(patterns) != 9:
        error("pattern registry: expected exactly 9 visual patterns")
        ok = False
    ids = [p.get("pattern_id", "") for p in patterns]
    if len(ids) != len(set(ids)) or not all(re.fullmatch(r"NP-VIS-PATTERN-\d{4}", i) for i in ids):
        error("pattern registry: IDs must be unique and follow NP-VIS-PATTERN-0001")
        ok = False
    names = {p.get("pattern_name") for p in patterns}
    for name in REQUIRED_PATTERNS:
        if name not in names:
            error(f"pattern registry: missing {name}")
            ok = False
    required = {"conceptual_function", "required_visual_behavior", "forbidden_visual_behavior", "related_html_classes", "related_css_concepts", "operational_boundary", "non_authorization_statement"}
    for pattern in patterns:
        if not required.issubset(pattern):
            error(f"pattern registry: {pattern.get('pattern_id')} missing required fields")
            ok = False
        statement = pattern.get("non_authorization_statement", "").lower()
        for term in ["engine", "classifier", "upload", "scoring", "fake/real", "api", "routes", "sitemap", "deployment", "dns", "cloudflare", "public tool"]:
            if term not in statement:
                error(f"pattern registry: {pattern.get('pattern_id')} non-authorization missing {term}")
                ok = False
    return ok


def validate_antipattern_audit() -> bool:
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-antipattern-audit-v1.json")
    ok = True
    if not set(BLOCKED_ANTIPATTERNS).issubset(set(data.get("blocked_antipatterns", []))):
        error("anti-pattern audit: missing blocked anti-patterns")
        ok = False
    if data.get("overall_outcome") != "visual_antipatterns_blocked":
        error("anti-pattern audit: invalid overall_outcome")
        ok = False
    return ok


def validate_boundary_audit() -> bool:
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-boundary-audit-v1.json")
    ok = True
    if data.get("audited_files") != ALLOWED_REL_FILES:
        error("boundary audit: audited_files must be exactly allowed prototype files")
        ok = False
    if data.get("overall_outcome") != "non_public_static_workbench_visual_system_hardening_boundary_validated":
        error("boundary audit: invalid overall_outcome")
        ok = False
    for key in VISUAL_KEYS:
        if key not in data.get("visual_hardening_results", {}):
            error(f"boundary audit: missing visual result {key}")
            ok = False
    for key in FILE_SCOPE_KEYS:
        if key not in data.get("file_scope_results", {}):
            error(f"boundary audit: missing file scope result {key}")
            ok = False
    for key in PUBLIC_SURFACE_KEYS:
        if key not in data.get("public_surface_results", {}):
            error(f"boundary audit: missing public surface result {key}")
            ok = False
    for key in CAPABILITY_KEYS:
        if key not in data.get("capability_block_results", {}):
            error(f"boundary audit: missing capability result {key}")
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
    html = INDEX_PATH.read_text(encoding="utf-8")
    html_lower = html.lower()
    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        error("index.html: expected exactly one H1")
        ok = False
    if "Evidence Posture Workbench — Static Prototype" not in html:
        error("index.html: required H1 changed")
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
    for cls in REQUIRED_CLASSES:
        if cls not in html_lower:
            error(f"index.html: missing visual-system class {cls}")
            ok = False
    for pattern, label in [
        (r"<script\b", "script tag"),
        (r"<form\b", "form element"),
        (r"<input\b", "input element"),
        (r"<textarea\b", "textarea element"),
        (r"<button\b", "button element"),
        (r"type\s*=\s*['\"]file['\"]", "file input"),
    ]:
        if re.search(pattern, html, re.I):
            error(f"index.html: prohibited {label}")
            ok = False
    prohibited_patterns = [
        r"\bfake\b.*\breal\b",
        r"\b\d+\s*%\b",
        r"generated output",
        r"api",
        r"analytics",
        r"network",
        r"storage",
    ]
    for pattern in prohibited_patterns:
        if re.search(pattern, html_lower):
            error(f"index.html: prohibited content pattern {pattern}")
            ok = False
    for term in ["score", "scoring", "detector", "scanner", "classifier", "engine", "upload"]:
        for m in re.finditer(rf"\b{term}\b", html_lower):
            start = max(0, m.start() - 80)
            if not NEGATION_CONTEXT.search(html_lower[start:m.start()]):
                error(f"index.html: prohibited {term} language outside negation")
                ok = False
                break
    return ok


def validate_prototype_css() -> bool:
    ok = True
    css = CSS_PATH.read_text(encoding="utf-8")
    css_lower = css.lower()
    if "@import" in css_lower:
        error("prototype.css: @import not allowed")
        ok = False
    if "url(" in css_lower:
        error("prototype.css: url( not allowed")
        ok = False
    for family in TOKEN_FAMILIES:
        token = "--" + family.replace("_", "-")
        if token not in css_lower:
            error(f"prototype.css: missing token {token}")
            ok = False
    for cls in REQUIRED_CLASSES:
        if cls not in css_lower:
            error(f"prototype.css: missing visual-system class {cls}")
            ok = False
    if "@media" not in css_lower or "max-width" not in css_lower:
        error("prototype.css: responsive/mobile-safe rule required")
        ok = False
    for forbidden in ["upload-dropzone", "score-gauge", "risk-gauge", "probability-meter", "verdict-green", "verdict-red", "fake-real", "detector-dashboard", "scanner"]:
        if forbidden in css_lower:
            error(f"prototype.css: forbidden styling pattern {forbidden}")
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
        path = route.get("path", "").lower()
        if "internal_prototypes" in path or PROTO_REL.lower() in path:
            error("route-registry: prototype must not be registered as public route")
            ok = False
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [el.text.strip().lower() for el in tree.findall(".//{*}loc") if el.text]
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
        "blocked_until_internal_prototype_release_blocker_board_validation",
    ):
        error(f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING}")
        ok = False
    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if g.get("name") == "Non-Public Static Workbench Visual System Hardening Gate"), None)
    if not gate:
        error("Non-Public Static Workbench Visual System Hardening Gate missing")
        ok = False
    else:
        for field in ["required_before_non_public_static_workbench_visual_system_hardening_validation", "required_before_any_interface_prototype_expansion", "required_before_engine_governance"]:
            if gate.get(field) is not True:
                error(f"visual hardening gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("visual hardening gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in ["public engine", "public classifier", "public tool", "public route", "sitemap", "navigation", "upload", "scoring", "api", "forms", "analytics", "deployment", "dns", "cloudflare", "custom domain launch"]:
            if term not in notes:
                error(f"visual hardening gate notes must mention non-authorization for {term}")
                ok = False
    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_visual_system_hardening" not in checks:
        error("reference-expansion-gate: visual system hardening required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_visual_system_hardening_alone" not in rules:
        error("reference-expansion-gate: visual hardening must not grant public engine eligibility")
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
    validate_all = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_non_public_static_workbench_visual_system_hardening.py" not in validate_all:
        error("validate_all.py must include visual system hardening validator")
        ok = False
    if "DEC-056" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-056 missing")
        ok = False
    ledger = load_json(ROOT / "data" / "evidence-ledger.json")
    if not any(c.get("claim_id") == "CLAIM-0044" for c in ledger.get("claims", [])):
        error("evidence-ledger: CLAIM-0044 missing")
        ok = False
    cmap = load_json(ROOT / "data" / "claim-source-map.json")
    if not any(c.get("claim_id") == "CLAIM-0044" for c in cmap.get("claim_source_links", [])):
        error("claim-source-map: CLAIM-0044 missing")
        ok = False
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.splitlines()
        staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.splitlines()
        for rel in tracked + staged:
            low = rel.lower().replace("\\", "/")
            if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
                error("python cache files must not be tracked or staged")
                ok = False
                break
    except OSError as exc:
        error(f"git cache check failed: {exc}")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-visual-system-hardening-policy.json",
        "data/non-public-static-workbench-visual-system-token-contract-v1.json",
        "data/non-public-static-workbench-visual-system-pattern-registry-v1.json",
        "data/non-public-static-workbench-visual-system-antipattern-audit-v1.json",
        "data/non-public-static-workbench-visual-system-boundary-audit-v1.json",
        "data/non-public-static-workbench-prototype-refinement-validation-results-v1.json",
        "data/non-public-static-workbench-prototype-refinement-visual-identity-validation-v1.json",
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
        validate_policy, validate_token_contract, validate_pattern_registry, validate_antipattern_audit,
        validate_boundary_audit, validate_prototype_files, validate_prototype_css, validate_public_safety,
        validate_publisher_governance, validate_source_registry, validate_cross_file,
    ]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
