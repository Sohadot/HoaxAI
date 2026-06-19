#!/usr/bin/env python3
"""Validate Sprint 54 — Public Reference Batch 1 Depth, SEO, and Inevitability Hardening."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
)

BATCH1_PAGES = {
    "reference/source-confidence/index.html": {
        "h1": "Source Confidence",
        "canonical": "https://hoax.ai/reference/source-confidence/",
        "path": "/reference/source-confidence/",
        "min_words": 1100,
        "specific_phrases": [
            "not source certification",
            "not truth judgment",
            "does not perform the verdict",
        ],
        "artifact_sep": True,
        "batch_links": [
            "/reference/provenance-gap/",
            "/reference/not-assessable/",
            "/reference/output-boundary/",
        ],
        "seo_terms": [
            "evidence posture",
            "source confidence",
            "source chain",
            "artifact-subject separation",
            "public reference framework",
        ],
    },
    "reference/provenance-gap/index.html": {
        "h1": "Provenance Gap",
        "canonical": "https://hoax.ai/reference/provenance-gap/",
        "path": "/reference/provenance-gap/",
        "min_words": 1100,
        "specific_phrases": [
            "does not prove manipulation",
            "does not prove deception",
            "chain of context",
        ],
        "artifact_sep": True,
        "batch_links": [
            "/reference/source-confidence/",
            "/reference/not-assessable/",
            "/reference/output-boundary/",
        ],
        "seo_terms": [
            "evidence posture",
            "provenance gap",
            "source chain",
            "not assessable",
            "synthetic media",
        ],
    },
    "reference/not-assessable/index.html": {
        "h1": "Not Assessable",
        "canonical": "https://hoax.ai/reference/not-assessable/",
        "path": "/reference/not-assessable/",
        "min_words": 1100,
        "specific_phrases": [
            "neither true nor false",
            "not mean the artifact is false",
            "not mean the artifact is true",
            "not hidden judgment",
        ],
        "artifact_sep": True,
        "batch_links": [
            "/reference/output-boundary/",
            "/reference/provenance-gap/",
            "/reference/source-confidence/",
        ],
        "seo_terms": [
            "evidence posture",
            "not assessable",
            "responsible classification",
            "evidence limitation",
            "artifact-subject separation",
        ],
    },
    "reference/output-boundary/index.html": {
        "h1": "Output Boundary",
        "canonical": "https://hoax.ai/reference/output-boundary/",
        "path": "/reference/output-boundary/",
        "min_words": 1100,
        "specific_phrases": [
            "prevents verdict",
            "subject accusation",
            "unsupported certainty",
            "output boundary",
        ],
        "artifact_sep": True,
        "batch_links": [
            "/reference/not-assessable/",
            "/reference/source-confidence/",
            "/reference/provenance-gap/",
        ],
        "seo_terms": [
            "evidence posture",
            "output boundary",
            "artifact-subject separation",
            "public reference framework",
            "responsible classification",
        ],
    },
}

REQUIRED_SECTIONS = [
    "Category Thesis",
    "Why This Term Is Necessary",
    "What This Concept Prevents",
    "System Role",
    "Practical Reading Frame",
    "Hoax.ai Boundary",
    "Related Reference Pages",
]

S53_SECTIONS = [
    "Definition",
    "Why It Matters",
    "What It Can Describe",
    "What It Cannot Decide",
    "Relationship to Evidence Posture",
    "Relationship to Artifact–Subject Separation",
]

FORBIDDEN_PAGE_TERMS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script[^>]+src=",
    r"deepfake detector",
    r"truth score",
    r"fake score",
    r"submit evidence",
    r"scan now",
    r"try it now",
    r"upload your",
    r"public classifier is available",
    r"public engine is available",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_54_PUBLIC_REFERENCE_BATCH_1_DEPTH_SEO_INEVITABILITY_AUDIT.md",
    "validators/validate_public_reference_batch_1_depth_seo_inevitability.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    return re.sub(r"<[^>]+>", " ", text)


def visible_word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html)))


def validate_pages() -> bool:
    ok = True
    for rel, spec in BATCH1_PAGES.items():
        path = ROOT / rel
        if not path.is_file():
            error(f"missing page {rel}")
            ok = False
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        if text.count("<h1") != 1:
            error(f"{rel}: must have exactly one H1")
            ok = False
        if spec["canonical"] not in text:
            error(f"{rel}: missing canonical URL")
            ok = False
        if "<title>" not in text:
            error(f"{rel}: missing title")
            ok = False
        if 'name="description"' not in text:
            error(f"{rel}: missing meta description")
            ok = False
        for section in REQUIRED_SECTIONS + S53_SECTIONS:
            if section not in text:
                error(f"{rel}: missing section {section}")
                ok = False
        for phrase in spec["specific_phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing required phrase '{phrase}'")
                ok = False
        for term in spec["seo_terms"]:
            if term.lower() not in lower:
                error(f"{rel}: missing SEO/concept term '{term}'")
                ok = False
        if "/reference/evidence-posture/" not in text:
            error(f"{rel}: must link to Evidence Posture")
            ok = False
        if spec["artifact_sep"] and "/reference/artifact-subject-separation/" not in text:
            error(f"{rel}: must link to Artifact–Subject Separation")
            ok = False
        linked = sum(1 for p in spec["batch_links"] if p in text)
        if linked < 2:
            error(f"{rel}: must link to at least two other Batch 1 pages")
            ok = False
        wc = visible_word_count(text)
        if wc < spec["min_words"]:
            error(f"{rel}: insufficient body substance ({wc} words, need {spec['min_words']})")
            ok = False
        if "classify the evidence artifact" not in lower and "evidence posture" not in lower:
            error(f"{rel}: must preserve evidence posture framing")
            ok = False
        for pat in FORBIDDEN_PAGE_TERMS:
            if re.search(pat, text, re.I):
                error(f"{rel}: forbidden pattern {pat}")
                ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must remain {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    pat = re.compile(
        r"internal_prototypes|evidence-posture-workbench|/workbench/|/tool/|/classifier/|/detector/|/upload/|/score/",
        re.I,
    )
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        if pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel}: must not link to prototype or blocked routes")
            ok = False
    if not all((ROOT / x).is_file() for x in LOCKED_FILES):
        error("prototype files missing")
        ok = False
    if subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip():
        error("prototype files modified")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-072" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-072 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_54_PUBLIC_REFERENCE_BATCH_1_DEPTH_SEO_INEVITABILITY_AUDIT.md").is_file():
        error("Sprint 54 audit missing")
        ok = False
    if "validate_public_reference_batch_1_depth_seo_inevitability.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 54 validator")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    return ok


def validate_cache() -> bool:
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines() + subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error(f"python cache tracked/staged: {rel}")
            return False
    return True


def main() -> int:
    checks = [validate_pages, validate_surface, validate_governance, validate_cache]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
