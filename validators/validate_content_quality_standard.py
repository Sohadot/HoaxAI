#!/usr/bin/env python3
"""Validate Hoax.ai content quality and reference substance standard enforcement."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STANDARD_TOP = {
    "standard_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "seo_principle",
    "reference_substance_definition",
    "substance_is_not",
    "minimum_substance_gates",
    "required_page_section_classes",
    "conditional_page_section_classes",
    "prohibited_content_quality_failures",
    "validation_requirements",
    "last_reviewed",
}

RULES_TOP = {"rules_id", "name", "version", "status", "maturity", "rules", "last_reviewed"}

PATTERNS_TOP = {"pattern_set_id", "name", "version", "status", "maturity", "patterns", "last_reviewed"}

SECTIONS_TOP = {
    "requirements_id",
    "name",
    "version",
    "status",
    "maturity",
    "required_sections",
    "conditional_sections",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "CONTENT_QUALITY_REFERENCE_SUBSTANCE_STANDARD.md",
    "data/content-quality-standard.json",
    "data/reference-substance-rules.json",
    "data/thin-content-failure-patterns.json",
    "data/reference-section-requirements.json",
    "validators/validate_content_quality_standard.py",
]

REQUIRED_GATES = [
    "purpose",
    "definition",
    "scope",
    "governance_boundary",
    "system_relationship",
    "claim_traceability",
    "source_scope",
    "semantic_seo",
    "prohibited_misreading",
    "internal_link",
    "technical_quality",
    "interface_boundary",
    "publisher_boundary",
    "review_status",
]

REQUIRED_PROHIBITED = [
    "thin_seo",
    "keyword_only",
    "glossary_only",
    "generic_ai",
    "unsupported_external",
    "placeholder",
    "future_capability",
    "tool_implication",
    "scoring",
    "fake_real",
    "subject_accusation",
    "publisher_output",
]

REQUIRED_RULE_IDS = [f"SUBSTANCE-RULE-{i:04d}" for i in range(1, 17)]

REQUIRED_PATTERN_IDS = [f"THIN-PATTERN-{i:04d}" for i in range(1, 15)]

REQUIRED_SECTION_IDS = [f"REF-SECTION-{i:04d}" for i in range(1, 17)]

REQUIRED_SECTION_NAMES = [
    "page thesis",
    "definition and scope",
    "governance boundary",
    "relationship to hoax.ai system",
    "semantic seo role",
    "prohibited misreadings",
    "claim and source traceability",
    "internal links",
    "last reviewed",
]

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

RULE_ID_PATTERN = re.compile(r"^SUBSTANCE-RULE-\d{4}$")
PATTERN_ID_PATTERN = re.compile(r"^THIN-PATTERN-\d{4}$")
SECTION_ID_PATTERN = re.compile(r"^REF-SECTION-\d{4}$")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_content_quality_standard() -> bool:
    ok = True
    path = ROOT / "data" / "content-quality-standard.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"content-quality-standard.json parse failed: {exc}")
        return False

    missing = STANDARD_TOP - set(data.keys())
    if missing:
        error(f"content-quality-standard.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_content_quality_standard":
        error("content-quality-standard.json: invalid status")
        ok = False
    if data.get("maturity") != "pre_reference_publication_standard":
        error("content-quality-standard.json: invalid maturity")
        ok = False

    principle = data.get("governing_principle", "").lower()
    if "not reference-grade because it is long" not in principle:
        error("content-quality-standard.json: governing principle missing required sentence")
        ok = False
    if "governed substance" not in principle:
        error("content-quality-standard.json: governing principle missing governed substance")
        ok = False

    seo = data.get("seo_principle", "").lower()
    if "clarifies governed reference value" not in seo:
        error("content-quality-standard.json: seo_principle missing required SEO sentence")
        ok = False
    if "keyword stuffing" in seo or "seo-first" in seo:
        if "not" not in seo[:seo.find("keyword") if "keyword" in seo else 0]:
            pass
    if "substitutes" not in seo:
        error("content-quality-standard.json: seo_principle must prohibit SEO substitution")
        ok = False

    gates = " ".join(data.get("minimum_substance_gates", [])).lower()
    for term in REQUIRED_GATES:
        if term.replace("_", " ") not in gates.replace("_", " "):
            error(f"content-quality-standard.json: minimum_substance_gates missing {term}")
            ok = False

    prohibited = " ".join(data.get("prohibited_content_quality_failures", [])).lower()
    for term in REQUIRED_PROHIBITED:
        key = term.replace("_", "")
        if key not in prohibited.replace("_", ""):
            error(f"content-quality-standard.json: prohibited failures missing {term}")
            ok = False

    combined = json.dumps(data).lower()
    for bad in ["quality_score", "seo_score", "percentage_grade", "numeric_grade"]:
        if bad in combined and bad not in ["no_numeric_content_scores", "no_seo_scores"]:
            if f"no_{bad}" not in combined and f"no numeric" not in combined:
                if bad in prohibited or bad in " ".join(data.get("prohibited_content_quality_failures", [])):
                    continue
                error(f"content-quality-standard.json: numeric score metric {bad} introduced")
                ok = False

    validation = " ".join(data.get("validation_requirements", [])).lower()
    if "score" in validation and "no_" not in validation:
        error("content-quality-standard.json: validation must not introduce scoring")
        ok = False

    return ok


def validate_substance_rules() -> bool:
    ok = True
    path = ROOT / "data" / "reference-substance-rules.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-substance-rules.json parse failed: {exc}")
        return False

    missing = RULES_TOP - set(data.keys())
    if missing:
        error(f"reference-substance-rules.json missing fields: {sorted(missing)}")
        ok = False

    rules = data.get("rules", [])
    ids: list[str] = []
    for rule in rules:
        rid = rule.get("rule_id", "")
        if not RULE_ID_PATTERN.match(rid):
            error(f"reference-substance-rules: invalid rule_id {rid}")
            ok = False
        if rid in ids:
            error(f"reference-substance-rules: duplicate rule_id {rid}")
            ok = False
        ids.append(rid)

        if rule.get("severity") != "blocking":
            error(f"reference-substance-rules: release gate {rid} must be blocking")
            ok = False

        for field in ["rule_id", "name", "applies_to", "requirement", "failure_condition",
                      "validation_method", "severity", "notes"]:
            if field not in rule:
                error(f"reference-substance-rules: {rid} missing {field}")
                ok = False

    if set(ids) != set(REQUIRED_RULE_IDS):
        error(f"reference-substance-rules: expected rules {REQUIRED_RULE_IDS}")
        ok = False

    rules_text = path.read_text(encoding="utf-8").lower()
    if "quality_score" in rules_text and "no thin seo" not in rules_text:
        error("reference-substance-rules: must not introduce quality_score")
        ok = False

    return ok


def validate_thin_patterns() -> bool:
    ok = True
    path = ROOT / "data" / "thin-content-failure-patterns.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"thin-content-failure-patterns.json parse failed: {exc}")
        return False

    missing = PATTERNS_TOP - set(data.keys())
    if missing:
        error(f"thin-content-failure-patterns.json missing fields: {sorted(missing)}")
        ok = False

    patterns = data.get("patterns", [])
    ids = [p.get("pattern_id") for p in patterns]
    if set(ids) != set(REQUIRED_PATTERN_IDS):
        error(f"thin-content-failure-patterns: expected patterns {REQUIRED_PATTERN_IDS}")
        ok = False

    blocking_required = {
        "THIN-PATTERN-0005",
        "THIN-PATTERN-0006",
        "THIN-PATTERN-0008",
        "THIN-PATTERN-0009",
        "THIN-PATTERN-0010",
        "THIN-PATTERN-0007",
        "THIN-PATTERN-0011",
        "THIN-PATTERN-0013",
        "THIN-PATTERN-0014",
    }
    for pat in patterns:
        pid = pat.get("pattern_id", "")
        if not PATTERN_ID_PATTERN.match(pid):
            error(f"thin-content-failure-patterns: invalid pattern_id {pid}")
            ok = False
        if pid in blocking_required and pat.get("severity") != "blocking":
            error(f"thin-content-failure-patterns: {pid} must be blocking")
            ok = False
        if pat.get("allowed_exception") not in ("none", None, ""):
            if pat.get("allowed_exception") != "none":
                error(f"thin-content-failure-patterns: {pid} allowed_exception must be narrow or none")
                ok = False

        for field in ["pattern_id", "name", "description", "prohibited_because",
                      "detection_hint", "severity", "allowed_exception", "notes"]:
            if field not in pat:
                error(f"thin-content-failure-patterns: {pid} missing {field}")
                ok = False

        desc = pat.get("description", "").lower()
        if "creates public route" in desc or "creates page file" in desc:
            error(f"thin-content-failure-patterns: {pid} creates public route or page")
            ok = False

    return ok


def validate_section_requirements() -> bool:
    ok = True
    path = ROOT / "data" / "reference-section-requirements.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-section-requirements.json parse failed: {exc}")
        return False

    missing = SECTIONS_TOP - set(data.keys())
    if missing:
        error(f"reference-section-requirements.json missing fields: {sorted(missing)}")
        ok = False

    required = data.get("required_sections", [])
    conditional = data.get("conditional_sections", [])
    all_sections = required + conditional
    ids = [s.get("section_id") for s in all_sections]

    if set(ids) != set(REQUIRED_SECTION_IDS):
        error(f"reference-section-requirements: expected sections {REQUIRED_SECTION_IDS}")
        ok = False

    found_names = {s.get("name", "").lower() for s in required}
    for name in REQUIRED_SECTION_NAMES:
        if name not in found_names:
            error(f"reference-section-requirements: missing required section {name}")
            ok = False

    for sec in all_sections:
        sid = sec.get("section_id", "")
        if not SECTION_ID_PATTERN.match(sid):
            error(f"reference-section-requirements: invalid section_id {sid}")
            ok = False
        if not sec.get("linked_substance_rules"):
            error(f"reference-section-requirements: {sid} must map to substance rules")
            ok = False
        prohibited = sec.get("prohibited_content", "").lower()
        if sid in ["REF-SECTION-0006", "REF-SECTION-0005", "REF-SECTION-0007"]:
            for term in ["tool", "fake", "score", "accusation"]:
                if term in prohibited or term in sec.get("minimum_substance_requirement", "").lower():
                    pass
            if sid == "REF-SECTION-0006" and "scoring" not in prohibited:
                error("reference-section-requirements: Prohibited Misreadings must prohibit scoring")
                ok = False

        for field in ["section_id", "name", "required_for", "purpose",
                      "minimum_substance_requirement", "prohibited_content",
                      "linked_substance_rules", "notes"]:
            if field not in sec:
                error(f"reference-section-requirements: {sid} missing {field}")
                ok = False

    return ok


def validate_cross_file_integration() -> bool:
    ok = True

    for rel in [
        "REFERENCE_PAGE_BLUEPRINT.md",
        "GOVERNED_PUBLISHER_CONTROL_PLANE.md",
        "data/reference-page-blueprint.json",
        "data/reference-expansion-gate.json",
        "data/reference-page-candidate-registry.json",
        "data/publisher-quality-gates.json",
        "data/publisher-governance-policy.json",
    ]:
        if not (ROOT / rel).exists():
            error(f"cross-file: missing {rel}")
            ok = False

    candidates = load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", [])
    if candidates:
        from candidate_registry_checks import validate_candidates_blocked_only

        if not validate_candidates_blocked_only(candidates, error):
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "content_quality" not in checks and "reference_substance" not in checks:
        error("reference-expansion-gate.json: must include content quality pre-release check")
        ok = False

    pub_gate = load_json(ROOT / "data" / "publisher-quality-gates.json")
    cq = next((g for g in pub_gate.get("gates", []) if g.get("gate_id") == "PUB-GATE-0003"), None)
    if not cq:
        error("publisher-quality-gates: PUB-GATE-0003 missing")
        ok = False
    elif "blocked_until_sprint_14" in cq.get("status", "").lower():
        error("publisher-quality-gates: Content Quality Gate still blocked after Sprint 14")
        ok = False
    elif cq.get("required_before_public_release") is not True:
        error("publisher-quality-gates: Content Quality Gate must remain required before public release")
        ok = False

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
    ):
        error(f"publisher-governance-policy: publisher must remain blocked from drafts and publication, got {status}")
        ok = False
    prohibited = " ".join(pub_policy.get("prohibited_current_outputs", [])).lower()
    if "draft_pages" not in prohibited and "content_drafts" not in prohibited:
        error("publisher-governance-policy: draft outputs must remain prohibited")
        ok = False

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    queues = load_json(ROOT / "data" / "publisher-queue-registry.json").get("queues", [])
    for q in queues:
        if q.get("items"):
            error(f"publisher-queue-registry: queue {q.get('queue_id')} must be empty")
            ok = False

    return ok


def validate_repository_safety() -> bool:
    ok = True

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_NON_PUBLIC_HTML:
            error(f"unexpected HTML file: {rel}")
            ok = False

    for draft in ROOT.glob("**/drafts/**"):
        if draft.is_file():
            error(f"draft page file found: {draft}")
            ok = False

    return ok


def validate_source_registry() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing content quality source {loc}")
            ok = False
    return ok


def validate_validate_all_integration() -> bool:
    ok = True
    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_content_quality_standard.py" not in content:
        error("validate_all.py: must include validate_content_quality_standard.py")
        ok = False
    return ok


def main() -> int:
    ok = True

    if not (ROOT / "CONTENT_QUALITY_REFERENCE_SUBSTANCE_STANDARD.md").exists():
        error("CONTENT_QUALITY_REFERENCE_SUBSTANCE_STANDARD.md missing")
        ok = False

    if not validate_content_quality_standard():
        ok = False
    if not validate_substance_rules():
        ok = False
    if not validate_thin_patterns():
        ok = False
    if not validate_section_requirements():
        ok = False
    if not validate_cross_file_integration():
        ok = False
    if not validate_repository_safety():
        ok = False
    if not validate_source_registry():
        ok = False
    if not validate_validate_all_integration():
        ok = False

    if ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
