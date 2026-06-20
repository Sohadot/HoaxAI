#!/usr/bin/env python3
"""Validate Sprint 64 — Evidence Field Static Interface Embodiment v1."""

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
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
    PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
    validate_public_surface,
)

INTERFACE_PATH = "interface/evidence-field/index.html"
INTERFACE_URL = "https://hoax.ai/interface/evidence-field/"
INTERFACE_ROUTE = "/interface/evidence-field/"
STANDARD_LINK = "/standard/evidence-posture/"
PROTOCOL_LINK = "/protocol/evidence-posture/"

CONCEPTUAL_ZONES = [
    "Artifact Layer",
    "Claim Layer",
    "Source Basis Layer",
    "Provenance Layer",
    "Context Layer",
    "Traceability Layer",
    "Evidence Limitation Layer",
    "Interpretation Risk Layer",
    "Attribution Boundary Layer",
    "Output Boundary Layer",
    "Evidence Posture Layer",
]

PROTOCOL_STEPS = [f"EP-P{i:02d}" for i in range(1, 18)]

EPS_PRINCIPLES = [
    "EPS-001",
    "EPS-002",
    "EPS-006",
    "EPS-012",
    "EPS-013",
    "EPS-014",
]

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

REQUIRED_SECTIONS = [
    "Evidence Field Static Embodiment v1",
    "Protocol Path",
    "Standard Alignment",
    "Boundary Rail",
    "Reading the Field",
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
    "result-card",
    "fake/real",
]

FORBIDDEN_PATTERNS = [
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
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_64_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1_AUDIT.md",
    "validators/validate_evidence_field_static_interface_embodiment_v1.py",
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
    for section in REQUIRED_SECTIONS:
        if section not in text:
            error(f"interface page missing section: {section}")
            ok = False
    for zone in CONCEPTUAL_ZONES:
        if zone not in text:
            error(f"interface page missing zone: {zone}")
            ok = False
    for step in PROTOCOL_STEPS:
        if step not in text:
            error(f"interface page missing protocol step: {step}")
            ok = False
    for eps in EPS_PRINCIPLES:
        if eps not in text:
            error(f"interface page missing standard principle: {eps}")
            ok = False
    if "Allowed" not in text or "Prohibited" not in text:
        error("interface page missing Allowed/Prohibited boundary blocks")
        ok = False
    for state in POSTURE_STATES:
        if state not in text:
            error(f"interface page missing posture state: {state}")
            ok = False
    if "Non-Operational" not in text:
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
    if "explanatory and non-operational" not in lower:
        error("protocol path must state explanatory and non-operational")
        ok = False
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.I):
            error(f"interface page forbidden pattern: {pat}")
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
    if "DEC-082" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-082 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_64_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1_AUDIT.md").is_file():
        error("Sprint 64 audit missing")
        ok = False
    if "validate_evidence_field_static_interface_embodiment_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 64 validator")
        ok = False
    policy = json.loads((ROOT / "data/publisher-governance-policy.json").read_text(encoding="utf-8"))
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
        PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
    ):
        error("publisher status must be blocked_until_evidence_field_static_interface_embodiment_v1_validation, visual system hardening validation, or controlled domain connection decision")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0066" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0066 missing")
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
