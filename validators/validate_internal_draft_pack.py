#!/usr/bin/env python3
"""Validate Hoax.ai first internal draft pack enforcement."""

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
    "discipline_principle",
    "allowed_internal_draft_actions",
    "prohibited_internal_draft_actions",
    "required_draft_fields",
    "required_draft_sections",
    "required_status_values",
    "draft_location_policy",
    "non_authorization_rules",
    "last_reviewed",
}

PACK_TOP = {
    "draft_pack_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "selected_blueprints",
    "drafts",
    "last_reviewed",
}

REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "draft_records",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "FIRST_INTERNAL_DRAFT_PACK.md",
    "data/internal-draft-pack-policy.json",
    "data/internal-draft-pack-v1.json",
    "data/internal-draft-registry.json",
    "_internal_drafts/reference/evidence-posture.md",
    "_internal_drafts/reference/artifact-subject-separation.md",
    "validators/validate_internal_draft_pack.py",
]

REQUIRED_DRAFT_IDS = ["DRAFT-0001", "DRAFT-0002"]

REQUIRED_BLUEPRINT_IDS = ["DRAFT-BLUEPRINT-0001", "DRAFT-BLUEPRINT-0002"]

REQUIRED_CANDIDATE_IDS = ["REF-CAND-0001", "REF-CAND-0002"]

EXPECTED_DRAFT_FILES = [
    ROOT / "_internal_drafts" / "reference" / "evidence-posture.md",
    ROOT / "_internal_drafts" / "reference" / "artifact-subject-separation.md",
]

DRAFT_FIELDS = [
    "draft_id",
    "candidate_id",
    "candidate_name",
    "blueprint_id",
    "draft_file_path",
    "draft_status",
    "route_status",
    "sitemap_status",
    "publication_status",
    "public_metadata_status",
    "public_navigation_status",
    "deployment_status",
    "page_family",
    "page_type_ref",
    "template_ref",
    "reference_thesis",
    "claim_scope",
    "source_scope",
    "semantic_seo_role",
    "required_sections",
    "required_gates",
    "non_authorization_statement",
    "review_status",
    "notes",
]

REQUIRED_SECTION_HEADERS = [
    "Draft Status Block",
    "Draft Thesis",
    "Definition and Scope",
    "Governance Boundary",
    "Relationship to Hoax.ai System",
    "Semantic SEO Role",
    "Claim and Source Traceability",
    "Prohibited Misreadings",
    "Internal Link Plan",
    "Structured Data Boundary",
    "Review Status",
    "Non-Authorization Statement",
]

STATUS_BLOCK_FIELDS = [
    "draft_id",
    "candidate_id",
    "blueprint_id",
    "draft_status",
    "route_status",
    "sitemap_status",
    "publication_status",
    "public_metadata_status",
    "public_navigation_status",
    "deployment_status",
    "review_status",
    "non_authorization_statement",
]

PROHIBITED_ACTIONS = [
    "public_page",
    "route_activation",
    "sitemap",
    "public_metadata",
    "public_navigation",
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
    "routes",
    "sitemap",
    "public_pages",
    "public_metadata",
    "publishing",
    "deployment",
    "seo_expansion",
]

FORBIDDEN_IMPLICATIONS = [
    "active detector",
    "fake/real",
    "fake-or-real",
    "upload workflow",
    "public classifier",
    "software product",
    "unsupported authority",
]

PUBLIC_METADATA_TERMS = [
    "public_title:",
    "meta_description:",
    "public_canonical:",
    "og:title",
    "twitter:card",
    '"@type":',
]

PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|FIXME|placeholder|lorem ipsum)\b", re.IGNORECASE)

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

NUMERIC_SCORE_PATTERN = re.compile(
    r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b",
    re.IGNORECASE,
)

DRAFT_ID_PATTERN = re.compile(r"^DRAFT-\d{4}$")

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

MIN_WORDS = 900
MAX_WORDS = 1400


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def json_has_numeric_scores(data: object) -> bool:
    text = json.dumps(data).lower()
    if NUMERIC_SCORE_PATTERN.search(text):
        if "no_numeric" in text.replace("-", "_"):
            return False
        return True
    return False


