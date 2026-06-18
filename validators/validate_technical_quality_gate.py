#!/usr/bin/env python3
"""Validate Hoax.ai technical quality gate enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GATE_TOP_REQUIRED = {
    "gate_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "html_requirements",
    "metadata_requirements",
    "robots_sitemap_requirements",
    "accessibility_requirements",
    "performance_dependency_requirements",
    "static_security_requirements",
    "public_asset_requirements",
    "prohibited_security_claims",
    "last_reviewed",
}

PUBLIC_FILE_REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "public_files",
    "last_reviewed",
}

HTML_METADATA_REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "route_id",
    "source_file",
    "required_metadata",
    "optional_metadata",
    "prohibited_metadata_claims",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "TECHNICAL_QUALITY_GATE.md",
    "data/technical-quality-gate.json",
    "data/public-file-registry.json",
    "data/html-metadata-registry.json",
    "validators/validate_technical_quality_gate.py",
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

ACTIVE_TOOL_PATTERNS = [
    "upload your",
    "upload a file",
    "scan now",
    "try our tool",
    "live classifier",
    "public classifier",
    "truth score",
    "fake score",
    "deepfake detected",
    "detect fakes",
    "now available",
    "deployment complete",
    "launch your",
    "start scanning",
]

SUPERIORITY_PATTERNS = [
    "first in the world",
    "world's first",
    "worlds first",
    "industry-leading",
    "best in class",
    "only system that",
    "unmatched accuracy",
    "100% accurate",
]

PLACEHOLDER_PATTERNS = [
    "todo",
    "fixme",
    "lorem ipsum",
    "placeholder text",
    "xxx",
    "tbd:",
]

INDEX_SECURITY_PATTERNS = [
    ("<form", "form element"),
    ("<input", "input element"),
    ('type="file"', "file upload input"),
    ("<iframe", "iframe embed"),
    ("<script", "script element"),
    ("onclick=", "inline onclick handler"),
    ("onload=", "inline onload handler"),
    ("onerror=", "inline onerror handler"),
    ("fetch(", "fetch API call"),
    ("xmlhttprequest", "XHR API call"),
    ("localstorage", "localStorage usage"),
    ("sessionstorage", "sessionStorage usage"),
    ("document.cookie", "cookie setting"),
    ("google-analytics", "analytics reference"),
    ("googletagmanager", "analytics reference"),
    ("gtag(", "analytics reference"),
    ("plausible.io", "analytics reference"),
    ("stripe.com", "payment widget"),
    ("paypal.com", "payment widget"),
]

CSS_PROHIBITED = [
    "@import",
    "fonts.googleapis",
    "fonts.gstatic",
    "url(http",
    "url(https",
]

JSON_LD_FORBIDDEN_TYPES = [
    "SoftwareApplication",
    "Product",
    "Service",
]


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


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def validate_gate_data() -> bool:
    ok = True
    path = ROOT / "data" / "technical-quality-gate.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"technical-quality-gate.json parse failed: {exc}")
        return False

    missing = GATE_TOP_REQUIRED - set(data.keys())
    if missing:
        error(f"technical-quality-gate.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_technical_quality_gate":
        error("technical-quality-gate.json: invalid status")
        ok = False
    if data.get("maturity") != "pre_expansion_static_quality_gate":
        error("technical-quality-gate.json: invalid maturity")
        ok = False

    required_claims = {
        "perfectly secure",
        "fully secure",
        "no security gaps",
        "unhackable",
        "guaranteed safe",
    }
    prohibited = {c.lower() for c in data.get("prohibited_security_claims", [])}
    if not required_claims.issubset(prohibited):
        error("technical-quality-gate.json: prohibited_security_claims incomplete")
        ok = False

    static_req = " ".join(data.get("static_security_requirements", [])).lower()
    for term in ["form", "input", "upload", "script", "iframe", "fetch", "localstorage",
                 "payment", "login", "api"]:
        if term not in static_req:
            error(f"technical-quality-gate.json: static_security_requirements missing {term}")
            ok = False

    perf = " ".join(data.get("performance_dependency_requirements", [])).lower()
    if "static" not in perf or "external" not in perf:
        error("technical-quality-gate.json: performance_dependency_requirements incomplete")
        ok = False

    return ok


def validate_public_file_registry_data() -> bool:
    ok = True
    path = ROOT / "data" / "public-file-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"public-file-registry.json parse failed: {exc}")
        return False

    missing = PUBLIC_FILE_REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"public-file-registry.json missing fields: {sorted(missing)}")
        ok = False

    files = data.get("public_files", [])
    paths: list[str] = []
    for entry in files:
        for field in ["file_id", "path", "file_type", "public_role", "required",
                      "validation_scope", "allowed_dependencies", "prohibited_content"]:
            if field not in entry:
                error(f"public-file-registry: {entry.get('file_id', '?')} missing {field}")
                ok = False
        p = entry.get("path", "")
        if p in paths:
            error(f"public-file-registry: duplicate path {p}")
            ok = False
        paths.append(p)

    index_entry = next((f for f in files if f.get("path") == "index.html"), None)
    if not index_entry or index_entry.get("route_id_if_applicable") != "ROUTE-0001":
        error("public-file-registry: index.html must map to ROUTE-0001")
        ok = False

    required_paths = {
        "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "styles.css",
        "robots.txt",
        "sitemap.xml",
    }
    if set(paths) != required_paths:
        error(f"public-file-registry: expected paths {sorted(required_paths)}")
        ok = False

    pilot_paths = {
        "reference/evidence-posture/index.html": "ROUTE-0002",
        "reference/artifact-subject-separation/index.html": "ROUTE-0003",
    }
    for path, route_id in pilot_paths.items():
        entry = next((f for f in files if f.get("path") == path), None)
        if not entry or entry.get("route_id_if_applicable") != route_id:
            error(f"public-file-registry: {path} must map to {route_id}")
            ok = False

    for entry in files:
        if entry.get("required") and not (ROOT / entry["path"]).exists():
            error(f"public-file-registry: required file missing: {entry['path']}")
            ok = False

    return ok


def validate_html_metadata_registry_data() -> bool:
    ok = True
    path = ROOT / "data" / "html-metadata-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"html-metadata-registry.json parse failed: {exc}")
        return False

    missing = HTML_METADATA_REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"html-metadata-registry.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("route_id") != "ROUTE-0001":
        error("html-metadata-registry: route_id must be ROUTE-0001")
        ok = False
    if data.get("source_file") != "index.html":
        error("html-metadata-registry: source_file must be index.html")
        ok = False

    required_names = {"charset", "viewport", "title", "meta_description", "canonical"}
    found = {m.get("name") for m in data.get("required_metadata", [])}
    if required_names - found:
        error(f"html-metadata-registry: missing required metadata {sorted(required_names - found)}")
        ok = False

    for section in ["required_metadata", "optional_metadata"]:
        for entry in data.get(section, []):
            for field in ["metadata_id", "name", "required", "expected_presence",
                          "allowed_claim_scope", "prohibited_claim_scope", "notes"]:
                if field not in entry:
                    error(f"html-metadata-registry: {entry.get('metadata_id', '?')} missing {field}")
                    ok = False

    reference_pages = data.get("reference_pages", [])
    if len(reference_pages) != 2:
        error("html-metadata-registry: expected two reference_pages entries")
        ok = False
    for page in reference_pages:
        if page.get("route_id") not in ("ROUTE-0002", "ROUTE-0003"):
            error("html-metadata-registry: invalid reference page route_id")
            ok = False
        if not page.get("source_file", "").startswith("reference/"):
            error("html-metadata-registry: reference page source_file invalid")
            ok = False

    return ok


def get_route_registry() -> dict:
    return load_json(ROOT / "data" / "route-registry.json")


def eligible_sitemap_urls(routes: list[dict]) -> set[str]:
    urls: set[str] = set()
    for route in routes:
        if route.get("sitemap_included") is True:
            canonical = route.get("canonical_url", "").rstrip("/") + "/"
            urls.add(canonical.rstrip("/") + "/")
            urls.add(route.get("canonical_url", ""))
    return urls


def validate_html_structure(index_html: str) -> bool:
    ok = True
    lower = index_html.lower()

    if not re.search(r'<html[^>]*\blang\s*=\s*["\'][^"\']+["\']', index_html, re.IGNORECASE):
        error("index.html: html lang attribute missing")
        ok = False

    if not re.search(r'<meta[^>]+charset\s*=\s*["\']?utf-8', lower):
        error("index.html: charset meta missing")
        ok = False

    if 'name="viewport"' not in lower and "name='viewport'" not in lower:
        error("index.html: viewport meta missing")
        ok = False

    title_match = re.search(r"<title>([^<]+)</title>", index_html, re.IGNORECASE)
    if not title_match or not title_match.group(1).strip():
        error("index.html: title missing or empty")
        ok = False

    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    )
    if not desc_match or not desc_match.group(1).strip():
        error("index.html: meta description missing or empty")
        ok = False

    canonicals = re.findall(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    )
    if len(canonicals) != 1:
        error(f"index.html: expected exactly one canonical link, found {len(canonicals)}")
        ok = False

    h1_count = len(re.findall(r"<h1\b", index_html, re.IGNORECASE))
    if h1_count != 1:
        error(f"index.html: expected exactly one H1, found {h1_count}")
        ok = False

    for href in re.findall(r'href\s*=\s*["\']([^"\']*)["\']', index_html, re.IGNORECASE):
        if href.strip() == "":
            error("index.html: empty href found")
            ok = False
        if href.strip().lower().startswith("javascript:"):
            error("index.html: javascript: href found")
            ok = False
        if href.startswith("#") and href != "#":
            frag = href[1:]
            if not re.search(rf'\bid\s*=\s*["\']{re.escape(frag)}["\']', index_html, re.IGNORECASE):
                error(f"index.html: fragment link #{frag} has no matching id")
                ok = False

    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in lower and pattern not in ("xxx",):
            if pattern == "todo" and "methodology" in lower:
                continue
            if contains_unnegated(lower, pattern):
                error(f"index.html: unresolved placeholder pattern '{pattern}'")
                ok = False

    for pattern in SUPERIORITY_PATTERNS:
        if contains_unnegated(lower, pattern):
            error(f"index.html: unsupported superiority claim '{pattern}'")
            ok = False

    for pattern in ACTIVE_TOOL_PATTERNS:
        if contains_unnegated(lower, pattern):
            error(f"index.html: active tool language '{pattern}' without negation")
            ok = False

    scanner_terms = ["scanner", "detector", "verdict machine", "scoring engine"]
    for term in scanner_terms:
        if contains_unnegated(lower, term):
            error(f"index.html: scanner/detector/scoring language '{term}' without negation")
            ok = False

    for pattern, label in INDEX_SECURITY_PATTERNS:
        if pattern in lower:
            error(f"index.html: static security violation — {label}")
            ok = False

    for link in re.findall(r"https?://[^\s\"'<>]+", index_html, re.IGNORECASE):
        if "hoax.ai" in link:
            continue
        if link.endswith(".css") or "stylesheet" in link.lower():
            error(f"index.html: external stylesheet reference {link}")
            ok = False

    stylesheet_links = re.findall(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    )
    for href in stylesheet_links:
        if href.startswith("http://") or href.startswith("https://"):
            error(f"index.html: external stylesheet {href}")
            ok = False
        local = ROOT / href
        if not local.exists():
            error(f"index.html: missing local stylesheet {href}")
            ok = False

    return ok


def validate_metadata(index_html: str, routes: list[dict]) -> bool:
    ok = True
    lower = index_html.lower()

    route = next((r for r in routes if r.get("route_id") == "ROUTE-0001"), None)
    if not route:
        error("route registry: ROUTE-0001 missing")
        return False

    canonical_match = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    )
    expected = route.get("canonical_url", "")
    if not canonical_match or canonical_match.group(1) != expected:
        error(f"index.html: canonical must be {expected}")
        ok = False

    meta_regions = []
    for prop in ["og:title", "og:description", "og:url", "twitter:title", "twitter:description"]:
        m = re.search(
            rf'<meta\s+(?:property|name)=["\']{re.escape(prop)}["\']\s+content=["\']([^"\']+)["\']',
            index_html,
            re.IGNORECASE,
        )
        if m:
            meta_regions.append(m.group(1))

    for region in meta_regions:
        region_lower = region.lower()
        for pattern in ACTIVE_TOOL_PATTERNS:
            if contains_unnegated(region_lower, pattern):
                error(f"metadata: OG/Twitter overclaim '{pattern}' in '{region[:60]}'")
                ok = False

    json_ld_blocks = re.findall(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        index_html,
        re.IGNORECASE | re.DOTALL,
    )
    for block in json_ld_blocks:
        try:
            parsed = json.loads(block.strip())
        except json.JSONDecodeError:
            error("index.html: JSON-LD block does not parse")
            ok = False
            continue
        block_str = json.dumps(parsed)
        for forbidden in JSON_LD_FORBIDDEN_TYPES:
            if forbidden in block_str:
                error(f"index.html: JSON-LD uses unapproved schema type {forbidden}")
                ok = False

    desc = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
        index_html,
        re.IGNORECASE,
    )
    if desc:
        desc_lower = desc.group(1).lower()
        if contains_unnegated(desc_lower, "upload") or contains_unnegated(desc_lower, "scan now"):
            error("index.html: meta description implies active tool")
            ok = False

    return ok


def validate_accessibility(index_html: str) -> bool:
    ok = True

    headings = [(int(m.group(1)), m.start()) for m in re.finditer(r"<h([1-6])\b", index_html, re.IGNORECASE)]
    headings.sort(key=lambda x: x[1])
    prev_level = 0
    for level, _ in headings:
        if prev_level and level > prev_level + 1:
            error(f"index.html: heading order skip from h{prev_level} to h{level}")
            ok = False
        prev_level = level

    for anchor in re.finditer(r"<a\b[^>]*>(.*?)</a>", index_html, re.IGNORECASE | re.DOTALL):
        tag = anchor.group(0)
        text = strip_tags(anchor.group(1)).strip()
        aria = re.search(r'aria-label=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not text and not (aria and aria.group(1).strip()):
            error("index.html: link without readable text or aria-label")
            ok = False

    for img in re.finditer(r"<img\b[^>]*>", index_html, re.IGNORECASE):
        tag = img.group(0)
        if re.search(r'\brole=["\']presentation["\']', tag, re.IGNORECASE):
            continue
        if re.search(r'\baria-hidden=["\']true["\']', tag, re.IGNORECASE):
            continue
        if not re.search(r'\balt\s*=\s*["\'][^"\']*["\']', tag, re.IGNORECASE):
            error("index.html: image missing alt attribute")
            ok = False

    return ok


def validate_css() -> bool:
    ok = True
    css_path = ROOT / "styles.css"
    if not css_path.exists():
        error("styles.css missing")
        return False

    content = css_path.read_text(encoding="utf-8")
    lower = content.lower()
    for pattern in CSS_PROHIBITED:
        if pattern.lower() in lower:
            error(f"styles.css: prohibited dependency pattern '{pattern}'")
            ok = False

    for term in ["upload", "scanner", "detector", "payment", "tracking", "login"]:
        if re.search(rf"\.{term}\b", lower):
            error(f"styles.css: prohibited class pattern '.{term}'")
            ok = False

    return ok


def validate_robots_sitemap(routes: list[dict]) -> bool:
    ok = True
    robots_path = ROOT / "robots.txt"
    sitemap_path = ROOT / "sitemap.xml"

    if not robots_path.exists():
        error("robots.txt missing")
        ok = False
    if not sitemap_path.exists():
        error("sitemap.xml missing")
        ok = False
    if not ok:
        return False

    robots = robots_path.read_text(encoding="utf-8")
    eligible = eligible_sitemap_urls(routes)

    blocked_statuses = {"planned", "blocked", "future", "draft", "internal_only", "placeholder"}
    for route in routes:
        if route.get("status", "").lower() in blocked_statuses:
            path = route.get("path", "")
            if path and path in robots:
                error(f"robots.txt: exposes blocked/placeholder route {path}")
                ok = False

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

    sitemap_set = set(locs)
    for url in locs:
        matched = any(
            url.rstrip("/") + "/" == r.get("canonical_url", "").rstrip("/") + "/"
            or url == r.get("canonical_url", "")
            for r in routes
            if r.get("sitemap_included") is True
        )
        if not matched:
            error(f"sitemap.xml: URL not in eligible route registry: {url}")
            ok = False

    for route in routes:
        if route.get("sitemap_included") is not True:
            canonical = route.get("canonical_url", "")
            if canonical in sitemap_set:
                error(f"sitemap.xml: includes route not eligible for sitemap: {canonical}")
                ok = False
        status = route.get("status", "").lower()
        if status in blocked_statuses and route.get("canonical_url") in sitemap_set:
            error(f"sitemap.xml: includes blocked route {route.get('route_id')}")
            ok = False

    if "Sitemap:" not in robots:
        error("robots.txt: missing Sitemap directive")
        ok = False

    return ok


def validate_source_registry() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing technical quality source {loc}")
            ok = False
    return ok


def main() -> int:
    ok = True

    if not validate_gate_data():
        ok = False
    if not validate_public_file_registry_data():
        ok = False
    if not validate_html_metadata_registry_data():
        ok = False
    if not validate_source_registry():
        ok = False

    index_path = ROOT / "index.html"
    if not index_path.exists():
        error("index.html missing")
        ok = False
    else:
        index_html = index_path.read_text(encoding="utf-8")
        routes = get_route_registry().get("routes", [])
        if not validate_html_structure(index_html):
            ok = False
        if not validate_metadata(index_html, routes):
            ok = False
        if not validate_accessibility(index_html):
            ok = False

    if not validate_css():
        ok = False

    routes = get_route_registry().get("routes", [])
    if not validate_robots_sitemap(routes):
        ok = False

    if ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
