#!/usr/bin/env python3
"""Validate Sprint 65 — Evidence Field Visual System and Accessibility Hardening."""

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
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
    PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
        PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    validate_public_surface,
)

INTERFACE_PATH = "interface/evidence-field/index.html"
STYLES_PATH = "styles.css"
INTERFACE_URL = "https://hoax.ai/interface/evidence-field/"
INTERFACE_ROUTE = "/interface/evidence-field/"
STANDARD_LINK = "/standard/evidence-posture/"
PROTOCOL_LINK = "/protocol/evidence-posture/"

POSTURE_STATES = [
    "Supported",
    "Qualified",
    "Limited",
    "Not Assessable",
    "Out of Scope",
]

CORE_REFERENCE_LINKS = [
    "/reference/evidence-posture/",
    "/reference/artifact-subject-separation/",
    "/reference/output-boundary/",
    "/reference/evidence-limitation/",
    "/reference/interpretation-risk/",
    "/reference/attribution-boundary/",
    "/reference/claim-source-traceability/",
]

NOT_TOOL_PHRASES = [
    "not a tool",
    "not an engine",
    "not a classifier",
    "not a scanner",
    "not a detector",
    "not an upload interface",
    "not a scoring system",
    "not an api",
    "not an automated verdict interface",
    "verdict behavior",
]

REJECT_FRAMING = [
    "detector dashboard",
    "upload-centered",
    "traffic-light",
    "confidence-score meter",
    "confidence meter",
    "result-card",
    "fake/real",
]

FORBIDDEN_HTML_PATTERNS = [
    r"<script\b",
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<select\b",
    r"<button\b",
    r"type=\"file\"",
    r"onclick=",
    r"onload=",
    r"\b\d{1,3}\s*%",
    r"confidence percentage",
    r"score:\s*\d",
    r"<progress\b",
    r'class="score-meter"',
]

CSS_REQUIRED_CLASSES = [
    "evidence-field",
    "protocol-path",
    "boundary-rail",
    "posture-state",
]

CSS_FORBIDDEN_PATTERNS = [
    r"@keyframes\s+\w*scan",
    r"@keyframes\s+\w*detect",
    r"\.score-meter",
    r"\.progress-meter",
    r"\.fake-real",
    r"\.verdict-result",
    r"animation:\s*[^;]*scan",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_65_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING_AUDIT.md",
    "validators/validate_evidence_field_visual_system_accessibility_hardening.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def validate_interface_page() -> bool:
    ok = True
    path = ROOT / INTERFACE_PATH
    if not path.is_file():
        error(f"missing {INTERFACE_PATH}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    if text.count("<h1") != 1:
        error("interface page must have exactly one H1")
        ok = False
    if INTERFACE_URL not in text:
        error("interface page missing canonical URL")
        ok = False
    if "<title>" not in text or 'name="description"' not in text:
        error("interface page missing title or meta description")
        ok = False
    if "Evidence Field Static Embodiment v1" not in text:
        error("interface page missing Evidence Field Static Embodiment v1")
        ok = False
    if "Reading Order and Interpretation" not in text and "Reading Order" not in text:
        error("interface page missing Reading Order and Interpretation")
        ok = False
    if "Evidence Field Visual Grammar" not in text and "Visual Grammar" not in text:
        error("interface page missing Evidence Field Visual Grammar")
        ok = False
    if "Boundary Rail" not in text:
        error("interface page missing Boundary Rail")
        ok = False
    if "Allowed" not in text or "Prohibited" not in text:
        error("interface page missing Allowed/Prohibited blocks")
        ok = False
    for state in POSTURE_STATES:
        if state not in text:
            error(f"interface page missing posture state: {state}")
            ok = False
    if not re.search(r"Supported[\s\S]{0,120}Not a truth verdict|Supported[\s\S]{0,120}not a truth", text, re.I):
        error("Supported posture must have text definition without truth verdict")
        ok = False
    if "Non-Operational Status" not in text and "Non-Operational" not in text:
        error("interface page missing Non-Operational Status")
        ok = False
    if STANDARD_LINK not in text:
        error("interface page must link to standard")
        ok = False
    if PROTOCOL_LINK not in text:
        error("interface page must link to protocol")
        ok = False
    for link in CORE_REFERENCE_LINKS:
        if link not in text:
            error(f"interface page missing link to {link}")
            ok = False
    for phrase in NOT_TOOL_PHRASES:
        if phrase not in lower:
            error(f"interface page missing non-tool phrase: {phrase}")
            ok = False
    for phrase in REJECT_FRAMING:
        if phrase not in lower:
            error(f"interface page must reject or address: {phrase}")
            ok = False
    for pat in FORBIDDEN_HTML_PATTERNS:
        if re.search(pat, text, re.I):
            error(f"interface page forbidden pattern: {pat}")
            ok = False
    return ok


def validate_styles() -> bool:
    ok = True
    path = ROOT / STYLES_PATH
    if not path.is_file():
        error(f"missing {STYLES_PATH}")
        return False
    css = path.read_text(encoding="utf-8")
    lower = css.lower()
    for token in CSS_REQUIRED_CLASSES:
        if token not in lower:
            error(f"styles.css missing evidence-field related class: {token}")
            ok = False
    for pat in CSS_FORBIDDEN_PATTERNS:
        if re.search(pat, css, re.I):
            error(f"styles.css forbidden pattern: {pat}")
            ok = False
    if "@media" not in css or "evidence-field" not in lower:
        error("styles.css must include responsive media handling for evidence-field layout")
        ok = False
    if "--ef-" not in css:
        error("styles.css must include evidence-field design tokens")
        ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    extra = [r for r in routes if r.get("path", "").startswith("/interface/") and r.get("path") != INTERFACE_ROUTE]
    if extra:
        error("no additional interface routes beyond /interface/evidence-field/")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    if pat.search((ROOT / INTERFACE_PATH).read_text(encoding="utf-8")):
        error("interface page prototype leak")
        ok = False
    if not all((ROOT / x).is_file() for x in LOCKED_FILES):
        error("prototype files missing")
        ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files modified")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-083" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-083 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_65_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING_AUDIT.md").is_file():
        error("Sprint 65 audit missing")
        ok = False
    if "validate_evidence_field_visual_system_accessibility_hardening.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 65 validator")
        ok = False
    policy = json.loads((ROOT / "data/publisher-governance-policy.json").read_text(encoding="utf-8"))
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
        PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
        PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    ):
        error("publisher status must be blocked_until_evidence_field_visual_system_accessibility_hardening_validation or controlled domain connection decision")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0067" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0067 missing")
        ok = False
    return ok


def validate_cache() -> bool:
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    names += subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error(f"python cache tracked/staged: {rel}")
            return False
    return True


def main() -> int:
    ok = all(
        fn()
        for fn in [
            validate_interface_page,
            validate_styles,
            validate_surface,
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
