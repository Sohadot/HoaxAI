"""Shared public surface checks for Hoax.ai validators."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PUBLIC_ROUTE_IDS = ["ROUTE-0001", "ROUTE-0002", "ROUTE-0003", "ROUTE-0004"]

PILOT_ROUTE_IDS = PUBLIC_ROUTE_IDS  # backward compatibility

PILOT_PATHS = {
    "/reference/evidence-posture/",
    "/reference/artifact-subject-separation/",
}

LANGUAGE_PATH = "/language/"

ALLOWED_PUBLIC_HTML = {
    "index.html",
    "language/index.html",
    "reference/evidence-posture/index.html",
    "reference/artifact-subject-separation/index.html",
}

ALLOWED_INTERNAL_PROTOTYPE_HTML = {
    "_internal_prototypes/evidence-posture-workbench/index.html",
}

ALLOWED_NON_PUBLIC_HTML = ALLOWED_PUBLIC_HTML | ALLOWED_INTERNAL_PROTOTYPE_HTML

ALLOWED_PUBLIC_ROOT_FILES = ALLOWED_PUBLIC_HTML | {
    "styles.css",
    "robots.txt",
    "sitemap.xml",
}

PUBLIC_SITEMAP_URL_COUNT = 4

PILOT_SITEMAP_URL_COUNT = PUBLIC_SITEMAP_URL_COUNT  # backward compatibility

PUBLISHER_STATUS_POST_PILOT = "blocked_until_public_reference_validation_and_live_surface_audit"

PUBLISHER_STATUS_POST_LIVE_AUDIT = "blocked_until_public_category_language_layer"

PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE = "blocked_until_public_category_language_validation"

PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE = "blocked_until_evidence_posture_workbench_governance"

PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN = "blocked_until_evidence_posture_workbench_dry_run_harness"

PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION = "blocked_until_workbench_specification_layer"

PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT = "blocked_until_workbench_interface_blueprint_governance"

PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION = "blocked_until_workbench_interface_blueprint_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE = "blocked_until_non_public_static_workbench_prototype_governance"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1 = "blocked_until_non_public_static_workbench_prototype_v1"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION = "blocked_until_non_public_static_workbench_prototype_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT = "blocked_until_non_public_static_workbench_prototype_refinement"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION = "blocked_until_non_public_static_workbench_prototype_refinement_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING = "blocked_until_non_public_static_workbench_public_readiness_boundary_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK = "blocked_until_non_public_static_workbench_public_readiness_boundary_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION = "blocked_until_non_public_static_workbench_public_readiness_boundary_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE = "blocked_until_non_public_static_workbench_public_readiness_boundary_validation"

PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_VALIDATION = "blocked_until_non_public_static_workbench_public_readiness_boundary_validation"

PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE = "blocked_until_public_route_eligibility_governance"

PUBLISHER_STATUSES_ALLOWED = (
    "blocked_until_first_reference_candidate_pack",
    "blocked_until_internal_draft_blueprint",
    "blocked_until_internal_draft_blueprint_or_candidate_evaluation",
    "blocked_until_first_internal_draft_blueprint_pack",
    "blocked_until_first_internal_draft_pack",
    "blocked_until_internal_draft_review_and_refinement",
    "blocked_until_public_route_readiness_gate",
    "blocked_until_first_controlled_public_reference_pilot",
    PUBLISHER_STATUS_POST_PILOT,
    PUBLISHER_STATUS_POST_LIVE_AUDIT,
    PUBLISHER_STATUS_POST_CATEGORY_LANGUAGE,
    PUBLISHER_STATUS_POST_WORKBENCH_GOVERNANCE,
    PUBLISHER_STATUS_POST_WORKBENCH_DRY_RUN,
    PUBLISHER_STATUS_POST_WORKBENCH_SPECIFICATION,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT,
    PUBLISHER_STATUS_POST_WORKBENCH_INTERFACE_BLUEPRINT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_GOVERNANCE,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_V1,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_PROTOTYPE_REFINEMENT_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_HARDENING,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_VISUAL_SYSTEM_BASELINE_LOCK_VALIDATION,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
)


def validate_public_route_registry(routes: list, error) -> bool:
    ids = sorted(r.get("route_id") for r in routes)
    if ids != sorted(PUBLIC_ROUTE_IDS):
        error(f"route-registry: expected {sorted(PUBLIC_ROUTE_IDS)}, got {ids}")
        return False
    return True


validate_pilot_route_registry = validate_public_route_registry


def validate_pilot_routes_present(routes: list, error) -> bool:
    """Verify pilot-era routes still exist (allows additional routes such as /language/)."""
    ids = {r.get("route_id") for r in routes}
    required = {"ROUTE-0001", "ROUTE-0002", "ROUTE-0003"}
    if not required.issubset(ids):
        error(f"route-registry: missing required routes {sorted(required - ids)}")
        return False
    return True


def validate_no_extra_public_html(error) -> bool:
    ok = True
    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_NON_PUBLIC_HTML:
            error(f"public safety: unexpected HTML file {rel}")
            ok = False
    return ok


def _sitemap_locs() -> list[str]:
    tree = ET.parse(ROOT / "sitemap.xml")
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
    if not locs:
        locs = [el.text.strip() for el in root.findall(".//{*}loc") if el.text]
    return locs


def eligible_sitemap_urls(routes: list) -> set[str]:
    urls: set[str] = set()
    for route in routes:
        if route.get("sitemap_included") is True:
            canonical = route.get("canonical_url", "")
            urls.add(canonical)
            urls.add(canonical.rstrip("/") + "/")
    return urls


def validate_public_sitemap(routes: list, error, expected_count: int | None = None) -> bool:
    ok = True
    count = expected_count if expected_count is not None else PUBLIC_SITEMAP_URL_COUNT
    try:
        locs = _sitemap_locs()
    except (ET.ParseError, OSError) as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return False

    if len(locs) != count:
        error(f"sitemap.xml: expected {count} URLs, found {len(locs)}")
        ok = False

    eligible = eligible_sitemap_urls(routes)
    if set(locs) != {u for u in eligible if u}:
        error("sitemap.xml: URLs do not match sitemap-eligible route registry entries")
        ok = False
    return ok


validate_pilot_sitemap = validate_public_sitemap


def validate_public_surface(routes: list, error, sitemap_count: int | None = None) -> bool:
    ok = validate_public_route_registry(routes, error)
    if not validate_public_sitemap(routes, error, sitemap_count):
        ok = False
    if not validate_no_extra_public_html(error):
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


validate_pilot_public_surface = validate_public_surface


def validate_pilot_era_public_surface(routes: list, error) -> bool:
    """Pilot-era routes and sitemap URLs must remain intact; additional routes allowed."""
    ok = validate_pilot_routes_present(routes, error)
    pilot_ids = {"ROUTE-0001", "ROUTE-0002", "ROUTE-0003"}
    pilot_routes = [r for r in routes if r.get("route_id") in pilot_ids]
    try:
        locs = _sitemap_locs()
    except (ET.ParseError, OSError) as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return False
    normalized_locs = {u.rstrip("/") + "/" for u in locs}
    normalized_eligible = {u.rstrip("/") + "/" for u in eligible_sitemap_urls(pilot_routes)}
    if not normalized_eligible.issubset(normalized_locs):
        missing = normalized_eligible - normalized_locs
        error(f"sitemap.xml: missing pilot-era URLs {sorted(missing)}")
        ok = False
    if not validate_no_extra_public_html(error):
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def is_pilot_route(route: dict) -> bool:
    return (
        route.get("pilot_status") == "first_controlled_public_reference_pilot"
        or route.get("status") == "controlled_public_reference_route_created"
        or route.get("path", "").lower() in {p.lower() for p in PILOT_PATHS}
    )


def is_language_route(route: dict) -> bool:
    return (
        route.get("status") == "controlled_public_category_language_route_created"
        or route.get("path", "").lower() in {LANGUAGE_PATH.lower(), "/language"}
    )


def validate_candidate_paths_not_registered_except_pilot(routes: list, candidates: list, error) -> bool:
    ok = True
    for candidate in candidates:
        path = candidate.get("proposed_path", "").lower()
        if not path:
            continue
        for route in routes:
            if route.get("path", "").lower() != path:
                continue
            if is_pilot_route(route) or is_language_route(route):
                continue
            error(f"route-registry: candidate path {path} must not be registered")
            ok = False
    return ok
