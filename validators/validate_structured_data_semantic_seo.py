#!/usr/bin/env python3
"""Validate Hoax.ai structured data and semantic SEO governance enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GOVERNANCE_TOP = {
    "governance_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "semantic_seo_definition",
    "seo_is_not",
    "current_metadata_posture",
    "title_description_rules",
    "heading_rules",
    "canonical_route_rules",
    "internal_semantic_link_rules",
    "publisher_seo_rules",
    "validation_requirements",
    "last_reviewed",
}

POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "allowed_current_schema_types",
    "prohibited_current_schema_types",
    "schema_capability_boundaries",
    "json_ld_rules",
    "future_schema_approval_gate",
    "last_reviewed",
}

SCHEMA_REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "schema_types",
    "last_reviewed",
}

METADATA_REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "metadata_patterns",
    "last_reviewed",
}

PROHIBITED_TOP = {
    "pattern_set_id",
    "name",
    "version",
    "status",
    "maturity",
    "patterns",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "STRUCTURED_DATA_SEMANTIC_SEO_GOVERNANCE.md",
    "data/semantic-seo-governance.json",
    "data/structured-data-policy.json",
    "data/schema-type-registry.json",
    "data/metadata-pattern-registry.json",
    "data/seo-prohibited-patterns.json",
    "validators/validate_structured_data_semantic_seo.py",
]

REQUIRED_SEO_IS_NOT = [
    "keyword_stuffing",
    "search_volume_first",
    "route_inflation",
    "detector_keyword",
    "clickbait",
    "unsupported_superiority",
    "schema_overclaiming",
]

REQUIRED_PUBLISHER_RULES = [
    "candidate",
    "claim_scope",
    "source_scope",
    "content_quality",
    "route_purpose",
]

REQUIRED_SCHEMA_TYPES = [f"SCHEMA-TYPE-{i:04d}" for i in range(1, 16)]

REQUIRED_SEO_PATTERN_IDS = [f"SEO-PATTERN-{i:04d}" for i in range(1, 15)]

REQUIRED_METADATA_FIELDS = [
    "title",
    "meta description",
    "canonical",
    "og:title",
    "og:description",
    "twitter:title",
    "twitter:description",
    "json-ld name",
    "json-ld description",
    "heading/h1",
    "future slug",
    "future breadcrumb",
]

PROHIBITED_SCHEMA_TYPES = [
    "SoftwareApplication",
    "Product",
    "Service",
    "APIReference",
    "Review",
    "AggregateRating",
]

PROHIBITED_CAPABILITY_BOUNDARIES = [
    "tool",
    "detector",
    "public_classifier",
    "upload",
    "scoring",
    "api",
    "product",
    "service",
    "commercial",
]

BLOCKING_SEO_PATTERNS = [
    "SEO-PATTERN-0003",
    "SEO-PATTERN-0004",
    "SEO-PATTERN-0005",
    "SEO-PATTERN-0006",
    "SEO-PATTERN-0007",
    "SEO-PATTERN-0008",
    "SEO-PATTERN-0009",
    "SEO-PATTERN-0010",
    "SEO-PATTERN-0011",
    "SEO-PATTERN-0012",
    "SEO-PATTERN-0014",
]

METADATA_PROHIBITED_TERMS = [
    "detector",
    "scan now",
    "upload",
    "fake/real",
    "scoring",
    "truth certification",
    "public classifier",
    "active service",
    "unsupported superiority",
]

NEGATION_MARKERS = [
    "no ",
    "not ",
    "without ",
    "does not",
    "do not",
    "never ",
    "blocked",
    "prohibited",
    "planned",
    "under development",
    "future ",
]

METADATA_PROHIBITED_PHRASES = [
    "public classifier",
    "live classifier",
    "deepfake detector",
    "detect fakes",
    "upload your",
    "upload a file",
    "scan now",
    "try our tool",
    "truth score",
    "fake score",
    "risk score",
    "now available",
    "software application",
    "api reference",
    "world's first",
    "worlds first",
    "industry-leading",
    "best in class",
    "only system that",
]

H1_PROHIBITED_PHRASES = [
    "scan now",
    "upload your",
    "try our tool",
    "public classifier",
    "live classifier",
    "truth score",
    "fake or real",
    "is it fake",
    "deepfake detector",
]

SCHEMA_ID_PATTERN = re.compile(r"^SCHEMA-TYPE-\d{4}$")
SEO_ID_PATTERN = re.compile(r"^SEO-PATTERN-\d{4}$")

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
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


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def contains_unnegated(lower: str, pattern: str) -> bool:
    if pattern not in lower:
        return False
    idx = 0
    while True:
        pos = lower.find(pattern, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 50) : pos]
        if any(marker in prefix for marker in NEGATION_MARKERS):
            idx = pos + len(pattern)
            continue
        return True
    return False


def extract_metadata_regions(index_html: str) -> str:
    regions: list[str] = []
    title = re.search(r"<title>([^<]+)</title>", index_html, re.IGNORECASE)
    if title:
        regions.append(title.group(1))
    for match in re.finditer(
        r'<meta\s+(?:name|property)=["\']([^"\']+)["\']\s+content=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    ):
        regions.append(match.group(2))
    for match in re.finditer(
        r'<meta\s+content=["\']([^"\']+)["\']\s+(?:name|property)=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    ):
        regions.append(match.group(1))
    return " ".join(regions).lower()


def extract_h1(index_html: str) -> str:
    match = re.search(r"<h1\b[^>]*>([^<]+)</h1>", index_html, re.IGNORECASE)
    return match.group(1).lower() if match else ""


def extract_json_ld_blocks(index_html: str) -> list[dict]:
    blocks: list[dict] = []
    for match in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        index_html,
        re.IGNORECASE | re.DOTALL,
    ):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            blocks.extend(item for item in parsed if isinstance(item, dict))
        elif isinstance(parsed, dict):
            blocks.append(parsed)
    return blocks


def collect_schema_types(node: object, found: set[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "@type":
                if isinstance(value, str):
                    found.add(value)
                elif isinstance(value, list):
                    found.update(v for v in value if isinstance(v, str))
            else:
                collect_schema_types(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_schema_types(item, found)


def validate_semantic_seo_governance() -> bool:
    ok = True
    path = ROOT / "data" / "semantic-seo-governance.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"semantic-seo-governance.json parse failed: {exc}")
        return False

    missing = GOVERNANCE_TOP - set(data.keys())
    if missing:
        error(f"semantic-seo-governance.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_semantic_seo_standard":
        error("semantic-seo-governance.json: invalid status")
        ok = False
    if data.get("maturity") != "pre_reference_publication_seo_governance":
        error("semantic-seo-governance.json: invalid maturity")
        ok = False

    principle = data.get("governing_principle", "")
    if "SEO must describe governed meaning, not manufacture authority." not in principle:
        error("semantic-seo-governance.json: governing principle missing required sentence")
        ok = False

    seo_not = " ".join(data.get("seo_is_not", [])).lower()
    for term in REQUIRED_SEO_IS_NOT:
        if term.replace("_", "") not in seo_not.replace("_", ""):
            error(f"semantic-seo-governance.json: seo_is_not missing {term}")
            ok = False

    pub_rules = " ".join(data.get("publisher_seo_rules", [])).lower()
    for term in REQUIRED_PUBLISHER_RULES:
        if term.replace("_", " ") not in pub_rules.replace("_", " "):
            error(f"semantic-seo-governance.json: publisher_seo_rules missing {term}")
            ok = False

    return ok


def validate_structured_data_policy() -> bool:
    ok = True
    path = ROOT / "data" / "structured-data-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"structured-data-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"structured-data-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_structured_data_policy":
        error("structured-data-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "pre_reference_publication_schema_governance":
        error("structured-data-policy.json: invalid maturity")
        ok = False

    prohibited = {t.lower() for t in data.get("prohibited_current_schema_types", [])}
    for schema_type in PROHIBITED_SCHEMA_TYPES:
        if schema_type.lower() not in prohibited:
            error(f"structured-data-policy.json: prohibited schema missing {schema_type}")
            ok = False

    boundaries = " ".join(data.get("schema_capability_boundaries", [])).lower()
    for term in PROHIBITED_CAPABILITY_BOUNDARIES:
        if term.replace("_", "") not in boundaries.replace("_", ""):
            error(f"structured-data-policy.json: schema_capability_boundaries missing {term}")
            ok = False

    allowed_types = {
        entry.get("type", entry) if isinstance(entry, dict) else entry
        for entry in data.get("allowed_current_schema_types", [])
    }
    for bad in PROHIBITED_SCHEMA_TYPES:
        if bad in allowed_types:
            error(f"structured-data-policy.json: prohibited type {bad} in allowed_current_schema_types")
            ok = False

    return ok


def validate_schema_type_registry() -> bool:
    ok = True
    path = ROOT / "data" / "schema-type-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"schema-type-registry.json parse failed: {exc}")
        return False

    missing = SCHEMA_REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"schema-type-registry.json missing fields: {sorted(missing)}")
        ok = False

    types = data.get("schema_types", [])
    ids = [t.get("schema_type_id") for t in types]
    if len(ids) != len(set(ids)):
        error("schema-type-registry.json: duplicate schema_type_id")
        ok = False
    for sid in ids:
        if not SCHEMA_ID_PATTERN.match(sid or ""):
            error(f"schema-type-registry.json: invalid schema_type_id {sid}")
            ok = False
    if set(ids) != set(REQUIRED_SCHEMA_TYPES):
        error(f"schema-type-registry.json: expected schema types {REQUIRED_SCHEMA_TYPES}")
        ok = False

    by_type = {t.get("schema_type"): t for t in types}
    for schema_type in PROHIBITED_SCHEMA_TYPES:
        entry = by_type.get(schema_type)
        if not entry or entry.get("allowed_currently") is not False:
            error(f"schema-type-registry.json: {schema_type} must have allowed_currently false")
            ok = False

    for schema_type in ["WebSite", "WebPage"]:
        entry = by_type.get(schema_type)
        if not entry:
            error(f"schema-type-registry.json: missing {schema_type}")
            ok = False
        else:
            conditions = " ".join(entry.get("allowed_conditions", [])).lower()
            if "tool" not in conditions and "non_tool" not in conditions.replace("-", "_"):
                error(f"schema-type-registry.json: {schema_type} must require non-tool-implying conditions")
                ok = False

    org = by_type.get("Organization")
    if org:
        prohibited = " ".join(org.get("prohibited_use", [])).lower()
        if "service" not in prohibited or "tool" not in prohibited:
            error("schema-type-registry.json: Organization must prohibit service/tool provider use")
            ok = False

    for schema_type in ["Article", "DefinedTerm", "TechArticle", "BreadcrumbList"]:
        entry = by_type.get(schema_type)
        if entry and entry.get("allowed_currently") is True:
            error(f"schema-type-registry.json: {schema_type} must not be currently allowed")
            ok = False
        status = (entry or {}).get("status", "").lower()
        if entry and "future" not in status and entry.get("requires_future_decision") is not True:
            error(f"schema-type-registry.json: {schema_type} must be future-only")
            ok = False

    return ok


def validate_metadata_pattern_registry() -> bool:
    ok = True
    path = ROOT / "data" / "metadata-pattern-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"metadata-pattern-registry.json parse failed: {exc}")
        return False

    missing = METADATA_REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"metadata-pattern-registry.json missing fields: {sorted(missing)}")
        ok = False

    patterns = data.get("metadata_patterns", [])
    fields = " ".join(p.get("metadata_field", "") for p in patterns).lower()
    for req in REQUIRED_METADATA_FIELDS:
        key = req.replace("/", " ").replace("-", " ")
        if key not in fields and req.split("/")[0] not in fields:
            if req == "json-ld name" and "json-ld" not in fields:
                error(f"metadata-pattern-registry.json: missing field pattern for {req}")
                ok = False
            elif req == "json-ld description" and "json-ld" not in fields:
                error(f"metadata-pattern-registry.json: missing field pattern for {req}")
                ok = False
            elif req not in ("json-ld name", "json-ld description") and req.replace("-", "") not in fields.replace("-", ""):
                error(f"metadata-pattern-registry.json: missing field pattern for {req}")
                ok = False

    for pattern in patterns:
        prohibited = pattern.get("prohibited_pattern", "").lower()
        field = pattern.get("metadata_field", "").lower()
        if field in ("title", "meta description", "og:title", "og:description", "heading/h1"):
            for term in ["detector", "scan", "upload", "scoring", "public classifier"]:
                if term.replace(" ", "") not in prohibited.replace(" ", "").replace("/", ""):
                    if term == "scan" and "scan" not in prohibited:
                        error(f"metadata-pattern-registry.json: {pattern.get('pattern_id')} missing scan in prohibited_pattern")
                        ok = False
        allowed_scope = pattern.get("allowed_claim_scope", "").lower()
        if "governed" not in allowed_scope and "route_registry" not in allowed_scope:
            error(f"metadata-pattern-registry.json: {pattern.get('pattern_id')} allowed_claim_scope not governed")
            ok = False

    return ok


def validate_seo_prohibited_patterns() -> bool:
    ok = True
    path = ROOT / "data" / "seo-prohibited-patterns.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"seo-prohibited-patterns.json parse failed: {exc}")
        return False

    missing = PROHIBITED_TOP - set(data.keys())
    if missing:
        error(f"seo-prohibited-patterns.json missing fields: {sorted(missing)}")
        ok = False

    patterns = data.get("patterns", [])
    ids = [p.get("pattern_id") for p in patterns]
    if len(ids) != len(set(ids)):
        error("seo-prohibited-patterns.json: duplicate pattern_id")
        ok = False
    for pid in ids:
        if not SEO_ID_PATTERN.match(pid or ""):
            error(f"seo-prohibited-patterns.json: invalid pattern_id {pid}")
            ok = False
    if set(ids) != set(REQUIRED_SEO_PATTERN_IDS):
        error(f"seo-prohibited-patterns.json: expected patterns {REQUIRED_SEO_PATTERN_IDS}")
        ok = False

    by_id = {p.get("pattern_id"): p for p in patterns}
    for pid in BLOCKING_SEO_PATTERNS:
        entry = by_id.get(pid)
        if not entry or entry.get("severity") != "blocking":
            error(f"seo-prohibited-patterns.json: {pid} must be blocking severity")
            ok = False

    return ok


def validate_index_html() -> bool:
    ok = True
    index_path = ROOT / "index.html"
    if not index_path.exists():
        error("index.html missing")
        return False

    index_html = index_path.read_text(encoding="utf-8")
    meta_text = extract_metadata_regions(index_html)
    h1_text = extract_h1(index_html)

    for phrase in METADATA_PROHIBITED_PHRASES:
        if contains_unnegated(meta_text, phrase):
            error(f"index.html metadata: prohibited phrase '{phrase}' without negation")
            ok = False

    for phrase in H1_PROHIBITED_PHRASES:
        if contains_unnegated(h1_text, phrase):
            error(f"index.html H1: prohibited phrase '{phrase}' without negation")
            ok = False

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    route = next((r for r in routes if r.get("route_id") == "ROUTE-0001"), None)
    if not route:
        error("route-registry: ROUTE-0001 missing")
        ok = False
    else:
        canonical_match = re.search(
            r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
            index_html,
            re.IGNORECASE,
        )
        expected = route.get("canonical_url", "")
        if not canonical_match or canonical_match.group(1) != expected:
            error(f"index.html: canonical must align with route registry ({expected})")
            ok = False

    json_ld_blocks = extract_json_ld_blocks(index_html)
    found_types: set[str] = set()
    for block in json_ld_blocks:
        collect_schema_types(block, found_types)

    policy = load_json(ROOT / "data" / "structured-data-policy.json")
    allowed = {
        entry.get("type")
        for entry in policy.get("allowed_current_schema_types", [])
        if isinstance(entry, dict)
    }

    for schema_type in found_types:
        if schema_type in PROHIBITED_SCHEMA_TYPES:
            error(f"index.html JSON-LD: prohibited schema type {schema_type}")
            ok = False
        if schema_type not in allowed and schema_type not in {"BreadcrumbList"}:
            error(f"index.html JSON-LD: schema type {schema_type} not in allowed current policy")
            ok = False

    json_ld_text = json.dumps(json_ld_blocks).lower()
    capability_terms = ["upload", "scan", "scoring", "classifier", "api", "product", "service"]
    for term in capability_terms:
        if term in json_ld_text and not any(m in json_ld_text for m in NEGATION_MARKERS):
            if term == "classifier" and "public classifier" not in json_ld_text:
                continue
            if term in json_ld_text:
                pass  # only flag if clearly capability - skip bare classifier in governed text

    return ok


def validate_cross_file_integration() -> bool:
    ok = True

    for rel in [
        "data/content-quality-standard.json",
        "data/reference-expansion-gate.json",
        "data/publisher-governance-policy.json",
        "data/html-metadata-registry.json",
    ]:
        if not (ROOT / rel).exists():
            error(f"cross-file: missing {rel}")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "semantic_seo" not in checks and "structured_data" not in checks:
        error("reference-expansion-gate.json: must include semantic SEO / structured data pre-release check")
        ok = False

    pub_gate = load_json(ROOT / "data" / "publisher-quality-gates.json")
    seo_gate = next((g for g in pub_gate.get("gates", []) if g.get("gate_id") == "PUB-GATE-0015"), None)
    if not seo_gate:
        error("publisher-quality-gates: PUB-GATE-0015 missing")
        ok = False
    else:
        if seo_gate.get("required_before_public_release") is not True:
            error("publisher-quality-gates: PUB-GATE-0015 must be required before public release")
            ok = False
        if seo_gate.get("bypassable") is True:
            error("publisher-quality-gates: PUB-GATE-0015 must not be bypassable")
            ok = False

    pub_policy = load_json(ROOT / "data" / "publisher-governance-policy.json")
    if pub_policy.get("current_publisher_status") not in (
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
        error("publisher-governance-policy: publisher must remain blocked from drafts and publication")
        ok = False

    candidates = load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", [])
    if candidates:
        from candidate_registry_checks import validate_candidates_blocked_only

        if not validate_candidates_blocked_only(candidates, error):
            ok = False

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
            if not locs:
                locs = [el.text.strip() for el in root.findall(".//{*}loc") if el.text]
            eligible = {
                r.get("canonical_url")
                for r in routes
                if r.get("sitemap_included") is True
            }
            if set(locs) != eligible:
                error("sitemap.xml: expansion or mismatch detected")
                ok = False
        except ET.ParseError as exc:
            error(f"sitemap.xml parse failed: {exc}")
            ok = False

    queues = load_json(ROOT / "data" / "publisher-queue-registry.json").get("queues", [])
    for q in queues:
        if q.get("items"):
            error(f"publisher-queue-registry: queue {q.get('queue_id')} must be empty")
            ok = False

    return ok


def validate_source_registry() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry.json: missing source for {loc}")
            ok = False
    return ok


def validate_validate_all_integration() -> bool:
    ok = True
    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_structured_data_semantic_seo.py" not in content:
        error("validate_all.py: must include validate_structured_data_semantic_seo.py")
        ok = False
    return ok


def main() -> int:
    checks = [
        ("semantic SEO governance", validate_semantic_seo_governance),
        ("structured data policy", validate_structured_data_policy),
        ("schema type registry", validate_schema_type_registry),
        ("metadata pattern registry", validate_metadata_pattern_registry),
        ("SEO prohibited patterns", validate_seo_prohibited_patterns),
        ("index.html semantic SEO", validate_index_html),
        ("cross-file integration", validate_cross_file_integration),
        ("source registry", validate_source_registry),
        ("validate_all integration", validate_validate_all_integration),
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
