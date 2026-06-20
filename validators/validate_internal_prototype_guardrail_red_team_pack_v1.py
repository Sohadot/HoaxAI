#!/usr/bin/env python3
"""Validate Sprint 78 — Internal Prototype Guardrail Red-Team Pack v1."""

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

RED_TEAM_PACK = "INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_V1.md"
VECTOR_MATRIX = "INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_VECTOR_MATRIX_V1.md"
COLLAPSE_MODEL = "INTERNAL_PROTOTYPE_FORBIDDEN_LANGUAGE_COLLAPSE_MODEL_V1.md"
RESULTS_POLICY = "INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_RESULTS_POLICY_V1.md"
RED_TEAM_JSON = "data/internal-prototype-guardrail-red-team-pack-v1.json"
RED_TEAM_SCHEMA = "data/internal-prototype-guardrail-red-team-pack-v1.schema.json"
AUDIT = "SPRINT_78_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_V1.md"
FIXTURES_JSON = "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
RED_TEAM_FILES = [
    PROTOTYPE_DIR / "guardrail_red_team_pack.py",
    PROTOTYPE_DIR / "guardrail_red_team_harness.py",
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
PHRASE_SCAN_EXEMPT = {
    "output_guardrail_checker.py",
    "guardrail_regression.py",
    "guardrail_red_team_pack.py",
    "output_admissibility_contract.py",
    "output_admissibility_harness.py",
    "admissibility_regression_suite.py",
    "admissibility_regression_harness.py",
}
REQUIRED_COLLAPSE_TARGETS = [
    "is fake",
    "is real",
    "verified true",
    "verified false",
    "confidence score",
    "detection result",
    "fraudulent",
    "guilty",
    "deceptive",
    "manipulated",
    "proven",
    "certified",
    "confirmed",
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
    RED_TEAM_PACK,
    VECTOR_MATRIX,
    COLLAPSE_MODEL,
    RESULTS_POLICY,
    RED_TEAM_JSON,
    RED_TEAM_SCHEMA,
    "internal/prototypes/controlled-engine-v0/guardrail_red_team_pack.py",
    "internal/prototypes/controlled-engine-v0/guardrail_red_team_harness.py",
    AUDIT,
    "validators/validate_internal_prototype_guardrail_red_team_pack_v1.py",
]
REQUIRED_FIXTURE_COUNT = 16


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [RED_TEAM_PACK, VECTOR_MATRIX, COLLAPSE_MODEL, RESULTS_POLICY, RED_TEAM_JSON, RED_TEAM_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in RED_TEAM_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_red_team_json() -> bool:
    ok = True
    data = load_json(RED_TEAM_JSON)
    _ = load_json(RED_TEAM_SCHEMA)
    if data.get("red_team_pack_id") != "internal-prototype-guardrail-red-team-pack-v1":
        error("red_team_pack_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-096":
        error("decision_ref must be DEC-096")
        ok = False
    if data.get("sprint") != "Sprint 78":
        error("sprint must be Sprint 78")
        ok = False
    if data.get("status") != "internal_non_public_guardrail_red_team_pack":
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
    if len(data.get("red_team_vectors", [])) < 16:
        error("red_team_vectors must define at least 16 vectors")
        ok = False
    targets = " ".join(data.get("forbidden_collapse_targets", [])).lower()
    for target in REQUIRED_COLLAPSE_TARGETS:
        if target not in targets:
            error(f"forbidden_collapse_targets missing {target}")
            ok = False
    if data.get("allowed_internal_validation_output") != "controlled internal guardrail red-team validation passed":
        error("allowed_internal_validation_output mismatch")
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


def validate_red_team_code() -> bool:
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
    if "DEC-096" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-096 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_prototype_guardrail_red_team_pack_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 78 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0080" for c in claims):
        error("CLAIM-0080 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0073" for g in gates):
        error("PUB-GATE-0073 missing")
        ok = False
    if "Sprint 78 | COMPLETE | G78 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 78 completion row")
        ok = False
    for rel in [RED_TEAM_PACK, VECTOR_MATRIX, COLLAPSE_MODEL, RESULTS_POLICY, AUDIT]:
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
            validate_red_team_json,
            validate_surface,
            validate_fixtures_unchanged,
            validate_red_team_code,
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
