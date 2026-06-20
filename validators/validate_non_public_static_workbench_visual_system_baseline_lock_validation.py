#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Visual System Baseline Lock Validation v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
INDEX_PATH = PROTO_DIR / "index.html"
CSS_PATH = PROTO_DIR / "prototype.css"
PROTO_REL = "_internal_prototypes/evidence-posture-workbench"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
ALLOWED_FILES = {"index.html", "prototype.css"}
MATURE = "validation_only_locked_static_internal_visual_baseline_no_engine_no_classifier_no_public_route"
STATUS = "governed_non_public_static_workbench_visual_system_baseline_lock_validation"
POLICY_STATUS = "governed_non_public_static_workbench_visual_system_baseline_lock_validation_policy"
DIMENSIONS = [
    "Baseline Lock Policy Integrity", "Baseline Lock Record Integrity", "Locked Elements Integrity",
    "Change-Control Integrity", "Baseline Boundary Audit Integrity", "Locked File Scope Integrity",
    "Prototype Files Not Modified", "No Additional Prototype Files", "Static HTML Boundary",
    "Static CSS Boundary", "Locked Evidence Field Identity", "Locked Evidence Chamber Identity",
    "Locked Boundary Rail Identity", "Locked Provenance Shadow Identity",
    "Locked Missing Context Absence Identity", "Locked Not-Assessable Restraint Identity",
    "Locked Refusal Gate Identity", "Locked Output Envelope Identity", "Locked Verification Path Identity",
    "Locked Token Families", "Locked Pattern Registry", "Locked Anti-Pattern Blocks",
    "Change-Control Requirement Completeness", "No Informal Visual Change Authorization",
    "Public Route Exclusion", "Sitemap Exclusion", "Public Navigation Exclusion", "Homepage Link Exclusion",
    "Reference Page Link Exclusion", "Language Page Link Exclusion", "No JavaScript", "No Forms or Inputs",
    "No Upload Surface", "No Scoring Surface", "No Fake/Real Verdict Surface", "No API/Network/Storage Behavior",
    "No Analytics", "No Real-World Content", "No External Factual Claims", "Non-Authorization Rule Integrity",
    "Publisher Gate Alignment", "Reference Expansion Gate Alignment", "Python Cache Exclusion",
    "Public Surface Four-URL Integrity", "Future Change Requires Governance",
]
PROHIBITED_ACTIONS = [
    "modifying prototype files", "new prototype files", "prototype expansion", "public route creation",
    "sitemap expansion", "public navigation link", "interface behavior", "javascript", "forms", "inputs",
    "upload", "scoring", "fake/real output", "generated output", "engine", "classifier", "detector",
    "api", "analytics", "storage", "network calls", "monetization", "dns", "cloudflare",
    "custom domain launch", "deployment changes", "external factual claims", "subject accusation",
    "python cache file commit",
]
SOURCE_LOCS = [
    "NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION_V1.md",
    "data/non-public-static-workbench-visual-system-baseline-lock-validation-policy.json",
    "data/non-public-static-workbench-visual-system-baseline-lock-validation-results-v1.json",
    "data/non-public-static-workbench-visual-system-baseline-record-validation-v1.json",
    "data/non-public-static-workbench-visual-system-change-control-validation-v1.json",
    "data/non-public-static-workbench-visual-system-baseline-public-isolation-audit-v1.json",
    "data/non-public-static-workbench-visual-system-baseline-static-safety-audit-v1.json",
    "validators/validate_non_public_static_workbench_visual_system_baseline_lock_validation.py",
]
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b", re.I)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def has_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower() in text or item.lower().replace("_", " ") in text for item in required)


def validate_doctrine() -> bool:
    ok = True
    text = (ROOT / "NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION_V1.md").read_text(encoding="utf-8")
    required = [
        "A baseline lock must be validated before it can govern future change.",
        "A locked baseline protects future design only when its boundaries remain enforceable.",
        "Baseline lock validation is a governance validation layer",
        "Sprint 41 validates the visual system baseline lock",
        "maturity: validation_only_locked_static_internal_visual_baseline_no_engine_no_classifier_no_public_route",
    ]
    for phrase in required:
        if phrase not in text:
            error(f"doctrine: missing {phrase}")
            ok = False
    for dim in DIMENSIONS:
        if dim not in text:
            error(f"doctrine: missing validation dimension {dim}")
            ok = False
    for term in ["prototype modification", "visual redesign", "prototype expansion", "public workbench readiness", "engine readiness", "classifier readiness", "deployment readiness", "public route approval"]:
        if term not in text.lower():
            error(f"doctrine: validation-is-not missing {term}")
            ok = False
    return ok


