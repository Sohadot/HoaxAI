#!/usr/bin/env python3
"""Validate Sprint 94 — Public Reference Navigation and IA Consolidation v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    PUBLIC_SITEMAP_URL_COUNT,
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    validate_public_surface,
)

IA_DOC = "PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_NAVIGATION_IA_AUDIT_V1.md"
STANDARD_DOC = "PUBLIC_NAVIGATION_IA_STANDARD_V1.md"
IA_JSON = "data/public-reference-navigation-ia-consolidation-v1.json"
IA_SCHEMA = "data/public-reference-navigation-ia-consolidation-v1.schema.json"
SPRINT_DOC = "SPRINT_94_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_V1.md"
INDEX = "index.html"
EXPECTED = 41

UTILITY_PAGES = [
    "manual-evidence-checklist/index.html",
    "evidence-posture-map/index.html",
    "synthetic-examples/index.html",
    "evidence-risk-questions/index.html",
]

CORE_PAGES = [
    "evidence-risk/index.html",
    "provenance-risk/index.html",
    "context-collapse/index.html",
    "claim-drift/index.html",
    "traceability-gap/index.html",
    "why-hoax-ai-is-not-a-detector/index.html",
]

DEEP_PAGES = [
    "source-ambiguity/index.html",
    "artifact-claim-gap/index.html",
    "boundary-integrity/index.html",
    "evidence-weight/index.html",
    "interpretation-risk/index.html",
    "not-assessable-posture/index.html",
]

PATHWAY_PAGES = [
    "pathways/source-unclear/index.html",
    "pathways/provenance-weak/index.html",
    "pathways/context-missing/index.html",
    "pathways/claim-overextended/index.html",
    "pathways/traceability-incomplete/index.html",
    "pathways/posture-not-assessable/index.html",
]

ALL_22 = UTILITY_PAGES + CORE_PAGES + DEEP_PAGES + PATHWAY_PAGES

PATHWAY_LINKS = {
    "source-ambiguity/index.html": "/pathways/source-unclear/",
    "provenance-risk/index.html": "/pathways/provenance-weak/",
    "context-collapse/index.html": "/pathways/context-missing/",
    "interpretation-risk/index.html": "/pathways/context-missing/",
    "claim-drift/index.html": "/pathways/claim-overextended/",
    "artifact-claim-gap/index.html": "/pathways/claim-overextended/",
    "traceability-gap/index.html": "/pathways/traceability-incomplete/",
    "not-assessable-posture/index.html": "/pathways/posture-not-assessable/",
}

UTILITY_ROUTES = [f"/{p.replace('/index.html', '')}/" for p in UTILITY_PAGES]
CORE_ROUTES = [f"/{p.replace('/index.html', '')}/" for p in CORE_PAGES]
DEEP_ROUTES = [f"/{p.replace('/index.html', '')}/" for p in DEEP_PAGES]
PATHWAY_ROUTES = [
    "/pathways/source-unclear/",
    "/pathways/provenance-weak/",
    "/pathways/context-missing/",
    "/pathways/claim-overextended/",
    "/pathways/traceability-incomplete/",
    "/pathways/posture-not-assessable/",
]

ROUTE_GROUPS = [
    "Public Utilities",
    "Core Reference Concepts",
    "Deep Reference Concepts",
    "Evidence-Risk Pathways",
    "Boundary and Standard References",
]

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
    IA_DOC,
    AUDIT_DOC,
    STANDARD_DOC,
    IA_JSON,
    IA_SCHEMA,
    SPRINT_DOC,
    "validators/validate_public_reference_navigation_ia_consolidation_v1.py",
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
    for rel in [IA_DOC, AUDIT_DOC, STANDARD_DOC, IA_JSON, IA_SCHEMA, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(IA_JSON)
    if data.get("decision_ref") != "DEC-112":
        error("decision_ref must be DEC-112")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if sorted(data.get("route_groups", [])) != sorted(ROUTE_GROUPS):
        error("route_groups must list exactly five IA groups")
        ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    count = PUBLIC_SITEMAP_URL_COUNT
    if (ROOT / "sitemap.xml").read_text(encoding="utf-8").count("<loc>") != count:
        error(f"sitemap must have exactly {count} URLs")
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != count:
        error(f"route registry must have exactly {count} entries")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    if "navigate hoax.ai by evidence-risk layer" not in lower:
        error("homepage missing Navigate Hoax.ai by Evidence-Risk Layer section")
        ok = False
    for group in ROUTE_GROUPS:
        if group.lower() not in lower:
            error(f"homepage missing route group {group!r}")
            ok = False
    if "hoax.ai system navigation" not in lower:
        error("homepage missing Hoax.ai System Navigation")
        ok = False
    for route in UTILITY_ROUTES + CORE_ROUTES + DEEP_ROUTES + PATHWAY_ROUTES:
        if route not in content:
            error(f"homepage missing link to {route}")
            ok = False
    return ok


def validate_page(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    if "page role:" not in lower:
        error(f"{rel}: missing page role label")
        ok = False
    if "hoax.ai system navigation" not in lower:
        error(f"{rel}: missing Hoax.ai System Navigation")
        ok = False
    if "ia capsule" not in lower:
        error(f"{rel}: missing IA Capsule")
        ok = False
    if "where to go next" not in lower:
        error(f"{rel}: missing Where to go next refinement")
        ok = False
    util_count = sum(1 for u in UTILITY_ROUTES if u in content)
    if util_count < 3 and rel in PATHWAY_PAGES:
        error(f"{rel}: must link to at least 3 utility routes")
        ok = False
    ref_routes = CORE_ROUTES + DEEP_ROUTES + ["/reference/evidence-posture/", "/why-hoax-ai-is-not-a-detector/"]
    ref_count = sum(1 for r in ref_routes if r in content)
    if ref_count < 5 and rel in PATHWAY_PAGES:
        error(f"{rel}: must link to at least 5 reference routes")
        ok = False
    if rel in PATHWAY_PAGES:
        page_path = "/" + rel.replace("index.html", "")
        siblings = [r for r in PATHWAY_ROUTES if r != page_path]
        sib_count = sum(1 for s in siblings if s in content)
        if sib_count < 2:
            error(f"{rel}: must link to at least 2 sibling pathway routes")
            ok = False
    if rel in PATHWAY_LINKS and PATHWAY_LINKS[rel] not in content:
        error(f"{rel}: missing pathway link {PATHWAY_LINKS[rel]}")
        ok = False
    if "<form" in lower or "<input" in lower:
        error(f"{rel}: forms/inputs forbidden")
        ok = False
    if re.search(r'<script\b(?![^>]*type=["\']application/ld\+json["\'])', content, re.I):
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
    if "DEC-112" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-112 missing")
        ok = False
    if "validate_public_reference_navigation_ia_consolidation_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 94 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,

    ):
        error("publisher status must reflect Sprint 94 navigation IA consolidation validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0095" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0095 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0088" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0088 missing")
        ok = False
    if "Sprint 94 | COMPLETE | G94 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 94 row")
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
    if not validate_homepage():
        ok = False
    for rel in ALL_22:
        if not validate_page(rel):
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
