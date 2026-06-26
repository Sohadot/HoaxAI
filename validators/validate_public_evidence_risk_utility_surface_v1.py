#!/usr/bin/env python3
"""Validate Sprint 84 — Public Evidence-Risk Utility Surface v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    validate_public_surface,
)

SURFACE = "PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_V1.md"
AUDIT_DOC = "PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_AUDIT_V1.md"
SURFACE_JSON = "data/public-evidence-risk-utility-surface-v1.json"
SURFACE_SCHEMA = "data/public-evidence-risk-utility-surface-v1.schema.json"
SPRINT_AUDIT = "SPRINT_84_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_V1.md"
INDEX = "index.html"
EXPECTED_ROUTES = 23
EXPECTED_SITEMAP = 23

UTILITY_PAGES = {
    "manual-evidence-checklist/index.html": {
        "h1": "Manual Evidence Checklist",
        "groups": [
            "Source",
            "Provenance",
            "Context",
            "Traceability",
            "Claim Drift",
            "Boundary Integrity",
            "Evidence Posture",
        ],
    },
    "evidence-posture-map/index.html": {
        "h1": "Evidence Posture Map",
        "map_steps": [
            "Source",
            "Provenance",
            "Context",
            "Traceability",
            "Claim Drift",
            "Boundary Integrity",
            "Evidence Posture",
        ],
    },
    "synthetic-examples/index.html": {
        "h1": "Synthetic Evidence-Risk Examples",
        "example_count": 5,
    },
    "evidence-risk-questions/index.html": {
        "h1": "Evidence-Risk Questions",
        "sections": [
            "Source Questions",
            "Provenance Questions",
            "Context Questions",
            "Traceability Questions",
            "Claim Drift Questions",
        ],
    },
}

UTILITY_PATHS = [
    "/manual-evidence-checklist/",
    "/evidence-posture-map/",
    "/synthetic-examples/",
    "/evidence-risk-questions/",
]

FORBIDDEN_CLAIMS = [
    "detects fake",
    "fake detector",
    "ai detector",
    "verifies truth",
    "scores authenticity",
    "confidence score",
    "upload a file",
    "submit evidence",
    "analyze your file",
    "generate report",
    "real or fake",
    "verified true",
    "verified false",
    "proven manipulated",
    "fraudulent",
    "guilty",
    "deceptive",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

SOURCE_LOCS = [
    SURFACE,
    AUDIT_DOC,
    SURFACE_JSON,
    SURFACE_SCHEMA,
    SPRINT_AUDIT,
    "validators/validate_public_evidence_risk_utility_surface_v1.py",
    "manual-evidence-checklist/index.html",
    "evidence-posture-map/index.html",
    "synthetic-examples/index.html",
    "evidence-risk-questions/index.html",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def extract_h1(html: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    return re.sub(r"<[^>]+>", " ", match.group(1)).strip() if match else ""


def line_has_unnegated_claim(line: str, claim: str) -> bool:
    lower = line.lower()
    if claim not in lower:
        return False
    pos = 0
    while True:
        idx = lower.find(claim, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 80) : idx]
        if not NEGATION_PATTERN.search(prefix + claim):
            return True
        pos = idx + len(claim)
    return False


def validate_artifacts() -> bool:
    ok = True
    for rel in [
        SURFACE,
        AUDIT_DOC,
        SURFACE_JSON,
        SURFACE_SCHEMA,
        SPRINT_AUDIT,
        "validators/validate_public_evidence_risk_utility_surface_v1.py",
    ] + list(UTILITY_PAGES):
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    return ok


def validate_surface_json() -> bool:
    ok = True
    try:
        data = load_json(SURFACE_JSON)
    except json.JSONDecodeError as exc:
        error(f"surface JSON parse error: {exc}")
        return False
    json.loads((ROOT / SURFACE_SCHEMA).read_text(encoding="utf-8"))
    if data.get("surface_id") != "public-evidence-risk-utility-surface-v1":
        error("surface_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-102":
        error("decision_ref must be DEC-102")
        ok = False
    if data.get("sprint") != "Sprint 84":
        error("sprint must be Sprint 84")
        ok = False
    if sorted(data.get("public_routes_added", [])) != sorted(UTILITY_PATHS):
        error("public_routes_added must list exactly four utility routes")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED_SITEMAP:
        error("expected_sitemap_url_count_after must be 23")
        ok = False
    for key in [
        "upload_authorized",
        "scoring_authorized",
        "verdict_authorized",
        "detector_claim_authorized",
        "public_api_authorized",
        "automated_report_authorized",
        "javascript_authorized",
    ]:
        if data.get(key) is not False:
            error(f"{key} must be false")
            ok = False
    for key in [
        "public_utility_authorized",
        "manual_reference_utility_authorized",
        "synthetic_examples_authorized",
        "visual_map_authorized",
        "checklist_authorized",
    ]:
        if data.get(key) is not True:
            error(f"{key} must be true")
            ok = False
    return ok


def validate_utility_pages() -> bool:
    ok = True
    for rel, spec in UTILITY_PAGES.items():
        content = (ROOT / rel).read_text(encoding="utf-8")
        lower = content.lower()
        if len(re.findall(r"<h1\b", content, re.I)) != 1:
            error(f"{rel}: expected exactly one H1")
            ok = False
        if extract_h1(content) != spec["h1"]:
            error(f"{rel}: H1 must be {spec['h1']!r}")
            ok = False
        if 'rel="canonical"' not in content:
            error(f"{rel}: missing canonical")
            ok = False
        if 'name="description"' not in content:
            error(f"{rel}: missing meta description")
            ok = False
        if "<form" in lower or "<input" in lower:
            error(f"{rel}: forms/inputs forbidden")
            ok = False
        if re.search(r"<script\b", content, re.I):
            error(f"{rel}: JavaScript forbidden")
            ok = False
        if 'href="/"' not in content:
            error(f"{rel}: must link to homepage")
            ok = False
        cross = sum(1 for p in UTILITY_PATHS if p in content and p.strip("/") not in rel)
        if cross < 2:
            error(f"{rel}: must link to at least two other utility pages")
            ok = False
        for claim in FORBIDDEN_CLAIMS:
            for line in content.splitlines():
                if line_has_unnegated_claim(line, claim):
                    error(f"{rel}: forbidden claim {claim!r}")
                    ok = False
                    break
        if "groups" in spec:
            for g in spec["groups"]:
                if g not in content:
                    error(f"{rel}: missing checklist group {g}")
                    ok = False
        if "map_steps" in spec:
            for step in spec["map_steps"]:
                if step not in content:
                    error(f"{rel}: missing map step {step}")
                    ok = False
        if "example_count" in spec:
            count = len(re.findall(r"<h3[^>]*>\s*Example\s+\d+", content, re.I))
            if count != spec["example_count"]:
                error(f"{rel}: expected {spec['example_count']} synthetic examples, found {count}")
                ok = False
        if "sections" in spec:
            for sec in spec["sections"]:
                if sec not in content:
                    error(f"{rel}: missing section {sec}")
                    ok = False
        if "non-verdict" not in lower and "non verdict" not in lower:
            error(f"{rel}: missing non-verdict boundary language")
            ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    if "use hoax.ai as an evidence-risk utility" not in lower:
        error("homepage missing utility section title")
        ok = False
    for path in UTILITY_PATHS:
        if path not in content:
            error(f"homepage missing link to {path}")
            ok = False
    if "<form" in lower or re.search(r"<script\b", content, re.I):
        error("homepage must not add forms or JavaScript")
        ok = False
    if "try it" in lower or "submit evidence" in lower or "analyze your" in lower:
        error("homepage contains forbidden CTA language")
        ok = False
    return ok


def validate_surface_counts() -> bool:
  ok = True
  routes = load_json("data/route-registry.json").get("routes", [])
  paths = {r.get("path") for r in routes}
  for util in UTILITY_PATHS:
    if util not in paths:
      error(f"route registry missing utility path {util}")
      ok = False
  locs = [
    e.text.strip().lower()
    for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")
    if e.text
  ]
  for util in UTILITY_PATHS:
    if f"https://hoax.ai{util}".lower() not in locs:
      error(f"sitemap missing utility URL {util}")
      ok = False
  fixtures = load_json(
    "internal/prototypes/controlled-engine-v0/fixtures/synthetic-fixtures-v0.json"
  ).get("fixtures", [])
  if len(fixtures) != 16:
    error("fixture count must remain 16")
    ok = False
  return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-102" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-102 missing")
        ok = False
    if "validate_public_evidence_risk_utility_surface_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 84 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    ):
        error("publisher status must remain blocked from publication")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0086" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0086 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0079" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0079 missing")
        ok = False
    if "Sprint 84 | COMPLETE | G84 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 84 row")
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
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")):
            error(f"python cache tracked/staged: {rel}")
            return False
    return True


def main() -> int:
    ok = all(
        fn()
        for fn in [
            validate_artifacts,
            validate_surface_json,
            validate_utility_pages,
            validate_homepage,
            validate_surface_counts,
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
