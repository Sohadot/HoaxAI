#!/usr/bin/env python3
"""Validate Sprint 62 — Protocol Integration, Standard Alignment, and Interface Readiness."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import PUBLIC_SITEMAP_URL_COUNT, validate_public_surface

PROTOCOL_PATH = "protocol/evidence-posture/index.html"
STANDARD_PATH = "standard/evidence-posture/index.html"
PROTOCOL_LINK = "/protocol/evidence-posture/"
STANDARD_LINK = "/standard/evidence-posture/"
INTERFACE_DOC = "PROTOCOL_TO_INTERFACE_READINESS.md"

REFERENCE_PAGES = [
    "reference/evidence-posture/index.html",
    "reference/artifact-subject-separation/index.html",
    "reference/source-confidence/index.html",
    "reference/provenance-gap/index.html",
    "reference/not-assessable/index.html",
    "reference/output-boundary/index.html",
    "reference/synthetic-fragility/index.html",
    "reference/evidence-chain/index.html",
    "reference/context-collapse/index.html",
    "reference/claim-source-traceability/index.html",
    "reference/attribution-boundary/index.html",
    "reference/claim-drift/index.html",
    "reference/evidence-limitation/index.html",
    "reference/interpretation-risk/index.html",
]

PROTOCOL_SECTION_PHRASES = [
    "standard alignment",
    "interface readiness",
    "non-operational status",
]

STANDARD_SECTION_PHRASES = [
    "relationship to evidence posture protocol",
    "standard vs protocol",
]

INTERFACE_DOC_PHRASES = [
    "no public interface route is created",
    "no engine",
    "no classifier",
    "no upload",
    "no scoring",
    "no api",
    "no analytics",
    "no forms",
    "javascript",
    "public tool behavior",
    "detector dashboard",
    "evidence field",
    "protocol visualization",
]

FORBIDDEN_HTML_PATTERNS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script[^>]+src=",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

PUBLIC_HTML = [
    "index.html",
    "language/index.html",
    STANDARD_PATH,
    PROTOCOL_PATH,
    *REFERENCE_PAGES,
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    protocol_routes = [r for r in routes if r.get("path") == PROTOCOL_LINK]
    if len(protocol_routes) != 1:
        error("must retain exactly one protocol route")
        ok = False
    interface_routes = [r for r in routes if "/interface/" in r.get("path", "")]
    if interface_routes:
        error("no public interface route may be created")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    return ok


def validate_linking() -> bool:
    ok = True
    for rel in ("index.html", "language/index.html", STANDARD_PATH):
        if PROTOCOL_LINK not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel} must link to protocol")
            ok = False
    protocol_text = (ROOT / PROTOCOL_PATH).read_text(encoding="utf-8")
    if STANDARD_LINK not in protocol_text:
        error("protocol page must link to standard")
        ok = False
    for rel in REFERENCE_PAGES:
        if PROTOCOL_LINK not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel} must link to protocol")
            ok = False
    return ok


def validate_protocol_page() -> bool:
    ok = True
    text = (ROOT / PROTOCOL_PATH).read_text(encoding="utf-8")
    lower = text.lower()
    for phrase in PROTOCOL_SECTION_PHRASES:
        if phrase not in lower:
            error(f"protocol page missing section phrase: {phrase}")
            ok = False
    if "reference layer" not in lower and "reference layer dependencies" not in lower:
        error("protocol page must describe reference layer dependencies")
        ok = False
    if "future interface" not in lower:
        error("protocol page must mention future interface boundary")
        ok = False
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    if pat.search(text):
        error("protocol page must not link to prototypes")
        ok = False
    return ok


def validate_standard_page() -> bool:
    ok = True
    text = (ROOT / STANDARD_PATH).read_text(encoding="utf-8")
    lower = text.lower()
    for phrase in STANDARD_SECTION_PHRASES:
        if phrase not in lower:
            error(f"standard page missing section phrase: {phrase}")
            ok = False
    if PROTOCOL_LINK not in text:
        error("standard page must link to protocol")
        ok = False
    if "cannot exceed the standard" not in lower and "protocol cannot exceed" not in lower:
        error("standard page must explain protocol cannot exceed standard")
        ok = False
    return ok


def validate_interface_doc() -> bool:
    ok = True
    path = ROOT / INTERFACE_DOC
    if not path.is_file():
        error(f"missing {INTERFACE_DOC}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    for phrase in INTERFACE_DOC_PHRASES:
        if phrase not in lower:
            error(f"{INTERFACE_DOC}: missing phrase '{phrase}'")
            ok = False
    if "/interface/" in text and "no public interface route" not in lower:
        error(f"{INTERFACE_DOC}: must clarify /interface/ is not created")
        ok = False
    return ok


def validate_reference_protocol_relationships() -> bool:
    ok = True
    for rel in REFERENCE_PAGES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "Protocol Relationship" not in text and "protocol relationship" not in text.lower():
            error(f"{rel} missing Protocol Relationship section")
            ok = False
        if "EP-P" not in text:
            error(f"{rel} must map to protocol step(s)")
            ok = False
    return ok


def validate_no_forbidden_public_patterns() -> bool:
    ok = True
    for rel in PUBLIC_HTML:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for pat in FORBIDDEN_HTML_PATTERNS:
            if re.search(pat, text, re.I):
                error(f"{rel} forbidden pattern: {pat}")
                ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-080" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-080 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_62_PROTOCOL_INTEGRATION_STANDARD_ALIGNMENT_INTERFACE_READINESS_AUDIT.md").is_file():
        error("Sprint 62 audit missing")
        ok = False
    if "validate_protocol_integration_standard_alignment_interface_readiness.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 62 validator")
        ok = False
    return ok


def validate_prototype_and_cache() -> bool:
    ok = True
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
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    names += subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error(f"python cache tracked/staged: {rel}")
            return False
    return ok


def main() -> int:
    ok = all(
        fn()
        for fn in [
            validate_surface,
            validate_linking,
            validate_protocol_page,
            validate_standard_page,
            validate_interface_doc,
            validate_reference_protocol_relationships,
            validate_no_forbidden_public_patterns,
            validate_governance,
            validate_prototype_and_cache,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
