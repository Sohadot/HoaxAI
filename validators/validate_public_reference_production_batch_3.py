#!/usr/bin/env python3
"""Validate Sprint 57 — Public Reference Production Batch 3 (depth-enforced)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
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
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_3,
    validate_public_surface,
)

BATCH3_PAGES = {
    "reference/attribution-boundary/index.html": {
        "h1": "Attribution Boundary",
        "canonical": "https://hoax.ai/reference/attribution-boundary/",
        "path": "/reference/attribution-boundary/",
        "named_model": "Attribution Boundary Model",
        "phrases": [
            "does not prove deception",
            "does not assign guilt",
            "does not certify authorship",
            "artifact condition is not subject judgment",
        ],
        "prior_links": [
            "/reference/artifact-subject-separation/",
            "/reference/output-boundary/",
            "/reference/evidence-posture/",
            "/reference/provenance-gap/",
        ],
        "batch3_links": [
            "/reference/claim-drift/",
            "/reference/evidence-limitation/",
        ],
    },
    "reference/claim-drift/index.html": {
        "h1": "Claim Drift",
        "canonical": "https://hoax.ai/reference/claim-drift/",
        "path": "/reference/claim-drift/",
        "named_model": "Claim Drift Chain",
        "phrases": [
            "not deception by default",
            "does not prove deception",
            "does not assign guilt",
            "claim movement is not deception",
        ],
        "prior_links": [
            "/reference/claim-source-traceability/",
            "/reference/evidence-chain/",
            "/reference/context-collapse/",
            "/reference/output-boundary/",
        ],
        "batch3_links": [
            "/reference/attribution-boundary/",
            "/reference/interpretation-risk/",
        ],
    },
    "reference/evidence-limitation/index.html": {
        "h1": "Evidence Limitation",
        "canonical": "https://hoax.ai/reference/evidence-limitation/",
        "path": "/reference/evidence-limitation/",
        "named_model": "Evidence Limitation Envelope",
        "phrases": [
            "limitation is not weakness",
            "evidence limitation is not a truth verdict",
            "does not prove deception",
            "does not assign guilt",
        ],
        "prior_links": [
            "/reference/not-assessable/",
            "/reference/output-boundary/",
            "/reference/provenance-gap/",
            "/reference/source-confidence/",
        ],
        "batch3_links": [
            "/reference/interpretation-risk/",
            "/reference/attribution-boundary/",
        ],
    },
    "reference/interpretation-risk/index.html": {
        "h1": "Interpretation Risk",
        "canonical": "https://hoax.ai/reference/interpretation-risk/",
        "path": "/reference/interpretation-risk/",
        "named_model": "Interpretation Risk Stack",
        "phrases": [
            "does not mean the artifact is false",
            "interpretation risk is not accusation",
            "does not prove deception",
            "does not assign guilt",
        ],
        "prior_links": [
            "/reference/context-collapse/",
            "/reference/synthetic-fragility/",
            "/reference/evidence-posture/",
            "/reference/not-assessable/",
        ],
        "batch3_links": [
            "/reference/evidence-limitation/",
            "/reference/attribution-boundary/",
        ],
    },
}

REQUIRED_SECTIONS = [
    "Definition",
    "Category Thesis",
    "Why This Term Is Necessary",
    "Evidence System Relationships",
    "Failure Modes",
    "Boundary Logic",
    "Institutional Relevance",
    "What It Cannot Decide",
    "Hoax.ai Boundary",
    "Related Reference Pages",
]

BOUNDARY_PHRASES = [
    "artifact condition is not subject judgment",
    "evidence limitation is not a truth verdict",
    "claim movement is not deception",
    "interpretation risk is not accusation",
]

INSTITUTIONAL_TERMS = [
    "platform",
    "journalist",
    "researcher",
    "analyst",
    "compliance",
    "trust",
    "ai system",
]

SEO_TERMS = [
    "evidence posture",
    "evidence limitation",
    "artifact-subject separation",
    "output boundary",
    "provenance gap",
    "synthetic media",
]

BATCH3_PATHS = [p["path"] for p in BATCH3_PAGES.values()]
BATCH3_ROUTE_IDS = ["ROUTE-0013", "ROUTE-0014", "ROUTE-0015", "ROUTE-0016"]
MIN_WORDS = 1100
MAX_SHARED_SENTENCE_CHARS = 120

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
    "reference/attribution-boundary/index.html",
    "reference/claim-drift/index.html",
    "reference/evidence-limitation/index.html",
    "reference/interpretation-risk/index.html",
    "validators/validate_public_reference_production_batch_3.py",
    "SPRINT_57_PUBLIC_REFERENCE_PRODUCTION_BATCH_3_AUDIT.md",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    return re.sub(r"<[^>]+>", " ", text)


def visible_word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html)))


def extract_sentences(html: str) -> list[str]:
    text = re.sub(r"\s+", " ", strip_tags(html)).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip().lower() for p in parts if len(p.strip()) >= MAX_SHARED_SENTENCE_CHARS]


def validate_batch_pages() -> bool:
    ok = True
    all_sentences: list[tuple[str, str]] = []
    for rel, spec in BATCH3_PAGES.items():
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
        if spec["named_model"] not in text:
            error(f"{rel}: missing named model/framework '{spec['named_model']}'")
            ok = False
        for phrase in spec["phrases"]:
            if phrase.lower() not in lower:
                error(f"{rel}: missing phrase '{phrase}'")
                ok = False
        boundary_hits = sum(1 for p in BOUNDARY_PHRASES if p in lower)
        if boundary_hits < 3:
            error(f"{rel}: insufficient explicit boundary language ({boundary_hits}/4)")
            ok = False
        inst = sum(1 for t in INSTITUTIONAL_TERMS if t in lower)
        if inst < 4:
            error(f"{rel}: insufficient institutional relevance language ({inst} terms)")
            ok = False
        seo = sum(1 for t in SEO_TERMS if t in lower)
        if seo < 4:
            error(f"{rel}: insufficient conceptual SEO depth ({seo} terms)")
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
        prior = sum(1 for p in spec["prior_links"] if p in text)
        if prior < 3:
            error(f"{rel}: must link to at least three prior reference pages")
            ok = False
        b3 = sum(1 for p in spec["batch3_links"] if p in text)
        if b3 < 1:
            error(f"{rel}: must link to at least one other Batch 3 page")
            ok = False
        wc = visible_word_count(text)
        if wc < MIN_WORDS:
            error(f"{rel}: insufficient depth ({wc} words, need {MIN_WORDS})")
            ok = False
        if "does not perform the verdict" not in lower and "classify the evidence artifact" not in lower:
            error(f"{rel}: missing evidence posture boundary language")
            ok = False
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, text, re.I):
                error(f"{rel}: forbidden pattern {pat}")
                ok = False
        for sentence in extract_sentences(text):
            all_sentences.append((rel, sentence))
    if all_sentences:
        counter = Counter(s for _, s in all_sentences)
        for sentence, count in counter.items():
            if count > 1:
                pages = sorted({rel for rel, s in all_sentences if s == sentence})
                if len(pages) > 1:
                    error(
                        f"excessive repeated wording across pages {pages}: "
                        f"{sentence[:80]}..."
                    )
                    ok = False
    return ok


def validate_internal_links() -> bool:
    ok = True
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for p in BATCH3_PATHS:
        if p not in home:
            error(f"homepage must link to {p}")
            ok = False
    ep = (ROOT / "reference/evidence-posture/index.html").read_text(encoding="utf-8")
    for p in BATCH3_PATHS:
        if p not in ep:
            error(f"evidence-posture must link to {p}")
            ok = False
    ass = (ROOT / "reference/artifact-subject-separation/index.html").read_text(encoding="utf-8")
    for p in BATCH3_PATHS:
        if p not in ass:
            error(f"artifact-subject-separation must link to {p}")
            ok = False
    lang = (ROOT / "language/index.html").read_text(encoding="utf-8")
    for p in BATCH3_PATHS:
        if p not in lang:
            error(f"language page must link to {p}")
            ok = False
    for term in ["Attribution Boundary", "Claim Drift", "Evidence Limitation", "Interpretation Risk"]:
        if term not in lang:
            error(f"language page must include {term}")
            ok = False
    ob = (ROOT / "reference/output-boundary/index.html").read_text(encoding="utf-8")
    for p in ["/reference/attribution-boundary/", "/reference/evidence-limitation/"]:
        if p not in ob:
            error(f"output-boundary must link to {p}")
            ok = False
    cst = (ROOT / "reference/claim-source-traceability/index.html").read_text(encoding="utf-8")
    if "/reference/claim-drift/" not in cst:
        error("claim-source-traceability must link to claim-drift")
        ok = False
    na = (ROOT / "reference/not-assessable/index.html").read_text(encoding="utf-8")
    if "/reference/evidence-limitation/" not in na:
        error("not-assessable must link to evidence-limitation")
        ok = False
    return ok


def validate_registry_and_sitemap() -> bool:
    ok = True
    routes = load("data/route-registry.json").get("routes", [])
    batch = [r for r in routes if r.get("production_batch") == "public_reference_production_batch_3"]
    if len(batch) != 4:
        error("route registry must include exactly four Batch 3 routes")
        ok = False
    if {r.get("path") for r in batch} != set(BATCH3_PATHS):
        error("route registry Batch 3 paths mismatch")
        ok = False
    if {r.get("route_id") for r in batch} != set(BATCH3_ROUTE_IDS):
        error("route registry Batch 3 route IDs mismatch")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    for p in BATCH3_PATHS:
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
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
    ):
        error("publisher status must be batch 3, standard v1, protocol v1 draft, interface thesis, static embodiment v1, visual system hardening, or controlled domain connection decision validation")
        ok = False
    gate = next(
        (g for g in load("data/publisher-quality-gates.json").get("gates", []) if g.get("gate_id") == "PUB-GATE-0055"),
        None,
    )
    if not gate:
        error("PUB-GATE-0055 missing")
        ok = False
    elif gate.get("required_before_public_reference_production_batch_3_validation") is not True:
        error("batch 3 gate must require validation before further expansion")
        ok = False
    locs = {s.get("location") for s in load("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0061" for c in load("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0061 missing")
        ok = False
    if "validate_public_reference_production_batch_3.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all missing batch 3 validator")
        ok = False
    if "DEC-075" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-075 missing")
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
