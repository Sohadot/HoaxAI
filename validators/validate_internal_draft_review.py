#!/usr/bin/env python3
"""Validate Hoax.ai internal draft review and refinement enforcement."""

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
    "refinement_principle",
    "allowed_review_actions",
    "prohibited_review_actions",
    "review_scope",
    "review_outcomes",
    "non_authorization_rules",
    "last_reviewed",
}

CRITERIA_TOP = {
    "criteria_set_id",
    "name",
    "version",
    "status",
    "maturity",
    "criteria",
    "last_reviewed",
}

REVIEW_TOP = {
    "review_id",
    "name",
    "version",
    "status",
    "maturity",
    "reviewed_draft_pack",
    "reviews",
    "last_reviewed",
}

REFINEMENT_TOP = {
    "refinement_log_id",
    "name",
    "version",
    "status",
    "maturity",
    "refinements",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "INTERNAL_DRAFT_REVIEW_AND_REFINEMENT.md",
    "data/internal-draft-review-policy.json",
    "data/internal-draft-review-criteria.json",
    "data/internal-draft-review-v1.json",
    "data/internal-draft-refinement-log.json",
    "validators/validate_internal_draft_review.py",
]

REQUIRED_DRAFT_IDS = ["DRAFT-0001", "DRAFT-0002"]
REQUIRED_REVIEW_RECORD_IDS = ["REVIEW-DRAFT-0001", "REVIEW-DRAFT-0002"]
REQUIRED_REFINEMENT_IDS = ["REFINEMENT-0001", "REFINEMENT-0002"]
REQUIRED_CANDIDATE_IDS = ["REF-CAND-0001", "REF-CAND-0002"]

REVIEW_SCOPE_FILES = [
    "_internal_drafts/reference/evidence-posture.md",
    "_internal_drafts/reference/artifact-subject-separation.md",
]

EXPECTED_DRAFT_FILES = [
    ROOT / "_internal_drafts" / "reference" / "evidence-posture.md",
    ROOT / "_internal_drafts" / "reference" / "artifact-subject-separation.md",
]

CRITERION_IDS = [f"REVIEW-CRITERION-{i:04d}" for i in range(1, 18)]

ALLOWED_REVIEW_OUTCOMES = {
    "review_passed_internal",
    "review_passed_with_refinement",
    "needs_minor_refinement",
    "needs_major_refinement",
    "blocked_for_boundary_issue",
    "blocked_for_claim_source_issue",
    "blocked_for_public_implication",
}

ALLOWED_REFINEMENT_STATUS = {"refinement_applied_internal", "refinement_not_required"}

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
    "refinement_status",
    "non_authorization_statement",
]

PROHIBITED_ACTIONS = [
    "new_draft",
    "public_page",
    "route",
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
    "public_navigation",
    "publishing",
    "deployment",
    "seo_expansion",
]

