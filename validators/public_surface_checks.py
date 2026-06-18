"""Shared public surface checks for Hoax.ai validators."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PILOT_ROUTE_IDS = ["ROUTE-0001", "ROUTE-0002", "ROUTE-0003"]

PILOT_PATHS = {
    "/reference/evidence-posture/",
    "/reference/artifact-subject-separation/",
}

ALLOWED_PUBLIC_HTML = {
    "index.html",
    "reference/evidence-posture/index.html",
    "reference/artifact-subject-separation/index.html",
}

ALLOWED_PUBLIC_ROOT_FILES = ALLOWED_PUBLIC_HTML | {
    "styles.css",
    "robots.txt",
    "sitemap.xml",
}

PILOT_SITEMAP_URL_COUNT = 3

PUBLISHER_STATUS_POST_PILOT = "blocked_until_public_reference_validation_and_live_surface_audit"

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
)


def validate_pilot_route_registry(routes: list, error) -> bool:
    ids = sorted(r.get("route_id") for r in routes)
    if ids != sorted(PILOT_ROUTE_IDS):
        error(f"route-registry: expected {sorted(PILOT_ROUTE_IDS)}, got {ids}")
        return False
    return True


def validate_no_extra_public_html(error) -> bool:
    ok = True
    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_PUBLIC_HTML:
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


def validate_pilot_sitemap(routes: list, error) -> bool:
    ok = True
    try:
        locs = _sitemap_locs()
    except (ET.ParseError, OSError) as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return False

    if len(locs) != PILOT_SITEMAP_URL_COUNT:
        error(f"sitemap.xml: expected {PILOT_SITEMAP_URL_COUNT} URLs, found {len(locs)}")
        ok = False

    eligible = eligible_sitemap_urls(routes)
    if set(locs) != {u for u in eligible if u}:
        error("sitemap.xml: URLs do not match sitemap-eligible route registry entries")
        ok = False
    return ok


def validate_pilot_public_surface(routes: list, error) -> bool:
    ok = validate_pilot_route_registry(routes, error)
    if not validate_pilot_sitemap(routes, error):
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


def validate_candidate_paths_not_registered_except_pilot(routes: list, candidates: list, error) -> bool:
    ok = True
    for candidate in candidates:
        path = candidate.get("proposed_path", "").lower()
        if not path:
            continue
        for route in routes:
            if route.get("path", "").lower() != path:
                continue
            if is_pilot_route(route):
                continue
            error(f"route-registry: candidate path {path} must not be registered")
            ok = False
    return ok
