#!/usr/bin/env python3
"""Validate Hoax.ai Category Intelligence Factory foundation registries and public surface."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent

EVIDENCE_POSTURES = {
    "conceptual",
    "repository_supported",
    "source_supported",
    "planned_not_claimed",
    "needs_review",
    "retired",
}

CLAIM_TYPES = {
    "conceptual_thesis",
    "operational_claim",
    "governance_claim",
    "external_factual_claim",
    "future_capability_claim",
}

LEDGER_REQUIRED = {
    "claim_id",
    "claim_text",
    "claim_type",
    "evidence_posture",
    "support_location",
    "source_type",
    "status",
    "last_reviewed",
    "notes",
}

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

TERM_REQUIRED = {
    "term_id",
    "term",
    "canonical_status",
    "definition",
    "layer",
    "public_use_allowed",
    "related_terms",
    "prohibited_misreadings",
    "notes",
}

CLASS_REQUIRED = {
    "class_id",
    "class_name",
    "category",
    "definition",
    "allowed_use",
    "prohibited_use",
    "related_terms",
    "status",
    "notes",
}

SOURCE_REQUIRED = {
    "source_id",
    "source_title",
    "source_type",
    "location",
    "supports",
    "reliability_posture",
    "status",
    "notes",
}

CATEGORY_PROHIBITED = [
    "truth machine",
    "fake/real detector",
    "detects all",
    "guaranteed detection",
    "certifies truth",
    "proves guilt",
    "accuses",
    "fraud by association",
]

INDEX_FORBIDDEN = [
    "upload",
    "submit",
    "<form",
    "truth score",
    "first in the world",
    "scan your",
    "scan now",
    "deepfake detector",
    "try our detector",
    "active classifier",
    "live tool",
]

INDEX_CONDITIONAL = ["detect", "check", "verdict", "fake", "real", "scan", "analyze"]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without)\s+[\w\s]{0,30}",
    re.IGNORECASE,
)

ID_PATTERNS = {
    "CLAIM": re.compile(r"^CLAIM-\d{4}$"),
    "ROUTE": re.compile(r"^ROUTE-\d{4}$"),
    "TERM": re.compile(r"^TERM-\d{4}$"),
    "CLASS": re.compile(r"^CLASS-\d{4}$"),
    "SOURCE": re.compile(r"^SOURCE-\d{4}$"),
    "DIM": re.compile(r"^DIM-\d{4}$"),
    "STATE": re.compile(r"^STATE-\d{4}$"),
    "STD-DIM": re.compile(r"^STD-DIM-\d{4}$"),
    "STD-RULE": re.compile(r"^STD-RULE-\d{4}$"),
    "PROTO-STAGE": re.compile(r"^PROTO-STAGE-\d{4}$"),
    "PROTO-RULE": re.compile(r"^PROTO-RULE-\d{4}$"),
    "OUT-FIELD": re.compile(r"^OUT-FIELD-\d{4}$"),
    "ENG-IN": re.compile(r"^ENG-IN-\d{4}$"),
    "ENG-LAYER": re.compile(r"^ENG-LAYER-\d{4}$"),
    "FIXTURE": re.compile(r"^FIXTURE-\d{4}$"),
}

DIMENSION_REQUIRED = {
    "dimension_id",
    "name",
    "definition",
    "applies_to",
    "prohibited_interpretation",
    "related_terms",
    "status",
}

STATE_REQUIRED = {
    "state_id",
    "label",
    "definition",
    "required_conditions",
    "boundary_statement",
    "prohibited_interpretations",
    "allowed_output_language",
    "status",
}

TAXONOMY_STATE_PROHIBITED = [
    "fake",
    "real",
    "true",
    "false",
    "detects all",
    "guaranteed",
    "certifies truth",
    "proves guilt",
    "fraud by association",
    "deceptive person",
    "lie score",
    "truth score",
]

TAXONOMY_TOP_REQUIRED = {
    "taxonomy_id",
    "name",
    "version",
    "status",
    "governing_principle",
    "applies_to",
    "does_not_apply_to",
    "dimensions",
    "states",
    "prohibited_state_names",
    "prohibited_output_patterns",
    "allowed_output_patterns",
    "last_reviewed",
}

WORD_BOUNDARY_TERMS = {"fake", "real", "true", "false"}

STD_DIMENSION_REQUIRED = {
    "dimension_id",
    "taxonomy_dimension_id",
    "name",
    "sufficient_condition",
    "limited_condition",
    "weak_condition",
    "not_assessable_condition",
    "prohibited_interpretation",
    "status",
}

STD_RULE_REQUIRED = {
    "rule_id",
    "taxonomy_state_id",
    "state_label",
    "required_conditions",
    "boundary_statement",
    "minimum_output_language",
    "prohibited_interpretations",
    "status",
}

STANDARD_TOP_REQUIRED = {
    "standard_id",
    "name",
    "version",
    "status",
    "governing_principle",
    "taxonomy_dependency",
    "applies_to",
    "does_not_apply_to",
    "dimensions",
    "posture_sufficiency_rules",
    "minimum_output_boundary",
    "prohibited_uses",
    "maturity",
    "last_reviewed",
}

STANDARD_RULE_PROHIBITED = [
    "truth verdict",
    "fake/real detector",
    "detects all",
    "guaranteed detection",
    "certifies truth",
    "proves guilt",
    "fraud by association",
    "deceptive person",
    "lie score",
    "truth score",
]

PROTOCOL_STAGE_REQUIRED = {
    "stage_id",
    "name",
    "purpose",
    "required_checks",
    "maps_to_dimensions",
    "possible_stop_conditions",
    "prohibited_interpretations",
    "status",
}

PROTOCOL_RULE_REQUIRED = {
    "selection_rule_id",
    "taxonomy_state_id",
    "standard_rule_id",
    "state_label",
    "selection_conditions",
    "boundary_statement",
    "prohibited_interpretations",
    "fallback_state",
    "status",
}

PROTOCOL_TOP_REQUIRED = {
    "protocol_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "taxonomy_dependency",
    "standard_dependency",
    "applies_to",
    "does_not_apply_to",
    "stages",
    "state_selection_rules",
    "stop_conditions",
    "minimum_output_shape",
    "prohibited_outputs",
    "last_reviewed",
}

PROTOCOL_PROHIBITED = [
    "truth score",
    "lie score",
    "deepfake detected",
    "guaranteed detection",
    "certifies truth",
    "proves guilt",
    "proves fraud",
    "deceptive person",
    "guilty institution",
]

PROTOCOL_WORD_BOUNDARY = {"fake", "real"}

SCHEMA_FIELD_REQUIRED = {
    "field_id",
    "field_name",
    "required",
    "field_type",
    "definition",
    "prohibited_use",
    "boundary_requirement",
    "status",
}

SCHEMA_TOP_REQUIRED = {
    "schema_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "dependencies",
    "required_output_fields",
    "allowed_posture_states",
    "required_boundary_statements",
    "prohibited_output_fields",
    "prohibited_output_language",
    "allowed_output_language_examples",
    "minimum_output_template",
    "output_status_values",
    "last_reviewed",
}

SCHEMA_REQUIRED_FIELD_NAMES = {
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
    "last_reviewed",
}

SCHEMA_PROHIBITED_LANGUAGE = [
    "this is fake",
    "this is real",
    "truth score",
    "lie score",
    "deepfake detected",
    "guaranteed detection",
    "certifies truth",
    "authenticity certified",
    "hoax confirmed",
    "proves guilt",
    "proves fraud",
    "deceptive person",
    "guilty institution",
]

SCHEMA_PROHIBITED_FIELDS = {
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
    "legal_conclusion",
    "guilt_finding",
}

ENGINE_PROHIBITED_INPUT_FIELDS = {
    "person_score",
    "institution_score",
    "truth_score",
    "fake_real_result",
    "upload_file",
    "accusation_target",
    "guilt_question",
    "deception_question",
}

ENGINE_PROHIBITED_OUTPUT_CATEGORIES = [
    ("scoring", ["truth_score", "lie_score", "guilt_score", "authenticity_score"]),
    ("fake/real", ["this is fake", "this is real", "fake_real"]),
    ("truth verdict", ["truth verdict", "pass/fail truth"]),
    ("accusation", ["accusation", "subject accusation"]),
    ("subject classification", ["subject classification", "subject judgment"]),
    ("upload workflow", ["upload workflow", "upload_file"]),
    ("public classifier", ["public classifier", "active classifier"]),
]

FIXTURE_REQUIRED = {
    "fixture_id",
    "fixture_name",
    "fictional",
    "artifact_type",
    "input_summary",
    "expected_allowed_posture_states",
    "required_boundary_statement",
    "prohibited_interpretations",
    "expected_output_status",
    "notes",
}

FIXTURE_PROHIBITED_LANGUAGE = [
    "this is fake",
    "this is real",
    "truth score",
    "lie score",
    "upload file",
    "upload workflow",
    "public classifier",
    "active classifier",
    "live tool",
    "deepfake detected",
]

FIXTURE_REAL_ENTITY_MARKERS = [
    "donald trump",
    "joe biden",
    "elon musk",
    "google",
    "microsoft",
    "facebook",
    "meta platforms",
    "united nations",
    "white house",
    "congress",
    "ukraine war",
    "israel",
    "hamas",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_unique_ids(items: list[dict], key: str, prefix: str, label: str) -> bool:
    ok = True
    seen: set[str] = set()
    pattern = ID_PATTERNS[prefix]
    for item in items:
        item_id = item.get(key, "")
        if not pattern.match(item_id):
            error(f"{label}: invalid ID format '{item_id}'")
            ok = False
        if item_id in seen:
            error(f"{label}: duplicate ID '{item_id}'")
            ok = False
        seen.add(item_id)
    return ok


def validate_required_fields(items: list[dict], required: set[str], label: str) -> bool:
    ok = True
    for item in items:
        item_id = item.get(next(iter(required), "id"), item.get("claim_id", "?"))
        missing = required - set(item.keys())
        if missing:
            error(f"{label} '{item_id}': missing fields {sorted(missing)}")
            ok = False
    return ok


def validate_evidence_ledger() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-ledger.json")
    claims = data.get("claims", [])
    ok &= validate_unique_ids(claims, "claim_id", "CLAIM", "evidence-ledger")
    ok &= validate_required_fields(claims, LEDGER_REQUIRED, "evidence-ledger")

    for claim in claims:
        cid = claim["claim_id"]
        posture = claim.get("evidence_posture")
        if posture not in EVIDENCE_POSTURES:
            error(f"evidence-ledger '{cid}': invalid evidence_posture '{posture}'")
            ok = False
        ctype = claim.get("claim_type")
        if ctype not in CLAIM_TYPES:
            error(f"evidence-ledger '{cid}': invalid claim_type '{ctype}'")
            ok = False
        if ctype == "future_capability_claim" and posture not in {
            "planned_not_claimed",
            "conceptual",
            "retired",
        }:
            error(
                f"evidence-ledger '{cid}': future capability must not be marked as existing"
            )
            ok = False
        if posture == "planned_not_claimed" and ctype not in {
            "future_capability_claim",
            "conceptual_thesis",
        }:
            error(
                f"evidence-ledger '{cid}': planned_not_claimed used on non-future claim"
            )
            ok = False
    return ok


def path_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if not path.endswith("/") and "." not in Path(path).name:
        path = path + "/"
    return path if path != "" else "/"


def validate_route_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "route-registry.json")
    routes = data.get("routes", [])
    ok &= validate_unique_ids(routes, "route_id", "ROUTE", "route-registry")
    ok &= validate_required_fields(routes, ROUTE_REQUIRED, "route-registry")

    paths = {r["path"] for r in routes}
    if "/" not in paths:
        error("route-registry: route / must exist")
        ok = False

    sitemap_paths: set[str] = set()
    registry_sitemap_paths: set[str] = set()

    for route in routes:
        if route.get("sitemap_included"):
            registry_sitemap_paths.add(route["path"])

    sitemap_file = ROOT / "sitemap.xml"
    if sitemap_file.exists():
        tree = ElementTree.parse(sitemap_file)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for loc in tree.findall(".//sm:loc", ns):
            if loc.text:
                sitemap_paths.add(path_from_url(loc.text.strip()))

        for sp in sorted(sitemap_paths):
            if sp not in paths:
                error(f"sitemap.xml: URL path '{sp}' not in route-registry.json")
                ok = False

        for rp in sorted(registry_sitemap_paths):
            if rp not in sitemap_paths:
                error(
                    f"route-registry: sitemap_included path '{rp}' missing from sitemap.xml"
                )
                ok = False

    deferred = [
        r for r in routes if r.get("deployment_status") == "external_deployment_deferred"
    ]
    if not deferred:
        error("route-registry: external_deployment_deferred status expected for deferred routes")
        ok = False

    return ok


def validate_category_language() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "category-language.json")
    terms = data.get("terms", [])
    ok &= validate_unique_ids(terms, "term_id", "TERM", "category-language")
    ok &= validate_required_fields(terms, TERM_REQUIRED, "category-language")

    for term in terms:
        tid = term["term_id"]
        definition = term.get("definition", "").lower()
        for phrase in CATEGORY_PROHIBITED:
            if phrase in definition:
                error(
                    f"category-language '{tid}': prohibited product language '{phrase}' in definition"
                )
                ok = False
    return ok


def validate_ontology_foundation() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "ontology-foundation.json")
    classes = data.get("classes", [])
    ok &= validate_unique_ids(classes, "class_id", "CLASS", "ontology-foundation")
    ok &= validate_required_fields(classes, CLASS_REQUIRED, "ontology-foundation")

    subject = None
    posture_class = None
    for cls in classes:
        if cls.get("class_name") == "SubjectReference":
            subject = cls
        if cls.get("class_name") == "EvidencePostureClassification":
            posture_class = cls

    if subject is None:
        error("ontology-foundation: SubjectReference class missing")
        ok = False
    else:
        combined = " ".join(
            [
                subject.get("definition", ""),
                subject.get("prohibited_use", ""),
                subject.get("notes", ""),
            ]
        ).lower()
        boundary_markers = [
            "artifact–subject separation",
            "artifact-subject separation",
            "not a classification target",
            "not evidence about people",
        ]
        if not any(marker in combined for marker in boundary_markers):
            error(
                "ontology-foundation: SubjectReference missing artifact–subject boundary language"
            )
            ok = False

    if posture_class is None:
        error("ontology-foundation: EvidencePostureClassification class missing")
        ok = False
    else:
        combined = " ".join(
            [
                posture_class.get("definition", ""),
                posture_class.get("prohibited_use", ""),
                posture_class.get("status", ""),
                posture_class.get("notes", ""),
            ]
        ).lower()
        if "active tool" in combined and "not" not in combined.split("active tool")[0][-20:]:
            pass
        active_markers = ["active tool", "live scoring", "currently deployed", "operational tool"]
        for marker in active_markers:
            if marker in combined and "not" not in combined:
                # allow if marker only in prohibited_use negation context
                if marker in posture_class.get("prohibited_use", "").lower():
                    continue
                error(
                    f"ontology-foundation: EvidencePostureClassification described as active tool ('{marker}')"
                )
                ok = False
        if posture_class.get("status") != "planned_not_deployed":
            error(
                "ontology-foundation: EvidencePostureClassification must be planned_not_deployed"
            )
            ok = False

    for cls in classes:
        prohibited = cls.get("prohibited_use", "").lower()
        definition = cls.get("definition", "").lower()
        for phrase in [
            "classify people",
            "classify institutions",
            "classify the person",
            "subject accusation target",
            "guilt assessment of",
        ]:
            if phrase in definition and cls.get("class_name") != "SubjectReference":
                error(
                    f"ontology-foundation '{cls['class_id']}': class describes people/institutions as classification targets"
                )
                ok = False
    return ok


def contains_prohibited_taxonomy_term(text: str, term: str) -> bool:
    lower = text.lower()
    if term in WORD_BOUNDARY_TERMS:
        return bool(re.search(rf"\b{re.escape(term)}\b", lower))
    return term in lower


def validate_evidence_posture_taxonomy() -> bool:
    ok = True
    path = ROOT / "data" / "evidence-posture-taxonomy.json"
    data = load_json(path)

    missing_top = TAXONOMY_TOP_REQUIRED - set(data.keys())
    if missing_top:
        error(f"evidence-posture-taxonomy: missing top-level fields {sorted(missing_top)}")
        ok = False

    if not data.get("taxonomy_id"):
        error("evidence-posture-taxonomy: taxonomy_id missing")
        ok = False
    if not data.get("version"):
        error("evidence-posture-taxonomy: version missing")
        ok = False

    dimensions = data.get("dimensions", [])
    states = data.get("states", [])
    if not dimensions:
        error("evidence-posture-taxonomy: dimensions missing or empty")
        ok = False
    if not states:
        error("evidence-posture-taxonomy: states missing or empty")
        ok = False

    ok &= validate_unique_ids(dimensions, "dimension_id", "DIM", "evidence-posture-taxonomy")
    ok &= validate_unique_ids(states, "state_id", "STATE", "evidence-posture-taxonomy")
    ok &= validate_required_fields(dimensions, DIMENSION_REQUIRED, "evidence-posture-taxonomy dimension")
    ok &= validate_required_fields(states, STATE_REQUIRED, "evidence-posture-taxonomy state")

    prohibited_names = {n.lower() for n in data.get("prohibited_state_names", [])}
    labels = {s.get("label", "").lower() for s in states}

    for state in states:
        sid = state["state_id"]
        label = state.get("label", "")
        definition = state.get("definition", "")
        boundary = state.get("boundary_statement", "")

        if not boundary.strip():
            error(f"evidence-posture-taxonomy '{sid}': boundary_statement missing")
            ok = False

        if label.lower() in prohibited_names:
            error(f"evidence-posture-taxonomy '{sid}': label matches prohibited state name")
            ok = False

        for field_name, field_text in [("label", label), ("definition", definition)]:
            for term in TAXONOMY_STATE_PROHIBITED:
                if contains_prohibited_taxonomy_term(field_text, term):
                    error(
                        f"evidence-posture-taxonomy '{sid}': prohibited term '{term}' in {field_name}"
                    )
                    ok = False

    high_risk = next((s for s in states if s.get("label") == "high_risk_evidence_posture"), None)
    if high_risk is None:
        error("evidence-posture-taxonomy: high_risk_evidence_posture state missing")
        ok = False
    else:
        combined = " ".join(
            [
                high_risk.get("boundary_statement", ""),
                " ".join(high_risk.get("prohibited_interpretations", [])),
            ]
        ).lower()
        for marker in ["deception", "guilt", "fraud", "subject involvement", "subject accusation"]:
            if marker not in combined:
                error(
                    f"evidence-posture-taxonomy: high_risk_evidence_posture missing boundary marker '{marker}'"
                )
                ok = False

    not_assessable = next((s for s in states if s.get("label") == "not_assessable_posture"), None)
    if not_assessable is None:
        error("evidence-posture-taxonomy: not_assessable_posture state missing")
        ok = False
    else:
        boundary = not_assessable.get("boundary_statement", "").lower()
        if "not suspicious" not in boundary and "not assessable is not" not in boundary:
            error(
                "evidence-posture-taxonomy: not_assessable_posture must state not assessable is not suspicion"
            )
            ok = False

    planned = next((s for s in states if s.get("label") == "planned_not_claimed_posture"), None)
    if planned is None:
        error("evidence-posture-taxonomy: planned_not_claimed_posture state missing")
        ok = False

    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in ["EVIDENCE_POSTURE_TAXONOMY.md", "data/evidence-posture-taxonomy.json"]:
        if required not in locations:
            error(f"source-registry: missing taxonomy source '{required}'")
            ok = False

    return ok


def contains_prohibited_standard_phrase(text: str, phrase: str) -> bool:
    lower = text.lower()
    idx = 0
    while True:
        pos = lower.find(phrase, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 25) : pos]
        if any(
            marker in prefix
            for marker in ["no ", "not ", "without ", "never ", "avoid ", "does not "]
        ):
            idx = pos + len(phrase)
            continue
        return True
    return False


def validate_evidence_posture_standard() -> bool:
    ok = True
    taxonomy = load_json(ROOT / "data" / "evidence-posture-taxonomy.json")
    taxonomy_dim_ids = {d["dimension_id"] for d in taxonomy.get("dimensions", [])}
    taxonomy_state_ids = {s["state_id"] for s in taxonomy.get("states", [])}
    taxonomy_state_labels = {s["label"] for s in taxonomy.get("states", [])}

    data = load_json(ROOT / "data" / "evidence-posture-standard.json")
    missing_top = STANDARD_TOP_REQUIRED - set(data.keys())
    if missing_top:
        error(f"evidence-posture-standard: missing top-level fields {sorted(missing_top)}")
        ok = False

    if not data.get("standard_id"):
        error("evidence-posture-standard: standard_id missing")
        ok = False
    if not data.get("version"):
        error("evidence-posture-standard: version missing")
        ok = False
    if not data.get("taxonomy_dependency"):
        error("evidence-posture-standard: taxonomy_dependency missing")
        ok = False
    if data.get("taxonomy_dependency") != taxonomy.get("taxonomy_id"):
        error("evidence-posture-standard: taxonomy_dependency does not match taxonomy_id")
        ok = False

    dimensions = data.get("dimensions", [])
    rules = data.get("posture_sufficiency_rules", [])
    if not dimensions:
        error("evidence-posture-standard: dimensions missing or empty")
        ok = False
    if not rules:
        error("evidence-posture-standard: posture_sufficiency_rules missing or empty")
        ok = False

    ok &= validate_unique_ids(dimensions, "dimension_id", "STD-DIM", "evidence-posture-standard")
    ok &= validate_unique_ids(rules, "rule_id", "STD-RULE", "evidence-posture-standard")
    ok &= validate_required_fields(dimensions, STD_DIMENSION_REQUIRED, "evidence-posture-standard dimension")
    ok &= validate_required_fields(rules, STD_RULE_REQUIRED, "evidence-posture-standard rule")

    for dim in dimensions:
        tax_id = dim.get("taxonomy_dimension_id")
        if tax_id not in taxonomy_dim_ids:
            error(
                f"evidence-posture-standard '{dim['dimension_id']}': invalid taxonomy_dimension_id '{tax_id}'"
            )
            ok = False

    for rule in rules:
        rid = rule["rule_id"]
        state_id = rule.get("taxonomy_state_id")
        label = rule.get("state_label", "")

        if state_id not in taxonomy_state_ids:
            error(f"evidence-posture-standard '{rid}': invalid taxonomy_state_id '{state_id}'")
            ok = False
        if label not in taxonomy_state_labels:
            error(f"evidence-posture-standard '{rid}': state_label '{label}' not in taxonomy")
            ok = False

        boundary = rule.get("boundary_statement", "")
        if not boundary.strip():
            error(f"evidence-posture-standard '{rid}': boundary_statement missing")
            ok = False

        scan_text = " ".join(
            [
                " ".join(rule.get("required_conditions", [])),
                boundary,
                " ".join(rule.get("minimum_output_language", [])),
            ]
        )
        for phrase in STANDARD_RULE_PROHIBITED:
            if contains_prohibited_standard_phrase(scan_text, phrase):
                error(
                    f"evidence-posture-standard '{rid}': prohibited phrase '{phrase}' in rule output fields"
                )
                ok = False

    high_risk = next((r for r in rules if r.get("state_label") == "high_risk_evidence_posture"), None)
    if high_risk is None:
        error("evidence-posture-standard: high_risk_evidence_posture rule missing")
        ok = False
    else:
        combined = " ".join(
            [
                high_risk.get("boundary_statement", ""),
                " ".join(high_risk.get("minimum_output_language", [])),
                " ".join(high_risk.get("prohibited_interpretations", [])),
            ]
        ).lower()
        for marker in [
            "subject accusation",
            "connected subject",
            "artifact or evidence chain only",
            "deception",
            "guilt",
            "fraud",
            "involvement",
        ]:
            if marker not in combined:
                error(
                    f"evidence-posture-standard: high_risk rule missing subject-separation marker '{marker}'"
                )
                ok = False

    not_assessable = next((r for r in rules if r.get("state_label") == "not_assessable_posture"), None)
    if not_assessable is None:
        error("evidence-posture-standard: not_assessable_posture rule missing")
        ok = False
    else:
        boundary = not_assessable.get("boundary_statement", "").lower()
        if "not suspicious" not in boundary and "not assessable is not" not in boundary:
            error(
                "evidence-posture-standard: not_assessable_posture must state not assessable is not suspicion"
            )
            ok = False

    planned = next((r for r in rules if r.get("state_label") == "planned_not_claimed_posture"), None)
    if planned is None:
        error("evidence-posture-standard: planned_not_claimed_posture rule missing")
        ok = False
    else:
        combined = (
            planned.get("boundary_statement", "") + " " + " ".join(planned.get("minimum_output_language", []))
        ).lower()
        if "planned is not live" not in combined and "not currently active" not in combined:
            error("evidence-posture-standard: planned_not_claimed_posture must state planned is not live")
            ok = False

    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in ["EVIDENCE_POSTURE_STANDARD.md", "data/evidence-posture-standard.json"]:
        if required not in locations:
            error(f"source-registry: missing standard source '{required}'")
            ok = False

    return ok


def contains_prohibited_protocol_term(text: str, term: str) -> bool:
    lower = text.lower()
    if term in PROTOCOL_WORD_BOUNDARY:
        return bool(re.search(rf"\b{re.escape(term)}\b", lower))
    idx = 0
    while True:
        pos = lower.find(term, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 25) : pos]
        if any(
            marker in prefix
            for marker in ["no ", "not ", "without ", "never ", "avoid ", "does not ", "imply "]
        ):
            idx = pos + len(term)
            continue
        return True
    return False


def validate_evidence_posture_protocol() -> bool:
    ok = True
    taxonomy = load_json(ROOT / "data" / "evidence-posture-taxonomy.json")
    standard = load_json(ROOT / "data" / "evidence-posture-standard.json")
    taxonomy_dim_ids = {d["dimension_id"] for d in taxonomy.get("dimensions", [])}
    taxonomy_state_ids = {s["state_id"] for s in taxonomy.get("states", [])}
    taxonomy_state_labels = {s["label"] for s in taxonomy.get("states", [])}
    standard_rule_ids = {r["rule_id"] for r in standard.get("posture_sufficiency_rules", [])}

    data = load_json(ROOT / "data" / "evidence-posture-protocol.json")
    missing_top = PROTOCOL_TOP_REQUIRED - set(data.keys())
    if missing_top:
        error(f"evidence-posture-protocol: missing top-level fields {sorted(missing_top)}")
        ok = False

    if not data.get("protocol_id"):
        error("evidence-posture-protocol: protocol_id missing")
        ok = False
    if not data.get("version"):
        error("evidence-posture-protocol: version missing")
        ok = False
    if data.get("taxonomy_dependency") != taxonomy.get("taxonomy_id"):
        error("evidence-posture-protocol: taxonomy_dependency mismatch")
        ok = False
    if data.get("standard_dependency") != standard.get("standard_id"):
        error("evidence-posture-protocol: standard_dependency mismatch")
        ok = False
    if data.get("maturity") != "not_public_tool":
        error("evidence-posture-protocol: maturity must be not_public_tool")
        ok = False

    if not data.get("output_schema_dependency"):
        error("evidence-posture-protocol: output_schema_dependency missing")
        ok = False
    elif data.get("output_schema_dependency") != "SCHEMA-OUTPUT-BOUNDARY-001":
        error("evidence-posture-protocol: output_schema_dependency mismatch")
        ok = False

    protocol_md = ROOT / "EVIDENCE_POSTURE_CLASSIFICATION_PROTOCOL.md"
    if protocol_md.exists():
        md_text = protocol_md.read_text(encoding="utf-8").lower()
        if "output_boundary_schema" not in md_text and "output boundary schema" not in md_text:
            error("evidence-posture-protocol: protocol document missing output schema reference")
            ok = False

    status = data.get("status", "").lower()
    if "active_classifier" in status or "live_tool" in status:
        error("evidence-posture-protocol: status implies active classifier")
        ok = False

    stages = data.get("stages", [])
    rules = data.get("state_selection_rules", [])
    stop_conditions = data.get("stop_conditions", [])
    output_shape = data.get("minimum_output_shape", {})

    if not stages:
        error("evidence-posture-protocol: stages missing or empty")
        ok = False
    if not rules:
        error("evidence-posture-protocol: state_selection_rules missing or empty")
        ok = False

    ok &= validate_unique_ids(stages, "stage_id", "PROTO-STAGE", "evidence-posture-protocol")
    ok &= validate_unique_ids(rules, "selection_rule_id", "PROTO-RULE", "evidence-posture-protocol")
    ok &= validate_required_fields(stages, PROTOCOL_STAGE_REQUIRED, "evidence-posture-protocol stage")
    ok &= validate_required_fields(rules, PROTOCOL_RULE_REQUIRED, "evidence-posture-protocol rule")

    stop_text = " ".join(stop_conditions).lower()
    if "subject separation" not in stop_text:
        error("evidence-posture-protocol: stop_conditions must include subject-separation failure")
        ok = False

    if "subject_boundary_statement" not in output_shape:
        error("evidence-posture-protocol: minimum_output_shape missing subject_boundary_statement")
        ok = False
    if "prohibited_interpretations" not in output_shape:
        error("evidence-posture-protocol: minimum_output_shape missing prohibited_interpretations")
        ok = False

    for stage in stages:
        sid = stage["stage_id"]
        for dim_id in stage.get("maps_to_dimensions", []):
            if dim_id not in taxonomy_dim_ids:
                error(
                    f"evidence-posture-protocol '{sid}': invalid maps_to_dimensions '{dim_id}'"
                )
                ok = False
        scan_text = " ".join(
            [
                stage.get("purpose", ""),
                " ".join(stage.get("required_checks", [])),
                " ".join(stage.get("possible_stop_conditions", [])),
            ]
        )
        for term in PROTOCOL_PROHIBITED:
            if contains_prohibited_protocol_term(scan_text, term):
                error(f"evidence-posture-protocol '{sid}': prohibited term '{term}' in stage")
                ok = False
        for term in PROTOCOL_WORD_BOUNDARY:
            if contains_prohibited_protocol_term(scan_text, term):
                error(f"evidence-posture-protocol '{sid}': prohibited term '{term}' in stage")
                ok = False

    for rule in rules:
        rid = rule["selection_rule_id"]
        state_id = rule.get("taxonomy_state_id")
        std_rule = rule.get("standard_rule_id")
        label = rule.get("state_label", "")

        if state_id not in taxonomy_state_ids:
            error(f"evidence-posture-protocol '{rid}': invalid taxonomy_state_id '{state_id}'")
            ok = False
        if std_rule not in standard_rule_ids:
            error(f"evidence-posture-protocol '{rid}': invalid standard_rule_id '{std_rule}'")
            ok = False
        if label not in taxonomy_state_labels:
            error(f"evidence-posture-protocol '{rid}': state_label '{label}' not in taxonomy")
            ok = False

        scan_text = " ".join(
            [
                rule.get("boundary_statement", ""),
                " ".join(rule.get("selection_conditions", [])),
            ]
        )
        for term in PROTOCOL_PROHIBITED:
            if contains_prohibited_protocol_term(scan_text, term):
                error(f"evidence-posture-protocol '{rid}': prohibited term '{term}' in rule")
                ok = False
        for term in PROTOCOL_WORD_BOUNDARY:
            if contains_prohibited_protocol_term(scan_text, term):
                error(f"evidence-posture-protocol '{rid}': prohibited term '{term}' in rule")
                ok = False

    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in [
        "EVIDENCE_POSTURE_CLASSIFICATION_PROTOCOL.md",
        "data/evidence-posture-protocol.json",
    ]:
        if required not in locations:
            error(f"source-registry: missing protocol source '{required}'")
            ok = False

    return ok


def contains_prohibited_schema_language(text: str, phrase: str) -> bool:
    lower = text.lower()
    idx = 0
    while True:
        pos = lower.find(phrase, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 30) : pos]
        if any(
            marker in prefix
            for marker in [
                "no ",
                "not ",
                "without ",
                "never ",
                "avoid ",
                "does not ",
                "not be interpreted as ",
                "not a ",
            ]
        ):
            idx = pos + len(phrase)
            continue
        return True
    return False


def validate_output_boundary_schema() -> bool:
    ok = True
    taxonomy = load_json(ROOT / "data" / "evidence-posture-taxonomy.json")
    protocol = load_json(ROOT / "data" / "evidence-posture-protocol.json")
    taxonomy_state_labels = {s["label"] for s in taxonomy.get("states", [])}

    data = load_json(ROOT / "data" / "output-boundary-schema.json")
    missing_top = SCHEMA_TOP_REQUIRED - set(data.keys())
    if missing_top:
        error(f"output-boundary-schema: missing top-level fields {sorted(missing_top)}")
        ok = False

    if not data.get("schema_id"):
        error("output-boundary-schema: schema_id missing")
        ok = False
    if not data.get("version"):
        error("output-boundary-schema: version missing")
        ok = False
    if data.get("status") != "governed_internal_schema":
        error("output-boundary-schema: status must be governed_internal_schema")
        ok = False
    if data.get("maturity") != "not_public_tool":
        error("output-boundary-schema: maturity must be not_public_tool")
        ok = False
    if not data.get("dependencies"):
        error("output-boundary-schema: dependencies missing")
        ok = False

    fields = data.get("required_output_fields", [])
    if not fields:
        error("output-boundary-schema: required_output_fields missing or empty")
        ok = False

    ok &= validate_unique_ids(fields, "field_id", "OUT-FIELD", "output-boundary-schema")
    ok &= validate_required_fields(fields, SCHEMA_FIELD_REQUIRED, "output-boundary-schema field")

    field_names = {f.get("field_name") for f in fields}
    for required_name in SCHEMA_REQUIRED_FIELD_NAMES:
        if required_name not in field_names:
            error(f"output-boundary-schema: missing required field '{required_name}'")
            ok = False

    for prohibited in SCHEMA_PROHIBITED_FIELDS:
        if prohibited in field_names:
            error(f"output-boundary-schema: prohibited field '{prohibited}' in required_output_fields")
            ok = False

    posture_field = next((f for f in fields if f.get("field_name") == "posture_state"), None)
    if posture_field is None:
        error("output-boundary-schema: posture_state field missing")
        ok = False
    else:
        allowed = set(posture_field.get("allowed_values", []))
        if allowed != taxonomy_state_labels:
            error("output-boundary-schema: posture_state allowed_values do not match taxonomy")
            ok = False
        schema_allowed = set(data.get("allowed_posture_states", []))
        if schema_allowed != taxonomy_state_labels:
            error("output-boundary-schema: allowed_posture_states do not match taxonomy")
            ok = False

    subject_field = next(
        (f for f in fields if f.get("field_name") == "subject_boundary_statement"), None
    )
    if subject_field is None or not subject_field.get("required"):
        error("output-boundary-schema: subject_boundary_statement must be required")
        ok = False

    prohibited_field = next(
        (f for f in fields if f.get("field_name") == "prohibited_interpretations"), None
    )
    if prohibited_field is None or not prohibited_field.get("required"):
        error("output-boundary-schema: prohibited_interpretations must be required")
        ok = False

    confidence_field = next((f for f in fields if f.get("field_name") == "confidence_boundary"), None)
    if confidence_field is None:
        error("output-boundary-schema: confidence_boundary field missing")
        ok = False
    else:
        definition = confidence_field.get("definition", "").lower()
        if confidence_field.get("field_type") not in {"string", "text"}:
            error("output-boundary-schema: confidence_boundary must be qualitative string type")
            ok = False
        if "numeric" in definition and "not" not in definition.split("numeric")[0][-15:]:
            error("output-boundary-schema: confidence_boundary must not be numeric score")
            ok = False

    scan_parts = []
    for field in fields:
        scan_parts.extend(
            [
                field.get("definition", ""),
                field.get("prohibited_use", ""),
                field.get("boundary_requirement", ""),
            ]
        )
    scan_parts.extend(data.get("allowed_output_language_examples", []))
    scan_text = " ".join(scan_parts).lower()

    for phrase in SCHEMA_PROHIBITED_LANGUAGE:
        if contains_prohibited_schema_language(scan_text, phrase):
            error(f"output-boundary-schema: prohibited language '{phrase}' in schema content")
            ok = False

    if protocol.get("output_schema_dependency") != data.get("schema_id"):
        error("output-boundary-schema: protocol output_schema_dependency mismatch")
        ok = False

    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in ["OUTPUT_BOUNDARY_SCHEMA.md", "data/output-boundary-schema.json"]:
        if required not in locations:
            error(f"source-registry: missing output schema source '{required}'")
            ok = False

    return ok


def validate_internal_engine_model() -> bool:
    ok = True
    schema = load_json(ROOT / "data" / "output-boundary-schema.json")
    schema_field_names = {f["field_name"] for f in schema.get("required_output_fields", [])}

    data = load_json(ROOT / "data" / "internal-engine-model.json")

    if not data.get("engine_model_id"):
        error("internal-engine-model: engine_model_id missing")
        ok = False
    if not data.get("version"):
        error("internal-engine-model: version missing")
        ok = False
    if data.get("status") != "governed_internal_model":
        error("internal-engine-model: status must be governed_internal_model")
        ok = False
    if data.get("maturity") != "not_public_tool":
        error("internal-engine-model: maturity must be not_public_tool")
        ok = False
    if not data.get("dependencies"):
        error("internal-engine-model: dependencies missing")
        ok = False
    if not data.get("allowed_input_fields"):
        error("internal-engine-model: allowed_input_fields missing")
        ok = False
    if not data.get("processing_layers"):
        error("internal-engine-model: processing_layers missing")
        ok = False
    if not data.get("required_output_shape"):
        error("internal-engine-model: required_output_shape missing")
        ok = False

    output_limits = data.get("output_status_limits", [])
    if set(output_limits) != {"draft_internal", "governed_internal"}:
        error("internal-engine-model: output_status_limits must be draft_internal and governed_internal only")
        ok = False
    if "public_allowed_after_gate" in output_limits:
        error("internal-engine-model: public_allowed_after_gate not allowed in output_status_limits")
        ok = False

    deps = data.get("dependencies", {})
    for dep_key in ["taxonomy", "standard", "protocol", "output_schema"]:
        if not deps.get(dep_key):
            error(f"internal-engine-model: dependencies missing '{dep_key}'")
            ok = False

    inputs = data.get("allowed_input_fields", [])
    ok &= validate_unique_ids(inputs, "input_field_id", "ENG-IN", "internal-engine-model input")
    for field in inputs:
        fname = field.get("field_name", "")
        if fname in ENGINE_PROHIBITED_INPUT_FIELDS:
            error(f"internal-engine-model: prohibited input field '{fname}'")
            ok = False

    layers = data.get("processing_layers", [])
    ok &= validate_unique_ids(layers, "layer_id", "ENG-LAYER", "internal-engine-model layer")
    if len(layers) != 10:
        error(f"internal-engine-model: expected 10 processing layers, found {len(layers)}")
        ok = False

    layer_names = {layer.get("name", "") for layer in layers}
    for required_layer in ["Output Boundary Composition", "Governance Safety Check"]:
        if required_layer not in layer_names:
            error(f"internal-engine-model: missing processing layer '{required_layer}'")
            ok = False

    required_shape = set(data.get("required_output_shape", []))
    for field_name in SCHEMA_REQUIRED_FIELD_NAMES:
        if field_name not in required_shape:
            error(f"internal-engine-model: required_output_shape missing '{field_name}'")
            ok = False
    for field_name in required_shape:
        if field_name not in schema_field_names:
            error(f"internal-engine-model: required_output_shape field '{field_name}' not in output schema")
            ok = False

    conservative = data.get("conservative_resolution_rule", "").lower()
    if not conservative:
        error("internal-engine-model: conservative_resolution_rule missing")
        ok = False
    elif "bounded uncertainty" not in conservative or "speculative" not in conservative:
        error("internal-engine-model: conservative_resolution_rule must prefer bounded uncertainty over speculation")
        ok = False

    if not data.get("non_scoring_rule"):
        error("internal-engine-model: non_scoring_rule missing")
        ok = False

    prohibited_outputs = " ".join(data.get("prohibited_engine_outputs", [])).lower()
    for label, markers in ENGINE_PROHIBITED_OUTPUT_CATEGORIES:
        if not any(marker in prohibited_outputs for marker in markers):
            error(f"internal-engine-model: prohibited_engine_outputs missing {label} coverage")
            ok = False

    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in [
        "INTERNAL_ENGINE_MODEL.md",
        "data/internal-engine-model.json",
        "data/internal-engine-fixtures.json",
    ]:
        if required not in locations:
            error(f"source-registry: missing internal engine source '{required}'")
            ok = False

    return ok


def validate_internal_engine_fixtures() -> bool:
    ok = True
    taxonomy = load_json(ROOT / "data" / "evidence-posture-taxonomy.json")
    taxonomy_state_labels = {s["label"] for s in taxonomy.get("states", [])}

    data = load_json(ROOT / "data" / "internal-engine-fixtures.json")

    if not data.get("fixture_set_id"):
        error("internal-engine-fixtures: fixture_set_id missing")
        ok = False
    if not data.get("status"):
        error("internal-engine-fixtures: status missing")
        ok = False
    if data.get("maturity") != "internal_validation_only":
        error("internal-engine-fixtures: maturity must be internal_validation_only")
        ok = False

    fixtures = data.get("fixtures", [])
    if not fixtures:
        error("internal-engine-fixtures: fixtures missing or empty")
        ok = False
    if len(fixtures) < 3 or len(fixtures) > 5:
        error(f"internal-engine-fixtures: expected 3 to 5 fixtures, found {len(fixtures)}")
        ok = False

    ok &= validate_unique_ids(fixtures, "fixture_id", "FIXTURE", "internal-engine-fixtures")

    for fixture in fixtures:
        fid = fixture.get("fixture_id", "unknown")
        missing = FIXTURE_REQUIRED - set(fixture.keys())
        if missing:
            error(f"internal-engine-fixtures '{fid}': missing fields {sorted(missing)}")
            ok = False

        if fixture.get("fictional") is not True:
            error(f"internal-engine-fixtures '{fid}': fictional must be true")
            ok = False

        status = fixture.get("expected_output_status", "")
        if status not in {"draft_internal", "governed_internal"}:
            error(f"internal-engine-fixtures '{fid}': invalid expected_output_status '{status}'")
            ok = False

        for state in fixture.get("expected_allowed_posture_states", []):
            if state not in taxonomy_state_labels:
                error(f"internal-engine-fixtures '{fid}': invalid posture state '{state}'")
                ok = False

        scan_text = json.dumps(
            {
                k: v
                for k, v in fixture.items()
                if k not in {"prohibited_interpretations", "expected_allowed_posture_states"}
            }
        ).lower()
        for phrase in FIXTURE_PROHIBITED_LANGUAGE:
            if contains_prohibited_schema_language(scan_text, phrase):
                error(f"internal-engine-fixtures '{fid}': prohibited language '{phrase}'")
                ok = False
        for marker in FIXTURE_REAL_ENTITY_MARKERS:
            if marker in scan_text:
                error(f"internal-engine-fixtures '{fid}': real entity marker '{marker}'")
                ok = False

    return ok


def validate_source_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "source-registry.json")
    sources = data.get("sources", [])
    ok &= validate_unique_ids(sources, "source_id", "SOURCE", "source-registry")
    ok &= validate_required_fields(sources, SOURCE_REQUIRED, "source-registry")

    for source in sources:
        sid = source["source_id"]
        location = source.get("location", "")
        stype = source.get("source_type", "")
        if stype.startswith("internal"):
            if not (ROOT / location).exists():
                error(f"source-registry '{sid}': internal source file missing '{location}'")
                ok = False
        if stype == "external_web":
            error(f"source-registry '{sid}': unsupported external factual source in Sprint 1D")
            ok = False
    return ok


def line_has_unnegated_term(line: str, term: str) -> bool:
    lower = line.lower()
    if term not in lower:
        return False

    line_negations = [
        "does not",
        "do not",
        "not a ",
        "not an ",
        "no absolute",
        "not absolute",
        "never the ",
        "not on connected",
        "not to any person",
        "planned,",
        "under development",
    ]
    if any(neg in lower for neg in line_negations):
        return False

    idx = 0
    while True:
        pos = lower.find(term, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 50) : pos]
        if not NEGATION_PATTERN.search(prefix + term):
            return True
        idx = pos + len(term)
    return False


def validate_public_surface() -> bool:
    ok = True
    index_path = ROOT / "index.html"
    if not index_path.exists():
        error("public surface: index.html missing")
        return False

    content = index_path.read_text(encoding="utf-8")
    lower = content.lower()

    h1_count = len(re.findall(r"<h1\b", content, re.IGNORECASE))
    if h1_count != 1:
        error(f"public surface: expected exactly one H1, found {h1_count}")
        ok = False

    for phrase in INDEX_FORBIDDEN:
        if phrase in lower:
            error(f"public surface: forbidden phrase '{phrase}' in index.html")
            ok = False

    for line in content.splitlines():
        line_lower = line.lower()
        for term in INDEX_CONDITIONAL:
            if term in line_lower and line_has_unnegated_term(line, term):
                error(
                    f"public surface: '{term}' in index.html may imply live tool without clear negation"
                )
                ok = False

    artifact_markers = [
        "evidence artifact",
        "artifact–subject",
        "artifact-subject",
        "not on connected subjects",
        "not a statement about people",
    ]
    if not any(marker in lower for marker in artifact_markers):
        error("public surface: artifact–subject separation language not visible")
        ok = False

    return ok


def validate_json_files() -> bool:
    ok = True
    for rel in [
        "data/evidence-ledger.json",
        "data/route-registry.json",
        "data/category-language.json",
        "data/ontology-foundation.json",
        "data/source-registry.json",
        "data/evidence-posture-taxonomy.json",
        "data/evidence-posture-standard.json",
        "data/evidence-posture-protocol.json",
        "data/output-boundary-schema.json",
        "data/internal-engine-model.json",
        "data/internal-engine-fixtures.json",
        "data/forbidden-language-policy.json",
        "data/adversarial-validation-cases.json",
    ]:
        path = ROOT / rel
        try:
            load_json(path)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"JSON parse failed for {rel}: {exc}")
            ok = False
    return ok


def main() -> int:
    checks = [
        ("JSON validity", validate_json_files),
        ("Evidence ledger", validate_evidence_ledger),
        ("Route registry", validate_route_registry),
        ("Category language", validate_category_language),
        ("Ontology foundation", validate_ontology_foundation),
        ("Source registry", validate_source_registry),
        ("Evidence posture taxonomy", validate_evidence_posture_taxonomy),
        ("Evidence posture standard", validate_evidence_posture_standard),
        ("Evidence posture protocol", validate_evidence_posture_protocol),
        ("Output boundary schema", validate_output_boundary_schema),
        ("Internal engine model", validate_internal_engine_model),
        ("Internal engine fixtures", validate_internal_engine_fixtures),
        ("Public surface", validate_public_surface),
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
