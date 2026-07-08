#!/usr/bin/env python3
"""Validate Sprint 138 — Public Surface Rebalance Pass (DEC-139).

Production acceptance validator for the rebalanced 63-route public surface.
Not an audit-only chain validator.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_ROUTE_IDS,
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
)

SPRINT = "SPRINT_138_PUBLIC_SURFACE_REBALANCE_PASS.md"
DECISION = "DEC-139"
README = "README.md"
CHANGELOG = "CHANGELOG.md"
ABOUT_PAGE = "about-this-reference/index.html"
ARCHIVE_MANIFEST = "docs/archive/public-surface-pre-rebalance/ARCHIVE_MANIFEST.md"

REMOVED_PREFIXES = (
    "/acquisition-readiness",
    "/external-review",
    "/reviewer-packet",
    "/executive-overview",
    "/strategic-review",
    "/system-map",
    "/entry-points",
    "/narrative",
)

STALE_README_PATTERNS = [
    r"will be developed",
    r"will happen only after",
    r"Sprint 137 completed",
    r"104-route",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def main() -> int:
    ok = True

    if not (ROOT / SPRINT).exists():
        error(f"missing sprint doc: {SPRINT}")
        ok = False

    dec = (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8")
    if DECISION not in dec or "Public Surface Rebalance and Audit Sprint Freeze" not in dec:
        error(f"{DECISION} not found in DECISION_LOG.md")
        ok = False

    if PUBLIC_SITEMAP_URL_COUNT != 63:
        error(f"expected PUBLIC_SITEMAP_URL_COUNT=63, got {PUBLIC_SITEMAP_URL_COUNT}")
        ok = False

    if len(PUBLIC_ROUTE_IDS) != 63:
        error(f"expected 63 PUBLIC_ROUTE_IDS, got {len(PUBLIC_ROUTE_IDS)}")
        ok = False

    if len(ALLOWED_PUBLIC_HTML) != 63:
        error(f"expected 63 ALLOWED_PUBLIC_HTML entries, got {len(ALLOWED_PUBLIC_HTML)}")
        ok = False

    routes_data = json.loads((ROOT / "data" / "route-registry.json").read_text(encoding="utf-8"))["routes"]

    def surf_err(msg: str) -> None:
        nonlocal ok
        error(msg)
        ok = False

    if not validate_public_surface(routes_data, surf_err, PUBLIC_SITEMAP_URL_COUNT):
        ok = False

    routes = routes_data
    if len(routes) != 63:
        error(f"route registry count {len(routes)} != 63")
        ok = False

    paths = {r["path"] for r in routes}
    if "/about-this-reference/" not in paths:
        error("missing /about-this-reference/ in route registry")
        ok = False

    for prefix in REMOVED_PREFIXES:
        if any(p.startswith(prefix + "/") or p == prefix + "/" for p in paths):
            error(f"removed prefix still in registry: {prefix}")
            ok = False

    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sitemap_urls = [
        u.find(f"{ns}loc").text
        for u in ET.parse(ROOT / "sitemap.xml").getroot().findall(f"{ns}url")
    ]
    if len(sitemap_urls) != 63:
        error(f"sitemap URL count {len(sitemap_urls)} != 63")
        ok = False

    for url in sitemap_urls:
        for prefix in REMOVED_PREFIXES:
            if f"https://hoax.ai{prefix}/" in url or url == f"https://hoax.ai{prefix}/":
                error(f"removed route still in sitemap: {url}")
                ok = False

    if not (ROOT / ABOUT_PAGE).exists():
        error(f"missing {ABOUT_PAGE}")
        ok = False
    else:
        about = (ROOT / ABOUT_PAGE).read_text(encoding="utf-8")
        if "acquisition-readiness" in about.lower() and "not an acquisition" not in about.lower():
            pass  # boundary language allowed
        if re.search(r"acquisition readiness hub", about, re.I):
            error("about page reads like acquisition readiness hub")
            ok = False

    if not (ROOT / ARCHIVE_MANIFEST).exists():
        error(f"missing {ARCHIVE_MANIFEST}")
        ok = False

    readme = (ROOT / README).read_text(encoding="utf-8")
    for pat in STALE_README_PATTERNS:
        if re.search(pat, readme, re.I):
            error(f"README still matches stale pattern: {pat}")
            ok = False
    if "CHANGELOG.md" not in readme:
        error("README must link to CHANGELOG.md")
        ok = False
    if "63" not in readme:
        error("README must mention current 63-route count")
        ok = False

    if not (ROOT / CHANGELOG).exists():
        error(f"missing {CHANGELOG}")
        ok = False
    elif "Sprint 138" not in (ROOT / CHANGELOG).read_text(encoding="utf-8"):
        error("CHANGELOG must document Sprint 138")
        ok = False

    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    if "strategic-surface-map" in homepage:
        error("homepage still contains strategic-surface-map section")
        ok = False
    if "acquisition-readiness" in homepage:
        error("homepage still links to acquisition-readiness")
        ok = False

    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
