#!/usr/bin/env python3
"""Validate Hoax.ai internal draft blueprint governance enforcement."""

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
    "structure_principle",
    "internal_draft_definition",
    "draft_blueprint_definition",
    "allowed_blueprint_actions",
    "prohibited_blueprint_actions",
    "required_blueprint_fields",
    "required_future_draft_sections",
    "candidate_eligibility_rules",
    "non_authorization_rules",
    "last_reviewed",
}

TEMPLATE_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "templates",
    "last_reviewed",
}

CONTRACTS_TOP = {
    "contract_set_id",
    "name",
    "version",
    "status",
    "maturity",
    "section_contracts",
    "last_reviewed",
}

STATE_MACHINE_TOP = {
    "state_machine_id",
    "name",
    "version",
    "status",
    "maturity",
    "states",
    "allowed_transitions",
    "blocked_transitions",
    "terminal_states",
    "current_system_state",
    "last_reviewed",
}

GATES_TOP = {
    "gate_set_id",
    "name",
    "version",
    "status",
    "maturity",
    "gates",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "INTERNAL_DRAFT_BLUEPRINT_GOVERNANCE.md",
    "data/internal-draft-blueprint-policy.json",
    "data/internal-draft-template-registry.json",
    "data/internal-draft-section-contracts.json",
    "data/internal-draft-state-machine.json",
    "data/internal-draft-readiness-gates.json",
    "validators/validate_internal_draft_blueprint_governance.py",
]

REQUIRED_TEMPLATE_IDS = [f"DRAFT-TEMPLATE-{i:04d}" for i in range(1, 8)]

REQUIRED_SECTION_IDS = [f"DRAFT-SECTION-{i:04d}" for i in range(1, 18)]

REQUIRED_DRAFT_GATE_IDS = [f"DRAFT-GATE-{i:04d}" for i in range(1, 18)]

REQUIRED_BLUEPRINT_STATES = {
    "blueprint_not_created",
    "blueprint_required",
    "blueprint_created_internal",
    "blueprint_validation_pending",
    "blueprint_validated",
    "ready_for_future_internal_draft_pack",
    "blocked_needs_candidate_refinement",
    "blocked_needs_claim_scope",
    "blocked_needs_source_scope",
    "blocked_needs_boundary_refinement",
    "retired",
}

PROHIBITED_STATES = {
    "draft_created",
    "public_page_created",
    "route_active",
    "sitemap_eligible",
    "publication_allowed",
    "release_eligible",
    "deployed",
}

ELIGIBLE_READINESS_STATES = {"draft_blueprint_candidate", "dependency_candidate"}

INELIGIBLE_READINESS_STATES = {"needs_boundary_refinement"}

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

PROHIBITED_SECTION_CONTENT = [
    "tool",
    "detector",
    "upload",
    "scoring",
    "fake",
    "verdict",
    "accusation",
    "unsupported",
]

NUMERIC_SCORE_PATTERN = re.compile(
    r"\b(score|grade|percent|percentage|\d+\s*%|seo_score|quality_score)\b",
    re.IGNORECASE,
)

TEMPLATE_ID_PATTERN = re.compile(r"^DRAFT-TEMPLATE-\d{4}$")
SECTION_ID_PATTERN = re.compile(r"^DRAFT-SECTION-\d{4}$")
DRAFT_GATE_ID_PATTERN = re.compile(r"^DRAFT-GATE-\d{4}$")

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

