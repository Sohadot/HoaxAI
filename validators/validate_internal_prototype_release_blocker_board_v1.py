#!/usr/bin/env python3
"""Validate Sprint 81 — Internal Prototype Release Blocker Board v1."""

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

BOARD = "INTERNAL_PROTOTYPE_RELEASE_BLOCKER_BOARD_V1.md"
TAXONOMY = "INTERNAL_PROTOTYPE_RELEASE_BLOCKER_TAXONOMY_V1.md"
DENIAL = "INTERNAL_PROTOTYPE_PUBLIC_EXPOSURE_DENIAL_POLICY_V1.md"
CLEARANCE = "INTERNAL_PROTOTYPE_RELEASE_BLOCKER_CLEARANCE_CRITERIA_V1.md"
BOARD_JSON = "data/internal-prototype-release-blocker-board-v1.json"
BOARD_SCHEMA = "data/internal-prototype-release-blocker-board-v1.schema.json"
AUDIT = "SPRINT_81_INTERNAL_PROTOTYPE_RELEASE_BLOCKER_BOARD_V1.md"
FIXTURES_JSON = "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
BOARD_FILES = [
    PROTOTYPE_DIR / "release_blocker_board.py",
    PROTOTYPE_DIR / "release_blocker_harness.py",
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
    "admissibility_regression_harness.py",
    "release_blocker_board.py",
    "release_blocker_harness.py",
}
CODE_SCAN_EXEMPT = PHRASE_SCAN_EXEMPT
REQUIRED_BLOCKER_STATEMENTS = [
    "no public route authorization",
    "no public output generator authorization",
    "no input system authorization",
    "no upload behavior authorization",
    "no scoring authorization",
    "no public report authorization",
    "no benchmark authorization",
    "no real-world case authorization",
    "no external data authorization",
    "no public release clearance mechanism yet",
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
    BOARD,
    TAXONOMY,
    DENIAL,
    CLEARANCE,
    BOARD_JSON,
    BOARD_SCHEMA,
    "internal/prototypes/controlled-engine-v0/release_blocker_board.py",
    "internal/prototypes/controlled-engine-v0/release_blocker_harness.py",
    AUDIT,
    "validators/validate_internal_prototype_release_blocker_board_v1.py",
]
REQUIRED_FIXTURE_COUNT = 16
REQUIRED_BLOCKER_COUNT = 20


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [BOARD, TAXONOMY, DENIAL, CLEARANCE, BOARD_JSON, BOARD_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in BOARD_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_board_json() -> bool:
    ok = True
    data = load_json(BOARD_JSON)
    _ = load_json(BOARD_SCHEMA)
    if data.get("board_id") != "internal-prototype-release-blocker-board-v1":
        error("board_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-099":
        error("decision_ref must be DEC-099")
        ok = False
    if data.get("sprint") != "Sprint 81":
        error("sprint must be Sprint 81")
        ok = False
    if data.get("status") != "internal_non_public_release_blocker_board":
        error("status mismatch")
        ok = False
    for key in [
        "release_authorized",
        "public_route_authorized",
        "public_benchmark_authorized",
        "public_report_authorized",
        "output_generator_authorized",
        "input_system_authorized",
        "upload_authorized",
        "scoring_authorized",
        "api_authorized",
        "javascript_authorized",
        "monetization_authorized",
    ]:
        if data.get(key) is not False:
            error(f"{key} must be false")
            ok = False
    blockers = data.get("blockers", [])
    if len(blockers) < REQUIRED_BLOCKER_COUNT:
        error(f"at least {REQUIRED_BLOCKER_COUNT} blockers required")
        ok = False
    statements = " ".join(b.get("blocker_statement", "") for b in blockers).lower()
    for item in REQUIRED_BLOCKER_STATEMENTS:
        if item not in statements:
            error(f"blockers missing {item}")
            ok = False
    for blocker in blockers:
        if blocker.get("current_status") != "unresolved":
            error(f"blocker {blocker.get('blocker_id')} must remain unresolved")
            ok = False
        if blocker.get("public_exposure_allowed") is not False:
            error(f"blocker {blocker.get('blocker_id')} must deny public exposure")
            ok = False
        sprint = str(blocker.get("authorized_clearance_sprint", "")).lower()
        if "future" not in sprint and "explicit" not in sprint:
            error(f"blocker {blocker.get('blocker_id')} must require explicit future authorization")
            ok = False
    boundaries = data.get("operational_boundaries", {})
    for key in [
        "no_public_route",
        "no_public_report",
        "no_public_engine",
        "no_output_generator",
        "no_input_system",
        "no_upload",
        "no_scoring",
        "no_api",
        "no_javascript",
        "no_public_tool_behavior",
    ]:
        if boundaries.get(key) is not True:
            error(f"operational_boundaries missing {key}")
            ok = False
    if "does not clear" not in data.get("non_release_statement", "").lower():
        error("non_release_statement must deny clearance in Sprint 81")
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


def validate_board_code() -> bool:
    ok = True
    for path in list(PROTOTYPE_DIR.rglob("*.py")):
        if path.name in CODE_SCAN_EXEMPT:
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        phrase_scan = path.name not in PHRASE_SCAN_EXEMPT
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
        "release_blocker_harness.py",
        "controlled internal release blocker board validation passed",
    ):
        ok = False
    if not _run_harness(
        "admissibility_regression_harness.py",
        "controlled internal admissibility regression validation passed",
    ):
        ok = False
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


def validate_no_output_files() -> bool:
    before = {p.name for p in PROTOTYPE_DIR.glob("*") if p.is_file()}
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / "release_blocker_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    after = {p.name for p in PROTOTYPE_DIR.glob("*") if p.is_file()}
    if proc.returncode != 0:
        error("release blocker harness failed during output-file check")
        return False
    if before != after:
        error("release blocker harness must not create output files")
        return False
    return True


def validate_governance() -> bool:
    ok = True
    if "DEC-099" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-099 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_prototype_release_blocker_board_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 81 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0083" for c in claims):
        error("CLAIM-0083 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0076" for g in gates):
        error("PUB-GATE-0076 missing")
        ok = False
    if "Sprint 81 | COMPLETE | G81 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 81 completion row")
        ok = False
    for rel in [BOARD, TAXONOMY, DENIAL, CLEARANCE, AUDIT]:
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
            validate_board_json,
            validate_surface,
            validate_fixtures_unchanged,
            validate_board_code,
            validate_harnesses,
            validate_no_output_files,
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
