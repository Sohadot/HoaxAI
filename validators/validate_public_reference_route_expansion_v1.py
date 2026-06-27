#!/usr/bin/env python3
"""Validate Sprint 85 — Public Reference Route Expansion v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    PUBLIC_SITEMAP_URL_COUNT,
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

EXPANSION_DOC = "PUBLIC_REFERENCE_ROUTE_EXPANSION_V1.md"
STANDARD_DOC = "HUMAN_AI_REFERENCE_UNIT_STANDARD_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_ROUTE_EXPANSION_AUDIT_V1.md"
EXPANSION_JSON = "data/public-reference-route-expansion-v1.json"
EXPANSION_SCHEMA = "data/public-reference-route-expansion-v1.schema.json"
SPRINT_AUDIT = "SPRINT_85_PUBLIC_REFERENCE_ROUTE_EXPANSION_V1.md"
INDEX = "index.html"
EXPECTED_ROUTES = 29
EXPECTED_SITEMAP = 29
MIN_VISIBLE_WORDS = 750

REFERENCE_PAGES = {
    "evidence-risk/index.html": "Evidence Risk",
    "provenance-risk/index.html": "Provenance Risk",
    "context-collapse/index.html": "Context Collapse",
    "claim-drift/index.html": "Claim Drift",
    "traceability-gap/index.html": "Traceability Gap",
    "why-hoax-ai-is-not-a-detector/index.html": "Why Hoax.ai Is Not a Detector",
}

REFERENCE_PATHS = [
    "/evidence-risk/",
    "/provenance-risk/",
    "/context-collapse/",
    "/claim-drift/",
    "/traceability-gap/",
    "/why-hoax-ai-is-not-a-detector/",
]

ROUTE_IDS = [f"ROUTE-{i:04d}" for i in range(24, 30)]

UTILITY_LINKS = [
    "/manual-evidence-checklist/",
    "/evidence-posture-map/",
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
    EXPANSION_DOC,
    STANDARD_DOC,
    AUDIT_DOC,
    EXPANSION_JSON,
    EXPANSION_SCHEMA,
    SPRINT_AUDIT,
    "validators/validate_public_reference_route_expansion_v1.py",
    *REFERENCE_PAGES,
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def visible_words(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"[A-Za-z0-9']+", text))


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
    for rel in SOURCE_LOCS:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    return ok


def validate_expansion_json() -> bool:
    ok = True
    try:
        data = load_json(EXPANSION_JSON)
    except json.JSONDecodeError as exc:
        error(f"expansion JSON parse error: {exc}")
        return False
    json.loads((ROOT / EXPANSION_SCHEMA).read_text(encoding="utf-8"))
    if data.get("expansion_id") != "public-reference-route-expansion-v1":
        error("expansion_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-103":
        error("decision_ref must be DEC-103")
        ok = False
    if data.get("sprint") != "Sprint 85":
        error("sprint must be Sprint 85")
        ok = False
    if sorted(data.get("public_routes_added", [])) != sorted(REFERENCE_PATHS):
        error("public_routes_added must list exactly six reference routes")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED_SITEMAP:
        error("expected_sitemap_url_count_after must be 29")
        ok = False
    for key in [
        "upload_authorized",
        "scoring_authorized",
        "verdict_authorized",
        "detector_claim_authorized",
        "public_api_authorized",
        "automated_report_authorized",
        "javascript_authorized",
        "forms_authorized",
        "real_world_case_evaluation_authorized",
    ]:
        if data.get(key) is not False:
            error(f"{key} must be false")
            ok = False
    for key in [
        "public_reference_routes_authorized",
        "ai_retrieval_capsules_authorized",
        "non_verdict_reference_units_authorized",
    ]:
        if data.get(key) is not True:
            error(f"{key} must be true")
            ok = False
    return ok


def validate_reference_pages() -> bool:
    ok = True
    for rel, h1 in REFERENCE_PAGES.items():
        content = (ROOT / rel).read_text(encoding="utf-8")
        lower = content.lower()
        if len(re.findall(r"<h1\b", content, re.I)) != 1:
            error(f"{rel}: expected exactly one H1")
            ok = False
        if extract_h1(content) != h1:
            error(f"{rel}: H1 must be {h1!r}")
            ok = False
        if 'rel="canonical"' not in content:
            error(f"{rel}: missing canonical")
            ok = False
        if 'name="description"' not in content:
            error(f"{rel}: missing meta description")
            ok = False
        if 'property="og:title"' not in content or 'property="og:description"' not in content:
            error(f"{rel}: missing Open Graph title/description")
            ok = False
        wc = visible_words(content)
        if wc < MIN_VISIBLE_WORDS:
            error(f"{rel}: expected at least {MIN_VISIBLE_WORDS} visible words, found {wc}")
            ok = False
        if "ai-readable reference capsule" not in lower and "ai-readable link capsule" not in lower:
            error(f"{rel}: missing AI-readable reference capsule")
            ok = False
        if "what not to conclude" not in lower:
            error(f"{rel}: missing What not to conclude section")
            ok = False
        if "questions to ask" not in lower:
            error(f"{rel}: missing Questions to ask section")
            ok = False
        if "non-verdict" not in lower and "non verdict" not in lower:
            error(f"{rel}: missing non-verdict boundary language")
            ok = False
        for util in UTILITY_LINKS:
            if util not in content:
                error(f"{rel}: must link to {util}")
                ok = False
        siblings = sum(1 for p in REFERENCE_PATHS if p in content and p.strip("/") not in rel)
        if siblings < 2:
            error(f"{rel}: must link to at least two sibling reference routes")
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
        for claim in FORBIDDEN_CLAIMS:
            for line in content.splitlines():
                if line_has_unnegated_claim(line, claim):
                    error(f"{rel}: forbidden claim {claim!r}")
                    ok = False
                    break
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    if "explore the evidence-risk reference layer" not in lower:
        error("homepage missing reference layer section title")
        ok = False
    for path in REFERENCE_PATHS:
        if path not in content:
            error(f"homepage missing link to {path}")
            ok = False
    if "<form" in lower or re.search(r"<script\b", content, re.I):
        error("homepage must not add forms or JavaScript")
        ok = False
    return ok


def validate_surface_counts() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) < EXPECTED_ROUTES:
        error(f"route registry must have exactly {EXPECTED_ROUTES} entries")
        ok = False
    by_id = {r.get("route_id"): r for r in routes}
    for rid, path in zip(ROUTE_IDS, REFERENCE_PATHS):
        if rid not in by_id:
            error(f"route registry missing {rid}")
            ok = False
        elif by_id[rid].get("path") != path:
            error(f"{rid}: path must be {path}")
            ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [
        e.text.strip().lower()
        for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")
        if e.text
    ]
    if len(locs) < EXPECTED_SITEMAP:
        error(f"sitemap must have exactly {EXPECTED_SITEMAP} URLs")
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
    if "DEC-103" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-103 missing")
        ok = False
    if "validate_public_reference_route_expansion_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 85 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_GROUP_DEEPENING_VALIDATION,
    ):
        error("publisher status must be blocked_until_public_reference_route_expansion_validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0087" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0087 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0080" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0080 missing")
        ok = False
    if "Sprint 85 | COMPLETE | G85 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 85 row")
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
            validate_expansion_json,
            validate_reference_pages,
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
