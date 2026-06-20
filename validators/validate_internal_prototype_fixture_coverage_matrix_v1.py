#!/usr/bin/env python3
"""Validate Sprint 75 — Internal Prototype Fixture Coverage Matrix v1."""

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
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    validate_public_surface,
)

COVERAGE_MATRIX = "INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_V1.md"
FIXTURE_TAXONOMY = "INTERNAL_PROTOTYPE_FIXTURE_TAXONOMY_V1.md"
GAP_ANALYSIS = "INTERNAL_PROTOTYPE_COVERAGE_GAP_ANALYSIS_V1.md"
ADMISSION_CRITERIA = "INTERNAL_PROTOTYPE_FUTURE_FIXTURE_ADMISSION_CRITERIA.md"
COVERAGE_JSON = "data/internal-prototype-fixture-coverage-matrix-v1.json"
COVERAGE_SCHEMA = "data/internal-prototype-fixture-coverage-matrix-v1.schema.json"
AUDIT = "SPRINT_75_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_V1.md"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
COVERAGE_FILES = [
    PROTOTYPE_DIR / "fixture_coverage_analyzer.py",
    PROTOTYPE_DIR / "fixture_coverage_harness.py",
]

FORBIDDEN_NETWORK = ["requests", "urllib.request", "httpx", "aiohttp", "socket"]
FORBIDDEN_INPUT = ["input(", "argparse", "click", "typer"]
FORBIDDEN_FRAMEWORKS = ["flask", "fastapi", "django", "streamlit", "gradio", "dash", "notebook"]
FORBIDDEN_REPORTING = ["reportlab", "csv.writer", "openpyxl", "xlsxwriter", "pdf", "export"]
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
REQUIRED_POSTURE_STATES = ["Supported", "Qualified", "Limited", "Not Assessable", "Out of Scope"]
REQUIRED_EDGE_MARKERS = [
    "attribution boundary",
    "provenance gap",
    "context collapse",
    "claim drift",
    "limitation-not-falsehood",
]
REQUIRED_VOCABULARY = ["Covered", "Partially Covered", "Gap", "Not Applicable", "Future Candidate"]
REQUIRED_FORBIDDEN_CLASSES = [
    "real-person accusation",
    "current event",
    "political claim",
    "legal dispute",
    "medical claim",
    "financial advice",
    "company fraud accusation",
    "private screenshot",
    "uploaded user file",
    "celebrity claim",
    "live URL",
    "external fact-check target",
    "copyrighted article reproduction",
]
SOURCE_LOCS = [
    COVERAGE_MATRIX,
    FIXTURE_TAXONOMY,
    GAP_ANALYSIS,
    ADMISSION_CRITERIA,
    COVERAGE_JSON,
    COVERAGE_SCHEMA,
    "internal/prototypes/controlled-engine-v0/fixture_coverage_analyzer.py",
    "internal/prototypes/controlled-engine-v0/fixture_coverage_harness.py",
    AUDIT,
    "validators/validate_internal_prototype_fixture_coverage_matrix_v1.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [COVERAGE_MATRIX, FIXTURE_TAXONOMY, GAP_ANALYSIS, ADMISSION_CRITERIA, COVERAGE_JSON, COVERAGE_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in COVERAGE_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_coverage_json() -> bool:
    ok = True
    data = load_json(COVERAGE_JSON)
    _ = load_json(COVERAGE_SCHEMA)
    if data.get("coverage_matrix_id") != "internal-prototype-fixture-coverage-matrix-v1":
        error("coverage_matrix_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-093":
        error("decision_ref must be DEC-093")
        ok = False
    if data.get("sprint") != "Sprint 75":
        error("sprint must be Sprint 75")
        ok = False
    if data.get("status") != "internal_non_public_fixture_coverage_matrix":
        error("status must be internal_non_public_fixture_coverage_matrix")
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
    vocab = data.get("coverage_status_vocabulary", [])
    for item in REQUIRED_VOCABULARY:
        if item not in vocab:
            error(f"coverage_status_vocabulary missing {item}")
            ok = False
    forbidden = [x.lower() for x in data.get("forbidden_fixture_classes", [])]
    for item in REQUIRED_FORBIDDEN_CLASSES:
        if item.lower() not in forbidden:
            error(f"forbidden_fixture_classes missing {item}")
            ok = False
    admission = data.get("future_fixture_admission_criteria", {})
    if not admission.get("requires_named_coverage_gap_reference"):
        error("future_fixture_admission_criteria must require named coverage gap reference")
        ok = False
    for section in [
        "current_fixture_inventory",
        "coverage_dimensions",
        "posture_state_coverage",
        "evidence_condition_dimension_coverage",
        "protocol_step_coverage",
        "standard_principle_coverage",
        "boundary_check_coverage",
        "caveat_family_coverage",
        "guardrail_rule_coverage",
        "forbidden_transformation_coverage",
        "traceability_field_coverage",
        "fixture_policy_coverage",
        "regression_vector_coverage",
        "coverage_gaps",
    ]:
        if not data.get(section):
            error(f"{section} missing")
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


def validate_coverage_code() -> bool:
    ok = True
    for path in list(PROTOTYPE_DIR.rglob("*.py")):
        if path.name in {"admissibility_regression_suite.py", "admissibility_regression_harness.py"}:
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        phrase_scan = path.name not in {"output_guardrail_checker.py", "guardrail_regression.py", "guardrail_red_team_pack.py", "output_admissibility_contract.py", "output_admissibility_harness.py"}
        for term in FORBIDDEN_NETWORK + FORBIDDEN_INPUT + FORBIDDEN_FRAMEWORKS:
            if term in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden pattern: {term}")
                ok = False
        for term in FORBIDDEN_REPORTING:
            if term in lower and "report_generation_authorized" not in lower and "public_report" not in lower:
                if path.name == "fixture_coverage_analyzer.py" and term == "export":
                    continue
                error(f"{path.relative_to(ROOT)} contains report/export behavior: {term}")
                ok = False
        for phrase in FORBIDDEN_PHRASES:
            if phrase_scan and phrase in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")
                ok = False
    return ok


def validate_harness() -> bool:
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / "fixture_coverage_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        error(f"fixture_coverage_harness failed: {proc.stderr or proc.stdout}")
        return False
    out = (proc.stdout or "").strip().lower()
    if out != "controlled internal fixture coverage validation passed":
        error("fixture_coverage_harness must print only safe controlled validation language")
        return False
    return True


def validate_fixture_postures() -> bool:
    ok = True
    fixtures = load_json("internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json").get(
        "fixtures", []
    )
    found_postures: set[str] = set()
    for fixture in fixtures:
        for posture in fixture.get("expected_allowed_posture_states", []):
            found_postures.add(posture)
    for posture in REQUIRED_POSTURE_STATES:
        if posture not in found_postures:
            error(f"fixtures missing posture state {posture}")
            ok = False
    edge_text = (ROOT / FIXTURE_TAXONOMY).read_text(encoding="utf-8").lower()
    for marker in REQUIRED_EDGE_MARKERS:
        if marker not in edge_text:
            error(f"edge coverage marker missing from taxonomy: {marker}")
            ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-093" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-093 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_prototype_fixture_coverage_matrix_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 75 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0077" for c in claims):
        error("CLAIM-0077 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0070" for g in gates):
        error("PUB-GATE-0070 missing")
        ok = False
    if "Sprint 75 | COMPLETE | G75 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 75 completion row")
        ok = False
    for rel in [COVERAGE_MATRIX, FIXTURE_TAXONOMY, GAP_ANALYSIS, ADMISSION_CRITERIA, AUDIT]:
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
            validate_coverage_json,
            validate_surface,
            validate_coverage_code,
            validate_harness,
            validate_fixture_postures,
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
