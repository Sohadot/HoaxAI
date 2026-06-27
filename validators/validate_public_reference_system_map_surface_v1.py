#!/usr/bin/env python3
"""Validate Sprint 108 — Public Reference System Map Surface v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
    validate_public_surface,
)

INDEX_DOC = "PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_SYSTEM_MAP_AUDIT_V1.md"
STANDARD_DOC = "PUBLIC_SYSTEM_MAP_STANDARD_V1.md"
INDEX_JSON = "data/public-reference-system-map-surface-v1.json"
INDEX_SCHEMA = "data/public-reference-system-map-surface-v1.schema.json"
SPRINT_DOC = "SPRINT_108_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_V1.md"
INDEX = "index.html"
EXPECTED = 83
MIN_WORDS = 850

NEW_PAGES = [
    "system-map/index.html",
    "system-map/route-groups/index.html",
    "system-map/human-review-paths/index.html",
    "system-map/ai-retrieval-paths/index.html",
    "system-map/boundary-layers/index.html",
]

NEW_PATHS = [
    "/system-map/",
    "/system-map/route-groups/",
    "/system-map/human-review-paths/",
    "/system-map/ai-retrieval-paths/",
    "/system-map/boundary-layers/",
]

ROUTE_IDS = [f"ROUTE-{i:04d}" for i in range(79, 84)]
PUB_FILE_IDS = [f"PUB-FILE-{i:04d}" for i in range(79, 84)]

REQUIRED_SECTIONS = [
    "Reference summary",
    "Map purpose",
    "System map path",
    "What this map supports",
    "What this map does not claim",
    "Reference Answer",
    "Source Confidence",
    "Cite This Reference",
    "Retrieval Capsule",
    "Boundary reminder",
    "Non-transactional review boundary",
]

REQUIRED_ANCHORS = [
    "reference-summary",
    "map-purpose",
    "system-map-path",
    "reference-answer",
    "source-confidence",
    "cite-this-reference",
    "retrieval-capsule",
    "boundary",
]

DASHBOARD_PROHIBITION = "Not a scorecard, rating system, or dashboard"

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
    "for sale",
    "asking price",
    "valuation",
    "term sheet",
    "broker representation",
    "sale offer",
    "acquisition terms available",
    "contact to buy",
    "make an offer",
    "purchase this domain",
    "price available",
    "listed for sale",
    "private data room",
    "downloadable report",
    "pitch deck",
    "sales page",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

STALE_ROUTE_COUNTS = [
    "58-route",
    "58 routes",
    "63-route",
    "63 routes",
    "68-route",
    "68 routes",
    "73-route",
    "73 routes",
    "78-route",
    "78 routes",
]

SOURCE_LOCS = [INDEX_DOC, AUDIT_DOC, STANDARD_DOC, INDEX_JSON, INDEX_SCHEMA, SPRINT_DOC]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def visible_words(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def line_has_unnegated_claim(line: str, claim: str) -> bool:
    lower = line.lower()
    if claim not in lower:
        return False
    pos = 0
    while True:
        idx = lower.find(claim, pos)
        if idx < 0:
            return False
        end = idx + len(claim)
        if end < len(lower) and lower[end].isalnum():
            pos = idx + 1
            continue
        if claim == "valuation" and idx > 0 and lower[idx - 1] == "e":
            pos = idx + len(claim)
            continue
        prefix = lower[max(0, idx - 80) : idx]
        if "is not a" in lower and idx > lower.find("is not a"):
            pos = idx + len(claim)
            continue
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
    data = load_json(INDEX_JSON)
    if data.get("decision_ref") != "DEC-126":
        error("decision_ref must be DEC-126")
        ok = False
    if data.get("homepage_release_snapshot_updated") is not True:
        error("homepage_release_snapshot_updated must be true")
        ok = False
    if data.get("new_public_routes_added") is not True:
        error("new_public_routes_added must be true")
        ok = False
    if data.get("dashboard_forbidden") is not True:
        error("dashboard_forbidden must be true")
        ok = False
    if set(data.get("public_routes_added", [])) != set(NEW_PATHS):
        error("public_routes_added must list exactly the five new routes")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED:
        error(f"expected_sitemap_url_count_after must be {EXPECTED}")
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
        "pricing_statement_authorized",
        "transaction_page_authorized",
        "acquisition_term_document_authorized",
        "representative_mandate_authorized",
        "legal_representation_authorized",
        "financial_representation_authorized",
        "downloadable_report_authorized",
        "private_data_room_authorized",
        "pitch_deck_authorized",
        "sales_page_authorized",
    ):
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    sitemap_count = len([u for u in ET.parse(ROOT / "sitemap.xml").getroot().iter() if u.tag.endswith("loc")])
    routes = load_json("data/route-registry.json").get("routes", [])
    if sitemap_count != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {sitemap_count}")
        ok = False
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have {PUBLIC_SITEMAP_URL_COUNT} entries, found {len(routes)}")
        ok = False
    by_id = {r.get("route_id"): r for r in routes}
    for rid, path in zip(ROUTE_IDS, NEW_PATHS):
        if rid not in by_id:
            error(f"route registry missing {rid}")
            ok = False
        elif by_id[rid].get("path") != path:
            error(f"{rid} path mismatch")
            ok = False
    return ok


def validate_public_file_registry() -> bool:
    ok = True
    pfr = load_json("data/public-file-registry.json")
    by_id = {f.get("file_id"): f for f in pfr.get("public_files", [])}
    for fid, rel in zip(PUB_FILE_IDS, NEW_PAGES):
        if fid not in by_id:
            error(f"public-file-registry missing {fid}")
            ok = False
        elif by_id[fid].get("path") != rel:
            error(f"{fid} path mismatch")
            ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    if "System Map" not in content:
        error("homepage must include System Map section")
        ok = False
    if f"Current public route count: {PUBLIC_SITEMAP_URL_COUNT}" not in content:
        error(f"homepage snapshot must include Current public route count: {PUBLIC_SITEMAP_URL_COUNT}")
        ok = False
    if "<strong>System Map</strong> — 5 routes" not in content:
        error("homepage Public Release Integrity Snapshot must include System Map route group")
        ok = False
    for path in NEW_PATHS:
        if f'href="{path}' not in content and f"href='{path}" not in content:
            error(f"homepage must link to {path}")
            ok = False
    return ok


def validate_new_page(rel: str) -> bool:
    ok = True
    fp = ROOT / rel
    if not fp.is_file():
        error(f"missing {rel}")
        return False
    content = fp.read_text(encoding="utf-8")
    wc = visible_words(content)
    if wc < MIN_WORDS:
        error(f"{rel}: need at least {MIN_WORDS} visible words, found {wc}")
        ok = False
    if len(re.findall(r"<h1\b", content, re.I)) != 1:
        error(f"{rel}: expected exactly one H1")
        ok = False
    for field in ('rel="canonical"', 'name="description"', "og:title", "og:description"):
        if field not in content.lower():
            error(f"{rel}: missing {field}")
            ok = False
    for section in REQUIRED_SECTIONS:
        if section not in content:
            error(f"{rel}: missing section {section!r}")
            ok = False
    for anchor in REQUIRED_ANCHORS:
        if f'id="{anchor}"' not in content:
            error(f"{rel}: missing anchor {anchor}")
            ok = False
    if DASHBOARD_PROHIBITION not in content:
        error(f"{rel}: missing dashboard prohibition {DASHBOARD_PROHIBITION!r}")
        ok = False
    if 'href="/system-map/"' not in content and 'href="/system-map/#' not in content:
        error(f"{rel}: must link to /system-map/")
        ok = False
    strategic_external = sum(
        1
        for p in (
            "/executive-overview/",
            "/entry-points/",
            "/narrative/",
            "/acquisition-readiness/",
            "/external-review/",
            "/reviewer-packet/",
            "/strategic-review/",
        )
        if p in content
    )
    if strategic_external < 3:
        error(f"{rel}: must link to at least 3 strategic layer routes")
        ok = False
    utility_ref = sum(
        1
        for p in (
            "/manual-evidence-checklist/",
            "/evidence-posture-map/",
            "/evidence-risk/",
            "/evidence-risk-questions/",
            "/synthetic-examples/",
            "/provenance-risk/",
            "/source-ambiguity/",
            "/boundary-integrity/",
            "/reference/",
            "/standard/",
            "/protocol/",
            "/why-hoax-ai-is-not-a-detector/",
            "/pathways/",
        )
        if p in content
    )
    if utility_ref < 5:
        error(f"{rel}: must link to at least 5 reference or utility routes")
        ok = False
    sibling_links = sum(1 for p in NEW_PATHS if f'href="{p}' in content or f"href='{p}" in content)
    if sibling_links < 2:
        error(f"{rel}: must link to at least 2 sibling system-map routes")
        ok = False
    if "Non-transactional review boundary" not in content:
        error(f"{rel}: missing non-transactional review boundary")
        ok = False
    if "<form" in content.lower() or "<input" in content.lower():
        error(f"{rel}: forms/inputs forbidden")
        ok = False
    if re.search(r'<script\b(?![^>]*type=["\']application/ld\+json["\'])', content, re.I):
        error(f"{rel}: JavaScript forbidden")
        ok = False
    return ok


def validate_stale_route_counts() -> bool:
    ok = True
    for rel in NEW_PAGES:
        lower = (ROOT / rel).read_text(encoding="utf-8").lower()
        for stale in STALE_ROUTE_COUNTS:
            if stale in lower:
                error(f"{rel}: stale route-count language {stale!r}")
                ok = False
    return ok


def validate_reviewer_packet_index() -> bool:
    ok = True
    content = (ROOT / "reviewer-packet/public-surface-index/index.html").read_text(encoding="utf-8")
    if "System map" not in content and "System Map" not in content:
        error("reviewer packet public surface index must include System Map route group")
        ok = False
    return ok


def validate_executive_overview_system() -> bool:
    ok = True
    content = (ROOT / "executive-overview/public-reference-system/index.html").read_text(encoding="utf-8")
    if "system map" not in content.lower():
        error("executive overview public reference system must mention system map")
        ok = False
    return ok


def validate_public_html_copy() -> bool:
    ok = True
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        content = (ROOT / rel).read_text(encoding="utf-8")
        for claim in FORBIDDEN_CLAIMS:
            for line in content.splitlines():
                if line_has_unnegated_claim(line, claim):
                    error(f"{rel}: forbidden claim {claim!r}")
                    ok = False
                    break
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-126" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-126 missing")
        ok = False
    if "validate_public_reference_system_map_surface_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 108 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") != PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION:
        error("publisher status must reflect Sprint 108 system map surface validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_system_map_surface_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0109" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0109 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0102" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0102 missing")
        ok = False
    if "Sprint 108 | COMPLETE | G108 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 108 row")
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
    if not validate_public_file_registry():
        ok = False
    if not validate_homepage():
        ok = False
    for rel in NEW_PAGES:
        if not validate_new_page(rel):
            ok = False
    if not validate_stale_route_counts():
        ok = False
    if not validate_reviewer_packet_index():
        ok = False
    if not validate_executive_overview_system():
        ok = False
    if not validate_public_html_copy():
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
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
