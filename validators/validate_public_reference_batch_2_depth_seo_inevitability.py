#!/usr/bin/env python3
"""Validate Sprint 56 — Public Reference Batch 2 Depth, SEO, and Inevitability Hardening."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
)

BATCH2_PAGES = {
    "reference/synthetic-fragility/index.html": {
        "h1": "Synthetic Fragility",
        "canonical": "https://hoax.ai/reference/synthetic-fragility/",
        "path": "/reference/synthetic-fragility/",
        "min_words": 1100,
        "specific_phrases": [
            "not automatic falsehood",
            "does not prove deception",
            "interpretive fragility",
            "does not perform the verdict",
        ],
        "batch1_links": [
            "/reference/provenance-gap/",
            "/reference/source-confidence/",
            "/reference/not-assessable/",
            "/reference/output-boundary/",
        ],
        "batch2_links": [
            "/reference/context-collapse/",
            "/reference/evidence-chain/",
        ],
        "seo_terms": [
            "evidence posture",
            "synthetic fragility",
            "provenance gap",
            "source confidence",
            "not assessable",
            "public reference framework",
        ],
    },
    "reference/evidence-chain/index.html": {
        "h1": "Evidence Chain",
        "canonical": "https://hoax.ai/reference/evidence-chain/",
        "path": "/reference/evidence-chain/",
        "min_words": 1100,
        "specific_phrases": [
            "not truth certification",
            "not a proof of truth",
            "does not assign guilt",
            "does not perform the verdict",
        ],
        "batch1_links": [
            "/reference/provenance-gap/",
            "/reference/source-confidence/",
            "/reference/output-boundary/",
        ],
        "batch2_links": [
            "/reference/claim-source-traceability/",
            "/reference/synthetic-fragility/",
        ],
        "seo_terms": [
            "evidence posture",
            "evidence chain",
            "source confidence",
            "provenance gap",
            "traceability",
        ],
    },
    "reference/context-collapse/index.html": {
        "h1": "Context Collapse",
        "canonical": "https://hoax.ai/reference/context-collapse/",
        "path": "/reference/context-collapse/",
        "min_words": 1100,
        "specific_phrases": [
            "does not prove manipulation",
            "does not prove deception",
            "does not assign motive",
            "does not prove misconduct",
        ],
        "batch1_links": [
            "/reference/provenance-gap/",
            "/reference/not-assessable/",
            "/reference/output-boundary/",
        ],
        "batch2_links": [
            "/reference/synthetic-fragility/",
            "/reference/evidence-chain/",
        ],
        "seo_terms": [
            "evidence posture",
            "context collapse",
            "provenance gap",
            "not assessable",
            "synthetic media",
        ],
    },
    "reference/claim-source-traceability/index.html": {
        "h1": "Claim–Source Traceability",
        "canonical": "https://hoax.ai/reference/claim-source-traceability/",
        "path": "/reference/claim-source-traceability/",
        "min_words": 1100,
        "specific_phrases": [
            "does not prove a claim true",
            "does not certify a source",
            "unsupported certainty",
            "does not perform the verdict",
        ],
        "batch1_links": [
            "/reference/source-confidence/",
            "/reference/output-boundary/",
            "/reference/provenance-gap/",
        ],
        "batch2_links": [
            "/reference/evidence-chain/",
            "/reference/context-collapse/",
        ],
        "seo_terms": [
            "evidence posture",
            "traceability",
            "source confidence",
            "output boundary",
            "public reference framework",
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

S55_SECTIONS = [
    "Definition",
    "Why It Matters",
    "What It Can Describe",
    "What It Cannot Decide",
    "Relationship to Evidence Posture",
    "Relationship to Artifact–Subject Separation",
]

INSTITUTIONAL_TERMS = [
    "platform",
    "researcher",
    "analyst",
    "journalist",
    "compliance",
    "trust",
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
    r"detector interface",
    r"scanner interface",
    r"classifier interface",
    r"scoring interface",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_56_PUBLIC_REFERENCE_BATCH_2_DEPTH_SEO_INEVITABILITY_AUDIT.md",
    "validators/validate_public_reference_batch_2_depth_seo_inevitability.py",
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
    for rel, spec in BATCH2_PAGES.items():
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
        for section in REQUIRED_SECTIONS + S55_SECTIONS:
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
        inst = sum(1 for t in INSTITUTIONAL_TERMS if t in lower)
        if inst < 3:
            error(f"{rel}: insufficient institutional relevance language ({inst} terms)")
            ok = False
        if "/reference/evidence-posture/" not in text:
            error(f"{rel}: must link to Evidence Posture")
            ok = False
        if "/reference/artifact-subject-separation/" not in text:
            error(f"{rel}: must link to Artifact–Subject Separation")
            ok = False
        b1 = sum(1 for p in spec["batch1_links"] if p in text)
        if b1 < 2:
            error(f"{rel}: must link to at least two Batch 1 pages")
            ok = False
        b2 = sum(1 for p in spec["batch2_links"] if p in text)
        if b2 < 1:
            error(f"{rel}: must link to at least one other Batch 2 page")
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
    batch2 = [r for r in routes if r.get("production_batch") == "public_reference_production_batch_2"]
    if len(batch2) != 4:
        error("route registry must retain exactly four Batch 2 routes")
        ok = False
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must remain {PUBLIC_SITEMAP_URL_COUNT} routes — no new routes")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    for spec in BATCH2_PAGES.values():
        if f"https://hoax.ai{spec['path']}" not in locs:
            error(f"sitemap missing Batch 2 URL {spec['path']}")
            ok = False
    pat = re.compile(
        r"internal_prototypes|evidence-posture-workbench|/workbench/|/tool/|/classifier/|/detector/|/upload/|/score/",
        re.I,
    )
    for rel in sorted(BATCH2_PAGES.keys()):
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
    if "DEC-074" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-074 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_56_PUBLIC_REFERENCE_BATCH_2_DEPTH_SEO_INEVITABILITY_AUDIT.md").is_file():
        error("Sprint 56 audit missing")
        ok = False
    if "validate_public_reference_batch_2_depth_seo_inevitability.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 56 validator")
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
