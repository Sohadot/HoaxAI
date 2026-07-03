#!/usr/bin/env python3
"""Validate Sprint 135 — Public Reference Release Candidate Integrity Audit v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import ALLOWED_PUBLIC_HTML, PUBLIC_SITEMAP_URL_COUNT  # noqa: E402

AUDIT_MD = "PUBLIC_REFERENCE_RELEASE_CANDIDATE_INTEGRITY_AUDIT_V1.md"
SPRINT = "SPRINT_135_PUBLIC_REFERENCE_RELEASE_CANDIDATE_INTEGRITY_AUDIT_V1.md"
JSON_PATH = "data/public-reference-release-candidate-integrity-audit-v1.json"
SCHEMA_PATH = "data/public-reference-release-candidate-integrity-audit-v1.schema.json"
SPRINT134_AUDIT = "PUBLIC_DISCOVERY_INTEGRITY_CLOSURE_AUDIT_V1.md"
SPRINT134_JSON = "data/public-discovery-integrity-closure-audit-v1.json"
SPRINT134_VALIDATOR = "validators/validate_public_discovery_integrity_closure_audit_v1.py"

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
    "reviewer-packet/public-surface-index/index.html",
    "acquisition-readiness/index.html",
    "acquisition-readiness/governance-traceability/index.html",
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
    "strategic-review/index.html",
    "reviewer-packet/index.html",
    "acquisition-readiness/index.html",
    "external-review/public-surface-checklist/index.html",
    "route-groups/review-and-overview-layers/index.html",
]

REQUIRED_RECORD_FIELDS = [
    "release_candidate_record_id",
    "public_page_or_file",
    "record_type",
    "route_or_file_path",
    "expected_release_candidate_role",
    "actual_release_candidate_role",
    "expected_supporting_paths",
    "actual_supporting_paths",
    "status",
    "observed_issue",
    "repair_applied",
    "release_candidate_integrity_check",
    "cross_phase_check",
    "boundary_check",
    "ai_agent_note",
]

REQUIRED_SCENARIO_FIELDS = [
    "scenario_id",
    "release_candidate_intent",
    "expected_pages_checked",
    "expected_safe_interpretation",
    "actual_interpretation",
    "supporting_routes_or_artifacts",
    "result",
    "observed_issue",
    "repair_applied",
    "release_candidate_integrity_check",
    "cross_phase_check",
    "boundary_check",
    "ai_agent_note",
]

CONFIRMATION_FLAGS = [
    "release_candidate_integrity_confirmed",
    "system_coherence_confirmed",
    "cross_phase_integrity_confirmed",
    "public_reference_foundation_confirmed",
    "external_use_discipline_confirmed",
    "strategic_review_integrity_confirmed",
    "value_integrity_confirmed",
    "public_discovery_integrity_confirmed",
    "indexation_integrity_confirmed",
    "entry_path_integrity_confirmed",
    "discoverability_confirmed",
    "navigability_confirmed",
    "crawler_readability_confirmed",
    "ai_agent_readability_confirmed",
    "human_reader_interpretation_confirmed",
    "sitemap_integrity_confirmed",
    "route_registry_integrity_confirmed",
    "public_file_registry_integrity_confirmed",
    "canonical_integrity_confirmed",
    "metadata_integrity_confirmed",
    "robots_integrity_confirmed",
    "internal_link_integrity_confirmed",
]

DRIFT_FLAGS = [
    "route_count_drift_found",
    "stale_copy_found",
    "stale_phase_language_found",
    "stale_release_language_found",
    "stale_discovery_language_found",
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
    "role_confusion_found",
    "cross_phase_conflict_found",
    "release_candidate_ambiguity_found",
    "seo_spam_drift_found",
    "marketing_drift_found",
    "launch_campaign_drift_found",
    "workflow_drift_found",
    "funnel_drift_found",
    "onboarding_drift_found",
    "tool_drift_found",
    "dashboard_drift_found",
    "product_suite_drift_found",
    "service_drift_found",
    "commercial_conversion_drift_found",
    "monetization_drift_found",
    "pricing_drift_found",
    "subscription_drift_found",
    "support_or_sponsorship_drift_found",
    "donation_drift_found",
    "paid_report_drift_found",
    "private_access_drift_found",
    "consulting_offer_drift_found",
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
    "audit_as_certification_drift_found",
    "source_as_proof_drift_found",
    "governance_inflation_found",
]

NON_FLAGS = [
    "non_release_page",
    "non_launch_page",
    "non_marketing_surface",
    "non_seo_spam_surface",
    "non_workflow_surface",
    "non_funnel_surface",
    "non_onboarding_surface",
    "non_tool_surface",
    "non_dashboard_surface",
    "non_product_suite_surface",
    "non_service_surface",
    "non_commercial_surface",
    "non_monetization_surface",
    "non_pricing",
    "non_subscription",
    "non_support_surface",
    "non_sponsorship_surface",
    "non_donation_surface",
    "non_paid_report",
    "non_private_access",
    "non_consulting_offer",
    "non_lead_generation",
    "non_sales_surface",
    "non_pitch_deck",
    "non_acquisition_solicitation",
    "non_buyer_solicitation",
    "non_transaction_surface",
    "non_due_diligence_room",
    "non_legal_representation",
    "non_financial_representation",
    "non_investment_claim",
    "non_authority_claim",
    "non_verification_claim",
    "non_proof",
    "non_detector",
    "non_scoring",
    "non_verdict",
    "non_case_conclusion",
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
    "official release",
    "press release",
    "launch page",
    "launch campaign",
    "marketing funnel",
    "official certification",
    "verified authority",
    "proof engine",
    "detector behavior",
    "detector output",
    "detector product",
    "detection service",
    "verification tool",
    "score system",
    "sales proof",
    "value proof",
    "guided workflow",
    "user journey",
    "onboarding flow",
    "service path",
    "product suite",
    "search product",
    "citation generator",
    "paid access",
    "paid report",
    "consulting offer",
    "book a call",
    "contact sales",
    "contact to buy",
    "lead generation",
    "for sale",
    "buyer opportunity",
    "investment opportunity",
    "transaction-ready",
]

NEGATION_PATTERN = re.compile(
    r"(?:must not|does not|do not|did not|not a|not an|no|without|rather than|forbidden|prohibited|is not|are not|cannot|not|replaced)\s+[\w\s\-/,.]{0,900}",
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
    return {(route.get("path", "/").rstrip("/") or "/") for route in routes}


def unnegated(text: str, term: str) -> bool:
    lower = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).lower()
    pos = 0
    while True:
        idx = lower.find(term, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 1000):idx]
        if NEGATION_PATTERN.search(prefix + term):
            pos = idx + len(term)
            continue
        return True


def validate_artifacts() -> bool:
    ok = True
    for rel in (AUDIT_MD, SPRINT, JSON_PATH, SCHEMA_PATH, SPRINT134_AUDIT, SPRINT134_JSON, SPRINT134_VALIDATOR, "robots.txt"):
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
        "release_candidate_audit": True,
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
        "release_candidate_records_unsafe": 0,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            error(f"{JSON_PATH}: {key} must be {value!r}")
            ok = False
    for flag in CONFIRMATION_FLAGS + NON_FLAGS:
        if data.get(flag) is not True:
            error(f"{JSON_PATH}: {flag} must be true")
            ok = False
    for flag in DRIFT_FLAGS:
        if data.get(flag) is not False:
            error(f"{JSON_PATH}: {flag} must be false")
            ok = False

    phases = data.get("phases_checked", {})
    for phase in [
        "Phase 1 public reference foundation",
        "Phase 2 external-use discipline",
        "Phase 3 strategic-review integrity",
        "Phase 4 value integrity",
        "Phase 5 public discovery integrity",
    ]:
        if phases.get(phase) is not True:
            error(f"{JSON_PATH}: phases_checked.{phase} must be true")
            ok = False

    records = data.get("release_candidate_records", [])
    if len(records) < 55:
        error(f"{JSON_PATH}: must include at least 55 release-candidate records")
        ok = False
    if data.get("total_release_candidate_records") != len(records):
        error(f"{JSON_PATH}: total_release_candidate_records mismatch")
        ok = False
    safe = sum(1 for record in records if record.get("status") == "safe")
    repaired = sum(1 for record in records if record.get("status") == "repaired")
    if data.get("release_candidate_records_safe") != safe:
        error(f"{JSON_PATH}: release_candidate_records_safe mismatch")
        ok = False
    if data.get("release_candidate_records_repaired") != repaired:
        error(f"{JSON_PATH}: release_candidate_records_repaired mismatch")
        ok = False
    for record in records:
        for field in REQUIRED_RECORD_FIELDS:
            if field not in record:
                error(f"{record.get('release_candidate_record_id', '?')}: missing field {field}")
                ok = False
        path = record.get("route_or_file_path", "")
        if path and not (ROOT / path).exists():
            error(f"{record.get('release_candidate_record_id')}: route_or_file_path missing: {path}")
            ok = False

    scenarios = data.get("walkthrough_scenarios", [])
    if len(scenarios) < 55:
        error(f"{JSON_PATH}: must include at least 55 scenarios")
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
        error("PUB-FILE-0105 must not exist after Sprint 135 audit-only sprint")
        ok = False
    route_files = {route_to_file(route["path"]) for route in routes}
    if route_files != set(ALLOWED_PUBLIC_HTML):
        error("public HTML route set must match route registry and sitemap surface")
        ok = False
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
    registry_paths = {(route.get("path", "/").rstrip("/") or "/") for route in routes}
    sitemap_paths: set[str] = set()
    for url in urls:
        loc = url.find("sm:loc", ns)
        if loc is None:
            loc = url.find("loc")
        if loc is None or not loc.text:
            error("sitemap URL missing loc")
            ok = False
            continue
        path = loc.text.replace("https://hoax.ai", "").rstrip("/") or "/"
        sitemap_paths.add(path)
        if not (ROOT / route_to_file(path)).is_file():
            error(f"sitemap URL {path} missing local file")
            ok = False
    if registry_paths != sitemap_paths:
        error("route registry and sitemap path sets must match")
        ok = False
    return ok


def validate_robots_noindex_metadata() -> bool:
    ok = True
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8").lower()
    if "allow: /" not in robots or "sitemap:" not in robots:
        error("robots.txt must allow crawl and reference sitemap")
        ok = False
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        lower = (ROOT / rel).read_text(encoding="utf-8").lower()
        if 'content="noindex' in lower or "content='noindex" in lower:
            error(f"{rel}: accidental noindex on public page")
            ok = False
    for rel in CORE_PAGES:
        content = (ROOT / rel).read_text(encoding="utf-8")
        lower = content.lower()
        for needle in ('rel="canonical"', 'name="description"', "og:title", "og:description", "og:url"):
            if needle not in lower:
                error(f"{rel}: missing metadata {needle}")
                ok = False
        if len(re.findall(r"<h1\b", content, re.I)) != 1:
            error(f"{rel}: expected exactly one H1")
            ok = False
    return ok


def validate_release_candidate_surfaces() -> bool:
    ok = True
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    system_map = (ROOT / "system-map/index.html").read_text(encoding="utf-8")
    if "Current public route count: 104" not in home or "Current public route count: 104" not in system_map:
        error("homepage and system map must reflect 104-route public surface")
        ok = False
    for needle in (
        "public-release-indexation-integrity",
        "public-entry-path-integrity",
        "public-discovery-integrity-closure",
        "public-reference-release-candidate-integrity",
    ):
        if needle not in home:
            error(f"homepage missing {needle}")
            ok = False
        if needle not in system_map:
            error(f"system map missing {needle}")
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
    if "public-discovery-integrity-closure" not in home or "public-discovery-integrity-closure" not in system_map:
        error("Phase 5 discovery integrity closure must remain discoverable")
        ok = False
    for rel in PATCHED_PAGES:
        if "public-reference-release-candidate-integrity" not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel}: missing release-candidate hardening")
            ok = False
    if "104-route release" in (ROOT / "route-groups/review-and-overview-layers/index.html").read_text(encoding="utf-8"):
        error("route-group page still contains ambiguous 104-route release language")
        ok = False
    if "launch readiness" in home.lower():
        error("homepage still contains launch-readiness ambiguity")
        ok = False
    return ok


def validate_internal_links() -> bool:
    ok = True
    routes = internal_route_set()
    audited = set(PATCHED_PAGES + [rel for _, rel in EXTERNAL_USE] + PHASE3_ROUTES + CORE_PAGES)
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


def validate_no_prohibited_elements() -> bool:
    ok = True
    for rel in PATCHED_PAGES:
        html = (ROOT / rel).read_text(encoding="utf-8").lower()
        for bad in ("<script", "<form", "<input", "<textarea", "<select"):
            if bad in html:
                error(f"{rel}: prohibited element {bad}")
                ok = False
    for forbidden_path in (
        "release/index.html",
        "launch/index.html",
        "announcement/index.html",
        "press/index.html",
        "marketing/index.html",
        "pricing/index.html",
        "sales/index.html",
        "api/index.html",
        "dashboard/index.html",
    ):
        if (ROOT / forbidden_path).exists():
            error(f"forbidden public route file exists: {forbidden_path}")
            ok = False
    return ok


def validate_terms_and_decision() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    if data.get("new_decision_created"):
        error("new_decision_created must be false unless DEC governs visible fix")
        ok = False
    text = "\n".join(
        (ROOT / rel).read_text(encoding="utf-8")
        for rel in [AUDIT_MD, SPRINT, JSON_PATH] + PATCHED_PAGES
    )
    for term in UNSAFE_TERMS:
        if unnegated(text, term):
            error(f"unnegated unsafe term {term!r}")
            ok = False
    return ok


def validate_governance_wiring() -> bool:
    ok = True
    if not any(claim.get("claim_id") == "CLAIM-0136" for claim in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0136 missing")
        ok = False
    if not any(gate.get("gate_id") == "PUB-GATE-0129" for gate in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0129 missing")
        ok = False
    if "validate_public_reference_release_candidate_integrity_audit_v1.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py missing Sprint 135 validator wiring")
        ok = False
    return ok


def main() -> int:
    checks = [
        validate_artifacts(),
        validate_audit_json(),
        validate_no_expansion(),
        validate_robots_noindex_metadata(),
        validate_release_candidate_surfaces(),
        validate_internal_links(),
        validate_stale_route_counts(),
        validate_no_prohibited_elements(),
        validate_terms_and_decision(),
        validate_governance_wiring(),
    ]
    if all(checks):
        print("PASS: Public Reference Release Candidate Integrity Audit v1")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
