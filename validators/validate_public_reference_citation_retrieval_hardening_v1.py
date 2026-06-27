#!/usr/bin/env python3
"""Validate Sprint 90 — Public Reference Citation and Retrieval Hardening v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    PUBLIC_SITEMAP_URL_COUNT,
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
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
    validate_public_surface,
)

HARDENING_DOC = "PUBLIC_REFERENCE_CITATION_AND_RETRIEVAL_HARDENING_V1.md"
CITATION_STD = "PUBLIC_CITATION_COMPONENT_STANDARD_V1.md"
RETRIEVAL_STD = "PUBLIC_AI_RETRIEVAL_CAPSULE_STANDARD_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_CITATION_RETRIEVAL_AUDIT_V1.md"
HARDENING_JSON = "data/public-reference-citation-retrieval-hardening-v1.json"
HARDENING_SCHEMA = "data/public-reference-citation-retrieval-hardening-v1.schema.json"
SPRINT_AUDIT = "SPRINT_90_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_V1.md"
INDEX = "index.html"
EXPECTED = 29

UTILITY_REFERENCE_PAGES = {
    "manual-evidence-checklist/index.html": "/manual-evidence-checklist/",
    "evidence-posture-map/index.html": "/evidence-posture-map/",
    "synthetic-examples/index.html": "/synthetic-examples/",
    "evidence-risk-questions/index.html": "/evidence-risk-questions/",
    "evidence-risk/index.html": "/evidence-risk/",
    "provenance-risk/index.html": "/provenance-risk/",
    "context-collapse/index.html": "/context-collapse/",
    "claim-drift/index.html": "/claim-drift/",
    "traceability-gap/index.html": "/traceability-gap/",
    "why-hoax-ai-is-not-a-detector/index.html": "/why-hoax-ai-is-not-a-detector/",
}

ALL_PAGES = {INDEX: "/", **UTILITY_REFERENCE_PAGES}

HOME_ANCHORS = [
    "id=\"hero\"",
    "id=\"public-utilities\"",
    "id=\"reference-layer\"",
    "id=\"reference-graph\"",
    "id=\"source-confidence\"",
    "id=\"reference-answer\"",
    "id=\"cite-this-reference\"",
    "id=\"retrieval-capsule\"",
    "id=\"boundary\"",
]

PAGE_ANCHORS = [
    "id=\"reference-answer\"",
    "id=\"source-confidence\"",
    "id=\"reference-path\"",
    "id=\"cite-this-reference\"",
    "id=\"retrieval-capsule\"",
    "id=\"boundary\"",
]

FORBIDDEN_PHRASE_CHECKS = [
    "confidence score",
    "verified truth",
    "detected authenticity",
    "forensic proof",
    "legal determination",
    "manipulation finding",
]

FORBIDDEN_CLAIMS = [
    "real or fake",
    "fake detector",
    "ai detector",
    "detects fake",
    "verifies truth",
    "scores authenticity",
    "upload a file",
    "submit evidence",
    "analyze your file",
    "generate report",
    "verified true",
    "verified false",
    "proven manipulated",
    "fraudulent",
    "guilty",
    "deceptive",
]

CHATBOT_MARKERS = ["chatbot", "answer generator", "automated response"]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

SOURCE_LOCS = [
    HARDENING_DOC,
    CITATION_STD,
    RETRIEVAL_STD,
    AUDIT_DOC,
    HARDENING_JSON,
    HARDENING_SCHEMA,
    SPRINT_AUDIT,
    "validators/validate_public_reference_citation_retrieval_hardening_v1.py",
    INDEX,
    *UTILITY_REFERENCE_PAGES.keys(),
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def line_has_unnegated_claim(line: str, claim: str) -> bool:
    lower = line.lower()
    if claim not in lower:
        return False
    pos = 0
    while True:
        idx = lower.find(claim, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 80) : idx]
        if not NEGATION_PATTERN.search(prefix + claim):
            return True
        pos = idx + len(claim)
    return False


def validate_artifacts() -> bool:
    ok = True
    for rel in [HARDENING_DOC, CITATION_STD, RETRIEVAL_STD, AUDIT_DOC, HARDENING_JSON, HARDENING_SCHEMA, SPRINT_AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(HARDENING_JSON)
    if data.get("decision_ref") != "DEC-108":
        error("decision_ref must be DEC-108")
        ok = False
    if len(data.get("pages_updated", [])) != 11:
        error("pages_updated must contain exactly 11 entries")
        ok = False
    if len(data.get("required_components", [])) != 5:
        error("required_components must contain exactly 5 components")
        ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    if (ROOT / "sitemap.xml").read_text(encoding="utf-8").count("<loc>") != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have exactly {EXPECTED} URLs")
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have exactly {EXPECTED} entries")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    return ok


def validate_page(rel: str, is_home: bool = False) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    for label in (
        "cite this reference",
        "retrieval capsule",
        "best used for",
        "not suitable for",
        "boundary reminder",
    ):
        if label not in lower:
            error(f"{rel}: missing {label!r}")
            ok = False
    if not is_home and "reference summary" not in lower:
        error(f"{rel}: missing reference summary line")
        ok = False
    if "cite-this-reference-block" in lower:
        cite_region = lower.split("cite-this-reference-block", 1)[-1].split("retrieval-capsule", 1)[0]
    else:
        cite_region = lower.split("cite-this-reference", 1)[-1].split("retrieval-capsule", 1)[0]
    if "https://hoax.ai" not in cite_region:
        error(f"{rel}: missing canonical URL in citation block")
        ok = False
    if "primary concept" not in lower or "boundary rule" not in lower:
        error(f"{rel}: retrieval capsule fields incomplete")
        ok = False
    anchors = HOME_ANCHORS if is_home else PAGE_ANCHORS
    for anchor in anchors:
        if anchor not in content:
            error(f"{rel}: missing anchor {anchor}")
            ok = False
    if not is_home and 'id="related-concepts"' not in content and 'id="continue-with"' not in content:
        error(f"{rel}: missing related-concepts or continue-with anchor")
        ok = False
    for marker in CHATBOT_MARKERS:
        if marker in lower:
            error(f"{rel}: forbidden marker {marker!r}")
            ok = False
    for phrase in FORBIDDEN_PHRASE_CHECKS:
        if phrase in lower:
            error(f"{rel}: forbidden phrase {phrase!r}")
            ok = False
    if "<form" in lower or "<input" in lower:
        error(f"{rel}: forms/inputs forbidden")
        ok = False
    if re.search(r"<script\b", content, re.I):
        error(f"{rel}: JavaScript forbidden")
        ok = False
    if 'type="application/ld+json"' in lower:
        error(f"{rel}: JSON-LD forbidden")
        ok = False
    for claim in FORBIDDEN_CLAIMS:
        for line in content.splitlines():
            if line_has_unnegated_claim(line, claim):
                error(f"{rel}: forbidden claim {claim!r}")
                ok = False
                break
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-108" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-108 missing")
        ok = False
    if "validate_public_reference_citation_retrieval_hardening_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 90 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,

    ):
        error("publisher status must reflect Sprint 90 citation retrieval hardening validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0091" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0091 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0084" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0084 missing")
        ok = False
    if "Sprint 90 | COMPLETE | G90 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 90 row")
        ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_cache() -> bool:
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    names += subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        r = rel.replace("\\", "/").lower()
        if "__pycache__/" in r or r.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in r:
            error(f"Python cache file tracked or staged: {rel}")
            return False
    return True


def main() -> int:
    ok = True
    if not validate_artifacts():
        ok = False
    if not validate_counts():
        ok = False
    if not validate_page(INDEX, is_home=True):
        ok = False
    for rel in UTILITY_REFERENCE_PAGES:
        if not validate_page(rel):
            ok = False
    if not validate_governance():
        ok = False
    if not validate_cache():
        ok = False
    if not ok:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
