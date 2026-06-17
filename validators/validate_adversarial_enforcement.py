#!/usr/bin/env python3
"""Adversarial enforcement validator for Hoax.ai governance boundaries."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent

ROUTE_REQUIRED = {
    "route_id",
    "path",
    "title",
    "route_type",
    "status",
    "index_policy",
    "canonical_url",
    "sitemap_included",
    "internal_linking_required",
    "public_surface",
    "deployment_status",
    "notes",
}

OUTPUT_REQUIRED = {
    "output_id",
    "schema_version",
    "protocol_version",
    "taxonomy_version",
    "standard_version",
    "artifact_scope",
    "artifact_type",
    "posture_state",
    "posture_reason_summary",
    "dimension_findings",
    "limiting_factors",
    "subject_boundary_statement",
    "prohibited_interpretations",
    "confidence_boundary",
    "output_status",
    "generated_by",
    "last_reviewed",
}

OUTPUT_PROHIBITED_FIELDS = {
    "truth_score",
    "lie_score",
    "guilt_score",
    "fraud_score",
    "authenticity_score",
    "deception_score",
    "subject_risk_score",
    "person_score",
    "institution_score",
    "fake_real_result",
    "deepfake_detected",
    "verdict",
    "accusation",
}

OUTPUT_PROHIBITED_LANGUAGE = [
    "this is fake",
    "this is real",
    "deepfake detected",
    "guaranteed detection",
    "certifies truth",
    "proves guilt",
]

SUBJECT_ACCUSATION_MARKERS = [
    "deceptive person",
    "guilty institution",
    "person is lying",
    "institution is guilty",
    "fraud by association",
    "involved by evidence risk",
]

NEGATION_MARKERS = [
    "no ",
    "not ",
    "without ",
    "never ",
    "avoid ",
    "does not ",
    "do not ",
    "not a ",
    "not an ",
    "not the ",
    "not issue",
    "not claim",
    "planned",
    "under development",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def path_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if not path.endswith("/") and "." not in Path(path).name:
        path = path + "/"
    return path if path != "" else "/"


def contains_unnegated_term(text: str, phrase: str) -> bool:
    lower = text.lower()
    idx = 0
    while True:
        pos = lower.find(phrase, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 40) : pos]
        if any(marker in prefix for marker in NEGATION_MARKERS):
            idx = pos + len(phrase)
            continue
        return True
    return False


class EnforcementContext:
    def __init__(self) -> None:
        self.taxonomy = load_json(ROOT / "data" / "evidence-posture-taxonomy.json")
        self.standard = load_json(ROOT / "data" / "evidence-posture-standard.json")
        self.protocol = load_json(ROOT / "data" / "evidence-posture-protocol.json")
        self.output_schema = load_json(ROOT / "data" / "output-boundary-schema.json")
        self.engine_model = load_json(ROOT / "data" / "internal-engine-model.json")
        self.route_registry = load_json(ROOT / "data" / "route-registry.json")
        self.source_registry = load_json(ROOT / "data" / "source-registry.json")
        self.evidence_ledger = load_json(ROOT / "data" / "evidence-ledger.json")
        self.policy = load_json(ROOT / "data" / "forbidden-language-policy.json")
        self.cases_data = load_json(ROOT / "data" / "adversarial-validation-cases.json")

        self.taxonomy_state_labels = {s["label"] for s in self.taxonomy.get("states", [])}
        self.taxonomy_state_ids = {s["state_id"] for s in self.taxonomy.get("states", [])}
        self.standard_rule_ids = {r["rule_id"] for r in self.standard.get("sufficiency_rules", [])}
        self.schema_field_names = {
            f["field_name"] for f in self.output_schema.get("required_output_fields", [])
        }
        self.public_terms = self._collect_public_forbidden_terms()

    def _collect_public_forbidden_terms(self) -> list[str]:
        terms: list[str] = []
        rules = self.policy.get("rules", {})
        for category in self.policy.get("prohibited_contexts", {}).get(
            "public_facing_unless_negated", []
        ):
            terms.extend(rules.get(category, []))
        return terms


def check_sitemap_alignment(payload: dict) -> tuple[bool, str]:
    sitemap_paths = set(payload.get("sitemap_paths", []))
    registry_paths = set(payload.get("registry_paths", []))
    for sp in sitemap_paths:
        if sp not in registry_paths:
            return False, "sitemap URL path not in route-registry"
    return True, ""


def check_route_record(route: dict) -> tuple[bool, str]:
    missing = ROUTE_REQUIRED - set(route.keys())
    if missing:
        if "canonical_url" in missing:
            return False, "route missing required canonical_url"
        return False, f"route missing required fields: {sorted(missing)}"
    if not route.get("canonical_url"):
        return False, "route missing required canonical_url"
    return True, ""


def check_posture_state(ctx: EnforcementContext, state: str) -> tuple[bool, str]:
    if state not in ctx.taxonomy_state_labels:
        return False, "posture state not in taxonomy"
    return True, ""


def check_standard_rule(ctx: EnforcementContext, rule: dict) -> tuple[bool, str]:
    state_id = rule.get("taxonomy_state_id")
    if state_id not in ctx.taxonomy_state_ids:
        return False, "standard rule taxonomy_state_id not in taxonomy"
    label = rule.get("state_label")
    if label and label not in ctx.taxonomy_state_labels:
        return False, "standard rule state_label not in taxonomy"
    return True, ""


def check_protocol_rule(ctx: EnforcementContext, rule: dict) -> tuple[bool, str]:
    std_rule = rule.get("standard_rule_id")
    if std_rule not in ctx.standard_rule_ids:
        return False, "protocol rule standard_rule_id not in standard"
    state_id = rule.get("taxonomy_state_id")
    if state_id not in ctx.taxonomy_state_ids:
        return False, "protocol rule taxonomy_state_id not in taxonomy"
    return True, ""


def check_output_payload(ctx: EnforcementContext, output: dict) -> tuple[bool, str]:
    for field in OUTPUT_PROHIBITED_FIELDS:
        if field in output:
            return False, "output contains prohibited scoring field"

    scan_text = json.dumps(output).lower()
    for phrase in OUTPUT_PROHIBITED_LANGUAGE:
        if contains_unnegated_term(scan_text, phrase):
            if phrase in ("this is fake", "this is real"):
                return False, "output contains fake/real verdict language"
            return False, "output contains prohibited detection claim"

    for marker in SUBJECT_ACCUSATION_MARKERS:
        if marker in scan_text and "not " not in scan_text.split(marker)[0][-20:]:
            boundary = output.get("subject_boundary_statement", "").lower()
            if marker in boundary:
                return False, "output implies subject accusation"

    for key in output:
        if key not in ctx.schema_field_names and key not in OUTPUT_PROHIBITED_FIELDS:
            if key in {"truth_score", "lie_score"}:
                return False, "output contains prohibited scoring field"
            if key not in {"recommended_next_checks", "source_record_refs", "claim_record_refs"}:
                if key not in OUTPUT_REQUIRED and key not in ctx.schema_field_names:
                    pass

    if "subject_boundary_statement" not in output or not output.get("subject_boundary_statement"):
        if any(k in output for k in OUTPUT_REQUIRED):
            return False, "output missing subject_boundary_statement"

    if output.get("posture_state"):
        ok_state, reason = check_posture_state(ctx, output["posture_state"])
        if not ok_state:
            return False, reason

    missing_required = OUTPUT_REQUIRED - set(output.keys())
    if missing_required and "subject_boundary_statement" in missing_required:
        return False, "output missing subject_boundary_statement"

    if output.get("truth_score") is not None:
        return False, "output contains prohibited scoring field"

    if all(k in output for k in OUTPUT_REQUIRED):
        ok, reason = check_posture_state(ctx, output["posture_state"])
        if not ok:
            return False, reason
        return True, ""

    if len(output) <= 3:
        if "truth_score" in output:
            return False, "output contains prohibited scoring field"
        if any(contains_unnegated_term(scan_text, p) for p in ("this is fake", "this is real")):
            return False, "output contains fake/real verdict language"
        if "deepfake detected" in scan_text:
            return False, "output contains prohibited detection claim"
        if any(m in scan_text for m in SUBJECT_ACCUSATION_MARKERS):
            return False, "output implies subject accusation"

    return False, "output missing subject_boundary_statement"


def check_public_language(ctx: EnforcementContext, text: str) -> tuple[bool, str]:
    lower = text.lower()
    for term in ctx.public_terms:
        if contains_unnegated_term(lower, term):
            if term in ctx.policy.get("rules", {}).get("tool_implication_terms", []):
                return False, "public language implies active upload tool"
            if term in ctx.policy.get("rules", {}).get("unsupported_superiority_terms", []):
                return False, "unsupported superiority claim"
            if term in ctx.policy.get("rules", {}).get("future_capability_as_live_terms", []):
                return False, "future capability described as live"
            return False, f"forbidden public language: {term}"
    return True, ""


def check_future_capability_claim(claim: dict) -> tuple[bool, str]:
    posture = claim.get("evidence_posture", "")
    text = claim.get("claim_text", "").lower()
    live_terms = [
        "active classifier",
        "live tool",
        "operational service",
        "now available",
        "currently running",
    ]
    if claim.get("claim_type") == "future_capability_claim":
        if posture == "repository_supported":
            return False, "future capability described as live"
        if any(term in text for term in live_terms):
            return False, "future capability described as live"
    if posture == "planned_not_claimed":
        if any(term in text for term in live_terms):
            return False, "future capability described as live"
        return True, ""
    if claim.get("claim_type") == "future_capability_claim" and posture not in {
        "planned_not_claimed",
        "conceptual",
        "retired",
    }:
        return False, "future capability described as live"
    return True, ""


def check_claim_payload(claim: dict) -> tuple[bool, str]:
    ctype = claim.get("claim_type")
    posture = claim.get("evidence_posture")
    support = claim.get("support_location", "")

    if ctype == "external_factual_claim":
        if not support or not str(support).strip():
            return False, "external factual claim without source support"
        if posture == "source_supported" and not support:
            return False, "external factual claim without source support"

    if posture == "repository_supported":
        if not support or not str(support).strip():
            return False, "repository_supported claim missing support_location"

    ok, reason = check_future_capability_claim(claim)
    if not ok:
        return False, reason

    return True, ""


def check_source_location(source: dict) -> tuple[bool, str]:
    location = source.get("location", "")
    stype = source.get("source_type", "")
    if stype.startswith("internal") and location:
        if not (ROOT / location).exists():
            return False, "internal source file missing"
    return True, ""


def check_repository_route(ctx: EnforcementContext, route_id: str) -> tuple[bool, str]:
    routes = ctx.route_registry.get("routes", [])
    route = next((r for r in routes if r.get("route_id") == route_id), None)
    if route is None:
        return False, "route not found in registry"
    return check_route_record(route)


def execute_case(ctx: EnforcementContext, case: dict) -> tuple[bool, str]:
    domain = case.get("enforcement_domain", "")
    payload = case.get("test_payload", {})

    if domain == "sitemap":
        return check_sitemap_alignment(payload)
    if domain == "routes":
        if case.get("fixture_type") == "repository_fixture":
            return check_repository_route(ctx, payload.get("route_id", ""))
        return check_route_record(payload.get("route", {}))
    if domain == "taxonomy":
        return check_posture_state(ctx, payload.get("posture_state", ""))
    if domain == "standard":
        return check_standard_rule(ctx, payload.get("standard_rule", {}))
    if domain == "protocol":
        return check_protocol_rule(ctx, payload.get("protocol_rule", {}))
    if domain == "output_schema":
        return check_output_payload(ctx, payload.get("output", {}))
    if domain == "public_language":
        return check_public_language(ctx, payload.get("text", ""))
    if domain == "future_capability_claims":
        return check_future_capability_claim(payload.get("claim", {}))
    if domain == "claims":
        return check_claim_payload(payload.get("claim", {}))
    if domain == "source_registry":
        return check_source_location(payload.get("source", {}))
    if domain == "adversarial_meta":
        return validate_prohibited_terms_contained(ctx)
    return False, f"unclassified enforcement domain: {domain}"


def validate_prohibited_terms_contained(ctx: EnforcementContext) -> tuple[bool, str]:
    invalid_cases = [
        c for c in ctx.cases_data.get("cases", []) if c.get("intentionally_invalid")
    ]
    leak_terms: list[str] = []
    for path in [ROOT / "index.html", ROOT / "README.md"]:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").lower()
        for case in invalid_cases:
            payload_text = json.dumps(case.get("test_payload", {})).lower()
            for term in ctx.public_terms:
                if term in payload_text and contains_unnegated_term(content, term):
                    leak_terms.append(term)
    if leak_terms:
        return False, f"prohibited terms leaked to public surface: {sorted(set(leak_terms))}"
    return True, ""


def validate_policy_structure(ctx: EnforcementContext) -> bool:
    ok = True
    policy = ctx.policy
    for field in [
        "policy_id",
        "name",
        "version",
        "status",
        "governing_principle",
        "contexts",
        "rules",
        "allowed_contexts",
        "prohibited_contexts",
        "last_reviewed",
    ]:
        if field not in policy:
            error(f"forbidden-language-policy: missing field '{field}'")
            ok = False

    required_categories = [
        "absolute_forbidden_public_claims",
        "tool_implication_terms",
        "verdict_terms",
        "fake_real_binary_terms",
        "scoring_terms",
        "subject_accusation_terms",
        "unsupported_superiority_terms",
        "future_capability_as_live_terms",
    ]
    rules = policy.get("rules", {})
    for cat in required_categories:
        if cat not in rules or not rules[cat]:
            error(f"forbidden-language-policy: missing rule category '{cat}'")
            ok = False

    allowed = policy.get("allowed_contexts", {})
    for key in [
        "allowed_in_negation_only",
        "allowed_in_expected_fail_tests",
        "allowed_in_internal_governance_only",
    ]:
        if key not in allowed:
            error(f"forbidden-language-policy: missing '{key}'")
            ok = False
    return ok


def validate_cases_structure(ctx: EnforcementContext) -> bool:
    ok = True
    data = ctx.cases_data
    for field in [
        "adversarial_case_set_id",
        "name",
        "version",
        "status",
        "maturity",
        "cases",
        "last_reviewed",
    ]:
        if field not in data:
            error(f"adversarial-validation-cases: missing field '{field}'")
            ok = False

    cases = data.get("cases", [])
    if len(cases) < 18:
        error(f"adversarial-validation-cases: expected at least 18 cases, found {len(cases)}")
        ok = False

    required_case_fields = {
        "case_id",
        "case_name",
        "enforcement_domain",
        "expected_result",
        "fixture_type",
        "intentionally_invalid",
        "test_payload",
        "expected_failure_reason",
        "notes",
    }
    seen_ids: set[str] = set()
    for case in cases:
        cid = case.get("case_id", "?")
        missing = required_case_fields - set(case.keys())
        if missing:
            error(f"adversarial case '{cid}': missing fields {sorted(missing)}")
            ok = False
        if cid in seen_ids:
            error(f"adversarial case: duplicate case_id '{cid}'")
            ok = False
        seen_ids.add(cid)
        if case.get("expected_result") not in {"pass", "fail"}:
            error(f"adversarial case '{cid}': invalid expected_result")
            ok = False
    return ok


def run_adversarial_cases(ctx: EnforcementContext) -> bool:
    ok = True
    for case in ctx.cases_data.get("cases", []):
        cid = case["case_id"]
        expected = case["expected_result"]
        passed, reason = execute_case(ctx, case)

        if expected == "fail":
            if passed:
                error(
                    f"adversarial case '{cid}': expected fail but passed "
                    f"(expected reason: {case.get('expected_failure_reason', '')})"
                )
                ok = False
            elif case.get("expected_failure_reason") and reason:
                expected_reason = case["expected_failure_reason"].lower()
                actual_reason = reason.lower()
                reason_tokens = [t for t in expected_reason.replace("_", " ").split() if len(t) > 3]
                if (
                    expected_reason not in actual_reason
                    and actual_reason not in expected_reason
                    and not any(token in actual_reason for token in reason_tokens[:3])
                ):
                    error(
                        f"adversarial case '{cid}': failure reason mismatch "
                        f"(got '{reason}', expected '{case['expected_failure_reason']}')"
                    )
                    ok = False
        elif expected == "pass":
            if not passed:
                error(f"adversarial case '{cid}': expected pass but failed ({reason})")
                ok = False
    return ok


def validate_repository_sitemap(ctx: EnforcementContext) -> bool:
    ok = True
    routes = ctx.route_registry.get("routes", [])
    paths = {r["path"] for r in routes}
    registry_sitemap_paths = {r["path"] for r in routes if r.get("sitemap_included")}

    sitemap_file = ROOT / "sitemap.xml"
    if sitemap_file.exists():
        tree = ElementTree.parse(sitemap_file)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_paths = set()
        for loc in tree.findall(".//sm:loc", ns):
            if loc.text:
                sitemap_paths.add(path_from_url(loc.text.strip()))
        for sp in sitemap_paths:
            if sp not in paths:
                error(f"repository sitemap: path '{sp}' not in route-registry")
                ok = False
        for rp in registry_sitemap_paths:
            if rp not in sitemap_paths:
                error(f"repository route-registry: sitemap path '{rp}' missing from sitemap.xml")
                ok = False
    return ok


def validate_repository_sources(ctx: EnforcementContext) -> bool:
    ok = True
    for source in ctx.source_registry.get("sources", []):
        sid = source.get("source_id", "?")
        location = source.get("location", "")
        stype = source.get("source_type", "")
        if stype.startswith("internal") and location:
            if not (ROOT / location).exists():
                error(f"repository source-registry '{sid}': internal file missing '{location}'")
                ok = False
    return ok


def validate_repository_ledger(ctx: EnforcementContext) -> bool:
    ok = True
    for claim in ctx.evidence_ledger.get("claims", []):
        cid = claim.get("claim_id", "?")
        posture = claim.get("evidence_posture")
        support = claim.get("support_location", "")
        if posture == "repository_supported" and not str(support).strip():
            error(f"repository evidence-ledger '{cid}': repository_supported missing support_location")
            ok = False
        if claim.get("claim_type") == "external_factual_claim":
            if not str(support).strip():
                error(f"repository evidence-ledger '{cid}': external factual claim without source")
                ok = False
    return ok


def validate_public_files(ctx: EnforcementContext) -> bool:
    ok = True
    for rel in ["index.html", "README.md"]:
        path = ROOT / rel
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        passed, reason = check_public_language(ctx, content)
        if not passed:
            error(f"public file '{rel}': {reason}")
            ok = False
    return ok


def validate_engine_model_boundaries(ctx: EnforcementContext) -> bool:
    ok = True
    model = ctx.engine_model
    prohibited_inputs = {
        "person_score",
        "institution_score",
        "truth_score",
        "fake_real_result",
        "upload_file",
        "accusation_target",
        "guilt_question",
        "deception_question",
    }
    for field in model.get("allowed_input_fields", []):
        fname = field.get("field_name", "")
        if fname in prohibited_inputs:
            error(f"engine model: prohibited input field '{fname}'")
            ok = False

    if "public_allowed_after_gate" in model.get("output_status_limits", []):
        error("engine model: public_allowed_after_gate not allowed")
        ok = False

    scan = json.dumps(model.get("prohibited_engine_outputs", [])).lower()
    for term in ["public classifier", "upload workflow", "truth_score"]:
        if term not in scan:
            error(f"engine model: prohibited_engine_outputs missing '{term}'")
            ok = False
    return ok


def validate_output_schema_boundaries(ctx: EnforcementContext) -> bool:
    ok = True
    subject_field = next(
        (
            f
            for f in ctx.output_schema.get("required_output_fields", [])
            if f.get("field_name") == "subject_boundary_statement"
        ),
        None,
    )
    if subject_field is None or not subject_field.get("required"):
        error("output schema: subject_boundary_statement must be required")
        ok = False
    return ok


def validate_enforcement_sources() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in [
        "ADVERSARIAL_ENFORCEMENT_HARNESS.md",
        "data/forbidden-language-policy.json",
        "data/adversarial-validation-cases.json",
        "validators/validate_adversarial_enforcement.py",
        "validators/generate_build_manifest.py",
    ]:
        if required not in locations:
            error(f"source-registry: missing adversarial enforcement source '{required}'")
            ok = False
    return ok


def main() -> int:
    ctx = EnforcementContext()
    checks = [
        ("Forbidden language policy structure", lambda: validate_policy_structure(ctx)),
        ("Adversarial cases structure", lambda: validate_cases_structure(ctx)),
        ("Adversarial case execution", lambda: run_adversarial_cases(ctx)),
        ("Repository sitemap alignment", lambda: validate_repository_sitemap(ctx)),
        ("Repository source files", lambda: validate_repository_sources(ctx)),
        ("Repository evidence ledger", lambda: validate_repository_ledger(ctx)),
        ("Public file forbidden language", lambda: validate_public_files(ctx)),
        ("Engine model boundaries", lambda: validate_engine_model_boundaries(ctx)),
        ("Output schema boundaries", lambda: validate_output_schema_boundaries(ctx)),
        ("Enforcement source registry", validate_enforcement_sources),
    ]

    all_ok = True
    for name, fn in checks:
        if not fn():
            all_ok = False

    if all_ok:
        print("PASS")
        return 0

    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
