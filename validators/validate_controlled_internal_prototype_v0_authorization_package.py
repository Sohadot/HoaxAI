#!/usr/bin/env python3
"""Validate Sprint 71 — Controlled Internal Prototype v0 Authorization Package."""

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
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    validate_public_surface,
)

AUTH_PACKAGE = "CONTROLLED_INTERNAL_PROTOTYPE_V0_AUTHORIZATION_PACKAGE.md"
CONTRACT = "CONTROLLED_PROTOTYPE_V0_IMPLEMENTATION_CONTRACT.md"
VALIDATION_PLAN = "CONTROLLED_PROTOTYPE_V0_VALIDATION_PLAN.md"
DISQUALIFICATION = "CONTROLLED_PROTOTYPE_V0_DISQUALIFICATION_MATRIX.md"
AUTH_JSON = "data/controlled-internal-prototype-v0-authorization-package.json"
AUTH_SCHEMA = "data/controlled-internal-prototype-v0-authorization-package.schema.json"
AUDIT = "SPRINT_71_CONTROLLED_INTERNAL_PROTOTYPE_V0_AUTHORIZATION_PACKAGE_AUDIT.md"

FUTURE_IMPL_DIR = ROOT / "internal" / "prototypes" / "controlled-engine-v0"

DISQUALIFICATION_CONDITIONS = [
    "public route leakage",
    "sitemap leakage",
    "upload implication",
    "user-input implication",
    "fake/real leakage",
    "score leakage",
    "subject accusation leakage",
    "real-person fixture",
    "current-event fixture",
    "external API call",
    "live web lookup",
    "output generator drift",
    "public demo drift",
    "report-export drift",
    "API endpoint drift",
]

VALIDATION_PLAN_CHECKS = [
    "fixture checks",
    "output checks",
    "guardrail checks",
    "prohibited-language checks",
    "public exposure checks",
    "route/sitemap checks",
    "external data checks",
    "rollback checks",
]

