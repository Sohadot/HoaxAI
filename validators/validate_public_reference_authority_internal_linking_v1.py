#!/usr/bin/env python3
"""Validate Sprint 87 — Public Reference Authority Internal Linking v1."""

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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    validate_public_surface,
)

LINKING_DOC = "PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_V1.md"
STANDARD_DOC = "HUMAN_AI_INTERNAL_LINKING_STANDARD_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_LINK_GRAPH_AUDIT_V1.md"
LINKING_JSON = "data/public-reference-authority-internal-linking-v1.json"
LINKING_SCHEMA = "data/public-reference-authority-internal-linking-v1.schema.json"
SPRINT_AUDIT = "SPRINT_87_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_V1.md"
INDEX = "index.html"
EXPECTED_ROUTES = PUBLIC_SITEMAP_URL_COUNT
EXPECTED_SITEMAP = PUBLIC_SITEMAP_URL_COUNT

UTILITY_PAGES = {
    "manual-evidence-checklist/index.html": "/manual-evidence-checklist/",
    "evidence-posture-map/index.html": "/evidence-posture-map/",
    "synthetic-examples/index.html": "/synthetic-examples/",
    "evidence-risk-questions/index.html": "/evidence-risk-questions/",
}

REFERENCE_PAGES = {
    "evidence-risk/index.html": "/evidence-risk/",
    "provenance-risk/index.html": "/provenance-risk/",
    "context-collapse/index.html": "/context-collapse/",
    "claim-drift/index.html": "/claim-drift/",
    "traceability-gap/index.html": "/traceability-gap/",
    "why-hoax-ai-is-not-a-detector/index.html": "/why-hoax-ai-is-not-a-detector/",
}

UTILITY_PATHS = list(UTILITY_PAGES.values())
REFERENCE_PATHS = list(REFERENCE_PAGES.values())

