#!/usr/bin/env python3
"""Validate Sprint 70 — Internal Non-Public Engine Prototype Charter."""

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
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    validate_public_surface,
)

CHARTER = "INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER.md"
ADMISSIBILITY = "INTERNAL_PROTOTYPE_ADMISSIBILITY_MODEL.md"
FIXTURE_POLICY = "INTERNAL_PROTOTYPE_FIXTURE_POLICY.md"
CHARTER_JSON = "data/internal-non-public-engine-prototype-charter-v1.json"
CHARTER_SCHEMA = "data/internal-non-public-engine-prototype-charter-v1.schema.json"
AUDIT = "SPRINT_70_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER_AUDIT.md"

PROHIBITED_FIXTURES = [
    "real person accusation",
    "active news event",
    "political claim",
    "company fraud claim",
    "legal dispute",
    "private screenshots",
    "personal messages",
    "uploaded user files",
    "external fact-check target",
]

PROHIBITED_OUTPUTS = [
    "fake/real result",
    "truth/falsity result",
    "score",
    "confidence percentage",
    "subject guilt",
    "deception finding",
    "manipulation proof",
    "fraud accusation",
    "legal conclusion",
    "moderation action",
    "public result card",
]

DOC_REQUIRED = [
    "non-public, non-executable review architecture without producing verdicts",
    "no prototype exists",
    "Sprint 70 does not authorize a prototype",
    "no input system is created in Sprint 70",
    "Sprint 70 authorizes no execution",
    "Sprint 71 may only consider",
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
    CHARTER,
    ADMISSIBILITY,
    FIXTURE_POLICY,
    CHARTER_JSON,
    CHARTER_SCHEMA,
    AUDIT,
    "validators/validate_internal_non_public_engine_prototype_charter.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in (CHARTER, ADMISSIBILITY, FIXTURE_POLICY, CHARTER_JSON, CHARTER_SCHEMA, AUDIT):
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    if not ok:
        return False
    charter = (ROOT / CHARTER).read_text(encoding="utf-8")
    lower = charter.lower()
    for phrase in DOC_REQUIRED:
        if phrase.lower() not in lower:
            error(f"charter missing required phrase: {phrase}")
            ok = False
    for term in FORBIDDEN_TERMS:
        if term in lower:
            error(f"charter contains forbidden term: {term}")
            ok = False
    for rel in SOURCE_LOCS[:5]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in text:
                error(f"{rel} contains forbidden term: {term}")
                ok = False
    return ok


def validate_charter_json() -> bool:
    ok = True
    data = load_json(CHARTER_JSON)
    if data.get("charter_id") != "internal-non-public-engine-prototype-charter-v1":
        error("charter_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-088":
        error("decision_ref must be DEC-088")
        ok = False
    if data.get("sprint") != "Sprint 70":
        error("sprint must be Sprint 70")
        ok = False
    if data.get("status") != "internal_non_public_prototype_charter_only":
        error("status must be internal_non_public_prototype_charter_only")
        ok = False
    for flag in [
        "prototype_authorized",
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
        "public_reference_seo_authority_map_v1",
    }
    if not required_auth.issubset(authority):
        error("source_authority missing required entries")
        ok = False
    fixture = data.get("fixture_policy", {})
    prohibited_fix = fixture.get("prohibited_classes", [])
    for item in [
        "real_person_accusation",
        "active_news_event",
        "political_claim",
        "company_fraud_claim",
        "legal_dispute",
        "private_screenshots",
        "personal_messages",
        "uploaded_user_files",
        "external_fact_check_target",
    ]:
        if item not in prohibited_fix:
            error(f"fixture policy missing prohibited class: {item}")
            ok = False
    outputs = data.get("output_boundaries", {}).get("prohibited_outputs", [])
    for item in PROHIBITED_OUTPUTS:
        if item not in outputs:
            error(f"output boundary missing prohibited: {item}")
            ok = False
    gate = data.get("future_authorization_gate", {})
    if gate.get("sprint_70_authorizes_prototype") is not False:
        error("future_authorization_gate must state sprint_70_authorizes_prototype false")
        ok = False
    if gate.get("next_consideration_sprint") != "Sprint 71":
        error("future_authorization_gate must reference Sprint 71")
        ok = False
    boundaries = data.get("operational_boundaries", {})
    for key in [
        "no_prototype_implementation",
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
    if "DEC-088" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-088 missing from DECISION_LOG.md")
        ok = False
    if "validate_internal_non_public_engine_prototype_charter.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 70 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0072"
        for c in load_json("data/evidence-ledger.json").get("claims", [])
    ):
        error("CLAIM-0072 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0065" for g in gates):
        error("PUB-GATE-0065 missing")
        ok = False
    for doc, needle in [
        ("ENGINE_BOUNDARY_CHARTER.md", "DEC-088"),
        ("ENGINE_MODEL_V0.md", "Internal Non-Public Engine Prototype Charter"),
        ("OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1.md", "Internal Non-Public Engine Prototype Charter"),
    ]:
        if needle not in (ROOT / doc).read_text(encoding="utf-8"):
            error(f"{doc} must reference prototype charter")
            ok = False
    if "Sprint 70 | COMPLETE | G70 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 70 completion row")
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
            validate_charter_json,
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
