#!/usr/bin/env python3
"""Validate Sprint 76 — Targeted Synthetic Fixture Expansion v1."""

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
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    validate_public_surface,
)

EXPANSION_DOC = "TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1.md"
ADMISSION_LOG = "TARGETED_FIXTURE_EXPANSION_ADMISSION_LOG_V1.md"
COVERAGE_DELTA = "TARGETED_FIXTURE_EXPANSION_COVERAGE_DELTA_V1.md"
EXPANSION_JSON = "data/targeted-synthetic-fixture-expansion-v1.json"
EXPANSION_SCHEMA = "data/targeted-synthetic-fixture-expansion-v1.schema.json"
AUDIT = "SPRINT_76_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1.md"
FIXTURES_JSON = "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"

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
REQUIRED_EXPANSION_FIELDS = [
    "coverage_gap_ref",
    "expansion_reason",
    "expected_required_caveats",
    "expected_boundary_checks",
    "expected_forbidden_transformations_blocked",
    "expected_traceability_fields",
]
REQUIRED_GAP_TERMS = ["traceability_caveat", "compound boundary"]
SOURCE_LOCS = [
    EXPANSION_DOC,
    ADMISSION_LOG,
    COVERAGE_DELTA,
    EXPANSION_JSON,
    EXPANSION_SCHEMA,
    FIXTURES_JSON,
    "internal/prototypes/controlled-engine-v0/targeted_fixture_expansion_harness.py",
    AUDIT,
    "validators/validate_targeted_synthetic_fixture_expansion_v1.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [EXPANSION_DOC, ADMISSION_LOG, COVERAGE_DELTA, EXPANSION_JSON, EXPANSION_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    harness = PROTOTYPE_DIR / "targeted_fixture_expansion_harness.py"
    if not harness.is_file():
        error("missing targeted_fixture_expansion_harness.py")
        ok = False
    return ok


def validate_expansion_json() -> bool:
    ok = True
    data = load_json(EXPANSION_JSON)
    _ = load_json(EXPANSION_SCHEMA)
    if data.get("expansion_id") != "targeted-synthetic-fixture-expansion-v1":
        error("expansion_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-094":
        error("decision_ref must be DEC-094")
        ok = False
    if data.get("sprint") != "Sprint 76":
        error("sprint must be Sprint 76")
        ok = False
    if data.get("status") != "internal_non_public_targeted_fixture_expansion":
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
    gaps_text = " ".join(data.get("named_coverage_gaps_addressed", [])).lower()
    for term in REQUIRED_GAP_TERMS:
        if term not in gaps_text:
            error(f"named_coverage_gaps_addressed missing {term}")
            ok = False
    if not data.get("fixture_admission_records"):
        error("fixture_admission_records missing")
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


def validate_fixtures() -> bool:
    ok = True
    fixtures = load_json(FIXTURES_JSON).get("fixtures", [])
    count = len(fixtures)
    if count <= 10 or count > 16:
        error(f"fixture count must be >10 and <=16, got {count}")
        ok = False
    expansion = [f for f in fixtures if f.get("coverage_gap_ref")]
    if len(expansion) != count - 10:
        error("every new fixture must include coverage_gap_ref")
        ok = False
    flags = {
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
    for fixture in expansion:
        for field in REQUIRED_EXPANSION_FIELDS:
            if not fixture.get(field):
                error(f"{fixture.get('fixture_id')} missing {field}")
                ok = False
        for flag, expected in flags.items():
            if fixture.get(flag) is not expected:
                error(f"{fixture.get('fixture_id')} failed policy flag {flag}")
                ok = False
    return ok


def validate_prototype_code() -> bool:
    ok = True
    for path in list(PROTOTYPE_DIR.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        phrase_scan = path.name not in {"output_guardrail_checker.py", "guardrail_regression.py", "guardrail_red_team_pack.py"}
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
    if "DEC-094" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-094 missing from DECISION_LOG.md")
        ok = False
    if "validate_targeted_synthetic_fixture_expansion_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 76 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0078" for c in claims):
        error("CLAIM-0078 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0071" for g in gates):
        error("PUB-GATE-0071 missing")
        ok = False
    if "Sprint 76 | COMPLETE | G76 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 76 completion row")
        ok = False
    for rel in [EXPANSION_DOC, ADMISSION_LOG, COVERAGE_DELTA, AUDIT]:
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
            validate_expansion_json,
            validate_surface,
            validate_fixtures,
            validate_prototype_code,
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
