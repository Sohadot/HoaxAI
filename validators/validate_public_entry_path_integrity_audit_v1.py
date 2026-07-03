#!/usr/bin/env python3
"""Validate Sprint 133 — Public Entry Path Integrity Audit v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import ALLOWED_PUBLIC_HTML, PUBLIC_SITEMAP_URL_COUNT  # noqa: E402

AUDIT_MD = "PUBLIC_ENTRY_PATH_INTEGRITY_AUDIT_V1.md"
SPRINT = "SPRINT_133_PUBLIC_ENTRY_PATH_INTEGRITY_AUDIT_V1.md"
JSON_PATH = "data/public-entry-path-integrity-audit-v1.json"
SCHEMA_PATH = "data/public-entry-path-integrity-audit-v1.schema.json"
SPRINT132_AUDIT = "PUBLIC_RELEASE_INDEXATION_INTEGRITY_AUDIT_V1.md"

EXTERNAL_USE = [
    ("/reading-sequences/", "reading-sequences/index.html"),
    ("/retrieval-index/", "retrieval-index/index.html"),
    ("/citation-orientation/", "citation-orientation/index.html"),
    ("/source-use-orientation/", "source-use-orientation/index.html"),
]

PHASE3_ROUTES = [
    "strategic-review/index.html",
    "strategic-review/retrieval-and-citation/index.html",
    "strategic-review/public-reference-depth/index.html",
    "reviewer-packet/index.html",
    "reviewer-packet/citation-and-retrieval-map/index.html",
    "acquisition-readiness/index.html",
    "acquisition-readiness/governance-traceability/index.html",
]

PATCHED_PAGES = [
    "index.html",
    "system-map/index.html",
    "reading-sequences/index.html",
    "retrieval-index/index.html",
    "citation-orientation/index.html",
    "source-use-orientation/index.html",
    "strategic-review/index.html",
    "entry-points/index.html",
    "reviewer-packet/index.html",
    "reviewer-packet/boundary-and-readiness-summary/index.html",
    "acquisition-readiness/index.html",
    "external-review/public-surface-checklist/index.html",
    "route-groups/review-and-overview-layers/index.html",
]

REQUIRED_RECORD_FIELDS = [
    "entry_path_record_id",
    "public_page",
    "entry_path_type",
    "route_or_file_path",
    "expected_entry_role",
    "actual_entry_role",
    "expected_next_paths",
    "actual_next_paths",
    "status",
    "observed_issue",
    "repair_applied",
    "entry_integrity_check",
    "boundary_check",
    "ai_agent_note",
]

REQUIRED_SCENARIO_FIELDS = [
    "scenario_id",
    "entry_path_intent",
    "expected_pages_checked",
    "expected_safe_interpretation",
    "actual_interpretation",
    "supporting_routes_or_artifacts",
    "result",
    "observed_issue",
    "repair_applied",
    "entry_integrity_check",
    "boundary_check",
    "ai_agent_note",
]

DRIFT_FLAGS = [
    "route_count_drift_found",
    "stale_copy_found",
    "stale_phase_language_found",
    "orphaned_entry_surface_found",
    "broken_internal_link_found",
    "role_confusion_found",
    "entry_path_ambiguity_found",
    "workflow_drift_found",
    "funnel_drift_found",
    "onboarding_drift_found",
    "tool_drift_found",
    "dashboard_drift_found",
    "product_suite_drift_found",
    "service_drift_found",
    "consulting_offer_drift_found",
    "lead_generation_drift_found",
    "sales_page_drift_found",
    "commercial_conversion_drift_found",
    "monetization_drift_found",
    "pricing_drift_found",
    "subscription_drift_found",
    "support_or_sponsorship_drift_found",
    "donation_drift_found",
    "paid_report_drift_found",
    "private_access_drift_found",
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
    "88-route",
    "88 routes",
    "100-route",
    "100 routes",
    "101-route",
    "101 routes",
    "102-route",
    "102 routes",
    "103-route",
    "103 routes",
]

UNSAFE_TERMS = [
    "guided workflow",
    "diagnostic journey",
    "user journey",
    "onboarding flow",
    "service path",
    "product suite",
    "search product",
    "citation generator",
    "verification tool",
    "detection service",
    "paid access",
    "paid report",
    "support us",
    "sponsor us",
    "donate now",
    "consulting offer",
    "book a call",
    "contact sales",
    "contact to buy",
    "lead generation",
    "for sale",
    "buyer opportunity",
    "investment opportunity",
    "transaction-ready",
    "official certification",
    "guaranteed authority",
]

NEGATION_PATTERN = re.compile(
    r"(?:must not|does not|do not|not a|not an|no |without|forbidden|prohibited|is not|are not|cannot|not)\s+[\w\s\-/]{0,260}",
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
        prefix = lower[max(0, idx - 320):idx]
        if NEGATION_PATTERN.search(prefix + term):
            pos = idx + len(term)
            continue
        return True


def validate_artifacts() -> bool:
    ok = True
    for rel in (AUDIT_MD, SPRINT, JSON_PATH, SCHEMA_PATH, SPRINT132_AUDIT):
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            ok = False
    return ok


def validate_audit_json() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    load_json(SCHEMA_PATH)
    expected = {
        "audit_only": True,
        "phase": "Phase 5",
        "phase_entry_path_audit": True,
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
        "public_entry_path_integrity_confirmed": True,
        "homepage_entry_integrity_confirmed": True,
        "system_map_entry_integrity_confirmed": True,
        "phase_2_entry_integrity_confirmed": True,
        "phase_3_entry_integrity_confirmed": True,
        "phase_4_entry_integrity_confirmed": True,
        "phase_5_entry_integrity_confirmed": True,
        "ai_agent_entry_interpretation_confirmed": True,
        "human_reader_entry_interpretation_confirmed": True,
        "crawler_entry_discoverability_confirmed": True,
        "route_group_entry_integrity_confirmed": True,
        "audience_path_entry_integrity_confirmed": True,
        "internal_navigation_integrity_confirmed": True,
        "related_page_entry_integrity_confirmed": True,
        "metadata_entry_integrity_confirmed": True,
        "entry_path_records_unsafe": 0,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            error(f"{JSON_PATH}: {key} must be {value!r}")
            ok = False
    for flag in DRIFT_FLAGS:
        if data.get(flag) is not False:
            error(f"{JSON_PATH}: {flag} must be false")
            ok = False

    records = data.get("entry_path_records", [])
    if len(records) < 40:
        error(f"{JSON_PATH}: must include at least 40 entry path records")
        ok = False
    if data.get("total_entry_path_records") != len(records):
        error(f"{JSON_PATH}: total_entry_path_records mismatch")
        ok = False
    safe = sum(1 for record in records if record.get("status") == "safe")
    repaired = sum(1 for record in records if record.get("status") == "repaired")
    if data.get("entry_path_records_safe") != safe:
        error(f"{JSON_PATH}: entry_path_records_safe mismatch")
        ok = False
    if data.get("entry_path_records_repaired") != repaired:
        error(f"{JSON_PATH}: entry_path_records_repaired mismatch")
        ok = False
    for record in records:
        for field in REQUIRED_RECORD_FIELDS:
            if field not in record:
                error(f"{record.get('entry_path_record_id', '?')}: missing field {field}")
                ok = False

    scenarios = data.get("walkthrough_scenarios", [])
    if len(scenarios) < 42:
        error(f"{JSON_PATH}: must include at least 42 scenarios")
        ok = False
    if data.get("total_scenarios") != len(scenarios):
        error(f"{JSON_PATH}: total_scenarios mismatch")
        ok = False
    passed = sum(1 for scenario in scenarios if scenario.get("result") == "pass")
    failed = sum(1 for scenario in scenarios if scenario.get("result") == "fail")
    if data.get("scenarios_passed") != passed or data.get("scenarios_failed") != failed:
        error(f"{JSON_PATH}: pass/fail counts mismatch")
        ok = False
    for scenario in scenarios:
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in scenario:
                error(f"{scenario.get('scenario_id', '?')}: missing field {field}")
                ok = False
        if scenario.get("result") not in ("pass", "fail"):
            error(f"{scenario.get('scenario_id')}: invalid result")
            ok = False
        if scenario.get("result") == "fail" and not (scenario.get("repair_applied") or scenario.get("deferred_reason")):
            error(f"{scenario.get('scenario_id')}: failed scenario needs repair_applied or deferred_reason")
            ok = False
    return ok


def validate_no_expansion() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != 104:
        error(f"route registry must have exactly 104 entries, found {len(routes)}")
        ok = False
    public_files = load_json("data/public-file-registry.json").get("public_files", [])
    if any(file.get("public_file_id") == "PUB-FILE-0105" for file in public_files):
        error("PUB-FILE-0105 must not exist after Sprint 133 audit-only sprint")
        ok = False
    route_files = {route_to_file(route["path"]) for route in routes}
    registered_files = {file.get("path") for file in public_files}
    if route_files - registered_files:
        error(f"public-file-registry missing route files: {sorted(route_files - registered_files)[:5]}")
        ok = False

    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = sitemap.findall("sm:url", ns) or sitemap.findall("url")
    if len(urls) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {len(urls)}")
        ok = False
    return ok


def validate_entry_pages() -> bool:
    ok = True
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    system_map = (ROOT / "system-map/index.html").read_text(encoding="utf-8")
    if "/system-map/" not in home:
        error("homepage must link to system map")
        ok = False
    if 'id="public-entry-path-integrity"' not in home:
        error("homepage missing public-entry-path-integrity anchor")
        ok = False
    if "public-entry-path-integrity" not in system_map:
        error("system map missing public entry path integrity link")
        ok = False
    for rel in (
        "route-groups/public-utilities/index.html",
        "audience-paths/index.html",
        "strategic-review/index.html",
        "reviewer-packet/index.html",
        "acquisition-readiness/index.html",
    ):
        if rel.replace("/index.html", "/") and not (ROOT / rel).is_file():
            error(f"entry surface missing: {rel}")
            ok = False
    for _, rel in EXTERNAL_USE:
        if not (ROOT / rel).is_file():
            error(f"Phase 2 external-use route missing: {rel}")
            ok = False
    for rel in PHASE3_ROUTES:
        if not (ROOT / rel).is_file():
            error(f"Phase 3 strategic/reviewer route missing: {rel}")
            ok = False
    if "phase-4-value-integrity-closure" not in home or "phase-4-value-integrity-closure" not in system_map:
        error("Phase 4 value-integrity closure must remain discoverable")
        ok = False
    if "public-release-indexation-integrity" not in home or "public-release-indexation-integrity" not in system_map:
        error("Phase 5 release/indexation integrity must remain discoverable")
        ok = False
    return ok


def validate_internal_links() -> bool:
    ok = True
    routes = internal_route_set()
    audited = set(PATCHED_PAGES + [rel for _, rel in EXTERNAL_USE] + PHASE3_ROUTES)
    for rel in sorted(audited):
        content = (ROOT / rel).read_text(encoding="utf-8")
        for match in re.finditer(r'href="(/[^"]*)"', content):
            href = match.group(1)
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


def validate_entry_hardening() -> bool:
    ok = True
    checks = {
        "index.html": "public-entry-path-integrity",
        "system-map/index.html": "public-entry-path-integrity",
        "reading-sequences/index.html": "public-entry-path-integrity",
        "retrieval-index/index.html": "public-entry-path-integrity",
        "citation-orientation/index.html": "public-entry-path-integrity",
        "source-use-orientation/index.html": "public-entry-path-integrity",
        "strategic-review/index.html": "public-entry-path-integrity",
        "external-review/public-surface-checklist/index.html": "public-entry-path-integrity",
    }
    for rel, needle in checks.items():
        if needle not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel}: missing entry path hardening needle {needle}")
            ok = False
    if "onboarding material" in (ROOT / "entry-points/index.html").read_text(encoding="utf-8"):
        error("entry-points hub still contains onboarding material wording")
        ok = False
    if "reviewer onboarding" in (ROOT / "reviewer-packet/index.html").read_text(encoding="utf-8"):
        error("reviewer packet still contains reviewer onboarding wording")
        ok = False
    if "Onboarding strategic reviewers" in (ROOT / "acquisition-readiness/index.html").read_text(encoding="utf-8"):
        error("acquisition-readiness still contains onboarding strategic reviewers wording")
        ok = False
    if "onboarding third-party readers" in (ROOT / "route-groups/review-and-overview-layers/index.html").read_text(encoding="utf-8"):
        error("review route group still contains onboarding third-party readers wording")
        ok = False
    for rel in PATCHED_PAGES:
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
    text = (ROOT / SPRINT).read_text(encoding="utf-8")
    for rel in PATCHED_PAGES:
        text += "\n" + (ROOT / rel).read_text(encoding="utf-8")
    for term in UNSAFE_TERMS:
        if unnegated(text, term):
            error(f"unnegated unsafe term {term!r}")
            ok = False
    return ok


def validate_governance_wiring() -> bool:
    ok = True
    if not any(claim.get("claim_id") == "CLAIM-0134" for claim in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0134 missing")
        ok = False
    if not any(gate.get("gate_id") == "PUB-GATE-0127" for gate in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0127 missing")
        ok = False
    if "validate_public_entry_path_integrity_audit_v1.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py missing Sprint 133 validator wiring")
        ok = False
    return ok


def main() -> int:
    checks = [
        validate_artifacts(),
        validate_audit_json(),
        validate_no_expansion(),
        validate_entry_pages(),
        validate_internal_links(),
        validate_stale_route_counts(),
        validate_entry_hardening(),
        validate_terms_and_decision(),
        validate_governance_wiring(),
    ]
    if all(checks):
        print("PASS: Public Entry Path Integrity Audit v1")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
