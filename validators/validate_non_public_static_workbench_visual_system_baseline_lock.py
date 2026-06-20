#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Visual System Baseline Lock v1."""

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
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION,
    validate_public_surface,
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

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
PROTO_REL = "_internal_prototypes/evidence-posture-workbench"
INDEX_PATH = PROTO_DIR / "index.html"
CSS_PATH = PROTO_DIR / "prototype.css"
ALLOWED_FILES = {"index.html", "prototype.css"}
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
MATURE = "baseline_lock_only_no_prototype_modification_no_engine_no_classifier_no_public_route"
TOKEN_FAMILIES = ["background_field", "chamber_surface", "chamber_edge", "graphite_text", "muted_text", "boundary_accent", "provenance_line", "provenance_shadow", "absence_field", "not_assessable_surface", "refusal_surface", "output_envelope_surface", "verification_path_line", "subtle_rule", "focus_ring", "mobile_spacing"]
PATTERNS = ["Evidence Field", "Evidence Chamber", "Boundary Rail", "Provenance Shadow", "Missing Context Absence", "Not-Assessable Restraint", "Refusal Gate", "Output Envelope", "Verification Path"]
ANTIPATTERNS = ["detector_dashboard", "scanner_ui", "upload_dashboard", "red_green_fake_real_interface", "truth_meter", "risk_gauge", "probability_meter", "forensic_game_interface", "policing_dashboard", "saas_analytics_dashboard", "product_landing_page_cta", "try_it_now_interface", "black_cyber_dashboard_default"]
VISUAL_ELEMENTS = ["evidence_field_background", "evidence_chamber_frame", "chamber_edge", "boundary_rail", "provenance_shadow_layer", "missing_context_absence_field", "not_assessable_restraint_surface", "refusal_gate_surface", "output_envelope_containment", "verification_path_line", "mobile_spacing_rhythm", "focus_ring_behavior"]
LOCKED_BOUNDARIES = ["no_public_route", "no_sitemap_entry", "no_public_navigation", "no_js", "no_forms", "no_inputs", "no_upload", "no_scoring", "no_fake_real", "no_engine", "no_classifier", "no_api", "no_analytics", "no_deployment_change"]
PROHIBITED_ACTIONS = ["modifying prototype files", "new prototype files", "prototype expansion", "public route creation", "sitemap expansion", "public navigation link", "interface behavior", "javascript", "forms", "inputs", "upload", "scoring", "fake/real output", "generated output", "engine", "classifier", "detector", "api", "analytics", "storage", "network calls", "monetization", "dns", "cloudflare", "custom domain launch", "deployment changes", "external factual claims", "subject accusation", "python cache file commit"]
FUTURE_REQ = ["future sprint required", "decision log entry required", "allowed files must be explicit", "prohibited changes must be explicit", "validator required", "boundary audit required", "public isolation audit required", "static safety audit required", "source registry update required", "evidence ledger update only if claim added", "no public route without separate public route governance", "no engine/classifier/upload/scoring authorization without separate engine governance"]
INFORMAL = ["unscheduled CSS edits", "unscheduled HTML edits", "visual redesign without DEC entry", "adding JS", "adding forms", "adding inputs", "adding upload controls", "adding scoring visuals", "adding fake/real language", "adding public links", "adding sitemap entries", "adding route registry entries", "adding deployment changes"]
SOURCE_LOCS = [
    "NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_V1.md",
    "data/non-public-static-workbench-visual-system-baseline-lock-policy.json",
    "data/non-public-static-workbench-visual-system-baseline-lock-record-v1.json",
    "data/non-public-static-workbench-visual-system-baseline-locked-elements-v1.json",
    "data/non-public-static-workbench-visual-system-change-control-v1.json",
    "data/non-public-static-workbench-visual-system-baseline-boundary-audit-v1.json",
    "validators/validate_non_public_static_workbench_visual_system_baseline_lock.py",
]
NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def has_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower() in text or item.lower().replace("_", " ") in text for item in required)


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "non-public-static-workbench-visual-system-baseline-lock-policy.json"
    data = load_json(path)
    required = {"policy_id", "name", "version", "status", "maturity", "governing_principle", "identity_principle", "allowed_lock_actions", "prohibited_actions", "locked_files", "baseline_scope", "change_control_requirement", "non_authorization_rules", "last_reviewed"}
    if not required.issubset(data):
        error("baseline lock policy: missing required top-level fields")
        ok = False
    if data.get("status") != "governed_non_public_static_workbench_visual_system_baseline_lock_policy":
        error("baseline lock policy: invalid status")
        ok = False
    if data.get("maturity") != MATURE:
        error("baseline lock policy: invalid maturity")
        ok = False
    if data.get("locked_files") != LOCKED_FILES:
        error("baseline lock policy: locked_files must be exactly prototype index and css")
        ok = False
    if not has_all(data.get("prohibited_actions", []), PROHIBITED_ACTIONS):
        error("baseline lock policy: missing prohibited actions")
        ok = False
    change = data.get("change_control_requirement", "").lower()
    for term in ["future governed sprint", "explicit allowed files", "validator", "boundary audit", "public-isolation", "decision log"]:
        if term not in change:
            error(f"baseline lock policy: change control missing {term}")
            ok = False
    blocked = " ".join(data.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in ["public_workbench", "engine", "classifier", "upload", "scoring", "api", "routes", "sitemap", "deployment", "dns", "cloudflare", "custom_domain_launch", "public_tool_behavior", "prototype_expansion", "production_readiness", "python_cache_commit"]:
        if term not in blocked and term.replace("_", " ") not in blocked:
            error(f"baseline lock policy: non-authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("baseline lock policy: numeric score, grade, percentage, or SEO score found")
        ok = False
    return ok


def validate_record() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-baseline-lock-record-v1.json")
    if data.get("status") != "non_public_static_workbench_visual_system_baseline_locked":
        error("baseline lock record: invalid status")
        ok = False
    if data.get("maturity") != MATURE:
        error("baseline lock record: invalid maturity")
        ok = False
    if data.get("locked_baseline_source") != "Sprint 38 hardening validated by Sprint 39":
        error("baseline lock record: invalid locked_baseline_source")
        ok = False
    if data.get("locked_files") != LOCKED_FILES:
        error("baseline lock record: locked_files must be exact")
        ok = False
    if data.get("allowed_next_phase") != "Sprint 41 — Non-Public Static Workbench Visual System Baseline Lock Validation v1":
        error("baseline lock record: invalid allowed_next_phase")
        ok = False
    for group, required in {
        "validation_refs": ["non_public_static_visual_system_hardening_validated", "token_system_validated", "pattern_system_validated", "visual_antipattern_blocking_validated", "hardening_public_isolation_validated", "hardening_static_safety_validated"],
        "locked_identity": ["evidence_chamber", "governed_evidence_field", "boundary_rail", "provenance_shadow", "missing_context_absence", "not_assessable_restraint", "refusal_gate", "output_envelope", "verification_path", "anti_detector_identity"],
        "locked_public_surface_status": ["four_public_urls_only", "not_registered_as_public_route", "not_in_sitemap", "not_linked_from_public_navigation"],
        "prohibited_capabilities": ["prototype_modification_in_sprint_40", "new_prototype_files", "public_route", "sitemap_entry", "public_navigation", "engine", "classifier", "detector", "upload", "scoring", "fake_real_output", "forms", "inputs", "API", "analytics", "storage", "network_calls", "monetization", "DNS", "Cloudflare", "custom_domain_launch", "deployment_change"],
    }.items():
        if not set(required).issubset(set(data.get(group, []))):
            error(f"baseline lock record: missing {group}")
            ok = False
    return ok


def validate_locked_elements() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-baseline-locked-elements-v1.json")
    checks = {
        "locked_visual_elements": VISUAL_ELEMENTS,
        "locked_token_families": TOKEN_FAMILIES,
        "locked_patterns": PATTERNS,
        "locked_antipattern_blocks": ANTIPATTERNS,
        "locked_boundaries": LOCKED_BOUNDARIES,
    }
    for key, required in checks.items():
        if not set(required).issubset(set(data.get(key, []))):
            error(f"locked elements: missing {key}")
            ok = False
    return ok


def validate_change_control() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-change-control-v1.json")
    if data.get("controlled_files") != LOCKED_FILES:
        error("change control: controlled_files must be exact")
        ok = False
    if not has_all(data.get("future_change_requirements", []), FUTURE_REQ):
        error("change control: missing future change requirements")
        ok = False
    if not has_all(data.get("prohibited_informal_changes", []), INFORMAL):
        error("change control: missing prohibited informal changes")
        ok = False
    if not has_all(data.get("required_future_validation", []), ["validate_all.py", "dedicated validator", "public surface", "python cache"]):
        error("change control: missing required future validation")
        ok = False
    return ok


def validate_boundary_audit() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "non-public-static-workbench-visual-system-baseline-boundary-audit-v1.json")
    if data.get("audited_files") != LOCKED_FILES:
        error("boundary audit: audited_files must be exact")
        ok = False
    if data.get("overall_outcome") != "non_public_static_visual_system_baseline_lock_boundary_validated":
        error("boundary audit: invalid overall_outcome")
        ok = False
    for group, keys in {
        "prototype_file_status": ["prototype_files_not_modified_in_sprint_40", "no_additional_prototype_files", "no_new_prototype_directories"],
        "public_surface_results": ["no_route_registry_entry", "no_sitemap_entry", "no_homepage_link", "no_public_reference_links", "no_language_page_link", "no_public_navigation", "public_surface_unchanged_four_urls"],
        "locked_boundary_results": ["visual_baseline_locked", "change_control_required_for_future_modification", "anti_detector_baseline_preserved", "evidence_field_baseline_preserved", "evidence_chamber_baseline_preserved", "static_only_boundary_preserved", "non_public_boundary_preserved"],
        "capability_block_results": ["no_engine", "no_classifier", "no_detector", "no_upload", "no_scoring", "no_fake_real", "no_api", "no_analytics", "no_storage", "no_network_calls", "no_deployment_change"],
        "python_cache_results": ["no_pycache_tracked", "no_pyc_staged", "no_python_cache_committed"],
    }.items():
        for key in keys:
            if key not in data.get(group, {}):
                error(f"boundary audit: missing {group}.{key}")
                ok = False
    return ok


def validate_prototype_and_public_safety() -> bool:
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
        error("prototype files must not be modified or staged in Sprint 40")
        ok = False
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    for route in routes:
        if "internal_prototypes" in route.get("path", "").lower() or PROTO_REL.lower() in route.get("path", "").lower():
            error("route-registry: prototype must not be registered")
            ok = False
    locs = [el.text.strip().lower() for el in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if el.text]
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
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION,
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
    ):
        error(f"publisher status must be {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION}")
        ok = False
    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next((g for g in gates if g.get("name") == "Non-Public Static Workbench Visual System Baseline Lock Gate"), None)
    if not gate:
        error("Non-Public Static Workbench Visual System Baseline Lock Gate missing")
        ok = False
    else:
        for field in ["required_before_non_public_static_workbench_visual_system_baseline_lock_validation", "required_before_any_interface_prototype_expansion", "required_before_engine_governance"]:
            if gate.get(field) is not True:
                error(f"baseline lock gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("baseline lock gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in ["public engine", "public classifier", "public tool", "public route", "sitemap", "navigation", "upload", "scoring", "api", "forms", "analytics", "deployment", "dns", "cloudflare", "custom domain launch"]:
            if term not in notes:
                error(f"baseline lock gate notes must mention {term}")
                ok = False
    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "non_public_static_workbench_visual_system_baseline_lock" not in checks:
        error("reference-expansion-gate: baseline lock required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_baseline_lock_alone" not in rules:
        error("reference-expansion-gate: baseline lock must not grant public engine eligibility")
        ok = False
    locations = {s.get("location") for s in load_json(ROOT / "data" / "source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locations:
            error(f"source-registry: missing {loc}")
            ok = False
    if "validate_non_public_static_workbench_visual_system_baseline_lock.py" not in (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8"):
        error("validate_all.py must include baseline lock validator")
        ok = False
    if "DEC-058" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DECISION_LOG.md: DEC-058 missing")
        ok = False
    ledger = load_json(ROOT / "data" / "evidence-ledger.json")
    cmap = load_json(ROOT / "data" / "claim-source-map.json")
    if not any(c.get("claim_id") == "CLAIM-0046" for c in ledger.get("claims", [])):
        error("evidence-ledger: CLAIM-0046 missing")
        ok = False
    if not any(c.get("claim_id") == "CLAIM-0046" for c in cmap.get("claim_source_links", [])):
        error("claim-source-map: CLAIM-0046 missing")
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
        "data/non-public-static-workbench-visual-system-baseline-lock-policy.json",
        "data/non-public-static-workbench-visual-system-baseline-lock-record-v1.json",
        "data/non-public-static-workbench-visual-system-baseline-locked-elements-v1.json",
        "data/non-public-static-workbench-visual-system-change-control-v1.json",
        "data/non-public-static-workbench-visual-system-baseline-boundary-audit-v1.json",
        "data/non-public-static-workbench-visual-system-hardening-validation-results-v1.json",
        "data/non-public-static-workbench-visual-system-token-validation-v1.json",
        "data/non-public-static-workbench-visual-system-pattern-validation-v1.json",
        "data/non-public-static-workbench-visual-system-antipattern-validation-v1.json",
        "data/non-public-static-workbench-visual-system-public-isolation-audit-v1.json",
        "data/non-public-static-workbench-visual-system-static-safety-audit-v1.json",
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
    for rel in ["sitemap.xml", "index.html", "reference/evidence-posture/index.html", "reference/artifact-subject-separation/index.html", "language/index.html", *LOCKED_FILES]:
        if not (ROOT / rel).is_file():
            error(f"{rel} must exist and be readable")
            return 1
    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1
    checks = [validate_policy, validate_record, validate_locked_elements, validate_change_control, validate_boundary_audit, validate_prototype_and_public_safety, validate_governance_and_registry, validate_python_cache]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
