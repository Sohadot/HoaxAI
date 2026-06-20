#!/usr/bin/env python3
"""Validate Sprint 61 — Hoax.ai Evidence Posture Protocol v1 Draft."""

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
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT,
    PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
    PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
        PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    validate_public_surface,
)

PROTOCOL_PATH = "protocol/evidence-posture/index.html"
PROTOCOL_URL = "https://hoax.ai/protocol/evidence-posture/"
PROTOCOL_ROUTE = "/protocol/evidence-posture/"
STANDARD_LINK = "/standard/evidence-posture/"

REQUIRED_SECTIONS = [
    "Protocol Statement",
    "Scope",
    "Protocol Inputs",
    "Protocol Sequence",
    "Step Definitions",
    "Evidence Posture Assignment",
    "Output Language Formation",
    "Protocol Matrix",
    "Failure Modes",
    "Relationship to Evidence Posture Standard v1",
    "Relationship to Reference Layer",
    "Institutional Usefulness",
    "Protocol Versioning",
    "Hoax.ai Boundary",
    "Related Pages",
]

PROTOCOL_STEPS = [f"EP-P{i:02d}" for i in range(1, 18)]

POSTURE_STATES = [
    "Supported",
    "Qualified",
    "Limited",
    "Not Assessable",
    "Out of Scope",
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

BOUNDARY_PHRASES = [
    "artifact-subject separation",
    "output boundary",
    "evidence limitation",
    "interpretation risk",
    "claim-source traceability",
    "attribution boundary",
]

NOT_TOOL_PHRASES = [
    "public reference protocol draft",
    "not a detector",
    "not a scanner",
    "not a classifier",
    "not an engine",
    "not an upload tool",
    "not a scoring system",
    "not an api",
    "not a legal judgment",
    "not a moderation system",
    "not an accusation system",
]

FORBIDDEN_PATTERNS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script[^>]+src=",
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
    "SPRINT_61_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT_AUDIT.md",
    "validators/validate_evidence_posture_protocol_v1_draft.py",
]

MIN_WORDS = 2500


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    return re.sub(r"<[^>]+>", " ", text)


def visible_word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html)))


def validate_protocol_page() -> bool:
    ok = True
    path = ROOT / PROTOCOL_PATH
    if not path.is_file():
        error(f"missing {PROTOCOL_PATH}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    if text.count("<h1") != 1:
        error("protocol page must have exactly one H1")
        ok = False
    if PROTOCOL_URL not in text:
        error("protocol page missing canonical URL")
        ok = False
    if "<title>" not in text or 'name="description"' not in text:
        error("protocol page missing title or meta description")
        ok = False
    for section in REQUIRED_SECTIONS:
        if section not in text:
            error(f"protocol page missing section: {section}")
            ok = False
    for step in PROTOCOL_STEPS:
        if step not in text:
            error(f"protocol page missing {step}")
            ok = False
    for state in POSTURE_STATES:
        if state not in text:
            error(f"protocol page missing posture state: {state}")
            ok = False
    if STANDARD_LINK not in text:
        error("protocol page must link to standard")
        ok = False
    for link in REFERENCE_LINKS:
        if link not in text:
            error(f"protocol page missing link to {link}")
            ok = False
    for phrase in BOUNDARY_PHRASES:
        if phrase not in lower:
            error(f"protocol page missing boundary phrase: {phrase}")
            ok = False
    for phrase in NOT_TOOL_PHRASES:
        if phrase not in lower:
            error(f"protocol page missing positioning phrase: {phrase}")
            ok = False
    if "posture assignment" not in lower and "posture state" not in lower:
        error("protocol page missing posture assignment language")
        ok = False
    if "prohibited inference" not in lower:
        error("protocol page missing prohibited inference language")
        ok = False
    if "numeric scoring" not in lower and "without numeric scoring" not in lower:
        error("protocol page must clarify no numeric scoring")
        ok = False
    wc = visible_word_count(text)
    if wc < MIN_WORDS:
        error(f"protocol page insufficient depth ({wc} words, need {MIN_WORDS})")
        ok = False
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.I):
            error(f"protocol page forbidden pattern: {pat}")
            ok = False
    return ok


def validate_linking() -> bool:
    ok = True
    for rel in ("index.html", "language/index.html", "standard/evidence-posture/index.html"):
        if PROTOCOL_ROUTE not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel} must link to protocol")
            ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    protocol_routes = [r for r in routes if r.get("path") == PROTOCOL_ROUTE]
    if len(protocol_routes) != 1:
        error("route registry must include exactly one protocol route")
        ok = False
    elif protocol_routes[0].get("route_id") != "ROUTE-0018":
        error("protocol route must be ROUTE-0018")
        ok = False
    extra = [r for r in routes if r.get("path", "").startswith("/protocol/") and r.get("path") != PROTOCOL_ROUTE]
    if extra:
        error("no additional protocol routes beyond /protocol/evidence-posture/")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    if PROTOCOL_URL not in locs:
        error("sitemap missing protocol URL")
        ok = False
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    if pat.search((ROOT / PROTOCOL_PATH).read_text(encoding="utf-8")):
        error("protocol page prototype leak")
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
    if "DEC-079" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-079 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_61_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT_AUDIT.md").is_file():
        error("Sprint 61 audit missing")
        ok = False
    if "validate_evidence_posture_protocol_v1_draft.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 61 validator")
        ok = False
    policy = json.loads((ROOT / "data/publisher-governance-policy.json").read_text(encoding="utf-8"))
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT,
        PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
        PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
        PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    ):
        error("publisher status must be blocked_until_evidence_posture_protocol_v1_draft_validation or interface thesis validation")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0064" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0064 missing")
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
            validate_protocol_page,
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