ROUTE_REQUIRED_LINKS: dict[str, list[str]] = {
    "evidence-risk/index.html": [
        "/provenance-risk/",
        "/context-collapse/",
        "/claim-drift/",
        "/traceability-gap/",
        "/manual-evidence-checklist/",
        "/evidence-posture-map/",
    ],
    "provenance-risk/index.html": [
        "/evidence-risk/",
        "/traceability-gap/",
        "/claim-drift/",
        "/manual-evidence-checklist/",
        "/evidence-posture-map/",
    ],
    "context-collapse/index.html": [
        "/evidence-risk/",
        "/claim-drift/",
        "/traceability-gap/",
        "/synthetic-examples/",
        "/evidence-risk-questions/",
    ],
    "claim-drift/index.html": [
        "/evidence-risk/",
        "/context-collapse/",
        "/traceability-gap/",
        "/synthetic-examples/",
        "/evidence-risk-questions/",
    ],
    "traceability-gap/index.html": [
        "/evidence-risk/",
        "/provenance-risk/",
        "/context-collapse/",
        "/claim-drift/",
        "/manual-evidence-checklist/",
        "/evidence-posture-map/",
    ],
    "why-hoax-ai-is-not-a-detector/index.html": [
        "/evidence-risk/",
        "/evidence-posture-map/",
        "/manual-evidence-checklist/",
        "/evidence-risk-questions/",
        "/synthetic-examples/",
    ],
    "manual-evidence-checklist/index.html": [
        "/evidence-posture-map/",
        "/evidence-risk-questions/",
        "/synthetic-examples/",
        "/evidence-risk/",
        "/provenance-risk/",
        "/traceability-gap/",
    ],
    "evidence-posture-map/index.html": [
        "/manual-evidence-checklist/",
        "/evidence-risk-questions/",
        "/synthetic-examples/",
        "/evidence-risk/",
        "/claim-drift/",
        "/traceability-gap/",
    ],
    "synthetic-examples/index.html": [
        "/manual-evidence-checklist/",
        "/evidence-posture-map/",
        "/evidence-risk-questions/",
        "/context-collapse/",
        "/claim-drift/",
        "/traceability-gap/",
    ],
    "evidence-risk-questions/index.html": [
        "/manual-evidence-checklist/",
        "/evidence-posture-map/",
        "/synthetic-examples/",
        "/evidence-risk/",
        "/context-collapse/",
        "/claim-drift/",
    ],
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
    LINKING_DOC,
    STANDARD_DOC,
    AUDIT_DOC,
    LINKING_JSON,
    LINKING_SCHEMA,
    SPRINT_AUDIT,
    "validators/validate_public_reference_authority_internal_linking_v1.py",
    INDEX,
    *UTILITY_PAGES,
    *REFERENCE_PAGES,
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


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
    for rel in [LINKING_DOC, STANDARD_DOC, AUDIT_DOC, LINKING_JSON, LINKING_SCHEMA, SPRINT_AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(LINKING_JSON)
    if data.get("linking_id") != "public-reference-authority-internal-linking-v1":
        error("linking_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-105":
        error("decision_ref must be DEC-105")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if len(data.get("utility_routes", [])) != 4:
        error("utility_routes must contain exactly 4 routes")
        ok = False
    if len(data.get("reference_routes", [])) != 6:
        error("reference_routes must contain exactly 6 routes")
        ok = False
    required = {
        "reference_path",
        "related_concepts",
        "use_next",
        "ai_readable_link_capsule",
        "homepage_reference_graph",
        "page_end_reference_navigation",
    }
    if not required.issubset(set(data.get("required_components", []))):
        error("required_components incomplete")
        ok = False
    return ok


def validate_surface_counts() -> bool:
    ok = True
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if sitemap.count("<loc>") != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have exactly {EXPECTED_SITEMAP} URLs")
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have exactly {EXPECTED_ROUTES} entries")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    if "hoax.ai reference graph" not in lower:
        error("homepage missing Hoax.ai Reference Graph section")
        ok = False
    if "evidence before verdict" not in lower:
        error("homepage missing Evidence before verdict section")
        ok = False
    for path in UTILITY_PATHS + REFERENCE_PATHS:
        if f'href="{path}"' not in content:
            error(f"homepage missing link to {path}")
            ok = False
    return ok


def validate_page(rel: str, is_utility: bool) -> bool:
    ok = True
    path = ROOT / rel
    content = path.read_text(encoding="utf-8")
    lower = content.lower()
    if "reference path" not in lower:
        error(f"{rel}: missing Reference Path section")
        ok = False
    if "page-end-reference-nav" not in content:
        error(f"{rel}: missing page-end reference navigation")
        ok = False
    if "ai-readable link capsule" not in lower:
        error(f"{rel}: missing AI-Readable Link Capsule")
        ok = False
    if is_utility:
        if "continue with" not in lower and "use next" not in lower:
            error(f"{rel}: missing Continue with / Use next section")
            ok = False
        others = [p for p in UTILITY_PATHS if p != UTILITY_PAGES[rel]]
        missing = [p for p in others if p not in content]
        if missing:
            error(f"{rel}: must link to all other utility routes, missing {missing}")
            ok = False
        ref_links = sum(1 for p in REFERENCE_PATHS if p in content)
        if ref_links < 3:
            error(f"{rel}: must link to at least 3 reference routes")
            ok = False
    else:
        if "related concepts" not in lower:
            error(f"{rel}: missing Related concepts section")
            ok = False
        self_path = REFERENCE_PAGES[rel]
        siblings = [p for p in REFERENCE_PATHS if p != self_path]
        sib_count = sum(1 for p in siblings if p in content)
        if sib_count < 3:
            error(f"{rel}: must link to at least 3 sibling reference routes")
            ok = False
        util_count = sum(1 for p in UTILITY_PATHS if p in content)
        if util_count < 2:
            error(f"{rel}: must link to at least 2 utility routes")
            ok = False
    for req in ROUTE_REQUIRED_LINKS.get(rel, []):
        if req not in content:
            error(f"{rel}: missing required contextual link {req}")
            ok = False
    if "<form" in lower or "<input" in lower:
        error(f"{rel}: forms/inputs forbidden")
        ok = False
    if re.search(r"<script\b", content, re.I):
        error(f"{rel}: JavaScript forbidden")
        ok = False
    for claim in FORBIDDEN_CLAIMS:
        for line in content.splitlines():
            if line_has_unnegated_claim(line, claim):
                error(f"{rel}: forbidden claim {claim!r}")
                ok = False
                break
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-105" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-105 missing")
        ok = False
    if "validate_public_reference_authority_internal_linking_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 87 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    ):
        error("publisher status must reflect Sprint 87 internal linking validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0088" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0088 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0081" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0081 missing")
        ok = False
    if "Sprint 87 | COMPLETE | G87 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 87 row")
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
    if not validate_surface_counts():
        ok = False
    if not validate_homepage():
        ok = False
    for rel in UTILITY_PAGES:
        if not validate_page(rel, is_utility=True):
            ok = False
    for rel in REFERENCE_PAGES:
        if not validate_page(rel, is_utility=False):
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
