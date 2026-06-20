#!/usr/bin/env python3
"""Validate Sprint 77 — Internal Prototype Compound Boundary Stress Test v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
)

STRESS_TEST = "INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_V1.md"
STRESS_MATRIX = "INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_MATRIX_V1.md"
COLLAPSE_MODEL = "INTERNAL_PROTOTYPE_BOUNDARY_COLLAPSE_PREVENTION_MODEL_V1.md"
STRESS_JSON = "data/internal-prototype-compound-boundary-stress-test-v1.json"
STRESS_SCHEMA = "data/internal-prototype-compound-boundary-stress-test-v1.schema.json"
AUDIT = "SPRINT_77_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_V1.md"
FIXTURES_JSON = "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
STRESS_FILES = [
    PROTOTYPE_DIR / "compound_boundary_stress_analyzer.py",
    PROTOTYPE_DIR / "compound_boundary_stress_harness.py",
]

FORBIDDEN_NETWORK = ["requests", "urllib.request", "httpx", "aiohttp", "socket"]
FORBIDDEN_INPUT = ["input(", "argparse", "click", "typer"]
FORBIDDEN_FRAMEWORKS = ["flask", "fastapi", "django", "streamlit", "gradio", "dash", "notebook"]
FORBIDDEN_REPORTING = ["reportlab", "csv.writer", "openpyxl", "xlsxwriter", "pdf"]
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
SOURCE_LOCS = [
    STRESS_TEST,
    STRESS_MATRIX,
    COLLAPSE_MODEL,
    STRESS_JSON,
    STRESS_SCHEMA,
    "internal/prototypes/controlled-engine-v0/compound_boundary_stress_analyzer.py",
    "internal/prototypes/controlled-engine-v0/compound_boundary_stress_harness.py",
    AUDIT,
    "validators/validate_internal_prototype_compound_boundary_stress_test_v1.py",
]
REQUIRED_FIXTURE_COUNT = 16


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [STRESS_TEST, STRESS_MATRIX, COLLAPSE_MODEL, STRESS_JSON, STRESS_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in STRESS_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_stress_json() -> bool:
    ok = True
    data = load_json(STRESS_JSON)
    _ = load_json(STRESS_SCHEMA)
    if data.get("stress_test_id") != "internal-prototype-compound-boundary-stress-test-v1":
        error("stress_test_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-095":
        error("decision_ref must be DEC-095")
        ok = False
    if data.get("sprint") != "Sprint 77":
        error("sprint must be Sprint 77")
        ok = False
    if data.get("status") != "internal_non_public_compound_boundary_stress_test":
        error("status mismatch")
        ok = False
    for key in [
        "public_route_authorized",
        "public_benchmark_authorized",
        "public_report_authorized",
        "output_generator_authorized",
        "scoring_authorized",
        "api_authorized",
        "javascript_authorized",
    ]:
        if data.get(key) is not False:
            error(f"{key} must be false")
            ok = False
    if len(data.get("stress_cases", [])) < 8:
        error("stress_cases must define at least 8 cases")
        ok = False
    if data.get("fixture_count") != REQUIRED_FIXTURE_COUNT:
        error("fixture_count must remain 16")
        ok = False
    return ok


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
    if any("internal/prototypes" in x for x in locs):
        error("sitemap must not reference internal prototypes")
        ok = False
    leak_pat = re.compile(r"internal/prototypes|internal_prototypes", re.I)
    for rel in ALLOWED_PUBLIC_HTML:
        if leak_pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"public page links to internal prototype: {rel}")
            ok = False
    return ok


def validate_fixtures_unchanged() -> bool:
    ok = True
    fixtures = load_json(FIXTURES_JSON).get("fixtures", [])
    if len(fixtures) != REQUIRED_FIXTURE_COUNT:
        error(f"fixture count must remain {REQUIRED_FIXTURE_COUNT}, got {len(fixtures)}")
        ok = False
    expansion = [f for f in fixtures if f.get("coverage_gap_ref")]
    if len(expansion) != 6:
        error("no new fixtures may be added beyond Sprint 76 expansion set")
        ok = False
    return ok


def validate_stress_code() -> bool:
    ok = True
    for path in list(PROTOTYPE_DIR.rglob("*.py")):
        if path.name in {"admissibility_regression_suite.py", "admissibility_regression_harness.py", "release_blocker_board.py", "release_blocker_harness.py"}:
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        phrase_scan = path.name not in {"output_guardrail_checker.py", "guardrail_regression.py", "guardrail_red_team_pack.py", "output_admissibility_contract.py", "output_admissibility_harness.py"}
        for term in FORBIDDEN_NETWORK + FORBIDDEN_INPUT + FORBIDDEN_FRAMEWORKS:
            if term in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden pattern: {term}")
                ok = False
        for term in FORBIDDEN_REPORTING:
            if term in lower and "public_report" not in lower and "report_generation" not in lower:
                error(f"{path.relative_to(ROOT)} contains report/export behavior: {term}")
                ok = False
        for phrase in FORBIDDEN_PHRASES:
            if phrase_scan and phrase in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")
                ok = False
    return ok


def _run_harness(rel: str, expected: str) -> bool:
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / rel)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        error(f"{rel} failed: {proc.stderr or proc.stdout}")
        return False
    out = (proc.stdout or "").strip().lower()
    if out != expected:
        error(f"{rel} must print only safe controlled validation language")
        return False
    return True


def validate_harnesses() -> bool:
    ok = True
    if not _run_harness(
        "compound_boundary_stress_harness.py",
        "controlled internal compound boundary stress validation passed",
    ):
        ok = False
    if not _run_harness(
        "targeted_fixture_expansion_harness.py",
        "controlled internal targeted fixture expansion validation passed",
    ):
        ok = False
    if not _run_harness(
        "fixture_coverage_harness.py",
        "controlled internal fixture coverage validation passed",
    ):
        ok = False
    if not _run_harness(
        "traceability_harness.py",
        "controlled internal traceability validation passed",
    ):
        ok = False
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / "regression_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        error(f"regression_harness failed: {proc.stderr or proc.stdout}")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-095" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-095 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_prototype_compound_boundary_stress_test_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 77 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0079" for c in claims):
        error("CLAIM-0079 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0072" for g in gates):
        error("PUB-GATE-0072 missing")
        ok = False
    if "Sprint 77 | COMPLETE | G77 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 77 completion row")
        ok = False
    for rel in [STRESS_TEST, STRESS_MATRIX, COLLAPSE_MODEL, AUDIT]:
        lower = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in lower:
                error(f"{rel} contains forbidden term: {term}")
                ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
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
            validate_artifacts,
            validate_stress_json,
            validate_surface,
            validate_fixtures_unchanged,
            validate_stress_code,
            validate_harnesses,
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
