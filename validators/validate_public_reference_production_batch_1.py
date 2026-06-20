#!/usr/bin/env python3
"""Validate Sprint 53 — Public Reference Production Batch 1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_1,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_2,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_3,
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_STANDARD_V1,
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT,
    PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
    PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
        PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    validate_public_surface,
)

BATCH1_PAGES = {
    "reference/source-confidence/index.html": {
        "h1": "Source Confidence",
        "canonical": "https://hoax.ai/reference/source-confidence/",
        "path": "/reference/source-confidence/",
        "boundary_phrases": [
            "does not perform the verdict",
            "cannot accuse",
            "does not certify",
            "contributes to posture",
        ],
        "batch_links": [
            "/reference/provenance-gap/",
            "/reference/not-assessable/",
            "/reference/output-boundary/",
        ],
    },
    "reference/provenance-gap/index.html": {
        "h1": "Provenance Gap",
        "canonical": "https://hoax.ai/reference/provenance-gap/",
        "path": "/reference/provenance-gap/",
        "boundary_phrases": [
            "does not prove manipulation",
            "cannot prove manipulation",
            "cannot identify a guilty subject",
        ],
        "batch_links": [
            "/reference/source-confidence/",
            "/reference/not-assessable/",
            "/reference/output-boundary/",
        ],
    },
    "reference/not-assessable/index.html": {
        "h1": "Not Assessable",
        "canonical": "https://hoax.ai/reference/not-assessable/",
        "path": "/reference/not-assessable/",
        "boundary_phrases": [
            "not mean the artifact is false",
            "not mean the artifact is true",
            "not failure",
            "not hidden judgment",
        ],
        "batch_links": [
            "/reference/output-boundary/",
            "/reference/provenance-gap/",
            "/reference/source-confidence/",
        ],
    },
    "reference/output-boundary/index.html": {
        "h1": "Output Boundary",
        "canonical": "https://hoax.ai/reference/output-boundary/",
        "path": "/reference/output-boundary/",
        "boundary_phrases": [
            "prevents verdict",
            "subject accusation",
            "unsupported certainty",
            "fake/real",
        ],
        "batch_links": [
            "/reference/not-assessable/",
            "/reference/source-confidence/",
            "/reference/provenance-gap/",
        ],
    },
}

REQUIRED_SECTIONS = [
    "Definition",
    "Why It Matters",
    "What It Can Describe",
    "What It Cannot Decide",
    "Relationship to Evidence Posture",
    "Relationship to Artifact–Subject Separation",
    "Common Misreadings",
    "Hoax.ai Boundary",
    "Related Reference Pages",
]

BATCH1_PATHS = [
    "/reference/source-confidence/",
    "/reference/provenance-gap/",
    "/reference/not-assessable/",
    "/reference/output-boundary/",
]

BATCH1_ROUTE_IDS = ["ROUTE-0005", "ROUTE-0006", "ROUTE-0007", "ROUTE-0008"]

FORBIDDEN_PAGE_TERMS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
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
    "reference/source-confidence/index.html",
    "reference/provenance-gap/index.html",
    "reference/not-assessable/index.html",
    "reference/output-boundary/index.html",
    "validators/validate_public_reference_production_batch_1.py",
    "SPRINT_53_PUBLIC_REFERENCE_PRODUCTION_BATCH_1_AUDIT.md",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_batch_pages() -> bool:
    ok = True
    for rel, spec in BATCH1_PAGES.items():
        path = ROOT / rel
        if not path.is_file():
            error(f"missing batch page {rel}")
            ok = False
            continue
        text = path.read_text(encoding="utf-8")
        if text.count("<h1") != 1:
            error(f"{rel}: must have exactly one H1")
            ok = False
        if spec["canonical"] not in text:
            error(f"{rel}: missing canonical URL")
            ok = False
        if "<title>" not in text:
            error(f"{rel}: missing title metadata")
            ok = False
        if 'name="description"' not in text:
            error(f"{rel}: missing meta description")
            ok = False
        for section in REQUIRED_SECTIONS:
            if section not in text:
                error(f"{rel}: missing section {section}")
                ok = False
        for phrase in spec["boundary_phrases"]:
            if phrase.lower() not in text.lower():
                error(f"{rel}: missing boundary phrase '{phrase}'")
                ok = False
        if "/language/" not in text:
            error(f"{rel}: must link to /language/")
            ok = False
        if "/reference/evidence-posture/" not in text:
            error(f"{rel}: must link to /reference/evidence-posture/")
            ok = False
        linked = sum(1 for p in spec["batch_links"] if p in text)
        if linked < 2:
            error(f"{rel}: must link to at least two other Batch 1 pages")
            ok = False
        for pat in FORBIDDEN_PAGE_TERMS:
            if re.search(pat, text, re.I):
                error(f"{rel}: forbidden term matched {pat}")
                ok = False
    return ok


def validate_internal_links() -> bool:
    ok = True
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    for p in BATCH1_PATHS:
        if p not in homepage:
            error(f"homepage must link to {p}")
            ok = False
    ep = (ROOT / "reference/evidence-posture/index.html").read_text(encoding="utf-8")
    for p in BATCH1_PATHS:
        if p not in ep:
            error(f"evidence-posture page must link to {p}")
            ok = False
    ass = (ROOT / "reference/artifact-subject-separation/index.html").read_text(encoding="utf-8")
    for p in ["/reference/not-assessable/", "/reference/output-boundary/"]:
        if p not in ass:
            error(f"artifact-subject-separation must link to {p}")
            ok = False
    for p in ["/reference/source-confidence/", "/reference/provenance-gap/"]:
        if p not in ass:
            error(f"artifact-subject-separation must link to {p}")
            ok = False
    lang = (ROOT / "language/index.html").read_text(encoding="utf-8")
    for p in BATCH1_PATHS:
        if p not in lang:
            error(f"language page must link to {p}")
            ok = False
    for term in ["Source Confidence", "Provenance Gap", "Not Assessable", "Output Boundary"]:
        if term not in lang:
            error(f"language page must include term {term}")
            ok = False
    return ok


def validate_registry_and_sitemap() -> bool:
    ok = True
    routes = load("data/route-registry.json").get("routes", [])
    batch = [r for r in routes if r.get("production_batch") == "public_reference_production_batch_1"]
    if len(batch) != 4:
        error("route registry must include exactly four Batch 1 routes")
        ok = False
    paths = {r.get("path") for r in batch}
    if paths != set(BATCH1_PATHS):
        error("route registry Batch 1 paths mismatch")
        ok = False
    ids = {r.get("route_id") for r in batch}
    if ids != set(BATCH1_ROUTE_IDS):
        error("route registry Batch 1 route IDs mismatch")
        ok = False
    for route in batch:
        if route.get("public_surface") is not True or route.get("sitemap_included") is not True:
            error(f"route {route.get('route_id')} must be public and sitemap eligible")
            ok = False
        prohibited = " ".join(route.get("prohibited_capabilities", [])).lower()
        for term in ["engine", "classifier", "upload", "scoring", "api", "analytics", "forms"]:
            if term not in prohibited:
                error(f"route {route.get('route_id')} must prohibit {term}")
                ok = False
    if not validate_public_surface(routes, error, len(routes)):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    for p in BATCH1_PATHS:
        url = f"https://hoax.ai{p}"
        if url not in locs:
            error(f"sitemap missing {url}")
            ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
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
        error("prototype files modified in Sprint 53")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    pub = load("data/publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_1,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_2,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_3,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_STANDARD_V1,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT,
        PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
        PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
        PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
        PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
        PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
        PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    ):
        error("publisher status must reflect batch 1, batch 2, batch 3, standard v1, protocol v1 draft, interface thesis, static embodiment v1, visual system hardening, or controlled domain connection decision state")
        ok = False
    gate = next(
        (g for g in load("data/publisher-quality-gates.json").get("gates", []) if g.get("gate_id") == "PUB-GATE-0053"),
        None,
    )
    if not gate:
        error("PUB-GATE-0053 missing")
        ok = False
    elif gate.get("required_before_public_reference_production_batch_1_validation") is not True:
        error("batch 1 gate must require validation before further expansion")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0059" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0059 missing")
        ok = False
    if "validate_public_reference_production_batch_1.py" not in (ROOT / "validators/validate_all.py").read_text(encoding="utf-8"):
        error("validate_all missing batch 1 validator")
        ok = False
    if "DEC-071" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-071 missing")
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
    for rel in ["data/route-registry.json", "data/publisher-governance-policy.json", "data/publisher-quality-gates.json"]:
        try:
            load(rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"parse failed {rel}: {exc}")
            return 1
    checks = [
        validate_batch_pages,
        validate_internal_links,
        validate_registry_and_sitemap,
        validate_public_safety,
        validate_governance,
        validate_cache,
    ]
    ok = all(fn() for fn in checks)
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
