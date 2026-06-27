#!/usr/bin/env python3
"""Validate Hoax.ai publisher dry-run harness enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "refusal_principle",
    "allowed_dry_run_actions",
    "prohibited_dry_run_actions",
    "required_packet_fields",
    "required_failure_classes",
    "pass_meaning",
    "non_authorization_rules",
    "last_reviewed",
}

CASES_TOP = {"case_set_id", "name", "version", "status", "maturity", "cases", "last_reviewed"}

RESULTS_TOP = {
    "result_set_id",
    "name",
    "version",
    "status",
    "maturity",
    "expected_results",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "PUBLISHER_DRY_RUN_HARNESS.md",
    "data/publisher-dry-run-policy.json",
    "data/publisher-dry-run-cases.json",
    "data/publisher-dry-run-expected-results.json",
    "validators/validate_publisher_dry_run.py",
]

REQUIRED_CASE_IDS = [f"DRY-RUN-CASE-{i:04d}" for i in range(1, 21)]

REQUIRED_FAILURE_CLASSES = [
    "route_creation",
    "sitemap",
    "draft_creation",
    "missing_reference_thesis",
    "missing_claim_scope",
    "missing_source_scope",
    "missing_governance_boundary",
    "keyword_only",
    "search_volume",
    "tool_implication",
    "upload",
    "scoring",
    "fake_real",
    "subject_accusation",
    "unsupported_external",
    "publication",
    "schema",
]

PROHIBITED_ACTIONS = [
    "page_creation",
    "draft_creation",
    "route_creation",
    "sitemap",
    "publishing",
    "deployment",
    "dns",
    "cloudflare",
    "forms",
    "analytics",
    "upload",
    "scoring",
    "classifier",
    "external_factual",
]

NON_AUTHORIZATION_TERMS = [
    "publishing",
    "drafts",
    "routes",
    "sitemap",
    "seo_expansion",
    "deployment",
]

REAL_ENTITY_TERMS = [
    "donald trump",
    "joe biden",
    "google",
    "microsoft",
    "openai",
    "facebook",
    "meta platforms",
    "ukraine war",
    "election 2024",
    "world health organization",
    "united nations",
    "elon musk",
]

OUTPUT_REQUEST_VALUES = {"create", "create_route", "add_sitemap_entry", "create_draft", "publish_now", "publish", "expand"}

CASE_ID_PATTERN = re.compile(r"^DRY-RUN-CASE-\d{4}$")

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    ALLOWED_PUBLIC_ROOT_FILES,
    PUBLISHER_STATUSES_ALLOWED,
    PUBLISHER_STATUS_POST_PILOT,
    validate_no_extra_public_html,
    validate_pilot_public_surface,
    validate_pilot_route_registry,
    validate_pilot_sitemap,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
)

PUBLIC_FILES = ALLOWED_PUBLIC_ROOT_FILES

DRAFT_PATTERNS = ["draft/", "drafts/", "-draft.html", "_draft.html"]
ALLOWED_INTERNAL_DRAFT_ROOT = "_internal_drafts"


def _is_governed_internal_draft(path: Path) -> bool:
    try:
        return path.relative_to(ROOT).parts[0] == ALLOWED_INTERNAL_DRAFT_ROOT
    except (ValueError, IndexError):
        return False

NEGATION_MARKERS = [
    "no ",
    "not ",
    "without ",
    "does not",
    "do not",
    "never ",
    "blocked",
    "prohibited",
    "not a ",
]


def contains_unnegated(blob: str, pattern: str) -> bool:
    if pattern not in blob:
        return False
    idx = 0
    while True:
        pos = blob.find(pattern, idx)
        if pos == -1:
            return False
        prefix = blob[max(0, pos - 40) : pos]
        if any(marker in prefix for marker in NEGATION_MARKERS):
            idx = pos + len(pattern)
            continue
        return True
    return False


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def case_text_blob(case: dict) -> str:
    fields = [
        "case_name",
        "reference_thesis",
        "purpose_statement",
        "definition_scope_summary",
        "governance_boundary_summary",
        "claim_scope_summary",
        "source_scope_summary",
        "semantic_seo_role",
        "prohibited_misreading_notes",
        "notes",
    ]
    return " ".join(str(case.get(f, "")) for f in fields).lower()


def is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def is_output_request(value: object) -> bool:
    if value is None:
        return False
    normalized = str(value).strip().lower()
    if normalized in ("none", "none_requested", "no", "not_requested", ""):
        return False
    return normalized in OUTPUT_REQUEST_VALUES or any(
        term in normalized for term in ("create", "publish", "add_", "expand")
    )


def evaluate_case(case: dict) -> tuple[str, str | None]:
    """Return (pass|fail, failure_reason_or_none)."""
    if is_output_request(case.get("requested_route_action")):
        return "fail", "route_creation_request"
    if is_output_request(case.get("requested_sitemap_action")):
        return "fail", "sitemap_expansion_request"
    if is_output_request(case.get("requested_draft_action")):
        return "fail", "draft_creation_request"
    if is_output_request(case.get("requested_publication_action")):
        return "fail", "direct_publication_request"

    if is_missing(case.get("reference_thesis")):
        return "fail", "missing_reference_thesis"
    if is_missing(case.get("claim_scope_summary")):
        return "fail", "missing_claim_scope"
    if is_missing(case.get("source_scope_summary")):
        return "fail", "missing_source_scope"
    if is_missing(case.get("governance_boundary_summary")):
        return "fail", "missing_governance_boundary"

    blob = case_text_blob(case)

    if "keyword-only" in blob or "keyword only" in blob or "keyword stuffing" in blob:
        return "fail", "keyword_only_seo"
    if "search-volume-first" in blob or "search volume" in blob and "first" in blob:
        return "fail", "search_volume_first"
    if any(contains_unnegated(blob, term) for term in ["scan now", "try our tool", "live classifier", "public classifier"]):
        return "fail", "tool_implication"
    if any(contains_unnegated(blob, term) for term in ["upload your", "upload workflow", "upload a file", "upload your file"]):
        return "fail", "upload_implication"
    if any(term in blob for term in ["truth score", "fake score", "risk score", "scoring engine"]):
        return "fail", "scoring_implication"
    if any(term in blob for term in ["fake or real", "is it fake", "fake/real", "binary verdict"]):
        return "fail", "fake_real_framing"
    if any(term in blob for term in [" accuse ", "determine guilt", "fraud of the", "guilt and fraud"]):
        return "fail", "subject_accusation"
    if any(term in blob for term in ["without source mapping", "unverified external", "97 percent", "according to recent reports"]):
        return "fail", "unsupported_external_factual_claim"
    if any(term in blob for term in ["softwareapplication", "product service", "apireference", "commercial product"]):
        return "fail", "prohibited_schema_tool_service_product_language"
    if any(term in blob for term in ["world's first", "worlds first", "only system that", "impossible to copy"]):
        return "fail", "unsupported_superiority"

    return "pass", None


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-dry-run-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-dry-run-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"publisher-dry-run-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_publisher_dry_run_harness":
        error("publisher-dry-run-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "candidate_logic_test_only_no_publication":
        error("publisher-dry-run-policy.json: invalid maturity")
        ok = False

    principle = data.get("governing_principle", "")
    if "The dry-run may test publisher logic. It must not create publishable content." not in principle:
        error("publisher-dry-run-policy.json: governing principle missing required sentence")
        ok = False

    refusal = data.get("refusal_principle", "")
    if "A publisher is not trusted because it can generate. It is trusted because it can refuse." not in refusal:
        error("publisher-dry-run-policy.json: refusal principle missing required sentence")
        ok = False

    prohibited = " ".join(data.get("prohibited_dry_run_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"publisher-dry-run-policy.json: prohibited_dry_run_actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"publisher-dry-run-policy.json: non_authorization_rules missing {term}")
            ok = False

    failure_classes = " ".join(data.get("required_failure_classes", [])).lower()
    for term in REQUIRED_FAILURE_CLASSES:
        if term.replace("_", "") not in failure_classes.replace("_", ""):
            error(f"publisher-dry-run-policy.json: required_failure_classes missing {term}")
            ok = False

    return ok


def validate_cases() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-dry-run-cases.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-dry-run-cases.json parse failed: {exc}")
        return False

    missing = CASES_TOP - set(data.keys())
    if missing:
        error(f"publisher-dry-run-cases.json missing fields: {sorted(missing)}")
        ok = False

    cases = data.get("cases", [])
    if len(cases) < 16:
        error(f"publisher-dry-run-cases.json: need at least 16 cases, found {len(cases)}")
        ok = False

    ids = [c.get("dry_run_case_id") for c in cases]
    if len(ids) != len(set(ids)):
        error("publisher-dry-run-cases.json: duplicate dry_run_case_id")
        ok = False
    for cid in ids:
        if not CASE_ID_PATTERN.match(cid or ""):
            error(f"publisher-dry-run-cases.json: invalid dry_run_case_id {cid}")
            ok = False
    if set(ids) != set(REQUIRED_CASE_IDS):
        error(f"publisher-dry-run-cases.json: expected case IDs {REQUIRED_CASE_IDS}")
        ok = False

    pass_count = 0
    fail_count = 0
    for case in cases:
        cid = case.get("dry_run_case_id", "?")
        if case.get("fictional") is not True:
            error(f"publisher-dry-run-cases.json: {cid} fictional must be true")
            ok = False
        if case.get("candidate_shape_only") is not True:
            error(f"publisher-dry-run-cases.json: {cid} candidate_shape_only must be true")
            ok = False

        result = case.get("expected_result")
        if result not in ("pass", "fail"):
            error(f"publisher-dry-run-cases.json: {cid} invalid expected_result")
            ok = False

        blob = case_text_blob(case)
        for term in REAL_ENTITY_TERMS:
            if term in blob:
                error(f"publisher-dry-run-cases.json: {cid} contains real entity term '{term}'")
                ok = False

        if result == "pass":
            pass_count += 1
            for action_field in [
                "requested_route_action",
                "requested_sitemap_action",
                "requested_draft_action",
                "requested_publication_action",
            ]:
                if is_output_request(case.get(action_field)):
                    error(f"publisher-dry-run-cases.json: pass case {cid} must not request output via {action_field}")
                    ok = False
            if case.get("expected_failure_reason"):
                error(f"publisher-dry-run-cases.json: pass case {cid} must not have expected_failure_reason")
                ok = False
        else:
            fail_count += 1
            if not case.get("expected_failure_reason"):
                error(f"publisher-dry-run-cases.json: fail case {cid} missing expected_failure_reason")
                ok = False

        computed, computed_reason = evaluate_case(case)
        if computed != result:
            error(
                f"publisher-dry-run-cases.json: {cid} logic mismatch "
                f"(expected {result}, computed {computed})"
            )
            ok = False
        elif result == "fail" and computed_reason != case.get("expected_failure_reason"):
            error(
                f"publisher-dry-run-cases.json: {cid} failure reason mismatch "
                f"(expected {case.get('expected_failure_reason')}, computed {computed_reason})"
            )
            ok = False

    if pass_count < 3:
        error("publisher-dry-run-cases.json: need at least 3 pass cases")
        ok = False
    if fail_count < 13:
        error("publisher-dry-run-cases.json: need sufficient fail cases")
        ok = False

    return ok


def validate_expected_results() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-dry-run-expected-results.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-dry-run-expected-results.json parse failed: {exc}")
        return False

    missing = RESULTS_TOP - set(data.keys())
    if missing:
        error(f"publisher-dry-run-expected-results.json missing fields: {sorted(missing)}")
        ok = False

    results = data.get("expected_results", [])
    result_ids = {r.get("dry_run_case_id") for r in results}
    if result_ids != set(REQUIRED_CASE_IDS):
        error("publisher-dry-run-expected-results.json: must have one result per dry-run case")
        ok = False

    cases_by_id = {
        c["dry_run_case_id"]: c
        for c in load_json(ROOT / "data" / "publisher-dry-run-cases.json").get("cases", [])
    }

    for entry in results:
        cid = entry.get("dry_run_case_id", "?")
        case = cases_by_id.get(cid)
        if not case:
            error(f"publisher-dry-run-expected-results.json: unknown case {cid}")
            ok = False
            continue

        for auth_field in [
            "publication_authorized",
            "draft_authorized",
            "route_authorized",
            "sitemap_authorized",
        ]:
            if entry.get(auth_field) is not False:
                error(f"publisher-dry-run-expected-results.json: {cid} {auth_field} must be false")
                ok = False

        if entry.get("expected_result") != case.get("expected_result"):
            error(f"publisher-dry-run-expected-results.json: {cid} expected_result mismatch with case")
            ok = False
        if entry.get("expected_state") != case.get("expected_state"):
            error(f"publisher-dry-run-expected-results.json: {cid} expected_state mismatch with case")
            ok = False

        if case.get("expected_result") == "fail":
            if not entry.get("rejection_reason_if_fail"):
                error(f"publisher-dry-run-expected-results.json: fail case {cid} missing rejection_reason_if_fail")
                ok = False
            elif entry.get("rejection_reason_if_fail") != case.get("expected_failure_reason"):
                error(f"publisher-dry-run-expected-results.json: {cid} rejection reason mismatch")
                ok = False
        elif "future_governance_review" not in " ".join(entry.get("required_checks", [])).lower():
            error(f"publisher-dry-run-expected-results.json: pass case {cid} must authorize only future governance review")
            ok = False

    return ok


def validate_state_machine() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "publisher-state-machine.json")

    states = data.get("states", [])
    if "public_release_blocked" not in states:
        error("publisher-state-machine.json: public_release_blocked state missing")
        ok = False
    if "dry_run_pass" not in states:
        error("publisher-state-machine.json: dry_run_pass state missing")
        ok = False
    if "candidate_pack_registered" not in states:
        error("publisher-state-machine.json: candidate_pack_registered state missing")
        ok = False

    current = data.get("current_system_state", "")
    if current not in (
        "blocked",
        "blocked_until_first_reference_candidate_pack",
        "blocked_until_internal_draft_blueprint",
        "blocked_until_first_internal_draft_blueprint_pack",
        "blocked_until_first_internal_draft_pack",
        "blocked_until_internal_draft_review_and_refinement",
        "blocked_until_public_route_readiness_gate",
        "blocked_until_first_controlled_public_reference_pilot",
        "blocked_until_public_reference_validation_and_live_surface_audit",
        "blocked_until_public_category_language_layer",
        "blocked_until_public_category_language_validation",
        "blocked_until_evidence_posture_workbench_governance",
        "blocked_until_evidence_posture_workbench_dry_run_harness",
        "blocked_until_workbench_specification_layer",
        "blocked_until_workbench_interface_blueprint_governance",
        "blocked_until_workbench_interface_blueprint_validation",
        "blocked_until_non_public_static_workbench_prototype_governance",
        "blocked_until_non_public_static_workbench_prototype_v1",
        "blocked_until_non_public_static_workbench_prototype_validation",
        "blocked_until_non_public_static_workbench_prototype_refinement",
        "blocked_until_non_public_static_workbench_prototype_refinement_validation",
        "blocked_until_non_public_static_workbench_visual_system_hardening",
        "blocked_until_non_public_static_workbench_visual_system_hardening_validation",
        "blocked_until_non_public_static_workbench_visual_system_baseline_lock",
        "blocked_until_non_public_static_workbench_visual_system_baseline_lock_validation",
        "blocked_until_non_public_static_workbench_public_readiness_boundary_governance",
        "blocked_until_non_public_static_workbench_public_readiness_boundary_validation",
        "blocked_until_public_route_eligibility_governance",
        "blocked_until_public_route_eligibility_governance_validation",
        "blocked_until_public_route_candidate_assessment_governance",
        "blocked_until_public_route_candidate_assessment_governance_validation",
        "blocked_until_public_route_candidate_registry_governance",
        "blocked_until_public_route_candidate_registry_governance_validation",
        "blocked_until_public_route_candidate_registration_governance",
        "blocked_until_public_route_candidate_registration_governance_validation",
        "blocked_until_public_route_candidate_registration_authorization_governance",
        "blocked_until_public_reference_production_batch_1",
        "blocked_until_public_reference_production_batch_1_validation",
        "blocked_until_public_reference_production_batch_2_validation",
        "blocked_until_public_reference_production_batch_3_validation",
        "blocked_until_evidence_posture_standard_v1_validation",
        "blocked_until_evidence_posture_protocol_v1_draft_validation",
        "blocked_until_public_interface_thesis_evidence_field_validation",
        "blocked_until_evidence_field_static_interface_embodiment_v1_validation",
        "blocked_until_evidence_field_visual_system_accessibility_hardening_validation",
        "blocked_until_controlled_domain_connection_decision",
        "blocked_until_engine_boundary_and_public_reference_seo_authority_map_validation",
        "blocked_until_evidence_posture_engine_model_v0_validation",
        "blocked_until_output_language_guardrail_model_v1_validation",
        "blocked_until_internal_non_public_engine_prototype_charter_validation",
        "blocked_until_controlled_internal_prototype_v0_implementation_sprint",
        "blocked_until_controlled_internal_prototype_v0_validation",
        "blocked_until_controlled_internal_prototype_v0_hardening_validation",
        "blocked_until_internal_prototype_traceability_interpretability_audit_validation",
        "blocked_until_internal_prototype_fixture_coverage_matrix_validation",
        "blocked_until_targeted_synthetic_fixture_expansion_v1_validation",
        "blocked_until_internal_prototype_compound_boundary_stress_test_validation",
        "blocked_until_internal_prototype_guardrail_red_team_pack_validation",
        "blocked_until_internal_prototype_release_blocker_board_validation",
        "blocked_until_public_exposure_prerequisite_map_validation",
        "blocked_until_public_copy_boundary_framework_validation",
        "blocked_until_public_evidence_risk_utility_surface_validation",
        "blocked_until_public_reference_route_expansion_validation",
        "blocked_until_public_utility_interface_embodiment_validation",
        "blocked_until_public_reference_authority_internal_linking_validation",
        "blocked_until_public_reference_source_confidence_layer_validation",
        "blocked_until_public_reference_answer_surface_validation",
        "blocked_until_public_reference_citation_retrieval_hardening_validation",
        "blocked_until_public_reference_quality_consolidation_validation",
        "blocked_until_public_reference_depth_expansion_validation",
        "blocked_until_public_reference_pathway_pages_validation",
        "blocked_until_public_reference_navigation_ia_consolidation_validation",
        "blocked_until_public_reference_surface_authority_review_validation",
        "blocked_until_public_reference_strategic_entry_points_validation",
        "blocked_until_public_reference_strategic_narrative_surface_validation",
        "blocked_until_public_reference_acquisition_readiness_surface_validation",
        "blocked_until_public_reference_strategic_surface_consolidation_validation",
        "blocked_until_public_reference_release_integrity_audit_validation",
        "blocked_until_public_reference_external_review_readiness_validation",
        "blocked_until_public_reference_reviewer_packet_validation",
        "blocked_until_public_reference_review_packet_integrity_audit_validation",
        "blocked_until_public_reference_executive_overview_surface_validation",
        "blocked_until_public_reference_executive_overview_integrity_audit_validation",
        "blocked_until_public_reference_strategic_review_index_validation",
        "blocked_until_public_reference_strategic_review_index_integrity_audit_validation",
    ):
        error(f"publisher-state-machine.json: invalid current_system_state {current}")
        ok = False

    blocked = data.get("blocked_transitions", [])
    dry_run_to_release = any(
        b.get("from") == "dry_run_pass" and b.get("to") == "release_eligible" for b in blocked
    )
    dry_run_to_public = any(
        b.get("from") == "dry_run_pass"
        and b.get("to") in ("public_release_blocked", "public_live")
        for b in blocked
    )
    if not dry_run_to_release:
        error("publisher-state-machine.json: must block dry_run_pass to release_eligible")
        ok = False
    if not dry_run_to_public:
        error("publisher-state-machine.json: must block dry_run_pass to public release")
        ok = False

    release_req = data.get("release_eligible_requires", [])
    if len(release_req) < 8:
        error("publisher-state-machine.json: release_eligible_requires too few gates")
        ok = False

    return ok


def validate_publisher_gates() -> bool:
    ok = True
    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    dry_run_gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0016"), None)
    if not dry_run_gate:
        error("publisher-quality-gates: PUB-GATE-0016 missing")
        ok = False
    else:
        if dry_run_gate.get("required_before_public_release") is not True:
            error("publisher-quality-gates: PUB-GATE-0016 must be required before public release")
            ok = False
        if dry_run_gate.get("bypassable") is True:
            error("publisher-quality-gates: PUB-GATE-0016 must not be bypassable")
            ok = False
        notes = dry_run_gate.get("notes", "").lower()
        if "authorize" in notes and "does not authorize" not in notes:
            error("publisher-quality-gates: PUB-GATE-0016 must not authorize publishing by itself")
            ok = False

    for gate in gates:
        if gate.get("required_before_public_release") is not True:
            error(f"publisher-quality-gates: {gate.get('gate_id')} must remain required before public release")
            ok = False

    return ok


def validate_repository_safety() -> bool:
    ok = True

    candidates = load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", [])
    if candidates:
        from candidate_registry_checks import validate_candidates_blocked_only

        if not validate_candidates_blocked_only(candidates, error):
            ok = False

    queues = load_json(ROOT / "data" / "publisher-queue-registry.json").get("queues", [])
    for q in queues:
        if q.get("items"):
            error(f"publisher-queue-registry: queue {q.get('queue_id')} must be empty")
            ok = False

    public_dir_files = {p.name for p in ROOT.iterdir() if p.is_file()}
    extra_public = public_dir_files - PUBLIC_FILES
    html_extra = [f for f in extra_public if f.endswith(".html")]
    if html_extra:
        error(f"repository safety: unexpected public HTML files {html_extra}")
        ok = False

    for pattern in DRAFT_PATTERNS:
        matches = [
            p for p in ROOT.glob(f"**/*{pattern}*")
            if not _is_governed_internal_draft(p)
        ]
        if matches:
            error(f"repository safety: draft-like files found matching {pattern}")
            ok = False

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
            if not locs:
                locs = [el.text.strip() for el in root.findall(".//{*}loc") if el.text]
            eligible = {
                r.get("canonical_url")
                for r in routes
                if r.get("sitemap_included") is True
            }
            if set(locs) != eligible:
                error("sitemap.xml: expansion or mismatch detected")
                ok = False
        except ET.ParseError as exc:
            error(f"sitemap.xml parse failed: {exc}")
            ok = False

    return ok


def validate_cross_file() -> bool:
    ok = True

    pub_policy = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub_policy.get("current_publisher_status", "")
    if status not in (
        "blocked_until_first_reference_candidate_pack",
        "blocked_until_internal_draft_blueprint",
        "blocked_until_first_internal_draft_blueprint_pack",
        "blocked_until_first_internal_draft_pack",
        "blocked_until_internal_draft_review_and_refinement",
        "blocked_until_public_route_readiness_gate",
        "blocked_until_first_controlled_public_reference_pilot",
        "blocked_until_public_reference_validation_and_live_surface_audit",
        "blocked_until_public_category_language_layer",
        "blocked_until_public_category_language_validation",
        "blocked_until_evidence_posture_workbench_governance",
        "blocked_until_evidence_posture_workbench_dry_run_harness",
        "blocked_until_workbench_specification_layer",
        "blocked_until_workbench_interface_blueprint_governance",
        "blocked_until_workbench_interface_blueprint_validation",
        "blocked_until_non_public_static_workbench_prototype_governance",
        "blocked_until_non_public_static_workbench_prototype_v1",
        "blocked_until_non_public_static_workbench_prototype_validation",
        "blocked_until_non_public_static_workbench_prototype_refinement",
        "blocked_until_non_public_static_workbench_prototype_refinement_validation",
        "blocked_until_non_public_static_workbench_visual_system_hardening",
        "blocked_until_non_public_static_workbench_visual_system_hardening_validation",
        "blocked_until_non_public_static_workbench_visual_system_baseline_lock",
        "blocked_until_non_public_static_workbench_visual_system_baseline_lock_validation",
        "blocked_until_non_public_static_workbench_public_readiness_boundary_governance",
        "blocked_until_non_public_static_workbench_public_readiness_boundary_validation",
        "blocked_until_public_route_eligibility_governance",
        "blocked_until_public_route_eligibility_governance_validation",
        "blocked_until_public_route_candidate_assessment_governance",
        "blocked_until_public_route_candidate_assessment_governance_validation",
        "blocked_until_public_route_candidate_registry_governance",
        "blocked_until_public_route_candidate_registry_governance_validation",
        "blocked_until_public_route_candidate_registration_governance",
        "blocked_until_public_route_candidate_registration_governance_validation",
        "blocked_until_public_route_candidate_registration_authorization_governance",
        "blocked_until_public_reference_production_batch_1",
        "blocked_until_public_reference_production_batch_1_validation",
        "blocked_until_public_reference_production_batch_2_validation",
        "blocked_until_public_reference_production_batch_3_validation",
        "blocked_until_evidence_posture_standard_v1_validation",
        "blocked_until_evidence_posture_protocol_v1_draft_validation",
        "blocked_until_public_interface_thesis_evidence_field_validation",
        "blocked_until_evidence_field_static_interface_embodiment_v1_validation",
        "blocked_until_evidence_field_visual_system_accessibility_hardening_validation",
        "blocked_until_controlled_domain_connection_decision",
        "blocked_until_engine_boundary_and_public_reference_seo_authority_map_validation",
        "blocked_until_evidence_posture_engine_model_v0_validation",
        "blocked_until_output_language_guardrail_model_v1_validation",
        "blocked_until_internal_non_public_engine_prototype_charter_validation",
        "blocked_until_controlled_internal_prototype_v0_implementation_sprint",
        "blocked_until_controlled_internal_prototype_v0_validation",
        "blocked_until_controlled_internal_prototype_v0_hardening_validation",
        "blocked_until_internal_prototype_traceability_interpretability_audit_validation",
        "blocked_until_internal_prototype_fixture_coverage_matrix_validation",
        "blocked_until_targeted_synthetic_fixture_expansion_v1_validation",
        "blocked_until_internal_prototype_compound_boundary_stress_test_validation",
        "blocked_until_internal_prototype_guardrail_red_team_pack_validation",
        "blocked_until_internal_prototype_release_blocker_board_validation",
        "blocked_until_public_exposure_prerequisite_map_validation",
        "blocked_until_public_copy_boundary_framework_validation",
        "blocked_until_public_evidence_risk_utility_surface_validation",
        "blocked_until_public_reference_route_expansion_validation",
        "blocked_until_public_utility_interface_embodiment_validation",
        "blocked_until_public_reference_authority_internal_linking_validation",
        "blocked_until_public_reference_source_confidence_layer_validation",
        "blocked_until_public_reference_answer_surface_validation",
        "blocked_until_public_reference_citation_retrieval_hardening_validation",
        "blocked_until_public_reference_quality_consolidation_validation",
        "blocked_until_public_reference_depth_expansion_validation",
        "blocked_until_public_reference_pathway_pages_validation",
        "blocked_until_public_reference_navigation_ia_consolidation_validation",
        "blocked_until_public_reference_surface_authority_review_validation",
        "blocked_until_public_reference_strategic_entry_points_validation",
        "blocked_until_public_reference_strategic_narrative_surface_validation",
        "blocked_until_public_reference_acquisition_readiness_surface_validation",
        "blocked_until_public_reference_strategic_surface_consolidation_validation",
        "blocked_until_public_reference_release_integrity_audit_validation",
        "blocked_until_public_reference_external_review_readiness_validation",
        "blocked_until_public_reference_reviewer_packet_validation",
        "blocked_until_public_reference_review_packet_integrity_audit_validation",
        "blocked_until_public_reference_executive_overview_surface_validation",
        "blocked_until_public_reference_executive_overview_integrity_audit_validation",
        "blocked_until_public_reference_strategic_review_index_validation",
        "blocked_until_public_reference_strategic_review_index_integrity_audit_validation",
    ):
        error(
            f"publisher-governance-policy: current_publisher_status must remain blocked from publication, got {status}"
        )
        ok = False
    prohibited = " ".join(pub_policy.get("prohibited_current_outputs", [])).lower()
    if "draft_pages" not in prohibited and "content_drafts" not in prohibited:
        error("publisher-governance-policy: draft outputs must remain prohibited")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "publisher_dry_run" not in checks and "dry_run" not in checks:
        error("reference-expansion-gate.json: must include publisher dry-run harness pre-release check")
        ok = False

    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry.json: missing source for {loc}")
            ok = False

    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_publisher_dry_run.py" not in content:
        error("validate_all.py: must include validate_publisher_dry_run.py")
        ok = False

    return ok


def main() -> int:
    checks = [
        ("dry-run policy", validate_policy),
        ("dry-run cases", validate_cases),
        ("expected results", validate_expected_results),
        ("state machine", validate_state_machine),
        ("publisher quality gates", validate_publisher_gates),
        ("repository safety", validate_repository_safety),
        ("cross-file integration", validate_cross_file),
    ]

    all_ok = True
    for name, fn in checks:
        if not fn():
            all_ok = False

    if all_ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
