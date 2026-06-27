#!/usr/bin/env python3
"""Validate Sprint 110 — Public Reference Navigation Backbone Consolidation v1."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    validate_public_surface,
)

AUDIT_DOC = "PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_V1.md"
REPAIR_DOC = "PUBLIC_REFERENCE_NAVIGATION_BACKBONE_REPAIR_LOG_V1.md"
STANDARD_DOC = "PUBLIC_NAVIGATION_BACKBONE_STANDARD_V1.md"
AUDIT_JSON = "data/public-reference-navigation-backbone-consolidation-v1.json"
AUDIT_SCHEMA = "data/public-reference-navigation-backbone-consolidation-v1.schema.json"
SPRINT_DOC = "SPRINT_110_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_V1.md"
HOMEPAGE = "index.html"
MAP_HUB = "system-map/index.html"

SYSTEM_MAP_BACKBONE_LINKS = [
    "/",
    "/system-map/route-groups/",
    "/system-map/human-review-paths/",
    "/system-map/ai-retrieval-paths/",
    "/system-map/boundary-layers/",
    "/reviewer-packet/public-surface-index/",
    "/executive-overview/public-reference-system/",
    "/strategic-review/public-reference-depth/",
    "/external-review/reviewer-map/",
]

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
    "due diligence room",
    "scorecard",
    "rating system",
    "dashboard",
    "graph tool",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

SOURCE_LOCS = [AUDIT_DOC, REPAIR_DOC, STANDARD_DOC, AUDIT_JSON, AUDIT_SCHEMA, SPRINT_DOC]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def route_to_file(path: str) -> str:
    p = path.strip("/")
    return "index.html" if not p else f"{p}/index.html"


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def text_has_unnegated_claim(text: str, claim: str) -> bool:
    lower = re.sub(r"\s+", " ", strip_tags(text)).lower()
    if claim not in lower:
        return False
    if re.search(r"not a [\w\s,\-/]*" + re.escape(claim) + r"s?\b", lower):
        return False
    if re.search(r"not an [\w\s,\-/]*" + re.escape(claim) + r"s?\b", lower):
        return False
    if re.search(r"not [\w\s,\-/]*" + re.escape(claim) + r"s?\b", lower):
        return False
    if re.search(r"without [\w\s,\-/]*" + re.escape(claim) + r"s?\b", lower):
        return False
    if any(
        marker in lower
        for marker in (
            "does not support",
            "what the map does not",
            "what this map does not",
            "what the backbone does not",
            "navigation backbone role",
        )
    ) and claim in lower:
        return False
    if claim == "dashboard" and re.search(r"detector[\s-]dashboard", lower):
        return False
    pos = 0
    while True:
        idx = lower.find(claim, pos)
        if idx < 0:
            return False
        if claim == "valuation" and idx > 0 and lower[idx - 1] == "e":
            pos = idx + len(claim)
            continue
        prefix = lower[max(0, idx - 120) : idx]
        if NEGATION_PATTERN.search(prefix + claim):
            pos = idx + len(claim)
            continue
        return True
        pos = idx + len(claim)
    return False


def line_has_unnegated_claim(line: str, claim: str) -> bool:
    return text_has_unnegated_claim(line, claim)


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
    if data.get("decision_ref") != "DEC-128":
        error("decision_ref must be DEC-128")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if data.get("total_repairs_made", 0) < 2:
        error("total_repairs_made must be at least 2")
        ok = False
    if data.get("navigation_backbone_snapshot_added") is not True:
        error("navigation_backbone_snapshot_added must be true")
        ok = False
    if data.get("system_map_navigation_backbone_section_added") is not True:
        error("system_map_navigation_backbone_section_added must be true")
        ok = False
    for key in (
        "visible_repairs_made",
        "route_count_integrity_checked",
        "file_existence_integrity_checked",
        "metadata_integrity_checked",
        "link_integrity_checked",
        "navigation_backbone_integrity_checked",
        "route_group_connectivity_checked",
        "page_end_navigation_checked",
        "ai_retrieval_navigation_checked",
        "boundary_integrity_checked",
        "dashboard_drift_checked",
        "graph_tool_drift_checked",
        "scorecard_drift_checked",
        "rating_system_drift_checked",
        "due_diligence_room_drift_checked",
        "pitch_deck_drift_checked",
        "sales_page_drift_checked",
        "private_data_room_drift_checked",
        "downloadable_report_drift_checked",
        "pricing_transaction_drift_checked",
        "validator_syntax_safety_checked",
        "stale_route_count_language_checked",
        "public_html_checked_only_for_current_forbidden_copy",
        "historical_governance_not_rewritten_for_current_copy_rules",
    ):
        if data.get(key) is not True:
            error(f"{key} must be true")
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
        "private_data_room_authorized",
        "downloadable_report_authorized",
        "pitch_deck_authorized",
        "sales_page_authorized",
        "scorecard_authorized",
        "rating_system_authorized",
        "dashboard_authorized",
        "graph_tool_authorized",
        "due_diligence_room_authorized",
    ):
        if data.get(flag) is not False:
            error(f"{flag} must be false")
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
    return ok


def validate_navigation_backbone_surfaces() -> bool:
    ok = True
    home = (ROOT / HOMEPAGE).read_text(encoding="utf-8")
    if "Navigation Backbone Snapshot" not in home:
        error("homepage must include Navigation Backbone Snapshot")
        ok = False
    if f"Current public route count: {PUBLIC_SITEMAP_URL_COUNT}" not in home:
        error(f"homepage must include Current public route count: {PUBLIC_SITEMAP_URL_COUNT}")
        ok = False
    if 'href="/system-map/"' not in home and 'href="/system-map/#' not in home:
        error("homepage must link to /system-map/")
        ok = False
    if 'href="/strategic-review/"' not in home and 'href="/strategic-review/#' not in home:
        error("homepage must link to /strategic-review/")
        ok = False
    map_hub = (ROOT / MAP_HUB).read_text(encoding="utf-8")
    if "Navigation Backbone" not in map_hub:
        error("/system-map/ must include Navigation Backbone")
        ok = False
    for path in SYSTEM_MAP_BACKBONE_LINKS:
        if f'href="{path}' not in map_hub and f"href='{path}" not in map_hub:
            error(f"/system-map/ must link to {path}")
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
        if len(re.findall(r"<h1\b", content, re.I)) != 1:
            error(f"{rel}: expected exactly one H1")
            ok = False
        for field in ('rel="canonical"', 'name="description"', "og:title", "og:description"):
            if field not in content.lower():
                error(f"{rel}: missing {field}")
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
    reg_paths = {f["path"] for f in files}
    route_files = {route_to_file(r["path"]) for r in load_json("data/route-registry.json").get("routes", [])}
    missing = sorted(route_files - reg_paths)
    if missing:
        error(f"public-file-registry missing route HTML files: {missing[:5]}")
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
        for claim in FORBIDDEN_CLAIMS:
            if text_has_unnegated_claim(content, claim):
                error(f"{rel}: forbidden claim {claim!r}")
                ok = False
    return ok


def validate_repair_log() -> bool:
    ok = True
    text = (ROOT / REPAIR_DOC).read_text(encoding="utf-8")
    for col in (
        "repair_id",
        "page_path",
        "issue_or_improvement_target",
        "repair_applied",
        "route_group_affected",
        "navigation_backbone_impact",
        "human_readability_impact",
        "ai_retrieval_impact",
        "non_verdict_impact",
        "non_transactional_impact",
        "validator_protection",
    ):
        if col not in text:
            error(f"repair log missing column {col}")
            ok = False
    if "NBB-001" not in text:
        error("repair log must include NBB-001")
        ok = False
    return ok


def validate_validator_syntax() -> bool:
    ok = True
    for path in sorted((ROOT / "validators").glob("validate*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            error(f"validator syntax error in {path.name}: {exc}")
            ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-128" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-128 missing")
        ok = False
    if "validate_public_reference_navigation_backbone_consolidation_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 110 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_BACKBONE_CONSOLIDATION_VALIDATION,
    ):
        error("publisher status must reflect Sprint 110 navigation backbone consolidation validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_navigation_backbone_consolidation_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0111" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0111 missing")
        ok = False
    if not any(
        g.get("gate_id") == "PUB-GATE-0104"
        for g in load_json("data/publisher-quality-gates.json").get("gates", [])
    ):
        error("PUB-GATE-0104 missing")
        ok = False
    if "Sprint 110 | COMPLETE | G110 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 110 row")
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
    if not validate_navigation_backbone_surfaces():
        ok = False
    if not validate_public_file_registry_scope():
        ok = False
    if not validate_route_files_and_metadata():
        ok = False
    if not validate_internal_links():
        ok = False
    if not validate_stale_route_counts():
        ok = False
    if not validate_public_html_copy():
        ok = False
    if not validate_repair_log():
        ok = False
    if not validate_validator_syntax():
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
