#!/usr/bin/env python3
"""Validate Sprint 72 — Controlled Internal Prototype v0 Implementation."""

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
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    validate_public_surface,
)

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
FIXTURES_JSON = PROTOTYPE_DIR / "fixtures" / "synthetic-fixtures-v0.json"
AUDIT = "SPRINT_72_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_AUDIT.md"

REQUIRED_PROTOTYPE_FILES = [
    "README.md",
    "prototype_scope.md",
    "README_BOUNDARIES.md",
    "fixtures/synthetic-fixtures-v0.json",
    "model_loader.py",
    "fixture_loader.py",
    "protocol_mapper.py",
    "boundary_evaluator.py",
    "caveat_mapper.py",
    "output_guardrail_checker.py",
    "prototype_core.py",
    "validation_harness.py",
]

REQUIRED_RESULT_KEYS = {
    "fixture_id",
    "posture_state_candidate",
    "active_boundary_checks",
    "triggered_caveats",
    "prohibited_language_blocks",
    "required_output_constraints",
    "not_assessable_reason",
    "out_of_scope_reason",
    "guardrail_failure_flags",
    "validation_status",
}

REQUIRED_POSTURES = {"Supported", "Qualified", "Limited", "Not Assessable", "Out of Scope"}

FIXTURE_FLAGS = {
    "synthetic": True,
    "real_person": False,
    "current_event": False,
    "political": False,
    "legal": False,
    "medical": False,
    "financial_advice": False,
    "company_accusatory": False,
    "private_data": False,
    "external_fact_check_target": False,
}

FORBIDDEN_NETWORK = [
    "requests",
    "urllib.request",
    "httpx",
    "aiohttp",
    "socket",
]

FORBIDDEN_INPUT = [
    "input(",
    "argparse",
    "click",
    "typer",
]

FORBIDDEN_FRAMEWORKS = [
    "flask",
    "fastapi",
    "django",
    "streamlit",
    "gradio",
    "dash",
]

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
    "internal/prototypes/controlled-engine-v0/README.md",
    "internal/prototypes/controlled-engine-v0/prototype_scope.md",
    "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json",
    "internal/prototypes/controlled-engine-v0/prototype_core.py",
    "internal/prototypes/controlled-engine-v0/validation_harness.py",
    AUDIT,
    "validators/validate_controlled_internal_prototype_v0_implementation.py",
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
    py_files = list(PROTOTYPE_DIR.rglob("*.py"))
    for path in py_files:
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        phrase_scan = path.name != "output_guardrail_checker.py"
        for term in FORBIDDEN_NETWORK + FORBIDDEN_INPUT + FORBIDDEN_FRAMEWORKS:
            if term in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden pattern: {term}")
                ok = False
        for phrase in FORBIDDEN_PHRASES:
            if phrase_scan and phrase in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")
                ok = False
        for term in FORBIDDEN_TERMS:
            if term in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden term: {term}")
                ok = False
    for rel in SOURCE_LOCS[:5]:
        if (ROOT / rel).is_file():
            lower = (ROOT / rel).read_text(encoding="utf-8").lower()
            for term in FORBIDDEN_TERMS:
                if term in lower:
                    error(f"{rel} contains forbidden term: {term}")
                    ok = False
    core = (PROTOTYPE_DIR / "prototype_core.py").read_text(encoding="utf-8")
    for key in REQUIRED_RESULT_KEYS:
        if key not in core:
            error(f"prototype_core.py must reference result key: {key}")
            ok = False
    guardrail = (PROTOTYPE_DIR / "output_guardrail_checker.py").read_text(encoding="utf-8").lower()
    for item in ["fake/real verdict", "confidence percentage", "subject guilt"]:
        if item not in guardrail:
            error(f"output_guardrail_checker.py must block: {item}")
            ok = False
    return ok


def validate_fixtures() -> bool:
    ok = True
    if not FIXTURES_JSON.is_file():
        error("synthetic fixtures missing")
        return False
    data = json.loads(FIXTURES_JSON.read_text(encoding="utf-8"))
    fixtures = data.get("fixtures", [])
    if len(fixtures) < 5:
        error("fixtures must contain at least 5 entries")
        ok = False
    seen_postures: set[str] = set()
    marker_pat = re.compile(
        r"\b(president|senator|ceo|celebrity|bitcoin|covid|election|lawsuit|fraud scandal)\b",
        re.I,
    )
    for fixture in fixtures:
        for key, expected in FIXTURE_FLAGS.items():
            if fixture.get(key) is not expected:
                error(f"fixture {fixture.get('fixture_id')} invalid flag {key}")
                ok = False
        blob = json.dumps(fixture)
        if marker_pat.search(blob):
            error(f"fixture {fixture.get('fixture_id')} contains prohibited marker")
            ok = False
        for posture in fixture.get("expected_allowed_posture_states", []):
            seen_postures.add(posture)
    if not REQUIRED_POSTURES.issubset(seen_postures):
        error("fixtures must cover all required posture states")
        ok = False
    return ok


def validate_harness() -> bool:
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / "validation_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        error(f"validation_harness failed: {proc.stderr or proc.stdout}")
        return False
    out = (proc.stdout or "").lower()
    if "controlled internal prototype validation passed" not in out:
        error("validation_harness must print controlled internal prototype validation passed")
        return False
    forbidden_out = ["is fake", "is real", "confidence score", "detection result", "fraudulent"]
    for phrase in forbidden_out:
        if phrase in out:
            error(f"validation_harness printed forbidden phrase: {phrase}")
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
    if any("internal/prototypes" in x or "internal_prototypes" in x for x in locs):
        error("sitemap must not reference internal prototypes")
        ok = False
    forbidden_paths = ["/engine/", "/tool/", "/scanner/", "/api/", "/dashboard/", "/upload/", "/score/"]
    registered = {r.get("path") for r in routes}
    for path in forbidden_paths:
        if path in registered:
            error(f"forbidden route registered: {path}")
            ok = False
    leak_pat = re.compile(r"internal/prototypes|internal_prototypes", re.I)
    for rel in ALLOWED_PUBLIC_HTML:
        if leak_pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"public page links to internal prototype: {rel}")
            ok = False
    js_added = [
        p
        for p in ROOT.rglob("*")
        if p.suffix.lower() == ".js"
        and "internal/prototypes/controlled-engine-v0" in str(p).replace("\\", "/")
    ]
    if js_added:
        error("prototype JavaScript files must not be added")
        ok = False
    if not all((ROOT / x).is_file() for x in LOCKED_FILES):
        error("locked prototype files missing")
        ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("locked prototype files modified")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("locked prototype files staged")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-090" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-090 missing from DECISION_LOG.md")
        ok = False
    if "validate_controlled_internal_prototype_v0_implementation.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 72 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0074"
        for c in load_json("data/evidence-ledger.json").get("claims", [])
    ):
        error("CLAIM-0074 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0067" for g in gates):
        error("PUB-GATE-0067 missing")
        ok = False
    if "Sprint 72 | COMPLETE | G72 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 72 completion row")
        ok = False
    if not (ROOT / AUDIT).is_file():
        error(f"missing {AUDIT}")
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
            validate_harness,
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
