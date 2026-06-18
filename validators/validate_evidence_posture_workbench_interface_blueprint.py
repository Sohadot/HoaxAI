#!/usr/bin/env python3
"""Validate Hoax.ai Evidence Posture Workbench Interface Blueprint Governance v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
    validate_no_extra_public_html,
    validate_public_surface,
)

POLICY_TOP = {
    "policy_id", "name", "version", "status", "maturity", "governing_principle",
    "interface_boundary_principle", "allowed_blueprint_actions", "prohibited_actions",
    "blueprint_definition", "blueprint_non_purpose", "non_authorization_rules",
    "conceptual_interface_identity_policy", "last_reviewed",
}

ZONE_TOP = {"registry_id", "name", "version", "status", "maturity", "zones", "last_reviewed"}

COMPONENT_TOP = {"registry_id", "name", "version", "status", "maturity", "components", "last_reviewed"}

STATE_TOP = {
    "contract_id", "name", "version", "status", "maturity", "interface_states",
    "forbidden_state_behaviors", "non_authorization_statement", "last_reviewed",
}

COPY_TOP = {
    "ruleset_id", "name", "version", "status", "maturity", "allowed_copy_patterns",
    "prohibited_copy_patterns", "required_boundary_phrases", "non_authorization_statement",
    "last_reviewed",
}

A11Y_TOP = {
    "ruleset_id", "name", "version", "status", "maturity", "accessibility_rules",
    "performance_rules", "dependency_rules", "motion_rules", "non_authorization_statement",
    "last_reviewed",
}

BLUEPRINT_TOP = {
    "blueprint_id", "name", "version", "status", "maturity", "specification_ref",
    "zone_registry_ref", "component_registry_ref", "interface_state_contract_ref",
    "copy_boundaries_ref", "accessibility_performance_rules_ref", "current_public_surface",
    "prohibited_capabilities", "allowed_next_phase", "non_authorization_statement",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "EVIDENCE_POSTURE_WORKBENCH_INTERFACE_BLUEPRINT_GOVERNANCE.md",
    "data/evidence-posture-workbench-interface-blueprint-policy.json",
    "data/evidence-posture-workbench-interface-zone-registry.json",
    "data/evidence-posture-workbench-interface-component-registry.json",
    "data/evidence-posture-workbench-interface-state-contracts.json",
    "data/evidence-posture-workbench-interface-copy-boundaries.json",
    "data/evidence-posture-workbench-interface-accessibility-performance-rules.json",
    "data/evidence-posture-workbench-interface-blueprint-v1.json",
    "validators/validate_evidence_posture_workbench_interface_blueprint.py",
]

PROHIBITED_ACTIONS = [
    "interface_creation", "prototype_creation", "public_workbench", "public_engine",
    "public_classifier", "public_tool", "upload", "scoring", "fake_real_output",
    "forms", "analytics", "api", "monetization", "new_routes", "sitemap_expansion",
    "dns", "cloudflare", "custom_domain_launch", "deployment_changes",
    "external_factual_claims", "subject_accusation",
]

REQUIRED_IDENTITY_TRAITS = [
    "artifact_first_framing", "boundary_first_layout", "posture_state_architecture",
    "provenance_shadow", "not_assessable_as_protected_state", "refusal_as_governance",
    "output_envelope_containment", "no_verdict_gravity",
]

REQUIRED_ALLOWED_METAPHORS = [
    "evidence_chamber", "posture_field", "boundary_rail", "provenance_shadow",
    "refusal_gate", "output_envelope", "not_assessable_lock",
]

FORBIDDEN_METAPHORS = [
    "detector", "scanner", "truth_meter", "risk_score", "fake_real_switch",
    "upload_machine", "forensic_game", "lie_detector", "courtroom_verdict",
    "policing_dashboard", "saas_analytics_dashboard",
]

FORBIDDEN_STATE_BEHAVIORS = [
    "fake_real_display", "score_display", "detector_result_display",
    "subject_accusation_display", "upload_ready_display", "verified_certified_display",
    "public_engine_output_display", "api_ready_display",
]

ALLOWED_COPY = [
    "artifact-focused language", "evidence posture language",
    "uncertainty-preserving language", "not-assessable language",
    "output-boundary language", "source-context language", "provenance-gap language",
    "verification-question language",
]

PROHIBITED_COPY = [
    "detect language", "fake/real language", "upload now language",
    "submit evidence language", "score language", "verified/certified language",
    "truth machine language", "accusation language", "product/SaaS/service claims",
    "API language", "public engine claims", "try it now language",
]

REQUIRED_BOUNDARY_PHRASES = [
    "This interface blueprint does not create a public workbench.",
    "The future workbench must not issue truth verdicts.",
    "The future workbench must not classify fake or real.",
    "The future workbench must not score evidence.",
    "The future workbench must not judge subjects.",
    "The future workbench must preserve artifact-subject separation.",
]

A11Y_REQUIRED = [
    "keyboard navigability", "semantic HTML", "one primary H1",
    "readable contrast", "visible focus", "clear refusal state wording",
    "text fallback", "no meaning conveyed by color alone", "reduced motion",
]

PERF_REQUIRED = [
    "dependency-light", "no external libraries", "no external scripts",
    "no WebGL", "no canvas", "no analytics", "no network calls",
    "no storage", "mobile stability",
]

PROHIBITED_CAPABILITIES = [
    "public_engine", "public_classifier", "public_tool", "workbench_interface",
    "prototype", "upload", "scoring", "fake_real_output", "api", "forms",
    "analytics", "monetization", "dns", "cloudflare", "custom_domain_launch",
    "new_public_routes", "sitemap_expansion", "deployment_change",
]

DETECTOR_UI_PATTERN = re.compile(
    r"\b(upload dashboard|score dashboard|fake.?real classifier|detector ui|"
    r"saas analytics|interface.?ready|prototype.?ready|ready for public use)\b",
    re.I,
)

NUMERIC_SCORE_PATTERN = re.compile(r"\b(seo_score|quality_score|quality grade|\d+\s*%)\b", re.I)
ZONE_ID_PATTERN = re.compile(r"^WB-ZONE-\d{4}$")
COMPONENT_ID_PATTERN = re.compile(r"^WB-COMPONENT-\d{4}$")
UI_STATE_ID_PATTERN = re.compile(r"^WB-UI-STATE-\d{4}$")
MODULE_ID_PATTERN = re.compile(r"^WB-SPEC-MODULE-\d{4}$")
FLOW_ID_PATTERN = re.compile(r"^WB-FLOW-\d{4}$")
GUARDRAIL_ID_PATTERN = re.compile(r"^WB-GUARDRAIL-\d{4}$")
ENVELOPE_ID_PATTERN = re.compile(r"^WB-ENVELOPE-\d{4}$")
STATE_ID_PATTERN = re.compile(r"^WB-STATE-\d{4}$")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_spec_refs() -> tuple[set[str], set[str], set[str], set[str]]:
    modules = {
        m["module_id"]
        for m in load_json(ROOT / "data" / "evidence-posture-workbench-module-registry.json").get("modules", [])
    }
    flows = {
        f["flow_step_id"]
        for f in load_json(ROOT / "data" / "evidence-posture-workbench-flow-contract.json").get("flow_steps", [])
    }
    guardrails = {
        g["guardrail_id"]
        for g in load_json(ROOT / "data" / "evidence-posture-workbench-boundary-guardrail-map.json").get(
            "guardrails", []
        )
    }
    envelopes = {
        e["envelope_id"]
        for e in load_json(ROOT / "data" / "evidence-posture-workbench-output-envelope.json").get(
            "output_envelopes", []
        )
    }
    return modules, flows, guardrails, envelopes


def load_workbench_states() -> set[str]:
    return {
        s["state_id"]
        for s in load_json(ROOT / "data" / "evidence-posture-workbench-state-model.json").get("states", [])
    }


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-workbench-interface-blueprint-policy.json"
    policy = load_json(path)
    if set(policy) != POLICY_TOP:
        error("interface blueprint policy: unexpected top-level keys")
        ok = False
    if policy.get("status") != "governed_evidence_posture_workbench_interface_blueprint_policy":
        error("interface blueprint policy: invalid status")
        ok = False
    if policy.get("maturity") != "blueprint_governance_only_no_interface_no_prototype_no_engine_no_classifier_no_tool":
        error("interface blueprint policy: invalid maturity")
        ok = False
    prohibited = " ".join(str(a) for a in policy.get("prohibited_actions", [])).lower()
    for action in PROHIBITED_ACTIONS:
        if action.replace("_", " ") not in prohibited and action not in prohibited:
            error(f"interface blueprint policy: missing prohibited action {action}")
            ok = False
    identity = policy.get("conceptual_interface_identity_policy", {})
    if identity.get("status") != "hoax_specific_interface_identity_required":
        error("conceptual_interface_identity_policy missing or invalid status")
        ok = False
    traits = identity.get("required_identity_traits", [])
    for trait in REQUIRED_IDENTITY_TRAITS:
        if trait not in traits:
            error(f"conceptual identity: missing required trait {trait}")
            ok = False
    allowed_m = identity.get("allowed_metaphors", [])
    for m in REQUIRED_ALLOWED_METAPHORS:
        if m not in allowed_m:
            error(f"conceptual identity: missing allowed metaphor {m}")
            ok = False
    forbidden_m = " ".join(identity.get("forbidden_metaphors", [])).lower()
    for m in FORBIDDEN_METAPHORS:
        if m.replace("_", " ") not in forbidden_m and m not in forbidden_m:
            error(f"conceptual identity: missing forbidden metaphor {m}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(path.read_text(encoding="utf-8")):
        error("interface blueprint policy: numeric score or grade found")
        ok = False
    return ok


def validate_specification_dependency() -> bool:
    ok = True
    spec = load_json(ROOT / "data" / "evidence-posture-workbench-specification-v1.json")
    if spec.get("status") != "evidence_posture_workbench_specification_created":
        error("workbench specification must exist with created status")
        ok = False
    blueprint = load_json(ROOT / "data" / "evidence-posture-workbench-interface-blueprint-v1.json")
    if "specification-v1" not in blueprint.get("specification_ref", ""):
        error("interface blueprint must reference specification as prerequisite")
        ok = False
    text = blueprint.get("non_authorization_statement", "").lower()
    if DETECTOR_UI_PATTERN.search(json.dumps(blueprint)):
        error("blueprint implies readiness or detector UI")
        ok = False
    if "prototype ready" in text or "interface ready" in text:
        error("blueprint claims interface or prototype readiness")
        ok = False
    return ok


def validate_zone_registry(modules: set[str], flows: set[str], guardrails: set[str], envelopes: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-zone-registry.json")
    if set(data) != ZONE_TOP:
        error("zone registry: unexpected top-level keys")
        ok = False
    zones = data.get("zones", [])
    if len(zones) != 8:
        error(f"zone registry: expected 8 zones, found {len(zones)}")
        ok = False
    ids: set[str] = set()
    for zone in zones:
        zid = zone.get("zone_id", "")
        if not ZONE_ID_PATTERN.match(zid):
            error(f"zone registry: invalid zone_id {zid}")
            ok = False
        if zid in ids:
            error(f"zone registry: duplicate zone_id {zid}")
            ok = False
        ids.add(zid)
        for field, expected in [
            ("interface_status", "no_interface_created"),
            ("prototype_status", "no_prototype_created"),
            ("engine_status", "no_engine_created"),
            ("route_status", "not_route_created"),
        ]:
            if zone.get(field) != expected:
                error(f"{zid}: {field} must be {expected}")
                ok = False
        for req in ["conceptual_role", "hoax_identity_function", "generic_ui_pattern_to_avoid"]:
            if not zone.get(req):
                error(f"{zid}: missing {req}")
                ok = False
        for mid in zone.get("related_spec_modules", []):
            if mid and mid not in modules:
                error(f"{zid}: invalid related_spec_module {mid}")
                ok = False
        for fid in zone.get("related_flow_steps", []):
            if fid and fid not in flows:
                error(f"{zid}: invalid related_flow_step {fid}")
                ok = False
        for gid in zone.get("related_guardrails", []):
            if gid and gid not in guardrails:
                error(f"{zid}: invalid related_guardrail {gid}")
                ok = False
        for eid in zone.get("related_output_envelopes", []):
            if eid and eid not in envelopes:
                error(f"{zid}: invalid related_output_envelope {eid}")
                ok = False
        blob = json.dumps(zone).lower()
        if DETECTOR_UI_PATTERN.search(blob):
            error(f"{zid}: implies generic detector UI")
            ok = False
    return ok


def validate_component_registry(zone_ids: set[str], modules: set[str], guardrails: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-component-registry.json")
    if set(data) != COMPONENT_TOP:
        error("component registry: unexpected top-level keys")
        ok = False
    components = data.get("components", [])
    if len(components) != 10:
        error(f"component registry: expected 10 components, found {len(components)}")
        ok = False
    ids: set[str] = set()
    for comp in components:
        cid = comp.get("component_id", "")
        if not COMPONENT_ID_PATTERN.match(cid):
            error(f"component registry: invalid component_id {cid}")
            ok = False
        if cid in ids:
            error(f"component registry: duplicate component_id {cid}")
            ok = False
        ids.add(cid)
        for field, expected in [
            ("interface_status", "no_interface_created"),
            ("prototype_status", "no_prototype_created"),
            ("engine_status", "no_engine_created"),
            ("route_status", "not_route_created"),
        ]:
            if comp.get(field) != expected:
                error(f"{cid}: {field} must be {expected}")
                ok = False
        for req in [
            "conceptual_identity_role", "hoax_specific_behavior", "generic_detector_pattern_blocked",
        ]:
            if not comp.get(req):
                error(f"{cid}: missing {req}")
                ok = False
        for zid in comp.get("related_zone_ids", []):
            if zid and zid not in zone_ids:
                error(f"{cid}: invalid related_zone_id {zid}")
                ok = False
        for mid in comp.get("related_spec_modules", []):
            if mid and mid not in modules:
                error(f"{cid}: invalid related_spec_module {mid}")
                ok = False
        for gid in comp.get("related_guardrails", []):
            if gid and gid not in guardrails:
                error(f"{cid}: invalid related_guardrail {gid}")
                ok = False
        blob = json.dumps(comp).lower()
        if DETECTOR_UI_PATTERN.search(blob):
            error(f"{cid}: implies generic detector UI")
            ok = False
    return ok


def validate_state_contracts(states: set[str], zone_ids: set[str]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-state-contracts.json")
    if set(data) != STATE_TOP:
        error("state contracts: unexpected top-level keys")
        ok = False
    ui_states = data.get("interface_states", [])
    if len(ui_states) != 10:
        error(f"state contracts: expected 10 states, found {len(ui_states)}")
        ok = False
    forbidden = " ".join(data.get("forbidden_state_behaviors", [])).lower()
    for beh in FORBIDDEN_STATE_BEHAVIORS:
        if beh.replace("_", " ") not in forbidden and beh not in forbidden:
            error(f"state contracts: missing forbidden behavior {beh}")
            ok = False
    ids: set[str] = set()
    for st in ui_states:
        sid = st.get("interface_state_id", "")
        if not UI_STATE_ID_PATTERN.match(sid):
            error(f"state contracts: invalid interface_state_id {sid}")
            ok = False
        if sid in ids:
            error(f"state contracts: duplicate interface_state_id {sid}")
            ok = False
        ids.add(sid)
        for field, expected in [
            ("interface_status", "no_interface_created"),
            ("prototype_status", "no_prototype_created"),
            ("engine_status", "no_engine_created"),
        ]:
            if st.get(field) != expected:
                error(f"{sid}: {field} must be {expected}")
                ok = False
        for wb in st.get("related_workbench_state_ids", []):
            if wb and wb not in states:
                error(f"{sid}: invalid related_workbench_state_id {wb}")
                ok = False
        for zid in st.get("related_zone_ids", []):
            if zid and zid not in zone_ids:
                error(f"{sid}: invalid related_zone_id {zid}")
                ok = False
    return ok


def validate_copy_boundaries() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-copy-boundaries.json")
    if set(data) != COPY_TOP:
        error("copy boundaries: unexpected top-level keys")
        ok = False
    allowed = " ".join(data.get("allowed_copy_patterns", [])).lower()
    for pat in ALLOWED_COPY:
        if pat.lower() not in allowed:
            error(f"copy boundaries: missing allowed pattern {pat}")
            ok = False
    prohibited = " ".join(data.get("prohibited_copy_patterns", [])).lower()
    for pat in PROHIBITED_COPY:
        if pat.lower() not in prohibited:
            error(f"copy boundaries: missing prohibited pattern {pat}")
            ok = False
    phrases = data.get("required_boundary_phrases", [])
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in phrases:
            error(f"copy boundaries: missing required phrase")
            ok = False
    return ok


def validate_a11y_perf() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-accessibility-performance-rules.json")
    if set(data) != A11Y_TOP:
        error("accessibility/performance rules: unexpected top-level keys")
        ok = False
    a11y = " ".join(data.get("accessibility_rules", [])).lower()
    for rule in A11Y_REQUIRED:
        if rule.lower() not in a11y:
            error(f"accessibility rules: missing {rule}")
            ok = False
    perf = " ".join(data.get("performance_rules", [])).lower()
    for rule in PERF_REQUIRED:
        if rule.lower() not in perf:
            error(f"performance rules: missing {rule}")
            ok = False
    return ok


def validate_master_blueprint() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-posture-workbench-interface-blueprint-v1.json")
    if set(data) != BLUEPRINT_TOP:
        error("master blueprint: unexpected top-level keys")
        ok = False
    if data.get("status") != "evidence_posture_workbench_interface_blueprint_governance_created":
        error("master blueprint: invalid status")
        ok = False
    if data.get("maturity") != "blueprint_governance_only_no_interface_no_prototype_no_engine_no_classifier_no_tool":
        error("master blueprint: invalid maturity")
        ok = False
    next_phase = data.get("allowed_next_phase", "")
    if "Sprint 32" not in next_phase or "Interface Blueprint Validation" not in next_phase:
        error("master blueprint: allowed_next_phase must be Sprint 32 Interface Blueprint Validation")
        ok = False
    surface = data.get("current_public_surface", [])
    required = [
        "homepage root", "/reference/evidence-posture/",
        "/reference/artifact-subject-separation/", "/language/",
    ]
    if surface != required:
        error(f"master blueprint: current_public_surface must be {required}")
        ok = False
    caps = {c.lower() for c in data.get("prohibited_capabilities", [])}
    for cap in PROHIBITED_CAPABILITIES:
        if cap.lower() not in caps:
            error(f"master blueprint: missing prohibited capability {cap}")
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
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
        PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
    ):
        error(
            f"publisher status must be {PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION} "
            f"or {PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE}"
        )
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    gate = next(
        (g for g in gates if g.get("name") == "Evidence Posture Workbench Interface Blueprint Governance Gate"),
        None,
    )
    if not gate:
        error("Evidence Posture Workbench Interface Blueprint Governance Gate missing")
        ok = False
    else:
        if gate.get("bypassable") is True:
            error("interface blueprint governance gate must not be bypassable")
            ok = False
        if gate.get("required_before_workbench_interface_blueprint_validation") is not True:
            error("gate must be required before interface blueprint validation")
            ok = False
        if gate.get("required_before_workbench_prototype") is not True:
            error("gate must be required before workbench prototype")
            ok = False
        if gate.get("required_before_engine_governance") is not True:
            error("gate must be required before engine governance")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "interface_blueprint" not in checks:
        error("reference-expansion-gate: interface blueprint governance required")
        ok = False
    rules = " ".join(expansion.get("release_eligibility_rules", [])).lower()
    if "no_public_engine_eligibility_by_blueprint_governance_alone" not in rules:
        error("reference-expansion-gate: must block public engine eligibility by blueprint governance alone")
        ok = False
    blocked = expansion.get("blocked_conditions", [])
    workbench_blocked = [
        "publisher_blocked_until_workbench_interface_blueprint_validation",
        "publisher_blocked_until_non_public_static_workbench_prototype_governance",
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
    if "validate_evidence_posture_workbench_interface_blueprint.py" not in content:
        error("validate_all.py must include interface blueprint validator")
        ok = False
    doc = (ROOT / "EVIDENCE_POSTURE_WORKBENCH_INTERFACE_BLUEPRINT_GOVERNANCE.md").read_text(encoding="utf-8")
    if "An interface blueprint may define the shape of interaction. It must not become an interface." not in doc:
        error("interface blueprint doc: missing governing principle")
        ok = False
    if "evidence should be structured before it is believed" not in doc:
        error("interface blueprint doc: missing Hoax thesis sentence")
        ok = False
    if "evidence chamber" not in doc.lower():
        error("interface blueprint doc: missing evidence chamber metaphor")
        ok = False
    for path in ROOT.glob("data/evidence-posture-workbench-interface-*.json"):
        text = path.read_text(encoding="utf-8").lower()
        if "interface_implemented" in text or "ready for public use" in text:
            error(f"{path.name}: claims interface implemented or ready")
            ok = False
    return ok


def main() -> int:
    parse_paths = [
        "data/evidence-posture-workbench-interface-blueprint-policy.json",
        "data/evidence-posture-workbench-interface-zone-registry.json",
        "data/evidence-posture-workbench-interface-component-registry.json",
        "data/evidence-posture-workbench-interface-state-contracts.json",
        "data/evidence-posture-workbench-interface-copy-boundaries.json",
        "data/evidence-posture-workbench-interface-accessibility-performance-rules.json",
        "data/evidence-posture-workbench-interface-blueprint-v1.json",
        "data/evidence-posture-workbench-specification-v1.json",
        "data/evidence-posture-workbench-module-registry.json",
        "data/evidence-posture-workbench-flow-contract.json",
        "data/evidence-posture-workbench-output-envelope.json",
        "data/evidence-posture-workbench-boundary-guardrail-map.json",
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

    modules, flows, guardrails, envelopes = load_spec_refs()
    states = load_workbench_states()
    zone_ids = {
        z["zone_id"]
        for z in load_json(ROOT / "data" / "evidence-posture-workbench-interface-zone-registry.json").get("zones", [])
    }

    checks = [
        validate_policy,
        validate_specification_dependency,
        lambda: validate_zone_registry(modules, flows, guardrails, envelopes),
        lambda: validate_component_registry(zone_ids, modules, guardrails),
        lambda: validate_state_contracts(states, zone_ids),
        validate_copy_boundaries,
        validate_a11y_perf,
        validate_master_blueprint,
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
