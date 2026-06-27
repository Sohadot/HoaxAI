#!/usr/bin/env python3
"""Validate Sprint 82 — Public Exposure Prerequisite Map v1."""

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

MAP = "PUBLIC_EXPOSURE_PREREQUISITE_MAP_V1.md"
TAXONOMY = "PUBLIC_EXPOSURE_PREREQUISITE_TAXONOMY_V1.md"
PATHWAY = "PUBLIC_EXPOSURE_CLEARANCE_PATHWAY_MODEL_V1.md"
SHORTCUTS = "PUBLIC_EXPOSURE_PROHIBITED_SHORTCUTS_V1.md"
MAP_JSON = "data/public-exposure-prerequisite-map-v1.json"
MAP_SCHEMA = "data/public-exposure-prerequisite-map-v1.schema.json"
AUDIT = "SPRINT_82_PUBLIC_EXPOSURE_PREREQUISITE_MAP_V1.md"
FIXTURES_JSON = "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
MAP_FILES = [
    PROTOTYPE_DIR / "public_exposure_prerequisite_map.py",
    PROTOTYPE_DIR / "public_exposure_prerequisite_harness.py",
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
    "public_exposure_prerequisite_map.py",
    "public_exposure_prerequisite_harness.py",
}
CODE_SCAN_EXEMPT = PHRASE_SCAN_EXEMPT
REQUIRED_PREREQUISITE_STATEMENTS = [
    "public route governance prerequisite",
    "public copy boundary prerequisite",
    "output-shape denial prerequisite",
    "no-score public language prerequisite",
    "no-verdict public language prerequisite",
    "no-detector positioning prerequisite",
    "claim-boundary review prerequisite",
    "source-governance review prerequisite",
    "abuse-case review prerequisite",
    "safety review prerequisite",
    "privacy review prerequisite",
    "real-world case exclusion prerequisite",
    "upload-denial prerequisite",
    "input-system-denial prerequisite",
    "API-denial prerequisite",
    "external-data-denial prerequisite",
    "rollback plan prerequisite",
    "monitoring plan prerequisite",
    "accessibility prerequisite",
    "performance prerequisite",
    "security prerequisite",
    "public documentation prerequisite",
    "monetization denial prerequisite",
    "explicit future authorization prerequisite",
]
REQUIRED_SHORTCUTS = [
    "internal validation is not public readiness",
    "passing harnesses is not release clearance",
    "github pages deployment is not prototype release",
    "dns activation is not prototype release",
    "custom domain activation is not prototype release",
    "public homepage is not engine authorization",
    "marketing need is not blocker clearance",
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
    MAP,
    TAXONOMY,
    PATHWAY,
    SHORTCUTS,
    MAP_JSON,
    MAP_SCHEMA,
    "internal/prototypes/controlled-engine-v0/public_exposure_prerequisite_map.py",
    "internal/prototypes/controlled-engine-v0/public_exposure_prerequisite_harness.py",
    AUDIT,
    "validators/validate_public_exposure_prerequisite_map_v1.py",
]
REQUIRED_FIXTURE_COUNT = 16
REQUIRED_PREREQUISITE_COUNT = 24


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [MAP, TAXONOMY, PATHWAY, SHORTCUTS, MAP_JSON, MAP_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in MAP_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_map_json() -> bool:
    ok = True
    data = load_json(MAP_JSON)
    _ = load_json(MAP_SCHEMA)
    if data.get("prerequisite_map_id") != "public-exposure-prerequisite-map-v1":
        error("prerequisite_map_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-100":
        error("decision_ref must be DEC-100")
        ok = False
    if data.get("sprint") != "Sprint 82":
        error("sprint must be Sprint 82")
        ok = False
    if data.get("status") != "internal_non_public_public_exposure_prerequisite_map":
        error("status mismatch")
        ok = False
    for key in [
        "public_exposure_authorized",
        "blocker_clearance_authorized",
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
    prerequisites = data.get("prerequisites", [])
    if len(prerequisites) < REQUIRED_PREREQUISITE_COUNT:
        error(f"at least {REQUIRED_PREREQUISITE_COUNT} prerequisites required")
        ok = False
    statements = " ".join(p.get("prerequisite_statement", "") for p in prerequisites).lower()
    for item in REQUIRED_PREREQUISITE_STATEMENTS:
        if item.lower() not in statements:
            error(f"prerequisites missing {item}")
            ok = False
    for item in prerequisites:
        if item.get("current_status") == "cleared":
            error(f"prerequisite {item.get('prerequisite_id')} must not be cleared")
            ok = False
        if item.get("public_exposure_authorized") is not False:
            error(f"prerequisite {item.get('prerequisite_id')} must deny public exposure")
            ok = False
    shortcuts = " ".join(data.get("prohibited_shortcuts", [])).lower()
    for item in REQUIRED_SHORTCUTS:
        if item not in shortcuts:
            error(f"prohibited_shortcuts missing {item}")
            ok = False
    pathway = " ".join(data.get("clearance_pathway_rules", [])).lower()
    if "explicit" not in pathway and "future" not in pathway:
        error("clearance pathway must require explicit future sprint authorization")
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


def validate_map_code() -> bool:
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
        "public_exposure_prerequisite_harness.py",
        "controlled internal public exposure prerequisite map validation passed",
    ):
        ok = False
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
        [sys.executable, str(PROTOTYPE_DIR / "public_exposure_prerequisite_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    after = {p.name for p in PROTOTYPE_DIR.glob("*") if p.is_file()}
    if proc.returncode != 0:
        error("public exposure prerequisite harness failed during output-file check")
        return False
    if before != after:
        error("public exposure prerequisite harness must not create output files")
        return False
    return True


def validate_governance() -> bool:
    ok = True
    if "DEC-100" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-100 missing from DECISION_LOG.md")
        ok = False
    if "validate_public_exposure_prerequisite_map_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 82 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0084" for c in claims):
        error("CLAIM-0084 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0077" for g in gates):
        error("PUB-GATE-0077 missing")
        ok = False
    if "Sprint 82 | COMPLETE | G82 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 82 completion row")
        ok = False
    for rel in [MAP, TAXONOMY, PATHWAY, SHORTCUTS, AUDIT]:
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
            validate_map_json,
            validate_surface,
            validate_fixtures_unchanged,
            validate_map_code,
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
