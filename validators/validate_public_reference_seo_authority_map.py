#!/usr/bin/env python3
"""Validate Sprint 67 Public Reference SEO Authority Map v1."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
)

MAP_DOC = ROOT / "PUBLIC_REFERENCE_SEO_AUTHORITY_MAP_V1.md"
MAP_JSON = ROOT / "data/public-reference-seo-authority-map-v1.json"
AUDIT = ROOT / "SPRINT_67_ENGINE_BOUNDARY_AND_SEO_AUTHORITY_MAP_AUDIT.md"

EXPECTED_CANDIDATES = [
    "/reference/evidence-sufficiency/",
    "/reference/source-corroboration/",
    "/reference/context-window/",
    "/reference/provenance-chain/",
    "/reference/media-lineage/",
    "/reference/synthetic-risk-signal/",
    "/reference/artifact-integrity/",
    "/reference/verification-burden/",
    "/reference/claim-context/",
    "/reference/evidence-threshold/",
    "/reference/interpretive-restraint/",
    "/reference/posture-state/",
]

REQUIRED_DOC_PHRASES = [
    "reference asset, not as a page-volume project",
    "No sitemap expansion is authorized",
    "Candidate pages are planning objects only",
    "no fake pages",
    "no unsupported external factual claims",
    "no route without route registry approval",
    "no sitemap entry before route validation",
    "no engine, classifier, upload, scoring, API, analytics, form, JavaScript",
    "no publication unless `validators/validate_all.py` passes",
]

REQUIRED_PROHIBITIONS = {
    "engine",
    "classifier",
    "detector",
    "upload",
    "scoring",
    "fake_real_verdict",
    "subject_accusation",
    "api",
    "analytics",
    "forms",
    "javascript",
    "monetization",
    "public_tool_behavior",
    "placeholder_pages",
    "unsupported_external_factual_claims",
}

FORBIDDEN_JSON_TERMS = [
    "DEC-084",
    "rick",
    "linkedin",
    "dns",
    "domain owner",
    "buyer conversation",
    "marketing notes",
    "cloudflare",
    "custom domain action",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def sitemap_locs() -> list[str]:
    tree = ET.parse(ROOT / "sitemap.xml")
    return [el.text.strip() for el in tree.findall(".//{*}loc") if el.text]


def validate_artifacts() -> bool:
    ok = True
    for path in [MAP_DOC, MAP_JSON, AUDIT]:
        if not path.is_file():
            error(f"missing artifact: {path.relative_to(ROOT).as_posix()}")
            ok = False
    if not ok:
        return False
    doc = MAP_DOC.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in doc:
            error(f"map document missing required phrase: {phrase}")
            ok = False
    for phrase in [
        "does not create a new route",
        "public surface remains exactly nineteen URLs",
        "candidate paths are absent from `sitemap.xml`",
    ]:
        if phrase not in audit:
            error(f"audit missing required phrase: {phrase}")
            ok = False
    raw_json = MAP_JSON.read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_JSON_TERMS:
        if term.lower() in raw_json:
            error(f"seo authority map JSON contains forbidden term: {term}")
            ok = False
    return ok


def validate_map_json() -> bool:
    ok = True
    data = load_json(MAP_JSON)
    if data.get("map_id") != "PUB-REF-SEO-AUTH-MAP-V1":
        error("map_id mismatch")
        ok = False
    if data.get("decision_ref") != "DEC-085":
        error("decision_ref must be DEC-085")
        ok = False
    if data.get("sprint") != "Sprint 67":
        error("sprint must be Sprint 67")
        ok = False
    if data.get("status") != "active_planning_artifact":
        error("status must be active_planning_artifact")
        ok = False
    if data.get("maturity") != "production_planning_only_no_new_routes_no_sitemap_expansion":
        error("maturity must preserve no-route/no-sitemap boundary")
        ok = False
    surface = data.get("current_public_surface", {})
    if surface.get("expected_url_count") != PUBLIC_SITEMAP_URL_COUNT:
        error("expected_url_count must match current public sitemap count")
        ok = False
    if surface.get("sitemap_must_remain_count") != PUBLIC_SITEMAP_URL_COUNT:
        error("sitemap_must_remain_count must be 19")
        ok = False
    if surface.get("route_registry_must_remain_count") != PUBLIC_SITEMAP_URL_COUNT:
        error("route_registry_must_remain_count must be 19")
        ok = False
    if surface.get("new_public_routes_authorized") is not False:
        error("new_public_routes_authorized must be false")
        ok = False
    if surface.get("new_sitemap_entries_authorized") is not False:
        error("new_sitemap_entries_authorized must be false")
        ok = False

    clusters = data.get("authority_clusters", [])
    if len(clusters) != 4:
        error("expected exactly four authority clusters")
        ok = False
    cluster_ids = {c.get("cluster_id") for c in clusters}
    expected_clusters = {
        "AUTH-CLUSTER-001",
        "AUTH-CLUSTER-002",
        "AUTH-CLUSTER-003",
        "AUTH-CLUSTER-004",
    }
    if cluster_ids != expected_clusters:
        error("authority cluster IDs mismatch")
        ok = False

    candidates = data.get("candidate_pages", [])
    paths = [c.get("proposed_path") for c in candidates]
    if paths != EXPECTED_CANDIDATES:
        error("candidate paths mismatch or ordering changed")
        ok = False
    if len({c.get("candidate_id") for c in candidates}) != len(EXPECTED_CANDIDATES):
        error("candidate IDs must be unique")
        ok = False
    for candidate in candidates:
        if candidate.get("status") != "candidate_only_no_route":
            error(f"{candidate.get('candidate_id')}: status must be candidate_only_no_route")
            ok = False
        if candidate.get("no_public_route_created") is not True:
            error(f"{candidate.get('candidate_id')}: no_public_route_created must be true")
            ok = False
        if candidate.get("no_sitemap_entry_created") is not True:
            error(f"{candidate.get('candidate_id')}: no_sitemap_entry_created must be true")
            ok = False
        if candidate.get("cluster_id") not in cluster_ids:
            error(f"{candidate.get('candidate_id')}: unknown cluster")
            ok = False
        if not re.match(r"^/reference/[a-z0-9-]+/$", candidate.get("proposed_path", "")):
            error(f"{candidate.get('candidate_id')}: invalid proposed path")
            ok = False

    prohibitions = set(data.get("prohibited_capabilities", []))
    missing = REQUIRED_PROHIBITIONS - prohibitions
    if missing:
        error(f"missing prohibited capabilities: {sorted(missing)}")
        ok = False
    for required in [
        "candidate_registered_before_route_creation",
        "route_registry_entry_before_sitemap_entry",
        "validate_all_pass_required",
    ]:
        if required not in data.get("publication_preconditions", []):
            error(f"missing publication precondition: {required}")
            ok = False
    return ok


def validate_no_public_surface_expansion() -> bool:
    ok = True
    routes = load_json(ROOT / "data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error("route registry must remain exactly 19 routes")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    registered_paths = {r.get("path") for r in routes}
    locs = sitemap_locs()
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error("sitemap must remain exactly 19 URLs")
        ok = False
    for candidate_path in EXPECTED_CANDIDATES:
        if candidate_path in registered_paths:
            error(f"candidate path must not be registered as route: {candidate_path}")
            ok = False
        if f"https://hoax.ai{candidate_path}" in locs:
            error(f"candidate path must not be in sitemap: {candidate_path}")
            ok = False
        rel = candidate_path.strip("/") + "/index.html"
        if (ROOT / rel).exists():
            error(f"candidate page must not exist yet: {rel}")
            ok = False
    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_PUBLIC_HTML and rel != "_internal_prototypes/evidence-posture-workbench/index.html":
            error(f"unexpected HTML file introduced: {rel}")
            ok = False
    return ok


def validate_registry_entries() -> bool:
    ok = True
    validate_all = (ROOT / "validators/validate_all.py").read_text(encoding="utf-8")
    if "validate_public_reference_seo_authority_map.py" not in validate_all:
        error("validate_all.py missing Sprint 67 SEO authority map validator")
        ok = False
    source_locs = {s.get("location") for s in load_json(ROOT / "data/source-registry.json").get("sources", [])}
    for loc in [
        "PUBLIC_REFERENCE_SEO_AUTHORITY_MAP_V1.md",
        "data/public-reference-seo-authority-map-v1.json",
        "validators/validate_public_reference_seo_authority_map.py",
        "SPRINT_67_ENGINE_BOUNDARY_AND_SEO_AUTHORITY_MAP_AUDIT.md",
    ]:
        if loc not in source_locs:
            error(f"source registry missing {loc}")
            ok = False
    if "Sprint 67 | COMPLETE | G67 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 67 completion row")
        ok = False
    return ok


def main() -> int:
    ok = all(
        fn()
        for fn in [
            validate_artifacts,
            validate_map_json,
            validate_no_public_surface_expansion,
            validate_registry_entries,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
