#!/usr/bin/env python3
"""Validate Sprint 74 — Internal Prototype Traceability and Interpretability Audit v1."""

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
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    validate_public_surface,
)

TRACE_MATRIX = "INTERNAL_PROTOTYPE_TRACEABILITY_MATRIX_V1.md"
INTERPRETABILITY_AUDIT = "INTERNAL_PROTOTYPE_INTERPRETABILITY_AUDIT_V1.md"
FAILURE_MODES = "INTERNAL_PROTOTYPE_TRACEABILITY_FAILURE_MODES.md"
TRACE_JSON = "data/internal-prototype-traceability-map-v1.json"
TRACE_SCHEMA = "data/internal-prototype-traceability-map-v1.schema.json"
AUDIT = "SPRINT_74_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_V1.md"

PROTOTYPE_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"
TRACEABILITY_FILES = [
    PROTOTYPE_DIR / "traceability_mapper.py",
    PROTOTYPE_DIR / "interpretability_auditor.py",
    PROTOTYPE_DIR / "traceability_harness.py",
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
REQUIRED_FIELDS = [
    "trace_id",
    "fixture_id",
    "posture_basis",
    "protocol_step_refs",
    "standard_principle_refs",
    "evidence_condition_refs",
    "boundary_check_refs",
    "caveat_trigger_refs",
    "guardrail_rule_refs",
    "forbidden_transformation_refs",
    "no_verdict_confirmation",
    "no_score_confirmation",
    "no_subject_accusation_confirmation",
    "non_public_confirmation",
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
    TRACE_MATRIX,
    INTERPRETABILITY_AUDIT,
    FAILURE_MODES,
    TRACE_JSON,
    TRACE_SCHEMA,
    "internal/prototypes/controlled-engine-v0/traceability_mapper.py",
    "internal/prototypes/controlled-engine-v0/interpretability_auditor.py",
    "internal/prototypes/controlled-engine-v0/traceability_harness.py",
    AUDIT,
    "validators/validate_internal_prototype_traceability_interpretability_audit_v1.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in [TRACE_MATRIX, INTERPRETABILITY_AUDIT, FAILURE_MODES, TRACE_JSON, TRACE_SCHEMA, AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    for path in TRACEABILITY_FILES:
        if not path.is_file():
            error(f"missing {path.relative_to(ROOT)}")
            ok = False
    return ok


def validate_trace_json() -> bool:
    ok = True
    data = load_json(TRACE_JSON)
    _ = load_json(TRACE_SCHEMA)
    if data.get("traceability_map_id") != "internal-prototype-traceability-map-v1":
        error("traceability_map_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-092":
        error("decision_ref must be DEC-092")
        ok = False
    if data.get("sprint") != "Sprint 74":
        error("sprint must be Sprint 74")
        ok = False
    if data.get("status") != "internal_non_public_traceability_map":
        error("status must be internal_non_public_traceability_map")
        ok = False
    for key in [
        "public_route_authorized",
        "public_explanation_authorized",
        "report_generation_authorized",
        "output_generator_authorized",
        "scoring_authorized",
        "api_authorized",
        "javascript_authorized",
    ]:
        if data.get(key) is not False:
            error(f"{key} must be false")
            ok = False
    if not data.get("traceability_chain"):
        error("traceability_chain missing")
        ok = False
    if not data.get("fixture_to_protocol_map"):
        error("fixture_to_protocol_map missing")
        ok = False
    if not data.get("protocol_to_standard_map"):
        error("protocol_to_standard_map missing")
        ok = False
    if not data.get("boundary_to_caveat_map"):
        error("boundary_to_caveat_map missing")
        ok = False
    if not data.get("guardrail_to_forbidden_transformation_map"):
        error("guardrail_to_forbidden_transformation_map missing")
        ok = False
    required = set(REQUIRED_FIELDS)
    actual = set(data.get("required_internal_explanation_fields", []))
    if not required.issubset(actual):
        error("required_internal_explanation_fields incomplete")
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


def validate_traceability_code() -> bool:
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
            if term in lower and "report_generation_authorized" not in lower:
                error(f"{path.relative_to(ROOT)} contains report/export behavior: {term}")
                ok = False
        for phrase in FORBIDDEN_PHRASES:
            if phrase_scan and phrase in lower:
                error(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")
                ok = False
    return ok


def validate_harness() -> bool:
    proc = subprocess.run(
        [sys.executable, str(PROTOTYPE_DIR / "traceability_harness.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        error(f"traceability_harness failed: {proc.stderr or proc.stdout}")
        return False
    out = (proc.stdout or "").strip().lower()
    if out != "controlled internal traceability validation passed":
        error("traceability_harness must print only safe controlled validation language")
        return False
    return True


def validate_governance() -> bool:
    ok = True
    if "DEC-092" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-092 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_prototype_traceability_interpretability_audit_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 74 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    claims = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0076" for c in claims):
        error("CLAIM-0076 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0069" for g in gates):
        error("PUB-GATE-0069 missing")
        ok = False
    if "Sprint 74 | COMPLETE | G74 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 74 completion row")
        ok = False
    for rel in [TRACE_MATRIX, INTERPRETABILITY_AUDIT, FAILURE_MODES, AUDIT]:
        lower = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in lower:
                error(f"{rel} contains forbidden term: {term}")
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
            validate_trace_json,
            validate_surface,
            validate_traceability_code,
            validate_harness,
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