def has_forbidden_implication(text: str) -> bool:
    lower = text.lower()
    for term in FORBIDDEN_IMPLICATIONS:
        if term in lower:
            # Allow negation / prohibition context
            idx = lower.find(term)
            window = lower[max(0, idx - 40) : idx + len(term) + 40]
            if any(n in window for n in ["not ", "no ", "without ", "prohibit", "exclude", "must not", "does not"]):
                continue
            return True
    if re.search(r"\bfake\b.*\breal\b", lower) or re.search(r"\breal\b.*\bfake\b", lower):
        if "not " in lower or "no " in lower:
            return False
        return True
    if " scoring" in lower or lower.startswith("scoring"):
        if "no " in lower or "not " in lower or "exclude" in lower:
            return False
        return True
    if re.search(r"\bapi availability\b", lower) and "no " not in lower:
        return True
    return False


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "internal-draft-pack-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"internal-draft-pack-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-pack-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_draft_pack_policy":
        error("internal-draft-pack-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "internal_drafts_only_no_routes_no_sitemap_no_publication":
        error("internal-draft-pack-policy.json: invalid maturity")
        ok = False

    if "_internal_drafts/reference/" not in data.get("draft_location_policy", ""):
        error("internal-draft-pack-policy.json: draft_location_policy must require _internal_drafts/reference/")
        ok = False

    prohibited = " ".join(data.get("prohibited_internal_draft_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"internal-draft-pack-policy.json: prohibited actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"internal-draft-pack-policy.json: non_authorization_rules missing {term}")
            ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-pack-policy.json: numeric scores prohibited")
        ok = False

    return ok


def validate_draft_pack() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-pack-v1.json")
    blueprints = {
        b.get("blueprint_id"): b
        for b in load_json(ROOT / "data" / "internal-draft-blueprint-pack-v1.json").get("blueprints", [])
    }

    missing = PACK_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-pack-v1.json missing fields: {sorted(missing)}")
        ok = False

    drafts = data.get("drafts", [])
    if len(drafts) != 2:
        error("internal-draft-pack-v1.json: exactly 2 draft records required")
        ok = False

    if set(data.get("selected_blueprints", [])) != set(REQUIRED_BLUEPRINT_IDS):
        error("internal-draft-pack-v1.json: selected blueprints must be 0001 and 0002")
        ok = False

    ids = [d.get("draft_id") for d in drafts]
    if set(ids) != set(REQUIRED_DRAFT_IDS):
        error("internal-draft-pack-v1.json: required draft IDs missing")
        ok = False

    for draft in drafts:
        did = draft.get("draft_id", "?")
        if not DRAFT_ID_PATTERN.match(did):
            error(f"draft pack: invalid draft_id {did}")
            ok = False

        bid = draft.get("blueprint_id", "")
        if bid not in blueprints:
            error(f"draft pack: {did} references unknown blueprint {bid}")
            ok = False

        for field in DRAFT_FIELDS:
            if field not in draft:
                error(f"draft pack: {did} missing field {field}")
                ok = False

        for field, expected in [
            ("draft_status", "internal_draft_created"),
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
            ("public_metadata_status", "not_created"),
            ("public_navigation_status", "not_linked"),
            ("deployment_status", "not_deployed"),
        ]:
            if draft.get(field) != expected:
                error(f"draft pack: {did} {field} must be {expected}")
                ok = False

        path = draft.get("draft_file_path", "")
        if not path.startswith("_internal_drafts/reference/"):
            error(f"draft pack: {did} draft_file_path must begin with _internal_drafts/reference/")
            ok = False

        blob = json.dumps(draft).lower()
        for term in PUBLIC_METADATA_TERMS:
            if term in blob:
                error(f"draft pack: {did} contains public metadata term {term}")
                ok = False

        if has_forbidden_implication(blob):
            error(f"draft pack: {did} forbidden implication in record")
            ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-pack-v1.json: numeric scores prohibited")
        ok = False

    return ok


def validate_draft_files() -> bool:
    ok = True
    pack = load_json(ROOT / "data" / "internal-draft-pack-v1.json")
    pack_by_path = {d.get("draft_file_path"): d for d in pack.get("drafts", [])}

    draft_dir = ROOT / "_internal_drafts" / "reference"
    if not draft_dir.is_dir():
        error("_internal_drafts/reference/: directory missing")
        return False

    md_files = sorted(draft_dir.glob("*.md"))
    if len(md_files) != 2:
        error(f"_internal_drafts/reference/: expected exactly 2 md files, found {len(md_files)}")
        ok = False

    for path in EXPECTED_DRAFT_FILES:
        if not path.exists():
            error(f"draft file missing: {path.relative_to(ROOT).as_posix()}")
            ok = False

    for md in md_files:
        rel = md.relative_to(ROOT).as_posix()
        if rel not in pack_by_path:
            error(f"unexpected draft file: {rel}")
            ok = False
            continue

        content = md.read_text(encoding="utf-8")
        wc = word_count(content)
        if wc < MIN_WORDS or wc > MAX_WORDS:
            error(f"draft file {rel}: word count {wc} outside {MIN_WORDS}-{MAX_WORDS}")
            ok = False

        if PLACEHOLDER_PATTERN.search(content):
            error(f"draft file {rel}: placeholder language detected")
            ok = False

        lower = content.lower()
        for entity in REAL_ENTITY_TERMS:
            if entity in lower:
                error(f"draft file {rel}: real entity reference detected")
                ok = False

        for term in PUBLIC_METADATA_TERMS:
            if term in lower and "no public" not in lower:
                error(f"draft file {rel}: public metadata label {term}")
                ok = False

        if has_forbidden_implication(content):
            error(f"draft file {rel}: forbidden implication detected")
            ok = False

        if "non-authorization statement" not in lower:
            error(f"draft file {rel}: missing Non-Authorization Statement section")
            ok = False

        for header in REQUIRED_SECTION_HEADERS:
            if f"## {header}" not in content and f"## {header}\n" not in content:
                if header not in content:
                    error(f"draft file {rel}: missing section {header}")
                    ok = False

        for field in STATUS_BLOCK_FIELDS:
            if field not in lower:
                error(f"draft file {rel}: Draft Status Block missing {field}")
                ok = False

        for field, expected in [
            ("draft_status", "internal_draft_created"),
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
            ("public_metadata_status", "not_created"),
            ("public_navigation_status", "not_linked"),
            ("deployment_status", "not_deployed"),
        ]:
            if expected not in content:
                error(f"draft file {rel}: status block missing {field}={expected}")
                ok = False

    return ok


def validate_draft_registry() -> bool:
    ok = True
    pack = load_json(ROOT / "data" / "internal-draft-pack-v1.json")
    pack_by_id = {d.get("draft_id"): d for d in pack.get("drafts", [])}

    data = load_json(ROOT / "data" / "internal-draft-registry.json")
    missing = REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-registry.json missing fields: {sorted(missing)}")
        ok = False

    records = data.get("draft_records", [])
    if len(records) != 2:
        error("internal-draft-registry.json: exactly 2 draft records required")
        ok = False

    for entry in records:
        did = entry.get("draft_id", "?")
        draft = pack_by_id.get(did)
        if not draft:
            error(f"draft registry: {did} not in pack")
            ok = False
            continue

        for field, expected in [
            ("draft_status", "internal_draft_created"),
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
            ("public_metadata_status", "not_created"),
            ("public_navigation_status", "not_linked"),
            ("deployment_status", "not_deployed"),
        ]:
            if entry.get(field) != expected:
                error(f"draft registry: {did} {field} must be {expected}")
                ok = False
            if draft.get(field) != entry.get(field):
                error(f"draft registry: {did} {field} mismatch with pack")
                ok = False

        if entry.get("draft_file_path") != draft.get("draft_file_path"):
            error(f"draft registry: {did} draft_file_path mismatch")
            ok = False

    return ok


def validate_blueprint_registry() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "internal-draft-blueprint-registry.json")

    for entry in registry.get("blueprint_records", []):
        bid = entry.get("blueprint_id", "?")
        if bid in REQUIRED_BLUEPRINT_IDS:
            if entry.get("internal_draft_status") != "internal_draft_created":
                error(f"blueprint registry: {bid} must have internal_draft_created")
                ok = False
            if entry.get("internal_draft_ref") != "data/internal-draft-pack-v1.json":
                error(f"blueprint registry: {bid} internal_draft_ref missing or wrong")
                ok = False
            if entry.get("internal_draft_pack_id") != "INT-DRAFT-PACK-V1-001":
                error(f"blueprint registry: {bid} internal_draft_pack_id missing or wrong")
                ok = False
            if entry.get("draft_status") != "internal_draft_created":
                error(f"blueprint registry: {bid} draft_status must be internal_draft_created")
                ok = False
            for field, expected in [
                ("route_status", "not_route_created"),
                ("sitemap_status", "not_sitemap_eligible"),
                ("publication_status", "publication_blocked"),
            ]:
                if entry.get(field) != expected:
                    error(f"blueprint registry: {bid} {field} must remain {expected}")
                    ok = False
        else:
            if entry.get("internal_draft_status") == "internal_draft_created":
                error(f"blueprint registry: {bid} must not be internal_draft_created")
                ok = False
            if entry.get("draft_status") == "internal_draft_created":
                error(f"blueprint registry: {bid} must not have draft_status internal_draft_created")
                ok = False

    return ok


def validate_candidate_registry() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "reference-page-candidate-registry.json")

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

        for field, expected in [
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
        ]:
            if entry.get(field) != expected:
                error(f"candidate registry: {cid} {field} must remain {expected}")
                ok = False

        if cid in REQUIRED_CANDIDATE_IDS:
            if entry.get("internal_draft_status") != "internal_draft_created":
                error(f"candidate registry: {cid} must have internal_draft_created")
                ok = False
            if entry.get("draft_status") != "internal_draft_created":
                error(f"candidate registry: {cid} draft_status must be internal_draft_created")
                ok = False
            if entry.get("internal_draft_ref") != "data/internal-draft-pack-v1.json":
                error(f"candidate registry: {cid} internal_draft_ref missing or wrong")
                ok = False
            if entry.get("internal_draft_pack_id") != "INT-DRAFT-PACK-V1-001":
                error(f"candidate registry: {cid} internal_draft_pack_id missing or wrong")
                ok = False
        else:
            if entry.get("internal_draft_status") == "internal_draft_created":
                error(f"candidate registry: {cid} must not be internal_draft_created")
                ok = False
            if entry.get("draft_status") == "internal_draft_created":
                error(f"candidate registry: {cid} must not have draft_status internal_draft_created")
                ok = False

    return ok


