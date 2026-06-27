#!/usr/bin/env python3
"""Validate Sprint 95 — Public Reference Surface Authority Review v1."""

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
)

REVIEW_DOC = "PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_V1.md"
REPAIR_LOG = "PUBLIC_REFERENCE_SURFACE_AUTHORITY_REPAIR_LOG_V1.md"
STANDARD_DOC = "PUBLIC_REFERENCE_SURFACE_AUTHORITY_STANDARD_V1.md"
REVIEW_JSON = "data/public-reference-surface-authority-review-v1.json"
REVIEW_SCHEMA = "data/public-reference-surface-authority-review-v1.schema.json"
SPRINT_DOC = "SPRINT_95_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_V1.md"
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

LEGACY_SUPPORT_PAGES = [
    "language/index.html",
    "reference/evidence-posture/index.html",
    "reference/artifact-subject-separation/index.html",
    "reference/source-confidence/index.html",
    "reference/provenance-gap/index.html",
    "reference/not-assessable/index.html",
    "reference/output-boundary/index.html",
    "reference/synthetic-fragility/index.html",
    "reference/evidence-chain/index.html",
    "reference/context-collapse/index.html",
    "reference/claim-source-traceability/index.html",
    "reference/attribution-boundary/index.html",
    "reference/claim-drift/index.html",
    "reference/evidence-limitation/index.html",
    "reference/interpretation-risk/index.html",
    "standard/evidence-posture/index.html",
    "protocol/evidence-posture/index.html",
    "interface/evidence-field/index.html",
]

PUBLIC_LINK_PREFIXES = (
    "/manual-evidence-checklist/",
    "/evidence-posture-map/",
    "/synthetic-examples/",
    "/evidence-risk-questions/",
    "/evidence-risk/",
    "/provenance-risk/",
    "/context-collapse/",
    "/claim-drift/",
    "/traceability-gap/",
    "/why-hoax-ai-is-not-a-detector/",
    "/source-ambiguity/",
    "/artifact-claim-gap/",
    "/boundary-integrity/",
    "/evidence-weight/",
    "/interpretation-risk/",
    "/not-assessable-posture/",
    "/pathways/",
    "/standard/",
    "/protocol/",
    "/reference/",
)

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

EXTERNAL_OPS_TERMS = [
    "github pages enablement",
    "cloudflare dns",
    "deploy to production",
    "custom domain launch",
]

SOURCE_LOCS = [
    REVIEW_DOC,
    REPAIR_LOG,
    STANDARD_DOC,
    REVIEW_JSON,
    REVIEW_SCHEMA,
    SPRINT_DOC,
    "validators/validate_public_reference_surface_authority_review_v1.py",
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
    for rel in [REVIEW_DOC, REPAIR_LOG, STANDARD_DOC, REVIEW_JSON, REVIEW_SCHEMA, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(REVIEW_JSON)
    if data.get("decision_ref") != "DEC-113":
        error("decision_ref must be DEC-113")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if not data.get("visible_repairs_made"):
        error("visible_repairs_made must be true")
        ok = False
    if data.get("total_repairs_made", 0) <= 0:
        error("total_repairs_made must be greater than 0")
        ok = False
    for flag in (
        "upload_authorized",
        "scoring_authorized",
        "verdict_authorized",
        "detector_claim_authorized",
        "public_api_authorized",
        "automated_report_authorized",
        "javascript_authorized",
        "forms_authorized",
        "real_world_case_evaluation_authorized",
        "chatbot_authorized",
        "generator_authorized",
    ):
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    for rel in [REVIEW_DOC, REPAIR_LOG, STANDARD_DOC, REVIEW_JSON, SPRINT_DOC]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in EXTERNAL_OPS_TERMS:
            if term in text:
                error(f"{rel}: external operations content {term!r}")
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


def validate_html_meta(rel: str) -> bool:
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
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    if "navigate hoax.ai by evidence-risk layer" not in lower:
        error("homepage missing Navigate Hoax.ai by Evidence-Risk Layer section")
        ok = False
    if "hoax.ai system navigation" not in lower:
        error("homepage missing Hoax.ai System Navigation")
        ok = False
    return ok


def validate_consolidated_page(rel: str) -> bool:
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
    return ok


def validate_legacy_page(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    has_role = "page role:" in lower
    has_fit = "how this page fits hoax.ai" in lower
    if not has_role and not has_fit:
        error(f"{rel}: missing page role label or How this page fits Hoax.ai")
        ok = False
    if not any(prefix in content for prefix in PUBLIC_LINK_PREFIXES):
        error(f"{rel}: must link to at least one public utility or reference route")
        ok = False
    if "hoax.ai system navigation" not in lower:
        error(f"{rel}: missing Hoax.ai System Navigation")
        ok = False
    return ok


def validate_surface_behavior(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
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
    if "DEC-113" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-113 missing")
        ok = False
    if "validate_public_reference_surface_authority_review_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 95 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
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

    ):
        error("publisher status must reflect Sprint 95 authority review validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0096" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0096 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0089" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0089 missing")
        ok = False
    if "Sprint 95 | COMPLETE | G95 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 95 row")
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
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        if not validate_html_meta(rel):
            ok = False
        if not validate_surface_behavior(rel):
            ok = False
    for rel in ALL_22:
        if not validate_consolidated_page(rel):
            ok = False
    for rel in LEGACY_SUPPORT_PAGES:
        if not validate_legacy_page(rel):
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
