#!/usr/bin/env python3
"""Validate Sprint 79 — Internal Prototype Output Admissibility Contract v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
)

CONTRACT = "INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_V1.md"
MATRIX = "INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_MATRIX_V1.md"
FAILURE_MODES = "INTERNAL_PROTOTYPE_OUTPUT_INADMISSIBILITY_FAILURE_MODES_V1.md"
REPAIR_POLICY = "INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_REPAIR_POLICY_V1.md"
CONTRACT_JSON = "data/internal-prototype-output-admissibility-contract-v1.json"
CONTRACT_SCHEMA = "data/internal-prototype-output-admissibility-contract-v1.schema.json"
AUDIT = "SPRINT_79_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_V1.md"
FIXTURES_JSON = "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
CONTRACT_FILES = [
    PROTOTYPE_DIR / "output_admissibility_contract.py",
    PROTOTYPE_DIR / "output_admissibility_harness.py",
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
FORBIDDEN_PHRASE_PATTERNS = [
    re.compile(r"\bmanipulated\b", re.I),
    re.compile(r"\bproven\b", re.I),
    re.compile(r"\bcertified\b", re.I),
    re.compile(r"\bconfirmed\b", re.I),
]
PHRASE_SCAN_EXEMPT = {
    "output_guardrail_checker.py",
    "guardrail_regression.py",
    "guardrail_red_team_pack.py",
    "output_admissibility_contract.py",
    "output_admissibility_harness.py",
    "admissibility_regression_suite.py",
    "admissibility_regression_harness.py", "release_blocker_board.py", "release_blocker_harness.py",
}
REQUIRED_VOCABULARY = ["admissible_internal", "repair_required", "not_assessable_for_output"]
REQUIRED_INADMISSIBILITY = [
    "missing caveats",
    "boundary collapse",
    "guardrail failure",
    "traceability gap",
    "report-shape",
    "score leakage",
    "verdict leakage",
    "accusation-transfer",
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
    CONTRACT,
    MATRIX,
    FAILURE_MODES,
    REPAIR_POLICY,
    CONTRACT_JSON,
    CONTRACT_SCHEMA,
    "internal/prototypes/controlled-engine-v0/output_admissibility_contract.py",
    "internal/prototypes/controlled-engine-v0/output_admissibility_harness.py",
    AUDIT,
    "validators/validate_internal_prototype_output_admissibility_contract_v1.py",
]
REQUIRED_FIXTURE_COUNT = 16


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [CONTRACT, MATRIX, FAILURE_MODES, REPAIR_POLICY, CONTRACT_JSON, CONTRACT_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in CONTRACT_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_contract_json() -> bool:
    ok = True
    data = load_json(CONTRACT_JSON)
    _ = load_json(CONTRACT_SCHEMA)
    if data.get("contract_id") != "internal-prototype-output-admissibility-contract-v1":
        error("contract_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-097":
        error("decision_ref must be DEC-097")
        ok = False
    if data.get("sprint") != "Sprint 79":
        error("sprint must be Sprint 79")
        ok = False
    if data.get("status") != "internal_non_public_output_admissibility_contract":
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
    vocab = data.get("admissibility_status_vocabulary", [])
    for item in REQUIRED_VOCABULARY:
        if item not in vocab:
            error(f"admissibility_status_vocabulary missing {item}")
            ok = False
    conditions = " ".join(data.get("inadmissibility_conditions", [])).lower()
    for item in REQUIRED_INADMISSIBILITY:
        if item not in conditions:
            error(f"inadmissibility_conditions missing {item}")
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


def validate_contract_code() -> bool:
    ok = True
    for path in list(PROTOTYPE_DIR.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        phrase_scan = path.name not in PHRASE_SCAN_EXEMPT
        code_scan = path.name not in PHRASE_SCAN_EXEMPT
        if code_scan:
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
        for pattern in FORBIDDEN_PHRASE_PATTERNS:
            if phrase_scan and pattern.search(text):
                error(f"{path.relative_to(ROOT)} contains forbidden phrase: {pattern.pattern}")
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
        "output_admissibility_harness.py",
        "controlled internal output admissibility validation passed",
    ):
        ok = False
    if not _run_harness(
        "guardrail_red_team_harness.py",
        "controlled internal guardrail red-team validation passed",
    ):
        ok = False
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
    if "DEC-097" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-097 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_prototype_output_admissibility_contract_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 79 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0081" for c in claims):
        error("CLAIM-0081 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0074" for g in gates):
        error("PUB-GATE-0074 missing")
        ok = False
    if "Sprint 79 | COMPLETE | G79 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 79 completion row")
        ok = False
    for rel in [CONTRACT, MATRIX, FAILURE_MODES, REPAIR_POLICY, AUDIT]:
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
            validate_contract_json,
            validate_surface,
            validate_fixtures_unchanged,
            validate_contract_code,
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