def validate_publisher_and_gates() -> bool:
    ok = True

    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub.get("current_publisher_status", "")
    if status not in (
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
        "blocked_until_internal_prototype_admissibility_regression_suite_validation",
    ):
        error(
            f"publisher-governance-policy: current_publisher_status must be "
            f"blocked_until_internal_draft_review_and_refinement, "
            f"blocked_until_public_route_readiness_gate, or "
            f"blocked_until_first_controlled_public_reference_pilot, got {status}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    pack_gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0021"), None)
    if not pack_gate:
        error("publisher-quality-gates: PUB-GATE-0021 missing")
        ok = False
    elif pack_gate.get("required_before_public_release") is not True or pack_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0021 must be required and not bypassable")
        ok = False
    else:
        notes = pack_gate.get("notes", "").lower()
        if "does not authorize" not in notes:
            error("publisher-quality-gates: PUB-GATE-0021 must not authorize outputs by itself")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "internal_draft_pack" not in checks and "first_internal_draft_pack" not in checks:
        error("reference-expansion-gate.json: must include internal draft pack pre-release check")
        ok = False

    return ok


def validate_route_sitemap_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])

    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    from public_surface_checks import validate_candidate_paths_not_registered_except_pilot
    candidates = load_json(ROOT / "data" / "reference-candidate-pack-v1.json").get("candidates", [])
    if not validate_candidate_paths_not_registered_except_pilot(routes, candidates, error):
        ok = False

    from public_surface_checks import validate_pilot_sitemap
    try:
        if not validate_pilot_sitemap(routes, error):
            ok = False
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        ok = False

    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not be created in Sprint 21")
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
    if "validate_internal_draft_pack.py" not in content:
        error("validate_all.py: must include validate_internal_draft_pack.py")
        ok = False

    return ok


def main() -> int:
    parse_paths = [
        "data/internal-draft-pack-policy.json",
        "data/internal-draft-pack-v1.json",
        "data/internal-draft-registry.json",
        "data/internal-draft-blueprint-registry.json",
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

    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    checks = [
        ("draft pack policy", validate_policy),
        ("draft pack", validate_draft_pack),
        ("draft files", validate_draft_files),
        ("draft registry", validate_draft_registry),
        ("blueprint registry", validate_blueprint_registry),
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
