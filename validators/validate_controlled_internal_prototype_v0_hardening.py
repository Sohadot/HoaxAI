#!/usr/bin/env python3
"""Validate Sprint 73 — Controlled Internal Prototype v0 Hardening and Fixture Coverage."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    validate_public_surface,
)

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
FIXTURES_JSON = PROTOTYPE_DIR / "fixtures" / "synthetic-fixtures-v0.json"
AUDIT = "SPRINT_73_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_AUDIT.md"

REQUIRED_PROTOTYPE_FILES = [
    "README.md",
    "prototype_scope.md",
    "README_BOUNDARIES.md",
    "HARDENING_COVERAGE.md",
    "fixtures/synthetic-fixtures-v0.json",
    "model_loader.py",
    "fixture_loader.py",
    "protocol_mapper.py",
    "boundary_evaluator.py",
    "caveat_mapper.py",
    "output_guardrail_checker.py",
    "prototype_core.py",
    "validation_harness.py",
    "guardrail_regression.py",
    "regression_harness.py",
]

EDGE_FIXTURE_IDS = [
    "SYN-FIX-006-ATTRIBUTION-BOUNDARY",
    "SYN-FIX-007-PROVENANCE-GAP",
    "SYN-FIX-008-CONTEXT-COLLAPSE",
    "SYN-FIX-009-CLAIM-DRIFT",
    "SYN-FIX-010-LIMITATION-NOT-FALSEHOOD",
]

FORBIDDEN_NETWORK = ["requests", "urllib.request", "httpx", "aiohttp", "socket"]
FORBIDDEN_INPUT = ["input(", "argparse", "click", "typer"]
FORBIDDEN_FRAMEWORKS = ["flask", "fastapi", "django", "streamlit", "gradio", "dash"]
FORBIDDEN_PHRASES = [
    "is fake",
    "is real",
    "verified true",
    "verified false",
    "confidence score",
    "detection result",
    "fraudulent",
    "guilty",
    "deceptive",
]
FORBIDDEN_TERMS = [
    "rick",
    "linkedin",
    "cloudflare",
    "domain owner",
    "buyer outreach",
    "marketing conversations",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "internal/prototypes/controlled-engine-v0/HARDENING_COVERAGE.md",
    "internal/prototypes/controlled-engine-v0/guardrail_regression.py",
    "internal/prototypes/controlled-engine-v0/regression_harness.py",
    "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json",
    AUDIT,
    "validators/validate_controlled_internal_prototype_v0_hardening.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_prototype_files() -> bool:
    ok = True
    if not PROTOTYPE_DIR.is_dir():
        error("internal/prototypes/controlled-engine-v0 must exist")
        return False
    for rel in REQUIRED_PROTOTYPE_FILES:
        if not (PROTOTYPE_DIR / rel).is_file():
            error(f"missing prototype file: {rel}")
            ok = False
    for path in PROTOTYPE_DIR.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        phrase_scan = path.name not in ("output_guardrail_checker.py", "guardrail_regression.py")
        for term in FORBIDDEN_NETWORK + FORBIDDEN_INPUT + FORBIDDEN_FRAMEWORKS:
            if term in text:
                error(f"{path.relative_to(ROOT)} contains forbidden pattern: {term}")
                ok = False
        for phrase in FORBIDDEN_PHRASES:
            if phrase_scan and phrase in text:
                error(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")
                ok = False
    hardening = (PROTOTYPE_DIR / "HARDENING_COVERAGE.md").read_text(encoding="utf-8").lower()
    if "10 synthetic fixtures" not in hardening:
        error("HARDENING_COVERAGE.md must document 10 synthetic fixtures")
        ok = False
    if "guardrail_regression" not in hardening:
        error("HARDENING_COVERAGE.md must reference guardrail regression")
        ok = False
    guardrail = (PROTOTYPE_DIR / "output_guardrail_checker.py").read_text(encoding="utf-8").lower()
    if "prohibited_marker" not in guardrail:
        error("output guardrail must include strengthened failure detection")
        ok = False
    return ok


def validate_fixtures() -> bool:
    ok = True
    data = json.loads(FIXTURES_JSON.read_text(encoding="utf-8"))
    fixtures = data.get("fixtures", [])
    if len(fixtures) < 10:
        error("fixture set must contain at least 10 fixtures")
        ok = False
    ids = {f.get("fixture_id") for f in fixtures}
    for edge_id in EDGE_FIXTURE_IDS:
        if edge_id not in ids:
            error(f"missing edge-case fixture: {edge_id}")
            ok = False
    if data.get("version") != "0.2.0":
        error("fixture set version must be 0.2.0 after hardening")
        ok = False
    return ok


def validate_regression() -> bool:
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / "regression_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        error(f"regression_harness failed: {proc.stderr or proc.stdout}")
        return False
    out = (proc.stdout or "").lower()
    if "controlled internal prototype hardening validation passed" not in out:
        error("regression_harness must print hardening validation passed message")
        return False
    return True


def validate_surface() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    leak_pat = re.compile(r"internal/prototypes|internal_prototypes", re.I)
    for rel in ALLOWED_PUBLIC_HTML:
        if leak_pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"public page links to internal prototype: {rel}")
            ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("locked prototype files modified")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-091" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-091 missing from DECISION_LOG.md")
        ok = False
    if "validate_controlled_internal_prototype_v0_hardening.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 73 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") != PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION:
        error("publisher status must be blocked_until_controlled_internal_prototype_v0_hardening_validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0075"
        for c in load_json("data/evidence-ledger.json").get("claims", [])
    ):
        error("CLAIM-0075 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0068" for g in gates):
        error("PUB-GATE-0068 missing")
        ok = False
    if "Sprint 73 | COMPLETE | G73 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 73 completion row")
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
            validate_prototype_files,
            validate_fixtures,
            validate_regression,
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