DOC_REQUIRED = [
    "Sprint 71 authorizes only the controlled scope for a future internal prototype implementation sprint",
    "no prototype is implemented in Sprint 71",
    "Sprint 71 does not authorize implementation",
    "Sprint 72 must be separately prompted, separately validated, and separately committed",
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

FORBIDDEN_IMPL_PATTERNS = [
    "prototype_runner.py",
    "engine_executor.py",
    "output_generator.py",
    "classifier_engine.py",
    "upload_handler.py",
]

SOURCE_LOCS = [
    AUTH_PACKAGE,
    CONTRACT,
    VALIDATION_PLAN,
    DISQUALIFICATION,
    AUTH_JSON,
    AUTH_SCHEMA,
    AUDIT,
    "validators/validate_controlled_internal_prototype_v0_authorization_package.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in (AUTH_PACKAGE, CONTRACT, VALIDATION_PLAN, DISQUALIFICATION, AUTH_JSON, AUTH_SCHEMA, AUDIT):
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    if not ok:
        return False
    auth = (ROOT / AUTH_PACKAGE).read_text(encoding="utf-8")
    lower = auth.lower()
    for phrase in DOC_REQUIRED:
        if phrase.lower() not in lower:
            error(f"authorization package missing required phrase: {phrase}")
            ok = False
    for term in FORBIDDEN_TERMS:
        if term in lower:
            error(f"authorization package contains forbidden term: {term}")
            ok = False
    contract = (ROOT / CONTRACT).read_text(encoding="utf-8").lower()
    if "anything not explicitly allowed remains prohibited" not in contract:
        error("implementation contract must state anything not explicitly allowed remains prohibited")
        ok = False
    plan = (ROOT / VALIDATION_PLAN).read_text(encoding="utf-8").lower()
    for check in VALIDATION_PLAN_CHECKS:
        if check not in plan:
            error(f"validation plan missing: {check}")
            ok = False
    matrix = (ROOT / DISQUALIFICATION).read_text(encoding="utf-8").lower()
    for item in DISQUALIFICATION_CONDITIONS:
        if item.lower() not in matrix:
            error(f"disqualification matrix missing: {item}")
            ok = False
    for rel in SOURCE_LOCS[:7]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in text:
                error(f"{rel} contains forbidden term: {term}")
                ok = False
    return ok


def validate_auth_json() -> bool:
    ok = True
    data = load_json(AUTH_JSON)
    if data.get("authorization_id") != "controlled-internal-prototype-v0-authorization-package":
        error("authorization_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-089":
        error("decision_ref must be DEC-089")
        ok = False
    if data.get("sprint") != "Sprint 71":
        error("sprint must be Sprint 71")
        ok = False
    if data.get("status") != "authorization_package_only":
        error("status must be authorization_package_only")
        ok = False
    if data.get("prototype_implemented") is not False:
        error("prototype_implemented must be false")
        ok = False
    if data.get("prototype_authorized_in_this_sprint") is not False:
        error("prototype_authorized_in_this_sprint must be false")
        ok = False
    if data.get("future_sprint_72_may_consider_implementation") is not True:
        error("future_sprint_72_may_consider_implementation must be true")
        ok = False
    for flag in [
        "public_route_authorized",
        "public_engine_authorized",
        "input_system_authorized",
        "output_generator_authorized",
        "scoring_authorized",
        "api_authorized",
        "javascript_authorized",
    ]:
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    authority = set(data.get("source_authority", []))
    required_auth = {
        "evidence_posture_standard_v1",
        "evidence_posture_protocol_v1_draft",
        "engine_boundary_charter",
        "evidence_posture_engine_model_v0",
        "output_language_guardrail_model_v1",
        "internal_non_public_engine_prototype_charter",
        "internal_prototype_admissibility_model",
        "internal_prototype_fixture_policy",
        "public_reference_seo_authority_map_v1",
    }
    if not required_auth.issubset(authority):
        error("source_authority missing required entries")
        ok = False
    paths = data.get("file_path_boundaries", {})
    if paths.get("sprint_71_creates_directory") is not False:
        error("file_path_boundaries must state sprint_71_creates_directory false")
        ok = False
    gate = data.get("future_sprint_gate", {})
    if gate.get("sprint_71_authorizes_implementation") is not False:
        error("future_sprint_gate must state sprint_71_authorizes_implementation false")
        ok = False
    if gate.get("next_implementation_sprint") != "Sprint 72":
        error("future_sprint_gate must reference Sprint 72")
        ok = False
    boundaries = data.get("operational_boundaries", {})
    for key in [
        "no_prototype_implementation_in_sprint_71",
        "no_public_engine",
        "no_output_generator",
        "no_upload",
        "no_scoring",
        "no_api",
        "no_javascript",
        "no_public_tool_behavior",
    ]:
        if boundaries.get(key) is not True:
            error(f"operational_boundaries.{key} must be true")
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
    forbidden_paths = ["/engine/", "/tool/", "/scanner/", "/api/", "/dashboard/", "/upload/", "/score/"]
    registered = {r.get("path") for r in routes}
    for path in forbidden_paths:
        if path in registered:
            error(f"forbidden route registered: {path}")
            ok = False
    if FUTURE_IMPL_DIR.is_dir():
        pass  # historical Sprint 71 artifact; implementation directory allowed after Sprint 72
    for pattern in FORBIDDEN_IMPL_PATTERNS:
        if list(ROOT.rglob(pattern)):
            error(f"prototype implementation file must not exist: {pattern}")
            ok = False
    proto_pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for rel in ALLOWED_PUBLIC_HTML:
        if proto_pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"prototype leak on public page: {rel}")
            ok = False
    if not all((ROOT / x).is_file() for x in LOCKED_FILES):
        error("prototype files missing")
        ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files modified")
        ok = False
    if subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files staged")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-089" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-089 missing from DECISION_LOG.md")
        ok = False
    if "validate_controlled_internal_prototype_v0_authorization_package.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 71 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0073"
        for c in load_json("data/evidence-ledger.json").get("claims", [])
    ):
        error("CLAIM-0073 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0066" for g in gates):
        error("PUB-GATE-0066 missing")
        ok = False
    for doc, needle in [
        ("INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER.md", "DEC-089"),
        ("INTERNAL_PROTOTYPE_ADMISSIBILITY_MODEL.md", "Authorization Package"),
        ("INTERNAL_PROTOTYPE_FIXTURE_POLICY.md", "Authorization Package"),
        ("ENGINE_MODEL_V0.md", "Authorization Package"),
        ("OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1.md", "Authorization Package"),
    ]:
        if needle not in (ROOT / doc).read_text(encoding="utf-8"):
            error(f"{doc} must reference authorization package")
            ok = False
    if "Sprint 71 | COMPLETE | G71 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 71 completion row")
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
            validate_auth_json,
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