PROHIBITED_CHANGES = [
    "public_route",
    "sitemap",
    "public_metadata",
    "public_navigation",
    "publication",
    "deployment",
    "external_factual",
    "tool",
    "classifier",
    "upload",
    "scoring",
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

PUBLISHER_STATUS = "blocked_until_public_route_readiness_gate"


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
    path = ROOT / "data" / "internal-draft-review-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"internal-draft-review-policy.json parse failed: {exc}")
        return False

    if POLICY_TOP - set(data.keys()):
        error(f"internal-draft-review-policy.json missing fields: {sorted(POLICY_TOP - set(data.keys()))}")
        ok = False

    if data.get("status") != "governed_internal_draft_review_policy":
        error("internal-draft-review-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "internal_review_only_no_routes_no_sitemap_no_publication":
        error("internal-draft-review-policy.json: invalid maturity")
        ok = False

    if set(data.get("review_scope", [])) != set(REVIEW_SCOPE_FILES):
        error("internal-draft-review-policy.json: review_scope must include exactly the two Sprint 21 draft files")
        ok = False

    prohibited = " ".join(data.get("prohibited_review_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"internal-draft-review-policy.json: prohibited actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"internal-draft-review-policy.json: non_authorization_rules missing {term}")
            ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-review-policy.json: numeric scores prohibited")
        ok = False

    return ok


def validate_criteria() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-review-criteria.json")

    if CRITERIA_TOP - set(data.keys()):
        error(f"internal-draft-review-criteria.json missing fields: {sorted(CRITERIA_TOP - set(data.keys()))}")
        ok = False

    criteria = data.get("criteria", [])
    if len(criteria) != 17:
        error("internal-draft-review-criteria.json: exactly 17 criteria required")
        ok = False

    seen = set()
    for c in criteria:
        cid = c.get("criterion_id", "")
        if cid not in CRITERION_IDS:
            error(f"criteria: invalid criterion_id {cid}")
            ok = False
        if cid in seen:
            error(f"criteria: duplicate criterion_id {cid}")
            ok = False
        seen.add(cid)

        notes = (c.get("validation_notes", "") + c.get("requirement", "")).lower()
        if "authorize publication" in notes and "does not authorize" not in notes:
            error(f"criteria {cid}: must not authorize publication")
            ok = False

    if seen != set(CRITERION_IDS):
        error("internal-draft-review-criteria.json: missing required criterion IDs")
        ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-review-criteria.json: numeric scores prohibited")
        ok = False

    return ok


def validate_review_results() -> bool:
    ok = True
    pack = {d.get("draft_id"): d for d in load_json(ROOT / "data" / "internal-draft-pack-v1.json").get("drafts", [])}
    data = load_json(ROOT / "data" / "internal-draft-review-v1.json")

    if REVIEW_TOP - set(data.keys()):
        error(f"internal-draft-review-v1.json missing fields: {sorted(REVIEW_TOP - set(data.keys()))}")
        ok = False

    reviews = data.get("reviews", [])
    if len(reviews) != 2:
        error("internal-draft-review-v1.json: exactly 2 review records required")
        ok = False

    seen = set()
    for review in reviews:
        rid = review.get("review_record_id", "?")
        did = review.get("draft_id", "?")
        seen.add(rid)

        if rid not in REQUIRED_REVIEW_RECORD_IDS:
            error(f"review: invalid review_record_id {rid}")
            ok = False

        if review.get("review_status") != "review_completed_internal":
            error(f"review {rid}: review_status must be review_completed_internal")
            ok = False

        outcome = review.get("review_outcome", "")
        if outcome not in ALLOWED_REVIEW_OUTCOMES:
            error(f"review {rid}: invalid review_outcome {outcome}")
            ok = False

        if did not in pack:
            error(f"review {rid}: draft {did} not in pack")
            ok = False

        results = review.get("criteria_results", [])
        result_ids = {r.get("criterion_id") for r in results}
        if result_ids != set(CRITERION_IDS):
            error(f"review {rid}: must cover all 17 criteria")
            ok = False

        for cr in results:
            if json_has_numeric_scores(cr):
                error(f"review {rid}: numeric scores prohibited in criteria_results")
                ok = False

        for field, expected in [
            ("public_status_after_review", "not_public_site_surface"),
            ("route_status_after_review", "not_route_created"),
            ("sitemap_status_after_review", "not_sitemap_eligible"),
            ("publication_status_after_review", "publication_blocked"),
            ("public_metadata_status_after_review", "not_created"),
            ("public_navigation_status_after_review", "not_linked"),
            ("deployment_status_after_review", "not_deployed"),
        ]:
            if review.get(field) != expected:
                error(f"review {rid}: {field} must be {expected}")
                ok = False

        stmt = review.get("non_authorization_statement", "").lower()
        if not stmt or "does not authorize" not in stmt:
            error(f"review {rid}: non_authorization_statement required")
            ok = False

    if seen != set(REQUIRED_REVIEW_RECORD_IDS):
        error("internal-draft-review-v1.json: missing required review record IDs")
        ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-review-v1.json: numeric scores prohibited")
        ok = False

    return ok


def validate_refinement_log() -> bool:
    ok = True
    pack_paths = {
        d.get("draft_id"): d.get("draft_file_path")
        for d in load_json(ROOT / "data" / "internal-draft-pack-v1.json").get("drafts", [])
    }
    data = load_json(ROOT / "data/internal-draft-refinement-log.json")

    if REFINEMENT_TOP - set(data.keys()):
        error(f"internal-draft-refinement-log.json missing fields: {sorted(REFINEMENT_TOP - set(data.keys()))}")
        ok = False

    refinements = data.get("refinements", [])
    if len(refinements) != 2:
        error("internal-draft-refinement-log.json: exactly 2 refinement records required")
        ok = False

    seen = set()
    for ref in refinements:
        fid = ref.get("refinement_id", "?")
        did = ref.get("draft_id", "?")
        seen.add(fid)

        if fid not in REQUIRED_REFINEMENT_IDS:
            error(f"refinement: invalid refinement_id {fid}")
            ok = False

        status = ref.get("refinement_status", "")
        if status not in ALLOWED_REFINEMENT_STATUS:
            error(f"refinement {fid}: invalid refinement_status {status}")
            ok = False

        if did not in pack_paths:
            error(f"refinement {fid}: draft {did} not in pack")
            ok = False
        if ref.get("draft_file_path") != pack_paths.get(did):
            error(f"refinement {fid}: draft_file_path mismatch")
            ok = False

        avoided = " ".join(ref.get("prohibited_changes_avoided", [])).lower()
        for term in PROHIBITED_CHANGES:
            if term.replace("_", "") not in avoided.replace("_", ""):
                error(f"refinement {fid}: prohibited_changes_avoided missing {term}")
                ok = False

        post = ref.get("post_refinement_status", {})
        for field, expected in [
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
            ("public_metadata_status", "not_created"),
            ("public_navigation_status", "not_linked"),
            ("deployment_status", "not_deployed"),
            ("review_status", "review_completed_internal"),
        ]:
            if post.get(field) != expected:
                error(f"refinement {fid}: post_refinement_status.{field} must be {expected}")
                ok = False

    if seen != set(REQUIRED_REFINEMENT_IDS):
        error("internal-draft-refinement-log.json: missing required refinement IDs")
        ok = False

    return ok


def validate_draft_files() -> bool:
    ok = True
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
        if rel not in REVIEW_SCOPE_FILES:
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
            if f"## {header}" not in content:
                error(f"draft file {rel}: missing section {header}")
                ok = False

        for field in STATUS_BLOCK_FIELDS:
            if field not in lower:
                error(f"draft file {rel}: Draft Status Block missing {field}")
                ok = False

        if "review_completed_internal" not in content:
            error(f"draft file {rel}: review_status must be review_completed_internal")
            ok = False

        ref_status = None
        for line in content.splitlines():
            if "refinement_status" in line.lower():
                if "refinement_applied_internal" in line or "refinement_not_required" in line:
                    ref_status = True
        if not ref_status:
            error(f"draft file {rel}: refinement_status must be refinement_applied_internal or refinement_not_required")
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


def validate_registries() -> bool:
    ok = True
    pack = {d.get("draft_id"): d for d in load_json(ROOT / "data" / "internal-draft-pack-v1.json").get("drafts", [])}

    for entry in load_json(ROOT / "data" / "internal-draft-registry.json").get("draft_records", []):
        did = entry.get("draft_id", "?")
        if entry.get("review_status") != "review_completed_internal":
            error(f"draft registry: {did} review_status must be review_completed_internal")
            ok = False
        if entry.get("review_ref") != "data/internal-draft-review-v1.json":
            error(f"draft registry: {did} review_ref missing or wrong")
            ok = False
        if entry.get("refinement_status") not in ALLOWED_REFINEMENT_STATUS:
            error(f"draft registry: {did} invalid refinement_status")
            ok = False
        if entry.get("refinement_ref") != "data/internal-draft-refinement-log.json":
            error(f"draft registry: {did} refinement_ref missing or wrong")
            ok = False
        for field, expected in [
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
        ]:
            if entry.get(field) != expected:
                error(f"draft registry: {did} {field} must remain {expected}")
                ok = False

    for did, draft in pack.items():
        if did in REQUIRED_DRAFT_IDS:
            if draft.get("review_status") != "review_completed_internal":
                error(f"draft pack: {did} review_status must be review_completed_internal")
                ok = False
            if draft.get("review_ref") != "data/internal-draft-review-v1.json":
                error(f"draft pack: {did} review_ref missing or wrong")
                ok = False
            if draft.get("refinement_status") not in ALLOWED_REFINEMENT_STATUS:
                error(f"draft pack: {did} invalid refinement_status")
                ok = False

    from candidate_registry_checks import is_batch1_production_candidate, is_batch2_production_candidate

    for entry in load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", []):
        cid = entry.get("candidate_id", "?")
        if is_batch1_production_candidate(entry):
            continue
        if is_batch2_production_candidate(entry):
            continue
        if cid in REQUIRED_CANDIDATE_IDS:
            if entry.get("internal_draft_review_status") != "review_completed_internal":
                error(f"candidate registry: {cid} internal_draft_review_status required")
                ok = False
            if entry.get("internal_draft_review_ref") != "data/internal-draft-review-v1.json":
                error(f"candidate registry: {cid} internal_draft_review_ref missing or wrong")
                ok = False
            if entry.get("internal_draft_refinement_status") not in ALLOWED_REFINEMENT_STATUS:
                error(f"candidate registry: {cid} internal_draft_refinement_status invalid")
                ok = False
            for field, expected in [
                ("route_status", "not_route_created"),
                ("sitemap_status", "not_sitemap_eligible"),
                ("publication_status", "publication_blocked"),
            ]:
                if entry.get(field) != expected:
                    error(f"candidate registry: {cid} {field} must remain {expected}")
                    ok = False
        else:
            if entry.get("internal_draft_review_status") == "review_completed_internal":
                error(f"candidate registry: {cid} must not have review_completed_internal")
                ok = False
            if entry.get("route_status") != "not_route_created":
                error(f"candidate registry: {cid} must not be route-ready")
                ok = False

    return ok


def validate_publisher_and_gates() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub.get("current_publisher_status", "")
    if status not in (
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
    ):
        error(
            f"publisher-governance-policy: current_publisher_status must be "
            f"blocked_until_public_route_readiness_gate or "
            f"blocked_until_first_controlled_public_reference_pilot, got {status}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    review_gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0022"), None)
    if not review_gate:
        error("publisher-quality-gates: PUB-GATE-0022 missing")
        ok = False
    elif review_gate.get("required_before_public_release") is not True or review_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0022 must be required and not bypassable")
        ok = False
    else:
        notes = review_gate.get("notes", "").lower()
        if "does not authorize" not in notes:
            error("publisher-quality-gates: PUB-GATE-0022 must not authorize outputs by itself")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "internal_draft_review" not in checks:
        error("reference-expansion-gate.json: must include internal draft review pre-release check")
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
        error(".nojekyll must not be created in this sprint")
        ok = False


    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_NON_PUBLIC_HTML:
            error(f"public safety: unexpected HTML file {rel}")
            ok = False

    return ok


def validate_cross_file() -> bool:
    ok = True
    locations = {s.get("location") for s in load_json(ROOT / "data" / "source-registry.json").get("sources", [])}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry.json: missing source for {loc}")
            ok = False

    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_internal_draft_review.py" not in content:
        error("validate_all.py: must include validate_internal_draft_review.py")
        ok = False

    return ok


def main() -> int:
    parse_paths = [
        "data/internal-draft-review-policy.json",
        "data/internal-draft-review-criteria.json",
        "data/internal-draft-review-v1.json",
        "data/internal-draft-refinement-log.json",
        "data/internal-draft-pack-v1.json",
        "data/internal-draft-registry.json",
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
        validate_policy,
        validate_criteria,
        validate_review_results,
        validate_refinement_log,
        validate_draft_files,
        validate_registries,
        validate_publisher_and_gates,
        validate_route_sitemap_public_safety,
        validate_cross_file,
    ]
    if not all(fn() for fn in checks):
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
