#!/usr/bin/env python3
"""Validate Sprint 100 — Public Reference Release Integrity Audit v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
    validate_public_surface,
)

AUDIT_DOC = "PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_V1.md"
REPAIR_DOC = "PUBLIC_REFERENCE_RELEASE_INTEGRITY_REPAIR_LOG_V1.md"
AUDIT_JSON = "data/public-reference-release-integrity-audit-v1.json"
AUDIT_SCHEMA = "data/public-reference-release-integrity-audit-v1.schema.json"
SPRINT_DOC = "SPRINT_100_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_V1.md"
INDEX = "index.html"
EXPECTED = 58

STALE_ROUTE_COUNTS = ["29 urls", "35 urls", "41 urls", "47 urls", "52 urls"]

FORBIDDEN_POSITIVE_TRANSACTION = [
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
]

FORBIDDEN_DETECTOR_COPY = [
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

SOURCE_LOCS = [AUDIT_DOC, REPAIR_DOC, AUDIT_JSON, AUDIT_SCHEMA, SPRINT_DOC]

PUBLIC_FILE_REGISTRY_SUPPORT = {"styles.css", "sitemap.xml", "robots.txt"}


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def route_to_file(path: str) -> str:
    p = path.strip("/")
    return "index.html" if not p else f"{p}/index.html"


def line_has_unnegated_claim(line: str, claim: str) -> bool:
    lower = line.lower()
    if claim not in lower:
        return False
    pos = 0
    while True:
        idx = lower.find(claim, pos)
        if idx < 0:
            return False
        if claim == "valuation" and idx > 0 and lower[idx - 1] == "e":
            pos = idx + len(claim)
            continue
        prefix = lower[max(0, idx - 80) : idx]
        if not NEGATION_PATTERN.search(prefix + claim):
            return True
        pos = idx + len(claim)
    return False


def internal_route_set() -> set[str]:
    routes = load_json("data/route-registry.json").get("routes", [])
    out = set()
    for r in routes:
        p = r.get("path", "/").rstrip("/") or "/"
        out.add(p)
    return out


def validate_artifacts() -> bool:
    ok = True
    for rel in SOURCE_LOCS:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(AUDIT_JSON)
    if data.get("decision_ref") != "DEC-118":
        error("decision_ref must be DEC-118")
        ok = False
    if data.get("homepage_snapshot_added") is not True:
        error("homepage_snapshot_added must be true")
        ok = False
    if data.get("visible_repairs_made") is not True:
        error("visible_repairs_made must be true")
        ok = False
    if data.get("total_repairs_made", 0) < 1:
        error("total_repairs_made must be at least 1")
        ok = False
    for key in (
        "homepage_snapshot_counts_as_visible_repair",
        "public_html_checked_only_for_current_forbidden_copy",
        "historical_governance_not_rewritten_for_current_copy_rules",
        "public_file_registry_scope_checked",
        "stale_route_count_language_checked",
        "broken_internal_route_links_checked",
    ):
        if data.get(key) is not True:
            error(f"{key} must be true")
            ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED:
        error("expected_sitemap_url_count_after must be 58")
        ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    sitemap_count = len([u for u in ET.parse(ROOT / "sitemap.xml").getroot().iter() if u.tag.endswith("loc")])
    registry_count = len(load_json("data/route-registry.json").get("routes", []))
    if sitemap_count != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {sitemap_count}")
        ok = False
    if registry_count != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have {PUBLIC_SITEMAP_URL_COUNT} entries, found {registry_count}")
        ok = False
    data = load_json(AUDIT_JSON)
    if data.get("expected_sitemap_url_count_after") != 58:
        error("historical expected_sitemap_url_count_after must remain 58 for Sprint 100")
        ok = False
    return ok


def validate_homepage_snapshot() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    if "Public Release Integrity Snapshot" not in content:
        error("homepage must include Public Release Integrity Snapshot")
        ok = False
    if 'id="public-release-integrity-snapshot"' not in content:
        error("homepage snapshot section id missing")
        ok = False
    required_phrases = [
        "public evidence-risk reference system",
        "strategic entry points",
        "strategic narrative pages",
        "strategic readiness pages",
        "does not produce automated authenticity labels",
        "not a transaction page",
        "not a pricing statement",
    ]
    lower = content.lower()
    for phrase in required_phrases:
        if phrase not in lower:
            error(f"homepage snapshot missing phrase: {phrase}")
            ok = False
    return ok


def validate_route_files_and_metadata() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    for r in routes:
        rel = route_to_file(r["path"])
        fp = ROOT / rel
        if not fp.is_file():
            error(f"missing route file {rel} for {r['path']}")
            ok = False
            continue
        content = fp.read_text(encoding="utf-8")
        h1 = len(re.findall(r"<h1\b", content, re.I))
        if h1 != 1:
            error(f"{rel}: expected exactly one H1, found {h1}")
            ok = False
        if 'rel="canonical"' not in content.lower():
            error(f"{rel}: missing canonical")
            ok = False
        if 'name="description"' not in content.lower():
            error(f"{rel}: missing meta description")
            ok = False
        if "og:title" not in content.lower():
            error(f"{rel}: missing og:title")
            ok = False
        if "og:description" not in content.lower():
            error(f"{rel}: missing og:description")
            ok = False
    return ok


def validate_internal_links() -> bool:
    ok = True
    routes = internal_route_set()
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        content = (ROOT / rel).read_text(encoding="utf-8")
        for m in re.finditer(r'href="(/[^"]*)"', content):
            href = m.group(1)
            if href.startswith("//"):
                continue
            base = href.split("#", 1)[0].rstrip("/") or "/"
            if base not in routes:
                error(f"{rel}: broken internal route link {href}")
                ok = False
    return ok


def validate_stale_route_counts() -> bool:
    ok = True
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        lower = (ROOT / rel).read_text(encoding="utf-8").lower()
        for stale in STALE_ROUTE_COUNTS:
            if stale in lower:
                error(f"{rel}: stale route-count language {stale!r}")
                ok = False
    return ok


def validate_public_file_registry_scope() -> bool:
    ok = True
    pfr = load_json("data/public-file-registry.json")
    files = pfr.get("public_files", [])
    if not files:
        error("public-file-registry missing public_files")
        return False
    reg_paths = {f["path"] for f in files}
    route_files = {route_to_file(r["path"]) for r in load_json("data/route-registry.json").get("routes", [])}
    missing = sorted(route_files - reg_paths)
    if missing:
        error(f"public-file-registry missing route HTML files: {missing[:5]}")
        ok = False
    extra_html = sorted(p for p in reg_paths if p.endswith(".html") and p not in route_files)
    if extra_html:
        error(f"public-file-registry has unexpected HTML route files: {extra_html[:5]}")
        ok = False
    non_route = sorted(p for p in reg_paths if p not in route_files)
    disallowed = [p for p in non_route if p not in PUBLIC_FILE_REGISTRY_SUPPORT]
    if disallowed:
        error(f"public-file-registry has undocumented non-route files: {disallowed}")
        ok = False
    return ok


def validate_public_html_copy() -> bool:
    ok = True
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        content = (ROOT / rel).read_text(encoding="utf-8")
        lower = content.lower()
        if "<form" in lower or "<input" in lower:
            error(f"{rel}: forms/inputs forbidden")
            ok = False
        if re.search(r'<script\b(?![^>]*type=["\']application/ld\+json["\'])', content, re.I):
            error(f"{rel}: JavaScript forbidden")
            ok = False
        for claim in FORBIDDEN_POSITIVE_TRANSACTION + FORBIDDEN_DETECTOR_COPY:
            for line in content.splitlines():
                if line_has_unnegated_claim(line, claim):
                    error(f"{rel}: forbidden claim {claim!r}")
                    ok = False
                    break
    return ok


def validate_repair_log() -> bool:
    ok = True
    text = (ROOT / REPAIR_DOC).read_text(encoding="utf-8")
    required_cols = [
        "repair_id",
        "page_path",
        "issue_or_improvement_target",
        "repair_applied",
        "route_group_affected",
        "release_integrity_impact",
        "human_readability_impact",
        "ai_retrieval_impact",
        "non_verdict_impact",
        "non_transactional_impact",
        "validator_protection",
    ]
    for col in required_cols:
        if col not in text:
            error(f"repair log missing column {col}")
            ok = False
    if "RIA-001" not in text:
        error("repair log must include RIA-001 homepage snapshot row")
        ok = False
    return ok


def validate_audit_inventory() -> bool:
    ok = True
    text = (ROOT / AUDIT_DOC).read_text(encoding="utf-8")
    if "58-Route Release Inventory" not in text:
        error("audit doc missing 58-Route Release Inventory")
        ok = False
    groups = [
        ("Homepage", "1"),
        ("Public Utilities", "4"),
        ("Core Reference Concepts", "6"),
        ("Deep Reference Concepts", "6"),
        ("Evidence-Risk Pathways", "6"),
        ("Strategic Entry Points", "6"),
        ("Strategic Narrative", "5"),
        ("Strategic Readiness", "6"),
        ("Boundary / Standard / Governance / Support References", "18"),
    ]
    for name, count in groups:
        if name not in text:
            error(f"audit inventory missing group {name}")
            ok = False
        if f"| {count}" not in text and f"| **{count}**" not in text:
            if f"**{count}**" not in text:
                error(f"audit inventory missing count for {name}")
                ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-118" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-118 missing")
        ok = False
    if "validate_public_reference_release_integrity_audit_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 100 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
    ):
        error("publisher status must reflect Sprint 100 release integrity audit validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_release_integrity_audit_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0101" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0101 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0094" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0094 missing")
        ok = False
    if "Sprint 100 | COMPLETE | G100 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 100 row")
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
    if not validate_homepage_snapshot():
        ok = False
    if not validate_route_files_and_metadata():
        ok = False
    if not validate_internal_links():
        ok = False
    if not validate_stale_route_counts():
        ok = False
    if not validate_public_file_registry_scope():
        ok = False
    if not validate_public_html_copy():
        ok = False
    if not validate_repair_log():
        ok = False
    if not validate_audit_inventory():
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
