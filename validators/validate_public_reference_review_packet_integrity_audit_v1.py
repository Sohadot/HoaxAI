#!/usr/bin/env python3
"""Validate Sprint 103 — Public Reference Review Packet Integrity Audit v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    validate_public_surface,
)

AUDIT_DOC = "PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_V1.md"
REPAIR_DOC = "PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_REPAIR_LOG_V1.md"
STANDARD_DOC = "PUBLIC_REVIEW_PACKET_INTEGRITY_STANDARD_V1.md"
AUDIT_JSON = "data/public-reference-review-packet-integrity-audit-v1.json"
AUDIT_SCHEMA = "data/public-reference-review-packet-integrity-audit-v1.schema.json"
SPRINT_DOC = "SPRINT_103_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_V1.md"
PACKET_HUB = "reviewer-packet/index.html"
EXPECTED = 68

REVIEWER_PACKET_PAGES = [
    "reviewer-packet/index.html",
    "reviewer-packet/review-sequence/index.html",
    "reviewer-packet/public-surface-index/index.html",
    "reviewer-packet/citation-and-retrieval-map/index.html",
    "reviewer-packet/boundary-and-readiness-summary/index.html",
]

REVIEWER_PACKET_PATHS = [
    "/reviewer-packet/",
    "/reviewer-packet/review-sequence/",
    "/reviewer-packet/public-surface-index/",
    "/reviewer-packet/citation-and-retrieval-map/",
    "/reviewer-packet/boundary-and-readiness-summary/",
]

REQUIRED_PACKET_SECTIONS = [
    "Reference summary",
    "Packet purpose",
    "Review path",
    "What this page supports",
    "What this page does not claim",
    "Reference Answer",
    "Source Confidence",
    "Cite This Reference",
    "Retrieval Capsule",
    "Boundary reminder",
    "Non-transactional review boundary",
]

STALE_ROUTE_COUNTS = [
    "63-route",
    "58-route",
    "63 urls",
    "58 urls",
    "29-route",
    "41-route",
    "47-route",
    "52-route",
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
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

SOURCE_LOCS = [AUDIT_DOC, REPAIR_DOC, STANDARD_DOC, AUDIT_JSON, AUDIT_SCHEMA, SPRINT_DOC]

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
    if data.get("decision_ref") != "DEC-121":
        error("decision_ref must be DEC-121")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if data.get("total_repairs_made", 0) < 1:
        error("total_repairs_made must be at least 1")
        ok = False
    if data.get("reviewer_packet_integrity_snapshot_added") is not True:
        error("reviewer_packet_integrity_snapshot_added must be true")
        ok = False
    for key in (
        "reviewer_packet_snapshot_counts_as_visible_repair",
        "visible_repairs_made",
        "route_count_integrity_checked",
        "file_existence_integrity_checked",
        "metadata_integrity_checked",
        "link_integrity_checked",
        "reviewer_packet_component_integrity_checked",
        "boundary_integrity_checked",
        "private_data_room_drift_checked",
        "downloadable_report_drift_checked",
        "pricing_transaction_drift_checked",
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
    ):
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    sitemap_count = len([u for u in ET.parse(ROOT / "sitemap.xml").getroot().iter() if u.tag.endswith("loc")])
    registry_count = len(load_json("data/route-registry.json").get("routes", []))
    if sitemap_count != EXPECTED:
        error(f"sitemap must have {EXPECTED} URLs, found {sitemap_count}")
        ok = False
    if registry_count != EXPECTED:
        error(f"route registry must have {EXPECTED} entries, found {registry_count}")
        ok = False
    if sitemap_count != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap count {sitemap_count} != PUBLIC_SITEMAP_URL_COUNT {PUBLIC_SITEMAP_URL_COUNT}")
        ok = False
    return ok


def validate_packet_hub_snapshot() -> bool:
    ok = True
    content = (ROOT / PACKET_HUB).read_text(encoding="utf-8")
    if "Reviewer Packet Integrity Snapshot" not in content:
        error("/reviewer-packet/ must include Reviewer Packet Integrity Snapshot")
        ok = False
    if "Current public route count: 68" not in content:
        error("/reviewer-packet/ must include Current public route count: 68")
        ok = False
    if "Reviewer packet route count: 5" not in content:
        error("/reviewer-packet/ must include Reviewer packet route count: 5")
        ok = False
    for path in REVIEWER_PACKET_PATHS:
        if f'href="{path}' not in content and f"href='{path}" not in content:
            error(f"/reviewer-packet/ must link to {path}")
            ok = False
    return ok


def validate_reviewer_packet_page(rel: str) -> bool:
    ok = True
    fp = ROOT / rel
    if not fp.is_file():
        error(f"missing {rel}")
        return False
    content = fp.read_text(encoding="utf-8")
    if len(re.findall(r"<h1\b", content, re.I)) != 1:
        error(f"{rel}: expected exactly one H1")
        ok = False
    for field in ('rel="canonical"', 'name="description"', "og:title", "og:description"):
        if field not in content.lower():
            error(f"{rel}: missing {field}")
            ok = False
    for section in REQUIRED_PACKET_SECTIONS:
        if section not in content:
            error(f"{rel}: missing section {section!r}")
            ok = False
    if 'href="/reviewer-packet/"' not in content and 'href="/reviewer-packet/#' not in content:
        error(f"{rel}: must link to /reviewer-packet/")
        ok = False
    strategic_external = sum(
        1
        for p in ("/entry-points/", "/narrative/", "/acquisition-readiness/", "/external-review/")
        if p in content
    )
    if strategic_external < 3:
        error(f"{rel}: must link to at least 3 strategic or external-review routes")
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
    sibling_links = sum(1 for p in REVIEWER_PACKET_PATHS if f'href="{p}' in content or f"href='{p}" in content)
    if sibling_links < 2:
        error(f"{rel}: must link to at least 2 sibling reviewer-packet routes")
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
            for line in content.splitlines():
                if line_has_unnegated_claim(line, claim):
                    error(f"{rel}: forbidden claim {claim!r}")
                    ok = False
                    break
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
        "review_packet_integrity_impact",
        "human_readability_impact",
        "ai_retrieval_impact",
        "non_verdict_impact",
        "non_transactional_impact",
        "validator_protection",
    ):
        if col not in text:
            error(f"repair log missing column {col}")
            ok = False
    if "RPIA-001" not in text:
        error("repair log must include RPIA-001")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-121" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-121 missing")
        ok = False
    if "validate_public_reference_review_packet_integrity_audit_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 103 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    ):
        error("publisher status must reflect Sprint 103 review packet integrity audit validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_review_packet_integrity_audit_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0104" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0104 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0097" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0097 missing")
        ok = False
    if "Sprint 103 | COMPLETE | G103 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 103 row")
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
    if not validate_packet_hub_snapshot():
        ok = False
    if not validate_public_file_registry_scope():
        ok = False
    for rel in REVIEWER_PACKET_PAGES:
        if not validate_reviewer_packet_page(rel):
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
