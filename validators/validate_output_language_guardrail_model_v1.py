#!/usr/bin/env python3
"""Validate Sprint 69 — Output Language Guardrail Model v1."""

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
    PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    validate_public_surface,
)

GUARDRAIL_DOC = "OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1.md"
GUARDRAIL_JSON = "data/output-language-guardrail-model-v1.json"
GUARDRAIL_SCHEMA = "data/output-language-guardrail-model-v1.schema.json"
AUDIT = "SPRINT_69_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1_AUDIT.md"

POSTURE_STATES = ["Supported", "Qualified", "Limited", "Not Assessable", "Out of Scope"]

REQUIRED_ALLOWED = [
    "evidence posture statement",
    "support condition statement",
    "qualification statement",
    "source caveat",
    "provenance caveat",
    "context caveat",
    "traceability caveat",
    "evidence limitation caveat",
    "interpretation risk caveat",
    "attribution boundary caveat",
    "output boundary caveat",
    "not assessable statement",
    "out of scope statement",
]

REQUIRED_PROHIBITED = [
    "fake/real verdict",
    "truth/falsity verdict",
    "deception finding",
    "manipulation proof",
    "fraud accusation",
    "subject guilt",
    "responsibility assignment",
    "legal conclusion",
    "numeric score",
    "confidence percentage",
    "upload classification result",
    "automated result card",
]

REQUIRED_CAVEAT_TRIGGERS = [
    "source_confidence_low",
    "provenance_gap",
    "context_collapse",
    "weak_traceability",
    "claim_drift",
    "evidence_limitation",
    "high_interpretation_risk",
    "attribution_boundary_risk",
    "output_boundary_risk",
]

REQUIRED_TRANSFORMATIONS = [
    "limitation_to_falsehood",
    "drift_to_deception",
    "gap_to_manipulation",
    "risk_to_verdict",
    "artifact_to_subject_guilt",
    "synthetic_to_fake",
]

DOC_DEPTH_PHRASES = [
    "linguistic primitives",
    "boundary transformation",
    "posture-state linguistic grammar",
    "output certainty without scoring",
    "no output generator exists",
    "no public engine exists",
    "no score, no fake/real label, and no verdict system",
    "future engine dependency",
    "future prototype gate",
    "evidence posture language",
    "bounded output language",
    "artifact-subject separation",
    "posture without verdict",
]