DRAFT_PATH_CANDIDATES = [
    ROOT / "internal" / "drafts",
    ROOT / "governance" / "drafts",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def json_has_numeric_scores(data: object) -> bool:
    text = json.dumps(data).lower()
    if NUMERIC_SCORE_PATTERN.search(text):
        if "no_numeric" in text.replace("-", "_"):
            return False
        if "seo_score" in text and "no seo score" in text:
            return False
        if "quality_score" in text and "no quality score" in text:
            return False
        return True
    return False


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "internal-draft-blueprint-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"internal-draft-blueprint-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-blueprint-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_draft_blueprint_policy":
        error("internal-draft-blueprint-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "blueprint_governance_only_no_drafts_no_routes_no_publication":
        error("internal-draft-blueprint-policy.json: invalid maturity")
        ok = False

    prohibited = " ".join(data.get("prohibited_blueprint_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"internal-draft-blueprint-policy.json: prohibited_blueprint_actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"internal-draft-blueprint-policy.json: non_authorization_rules missing {term}")
            ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-blueprint-policy.json: numeric scores or grades prohibited")
        ok = False

    return ok


def validate_template_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-template-registry.json")

    missing = TEMPLATE_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-template-registry.json missing fields: {sorted(missing)}")
        ok = False

    page_types = {
        pt.get("page_type_id")
        for pt in load_json(ROOT / "data" / "reference-page-type-registry.json").get("page_types", [])
    }

    templates = data.get("templates", [])
    ids = [t.get("template_id") for t in templates]
    if set(ids) != set(REQUIRED_TEMPLATE_IDS):
        error("internal-draft-template-registry.json: required template IDs missing")
        ok = False

    for template in templates:
        tid = template.get("template_id", "")
        if not TEMPLATE_ID_PATTERN.match(tid):
            error(f"internal-draft-template-registry.json: invalid template_id {tid}")
            ok = False

        notes = (template.get("notes", "") + " " + template.get("prohibited_content", "")).lower()
        if "does not authorize draft creation" not in notes:
            error(f"internal-draft-template-registry.json: {tid} must state it does not authorize draft creation")
            ok = False
        for term in ["public page", "route creation", "sitemap", "publication"]:
            if term.replace("_", "") not in notes.replace("_", ""):
                error(f"internal-draft-template-registry.json: {tid} missing prohibited {term}")
                ok = False

        for ref in template.get("applies_to_page_type_refs", []):
            if ref not in page_types:
                error(f"internal-draft-template-registry.json: {tid} references unknown page type {ref}")
                ok = False

    return ok


def validate_section_contracts() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-section-contracts.json")

    missing = CONTRACTS_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-section-contracts.json missing fields: {sorted(missing)}")
        ok = False

    contracts = data.get("section_contracts", [])
    ids = [c.get("section_contract_id") for c in contracts]
    if set(ids) != set(REQUIRED_SECTION_IDS):
        error("internal-draft-section-contracts.json: required section contract IDs missing")
        ok = False

    for contract in contracts:
        cid = contract.get("section_contract_id", "")
        if not SECTION_ID_PATTERN.match(cid):
            error(f"internal-draft-section-contracts.json: invalid section_contract_id {cid}")
            ok = False

        prohibited = contract.get("prohibited_content", "").lower()
        validation = contract.get("validation_notes", "").lower()
        if "does not authorize public release" not in validation:
            error(f"internal-draft-section-contracts.json: {cid} must not authorize public release")
            ok = False

        if cid in REQUIRED_SECTION_IDS[:10]:
            matches = sum(1 for term in PROHIBITED_SECTION_CONTENT if term in prohibited)
            if matches < 4:
                error(
                    f"internal-draft-section-contracts.json: {cid} prohibited_content "
                    f"insufficient (need tool/detector/upload/scoring/fake/verdict/accusation/unsupported)"
                )
                ok = False

    return ok


def validate_state_machine() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-state-machine.json")

    missing = STATE_MACHINE_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-state-machine.json missing fields: {sorted(missing)}")
        ok = False

    current = data.get("current_system_state", "")
    if current not in ("blueprint_governance_defined_no_drafts", "blueprint_governance_defined"):
        error(
            f"internal-draft-state-machine.json: current_system_state must be "
            f"blueprint_governance_defined_no_drafts, got {current}"
        )
        ok = False

    states = set(data.get("states", []))
    if not REQUIRED_BLUEPRINT_STATES.issubset(states):
        error("internal-draft-state-machine.json: missing required blueprint states")
        ok = False
    if states & PROHIBITED_STATES:
        error("internal-draft-state-machine.json: prohibited states must not be in states list")
        ok = False

    for transition in data.get("allowed_transitions", []):
        to_state = transition.get("to", "")
        if to_state in PROHIBITED_STATES or to_state == "draft_created":
            error(f"internal-draft-state-machine.json: allowed transition to prohibited state {to_state}")
            ok = False

    ready = next((s for s in states if s == "ready_for_future_internal_draft_pack"), None)
    if not ready:
        error("internal-draft-state-machine.json: ready_for_future_internal_draft_pack state missing")
        ok = False

    blocked = " ".join(
        f"{b.get('from', '')} {b.get('to', '')} {b.get('reason', '')}"
        for b in data.get("blocked_transitions", [])
    ).lower()
    if "draft_created" not in blocked:
        error("internal-draft-state-machine.json: must block draft_created transitions")
        ok = False

    return ok


def validate_readiness_gates() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-readiness-gates.json")

    missing = GATES_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-readiness-gates.json missing fields: {sorted(missing)}")
        ok = False

    gates = data.get("gates", [])
    ids = [g.get("gate_id") for g in gates]
    if set(ids) != set(REQUIRED_DRAFT_GATE_IDS):
        error("internal-draft-readiness-gates.json: required gate IDs missing")
        ok = False

    required_gate_names = {
        "DRAFT-GATE-0015": "validate_all",
        "DRAFT-GATE-0016": "audit",
        "DRAFT-GATE-0017": "approval",
    }

    for gate in gates:
        gid = gate.get("gate_id", "")
        if not DRAFT_GATE_ID_PATTERN.match(gid):
            error(f"internal-draft-readiness-gates.json: invalid gate_id {gid}")
            ok = False

        notes = gate.get("notes", "").lower()
        if "does not authorize draft creation" not in notes:
            error(f"internal-draft-readiness-gates.json: {gid} must not authorize draft creation by itself")
            ok = False
        if "does not authorize" not in notes or "public release" not in notes:
            error(f"internal-draft-readiness-gates.json: {gid} must not authorize public release by itself")
            ok = False

        if gate.get("required_before_future_internal_draft") is not True:
            error(f"internal-draft-readiness-gates.json: {gid} must be required before future internal draft")
            ok = False

        if gid in required_gate_names:
            blob = (gate.get("name", "") + " " + gate.get("validation_source", "")).lower()
            if required_gate_names[gid] not in blob:
                error(f"internal-draft-readiness-gates.json: {gid} missing {required_gate_names[gid]} reference")
                ok = False

    return ok


def validate_candidate_eligibility() -> bool:
    ok = True
    evaluations = load_json(ROOT / "data" / "reference-candidate-evaluation-v1.json").get("evaluations", [])

    eligible = [
        e.get("candidate_id")
        for e in evaluations
        if e.get("readiness_state") in ELIGIBLE_READINESS_STATES
    ]
    ineligible = [
        e.get("candidate_id")
        for e in evaluations
        if e.get("readiness_state") in INELIGIBLE_READINESS_STATES
    ]

    if len(eligible) < 1:
        error("candidate eligibility: no draft_blueprint_candidate or dependency_candidate found")
        ok = False

    if "REF-CAND-0008" not in ineligible:
        error("candidate eligibility: REF-CAND-0008 must be needs_boundary_refinement and ineligible")
        ok = False

    policy = load_json(ROOT / "data" / "internal-draft-blueprint-policy.json")
    rules = " ".join(policy.get("candidate_eligibility_rules", [])).lower()
    if "needs_boundary_refinement" not in rules:
        error("internal-draft-blueprint-policy.json: must block needs_boundary_refinement candidates")
        ok = False
    if "noeligibilityauthorizesdraft" not in rules.replace("_", ""):
        error("internal-draft-blueprint-policy.json: must state eligibility does not authorize drafts")
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
    ):
        error(
            f"publisher-governance-policy: current_publisher_status must be "
            f"blocked_until_first_internal_draft_blueprint_pack, blocked_until_first_internal_draft_pack, blocked_until_internal_draft_review_and_refinement, blocked_until_public_route_readiness_gate, or blocked_until_first_controlled_public_reference_pilot, got {status}"
        )
        ok = False

    allowed = " ".join(pub.get("allowed_current_outputs", [])).lower()
    if "content_drafts" in " ".join(pub.get("prohibited_current_outputs", [])).lower():
        pass
    elif "draft_pages" not in " ".join(pub.get("prohibited_current_outputs", [])).lower():
        error("publisher-governance-policy: draft_pages must remain prohibited")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    bp_gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0019"), None)
    if not bp_gate:
        error("publisher-quality-gates: PUB-GATE-0019 missing")
        ok = False
    elif bp_gate.get("required_before_public_release") is not True or bp_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0019 must be required and not bypassable")
        ok = False
    else:
        notes = bp_gate.get("notes", "").lower()
        if "does not authorize" not in notes:
            error("publisher-quality-gates: PUB-GATE-0019 must not authorize outputs by itself")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "draft_blueprint" not in checks and "internal_draft_blueprint" not in checks:
        error("reference-expansion-gate.json: must include internal draft blueprint governance pre-release check")
        ok = False

    return ok


def validate_route_sitemap_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])

    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    from public_surface_checks import validate_pilot_sitemap
    try:
        if not validate_pilot_sitemap(routes, error):
            ok = False
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        ok = False

    for draft_dir in DRAFT_PATH_CANDIDATES:
        if draft_dir.exists():
            for item in draft_dir.rglob("*"):
                if item.is_file() and item.suffix in {".md", ".html", ".json"}:
                    error(f"public safety: draft file exists at {item.relative_to(ROOT)}")
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
    if "validate_internal_draft_blueprint_governance.py" not in content:
        error("validate_all.py: must include validate_internal_draft_blueprint_governance.py")
        ok = False

    return ok


def main() -> int:
    parse_paths = [
        "data/internal-draft-blueprint-policy.json",
        "data/internal-draft-template-registry.json",
        "data/internal-draft-section-contracts.json",
        "data/internal-draft-state-machine.json",
        "data/internal-draft-readiness-gates.json",
        "data/reference-candidate-evaluation-v1.json",
        "data/reference-page-candidate-registry.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
    ]
    for rel in parse_paths:
        try:
            load_json(ROOT / rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"{rel} parse failed: {exc}")
            return 1

    sitemap_path = ROOT / "sitemap.xml"
    try:
        ET.parse(sitemap_path)
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    checks = [
        ("blueprint policy", validate_policy),
        ("template registry", validate_template_registry),
        ("section contracts", validate_section_contracts),
        ("state machine", validate_state_machine),
        ("readiness gates", validate_readiness_gates),
        ("candidate eligibility", validate_candidate_eligibility),
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
