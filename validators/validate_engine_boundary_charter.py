#!/usr/bin/env python3
"""Validate Sprint 67 — Engine Boundary Charter."""

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
    validate_public_surface,
)

CHARTER = "ENGINE_BOUNDARY_CHARTER.md"
AUDIT = "SPRINT_67_ENGINE_BOUNDARY_AND_SEO_AUTHORITY_MAP_AUDIT.md"

REQUIRED_PHRASES = [
    "what any future engine may and may not do",
    "internal asset-quality boundary",
    "exactly nineteen URLs",
    "no public engine",
    "Engine drift",
    "not authorized now",
    "validate_all.py PASS",
    "Engine Model v0",
]

FORBIDDEN_TERMS = [
    "rick",
    "linkedin",
    "cloudflare",
    "domain owner",
    "buyer conversation",
    "marketing notes",
]

SOURCE_LOCS = [
    CHARTER,
    AUDIT,
    "validators/validate_engine_boundary_charter.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def validate_charter() -> bool:
    ok = True
    path = ROOT / CHARTER
    if not path.is_file():
        error(f"missing {CHARTER}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lower:
            error(f"charter missing required phrase: {phrase}")
            ok = False
    for term in FORBIDDEN_TERMS:
        if term in lower:
            error(f"charter contains forbidden term: {term}")
            ok = False
    if "DEC-085" not in text:
        error("charter must reference DEC-085")
        ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-085" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-085 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / AUDIT).is_file():
        error(f"missing {AUDIT}")
        ok = False
    if "validate_engine_boundary_charter.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py must include engine boundary charter validator")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0069"
        for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])
    ):
        error("CLAIM-0069 missing")
        ok = False
    gates = json.loads((ROOT / "data/publisher-quality-gates.json").read_text(encoding="utf-8")).get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0062" for g in gates):
        error("PUB-GATE-0062 missing")
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
    ok = all(fn() for fn in [validate_charter, validate_surface, validate_governance, validate_cache])
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