FORBIDDEN_TERMS = [
    "rick",
    "linkedin",
    "cloudflare",
    "domain owner",
    "buyer outreach",
    "marketing conversations",
    "timezone notes",
    "outreach history",
    "negotiation context",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    GUARDRAIL_DOC,
    GUARDRAIL_JSON,
    GUARDRAIL_SCHEMA,
    AUDIT,
    "validators/validate_output_language_guardrail_model_v1.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_artifacts() -> bool:
    ok = True
    for rel in (GUARDRAIL_DOC, GUARDRAIL_JSON, GUARDRAIL_SCHEMA, AUDIT):
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    if not ok:
        return False
    doc = (ROOT / GUARDRAIL_DOC).read_text(encoding="utf-8")
    lower = doc.lower()
    for phrase in DOC_DEPTH_PHRASES:
        if phrase.lower() not in lower:
            error(f"guardrail doc missing required depth phrase: {phrase}")
            ok = False
    for term in FORBIDDEN_TERMS:
        if term in lower:
            error(f"guardrail doc contains forbidden term: {term}")
            ok = False
    for rel in (GUARDRAIL_DOC, GUARDRAIL_JSON, GUARDRAIL_SCHEMA):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in text:
                error(f"{rel} contains forbidden term: {term}")
                ok = False
    return ok


def validate_guardrail_json() -> bool:
    ok = True
    data = load_json(GUARDRAIL_JSON)
    schema = load_json(GUARDRAIL_SCHEMA)
    if schema.get("title") != "Output Language Guardrail Model v1":
        error("schema title mismatch")
        ok = False
    if data.get("guardrail_id") != "output-language-guardrail-model-v1":
        error("guardrail_id must be output-language-guardrail-model-v1")
        ok = False
    if data.get("decision_ref") != "DEC-087":
        error("decision_ref must be DEC-087")
        ok = False
    if data.get("sprint") != "Sprint 69":
        error("sprint must be Sprint 69")
        ok = False
    if data.get("status") != "internal_non_operational_guardrail_model":
        error("status must be internal_non_operational_guardrail_model")
        ok = False
    for flag in [
        "public_route_authorized",
        "public_output_generator_authorized",
        "public_engine_authorized",
        "classifier_authorized",
        "scoring_authorized",
        "api_authorized",
        "javascript_authorized",
    ]:
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    primitives = data.get("linguistic_primitives", [])
    if len(primitives) < 12:
        error("linguistic_primitives must include at least 12 entries")
        ok = False
    for p in primitives:
        for field in [
            "definition",
            "function",
            "allowed_use",
            "forbidden_misuse",
            "standard_relation",
            "protocol_relation",
            "engine_model_relation",
        ]:
            if not p.get(field):
                error(f"primitive {p.get('primitive_id')} missing {field}")
                ok = False
    allowed = data.get("allowed_output_families", [])
    for item in REQUIRED_ALLOWED:
        if item not in allowed:
            error(f"missing allowed output family: {item}")
            ok = False
    prohibited = data.get("prohibited_output_families", [])
    for item in REQUIRED_PROHIBITED:
        if item not in prohibited:
            error(f"missing prohibited output family: {item}")
            ok = False
    posture_rules = data.get("posture_state_language_rules", [])
    states = {r.get("posture_state") for r in posture_rules}
    if states != set(POSTURE_STATES):
        error("posture_state_language_rules must include all five posture states")
        ok = False
    triggers = {r.get("trigger") for r in data.get("required_caveat_rules", [])}
    for t in REQUIRED_CAVEAT_TRIGGERS:
        if t not in triggers:
            error(f"missing required caveat trigger: {t}")
            ok = False
    transform_ids = {r.get("rule_id") for r in data.get("boundary_transformation_rules", [])}
    for tid in REQUIRED_TRANSFORMATIONS:
        if tid not in transform_ids:
            error(f"missing boundary transformation rule: {tid}")
            ok = False
    ftc = data.get("forbidden_term_controls", {})
    if not ftc.get("forbidden_as_output_conclusions") or not ftc.get("allowed_only_as_prohibited_examples"):
        error("forbidden_term_controls incomplete")
        ok = False
    boundaries = data.get("operational_boundaries", {})
    for key in [
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
    if len(data.get("failure_modes", [])) < 8:
        error("failure_modes insufficient")
        ok = False
    if len(data.get("canonical_language_assets", [])) < 10:
        error("canonical_language_assets insufficient for category depth")
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
    if "DEC-087" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-087 missing from DECISION_LOG.md")
        ok = False
    if "validate_output_language_guardrail_model_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 69 validator")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(
        c.get("claim_id") == "CLAIM-0071"
        for c in load_json("data/evidence-ledger.json").get("claims", [])
    ):
        error("CLAIM-0071 missing")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    if not any(g.get("gate_id") == "PUB-GATE-0064" for g in gates):
        error("PUB-GATE-0064 missing")
        ok = False
    engine_model = (ROOT / "ENGINE_MODEL_V0.md").read_text(encoding="utf-8")
    if "DEC-087" not in engine_model or "Output Language Guardrail" not in engine_model:
        error("ENGINE_MODEL_V0.md must reference Output Language Guardrail and DEC-087")
        ok = False
    charter = (ROOT / "ENGINE_BOUNDARY_CHARTER.md").read_text(encoding="utf-8")
    if "DEC-087" not in charter or "Output Language Guardrail" not in charter:
        error("ENGINE_BOUNDARY_CHARTER.md must reference Output Language Guardrail and DEC-087")
        ok = False
    if "Sprint 69 | COMPLETE | G69 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 69 completion row")
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
            validate_guardrail_json,
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
