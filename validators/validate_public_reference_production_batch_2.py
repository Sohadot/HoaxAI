#!/usr/bin/env python3
"""Validate Sprint 55 — Public Reference Production Batch 2."""

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
    validate_public_surface,
)

BATCH2_PAGES = {
    "reference/synthetic-fragility/index.html": {
        "h1": "Synthetic Fragility",
        "canonical": "https://hoax.ai/reference/synthetic-fragility/",
        "path": "/reference/synthetic-fragility/",
        "phrases": [
            "does not prove that an artifact is fake",
            "does not prove manipulation",
            "does not prove deception",
            "does not accuse",
        ],
        "batch1_links": [
            "/reference/provenance-gap/",
            "/reference/source-confidence/",
            "/reference/not-assessable/",
        ],
        "batch2_links": [
            "/reference/context-collapse/",
            "/reference/evidence-chain/",
        ],
    },
    "reference/evidence-chain/index.html": {
        "h1": "Evidence Chain",
        "canonical": "https://hoax.ai/reference/evidence-chain/",
        "path": "/reference/evidence-chain/",
        "phrases": [
            "not a proof of truth",
            "not truth certification",
            "not a verdict chain",
            "does not assign guilt",
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
    },
    "reference/context-collapse/index.html": {
        "h1": "Context Collapse",
        "canonical": "https://hoax.ai/reference/context-collapse/",
        "path": "/reference/context-collapse/",
        "phrases": [
            "does not prove manipulation",
            "does not prove deception",
            "does not identify a guilty subject",
            "does not assign motive",
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
    },
    "reference/claim-source-traceability/index.html": {
        "h1": "Claim–Source Traceability",
        "canonical": "https://hoax.ai/reference/claim-source-traceability/",
        "path": "/reference/claim-source-traceability/",
        "phrases": [
            "does not prove a claim true",
            "does not certify a source",
            "unsupported certainty",
        ],
        "batch1_links": [
            "/reference/source-confidence/",
            "/reference/output-boundary/",
            "/reference/evidence-posture/",
        ],
        "batch2_links": [
            "/reference/evidence-chain/",
            "/reference/context-collapse/",
        ],
    },
}

REQUIRED_SECTIONS = [
    "Definition",
    "Category Thesis",
    "Why This Term Is Necessary",
    "Why It Matters",
    "What It Can Describe",
    "What It Cannot Decide",
    "What This Concept Prevents",
    "System Role",
    "Relationship to Evidence Posture",
    "Relationship to Artifact–Subject Separation",
    "Practical Reading Frame",
    "Common Misreadings",
    "Hoax.ai Boundary",
    "Related Reference Pages",
]

BATCH2_PATHS = list(p["path"] for p in BATCH2_PAGES.values())
BATCH2_ROUTE_IDS = ["ROUTE-0009", "ROUTE-0010", "ROUTE-0011", "ROUTE-0012"]
BATCH1_PATHS = [
    "/reference/source-confidence/",
    "/reference/provenance-gap/",
    "/reference/not-assessable/",
    "/reference/output-boundary/",
]

FORBIDDEN_PATTERNS = [
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
    r"scanner interface",
    r"detector interface",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "reference/synthetic-fragility/index.html",
    "reference/evidence-chain/index.html",
    "reference/context-collapse/index.html",
    "reference/claim-source-traceability/index.html",
    "validators/validate_public_reference_production_batch_2.py",
    "SPRINT_55_PUBLIC_REFERENCE_PRODUCTION_BATCH_2_AUDIT.md",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_batch_pages() -> bool:
    ok = True
    for rel, spec in BATCH2_PAGES.items():
        path = ROOT / rel
        if not path.is_file():
            error(f"missing batch page {rel}")
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
        for section in REQUIRED_SECTIONS:
            if section not in text:
                error(f"{rel}: missing section {section}")
                ok = False
        for phrase in spec["phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing phrase '{phrase}'")
                ok = False
        if "/language/" not in text:
            error(f"{rel}: must link to /language/")
            ok = False
        if "/reference/evidence-posture/" not in text:
            error(f"{rel}: must link to evidence posture")
            ok = False
        if "/reference/artifact-subject-separation/" not in text:
            error(f"{rel}: must link to artifact-subject separation")
            ok = False
        b1 = sum(1 for p in spec["batch1_links"] if p in text)
        if b1 < 2:
            error(f"{rel}: must link to at least two Batch 1 pages")
            ok = False
        b2 = sum(1 for p in spec["batch2_links"] if p in text)
        if b2 < 1:
            error(f"{rel}: must link to at least one other Batch 2 page")
            ok = False
        if "evidence posture" not in lower and "classify the evidence artifact" not in lower:
            error(f"{rel}: missing evidence posture boundary language")
            ok = False
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, text, re.I):
                error(f"{rel}: forbidden pattern {pat}")
                ok = False
    return ok


def validate_internal_links() -> bool:
    ok = True
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for p in BATCH2_PATHS:
        if p not in home:
            error(f"homepage must link to {p}")
            ok = False
    ep = (ROOT / "reference/evidence-posture/index.html").read_text(encoding="utf-8")
    for p in BATCH2_PATHS:
        if p not in ep:
            error(f"evidence-posture must link to {p}")
            ok = False
    ass = (ROOT / "reference/artifact-subject-separation/index.html").read_text(encoding="utf-8")
    for p in [
        "/reference/synthetic-fragility/",
        "/reference/context-collapse/",
        "/reference/claim-source-traceability/",
        "/reference/evidence-chain/",
    ]:
        if p not in ass:
            error(f"artifact-subject-separation must link to {p}")
            ok = False
    if "does not imply subject guilt" not in ass.lower() and "does not prove misconduct" not in ass.lower():
        error("artifact-subject-separation must include Batch 2 boundary language")
        ok = False
    lang = (ROOT / "language/index.html").read_text(encoding="utf-8")
    for p in BATCH2_PATHS:
        if p not in lang:
            error(f"language page must link to {p}")
            ok = False
    for term in ["Synthetic Fragility", "Evidence Chain", "Context Collapse", "Claim"]:
        if term not in lang:
            error(f"language page must include {term}")
            ok = False
    sc = (ROOT / "reference/source-confidence/index.html").read_text(encoding="utf-8")
    for p in ["/reference/evidence-chain/", "/reference/claim-source-traceability/"]:
        if p not in sc:
            error(f"source-confidence must link to {p}")
            ok = False
    pg = (ROOT / "reference/provenance-gap/index.html").read_text(encoding="utf-8")
    for p in ["/reference/evidence-chain/", "/reference/context-collapse/", "/reference/synthetic-fragility/"]:
        if p not in pg:
            error(f"provenance-gap must link to {p}")
            ok = False
    na = (ROOT / "reference/not-assessable/index.html").read_text(encoding="utf-8")
    for p in ["/reference/context-collapse/", "/reference/synthetic-fragility/"]:
        if p not in na:
            error(f"not-assessable must link to {p}")
            ok = False
    ob = (ROOT / "reference/output-boundary/index.html").read_text(encoding="utf-8")
    for p in ["/reference/claim-source-traceability/", "/reference/evidence-chain/"]:
        if p not in ob:
            error(f"output-boundary must link to {p}")
            ok = False
    return ok


def validate_registry_and_sitemap() -> bool:
    ok = True
    routes = load("data/route-registry.json").get("routes", [])
    batch = [r for r in routes if r.get("production_batch") == "public_reference_production_batch_2"]
    if len(batch) != 4:
        error("route registry must include exactly four Batch 2 routes")
        ok = False
    if {r.get("path") for r in batch} != set(BATCH2_PATHS):
        error("route registry Batch 2 paths mismatch")
        ok = False
    if {r.get("route_id") for r in batch} != set(BATCH2_ROUTE_IDS):
        error("route registry Batch 2 route IDs mismatch")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    for p in BATCH2_PATHS:
        if f"https://hoax.ai{p}" not in locs:
            error(f"sitemap missing {p}")
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
    pub = load("data/publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
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
    ):
        error("publisher status must be batch 2, batch 3, standard v1, protocol v1 draft, interface thesis, static embodiment v1, visual system hardening, or controlled domain connection decision validation")
        ok = False
    gate = next(
        (g for g in load("data/publisher-quality-gates.json").get("gates", []) if g.get("gate_id") == "PUB-GATE-0054"),
        None,
    )
    if not gate:
        error("PUB-GATE-0054 missing")
        ok = False
    elif gate.get("required_before_public_reference_production_batch_2_validation") is not True:
        error("batch 2 gate must require validation before further expansion")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0060" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0060 missing")
        ok = False
    if "validate_public_reference_production_batch_2.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing batch 2 validator")
        ok = False
    if "DEC-073" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-073 missing")
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
    ok = all(
        fn()
        for fn in [
            validate_batch_pages,
            validate_internal_links,
            validate_registry_and_sitemap,
            validate_public_safety,
            validate_governance,
            validate_cache,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
