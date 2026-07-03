#!/usr/bin/env python3
"""Validate Sprint 132 — Public Release and Indexation Integrity Audit v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
)

AUDIT_MD = "PUBLIC_RELEASE_INDEXATION_INTEGRITY_AUDIT_V1.md"
SPRINT = "SPRINT_132_PUBLIC_RELEASE_INDEXATION_INTEGRITY_AUDIT_V1.md"
JSON_PATH = "data/public-release-indexation-integrity-audit-v1.json"
SCHEMA_PATH = "data/public-release-indexation-integrity-audit-v1.schema.json"
SPRINT129 = "PUBLIC_REFERENCE_VALUE_BOUNDARY_AUDIT_V1.md"
SPRINT130 = "PUBLIC_REFERENCE_NON_TRANSACTIONAL_REVENUE_BOUNDARY_AUDIT_V1.md"
SPRINT131 = "PUBLIC_REFERENCE_VALUE_INTEGRITY_CLOSURE_AUDIT_V1.md"

EXTERNAL_USE = [
    ("/reading-sequences/", "reading-sequences/index.html"),
    ("/retrieval-index/", "retrieval-index/index.html"),
    ("/citation-orientation/", "citation-orientation/index.html"),
    ("/source-use-orientation/", "source-use-orientation/index.html"),
]

CORE_PAGES = [
    "index.html",
    "system-map/index.html",
    "reading-sequences/index.html",
    "retrieval-index/index.html",
    "strategic-review/index.html",
]

PATCHED_PAGES = [
    "index.html",
    "system-map/index.html",
    "reading-sequences/index.html",
    "external-review/public-surface-checklist/index.html",
    "citation-orientation/index.html",
    "strategic-review/index.html",
]

REQUIRED_RECORD_FIELDS = [
    "release_record_id",
    "public_page_or_file",
    "record_type",
    "route_or_file_path",
    "expected_state",
    "actual_state",
    "status",
    "observed_issue",
    "repair_applied",
    "release_integrity_check",
    "indexation_check",
    "ai_agent_note",
]

REQUIRED_SCENARIO_FIELDS = [
    "scenario_id",
    "release_integrity_intent",
    "expected_pages_checked",
    "expected_safe_interpretation",
    "actual_interpretation",
    "supporting_routes_or_artifacts",
    "result",
    "observed_issue",
    "repair_applied",
    "release_integrity_check",
    "indexation_check",
    "boundary_check",
    "ai_agent_note",
]

DRIFT_FLAGS = [
    "route_count_drift_found",
    "stale_copy_found",
    "stale_phase_language_found",
    "stale_release_language_found",
    "sitemap_mismatch_found",
    "route_registry_mismatch_found",
    "public_file_registry_mismatch_found",
    "orphaned_public_page_found",
    "missing_public_page_found",
    "broken_internal_link_found",
    "canonical_defect_found",
    "metadata_defect_found",
    "og_defect_found",
    "robots_defect_found",
    "accidental_noindex_found",
    "accidental_public_exposure_found",
    "commercial_metadata_drift_found",
    "seo_spam_drift_found",
    "marketing_drift_found",
    "monetization_drift_found",
    "pricing_drift_found",
    "subscription_drift_found",
    "support_or_sponsorship_drift_found",
    "donation_drift_found",
    "paid_report_drift_found",
    "private_access_drift_found",
    "consulting_offer_drift_found",
    "service_funnel_drift_found",
    "lead_generation_drift_found",
    "sales_page_drift_found",
    "pitch_deck_drift_found",
    "acquisition_solicitation_drift_found",
    "buyer_solicitation_drift_found",
    "transaction_readiness_drift_found",
    "due_diligence_room_drift_found",
    "legal_or_financial_representation_drift_found",
    "investment_claim_drift_found",
    "authority_claim_drift_found",
    "verification_drift_found",
    "proof_drift_found",
    "detector_drift_found",
    "score_or_verdict_drift_found",
    "case_conclusion_drift_found",
    "governance_inflation_found",
]

STALE_ROUTE_COUNTS = [
    "88-route", "88 routes", "93-route", "93 routes", "99-route", "99 routes",
    "100-route", "100 routes", "101-route", "101 routes", "102-route", "102 routes",
    "103-route", "103 routes",
]

UNSAFE_TERMS = [
    "seo campaign",
    "launch campaign",
    "marketing funnel",
    "subscribe",
    "subscription page",
    "paid access",
    "paid report",
    "support us",
    "sponsor us",
    "donate now",
    "consulting offer",
    "contact sales",
    "contact to buy",
    "lead generation",
    "monetization page",
    "for sale",
    "buyer opportunity",
    "investment opportunity",
]

NEGATION_PATTERN = re.compile(
    r"(?:must not|does not|do not|not a|not an|no |without|forbidden|prohibited|is not|are not|cannot|not)\s+[\w\s\-/]{0,120}",
    re.IGNORECASE,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def route_to_file(path: str) -> str:
    p = path.strip("/")
    return "index.html" if not p else f"{p}/index.html"


def internal_route_set() -> set[str]:
    routes = load_json("data/route-registry.json").get("routes", [])
    return {(r.get("path", "/").rstrip("/") or "/") for r in routes}


def unnegated(text: str, term: str) -> bool:
    lower = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).lower()
    pos = 0
    while True:
        idx = lower.find(term, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 160):idx]
        if NEGATION_PATTERN.search(prefix + term):
            pos = idx + len(term)
            continue
        return True


def validate_artifacts() -> bool:
    ok = True
    for rel in (AUDIT_MD, SPRINT, JSON_PATH, SCHEMA_PATH, SPRINT129, SPRINT130, SPRINT131):
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            ok = False
    if not (ROOT / "robots.txt").is_file():
        error("robots.txt missing")
        ok = False
    return ok


def validate_audit_json() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    load_json(SCHEMA_PATH)
    expected = {
        "audit_only": True,
        "phase": "Phase 5",
        "phase_entry_audit": True,
        "production_route_added": False,
        "public_route_count_before": 104,
        "public_route_count_after": 104,
        "sitemap_url_count_expected": 104,
        "route_registry_count_expected": 104,
        "public_file_registry_unchanged": True,
        "route_registry_changed": False,
        "public_file_registry_changed": False,
        "sitemap_changed": False,
        "no_new_routes": True,
        "new_decision_created": False,
        "public_release_integrity_confirmed": True,
        "indexation_integrity_confirmed": True,
        "deployability_confirmed": True,
        "discoverability_confirmed": True,
        "crawler_readability_confirmed": True,
        "ai_agent_readability_confirmed": True,
        "human_navigation_integrity_confirmed": True,
        "sitemap_integrity_confirmed": True,
        "route_registry_integrity_confirmed": True,
        "public_file_registry_integrity_confirmed": True,
        "canonical_integrity_confirmed": True,
        "metadata_integrity_confirmed": True,
        "robots_integrity_confirmed": True,
        "internal_link_integrity_confirmed": True,
        "phase_2_support_discoverability_confirmed": True,
        "phase_3_support_discoverability_confirmed": True,
        "phase_4_support_discoverability_confirmed": True,
        "release_records_unsafe": 0,
    }
    for k, v in expected.items():
        if data.get(k) != v:
            error(f"{JSON_PATH}: {k} must be {v!r}")
            ok = False
    for flag in DRIFT_FLAGS:
        if data.get(flag) is not False:
            error(f"{JSON_PATH}: {flag} must be false")
            ok = False
    records = data.get("release_records", [])
    if len(records) < 40:
        error(f"{JSON_PATH}: must include at least 40 release records")
        ok = False
    if data.get("total_release_records") != len(records):
        error(f"{JSON_PATH}: total_release_records mismatch")
        ok = False
    safe = sum(1 for x in records if x.get("status") == "safe")
    repaired = sum(1 for x in records if x.get("status") == "repaired")
    if data.get("release_records_safe") != safe:
        error(f"{JSON_PATH}: release_records_safe mismatch")
        ok = False
    if data.get("release_records_repaired") != repaired:
        error(f"{JSON_PATH}: release_records_repaired mismatch")
        ok = False
    for rec in records:
        for field in REQUIRED_RECORD_FIELDS:
            if field not in rec:
                error(f"{rec.get('release_record_id', '?')}: missing field {field}")
                ok = False
    scenarios = data.get("walkthrough_scenarios", [])
    if len(scenarios) < 40:
        error(f"{JSON_PATH}: must include at least 40 scenarios")
        ok = False
    if data.get("total_scenarios") != len(scenarios):
        error(f"{JSON_PATH}: total_scenarios mismatch")
        ok = False
    passed = sum(1 for s in scenarios if s.get("result") == "pass")
    failed = sum(1 for s in scenarios if s.get("result") == "fail")
    if data.get("scenarios_passed") != passed or data.get("scenarios_failed") != failed:
        error(f"{JSON_PATH}: pass/fail counts mismatch")
        ok = False
    for sc in scenarios:
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in sc:
                error(f"{sc.get('scenario_id', '?')}: missing field {field}")
                ok = False
        if sc.get("result") not in ("pass", "fail"):
            error(f"{sc.get('scenario_id')}: invalid result")
            ok = False
        if sc.get("result") == "fail" and not (sc.get("repair_applied") or sc.get("deferred_reason")):
            error(f"{sc.get('scenario_id')}: failed scenario needs repair_applied or deferred_reason")
            ok = False
    return ok


def validate_no_expansion() -> bool:
    ok = True
    reg = load_json("data/route-registry.json").get("routes", [])
    if len(reg) != 104:
        error(f"route registry must have exactly 104 entries, found {len(reg)}")
        ok = False
    files = load_json("data/public-file-registry.json").get("public_files", [])
    if any(f.get("public_file_id") == "PUB-FILE-0105" for f in files):
        error("PUB-FILE-0105 must not exist after Sprint 132 audit-only sprint")
        ok = False
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = sitemap.findall("sm:url", ns) or sitemap.findall("url")
    if len(urls) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {len(urls)}")
        ok = False
    reg_paths = {(r.get("path", "/").rstrip("/") or "/") for r in reg}
    sitemap_paths = set()
    for u in urls:
        loc = u.find("sm:loc", ns)
        if loc is None:
            loc = u.find("loc")
        if loc is None or not loc.text:
            error("sitemap URL missing loc")
            ok = False
            continue
        path = loc.text.replace("https://hoax.ai", "").rstrip("/") or "/"
        sitemap_paths.add(path)
        rel = route_to_file(path)
        if not (ROOT / rel).is_file():
            error(f"sitemap URL {path} missing local file {rel}")
            ok = False
    if reg_paths != sitemap_paths:
        missing = sorted(reg_paths - sitemap_paths)
        extra = sorted(sitemap_paths - reg_paths)
        if missing:
            error(f"route registry entries missing from sitemap: {missing[:5]}")
            ok = False
        if extra:
            error(f"sitemap URLs not in route registry: {extra[:5]}")
            ok = False
    for route, rel in EXTERNAL_USE:
        if not (ROOT / rel).is_file():
            error(f"{rel} missing for {route}")
            ok = False
    return ok


def validate_robots_and_noindex() -> bool:
    ok = True
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8").lower()
    if "disallow: /" in robots.replace(" ", ""):
        error("robots.txt must not disallow entire public surface")
        ok = False
    if "sitemap:" not in robots:
        error("robots.txt must reference sitemap")
        ok = False
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        lower = (ROOT / rel).read_text(encoding="utf-8").lower()
        if 'content="noindex' in lower or "content='noindex" in lower:
            error(f"{rel}: accidental noindex on public page")
            ok = False
    return ok


def validate_core_metadata() -> bool:
    ok = True
    for rel in CORE_PAGES:
        content = (ROOT / rel).read_text(encoding="utf-8")
        lower = content.lower()
        if 'rel="canonical"' not in lower:
            error(f"{rel}: missing canonical")
            ok = False
        if 'name="description"' not in lower:
            error(f"{rel}: missing meta description")
            ok = False
        if "og:title" not in lower:
            error(f"{rel}: missing og:title")
            ok = False
        if "og:description" not in lower:
            error(f"{rel}: missing og:description")
            ok = False
        if "og:url" not in lower:
            error(f"{rel}: missing og:url")
            ok = False
        if len(re.findall(r"<h1\b", content, re.I)) != 1:
            error(f"{rel}: expected exactly one H1")
            ok = False
    home = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    if "current public route count: 104" not in home:
        error("homepage missing 104-route count in release snapshot")
        ok = False
    smap = (ROOT / "system-map/index.html").read_text(encoding="utf-8").lower()
    if "current public route count: 104" not in smap:
        error("system-map missing 104-route count")
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


def validate_release_hardening() -> bool:
    ok = True
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    smap = (ROOT / "system-map/index.html").read_text(encoding="utf-8")
    rs = (ROOT / "reading-sequences/index.html").read_text(encoding="utf-8")
    checklist = (ROOT / "external-review/public-surface-checklist/index.html").read_text(encoding="utf-8")
    cit = (ROOT / "citation-orientation/index.html").read_text(encoding="utf-8")
    sri = (ROOT / "strategic-review/index.html").read_text(encoding="utf-8")

    if 'id="public-release-indexation-integrity"' not in home:
        error("homepage missing public-release-indexation-integrity hardening")
        ok = False
    if "public-release-indexation-integrity" not in smap:
        error("system-map missing release indexation cross-link")
        ok = False
    if "public-release-indexation-integrity" not in rs:
        error("reading-sequences missing release indexation cross-link")
        ok = False
    if "public-release-indexation-integrity" not in checklist:
        error("public-surface-checklist missing release indexation cross-link")
        ok = False
    if "public-release-indexation-integrity" not in cit:
        error("citation-orientation missing release indexation cross-link")
        ok = False
    if "public-release-indexation-integrity" not in sri:
        error("strategic-review missing release indexation cross-link")
        ok = False
    if "phase-4-value-integrity-closure" not in home:
        error("homepage missing Phase 4 value integrity closure link")
        ok = False

    for rel in PATCHED_PAGES + [p for _, p in EXTERNAL_USE]:
        html = (ROOT / rel).read_text(encoding="utf-8").lower()
        for bad in ("<script", "<form", "<input", "<textarea", "<select"):
            if bad in html:
                error(f"{rel}: prohibited element {bad}")
                ok = False
    return ok


def validate_terms_and_decision() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    if data.get("new_decision_created"):
        error("new_decision_created must be false unless DEC governs visible fix")
        ok = False
    sprint_md = (ROOT / SPRINT).read_text(encoding="utf-8")
    for term in UNSAFE_TERMS:
        if unnegated(sprint_md, term):
            error(f"{SPRINT}: unnegated unsafe term {term!r}")
            ok = False
    return ok


def validate_governance_wiring() -> bool:
    ok = True
    if not any(c.get("claim_id") == "CLAIM-0133" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0133 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0126" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0126 missing")
        ok = False
    val_all = (ROOT / "validators/validate_all.py").read_text(encoding="utf-8")
    if "validate_public_release_indexation_integrity_audit_v1.py" not in val_all:
        error("validate_all.py missing Sprint 132 validator wiring")
        ok = False
    return ok


def main() -> int:
    checks = [
        validate_artifacts(),
        validate_audit_json(),
        validate_no_expansion(),
        validate_robots_and_noindex(),
        validate_core_metadata(),
        validate_stale_route_counts(),
        validate_internal_links(),
        validate_release_hardening(),
        validate_terms_and_decision(),
        validate_governance_wiring(),
    ]
    if all(checks):
        print("PASS: Public Release and Indexation Integrity Audit v1")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
