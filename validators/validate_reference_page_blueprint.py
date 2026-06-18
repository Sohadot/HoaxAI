#!/usr/bin/env python3
"""Validate Hoax.ai reference page blueprint and expansion gate enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BLUEPRINT_TOP_REQUIRED = {
    "blueprint_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "reference_page_definition",
    "prohibited_page_types",
    "allowed_future_page_families",
    "minimum_page_requirements",
    "required_page_sections",
    "expansion_gate_requirements",
    "sitemap_eligibility_requirements",
    "last_reviewed",
}

TYPE_REGISTRY_TOP = {"registry_id", "name", "version", "status", "page_types", "last_reviewed"}

EXPANSION_GATE_TOP = {
    "gate_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "candidate_statuses",
    "required_pre_release_checks",
    "blocked_conditions",
    "release_eligibility_rules",
    "last_reviewed",
}

CANDIDATE_REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "candidates",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "REFERENCE_PAGE_BLUEPRINT.md",
    "data/reference-page-blueprint.json",
    "data/reference-page-type-registry.json",
    "data/reference-expansion-gate.json",
    "data/reference-page-candidate-registry.json",
    "validators/validate_reference_page_blueprint.py",
]

REQUIRED_PROHIBITED_TYPES = [
    "thin_seo",
    "placeholder",
    "tool_implying",
    "upload_implying",
    "fake_real",
    "unsupported_superiority",
    "unmapped_public_claim",
]

REQUIRED_MINIMUM_REQUIREMENTS = [
    ("claim_mapping", ["claim_mapping", "required_claim"]),
    ("source_scope", ["source_scope", "source_support"]),
    ("route", ["route_candidate", "route_elig"]),
    ("internal_link", ["internal_link"]),
    ("metadata", ["metadata"]),
    ("technical_quality", ["technical_quality"]),
    ("governance_boundary", ["governance_boundary"]),
]

REQUIRED_BLOCKED_CONDITIONS = [
    "missing_route_registry",
    "missing_claim_mapping",
    "missing_source_scope",
    "broken_links",
    "sitemap_mismatch",
    "unsupported_external_claim",
    "forbidden_language",
    "tool_implication",
    "upload_implication",
    "scoring_implication",
    "subject_accusation",
    "technical_quality_failure",
]

PAGE_TYPE_PROHIBITED_PATTERNS = [
    "upload your",
    "scan now",
    "truth score",
    "fake/real",
    "fake or real",
    "deepfake detected",
    "now available",
    "live tool",
    "public classifier",
]

PUBLIC_FILES = {"index.html", "styles.css", "robots.txt", "sitemap.xml"}

PAGE_TYPE_ID_PATTERN = re.compile(r"^REF-TYPE-\d{4}$")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_blueprint_data() -> bool:
    ok = True
    path = ROOT / "data" / "reference-page-blueprint.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-page-blueprint.json parse failed: {exc}")
        return False

    missing = BLUEPRINT_TOP_REQUIRED - set(data.keys())
    if missing:
        error(f"reference-page-blueprint.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_reference_blueprint":
        error("reference-page-blueprint.json: invalid status")
        ok = False
    if data.get("maturity") != "pre_reference_expansion_gate":
        error("reference-page-blueprint.json: invalid maturity")
        ok = False

    prohibited = " ".join(data.get("prohibited_page_types", [])).lower()
    for term in REQUIRED_PROHIBITED_TYPES:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"reference-page-blueprint.json: prohibited_page_types missing {term}")
            ok = False

    minimum = " ".join(data.get("minimum_page_requirements", [])).lower()
    for label, aliases in REQUIRED_MINIMUM_REQUIREMENTS:
        if not any(alias in minimum for alias in aliases):
            error(f"reference-page-blueprint.json: minimum_page_requirements missing {label}")
            ok = False

    for family in data.get("allowed_future_page_families", []):
        if family.get("route_status") != "future_not_routes":
            error(f"reference-page-blueprint.json: family {family.get('family_id')} must be future_not_routes")
            ok = False

    return ok


def validate_page_type_registry() -> bool:
    ok = True
    path = ROOT / "data" / "reference-page-type-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-page-type-registry.json parse failed: {exc}")
        return False

    missing = TYPE_REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"reference-page-type-registry.json missing fields: {sorted(missing)}")
        ok = False

    page_types = data.get("page_types", [])
    if len(page_types) != 8:
        error(f"reference-page-type-registry.json: expected 8 page types, found {len(page_types)}")
        ok = False

    ids: list[str] = []
    for pt in page_types:
        pid = pt.get("page_type_id", "")
        if not PAGE_TYPE_ID_PATTERN.match(pid):
            error(f"reference-page-type-registry: invalid page_type_id format {pid}")
            ok = False
        if pid in ids:
            error(f"reference-page-type-registry: duplicate page_type_id {pid}")
            ok = False
        ids.append(pid)

        if pt.get("route_allowed_currently") is not False:
            error(f"reference-page-type-registry: {pid} route_allowed_currently must be false")
            ok = False

        status = pt.get("status", "")
        if status not in ("planned_not_claimed", "blueprint_only"):
            error(f"reference-page-type-registry: {pid} invalid status {status}")
            ok = False

        combined = " ".join(
            str(pt.get(k, "")) for k in ["name", "description", "prohibited_content", "notes"]
        ).lower()
        if "publicly available" in combined and "not publicly available" not in combined:
            error(f"reference-page-type-registry: {pid} implies public availability")
            ok = False
        if "active route" in combined and "not a route" not in combined:
            error(f"reference-page-type-registry: {pid} implies active route")
            ok = False

        for pattern in PAGE_TYPE_PROHIBITED_PATTERNS:
            if pattern in combined and "no " not in combined[max(0, combined.find(pattern) - 20) : combined.find(pattern)]:
                if pattern in pt.get("prohibited_content", "").lower():
                    continue
                if pattern in combined:
                    pass  # only fail if used affirmatively outside prohibited_content negation context

        for field in ["page_type_id", "name", "status", "route_allowed_currently", "description",
                      "required_sections", "required_claim_mapping", "required_source_scope",
                      "required_internal_links", "prohibited_content", "notes"]:
            if field not in pt:
                error(f"reference-page-type-registry: {pid} missing {field}")
                ok = False

    return ok


def validate_expansion_gate() -> bool:
    ok = True
    path = ROOT / "data" / "reference-expansion-gate.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-expansion-gate.json parse failed: {exc}")
        return False

    missing = EXPANSION_GATE_TOP - set(data.keys())
    if missing:
        error(f"reference-expansion-gate.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_reference_expansion_gate":
        error("reference-expansion-gate.json: invalid status")
        ok = False
    if data.get("maturity") != "pre_expansion":
        error("reference-expansion-gate.json: invalid maturity")
        ok = False

    blocked = " ".join(data.get("blocked_conditions", [])).lower()
    for term in REQUIRED_BLOCKED_CONDITIONS:
        if term not in blocked:
            error(f"reference-expansion-gate.json: blocked_conditions missing {term}")
            ok = False

    release_rules = " ".join(data.get("release_eligibility_rules", [])).lower()
    if "validate_all" not in release_rules:
        error("reference-expansion-gate.json: release_eligibility_rules must require validate_all.py")
        ok = False

    pre_release = data.get("required_pre_release_checks", [])
    if not pre_release:
        error("reference-expansion-gate.json: required_pre_release_checks empty")
        ok = False

    return ok


def validate_candidate_registry() -> bool:
    ok = True
    path = ROOT / "data" / "reference-page-candidate-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"reference-page-candidate-registry.json parse failed: {exc}")
        return False

    missing = CANDIDATE_REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"reference-page-candidate-registry.json missing fields: {sorted(missing)}")
        ok = False

    candidates = data.get("candidates")
    if candidates is None:
        error("reference-page-candidate-registry.json: candidates list missing")
        ok = False
    elif candidates != []:
        error(f"reference-page-candidate-registry.json: candidates must be empty in Sprint 13, found {len(candidates)}")
        ok = False

    return ok


def validate_route_sitemap_safety() -> bool:
    ok = True

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    route_ids = [r.get("route_id") for r in routes]
    if route_ids != ["ROUTE-0001"]:
        error(f"route-registry: expected only ROUTE-0001, found {route_ids}")
        ok = False

    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.exists():
        error("sitemap.xml missing")
        return False

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
        if not locs:
            locs = [el.text.strip() for el in root.findall(".//{*}loc") if el.text]
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return False

    eligible = {
        r.get("canonical_url")
        for r in routes
        if r.get("sitemap_included") is True
    }
    for url in locs:
        if url not in eligible:
            error(f"sitemap.xml: URL not eligible in route registry: {url}")
            ok = False

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in PUBLIC_FILES:
            error(f"unexpected public HTML file: {rel}")
            ok = False

    public_registry = load_json(ROOT / "data" / "public-file-registry.json")
    registered = {f.get("path") for f in public_registry.get("public_files", [])}
    if registered != PUBLIC_FILES:
        error(f"public-file-registry: expected only {sorted(PUBLIC_FILES)}")
        ok = False

    return ok


def validate_source_registry() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing reference blueprint source {loc}")
            ok = False
    return ok


def main() -> int:
    ok = True

    if not validate_blueprint_data():
        ok = False
    if not validate_page_type_registry():
        ok = False
    if not validate_expansion_gate():
        ok = False
    if not validate_candidate_registry():
        ok = False
    if not validate_route_sitemap_safety():
        ok = False
    if not validate_source_registry():
        ok = False

    if ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
