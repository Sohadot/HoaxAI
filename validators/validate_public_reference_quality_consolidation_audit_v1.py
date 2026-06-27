#!/usr/bin/env python3
"""Validate Sprint 91 — Public Reference Quality Consolidation Audit v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    validate_public_surface,

    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_GROUP_DEEPENING_VALIDATION,)

AUDIT_DOC = "PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_AUDIT_V1.md"
REPAIR_LOG = "PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_REPAIR_LOG_V1.md"
STANDARD_DOC = "PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_STANDARD_V1.md"
AUDIT_JSON = "data/public-reference-quality-consolidation-audit-v1.json"
AUDIT_SCHEMA = "data/public-reference-quality-consolidation-audit-v1.schema.json"
SPRINT_DOC = "SPRINT_91_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_AUDIT_V1.md"
INDEX = "index.html"
EXPECTED = 29

CORE_UTILITY_REFERENCE = {
    "manual-evidence-checklist/index.html",
    "evidence-posture-map/index.html",
    "synthetic-examples/index.html",
    "evidence-risk-questions/index.html",
    "evidence-risk/index.html",
    "provenance-risk/index.html",
    "context-collapse/index.html",
    "claim-drift/index.html",
    "traceability-gap/index.html",
    "why-hoax-ai-is-not-a-detector/index.html",
}

FORBIDDEN_CLAIMS = [
    "real or fake",
    "fake detector",
    "ai detector",
    "detects fake",
    "verifies truth",
    "scores authenticity",
    "confidence score",
    "upload a file",
    "submit evidence",
    "analyze your file",
    "generate report",
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
    AUDIT_DOC,
    REPAIR_LOG,
    STANDARD_DOC,
    AUDIT_JSON,
    AUDIT_SCHEMA,
    SPRINT_DOC,
    "validators/validate_public_reference_quality_consolidation_audit_v1.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def html_to_path(rel: str) -> str:
    if rel == "index.html":
        return "/"
    base = rel.removesuffix("index.html")
    return "/" + base if base.endswith("/") else "/" + base + "/"


CORE_AND_HOME = {"index.html"} | CORE_UTILITY_REFERENCE


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
    for rel in [AUDIT_DOC, REPAIR_LOG, STANDARD_DOC, AUDIT_JSON, AUDIT_SCHEMA, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(AUDIT_JSON)
    if data.get("decision_ref") != "DEC-109":
        error("decision_ref must be DEC-109")
        ok = False
    if data.get("total_repairs_made", 0) <= 0:
        error("total_repairs_made must be greater than 0")
        ok = False
    if data.get("public_routes_inspected") != 29:
        error("public_routes_inspected must be 29")
        ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    if (ROOT / "sitemap.xml").read_text(encoding="utf-8").count("<loc>") != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have exactly {PUBLIC_SITEMAP_URL_COUNT} entries")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    registry_paths = {r.get("path") for r in routes}
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        path = html_to_path(rel)
        if path not in registry_paths:
            error(f"registry missing path for {rel}")
            ok = False
        if not (ROOT / rel).is_file():
            error(f"missing html file {rel}")
            ok = False
    return ok


def validate_html(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    h1s = len(re.findall(r"<h1\b", content, re.I))
    if h1s != 1:
        error(f"{rel}: expected exactly one H1, found {h1s}")
        ok = False
    if 'rel="canonical"' not in lower:
        error(f"{rel}: missing canonical URL")
        ok = False
    if 'name="description"' not in lower:
        error(f"{rel}: missing meta description")
        ok = False
    if 'property="og:title"' not in lower or 'property="og:description"' not in lower:
        error(f"{rel}: missing Open Graph title/description")
        ok = False
    if "<form" in lower or "<input" in lower:
        error(f"{rel}: forms/inputs forbidden")
        ok = False
    if re.search(r'<script\b(?![^>]*type=["\']application/ld\+json["\'])', content, re.I):
        error(f"{rel}: JavaScript forbidden")
        ok = False
    scan_lines = content.splitlines()
    if rel not in CORE_AND_HOME:
        scan_lines = [
            line
            for line in scan_lines
            if any(
                token in line.lower()
                for token in (
                    'name="description"',
                    'property="og:title"',
                    'property="og:description"',
                    "<title>",
                )
            )
        ]
    for claim in FORBIDDEN_CLAIMS:
        for line in scan_lines:
            if line_has_unnegated_claim(line, claim):
                error(f"{rel}: forbidden claim {claim!r}")
                ok = False
                break
    return ok


def validate_core(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    for label in (
        "reference answer",
        "source confidence",
        "cite this reference",
        "retrieval capsule",
    ):
        if label not in lower:
            error(f"{rel}: missing {label!r}")
            ok = False
    if "page-end-reference-nav" not in lower:
        error(f"{rel}: missing page-end reference navigation")
        ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    for label in (
        "public utilities",
        "reference layer",
        "reference graph",
        "source confidence",
        "reference answer",
        "cite this reference",
        "retrieval capsule",
    ):
        if label not in lower:
            error(f"homepage: missing {label!r}")
            ok = False
    for anchor in (
        'id="hero"',
        'id="public-utilities"',
        'id="reference-layer"',
        'id="reference-graph"',
        'id="source-confidence"',
        'id="reference-answer"',
        'id="cite-this-reference"',
        'id="retrieval-capsule"',
        'id="boundary"',
    ):
        if anchor not in content:
            error(f"homepage: missing anchor {anchor}")
            ok = False
    if "#reference-answer" not in content:
        error("homepage: missing deep links to #reference-answer")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-109" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-109 missing")
        ok = False
    if "validate_public_reference_quality_consolidation_audit_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 91 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_GROUP_DEEPENING_VALIDATION,
    ):
        error("publisher status must reflect Sprint 91 quality consolidation validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0092" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0092 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0085" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0085 missing")
        ok = False
    if "Sprint 91 | COMPLETE | G91 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 91 row")
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
        r = rel.replace("\\", "/").lower()
        if "__pycache__/" in r or r.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in r:
            error(f"Python cache file tracked or staged: {rel}")
            return False
    return True


def main() -> int:
    ok = True
    if not validate_artifacts():
        ok = False
    if not validate_counts():
        ok = False
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        if not validate_html(rel):
            ok = False
    if not validate_homepage():
        ok = False
    for rel in sorted(CORE_UTILITY_REFERENCE):
        if not validate_core(rel):
            ok = False
    if not validate_governance():
        ok = False
    if not validate_cache():
        ok = False
    if not ok:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
