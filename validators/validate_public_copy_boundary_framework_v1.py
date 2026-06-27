#!/usr/bin/env python3
"""Validate Sprint 83 — Public Copy Boundary Framework v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
)

FRAMEWORK = "PUBLIC_COPY_BOUNDARY_FRAMEWORK_V1.md"
UTILITY = "PUBLIC_UTILITY_LANGUAGE_STANDARD_V1.md"
HERO = "PUBLIC_HERO_COPY_MODEL_V1.md"
PREVENTION = "PUBLIC_DETECTOR_MISREADING_PREVENTION_V1.md"
FRAMEWORK_JSON = "data/public-copy-boundary-framework-v1.json"
FRAMEWORK_SCHEMA = "data/public-copy-boundary-framework-v1.schema.json"
AUDIT = "SPRINT_83_PUBLIC_COPY_BOUNDARY_FRAMEWORK_V1.md"
INDEX = "index.html"

REQUIRED_HERO_PHRASES = [
    "truth is no longer the first layer",
    "evidence is",
    "without issuing verdicts, scores, uploads, or binary authenticity labels",
]

REQUIRED_UTILITY_PHRASES = [
    "helps people read evidence risk",
    "ask better evidence questions",
    "manual",
    "non-verdict",
]

FORBIDDEN_HOMEPAGE_CLAIMS = [
    "detects fake",
    "ai detector",
    "deepfake detector",
    "upload your",
    "scan your",
    "truth score",
    "authenticity score",
    "confidence score",
    "verifies truth",
    "certifies evidence",
    "confirms real or fake",
    "<form",
    "<script",
    "type=\"file\"",
]

DETECTOR_CLAIM_PATTERNS = [
    re.compile(r"\bdetects\s+(?:fake|synthetic|deepfake)", re.I),
    re.compile(r"\b(?:ai|automated)\s+detector\b", re.I),
]

SOURCE_LOCS = [
    FRAMEWORK,
    UTILITY,
    HERO,
    PREVENTION,
    FRAMEWORK_JSON,
    FRAMEWORK_SCHEMA,
    AUDIT,
    "validators/validate_public_copy_boundary_framework_v1.py",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,40}",
    re.IGNORECASE,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def extract_h1(html: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    return re.sub(r"<[^>]+>", " ", match.group(1)).strip() if match else ""


def line_has_unnegated_term(line: str, term: str) -> bool:
    lower = line.lower()
    if term not in lower:
        return False
    pos = 0
    while True:
        idx = lower.find(term, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 60) : idx]
        if not NEGATION_PATTERN.search(prefix + term):
            return True
        pos = idx + len(term)
    return False


def validate_artifacts() -> bool:
    ok = True
    for rel in [FRAMEWORK, UTILITY, HERO, PREVENTION, FRAMEWORK_JSON, FRAMEWORK_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    if not (ROOT / "validators" / "validate_public_copy_boundary_framework_v1.py").is_file():
        error("missing Sprint 83 validator")
        ok = False
    return ok


def validate_framework_json() -> bool:
    ok = True
    try:
        data = load_json(FRAMEWORK_JSON)
    except json.JSONDecodeError as exc:
        error(f"framework JSON parse error: {exc}")
        return False
    try:
        json.loads((ROOT / FRAMEWORK_SCHEMA).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"framework schema parse error: {exc}")
        ok = False
    if data.get("framework_id") != "public-copy-boundary-framework-v1":
        error("framework_id must be public-copy-boundary-framework-v1")
        ok = False
    if data.get("decision_ref") != "DEC-101":
        error("decision_ref must be DEC-101")
        ok = False
    if data.get("sprint") != "Sprint 83":
        error("sprint must be Sprint 83")
        ok = False
    for key in [
        "public_route_authorized",
        "new_public_routes_authorized",
        "upload_authorized",
        "scoring_authorized",
        "verdict_authorized",
        "detector_claim_authorized",
        "public_api_authorized",
        "automated_report_authorized",
    ]:
        if data.get(key) is not False:
            error(f"{key} must be false")
            ok = False
    for key in ["public_utility_language_authorized", "manual_reference_utility_authorized"]:
        if data.get(key) is not True:
            error(f"{key} must be true")
            ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    path = ROOT / INDEX
    if not path.is_file():
        error("index.html missing")
        return False
    content = path.read_text(encoding="utf-8")
    lower = content.lower()
    h1_text = extract_h1(content).lower()
    if "hoax.ai is not a truth machine" in h1_text:
        error("homepage H1 must not be 'Hoax.ai is not a truth machine.'")
        ok = False
    for phrase in REQUIRED_HERO_PHRASES:
        if phrase not in lower:
            error(f"homepage missing hero phrase: {phrase}")
            ok = False
    utility_hits = sum(1 for p in REQUIRED_UTILITY_PHRASES if p in lower)
    if utility_hits < 3:
        error("homepage missing public utility language")
        ok = False
    for claim in FORBIDDEN_HOMEPAGE_CLAIMS:
        if claim in lower:
            error(f"homepage contains forbidden claim: {claim}")
            ok = False
    for line in content.splitlines():
        line_lower = line.lower()
        for pattern in DETECTOR_CLAIM_PATTERNS:
            if pattern.search(line) and not NEGATION_PATTERN.search(line_lower):
                error(f"homepage detector claim without negation: {line.strip()[:80]}")
                ok = False
    if re.search(r"<script\b", content, re.I):
        error("homepage must not include JavaScript")
        ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [
        e.text.strip().lower()
        for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")
        if e.text
    ]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must remain {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    fixtures = load_json(
        "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"
    ).get("fixtures", [])
    if len(fixtures) != 16:
        error("fixture count must remain 16")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-101" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-101 missing from DECISION_LOG.md")
        ok = False
    if "validate_public_copy_boundary_framework_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 83 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0085" for c in claims):
        error("CLAIM-0085 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0078" for g in gates):
        error("PUB-GATE-0078 missing")
        ok = False
    if "Sprint 83 | COMPLETE | G83 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 83 completion row")
        ok = False
    return ok


def main() -> int:
    ok = all(
        fn()
        for fn in [
            validate_artifacts,
            validate_framework_json,
            validate_homepage,
            validate_surface,
            validate_governance,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
