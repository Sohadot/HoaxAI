#!/usr/bin/env python3
"""Validate Sprint 68 — Evidence Posture Engine Model v0."""

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
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
    validate_public_surface,
)

MODEL_DOC = "ENGINE_MODEL_V0.md"
MODEL_JSON = "data/evidence-posture-engine-model-v0.json"
MODEL_SCHEMA = "data/evidence-posture-engine-model-v0.schema.json"
AUDIT = "SPRINT_68_EVIDENCE_POSTURE_ENGINE_MODEL_V0_AUDIT.md"

PROTOCOL_STEPS = [f"EP-P{i:02d}" for i in range(1, 18)]
STANDARD_PRINCIPLES = [f"EPS-{i:03d}" for i in range(1, 15)]
POSTURE_STATES = ["Supported", "Qualified", "Limited", "Not Assessable", "Out of Scope"]

REQUIRED_BOUNDARY_CHECKS = [
    "attribution_boundary_no_subject_transfer_check",
    "output_boundary_no_forbidden_language_check",
]

REQUIRED_PROHIBITED = [
    "fake/real verdict",
    "truth/falsity verdict",
    "subject guilt",
    "deception intent",
    "manipulation proof",
    "fraud accusation",
    "responsibility assignment",
    "legal conclusion",
    "moderation action",
    "numeric score",
    "confidence percentage",
    "upload classification result",
]

FORBIDDEN_PERMITTED = ["verdict", "score", "classification result", "accusation"]

DOC_REQUIRED = [
    "maps evidence conditions, protocol steps, posture states, boundary checks, and permitted output language without executing review",
    "no public engine",
    "No input form, upload workflow, API endpoint, or user-facing submission process is created",
    "No numeric score. No percentage. No fake/real label.",
    "no verdict system",
]

FORBIDDEN_TERMS = [
    "rick",
    "linkedin",
    "cloudflare",
    "domain owner",
    "buyer conversation",
    "marketing notes",
    "timezone notes",
    "outreach history",
    "negotiation context",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    MODEL_DOC,
    MODEL_JSON,
    MODEL_SCHEMA,
    AUDIT,
    "validators/validate_evidence_posture_engine_model_v0.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in (MODEL_DOC, MODEL_JSON, MODEL_SCHEMA, AUDIT):
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    if not ok:
        return False
    doc = (ROOT / MODEL_DOC).read_text(encoding="utf-8")
    lower = doc.lower()
    for phrase in DOC_REQUIRED:
        if phrase.lower() not in lower:
            error(f"ENGINE_MODEL_V0.md missing required phrase: {phrase}")
            ok = False
    for term in FORBIDDEN_TERMS:
        if term in lower:
            error(f"model doc contains forbidden term: {term}")
            ok = False
    for rel in (MODEL_DOC, MODEL_JSON, MODEL_SCHEMA):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in text:
                error(f"{rel} contains forbidden term: {term}")
                ok = False
    return ok


def validate_model_json() -> bool:
    ok = True
    data = load_json(MODEL_JSON)
    schema = load_json(MODEL_SCHEMA)
    if schema.get("title") != "Evidence Posture Engine Model v0":
        error("schema title mismatch")
        ok = False
    if data.get("model_id") != "evidence-posture-engine-model-v0":
        error("model_id must be evidence-posture-engine-model-v0")
        ok = False
    if data.get("decision_ref") != "DEC-086":
        error("decision_ref must be DEC-086")
        ok = False
    if data.get("sprint") != "Sprint 68":
        error("sprint must be Sprint 68")
        ok = False
    if data.get("status") != "internal_non_operational_model":
        error("status must be internal_non_operational_model")
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
    step_ids = [s.get("step_id") for s in data.get("protocol_steps", [])]
    if step_ids != PROTOCOL_STEPS:
        error("protocol_steps must include EP-P01 through EP-P17 in order")
        ok = False
    principle_ids = [p.get("principle_id") for p in data.get("standard_principles", [])]
    if principle_ids != STANDARD_PRINCIPLES:
        error("standard_principles must include EPS-001 through EPS-014 in order")
        ok = False
    if data.get("posture_states") != POSTURE_STATES:
        error("posture_states mismatch")
        ok = False
    checks = data.get("boundary_checks", [])
    for check in REQUIRED_BOUNDARY_CHECKS:
        if check not in checks:
            error(f"missing boundary check: {check}")
            ok = False
    prohibited = data.get("prohibited_output_types", [])
    for item in REQUIRED_PROHIBITED:
        if item not in prohibited:
            error(f"missing prohibited output type: {item}")
            ok = False
    permitted = " ".join(data.get("permitted_output_types", [])).lower()
    for bad in FORBIDDEN_PERMITTED:
        if bad in permitted:
            error(f"permitted_output_types must not include: {bad}")
            ok = False
    boundaries = data.get("operational_boundaries", {})
    for key in ["no_public_engine", "no_upload", "no_scoring", "no_api", "no_javascript", "no_public_tool_behavior"]:
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
    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_PUBLIC_HTML and rel != "_internal_prototypes/evidence-posture-workbench/index.html":
            error(f"unexpected HTML file: {rel}")
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
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-086" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-086 missing from DECISION_LOG.md")
        ok = False
    if "validate_evidence_posture_engine_model_v0.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 68 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") != PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0:
        error("publisher status must be blocked_until_evidence_posture_engine_model_v0_validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0070" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0070 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0063" for g in gates):
        error("PUB-GATE-0063 missing")
        ok = False
    charter = (ROOT / "ENGINE_BOUNDARY_CHARTER.md").read_text(encoding="utf-8")
    if "DEC-086" not in charter or "Engine Model v0" not in charter:
        error("ENGINE_BOUNDARY_CHARTER.md must reference Engine Model v0 and DEC-086")
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
            validate_model_json,
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
