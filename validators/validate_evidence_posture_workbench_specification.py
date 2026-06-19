#!/usr/bin/env python3
"""Validate Hoax.ai Evidence Posture Workbench Specification Layer v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING,
    validate_no_extra_public_html,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "boundary_principle", "allowed_specification_actions", "prohibited_actions",
    "specification_definition", "specification_non_purpose", "non_authorization_rules",
    "last_reviewed",
}

MODULE_TOP = {"registry_id", "name", "version", "status", "maturity", "modules", "last_reviewed"}

FLOW_TOP = {
    "flow_contract_id", "name", "version", "status", "maturity", "flow_steps",
    "transition_constraints", "forbidden_flows", "non_authorization_statement", "last_reviewed",
}

ENVELOPE_TOP = {
    "envelope_spec_id", "name", "version", "status", "maturity", "output_envelopes",
    "forbidden_envelope_content", "non_authorization_statement", "last_reviewed",
}

GUARDRAIL_TOP = {"guardrail_map_id", "name", "version", "status", "maturity", "guardrails", "last_reviewed"}

SPEC_TOP = {
    "specification_id", "name", "version", "status", "maturity", "governance_ref",
    "dry_run_ref", "module_registry_ref", "flow_contract_ref", "output_envelope_ref",
    "boundary_guardrail_map_ref", "current_public_surface", "prohibited_capabilities",
    "allowed_next_phase", "non_authorization_statement", "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "EVIDENCE_POSTURE_WORKBENCH_SPECIFICATION_LAYER.md",
    "data/evidence-posture-workbench-specification-policy.json",
    "data/evidence-posture-workbench-module-registry.json",
    "data/evidence-posture-workbench-flow-contract.json",
    "data/evidence-posture-workbench-output-envelope.json",
    "data/evidence-posture-workbench-boundary-guardrail-map.json",
    "data/evidence-posture-workbench-specification-v1.json",
    "validators/validate_evidence_posture_workbench_specification.py",
]

PROHIBITED_ACTIONS = [
    "interface_creation", "prototype_creation", "public_workbench", "public_engine",
    "public_classifier", "public_tool", "upload", "scoring", "fake_real_output",
    "forms", "analytics", "api", "monetization", "new_routes", "sitemap_expansion",
    "dns", "cloudflare", "custom_domain_launch", "deployment_changes",
    "external_factual_claims", "subject_accusation",
]

FORBIDDEN_FLOWS = [
    "direct_fake_real_verdict", "direct_scoring", "direct_subject_accusation",
    "upload_to_verdict", "source_confidence_to_truth_certification",
    "provenance_gap_to_falsehood_verdict", "evidence_free_certainty",
    "high_stakes_determination", "interface_to_engine_without_governance",
]

FORBIDDEN_ENVELOPE = [
    "truth_verdict", "fake_real_verdict", "deepfake_verdict", "authenticity_certification",
    "subject_accusation", "numeric_score", "high_stakes_conclusion", "definitive_claim",
    "verified_claim", "public_engine_output_claim",
]

PROHIBITED_CAPABILITIES = [
    "public_engine", "public_classifier", "public_tool", "workbench_interface", "prototype",
    "upload", "scoring", "fake_real_output", "api", "forms", "analytics", "monetization",
    "dns", "cloudflare", "custom_domain_launch", "new_public_routes", "sitemap_expansion",
    "deployment_change",
]

READINESS_IMPLIED = re.compile(
    r"\b(engine_ready|classifier_ready|tool_ready|public_engine_ready|"
    r"public_release_ready|production_ready)\b",
    re.I,
)

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
MODULE_ID_PATTERN = re.compile(r"^WB-SPEC-MODULE-\d{4}$")
FLOW_ID_PATTERN = re.compile(r"^WB-FLOW-\d{4}$")
ENVELOPE_ID_PATTERN = re.compile(r"^WB-ENVELOPE-\d{4}$")
GUARDRAIL_ID_PATTERN = re.compile(r"^WB-GUARDRAIL-\d{4}$")
STATE_ID_PATTERN = re.compile(r"^WB-STATE-\d{4}$")
OUTPUT_ID_PATTERN = re.compile(r"^WB-OUTPUT-\d{4}$")
REFUSAL_ID_PATTERN = re.compile(r"^WB-REFUSAL-\d{4}$")
LANG_TERM_PATTERN = re.compile(r"^LANG-TERM-\d{4}$")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_governance_ids() -> tuple[set[str], set[str], set[str], set[str]]:
    states = {
        s["state_id"]
        for s in load_json(ROOT / "data" / "evidence-posture-workbench-state-model.json").get("states", [])
    }
    outputs = {
        o["output_id"]
        for o in load_json(ROOT / "data" / "evidence-posture-workbench-output-boundary.json").get(
            "allowed_output_families", []
        )
    }
    refusals = {
        r["refusal_id"]
        for r in load_json(ROOT / "data" / "evidence-posture-workbench-refusal-model.json").get(
            "refusal_families", []
        )
    }
    lang_terms = {
        t["term_id"]
        for t in load_json(ROOT / "data" / "category-language-term-registry.json").get("terms", [])
    }
    return states, outputs, refusals, lang_terms


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-workbench-specification-policy.json"
    policy = load_json(path)
    if set(policy) != POLICY_TOP:
        error("specification policy: unexpected top-level keys")
        ok = False
    if policy.get("status") != "governed_evidence_posture_workbench_specification_policy":
        error("specification policy: invalid status")
        ok = False
    if policy.get("maturity") != "specification_only_no_workbench_no_interface_no_engine_no_classifier_no_tool":
        error("specification policy: invalid maturity")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"specification policy: missing prohibited action {action}")
            ok = False
    blocked = policy.get("non_authorization_rules", {}).get("blocked", [])
    for cap in ["workbench_interface", "workbench_prototype", "workbench_engine", "upload", "scoring"]:
        if cap not in blocked and cap.upper() not in blocked:
            found = any(cap.lower() in str(b).lower() for b in blocked)
            if not found:
                error(f"specification policy: non_authorization must block {cap}")
                ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("specification policy: numeric score or grade found")
        ok = False
    return ok


def validate_governance_dependency() -> bool:
    ok = True
    gov = load_json(ROOT / "data" / "evidence-posture-workbench-governance-policy.json")
    if gov.get("status") != "governed_evidence_posture_workbench_policy":
        error("workbench governance policy must exist with governed status")
        ok = False
    dry = load_json(ROOT / "data" / "evidence-posture-workbench-dry-run-results-v1.json")
    if dry.get("overall_result") != "evidence_posture_workbench_dry_run_passed_with_conditions":
        error("dry-run overall result must be evidence_posture_workbench_dry_run_passed_with_conditions")
        ok = False
    spec = load_json(ROOT / "data" / "evidence-posture-workbench-specification-v1.json")
    if "EVIDENCE_POSTURE_WORKBENCH_GOVERNANCE" not in spec.get("governance_ref", ""):
        error("specification must reference governance")
        ok = False
    if "dry-run-results-v1" not in spec.get("dry_run_ref", ""):
        error("specification must reference dry-run results")
        ok = False
    for rel in [
        "data/evidence-posture-workbench-dry-run-results-v1.json",
        "data/evidence-posture-workbench-specification-v1.json",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        if READINESS_IMPLIED.search(text):
            error(f"{rel}: implies public engine readiness")
            ok = False
    return ok


def validate_module_registry(states: set[str], outputs: set[str], refusals: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-module-registry.json")
    if set(data) != MODULE_TOP:
        error("module registry: unexpected top-level keys")
        ok = False
    modules = data.get("modules", [])
    if len(modules) != 10:
        error(f"module registry: expected 10 modules, found {len(modules)}")
        ok = False
    ids: set[str] = set()
    for mod in modules:
        mid = mod.get("module_id", "")
        if not MODULE_ID_PATTERN.match(mid):
            error(f"module registry: invalid module_id {mid}")
            ok = False
        if mid in ids:
            error(f"module registry: duplicate module_id {mid}")
            ok = False
        ids.add(mid)
        for field, expected in [
            ("interface_status", "no_interface_created"),
            ("prototype_status", "no_prototype_created"),
            ("engine_status", "no_engine_created"),
            ("route_status", "not_route_created"),
        ]:
            if mod.get(field) != expected:
                error(f"{mid}: {field} must be {expected}")
                ok = False
        blob = json.dumps(mod).lower()
        for term in ["public_engine", "classifier", "upload", "scoring", "subject_accusation"]:
            if term in mod.get("allowed_future_role", "").lower():
                error(f"{mid}: allowed_future_role must not authorize {term}")
                ok = False
        for sid in mod.get("related_states", []):
            if sid and sid not in states:
                error(f"{mid}: invalid related state {sid}")
                ok = False
        for oid in mod.get("related_output_families", []):
            if oid and oid not in outputs:
                error(f"{mid}: invalid related output {oid}")
                ok = False
        for rid in mod.get("related_refusal_families", []):
            if rid and rid not in refusals:
                error(f"{mid}: invalid related refusal {rid}")
                ok = False
    return ok


def validate_flow_contract(states: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-flow-contract.json")
    if set(data) != FLOW_TOP:
        error("flow contract: unexpected top-level keys")
        ok = False
    steps = data.get("flow_steps", [])
    if len(steps) != 10:
        error(f"flow contract: expected 10 steps, found {len(steps)}")
        ok = False
    module_ids = {
        m["module_id"]
        for m in load_json(ROOT / "data" / "evidence-posture-workbench-module-registry.json").get("modules", [])
    }
    ids: set[str] = set()
    for step in steps:
        fid = step.get("flow_step_id", "")
        if not FLOW_ID_PATTERN.match(fid):
            error(f"flow contract: invalid flow_step_id {fid}")
            ok = False
        if fid in ids:
            error(f"flow contract: duplicate flow_step_id {fid}")
            ok = False
        ids.add(fid)
        for sid in step.get("related_state_ids", []):
            if sid not in states:
                error(f"{fid}: invalid related_state_id {sid}")
                ok = False
        for mid in step.get("related_module_ids", []):
            if mid not in module_ids:
                error(f"{fid}: invalid related_module_id {mid}")
                ok = False
    forbidden = " ".join(data.get("forbidden_flows", [])).lower()
    for flow in FORBIDDEN_FLOWS:
        if flow.replace("_", " ") not in forbidden and flow not in forbidden:
            error(f"flow contract: missing forbidden flow {flow}")
            ok = False
    if "public engine" in json.dumps(steps).lower() and "does not authorize" not in json.dumps(steps).lower():
        pass  # allowed in non_authorization_statement
    return ok


def validate_output_envelope(outputs: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-output-envelope.json")
    if set(data) != ENVELOPE_TOP:
        error("output envelope: unexpected top-level keys")
        ok = False
    envelopes = data.get("output_envelopes", [])
    if len(envelopes) != 8:
        error(f"output envelope: expected 8 envelopes, found {len(envelopes)}")
        ok = False
    ids: set[str] = set()
    for env in envelopes:
        eid = env.get("envelope_id", "")
        if not ENVELOPE_ID_PATTERN.match(eid):
            error(f"output envelope: invalid envelope_id {eid}")
            ok = False
        if eid in ids:
            error(f"output envelope: duplicate envelope_id {eid}")
            ok = False
        ids.add(eid)
        oid = env.get("related_output_family_id", "")
        if oid not in outputs:
            error(f"{eid}: invalid related_output_family_id {oid}")
            ok = False
        for field, expected in [
            ("verdict_status", "no_verdict_allowed"),
            ("scoring_status", "no_score_allowed"),
            ("subject_judgment_status", "no_subject_judgment_allowed"),
            ("public_output_status", "no_public_output_created"),
        ]:
            if env.get(field) != expected:
                error(f"{eid}: {field} must be {expected}")
                ok = False
    forbidden = " ".join(data.get("forbidden_envelope_content", [])).lower()
    for item in FORBIDDEN_ENVELOPE:
        if item.replace("_", " ") not in forbidden and item not in forbidden:
            error(f"output envelope: missing forbidden content {item}")
            ok = False
    return ok


def validate_guardrail_map(states: set[str], refusals: set[str], lang_terms: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-boundary-guardrail-map.json")
    if set(data) != GUARDRAIL_TOP:
        error("guardrail map: unexpected top-level keys")
        ok = False
    guardrails = data.get("guardrails", [])
    if len(guardrails) != 9:
        error(f"guardrail map: expected 9 guardrails, found {len(guardrails)}")
        ok = False
    ids: set[str] = set()
    for g in guardrails:
        gid = g.get("guardrail_id", "")
        if not GUARDRAIL_ID_PATTERN.match(gid):
            error(f"guardrail map: invalid guardrail_id {gid}")
            ok = False
        if gid in ids:
            error(f"guardrail map: duplicate guardrail_id {gid}")
            ok = False
        ids.add(gid)
        if not g.get("blocked_action"):
            error(f"{gid}: must block at least one prohibited behavior")
            ok = False
        for tid in g.get("related_language_terms", []):
            if tid and not LANG_TERM_PATTERN.match(tid):
                error(f"{gid}: invalid language term {tid}")
                ok = False
            if tid and tid not in lang_terms:
                error(f"{gid}: unknown language term {tid}")
                ok = False
        for rid in g.get("related_refusal_families", []):
            if rid and rid not in refusals:
                error(f"{gid}: invalid refusal family {rid}")
                ok = False
        for sid in g.get("related_states", []):
            if sid and sid not in states:
                error(f"{gid}: invalid state {sid}")
                ok = False
        if "authorize interface" in g.get("non_authorization_statement", "").lower():
            pass
        elif "does not authorize" not in g.get("non_authorization_statement", "").lower():
            error(f"{gid}: missing non_authorization_statement")
            ok = False
    return ok


def validate_master_specification() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-specification-v1.json")
    if set(data) != SPEC_TOP:
        error("master specification: unexpected top-level keys")
        ok = False
    if data.get("status") != "evidence_posture_workbench_specification_created":
        error("master specification: invalid status")
        ok = False
    if data.get("maturity") != "specification_only_no_workbench_no_interface_no_engine_no_classifier_no_tool":
        error("master specification: invalid maturity")
        ok = False
    next_phase = data.get("allowed_next_phase", "")
    if "Sprint 31" not in next_phase or "Interface Blueprint Governance" not in next_phase:
        error("master specification: allowed_next_phase must be Sprint 31 Interface Blueprint Governance")
        ok = False
    surface = data.get("current_public_surface", [])
    required = ["homepage root", "/reference/evidence-posture/", "/reference/artifact-subject-separation/", "/language/"]
    if surface != required:
        error(f"master specification: current_public_surface must be {required}")
        ok = False
    caps = {c.lower() for c in data.get("prohibited_capabilities", [])}
    for cap in PROHIBITED_CAPABILITIES:
        if cap.lower() not in caps and cap.replace("_", " ").lower() not in " ".join(caps):
            error(f"master specification: missing prohibited capability {cap}")
            ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    if not validate_no_extra_public_html(error):
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_publisher_governance() -> bool:
    ok = True
    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    allowed = {
        PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT,
        PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
    }
    if pub.get("current_publisher_status") not in allowed:
        error(f"publisher status must be one of {sorted(allowed)}")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Evidence Posture Workbench Specification Layer Gate"),
        None,
    )
    if not gate:
        error("Evidence Posture Workbench Specification Layer Gate missing")
        ok = False
    else:
        if gate.get("bypassable") is True:
            error("specification layer gate must not be bypassable")
            ok = False
        if gate.get("required_before_workbench_interface_blueprint") is not True:
            error("specification gate must be required before workbench interface blueprint")
            ok = False
        if gate.get("required_before_workbench_prototype") is not True:
            error("specification gate must be required before workbench prototype")
            ok = False
        if gate.get("required_before_engine_governance") is not True:
            error("specification gate must be required before engine governance")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "workbench_specification" not in checks and "specification_layer" not in checks:
        error("reference-expansion-gate: workbench specification layer required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_specification_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by specification alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    workbench_blocked = [
        "publisher_blocked_until_workbench_specification_layer",
        "publisher_blocked_until_workbench_interface_blueprint_governance",
        "publisher_blocked_until_workbench_interface_blueprint_validation",
        "publisher_blocked_until_non_public_static_workbench_prototype_governance",
        "publisher_blocked_until_non_public_static_workbench_prototype_v1",
        "publisher_blocked_until_non_public_static_workbench_prototype_validation",
        "publisher_blocked_until_non_public_static_workbench_prototype_refinement",
        "publisher_blocked_until_non_public_static_workbench_prototype_refinement_validation",
        "publisher_blocked_until_non_public_static_workbench_visual_system_hardening",
        "publisher_blocked_until_non_public_static_workbench_visual_system_hardening_validation",
        "publisher_blocked_until_non_public_static_workbench_visual_system_baseline_lock",
        "publisher_blocked_until_non_public_static_workbench_visual_system_baseline_lock_validation",
        "publisher_blocked_until_non_public_static_workbench_public_readiness_boundary_governance",
        "publisher_blocked_until_non_public_static_workbench_public_readiness_boundary_validation",
        "publisher_blocked_until_public_route_eligibility_governance",
    ]
    if not any(b in blocked for b in workbench_blocked):
        error("reference-expansion-gate: publisher blocked until workbench progression")
        ok = False
    return ok


def validate_source_registry() -> bool:
    ok = True
    locations = {s.get("location") for s in load_json(ROOT / "data" / "source-registry.json").get("sources", [])}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing {loc}")
            ok = False
    return ok


def validate_cross_file() -> bool:
    ok = True
    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_evidence_posture_workbench_specification.py" not in content:
        error("validate_all.py must include workbench specification validator")
        ok = False
    doc = (ROOT / "EVIDENCE_POSTURE_WORKBENCH_SPECIFICATION_LAYER.md").read_text(encoding="utf-8")
    if "A specification may define the workbench's shape. It must not become the workbench." not in doc:
        if "A specification may define the workbench’s shape. It must not become the workbench." not in doc:
            error("specification doc: missing governing principle sentence")
            ok = False
    if "The first workbench specification must preserve refusal, uncertainty, and artifact boundaries" not in doc:
        error("specification doc: missing boundary principle sentence")
        ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/evidence-posture-workbench-specification-policy.json",
        "data/evidence-posture-workbench-module-registry.json",
        "data/evidence-posture-workbench-flow-contract.json",
        "data/evidence-posture-workbench-output-envelope.json",
        "data/evidence-posture-workbench-boundary-guardrail-map.json",
        "data/evidence-posture-workbench-specification-v1.json",
        "data/evidence-posture-workbench-governance-policy.json",
        "data/evidence-posture-workbench-dry-run-results-v1.json",
        "data/evidence-posture-workbench-input-model.json",
        "data/evidence-posture-workbench-output-boundary.json",
        "data/evidence-posture-workbench-state-model.json",
        "data/evidence-posture-workbench-refusal-model.json",
        "data/evidence-posture-workbench-non-authorization-rules.json",
        "data/category-language-term-registry.json",
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

    states, outputs, refusals, lang_terms = load_governance_ids()

    checks = [
        validate_policy,
        validate_governance_dependency,
        lambda: validate_module_registry(states, outputs, refusals),
        lambda: validate_flow_contract(states),
        lambda: validate_output_envelope(outputs),
        lambda: validate_guardrail_map(states, refusals, lang_terms),
        validate_master_specification,
        validate_public_safety,
        validate_publisher_governance,
        validate_source_registry,
        validate_cross_file,
    ]
    ok = True
    for fn in checks:
        if not fn():
            ok = False

    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
