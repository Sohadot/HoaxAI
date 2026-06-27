#!/usr/bin/env python3
"""Validate Hoax.ai reference candidate evaluation and prioritization enforcement."""

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
    "boundary_principle",
    "allowed_evaluation_actions",
    "prohibited_evaluation_actions",
    "evaluation_dimensions",
    "priority_bands",
    "readiness_states",
    "non_authorization_rules",
    "last_reviewed",
}

BANDS_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "priority_bands",
    "last_reviewed",
}

DEP_MAP_TOP = {
    "dependency_map_id",
    "name",
    "version",
    "status",
    "maturity",
    "dependencies",
    "last_reviewed",
}

EVAL_TOP = {
    "evaluation_id",
    "name",
    "version",
    "status",
    "maturity",
    "evaluated_candidate_pack",
    "evaluations",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "REFERENCE_CANDIDATE_EVALUATION_AND_PRIORITIZATION.md",
    "data/reference-candidate-evaluation-policy.json",
    "data/reference-candidate-evaluation-v1.json",
    "data/reference-candidate-priority-bands.json",
    "data/reference-candidate-dependency-map.json",
    "validators/validate_reference_candidate_evaluation.py",
]

REQUIRED_CANDIDATE_IDS = [f"REF-CAND-{i:04d}" for i in range(1, 9)]

REQUIRED_BAND_IDS = [f"PRIORITY-BAND-{i:04d}" for i in range(1, 8)]

REQUIRED_BAND_NAMES = [
    "priority_foundational",
    "priority_high_dependency",
    "priority_ready_for_draft_blueprint",
    "priority_needs_boundary_refinement",
    "priority_needs_claim_scope_refinement",
    "priority_defer",
    "priority_blocked",
]

ALLOWED_READINESS_STATES = {
    "evaluation_complete",
    "draft_blueprint_candidate",
    "needs_boundary_refinement",
    "needs_claim_source_refinement",
    "needs_semantic_seo_refinement",
    "dependency_candidate",
    "deferred",
    "blocked",
}

FORBIDDEN_ELIGIBILITY = [
    "route_eligible",
    "sitemap_eligible",
    "draft_created",
    "release_eligible",
    "publication_allowed",
    "publication_eligible",
]

EVAL_FIELDS = [
    "candidate_id",
    "candidate_name",
    "evaluation_status",
    "primary_priority_band",
    "readiness_state",
    "foundation_value",
    "governance_clarity",
    "claim_source_scope_clarity",
    "semantic_seo_safety",
    "internal_link_dependency_value",
    "content_substance_readiness",
    "publisher_safety",
    "route_risk",
    "draft_blueprint_suitability",
    "blocking_issues",
    "recommended_next_step",
    "non_authorization_statement",
    "notes",
]

PROHIBITED_ACTIONS = [
    "draft_creation",
    "page_creation",
    "route_activation",
    "sitemap",
    "public_metadata",
    "publication",
    "deployment",
    "dns",
    "cloudflare",
    "tool",
    "classifier",
    "upload",
    "scoring",
    "forms",
    "analytics",
    "external_factual",
]

NON_AUTHORIZATION_TERMS = [
    "drafts",
    "routes",
    "sitemap",
    "publishing",
    "deployment",
    "seo_expansion",
]

NUMERIC_SCORE_PATTERN = re.compile(
    r"\b(score|grade|percent|percentage|\d+\s*%|seo_score|quality_score)\b",
    re.IGNORECASE,
)

REAL_ENTITY_TERMS = [
    "donald trump",
    "joe biden",
    "google",
    "microsoft",
    "openai",
    "elon musk",
    "ukraine",
    "election 2024",
]

BAND_ID_PATTERN = re.compile(r"^PRIORITY-BAND-\d{4}$")

