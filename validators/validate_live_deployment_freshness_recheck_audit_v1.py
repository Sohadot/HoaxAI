#!/usr/bin/env python3
"""Validate Sprint 137 — Live Deployment Freshness Recheck Audit v1.

The validator is intentionally network-independent. It validates the recorded
recheck artifact plus repository invariants only.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import ALLOWED_PUBLIC_HTML, PUBLIC_SITEMAP_URL_COUNT  # noqa: E402

AUDIT_MD = "LIVE_DEPLOYMENT_FRESHNESS_RECHECK_AUDIT_V1.md"
SPRINT = "SPRINT_137_LIVE_DEPLOYMENT_FRESHNESS_RECHECK_AUDIT_V1.md"
JSON_PATH = "data/live-deployment-freshness-recheck-audit-v1.json"
SCHEMA_PATH = "data/live-deployment-freshness-recheck-audit-v1.schema.json"
SPRINT136_AUDIT = "LIVE_PUBLIC_SURFACE_PARITY_AUDIT_V1.md"
SPRINT136_JSON = "data/live-public-surface-parity-audit-v1.json"
SPRINT136_VALIDATOR = "validators/validate_live_public_surface_parity_audit_v1.py"

REQUIRED_RECORD_FIELDS = [
    "recheck_record_id",
    "live_url",
    "record_type",
    "expected_live_state",
    "actual_live_state",
    "previous_sprint_136_state",
    "current_recheck_state",
    "status",
    "observed_issue",
    "repair_applied",
    "freshness_check",
    "boundary_check",
    "ai_agent_note",
]

REQUIRED_SCENARIO_FIELDS = [
    "scenario_id",
    "recheck_intent",
    "sprint_136_failed_scenario_reference",
    "live_urls_checked",
    "expected_live_state",
    "actual_live_state",
    "result",
    "observed_issue",
    "repair_applied",
    "freshness_check",
    "boundary_check",
    "ai_agent_note",
]

FALSE_FLAGS = [
    "live_route_count_drift_found",
    "stale_live_deployment_found",
    "live_sitemap_mismatch_found",
    "live_route_missing_found",
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
    "live_service_drift_found",
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
    "governance_inflation_found",
]

TRUE_FLAGS = [
    "release_candidate_language_visible_live",
    "public_reference_release_candidate_language_visible_live",
    "public_reference_release_candidate_integrity_anchor_visible_live",
    "live_deployment_freshness_restored",
    "repository_release_candidate_visible_live",
    "live_sitemap_104_confirmed",
    "live_homepage_freshness_confirmed",
    "live_system_map_freshness_confirmed",
    "live_strategic_review_freshness_confirmed",
    "live_boundary_preservation_confirmed",
    "non_live_status_page",
    "non_deployment_page",
    "non_release_page",
    "non_launch_page",
    "non_marketing_surface",
    "non_commercial_surface",
    "non_monetization_surface",
    "non_detector",
    "non_proof",
    "non_scoring",
    "non_verdict",
    "non_case_conclusion",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def route_to_file(path: str) -> str:
    p = path.strip("/")
    return "index.html" if not p else f"{p}/index.html"


def validate_artifacts() -> bool:
    ok = True
    for rel in (AUDIT_MD, SPRINT, JSON_PATH, SCHEMA_PATH, SPRINT136_AUDIT, SPRINT136_JSON, SPRINT136_VALIDATOR):
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            ok = False
    return ok


def validate_repository_invariants() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != 104:
        error(f"route registry must have exactly 104 entries, found {len(routes)}")
        ok = False
    public_files = load_json("data/public-file-registry.json").get("public_files", [])
    if any(file.get("public_file_id") == "PUB-FILE-0105" for file in public_files):
        error("PUB-FILE-0105 must not exist")
        ok = False
    route_files = {route_to_file(route["path"]) for route in routes}
    if route_files != set(ALLOWED_PUBLIC_HTML):
        error("public route file set must remain unchanged")
        ok = False
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = sitemap.findall("sm:url", ns) or sitemap.findall("url")
    if len(urls) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {len(urls)}")
        ok = False
    return ok


def validate_json() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    load_json(SCHEMA_PATH)
    expected = {
        "id": "live-deployment-freshness-recheck-audit-v1",
        "sprint": 137,
        "audit_only": True,
        "recheck_only": True,
        "live_base_url": "https://hoax.ai/",
        "prior_live_parity_audit": "Sprint 136",
        "prior_live_parity_commit": "0b5e393",
        "deployment_trigger_commit": "0a25e37",
        "deployment_trigger_commit_type": "empty commit",
        "repository_repair_required": False,
        "production_route_added": False,
        "public_route_count_before": 104,
        "public_route_count_after": 104,
        "repository_sitemap_url_count_expected": 104,
        "live_sitemap_url_count_expected": 104,
        "live_fetch_completed": True,
        "live_access_issue_found": False,
        "sprint_136_failed_scenarios_rechecked": 5,
        "sprint_136_failed_scenarios_resolved": 5,
        "sprint_136_failed_scenarios_remaining": 0,
        "scenarios_failed": 0,
        "new_decision_created": False,
        "route_registry_changed": False,
        "public_file_registry_changed": False,
        "sitemap_changed": False,
        "no_new_routes": True,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            error(f"{JSON_PATH}: {key} must be {value!r}")
            ok = False
    for flag in TRUE_FLAGS:
        if data.get(flag) is not True:
            error(f"{JSON_PATH}: {flag} must be true")
            ok = False
    for flag in FALSE_FLAGS:
        if data.get(flag) is not False:
            error(f"{JSON_PATH}: {flag} must be false")
            ok = False
    records = data.get("recheck_records", [])
    if len(records) < 10:
        error(f"{JSON_PATH}: must include at least 10 recheck records")
        ok = False
    if data.get("total_recheck_records") != len(records):
        error(f"{JSON_PATH}: total_recheck_records mismatch")
        ok = False
    if data.get("recheck_records_safe") != len(records) or data.get("recheck_records_unsafe") != 0:
        error(f"{JSON_PATH}: recheck record counts must all be safe")
        ok = False
    for record in records:
        for field in REQUIRED_RECORD_FIELDS:
            if field not in record:
                error(f"{record.get('recheck_record_id', '?')}: missing field {field}")
                ok = False
        if record.get("status") != "safe":
            error(f"{record.get('recheck_record_id')}: status must be safe")
            ok = False
    scenarios = data.get("walkthrough_scenarios", [])
    if len(scenarios) < 10:
        error(f"{JSON_PATH}: must include at least 10 scenarios")
        ok = False
    if data.get("total_scenarios") != len(scenarios):
        error(f"{JSON_PATH}: total_scenarios mismatch")
        ok = False
    if data.get("scenarios_passed") != len(scenarios) or data.get("scenarios_failed") != 0:
        error(f"{JSON_PATH}: all scenarios must pass")
        ok = False
    for scenario in scenarios:
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in scenario:
                error(f"{scenario.get('scenario_id', '?')}: missing field {field}")
                ok = False
        if scenario.get("result") != "pass":
            error(f"{scenario.get('scenario_id')}: result must be pass")
            ok = False
    return ok


def validate_governance_wiring() -> bool:
    ok = True
    if not any(claim.get("claim_id") == "CLAIM-0138" for claim in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0138 missing")
        ok = False
    if not any(gate.get("gate_id") == "PUB-GATE-0131" for gate in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0131 missing")
        ok = False
    if "validate_live_deployment_freshness_recheck_audit_v1.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py missing Sprint 137 validator wiring")
        ok = False
    return ok


def main() -> int:
    checks = [
        validate_artifacts(),
        validate_repository_invariants(),
        validate_json(),
        validate_governance_wiring(),
    ]
    if all(checks):
        print("PASS: Live Deployment Freshness Recheck Audit v1")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
