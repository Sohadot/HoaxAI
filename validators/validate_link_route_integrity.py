#!/usr/bin/env python3
"""Validate Hoax.ai link and route integrity."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import REGISTERED_CANDIDATE_ROUTE_STATUSES

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

POLICY_TOP_REQUIRED = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "route_rules",
    "sitemap_rules",
    "canonical_rules",
    "internal_link_rules",
    "anchor_rules",
    "deployment_status_rules",
    "prohibited_route_states_in_sitemap",
    "prohibited_public_link_targets",
    "last_reviewed",
}

GRAPH_ROUTE_REQUIRED = {
    "route_id",
    "path",
    "source_file",
    "internal_links_out",
    "internal_links_in",
    "anchor_targets",
    "public_navigation_links",
    "orphan_status",
    "notes",
}

PROHIBITED_SITEMAP_STATES = {"planned", "blocked", "future", "draft", "internal_only"}

PLACEHOLDER_URL_MARKERS = [
    "example.com",
    "placeholder",
    "coming-soon",
    "todo",
    "tbd",
    "lorem",
    "undefined",
]

ROUTE_PATTERN = re.compile(r"^ROUTE-\d{4}$")

MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

GOVERNANCE_MARKDOWN_FILES = [
    "README.md",
    "DECISION_LOG.md",
    "ROADMAP.md",
    "MASTER_EXECUTION_PLAN.md",
    "GOVERNANCE_BOUNDARY.md",
    "LINK_ROUTE_INTEGRITY_POLICY.md",
    "CATEGORY_INTELLIGENCE_FACTORY_PLAN.md",
]

FIRST_PARTY_ASSETS = {
    "styles.css",
    "robots.txt",
    "sitemap.xml",
    "favicon.ico",
}


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


def normalize_route_path(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/") and "." not in Path(path).name:
        path = path + "/"
    return path


def route_status_prohibited_in_sitemap(status: str) -> bool:
    if status in REGISTERED_CANDIDATE_ROUTE_STATUSES:
        return False
    lower = status.lower()
    return any(state in lower for state in PROHIBITED_SITEMAP_STATES)


def extract_element_ids(html: str) -> set[str]:
    ids: set[str] = set()
    for match in re.finditer(r'\bid\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE):
        ids.add(match.group(1))
    return ids


def extract_hrefs(html: str) -> list[str]:
    hrefs: list[str] = []
    for match in re.finditer(r'href\s*=\s*["\']([^"\']*)["\']', html, re.IGNORECASE):
        hrefs.append(match.group(1).strip())
    return hrefs


def validate_policy_data() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "link-route-integrity-policy.json")
    missing = POLICY_TOP_REQUIRED - set(data.keys())
    if missing:
        error(f"link-route-integrity-policy: missing fields {sorted(missing)}")
        ok = False
    if data.get("status") != "governed_internal_route_link_policy":
        error("link-route-integrity-policy: invalid status")
        ok = False
    if data.get("maturity") != "pre_expansion_hardening":
        error("link-route-integrity-policy: maturity must be pre_expansion_hardening")
        ok = False

    prohibited_states = {s.lower() for s in data.get("prohibited_route_states_in_sitemap", [])}
    if not PROHIBITED_SITEMAP_STATES.issubset(prohibited_states):
        error("link-route-integrity-policy: prohibited_route_states_in_sitemap incomplete")
        ok = False

    prohibited_targets = " ".join(data.get("prohibited_public_link_targets", [])).lower()
    for term in ["missing route", "placeholder", "future route", "blocked route", "unregistered route"]:
        if term not in prohibited_targets:
            error(f"link-route-integrity-policy: missing prohibited target '{term}'")
            ok = False

    deployment_rules = " ".join(data.get("deployment_status_rules", [])).lower()
    if "external_deployment_deferred" not in deployment_rules:
        error("link-route-integrity-policy: deployment_status_rules must preserve external_deployment_deferred")
        ok = False
    return ok


def validate_route_registry() -> tuple[bool, dict]:
    ok = True
    data = load_json(ROOT / "data" / "route-registry.json")
    routes = data.get("routes", [])
    if not routes:
        error("route-registry: no routes defined")
        return False, {}

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    by_id: dict[str, dict] = {}
    by_path: dict[str, dict] = {}

    for route in routes:
        rid = route.get("route_id", "")
        path = route.get("path", "")

        if not ROUTE_PATTERN.match(rid):
            error(f"route-registry: invalid route_id '{rid}'")
            ok = False
        if rid in seen_ids:
            error(f"route-registry: duplicate route_id '{rid}'")
            ok = False
        seen_ids.add(rid)
        by_id[rid] = route
        by_path[path] = route

        missing = ROUTE_REQUIRED - set(route.keys())
        if missing:
            error(f"route-registry '{rid}': missing fields {sorted(missing)}")
            ok = False

        if not route.get("canonical_url"):
            error(f"route-registry '{rid}': missing canonical_url")
            ok = False
        if not route.get("deployment_status"):
            error(f"route-registry '{rid}': missing deployment_status")
            ok = False
        if path in seen_paths:
            error(f"route-registry: duplicate path '{path}'")
            ok = False
        seen_paths.add(path)

    if "ROUTE-0001" not in by_id:
        error("route-registry: ROUTE-0001 must exist")
        ok = False
    if "/" not in seen_paths:
        error("route-registry: path / must exist")
        ok = False

    return ok, by_path


def validate_sitemap(by_path: dict[str, dict]) -> bool:
    ok = True
    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.exists():
        error("sitemap.xml: missing")
        return False

    try:
        tree = ElementTree.parse(sitemap_path)
    except ElementTree.ParseError as exc:
        error(f"sitemap.xml: parse error {exc}")
        return False

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [loc.text.strip() for loc in tree.findall(".//sm:loc", ns) if loc.text]

    registry_sitemap_paths = {
        r["path"] for r in by_path.values() if r.get("sitemap_included")
    }

    for url in locs:
        lower_url = url.lower()
        for marker in PLACEHOLDER_URL_MARKERS:
            if marker in lower_url:
                error(f"sitemap.xml: placeholder URL marker '{marker}' in '{url}'")
                ok = False

        spath = path_from_url(url)
        route = by_path.get(spath)
        if route is None:
            error(f"sitemap.xml: URL '{url}' not in route-registry")
            ok = False
            continue

        if not route.get("sitemap_included"):
            error(f"sitemap.xml: path '{spath}' is not sitemap-eligible")
            ok = False

        if route_status_prohibited_in_sitemap(route.get("status", "")):
            error(f"sitemap.xml: route '{route.get('route_id')}' has prohibited status for sitemap")
            ok = False

    for rpath in registry_sitemap_paths:
        if rpath not in {path_from_url(u) for u in locs}:
            error(f"sitemap.xml: sitemap-eligible path '{rpath}' missing from sitemap")
            ok = False

    return ok


def validate_canonical(by_path: dict[str, dict]) -> bool:
    ok = True
    canonicals: list[str] = []
    index_path = ROOT / "index.html"
    if not index_path.exists():
        error("index.html: missing")
        return False

    html = index_path.read_text(encoding="utf-8")
    head_canonical = None
    for match in re.finditer(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    ):
        head_canonical = match.group(1)
    if head_canonical is None:
        for match in re.finditer(
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
            html,
            re.IGNORECASE,
        ):
            head_canonical = match.group(1)

    route = by_path.get("/")
    if route is None:
        return ok

    registry_canonical = route.get("canonical_url", "")
    if not registry_canonical:
        error("canonical: ROUTE-0001 missing canonical_url in registry")
        ok = False
    else:
        canonicals.append(registry_canonical)

    if head_canonical and head_canonical != registry_canonical:
        error(
            f"canonical: index.html canonical '{head_canonical}' "
            f"does not match registry '{registry_canonical}'"
        )
        ok = False

    for marker in PLACEHOLDER_URL_MARKERS:
        if marker in registry_canonical.lower():
            error(f"canonical: placeholder in canonical_url '{registry_canonical}'")
            ok = False

    if len(set(canonicals)) != len(canonicals):
        error("canonical: duplicate canonical_url values")
        ok = False

    return ok


def validate_index_html_links(by_path: dict[str, dict]) -> bool:
    ok = True
    index_path = ROOT / "index.html"
    html = index_path.read_text(encoding="utf-8")
    element_ids = extract_element_ids(html)
    hrefs = extract_hrefs(html)

    for href in hrefs:
        if not href:
            error("index.html: empty href prohibited")
            ok = False
            continue

        lower = href.lower()
        if lower.startswith("javascript:"):
            error(f"index.html: javascript: link prohibited '{href}'")
            ok = False
            continue
        if lower.startswith("mailto:"):
            error(f"index.html: mailto link prohibited '{href}'")
            ok = False
            continue
        if href == "#" or href == "":
            error("index.html: empty hash link prohibited")
            ok = False
            continue

        if href.startswith("#"):
            fragment = href[1:]
            if not fragment or fragment in {"placeholder", "todo", "tbd"}:
                error(f"index.html: placeholder anchor '{href}'")
                ok = False
            elif fragment not in element_ids:
                error(f"index.html: fragment '{href}' targets missing ID")
                ok = False
            continue

        if href.startswith("http://") or href.startswith("https://"):
            spath = path_from_url(href)
            if spath in by_path:
                continue
            if any(marker in lower for marker in PLACEHOLDER_URL_MARKERS):
                error(f"index.html: placeholder external link '{href}'")
                ok = False
            continue

        if href in FIRST_PARTY_ASSETS or (ROOT / href).exists():
            continue

        route_path = normalize_route_path(href)
        if route_path not in by_path:
            error(f"index.html: href '{href}' points to unregistered route")
            ok = False
            continue

        route = by_path[route_path]
        if route_status_prohibited_in_sitemap(route.get("status", "")):
            error(f"index.html: href '{href}' points to blocked or non-public route")
            ok = False

    return ok


def validate_internal_link_graph(by_path: dict[str, dict]) -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-link-graph.json")
    routes = data.get("routes", [])
    if not routes:
        error("internal-link-graph: routes missing")
        return False

    for entry in routes:
        rid = entry.get("route_id", "?")
        missing = GRAPH_ROUTE_REQUIRED - set(entry.keys())
        if missing:
            error(f"internal-link-graph '{rid}': missing fields {sorted(missing)}")
            ok = False

        registry_route = by_path.get(entry.get("path", ""))
        if registry_route is None or registry_route.get("route_id") != rid:
            error(f"internal-link-graph '{rid}': does not map to route-registry")
            ok = False

        source = entry.get("source_file", "")
        if source and not (ROOT / source).exists():
            error(f"internal-link-graph '{rid}': source_file missing '{source}'")
            ok = False

        for link in entry.get("public_navigation_links", []):
            norm = normalize_route_path(link)
            if norm not in by_path:
                error(f"internal-link-graph '{rid}': public navigation to unregistered '{link}'")
                ok = False

        orphan = entry.get("orphan_status", "")
        if len(routes) == 1 and orphan != "allowed_single_route_foundation":
            error("internal-link-graph: single-route foundation requires allowed_single_route_foundation")
            ok = False

    for link in data.get("public_surface_links", []):
        rid = link.get("route_id")
        if rid and rid not in {r.get("route_id") for r in routes}:
            error(f"internal-link-graph: public_surface_links unknown route '{rid}'")
            ok = False

    if data.get("unresolved_links_allowed"):
        error("internal-link-graph: unresolved_links_allowed must be false")
        ok = False

    return ok


def validate_markdown_links() -> bool:
    ok = True
    for rel in GOVERNANCE_MARKDOWN_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_PATTERN.finditer(content):
            target = match.group(1).strip()
            if not target or target.startswith("#"):
                continue
            if target.startswith("http://") or target.startswith("https://"):
                if " " in target or target.endswith(")"):
                    error(f"markdown '{rel}': malformed external URL '{target}'")
                    ok = False
                continue
            if target.startswith("mailto:"):
                continue
            local = target.split("#")[0]
            if not local:
                continue
            if not (ROOT / local).exists():
                error(f"markdown '{rel}': broken local link to '{target}'")
                ok = False
    return ok


def validate_deployment_posture(by_path: dict[str, dict]) -> bool:
    ok = True
    for route in by_path.values():
        rid = route.get("route_id", "?")
        status = route.get("deployment_status", "")
        if status == "deployment_ready":
            error(f"route-registry '{rid}': deployment_ready not allowed before readiness gate")
            ok = False
    return ok


def validate_source_registry_entries() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "source-registry.json")
    locations = {s.get("location") for s in registry.get("sources", [])}
    for required in [
        "LINK_ROUTE_INTEGRITY_POLICY.md",
        "data/link-route-integrity-policy.json",
        "data/internal-link-graph.json",
        "validators/validate_link_route_integrity.py",
    ]:
        if required not in locations:
            error(f"source-registry: missing route/link source '{required}'")
            ok = False
    return ok


def main() -> int:
    route_ok, by_path = validate_route_registry()

    checks = [
        ("Link route integrity policy", validate_policy_data),
        ("Sitemap integrity", lambda: validate_sitemap(by_path)),
        ("Canonical integrity", lambda: validate_canonical(by_path)),
        ("Index HTML links", lambda: validate_index_html_links(by_path)),
        ("Internal link graph", lambda: validate_internal_link_graph(by_path)),
        ("Markdown local links", validate_markdown_links),
        ("Deployment posture", lambda: validate_deployment_posture(by_path)),
        ("Route link source registry", validate_source_registry_entries),
    ]

    all_ok = route_ok
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