from public_surface_checks import (
    ALLOWED_NON_PUBLIC_HTML,
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


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def json_has_numeric_scores(data: object) -> bool:
    text = json.dumps(data).lower()
    if NUMERIC_SCORE_PATTERN.search(text):
        if "seo_score" in text and "no seo score" in text:
            return False
        if "quality_score" in text and "no quality score" in text:
            return False
        if "numeric_score" in text and "no_numeric" in text.replace("-", "_"):
            return False
        return True
    return False


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "reference-candidate-evaluation-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-candidate-evaluation-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"reference-candidate-evaluation-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_candidate_evaluation_policy":
        error("reference-candidate-evaluation-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "evaluation_only_no_drafts_no_routes_no_publication":
        error("reference-candidate-evaluation-policy.json: invalid maturity")
        ok = False

    if "Evaluation ranks readiness. It does not grant publication permission." not in data.get(
        "governing_principle", ""
    ):
        error("reference-candidate-evaluation-policy.json: governing principle missing required sentence")
        ok = False

    prohibited = " ".join(data.get("prohibited_evaluation_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"reference-candidate-evaluation-policy.json: prohibited actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"reference-candidate-evaluation-policy.json: non_authorization_rules missing {term}")
            ok = False

    if json_has_numeric_scores(data):
        error("reference-candidate-evaluation-policy.json: numeric scores or grades prohibited")
        ok = False

    return ok


def validate_priority_bands() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "reference-candidate-priority-bands.json")

    missing = BANDS_TOP - set(data.keys())
    if missing:
        error(f"reference-candidate-priority-bands.json missing fields: {sorted(missing)}")
        ok = False

    bands = data.get("priority_bands", [])
    ids = [b.get("priority_band_id") for b in bands]
    if set(ids) != set(REQUIRED_BAND_IDS):
        error("reference-candidate-priority-bands.json: required band IDs missing")
        ok = False
    for bid in ids:
        if not BAND_ID_PATTERN.match(bid or ""):
            error(f"reference-candidate-priority-bands.json: invalid band ID {bid}")
            ok = False

    names = {b.get("name") for b in bands}
    if names != set(REQUIRED_BAND_NAMES):
        error("reference-candidate-priority-bands.json: required band names missing")
        ok = False

    for band in bands:
        prohibited = band.get("prohibited_interpretation", "").lower()
        for term in ["public_release", "route_creation", "sitemap", "draft_creation", "publication"]:
            if term.replace("_", "") not in prohibited.replace("_", ""):
                error(f"reference-candidate-priority-bands.json: {band.get('priority_band_id')} missing {term}")
                ok = False
        if band.get("name") == "priority_ready_for_draft_blueprint":
            allowed = band.get("allowed_next_step", "").lower()
            if "future" not in allowed and "consideration" not in allowed:
                error("priority_ready_for_draft_blueprint must mean future consideration only")
                ok = False

    return ok


def validate_dependency_map() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "reference-candidate-dependency-map.json")

    missing = DEP_MAP_TOP - set(data.keys())
    if missing:
        error(f"reference-candidate-dependency-map.json missing fields: {sorted(missing)}")
        ok = False

    valid_ids = set(REQUIRED_CANDIDATE_IDS)
    for entry in data.get("dependencies", []):
        cid = entry.get("candidate_id")
        if cid not in valid_ids:
            error(f"dependency map: invalid candidate_id {cid}")
            ok = False
        for dep in entry.get("depends_on", []):
            if dep not in valid_ids:
                error(f"dependency map: {cid} depends_on unknown {dep}")
                ok = False
        for sup in entry.get("supports_future_candidates", []):
            if sup not in valid_ids:
                error(f"dependency map: {cid} supports unknown {sup}")
                ok = False

    return ok


def validate_evaluations() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "reference-candidate-evaluation-v1.json")
    pack_ids = {
        c.get("candidate_id")
        for c in load_json(ROOT / "data" / "reference-candidate-pack-v1.json").get("candidates", [])
    }
    band_names = {b.get("name") for b in load_json(ROOT / "data" / "reference-candidate-priority-bands.json").get("priority_bands", [])}

    missing = EVAL_TOP - set(data.keys())
    if missing:
        error(f"reference-candidate-evaluation-v1.json missing fields: {sorted(missing)}")
        ok = False

    evaluations = data.get("evaluations", [])
    if len(evaluations) != 8:
        error(f"reference-candidate-evaluation-v1.json: expected 8 evaluations, found {len(evaluations)}")
        ok = False

    eval_ids = [e.get("candidate_id") for e in evaluations]
    if set(eval_ids) != pack_ids:
        error("reference-candidate-evaluation-v1.json: evaluations must match candidate pack")
        ok = False

    if json_has_numeric_scores(data):
        error("reference-candidate-evaluation-v1.json: numeric scores, grades, or SEO scores prohibited")
        ok = False

    for ev in evaluations:
        cid = ev.get("candidate_id", "?")
        for field in EVAL_FIELDS:
            if field not in ev:
                error(f"reference-candidate-evaluation-v1.json: {cid} missing {field}")
                ok = False

        band = ev.get("primary_priority_band")
        if band not in band_names:
            error(f"reference-candidate-evaluation-v1.json: {cid} invalid primary_priority_band")
            ok = False

        readiness = ev.get("readiness_state")
        if readiness not in ALLOWED_READINESS_STATES:
            error(f"reference-candidate-evaluation-v1.json: {cid} invalid readiness_state {readiness}")
            ok = False

        blob = json.dumps(ev).lower()
        for forbidden in FORBIDDEN_ELIGIBILITY:
            if forbidden in blob and "does not authorize" not in blob:
                error(f"reference-candidate-evaluation-v1.json: {cid} contains forbidden eligibility {forbidden}")
                ok = False

        stmt = ev.get("non_authorization_statement", "").lower()
        if "does not authorize" not in stmt:
            error(f"reference-candidate-evaluation-v1.json: {cid} missing non_authorization_statement")
            ok = False
        for term in ["drafts", "routes", "sitemap", "publication"]:
            if term not in stmt:
                error(f"reference-candidate-evaluation-v1.json: {cid} non_authorization_statement incomplete")
                ok = False

        for term in REAL_ENTITY_TERMS:
            if term in blob:
                error(f"reference-candidate-evaluation-v1.json: {cid} contains real entity term")
                ok = False

    return ok


