#!/usr/bin/env python3
"""Validate Sprint 88 — Public Reference Source Confidence Layer v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    PUBLIC_SITEMAP_URL_COUNT,
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    validate_public_surface,
)

LAYER_DOC = "PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_V1.md"
STANDARD_DOC = "PUBLIC_SOURCE_CONFIDENCE_COMPONENT_STANDARD_V1.md"
AUDIT_DOC = "PUBLIC_SOURCE_CONFIDENCE_AUDIT_V1.md"
LAYER_JSON = "data/public-reference-source-confidence-layer-v1.json"
LAYER_SCHEMA = "data/public-reference-source-confidence-layer-v1.schema.json"
SPRINT_AUDIT = "SPRINT_88_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_V1.md"
INDEX = "index.html"
EXPECTED = 29

ALL_PAGES = {
    INDEX: "/",
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

ALLOWED_SUPPORT_MARKERS = [
    "conceptual definition",
    "manual utility guidance",
    "synthetic example",
    "boundary statement",
    "repository-governed reference",
]

FORBIDDEN_SUPPORT = [
    "verified truth",
    "detected authenticity",
    "factual determination",
    "legal determination",
    "forensic proof",
    "manipulation finding",
    "user-submitted evidence",
    "live detection result",
    "automated confidence score",
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

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

SOURCE_LOCS = [
    LAYER_DOC,
    STANDARD_DOC,
    AUDIT_DOC,
    LAYER_JSON,
    LAYER_SCHEMA,
    SPRINT_AUDIT,
    "validators/validate_public_reference_source_confidence_layer_v1.py",
    INDEX,
    *[p for p in ALL_PAGES if p != INDEX],
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
    for rel in [LAYER_DOC, STANDARD_DOC, AUDIT_DOC, LAYER_JSON, LAYER_SCHEMA, SPRINT_AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(LAYER_JSON)
    if data.get("decision_ref") != "DEC-106":
        error("decision_ref must be DEC-106")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if len(data.get("pages_updated", [])) != 11:
        error("pages_updated must contain exactly 11 entries")
        ok = False
    if len(data.get("allowed_support_types", [])) != 5:
        error("allowed_support_types must contain exactly 5 types")
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


def validate_page(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    for label in (
        "source confidence",
        "support type",
        "what this page can support",
        "what this page cannot support",
    ):
        if label not in lower:
            error(f"{rel}: missing {label!r}")
            ok = False
    if "automated authenticity labels" not in lower and "numeric certainty outputs" not in lower:
        error(f"{rel}: missing safe boundary language")
        ok = False
    if not any(m in lower for m in ALLOWED_SUPPORT_MARKERS):
        error(f"{rel}: missing allowed support type marker")
        ok = False
    for forbidden in FORBIDDEN_SUPPORT:
        if forbidden in lower:
            error(f"{rel}: forbidden support type {forbidden!r}")
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
    for claim in FORBIDDEN_CLAIMS:
        for line in content.splitlines():
            if line_has_unnegated_claim(line, claim):
                error(f"{rel}: forbidden claim {claim!r}")
                ok = False
                break
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-106" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-106 missing")
        ok = False
    if "validate_public_reference_source_confidence_layer_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 88 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
        "blocked_until_public_reference_answer_surface_validation",
        "blocked_until_public_reference_citation_retrieval_hardening_validation",
        "blocked_until_public_reference_quality_consolidation_validation",
        "blocked_until_public_reference_depth_expansion_validation",
        "blocked_until_public_reference_pathway_pages_validation",
        "blocked_until_public_reference_navigation_ia_consolidation_validation",
        "blocked_until_public_reference_surface_authority_review_validation",
        "blocked_until_public_reference_strategic_entry_points_validation",
        "blocked_until_public_reference_strategic_narrative_surface_validation",
        "blocked_until_public_reference_acquisition_readiness_surface_validation",
        "blocked_until_public_reference_strategic_surface_consolidation_validation",
        "blocked_until_public_reference_release_integrity_audit_validation",
        "blocked_until_public_reference_external_review_readiness_validation",
        "blocked_until_public_reference_reviewer_packet_validation",
        "blocked_until_public_reference_review_packet_integrity_audit_validation",
    ):
        error("publisher status must reflect Sprint 88 source confidence layer validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0089" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0089 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0082" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0082 missing")
        ok = False
    if "Sprint 88 | COMPLETE | G88 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 88 row")
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
    for rel in ALL_PAGES:
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