def validate_policy() -> bool:
    ok = True
    data = load_json("data/non-public-static-workbench-visual-system-baseline-lock-validation-policy.json")
    required = {"policy_id", "name", "version", "status", "maturity", "governing_principle", "identity_principle", "allowed_validation_actions", "prohibited_actions", "validation_scope", "correction_policy", "non_authorization_rules", "last_reviewed"}
    if not required.issubset(data):
        error("validation policy: missing top-level fields")
        ok = False
    if data.get("status") != POLICY_STATUS:
        error("validation policy: invalid status")
        ok = False
    if data.get("maturity") != MATURE:
        error("validation policy: invalid maturity")
        ok = False
    if not has_all(data.get("allowed_validation_actions", []), ["baseline lock validation", "locked record validation", "locked elements validation", "change-control validation", "public isolation validation", "static safety validation", "publisher gate validation", "reference gate validation", "python cache exclusion validation", "validation only"]):
        error("validation policy: missing allowed validation actions")
        ok = False
    if not has_all(data.get("prohibited_actions", []), PROHIBITED_ACTIONS):
        error("validation policy: missing prohibited actions")
        ok = False
    if not has_all(data.get("validation_scope", []), ["Sprint 40 baseline lock artifacts", "current prototype HTML", "current prototype CSS", "route registry exclusion", "sitemap exclusion", "public link exclusion", "publisher governance", "publisher gates", "reference expansion gate", "Python cache exclusion"]):
        error("validation policy: missing validation scope")
        ok = False
    correction = data.get("correction_policy", "").lower()
    for term in ["modify prototype files", "add files", "add routes", "add sitemap entries", "add public links", "add js", "add forms", "add inputs", "add upload", "add scoring", "add engine behavior", "add classifier behavior", "add api", "add analytics", "add deployment changes", "commit python cache files"]:
        if term not in correction:
            error(f"validation policy: correction policy missing {term}")
            ok = False
    blocked = " ".join(data.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in ["public workbench", "engine", "classifier", "upload", "scoring", "api", "routes", "sitemap", "deployment", "dns", "cloudflare", "custom domain launch", "public tool behavior", "prototype modification", "prototype expansion", "production readiness", "python cache commit"]:
        if term not in blocked:
            error(f"validation policy: non-authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search((ROOT / "data/non-public-static-workbench-visual-system-baseline-lock-validation-policy.json").read_text(encoding="utf-8")):
        error("validation policy: numeric score, grade, percentage, or SEO score found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    data = load_json("data/non-public-static-workbench-visual-system-baseline-lock-validation-results-v1.json")
    dims = data.get("validation_dimensions", [])
    names = [d.get("name") for d in dims]
    if names != DIMENSIONS:
        error("validation results: all 45 dimensions must exist in order")
        ok = False
    if any(d.get("result") != "pass" for d in dims):
        error("validation results: every dimension must pass")
        ok = False
    if data.get("overall_result") != "non_public_static_visual_system_baseline_lock_validated":
        error("validation results: invalid overall_result")
        ok = False
    if data.get("python_cache_result") != "python_cache_excluded":
        error("validation results: python_cache_result must be python_cache_excluded")
        ok = False
    note = data.get("non_authorization_note", "").lower()
    for term in ["prototype modification", "prototype expansion", "public workbench", "engine", "classifier", "tool", "deployment", "public release"]:
        if term not in note:
            error(f"validation results: non_authorization_note missing {term}")
            ok = False
    return ok


def validate_record_and_change_control() -> bool:
    ok = True
    record = load_json("data/non-public-static-workbench-visual-system-baseline-record-validation-v1.json")
    if record.get("status") != "non_public_static_visual_system_baseline_record_validated" or record.get("maturity") != "baseline_record_validation_only_no_public_interface_no_engine" or record.get("overall_result") != "baseline_record_validated":
        error("baseline record validation: invalid status, maturity, or overall_result")
        ok = False
    required_groups = {
        "validation_reference_results": ["non_public_static_visual_system_hardening_validated", "token_system_validated", "pattern_system_validated", "visual_antipattern_blocking_validated", "hardening_public_isolation_validated", "hardening_static_safety_validated"],
        "locked_identity_results": ["evidence_chamber", "governed_evidence_field", "boundary_rail", "provenance_shadow", "missing_context_absence", "not_assessable_restraint", "refusal_gate", "output_envelope", "verification_path", "anti_detector_identity"],
        "public_surface_status_results": ["four_public_urls_only", "not_registered_as_public_route", "not_in_sitemap", "not_linked_from_public_navigation"],
        "prohibited_capability_results": ["no_prototype_modification_authorized", "no_new_prototype_files", "no_public_route", "no_sitemap_entry", "no_public_navigation", "no_engine", "no_classifier", "no_detector", "no_upload", "no_scoring", "no_fake_real_output", "no_forms", "no_inputs", "no_api", "no_analytics", "no_storage", "no_network_calls", "no_monetization", "no_dns", "no_cloudflare", "no_custom_domain_launch", "no_deployment_change"],
    }
    for key, required in required_groups.items():
        if not set(required).issubset(set(record.get(key, []))):
            error(f"baseline record validation: missing {key}")
            ok = False
    cc = load_json("data/non-public-static-workbench-visual-system-change-control-validation-v1.json")
    if cc.get("status") != "non_public_static_visual_system_change_control_validated" or cc.get("maturity") != "change_control_validation_only_no_prototype_modification" or cc.get("overall_result") != "change_control_validated":
        error("change-control validation: invalid status, maturity, or overall_result")
        ok = False
    for key, required in {
        "controlled_file_results": ["index_html_controlled", "prototype_css_controlled"],
        "future_change_requirement_results": ["future_sprint_required", "decision_log_entry_required", "explicit_allowed_files_required", "explicit_prohibited_changes_required", "validator_required", "boundary_audit_required", "public_isolation_audit_required", "static_safety_audit_required", "source_registry_update_required", "evidence_ledger_update_only_if_claim_added", "no_public_route_without_separate_public_route_governance", "no_engine_classifier_upload_scoring_without_separate_engine_governance"],
        "prohibited_informal_change_results": ["unscheduled_css_edits_blocked", "unscheduled_html_edits_blocked", "visual_redesign_without_decision_blocked", "adding_js_blocked", "adding_forms_blocked", "adding_inputs_blocked", "adding_upload_controls_blocked", "adding_scoring_visuals_blocked", "adding_fake_real_language_blocked", "adding_public_links_blocked", "adding_sitemap_entries_blocked", "adding_route_registry_entries_blocked", "adding_deployment_changes_blocked"],
        "required_future_validation_results": ["validate_all_required", "dedicated_validator_required", "public_surface_governance_required", "python_cache_exclusion_required"],
    }.items():
        if not set(required).issubset(set(cc.get(key, []))):
            error(f"change-control validation: missing {key}")
            ok = False
    return ok


def validate_isolation_and_static_safety() -> bool:
    ok = True
    isolation = load_json("data/non-public-static-workbench-visual-system-baseline-public-isolation-audit-v1.json")
    expected = {
        "route_registry_result": "not_registered_as_public_route",
        "sitemap_result": "not_in_sitemap",
        "homepage_link_result": "not_linked_from_homepage",
        "reference_page_link_result": "not_linked_from_reference_pages",
        "language_page_link_result": "not_linked_from_language_page",
        "public_navigation_result": "not_linked_from_public_navigation",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "overall_outcome": "baseline_public_isolation_validated",
    }
    for key, value in expected.items():
        if isolation.get(key) != value:
            error(f"public isolation audit: {key} must be {value}")
            ok = False
    safety = load_json("data/non-public-static-workbench-visual-system-baseline-static-safety-audit-v1.json")
    if safety.get("overall_outcome") != "baseline_static_safety_validated":
        error("static safety audit: invalid overall_outcome")
        ok = False
    for key, required in {
        "prototype_file_results": ["prototype_files_not_modified_in_sprint_41", "only_index_and_css_in_prototype_directory", "no_additional_prototype_files", "no_new_prototype_directories"],
        "html_safety_results": ["no_script_tags", "no_forms", "no_inputs", "no_textarea", "no_file_inputs", "no_buttons", "no_upload_controls", "no_generated_output_regions", "no_external_scripts", "no_external_libraries"],
        "css_safety_results": ["no_imports", "no_external_urls", "no_upload_dropzone_styling", "no_scoring_gauge_styling", "no_red_green_verdict_styling", "no_detector_scanner_naming", "visual_tokens_present", "evidence_field_classes_present", "chamber_boundary_classes_present", "provenance_shadow_classes_present", "output_envelope_classes_present", "responsive_rules_present"],
        "capability_block_results": ["no_engine", "no_classifier", "no_detector", "no_upload", "no_scoring", "no_fake_real", "no_api", "no_analytics", "no_storage", "no_network_calls", "no_deployment_change"],
        "content_safety_results": ["no_real_people", "no_real_companies", "no_real_institutions", "no_real_brands", "no_current_events", "no_political_events", "no_accusations", "no_external_factual_claims", "no_generated_analysis", "no_verified_certified_claims"],
        "python_cache_results": ["no_pycache_tracked", "no_pyc_staged", "no_python_cache_committed"],
    }.items():
        if not set(required).issubset(set(safety.get(key, []))):
            error(f"static safety audit: missing {key}")
            ok = False
    return ok


def validate_prototype_files() -> bool:
    ok = True
    if not INDEX_PATH.is_file() or not CSS_PATH.is_file():
        error("prototype index and css must exist")
        return False
    files = {p.name for p in PROTO_DIR.iterdir() if p.is_file()}
    if files != ALLOWED_FILES:
        error("prototype directory must contain only index.html and prototype.css")
        ok = False
    diff = subprocess.run(["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip()
    staged = subprocess.run(["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip()
    if diff or staged:
        error("prototype files must not be modified or staged in Sprint 41")
        ok = False
    html = INDEX_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    lower_html = html.lower()
    if html.count("<h1") != 1 or "Evidence Posture Workbench" not in html or "Static Prototype" not in html:
        error("prototype html: expected exactly one H1 for Evidence Posture Workbench Static Prototype")
        ok = False
    for forbidden in ["<script", "<form", "<input", "<textarea", "type=\"file\"", "<button", "upload control", "generated output", "fake/real", "probability", "api", "analytics"]:
        if forbidden in lower_html:
            error(f"prototype html: forbidden {forbidden}")
            ok = False
    if 'href="prototype.css"' not in lower_html:
        error("prototype html: must link only to prototype.css")
        ok = False
    for phrase in ["Internal static prototype", "Non-public web surface", "Evidence Chamber", "Governed Evidence Field", "boundary rail", "provenance shadow", "missing context", "Not Assessable", "Refusal Gate", "Output Envelope", "Verification Path"]:
        if phrase.lower() not in lower_html:
            error(f"prototype html: missing locked visual-system language {phrase}")
            ok = False
    for zone in ["zone-boundary-header", "zone-artifact-context", "zone-provenance-context", "zone-missing-information", "zone-state-routing", "zone-refusal-boundary", "zone-output-envelope", "zone-verification-questions"]:
        if zone not in html:
            error(f"prototype html: missing {zone}")
            ok = False
    lower_css = css.lower()
    for forbidden in ["@import", "url(", "dropzone", "gauge", "verdict", "fake", "real", "detector", "scanner"]:
        if forbidden in lower_css:
            error(f"prototype css: forbidden {forbidden}")
            ok = False
    for phrase in ["--background-field", "--chamber-surface", "--boundary-accent", "--provenance-shadow", "evidence-field", "evidence-chamber", "boundary-rail", "output-envelope", "@media"]:
        if phrase.lower() not in lower_css:
            error(f"prototype css: missing {phrase}")
            ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    route_text = json.dumps(routes).lower()
    if "internal_prototypes" in route_text or "evidence-posture-workbench" in route_text:
        error("route-registry: prototype must not be registered")
        ok = False
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [el.text.strip().lower() for el in tree.findall(".//{*}loc") if el.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error("sitemap.xml must remain exactly 4 URLs")
        ok = False
    if any("internal_prototypes" in loc or "evidence-posture-workbench" in loc for loc in locs):
        error("sitemap.xml must not include prototype")
        ok = False
    link_pattern = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for rel in ["index.html", "reference/evidence-posture/index.html", "reference/artifact-subject-separation/index.html", "language/index.html"]:
        if link_pattern.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel}: must not link to prototype")
            ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance_and_registry() -> bool:
    ok = True
    pub = load_json("data/publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
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
    ):
        error("publisher status must be blocked until public-readiness boundary governance")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if g.get("name") == "Non-Public Static Workbench Visual System Baseline Lock Validation Gate"), None)
    if not gate:
        error("baseline lock validation gate missing")
        ok = False
    else:
        for field in ["required_before_non_public_static_workbench_public_readiness_boundary_governance", "required_before_any_interface_prototype_expansion", "required_before_engine_governance"]:
            if gate.get(field) is not True:
                error(f"baseline lock validation gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("baseline lock validation gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in ["public engine", "public classifier", "public tool", "public route", "sitemap", "navigation", "upload", "scoring", "api", "forms", "analytics", "deployment", "dns", "cloudflare", "custom domain launch"]:
            if term not in notes:
                error(f"baseline lock validation gate notes must mention {term}")
                ok = False
    expansion = load_json("data/reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "baseline_lock_validation" not in checks:
        error("reference-expansion-gate: baseline lock validation required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_baseline_lock_validation_alone" not in rules:
        error("reference-expansion-gate: baseline lock validation must not grant public engine eligibility")
        ok = False
    locations = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locations:
            error(f"source-registry: missing {loc}")
            ok = False
    ledger = load_json("data/evidence-ledger.json")
    cmap = load_json("data/claim-source-map.json")
    if not any(c.get("claim_id") == "CLAIM-0047" for c in ledger.get("claims", [])):
        error("evidence-ledger: CLAIM-0047 missing")
        ok = False
    if not any(c.get("claim_id") == "CLAIM-0047" for c in cmap.get("claim_source_links", [])):
        error("claim-source-map: CLAIM-0047 missing")
        ok = False
    if "DEC-059" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-059 missing")
        ok = False
    if "validate_non_public_static_workbench_visual_system_baseline_lock_validation.py" not in (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py must include baseline lock validation validator")
        ok = False
    return ok


def validate_python_cache() -> bool:
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.splitlines()
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.splitlines()
    for rel in tracked + staged:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error("python cache files must not be tracked or staged")
            return False
    return True


def main() -> int:
    parse_paths = [
        "data/non-public-static-workbench-visual-system-baseline-lock-validation-policy.json",
        "data/non-public-static-workbench-visual-system-baseline-lock-validation-results-v1.json",
        "data/non-public-static-workbench-visual-system-baseline-record-validation-v1.json",
        "data/non-public-static-workbench-visual-system-change-control-validation-v1.json",
        "data/non-public-static-workbench-visual-system-baseline-public-isolation-audit-v1.json",
        "data/non-public-static-workbench-visual-system-baseline-static-safety-audit-v1.json",
        "data/publisher-governance-policy.json", "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json", "data/route-registry.json",
    ]
    for rel in parse_paths:
        try:
            load_json(rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"{rel} parse failed: {exc}")
            return 1
    for rel in ["sitemap.xml", "index.html", "reference/evidence-posture/index.html", "reference/artifact-subject-separation/index.html", "language/index.html", *LOCKED_FILES]:
        if not (ROOT / rel).is_file():
            error(f"{rel} must exist and be readable")
            return 1
    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1
    checks = [validate_doctrine, validate_policy, validate_results, validate_record_and_change_control, validate_isolation_and_static_safety, validate_prototype_files, validate_public_safety, validate_governance_and_registry, validate_python_cache]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