def validate_candidate_registry() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "reference-page-candidate-registry.json")
    evaluations = {
        e.get("candidate_id"): e
        for e in load_json(ROOT / "data" / "reference-candidate-evaluation-v1.json").get("evaluations", [])
    }

    from candidate_registry_checks import (
        is_batch1_production_candidate,
        is_batch2_production_candidate,
        validate_batch1_production_candidate,
        validate_batch2_production_candidate,
    )

    for entry in registry.get("candidates", []):
        cid = entry.get("candidate_id", "?")
        if is_batch1_production_candidate(entry):
            if not validate_batch1_production_candidate(entry, error, "candidate registry"):
                ok = False
            continue
        if is_batch2_production_candidate(entry):
            if not validate_batch2_production_candidate(entry, error, "candidate registry"):
                ok = False
            continue
        ev = evaluations.get(cid)
        if not ev:
            error(f"candidate registry: {cid} missing evaluation")
            ok = False
            continue

        for field, expected in [
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
        ]:
            if entry.get(field) != expected:
                error(f"candidate registry: {cid} {field} must remain {expected}")
                ok = False

        draft_status = entry.get("draft_status", "")
        if draft_status not in ("not_draft_created", "internal_draft_created"):
            error(f"candidate registry: {cid} invalid draft_status {draft_status}")
            ok = False

        if entry.get("evaluation_status") != ev.get("evaluation_status"):
            error(f"candidate registry: {cid} evaluation_status mismatch")
            ok = False
        if entry.get("primary_priority_band") != ev.get("primary_priority_band"):
            error(f"candidate registry: {cid} primary_priority_band mismatch")
            ok = False
        if entry.get("readiness_state") != ev.get("readiness_state"):
            error(f"candidate registry: {cid} readiness_state mismatch")
            ok = False
        if entry.get("evaluation_ref") != "data/reference-candidate-evaluation-v1.json":
            error(f"candidate registry: {cid} evaluation_ref missing or wrong")
            ok = False

    return ok


def validate_publisher_and_gates() -> bool:
    ok = True

    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub.get("current_publisher_status", "")
    if status not in (
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
        "blocked_until_public_reference_system_map_surface_validation",
        "blocked_until_public_reference_system_map_integrity_audit_validation",
        "blocked_until_public_reference_navigation_backbone_consolidation_validation",
    ):
        error(
            f"publisher-governance-policy: current_publisher_status must be "
            f"blocked_until_internal_draft_blueprint, blocked_until_first_internal_draft_blueprint_pack, blocked_until_first_internal_draft_pack, blocked_until_internal_draft_review_and_refinement, blocked_until_public_route_readiness_gate, or blocked_until_first_controlled_public_reference_pilot, got {status}"
        )
        ok = False
    prohibited = " ".join(pub.get("prohibited_current_outputs", [])).lower()
    if "draft_pages" not in prohibited and "content_drafts" not in prohibited:
        error("publisher-governance-policy: draft outputs must remain prohibited")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    eval_gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0018"), None)
    if not eval_gate:
        error("publisher-quality-gates: PUB-GATE-0018 missing")
        ok = False
    elif eval_gate.get("required_before_public_release") is not True or eval_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0018 must be required and not bypassable")
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "candidate_evaluation" not in checks and "reference_candidate_evaluation" not in checks:
        error("reference-expansion-gate.json: must include candidate evaluation pre-release check")
        ok = False

    return ok


def validate_route_sitemap_public_safety() -> bool:
    ok = True
    pack = load_json(ROOT / "data" / "reference-candidate-pack-v1.json")
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])

    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    sitemap_path = ROOT / "sitemap.xml"
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
        if not locs:
            locs = [el.text.strip() for el in root.findall(".//{*}loc") if el.text]
        eligible = {r.get("canonical_url") for r in routes if r.get("sitemap_included") is True}
        if set(locs) != eligible:
            error("sitemap.xml: expansion or mismatch detected")
            ok = False
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        ok = False

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_NON_PUBLIC_HTML:
            error(f"public safety: unexpected HTML file {rel}")
            ok = False

    return ok


def validate_cross_file() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry.json: missing source for {loc}")
            ok = False

    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_reference_candidate_evaluation.py" not in content:
        error("validate_all.py: must include validate_reference_candidate_evaluation.py")
        ok = False

    return ok


def main() -> int:
    checks = [
        ("evaluation policy", validate_policy),
        ("priority bands", validate_priority_bands),
        ("dependency map", validate_dependency_map),
        ("evaluations", validate_evaluations),
        ("candidate registry", validate_candidate_registry),
        ("publisher and gates", validate_publisher_and_gates),
        ("route sitemap public safety", validate_route_sitemap_public_safety),
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
