#!/usr/bin/env python3
"""Validate Hoax.ai first reference candidate pack enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from public_surface_checks import BATCH1_CANDIDATE_IDS, BATCH2_CANDIDATE_IDS, REGISTERED_CANDIDATE_ROUTE_STATUSES

ROOT = Path(__file__).resolve().parent.parent

POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "allowed_candidate_actions",
    "prohibited_candidate_actions",
    "required_candidate_fields",
    "required_candidate_gates",
    "candidate_status_rules",
    "non_authorization_rules",
    "last_reviewed",
}

PACK_TOP = {
    "candidate_pack_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "candidates",
    "last_reviewed",
}

REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "candidates",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "FIRST_REFERENCE_CANDIDATE_PACK.md",
    "data/reference-candidate-pack-policy.json",
    "data/reference-candidate-pack-v1.json",
    "validators/validate_reference_candidate_pack.py",
]

REQUIRED_CANDIDATE_IDS = [f"REF-CAND-{i:04d}" for i in range(1, 9)]

REQUIRED_CANDIDATE_FIELDS = [
    "candidate_id",
    "candidate_name",
    "candidate_status",
    "page_family",
    "page_type_ref",
    "candidate_slug",
    "proposed_path",
    "route_status",
    "sitemap_status",
    "draft_status",
    "publication_status",
    "reference_thesis",
    "reference_purpose",
    "definition_scope_summary",
    "governance_boundary_summary",
    "system_relationships",
    "claim_scope",
    "source_scope",
    "semantic_seo_role",
    "prohibited_misreadings",
    "required_sections",
    "required_gates",
    "related_existing_governance_files",
    "future_internal_link_targets",
    "forbidden_public_implications",
    "review_status",
    "notes",
]

REQUIRED_GATES = [
    "PUB-GATE-0002",
    "PUB-GATE-0003",
    "PUB-GATE-0004",
    "PUB-GATE-0005",
    "PUB-GATE-0015",
    "PUB-GATE-0006",
    "PUB-GATE-0007",
    "PUB-GATE-0008",
    "PUB-GATE-0009",
    "PUB-GATE-0010",
    "PUB-GATE-0016",
    "PUB-GATE-0012",
    "PUB-GATE-0013",
    "PUB-GATE-0014",
]

REQUIRED_SECTIONS = [f"REF-SECTION-{i:04d}" for i in range(1, 10)]

PROHIBITED_ACTIONS = [
    "public_pages",
    "draft_pages",
    "route_creation",
    "sitemap",
    "public_navigation",
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

SEO_PROHIBITED = [
    "keyword stuffing",
    "scan now",
    "upload your",
    "truth score",
    "fake score",
    "public classifier",
    "live classifier",
    "softwareapplication",
    "software application",
    "api reference",
    "world's first",
    "industry-leading",
]

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

CANDIDATE_ID_PATTERN = re.compile(r"^REF-CAND-\d{4}$")

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


def candidate_text_blob(candidate: dict) -> str:
    fields = [
        "candidate_name",
        "reference_thesis",
        "reference_purpose",
        "definition_scope_summary",
        "governance_boundary_summary",
        "claim_scope",
        "source_scope",
        "semantic_seo_role",
        "notes",
    ]
    blob = " ".join(str(candidate.get(f, "")) for f in fields).lower()
    blob += " " + " ".join(str(x) for x in candidate.get("prohibited_misreadings", [])).lower()
    return blob


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "reference-candidate-pack-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-candidate-pack-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"reference-candidate-pack-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_candidate_pack_policy":
        error("reference-candidate-pack-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "candidates_only_no_drafts_no_routes_no_publication":
        error("reference-candidate-pack-policy.json: invalid maturity")
        ok = False

    principle = data.get("governing_principle", "")
    if "A candidate is not a page" not in principle:
        error("reference-candidate-pack-policy.json: governing principle missing required sentence")
        ok = False

    prohibited = " ".join(data.get("prohibited_candidate_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"reference-candidate-pack-policy.json: prohibited_candidate_actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"reference-candidate-pack-policy.json: non_authorization_rules missing {term}")
            ok = False

    return ok


def validate_candidate_pack() -> bool:
    ok = True
    path = ROOT / "data" / "reference-candidate-pack-v1.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-candidate-pack-v1.json parse failed: {exc}")
        return False

    missing = PACK_TOP - set(data.keys())
    if missing:
        error(f"reference-candidate-pack-v1.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_candidate_pack":
        error("reference-candidate-pack-v1.json: invalid status")
        ok = False

    page_types = {
        pt.get("page_type_id")
        for pt in load_json(ROOT / "data" / "reference-page-type-registry.json").get("page_types", [])
    }
    section_ids = {
        s.get("section_id")
        for s in load_json(ROOT / "data" / "reference-section-requirements.json").get("required_sections", [])
    }

    candidates = data.get("candidates", [])
    if not (6 <= len(candidates) <= 8):
        error(f"reference-candidate-pack-v1.json: expected 6-8 candidates, found {len(candidates)}")
        ok = False

    ids = [c.get("candidate_id") for c in candidates]
    if len(ids) != len(set(ids)):
        error("reference-candidate-pack-v1.json: duplicate candidate_id")
        ok = False
    for cid in ids:
        if not CANDIDATE_ID_PATTERN.match(cid or ""):
            error(f"reference-candidate-pack-v1.json: invalid candidate_id {cid}")
            ok = False
    if set(ids) != set(REQUIRED_CANDIDATE_IDS):
        error(f"reference-candidate-pack-v1.json: expected IDs {REQUIRED_CANDIDATE_IDS}")
        ok = False

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    route_paths = {r.get("path", r.get("canonical_url", "")) for r in routes}

    for candidate in candidates:
        cid = candidate.get("candidate_id", "?")
        for field in REQUIRED_CANDIDATE_FIELDS:
            if field not in candidate:
                error(f"reference-candidate-pack-v1.json: {cid} missing field {field}")
                ok = False

        if cid in BATCH1_CANDIDATE_IDS:
            if candidate.get("route_status") != "public_reference_production_batch_1_route_created":
                error(f"reference-candidate-pack-v1.json: {cid} route_status must be public_reference_production_batch_1_route_created")
                ok = False
            if candidate.get("sitemap_status") != "sitemap_eligible":
                error(f"reference-candidate-pack-v1.json: {cid} sitemap_status must be sitemap_eligible")
                ok = False
            if candidate.get("draft_status") != "production_page_created":
                error(f"reference-candidate-pack-v1.json: {cid} draft_status must be production_page_created")
                ok = False
            if candidate.get("publication_status") != "public_reference_production_batch_1":
                error(f"reference-candidate-pack-v1.json: {cid} publication_status must be public_reference_production_batch_1")
                ok = False
        elif cid in BATCH2_CANDIDATE_IDS:
            if candidate.get("route_status") != "public_reference_production_batch_2_route_created":
                error(f"reference-candidate-pack-v1.json: {cid} route_status must be public_reference_production_batch_2_route_created")
                ok = False
            if candidate.get("sitemap_status") != "sitemap_eligible":
                error(f"reference-candidate-pack-v1.json: {cid} sitemap_status must be sitemap_eligible")
                ok = False
            if candidate.get("draft_status") != "production_page_created":
                error(f"reference-candidate-pack-v1.json: {cid} draft_status must be production_page_created")
                ok = False
            if candidate.get("publication_status") != "public_reference_production_batch_2":
                error(f"reference-candidate-pack-v1.json: {cid} publication_status must be public_reference_production_batch_2")
                ok = False
        else:
            if candidate.get("route_status") != "not_route_created":
                error(f"reference-candidate-pack-v1.json: {cid} route_status must be not_route_created")
                ok = False
            if candidate.get("sitemap_status") != "not_sitemap_eligible":
                error(f"reference-candidate-pack-v1.json: {cid} sitemap_status must be not_sitemap_eligible")
                ok = False
            if candidate.get("draft_status") != "not_draft_created":
                error(f"reference-candidate-pack-v1.json: {cid} draft_status must be not_draft_created")
                ok = False
            if candidate.get("publication_status") != "publication_blocked":
                error(f"reference-candidate-pack-v1.json: {cid} publication_status must be publication_blocked")
                ok = False

        if candidate.get("candidate_status") not in ("candidate_registered", "proposed_internal"):
            error(f"reference-candidate-pack-v1.json: {cid} invalid candidate_status")
            ok = False

        if candidate.get("page_type_ref") not in page_types:
            error(f"reference-candidate-pack-v1.json: {cid} invalid page_type_ref")
            ok = False

        sections = candidate.get("required_sections", [])
        if not all(s in section_ids for s in sections):
            error(f"reference-candidate-pack-v1.json: {cid} required_sections invalid")
            ok = False
        if not all(s in sections for s in REQUIRED_SECTIONS):
            error(f"reference-candidate-pack-v1.json: {cid} missing core required sections")
            ok = False

        gates = set(candidate.get("required_gates", []))
        if not all(g in gates for g in REQUIRED_GATES):
            error(f"reference-candidate-pack-v1.json: {cid} missing required gates")
            ok = False

        blob = " ".join(
            str(candidate.get(f, ""))
            for f in ["reference_thesis", "reference_purpose", "semantic_seo_role", "definition_scope_summary"]
        ).lower()
        for term in REAL_ENTITY_TERMS:
            full_blob = candidate_text_blob(candidate)
            if term in full_blob:
                error(f"reference-candidate-pack-v1.json: {cid} contains real entity term '{term}'")
                ok = False
        for term in SEO_PROHIBITED:
            if term not in blob:
                continue
            if term == "keyword stuffing" and "no keyword stuffing" in blob:
                continue
            prefix = blob[max(0, blob.find(term) - 30) : blob.find(term)]
            if any(m in prefix for m in ["no ", "not ", "without ", "exclude"]):
                continue
            error(f"reference-candidate-pack-v1.json: {cid} prohibited SEO/capability term '{term}' in candidate content")
            ok = False

        proposed = candidate.get("proposed_path", "")
        route_match = next((r for r in routes if r.get("path") == proposed), None)

        if route_match and route_match.get("status") not in REGISTERED_CANDIDATE_ROUTE_STATUSES:
            error(f"reference-candidate-pack-v1.json: {cid} proposed_path must not be in route registry")
            ok = False

        for gov_file in candidate.get("related_existing_governance_files", []):
            if not (ROOT / gov_file).exists():
                error(f"reference-candidate-pack-v1.json: {cid} missing governance file {gov_file}")
                ok = False

    return ok


def validate_candidate_registry() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "reference-page-candidate-registry.json")
    pack = load_json(ROOT / "data" / "reference-candidate-pack-v1.json")

    missing = REGISTRY_TOP - set(registry.keys())
    if missing and missing != {"candidate_pack_id", "candidate_pack_source"}:
        extra_allowed = {"candidate_pack_id", "candidate_pack_source"}
        real_missing = missing - extra_allowed
        if real_missing:
            error(f"reference-page-candidate-registry.json missing fields: {sorted(real_missing)}")
            ok = False

    reg_candidates = registry.get("candidates", [])
    if not reg_candidates:
        error("reference-page-candidate-registry.json: candidates must not be empty after Sprint 17")
        ok = False

    pack_ids = {c.get("candidate_id") for c in pack.get("candidates", [])}
    reg_ids = {c.get("candidate_id") for c in reg_candidates}
    if reg_ids != pack_ids:
        error("reference-page-candidate-registry.json: registry IDs must match candidate pack")
        ok = False

    for entry in reg_candidates:
        cid = entry.get("candidate_id", "?")
        if cid in BATCH1_CANDIDATE_IDS:
            if entry.get("publication_status") != "public_reference_production_batch_1":
                error(f"candidate registry: {cid} must be public_reference_production_batch_1")
                ok = False
            if entry.get("route_status") != "public_reference_production_batch_1_route_created":
                error(f"candidate registry: {cid} must be public_reference_production_batch_1_route_created")
                ok = False
            continue
        if cid in BATCH2_CANDIDATE_IDS:
            if entry.get("publication_status") != "public_reference_production_batch_2":
                error(f"candidate registry: {cid} must be public_reference_production_batch_2")
                ok = False
            if entry.get("route_status") != "public_reference_production_batch_2_route_created":
                error(f"candidate registry: {cid} must be public_reference_production_batch_2_route_created")
                ok = False
            continue
        if entry.get("publication_status") != "publication_blocked":
            error(f"candidate registry: {cid} must be publication_blocked")
            ok = False
        if entry.get("route_status") != "not_route_created":
            error(f"candidate registry: {cid} must be not_route_created")
            ok = False
        if entry.get("pack_reference") != "data/reference-candidate-pack-v1.json":
            error(f"candidate registry: {cid} must reference candidate pack file")
            ok = False

    return ok


def validate_publisher_queues() -> bool:
    ok = True
    queues = load_json(ROOT / "data" / "publisher-queue-registry.json").get("queues", [])
    for queue in queues:
        if queue.get("items"):
            error(f"publisher-queue-registry: {queue.get('queue_id')} must remain empty in Sprint 17")
            ok = False
    return ok


def validate_route_sitemap_safety() -> bool:
    ok = True
    pack = load_json(ROOT / "data" / "reference-candidate-pack-v1.json")
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])

    from public_surface_checks import ALLOWED_PUBLIC_ROOT_FILES, BATCH1_CANDIDATE_IDS, BATCH2_CANDIDATE_IDS, validate_pilot_route_registry

    if not validate_pilot_route_registry(routes, error):
        ok = False

    registered_paths = {r.get("path") for r in routes}
    for candidate in pack.get("candidates", []):
        proposed = candidate.get("proposed_path", "")
        cid = candidate.get("candidate_id", "")
        route_match = next((r for r in routes if r.get("path") == proposed), None)
        if route_match and route_match.get("status") not in REGISTERED_CANDIDATE_ROUTE_STATUSES:
            error(f"route safety: candidate {cid} proposed_path in route registry")
            ok = False
        if cid in ("REF-CAND-0001", "REF-CAND-0002", *BATCH1_CANDIDATE_IDS, *BATCH2_CANDIDATE_IDS):
            continue
        candidate_dir = ROOT / proposed.strip("/") if proposed else None
        if candidate_dir and candidate_dir.exists():
            error(f"route safety: candidate path directory exists: {proposed}")
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
        for candidate in pack.get("candidates", []):
            if candidate.get("candidate_id") in ("REF-CAND-0001", "REF-CAND-0002"):
                continue
            prop = candidate.get("proposed_path", "").rstrip("/") + "/"
            for loc in locs:
                if candidate.get("candidate_slug", "") in loc and loc not in eligible:
                    error(f"sitemap.xml: candidate path appears in sitemap: {loc}")
                    ok = False
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        ok = False

    return ok


def validate_public_safety() -> bool:
    ok = True

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_NON_PUBLIC_HTML:
            error(f"public safety: unexpected HTML file {rel}")
            ok = False

    return ok


def validate_cross_file() -> bool:
    ok = True

    pub_policy = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub_policy.get("current_publisher_status", "")
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
    ):
        error(
            "publisher-governance-policy: current_publisher_status must be "
            "blocked_until_internal_draft_blueprint, blocked_until_first_internal_draft_blueprint_pack, blocked_until_first_internal_draft_pack, blocked_until_internal_draft_review_and_refinement, blocked_until_public_route_readiness_gate, or blocked_until_first_controlled_public_reference_pilot"
        )
        ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "candidate_pack" not in checks and "reference_candidate" not in checks:
        error("reference-expansion-gate.json: must include candidate pack pre-release check")
        ok = False
    if "candidate_evaluation" not in checks and "reference_candidate_evaluation" not in checks:
        error("reference-expansion-gate.json: must include candidate evaluation pre-release check")
        ok = False

    pub_gate = load_json(ROOT / "data" / "publisher-quality-gates.json")
    cp_gate = next((g for g in pub_gate.get("gates", []) if g.get("gate_id") == "PUB-GATE-0017"), None)
    if not cp_gate:
        error("publisher-quality-gates: PUB-GATE-0017 missing")
        ok = False
    elif cp_gate.get("required_before_public_release") is not True or cp_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0017 must be required and not bypassable")
        ok = False

    eval_gate = next((g for g in pub_gate.get("gates", []) if g.get("gate_id") == "PUB-GATE-0018"), None)
    if not eval_gate:
        error("publisher-quality-gates: PUB-GATE-0018 missing")
        ok = False
    elif eval_gate.get("required_before_public_release") is not True or eval_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0018 must be required and not bypassable")
        ok = False

    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry.json: missing source for {loc}")
            ok = False

    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_reference_candidate_pack.py" not in content:
        error("validate_all.py: must include validate_reference_candidate_pack.py")
        ok = False

    return ok


def main() -> int:
    checks = [
        ("candidate pack policy", validate_policy),
        ("candidate pack", validate_candidate_pack),
        ("candidate registry", validate_candidate_registry),
        ("publisher queues", validate_publisher_queues),
        ("route and sitemap safety", validate_route_sitemap_safety),
        ("public safety", validate_public_safety),
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
