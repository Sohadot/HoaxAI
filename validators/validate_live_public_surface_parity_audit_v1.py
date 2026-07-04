#!/usr/bin/env python3
"""Validate Sprint 136 — Live Public Surface Parity Audit v1.

This validator is intentionally network-independent. It validates the recorded
live audit artifact and repository invariants only.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import ALLOWED_PUBLIC_HTML, PUBLIC_SITEMAP_URL_COUNT  # noqa: E402

AUDIT_MD = "LIVE_PUBLIC_SURFACE_PARITY_AUDIT_V1.md"
SPRINT = "SPRINT_136_LIVE_PUBLIC_SURFACE_PARITY_AUDIT_V1.md"
JSON_PATH = "data/live-public-surface-parity-audit-v1.json"
SCHEMA_PATH = "data/live-public-surface-parity-audit-v1.schema.json"
SPRINT135_AUDIT = "PUBLIC_REFERENCE_RELEASE_CANDIDATE_INTEGRITY_AUDIT_V1.md"
SPRINT135_JSON = "data/public-reference-release-candidate-integrity-audit-v1.json"
SPRINT135_VALIDATOR = "validators/validate_public_reference_release_candidate_integrity_audit_v1.py"

REQUIRED_RECORD_FIELDS = [
    "live_parity_record_id",
    "repository_page_or_file",
    "live_url",
    "record_type",
    "expected_repository_state",
    "actual_live_state",
    "parity_status",
    "http_status",
    "observed_issue",
    "repair_applied",
    "live_parity_check",
    "repository_integrity_check",
    "boundary_check",
    "ai_agent_note",
]

REQUIRED_SCENARIO_FIELDS = [
    "scenario_id",
    "live_parity_intent",
    "repository_pages_checked",
    "live_urls_checked",
    "expected_safe_interpretation",
    "actual_live_interpretation",
    "supporting_routes_or_artifacts",
    "result",
    "observed_issue",
    "repair_applied",
    "live_parity_check",
    "repository_integrity_check",
    "boundary_check",
    "ai_agent_note",
]

CONFIRMATION_FLAGS = [
    "live_surface_parity_confirmed",
    "repository_integrity_confirmed",
    "sitemap_parity_confirmed",
    "robots_parity_confirmed",
    "route_availability_confirmed",
    "canonical_parity_confirmed",
    "metadata_parity_confirmed",
    "open_graph_parity_confirmed",
    "homepage_parity_confirmed",
    "system_map_parity_confirmed",
    "phase_2_live_visibility_confirmed",
    "phase_3_live_visibility_confirmed",
    "phase_4_live_visibility_confirmed",
    "phase_5_live_visibility_confirmed",
    "release_candidate_live_visibility_confirmed",
    "live_internal_link_integrity_confirmed",
    "live_crawler_readability_confirmed",
    "live_ai_agent_readability_confirmed",
    "live_human_reader_interpretation_confirmed",
]

DRIFT_FLAGS = [
    "live_route_count_drift_found",
    "stale_live_deployment_found",
    "live_sitemap_mismatch_found",
    "live_robots_mismatch_found",
    "live_route_missing_found",
    "live_canonical_defect_found",
    "live_metadata_defect_found",
    "live_og_defect_found",
    "live_internal_link_defect_found",
    "live_accidental_noindex_found",
    "live_accidental_public_exposure_found",
    "live_stale_copy_found",
    "live_stale_phase_language_found",
    "live_stale_release_language_found",
    "live_commercial_drift_found",
    "live_marketing_drift_found",
    "live_launch_campaign_drift_found",
    "live_seo_spam_drift_found",
    "live_workflow_drift_found",
    "live_funnel_drift_found",
    "live_tool_drift_found",
    "live_dashboard_drift_found",
    "live_product_suite_drift_found",
    "live_service_drift_found",
    "live_commercial_conversion_drift_found",
    "live_monetization_drift_found",
    "live_pricing_drift_found",
    "live_subscription_drift_found",
    "live_support_or_sponsorship_drift_found",
    "live_donation_drift_found",
    "live_paid_report_drift_found",
    "live_private_access_drift_found",
    "live_consulting_offer_drift_found",
    "live_lead_generation_drift_found",
    "live_sales_page_drift_found",
    "live_pitch_deck_drift_found",
    "live_acquisition_solicitation_drift_found",
    "live_buyer_solicitation_drift_found",
    "live_transaction_readiness_drift_found",
    "live_due_diligence_room_drift_found",
    "live_legal_or_financial_representation_drift_found",
    "live_investment_claim_drift_found",
    "live_authority_claim_drift_found",
    "live_verification_drift_found",
    "live_proof_drift_found",
    "live_detector_drift_found",
    "live_score_or_verdict_drift_found",
    "live_case_conclusion_drift_found",
    "live_audit_as_certification_drift_found",
    "live_source_as_proof_drift_found",
    "governance_inflation_found",
]

NON_FLAGS = [
    "non_live_status_page",
    "non_deployment_page",
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
    "non_donation",
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

UNSAFE_TERMS = [
    "official release",
    "press release",
    "launch page",
    "deployment page",
    "live status page",
    "marketing funnel",
    "official certification",
    "verified authority",
    "proof engine",
    "detection service",
    "verification tool",
    "contact sales",
    "contact to buy",
    "book a call",
    "paid access",
    "paid report",
    "lead generation",
    "transaction-ready",
]

NEGATION_PATTERN = re.compile(
    r"(?:must not|does not|do not|did not|not a|not an|no|without|forbidden|prohibited|is not|are not|cannot|not)\s+[\w\s\-/,.]{0,900}",
    re.IGNORECASE,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def route_to_file(path: str) -> str:
    p = path.strip("/")
    return "index.html" if not p else f"{p}/index.html"


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
    for rel in (AUDIT_MD, SPRINT, JSON_PATH, SCHEMA_PATH, SPRINT135_AUDIT, SPRINT135_JSON, SPRINT135_VALIDATOR, "CNAME"):
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            ok = False
    if (ROOT / "CNAME").is_file() and (ROOT / "CNAME").read_text(encoding="utf-8").strip() != "hoax.ai":
        error("CNAME must be hoax.ai")
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
        error("PUB-FILE-0105 must not exist after Sprint 136 audit-only sprint")
        ok = False
    route_files = {route_to_file(route["path"]) for route in routes}
    if route_files != set(ALLOWED_PUBLIC_HTML):
        error("public HTML route set must match route registry and sitemap surface")
        ok = False
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = sitemap.findall("sm:url", ns) or sitemap.findall("url")
    if len(urls) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {len(urls)}")
        ok = False
    return ok


def validate_audit_json() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    load_json(SCHEMA_PATH)
    expected = {
        "audit_only": True,
        "live_parity_audit": True,
        "live_base_url": "https://hoax.ai/",
        "repository_release_candidate_commit": "fe7214d",
        "production_route_added": False,
        "public_route_count_before": 104,
        "public_route_count_after": 104,
        "repository_sitemap_url_count_expected": 104,
        "live_sitemap_url_count_expected": 104,
        "route_registry_count_expected": 104,
        "public_file_registry_unchanged": True,
        "route_registry_changed": False,
        "public_file_registry_changed": False,
        "sitemap_changed": False,
        "no_new_routes": True,
        "new_decision_created": False,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            error(f"{JSON_PATH}: {key} must be {value!r}")
            ok = False
    if not isinstance(data.get("live_fetch_completed"), bool):
        error(f"{JSON_PATH}: live_fetch_completed must be boolean")
        ok = False
    if not isinstance(data.get("live_access_issue_found"), bool):
        error(f"{JSON_PATH}: live_access_issue_found must be boolean")
        ok = False
    if "live_fetch_timestamp_utc" not in data or not data["live_fetch_timestamp_utc"]:
        error(f"{JSON_PATH}: live_fetch_timestamp_utc missing")
        ok = False
    for flag in CONFIRMATION_FLAGS + DRIFT_FLAGS:
        if not isinstance(data.get(flag), bool):
            error(f"{JSON_PATH}: {flag} must be recorded as boolean")
            ok = False
    for flag in NON_FLAGS:
        if data.get(flag) is not True:
            error(f"{JSON_PATH}: {flag} must be true")
            ok = False
    if data.get("repository_integrity_confirmed") is not True:
        error(f"{JSON_PATH}: repository_integrity_confirmed must be true")
        ok = False
    if data.get("live_surface_parity_confirmed") is False:
        if not (data.get("stale_live_deployment_found") or data.get("live_access_issue_found") or data.get("live_sitemap_mismatch_found") or data.get("live_route_missing_found")):
            error(f"{JSON_PATH}: unconfirmed live parity must name a live issue")
            ok = False

    records = data.get("live_parity_records", [])
    if len(records) < 60:
        error(f"{JSON_PATH}: must include at least 60 live parity records")
        ok = False
    if data.get("total_live_parity_records") != len(records):
        error(f"{JSON_PATH}: total_live_parity_records mismatch")
        ok = False
    safe = sum(1 for record in records if record.get("parity_status") == "safe")
    repaired = sum(1 for record in records if record.get("parity_status") == "repaired")
    unsafe = sum(1 for record in records if record.get("parity_status") == "unsafe")
    if data.get("live_parity_records_safe") != safe:
        error(f"{JSON_PATH}: live_parity_records_safe mismatch")
        ok = False
    if data.get("live_parity_records_repaired") != repaired:
        error(f"{JSON_PATH}: live_parity_records_repaired mismatch")
        ok = False
    if data.get("live_parity_records_unsafe") != unsafe:
        error(f"{JSON_PATH}: live_parity_records_unsafe mismatch")
        ok = False
    for record in records:
        for field in REQUIRED_RECORD_FIELDS:
            if field not in record:
                error(f"{record.get('live_parity_record_id', '?')}: missing field {field}")
                ok = False
        if record.get("parity_status") not in ("safe", "repaired", "unsafe"):
            error(f"{record.get('live_parity_record_id')}: invalid parity_status")
            ok = False

    scenarios = data.get("walkthrough_scenarios", [])
    if len(scenarios) < 60:
        error(f"{JSON_PATH}: must include at least 60 scenarios")
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


def validate_terms_and_governance() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    if data.get("new_decision_created"):
        error("new_decision_created must be false unless DEC governs visible live parity fix")
        ok = False
    text = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in [AUDIT_MD, SPRINT, JSON_PATH])
    for term in UNSAFE_TERMS:
        if unnegated(text, term):
            error(f"unnegated unsafe term {term!r}")
            ok = False
    for forbidden_path in (
        "live-status/index.html",
        "deployment/index.html",
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
    if not any(claim.get("claim_id") == "CLAIM-0137" for claim in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0137 missing")
        ok = False
    if not any(gate.get("gate_id") == "PUB-GATE-0130" for gate in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0130 missing")
        ok = False
    if "validate_live_public_surface_parity_audit_v1.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py missing Sprint 136 validator wiring")
        ok = False
    return ok


def main() -> int:
    checks = [
        validate_artifacts(),
        validate_no_expansion(),
        validate_audit_json(),
        validate_terms_and_governance(),
    ]
    if all(checks):
        print("PASS: Live Public Surface Parity Audit v1")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
