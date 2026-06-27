#!/usr/bin/env python3
"""Validate Sprint 58 — Public Reference Batch 3 Depth and Standard Readiness."""

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

BATCH3_PAGES = {
    "reference/attribution-boundary/index.html": {
        "h1": "Attribution Boundary",
        "canonical": "https://hoax.ai/reference/attribution-boundary/",
        "path": "/reference/attribution-boundary/",
        "named_model": "Attribution Boundary Model",
        "min_words": 1900,
        "standard_phrases": [
            "Evidence Posture Standard v1",
            "artifact-level condition",
            "subject implication",
        ],
        "allowed_phrases": [
            "artifact-level condition",
            "provenance uncertainty",
            "context limitation",
        ],
        "prohibited_phrases": [
            "guilt",
            "intent",
            "authorship",
            "deception",
            "misconduct",
            "responsibility",
        ],
        "boundary_phrases": [
            "does not assign guilt",
            "does not prove deception",
            "artifact condition is not subject judgment",
            "does not certify authorship",
        ],
        "prior_links": [
            "/reference/artifact-subject-separation/",
            "/reference/evidence-posture/",
            "/reference/output-boundary/",
        ],
    },
    "reference/claim-drift/index.html": {
        "h1": "Claim Drift",
        "canonical": "https://hoax.ai/reference/claim-drift/",
        "path": "/reference/claim-drift/",
        "named_model": "Claim Drift Chain",
        "min_words": 1500,
        "standard_phrases": [
            "Evidence Posture Standard v1",
            "not assessable",
            "Claim–Source Traceability",
        ],
        "allowed_phrases": [
            "compression drift",
            "certainty drift",
            "model-summary drift",
        ],
        "prohibited_phrases": [
            "does not prove deception",
            "does not prove manipulation",
            "motive",
        ],
        "boundary_phrases": [
            "not deception by default",
            "claim movement is not deception",
            "does not assign guilt",
        ],
        "prior_links": [
            "/reference/claim-source-traceability/",
            "/reference/evidence-chain/",
            "/reference/evidence-posture/",
        ],
    },
    "reference/evidence-limitation/index.html": {
        "h1": "Evidence Limitation",
        "canonical": "https://hoax.ai/reference/evidence-limitation/",
        "path": "/reference/evidence-limitation/",
        "named_model": "Evidence Limitation Envelope",
        "min_words": 1500,
        "standard_phrases": [
            "Evidence Posture Standard v1",
            "supported statement",
            "not assessable statement",
        ],
        "allowed_phrases": [
            "qualified statement",
            "limited statement",
            "unsupported statement",
        ],
        "prohibited_phrases": [
            "limitation is not weakness",
            "not a truth verdict",
            "not failure",
            "not proof that the underlying claim is false",
        ],
        "boundary_phrases": [
            "evidence limitation is not a truth verdict",
            "does not assign guilt",
            "does not prove deception",
        ],
        "prior_links": [
            "/reference/not-assessable/",
            "/reference/output-boundary/",
            "/reference/evidence-posture/",
        ],
    },
    "reference/interpretation-risk/index.html": {
        "h1": "Interpretation Risk",
        "canonical": "https://hoax.ai/reference/interpretation-risk/",
        "path": "/reference/interpretation-risk/",
        "named_model": "Interpretation Risk Stack",
        "min_words": 1500,
        "standard_phrases": [
            "Evidence Posture Standard v1",
            "output restraint",
            "overinterpretation",
        ],
        "allowed_phrases": [
            "interpretation risk is not accusation",
            "does not mean the artifact is false",
        ],
        "prohibited_phrases": [
            "does not prove falsehood",
            "does not prove deception",
            "motive",
            "blame",
        ],
        "boundary_phrases": [
            "interpretation risk is not accusation",
            "does not mean the artifact is false",
            "does not assign guilt",
        ],
        "prior_links": [
            "/reference/evidence-limitation/",
            "/reference/context-collapse/",
            "/reference/evidence-posture/",
        ],
    },
}

REQUIRED_SECTIONS = [
    "Definition",
    "Category Thesis",
    "Failure Modes",
    "Boundary Logic",
    "Institutional Relevance",
    "Evidence System Relationships",
    "Standard-Readiness",
    "Allowed and Prohibited Output Language",
    "Practical Reading Frame",
    "Hoax.ai Boundary",
    "Related Reference Pages",
]

FORBIDDEN_PATTERNS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script[^>]+src=",
    r"deepfake detector",
    r"truth score",
    r"upload your",
    r"scan now",
    r"public classifier is available",
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
    "SPRINT_58_PUBLIC_REFERENCE_BATCH_3_DEPTH_STANDARD_READINESS_AUDIT.md",
    "validators/validate_public_reference_batch_3_depth_standard_readiness.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    return re.sub(r"<[^>]+>", " ", text)


def visible_word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html)))


def validate_pages() -> bool:
    ok = True
    for rel, spec in BATCH3_PAGES.items():
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
        if "<title>" not in text or 'name="description"' not in text:
            error(f"{rel}: missing title or meta description")
            ok = False
        for section in REQUIRED_SECTIONS:
            if section not in text:
                error(f"{rel}: missing section {section}")
                ok = False
        if spec["named_model"] not in text:
            error(f"{rel}: missing named model {spec['named_model']}")
            ok = False
        for phrase in spec["standard_phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing standard-readiness phrase '{phrase}'")
                ok = False
        for phrase in spec["allowed_phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing allowed-language phrase '{phrase}'")
                ok = False
        for phrase in spec["prohibited_phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing prohibited-language phrase '{phrase}'")
                ok = False
        for phrase in spec["boundary_phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing boundary phrase '{phrase}'")
                ok = False
        if "/reference/evidence-posture/" not in text:
            error(f"{rel}: must link to Evidence Posture")
            ok = False
        prior = sum(1 for p in spec["prior_links"] if p in text)
        if prior < 3:
            error(f"{rel}: must link to at least three prior reference pages")
            ok = False
        wc = visible_word_count(text)
        if wc < spec["min_words"]:
            error(f"{rel}: insufficient depth ({wc} words, need {spec['min_words']})")
            ok = False
        if "classify the evidence artifact" not in lower and "evidence posture" not in lower:
            error(f"{rel}: missing evidence posture framing")
            ok = False
        if "artifact-subject separation" not in lower.replace("–", "-"):
            error(f"{rel}: must preserve artifact-subject separation")
            ok = False
        for pat in FORBIDDEN_PATTERNS:
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
    batch3 = [r for r in routes if r.get("production_batch") == "public_reference_production_batch_3"]
    if len(batch3) != 4:
        error("must retain exactly four Batch 3 routes")
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
    for rel in BATCH3_PAGES:
        if pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel}: prototype or blocked route leak")
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
    if "DEC-076" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-076 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_58_PUBLIC_REFERENCE_BATCH_3_DEPTH_STANDARD_READINESS_AUDIT.md").is_file():
        error("Sprint 58 audit missing")
        ok = False
    if "validate_public_reference_batch_3_depth_standard_readiness.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 58 validator")
        ok = False
    if "validate_decision_log_chronology.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include decision log chronology validator")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0062" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0062 missing")
        ok = False
    return ok


def validate_cache() -> bool:
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    names += subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error(f"python cache tracked/staged: {rel}")
            return False
    return True


def main() -> int:
    ok = all(fn() for fn in [validate_pages, validate_surface, validate_governance, validate_cache])
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
