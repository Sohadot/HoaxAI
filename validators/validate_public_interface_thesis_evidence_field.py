#!/usr/bin/env python3
"""Validate Sprint 63 — Public Interface Thesis and Evidence Field Design Foundation."""

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
    PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
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
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_RELEASE_BLOCKER_BOARD_VALIDATION,
    validate_public_surface,
)

INTERFACE_PATH = "interface/evidence-field/index.html"
INTERFACE_URL = "https://hoax.ai/interface/evidence-field/"
INTERFACE_ROUTE = "/interface/evidence-field/"
STANDARD_LINK = "/standard/evidence-posture/"
PROTOCOL_LINK = "/protocol/evidence-posture/"

REQUIRED_SECTIONS = [
    "Interface Thesis Statement",
    "Why Interface Matters",
    "Evidence Field, Not Detector Dashboard",
    "Interface Layers",
    "Protocol Visualization",
    "Standard Alignment",
    "Boundary Visualization",
    "Future Interface Components",
    "Visual Language Principles",
    "Accessibility and Trust",
    "Technical Foundation",
    "Relationship to Protocol",
    "Relationship to Standard",
    "Relationship to Reference Layer",
    "Non-Operational Status",
    "Hoax.ai Boundary",
    "Related Pages",
]

REFERENCE_LINKS = [
    "/reference/evidence-posture/",
    "/reference/artifact-subject-separation/",
    "/reference/source-confidence/",
    "/reference/provenance-gap/",
    "/reference/not-assessable/",
    "/reference/output-boundary/",
    "/reference/synthetic-fragility/",
    "/reference/evidence-chain/",
    "/reference/context-collapse/",
    "/reference/claim-source-traceability/",
    "/reference/attribution-boundary/",
    "/reference/claim-drift/",
    "/reference/evidence-limitation/",
    "/reference/interpretation-risk/",
]

NOT_TOOL_PHRASES = [
    "not a detector dashboard",
    "not a scanner",
    "not a classifier",
    "not an upload interface",
    "not a scoring system",
    "not an api",
    "automated verdict interface",
]

FRAMING_PHRASES = [
    "evidence field",
    "protocol visualization",
    "detector dashboard",
    "result-card",
]

REJECT_FRAMING = [
    "upload-centered",
    "traffic-light",
    "confidence-score meter",
    "fake/real",
]

FORBIDDEN_PATTERNS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script",
    r"scoring interface",
    r"classifier interface",
    r"detector interface",
    r"scanner interface",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_63_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD_AUDIT.md",
    "validators/validate_public_interface_thesis_evidence_field.py",
]

MIN_WORDS = 2000


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def visible_word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html)))


def validate_interface_page() -> bool:
    ok = True
    path = ROOT / INTERFACE_PATH
    if not path.is_file():
        error(f"missing {INTERFACE_PATH}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    if text.count("<h1") != 1:
        error("interface thesis page must have exactly one H1")
        ok = False
    if INTERFACE_URL not in text:
        error("interface thesis page missing canonical URL")
        ok = False
    if "<title>" not in text or 'name="description"' not in text:
        error("interface thesis page missing title or meta description")
        ok = False
    for section in REQUIRED_SECTIONS:
        if section not in text:
            error(f"interface thesis page missing section: {section}")
            ok = False
    if STANDARD_LINK not in text:
        error("interface thesis page must link to standard")
        ok = False
    if PROTOCOL_LINK not in text:
        error("interface thesis page must link to protocol")
        ok = False
    for link in REFERENCE_LINKS:
        if link not in text:
            error(f"interface thesis page missing link to {link}")
            ok = False
    for phrase in NOT_TOOL_PHRASES:
        if phrase not in lower:
            error(f"interface thesis page missing positioning phrase: {phrase}")
            ok = False
    if not any(p in lower for p in ("evidence field", "evidence-field")):
        error("interface thesis page must use evidence-field framing")
        ok = False
    if "protocol visualization" not in lower and "protocol path" not in lower:
        error("interface thesis page must use protocol-visualization framing")
        ok = False
    for phrase in REJECT_FRAMING:
        if phrase not in lower:
            error(f"interface thesis page must reject or address: {phrase}")
            ok = False
    wc = visible_word_count(text)
    if wc < MIN_WORDS:
        error(f"interface thesis page insufficient depth ({wc} words, need {MIN_WORDS})")
        ok = False
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.I):
            error(f"interface thesis page forbidden pattern: {pat}")
            ok = False
    return ok


def validate_linking() -> bool:
    ok = True
    for rel in (
        "index.html",
        "language/index.html",
        "standard/evidence-posture/index.html",
        "protocol/evidence-posture/index.html",
    ):
        if INTERFACE_ROUTE not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel} must link to interface thesis")
            ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    interface_routes = [r for r in routes if r.get("path") == INTERFACE_ROUTE]
    if len(interface_routes) != 1:
        error("route registry must include exactly one interface thesis route")
        ok = False
    elif interface_routes[0].get("route_id") != "ROUTE-0019":
        error("interface thesis route must be ROUTE-0019")
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
    if INTERFACE_URL not in locs:
        error("sitemap missing interface thesis URL")
        ok = False
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    if pat.search((ROOT / INTERFACE_PATH).read_text(encoding="utf-8")):
        error("interface thesis page prototype leak")
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
    if "DEC-081" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-081 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_63_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD_AUDIT.md").is_file():
        error("Sprint 63 audit missing")
        ok = False
    if "validate_public_interface_thesis_evidence_field.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 63 validator")
        ok = False
    policy = json.loads((ROOT / "data/publisher-governance-policy.json").read_text(encoding="utf-8"))
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
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
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_RELEASE_BLOCKER_BOARD_VALIDATION,
    ):
        error("publisher status must be blocked_until_public_interface_thesis_evidence_field_validation, static embodiment v1 validation, visual system hardening validation, or controlled domain connection decision")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0065" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0065 missing")
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
            validate_linking,
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
