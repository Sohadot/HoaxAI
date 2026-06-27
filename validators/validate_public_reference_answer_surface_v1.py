#!/usr/bin/env python3
"""Validate Sprint 89 — Public Reference Answer Surface v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    validate_public_surface,
)

SURFACE_DOC = "PUBLIC_REFERENCE_ANSWER_SURFACE_V1.md"
STANDARD_DOC = "PUBLIC_ANSWER_SURFACE_COMPONENT_STANDARD_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_ANSWER_SURFACE_AUDIT_V1.md"
SURFACE_JSON = "data/public-reference-answer-surface-v1.json"
SURFACE_SCHEMA = "data/public-reference-answer-surface-v1.schema.json"
SPRINT_AUDIT = "SPRINT_89_PUBLIC_REFERENCE_ANSWER_SURFACE_V1.md"
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

CANONICAL_QUESTIONS = {
    INDEX: "what is hoax.ai?",
    "evidence-risk/index.html": "what is evidence risk?",
    "provenance-risk/index.html": "what is provenance risk?",
    "context-collapse/index.html": "what is context collapse?",
    "claim-drift/index.html": "what is claim drift?",
    "traceability-gap/index.html": "what is a traceability gap?",
    "why-hoax-ai-is-not-a-detector/index.html": "why is hoax.ai not a detector?",
}

FORBIDDEN_ANSWER_TYPES = [
    "authenticity determination",
    "legal determination",
    "forensic proof",
    "accusation",
    "live case assessment",
    "user-submitted artifact answer",
    "numeric certainty output",
    "automated report output",
    "binary authenticity label output",
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

CHATBOT_MARKERS = [
    "chatbot",
    "answer generator",
    "automated response",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

SOURCE_LOCS = [
    SURFACE_DOC,
    STANDARD_DOC,
    AUDIT_DOC,
    SURFACE_JSON,
    SURFACE_SCHEMA,
    SPRINT_AUDIT,
    "validators/validate_public_reference_answer_surface_v1.py",
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
    for rel in [SURFACE_DOC, STANDARD_DOC, AUDIT_DOC, SURFACE_JSON, SURFACE_SCHEMA, SPRINT_AUDIT]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(SURFACE_JSON)
    if data.get("decision_ref") != "DEC-107":
        error("decision_ref must be DEC-107")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if len(data.get("pages_updated", [])) != 11:
        error("pages_updated must contain exactly 11 entries")
        ok = False
    if len(data.get("allowed_answer_types", [])) != 6:
        error("allowed_answer_types must contain exactly 6 types")
        ok = False
    if data.get("chatbot_authorized") is not False or data.get("generator_authorized") is not False:
        error("chatbot_authorized and generator_authorized must be false")
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
    if "reference-answer-block" not in lower:
        error(f"{rel}: missing reference answer block")
        return False
    answer_lower = lower.split("reference-answer-block", 1)[1].split("</section>", 1)[0]
    for label in (
        "reference answer",
        "question",
        "short answer",
        "use this answer when",
        "do not use this answer to",
        "related pages",
    ):
        if label not in lower:
            error(f"{rel}: missing {label!r}")
            ok = False
    if "automated authenticity labels" not in lower and "numeric certainty outputs" not in lower:
        error(f"{rel}: missing safe boundary language")
        ok = False
    if '<a href="' not in content.split("reference-answer-block", 1)[-1]:
        error(f"{rel}: missing related page links in answer block")
        ok = False
    for forbidden in FORBIDDEN_ANSWER_TYPES:
        if forbidden in answer_lower:
            error(f"{rel}: forbidden answer type {forbidden!r}")
            ok = False
    for marker in CHATBOT_MARKERS:
        if marker in answer_lower:
            error(f"{rel}: forbidden chatbot/generator marker {marker!r}")
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
    if rel in CANONICAL_QUESTIONS and CANONICAL_QUESTIONS[rel] not in lower:
        error(f"{rel}: missing canonical question {CANONICAL_QUESTIONS[rel]!r}")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-107" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-107 missing")
        ok = False
    if "validate_public_reference_answer_surface_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 89 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,

    ):
        error("publisher status must reflect Sprint 89 answer surface validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0090" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0090 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0083" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0083 missing")
        ok = False
    if "Sprint 89 | COMPLETE | G89 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 89 row")
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
