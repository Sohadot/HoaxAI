#!/usr/bin/env python3
"""Validate Sprint 96 — Public Reference Strategic Entry Points v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    PUBLIC_SITEMAP_URL_COUNT,
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
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
    validate_public_surface,
)

ENTRY_DOC = "PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_AUDIT_V1.md"
STANDARD_DOC = "PUBLIC_STRATEGIC_ENTRY_POINT_STANDARD_V1.md"
ENTRY_JSON = "data/public-reference-strategic-entry-points-v1.json"
ENTRY_SCHEMA = "data/public-reference-strategic-entry-points-v1.schema.json"
SPRINT_DOC = "SPRINT_96_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_V1.md"
INDEX = "index.html"
EXPECTED = 47
MIN_WORDS = 800

NEW_ROUTES = {
    "entry-points/index.html": "/entry-points/",
    "entry-points/human-readers/index.html": "/entry-points/human-readers/",
    "entry-points/ai-agents/index.html": "/entry-points/ai-agents/",
    "entry-points/research-review/index.html": "/entry-points/research-review/",
    "entry-points/trust-safety/index.html": "/entry-points/trust-safety/",
    "entry-points/education-literacy/index.html": "/entry-points/education-literacy/",
}

ROUTE_IDS = [f"ROUTE-{i:04d}" for i in range(42, 48)]

UTILITY_OR_PATHWAY = [
    "/manual-evidence-checklist/",
    "/evidence-posture-map/",
    "/synthetic-examples/",
    "/evidence-risk-questions/",
    "/pathways/source-unclear/",
    "/pathways/provenance-weak/",
    "/pathways/context-missing/",
    "/pathways/claim-overextended/",
    "/pathways/traceability-incomplete/",
    "/pathways/posture-not-assessable/",
]

REFERENCE_ROUTES = [
    "/evidence-risk/",
    "/provenance-risk/",
    "/context-collapse/",
    "/claim-drift/",
    "/traceability-gap/",
    "/source-ambiguity/",
    "/artifact-claim-gap/",
    "/boundary-integrity/",
    "/evidence-weight/",
    "/interpretation-risk/",
    "/not-assessable-posture/",
    "/why-hoax-ai-is-not-a-detector/",
    "/reference/evidence-posture/",
    "/standard/evidence-posture/",
]

ANCHORS = [
    'id="reference-summary"',
    'id="entry-purpose"',
    'id="start-here"',
    'id="recommended-path"',
    'id="reference-answer"',
    'id="source-confidence"',
    'id="cite-this-reference"',
    'id="retrieval-capsule"',
    'id="boundary"',
]

SECTION_LABELS = [
    "reference summary",
    "entry purpose",
    "start here",
    "recommended path",
    "reference answer",
    "source confidence",
    "cite this reference",
    "retrieval capsule",
    "boundary reminder",
]

FORBIDDEN_CLAIMS = [
    "real or fake",
    "fake detector",
    "ai detector",
    "detects fake",
    "verifies truth",
    "scores authenticity",
    "confidence score",
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

EXTERNAL_OPS = [
    "github pages enablement",
    "cloudflare dns",
    "deploy to production",
    "custom domain launch",
]

SOURCE_LOCS = [
    ENTRY_DOC,
    AUDIT_DOC,
    STANDARD_DOC,
    ENTRY_JSON,
    ENTRY_SCHEMA,
    SPRINT_DOC,
]

REQUIRED_LINKS = {
    "entry-points/human-readers/index.html": [
        "/manual-evidence-checklist/",
        "/evidence-risk-questions/",
        "/evidence-posture-map/",
        "/pathways/source-unclear/",
        "/pathways/context-missing/",
        "/pathways/claim-overextended/",
        "/why-hoax-ai-is-not-a-detector/",
    ],
    "entry-points/ai-agents/index.html": [
        "/evidence-risk/",
        "/claim-drift/",
        "/traceability-gap/",
        "/boundary-integrity/",
        "/not-assessable-posture/",
        "/why-hoax-ai-is-not-a-detector/",
        "/entry-points/",
    ],
    "entry-points/research-review/index.html": [
        "/evidence-risk/",
        "/provenance-risk/",
        "/source-ambiguity/",
        "/artifact-claim-gap/",
        "/evidence-weight/",
        "/interpretation-risk/",
        "/pathways/traceability-incomplete/",
        "/pathways/posture-not-assessable/",
    ],
    "entry-points/trust-safety/index.html": [
        "/claim-drift/",
        "/context-collapse/",
        "/source-ambiguity/",
        "/traceability-gap/",
        "/boundary-integrity/",
        "/not-assessable-posture/",
        "/pathways/claim-overextended/",
        "/pathways/context-missing/",
        "/why-hoax-ai-is-not-a-detector/",
    ],
    "entry-points/education-literacy/index.html": [
        "/synthetic-examples/",
        "/manual-evidence-checklist/",
        "/evidence-risk-questions/",
        "/context-collapse/",
        "/claim-drift/",
        "/interpretation-risk/",
        "/pathways/context-missing/",
        "/pathways/claim-overextended/",
    ],
}


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def visible_words(html: str) -> int:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return len(text.split())


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
    for rel in [ENTRY_DOC, AUDIT_DOC, STANDARD_DOC, ENTRY_JSON, ENTRY_SCHEMA, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(ENTRY_JSON)
    if data.get("decision_ref") != "DEC-114":
        error("decision_ref must be DEC-114")
        ok = False
    if sorted(data.get("public_routes_added", [])) != sorted(NEW_ROUTES.values()):
        error("public_routes_added must list exactly six new routes")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED:
        error("expected_sitemap_url_count_after must be 47")
        ok = False
    for flag in (
        "upload_authorized",
        "scoring_authorized",
        "verdict_authorized",
        "detector_claim_authorized",
        "public_api_authorized",
        "automated_report_authorized",
        "javascript_authorized",
        "forms_authorized",
        "real_world_case_evaluation_authorized",
        "chatbot_authorized",
        "generator_authorized",
    ):
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    for rel in [ENTRY_DOC, AUDIT_DOC, STANDARD_DOC, ENTRY_JSON, SPRINT_DOC]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in EXTERNAL_OPS:
            if term in text:
                error(f"{rel}: external operations content {term!r}")
                ok = False
    return ok


def validate_counts() -> bool:
    ok = True
    if (ROOT / "sitemap.xml").read_text(encoding="utf-8").count("<loc>") != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have exactly {PUBLIC_SITEMAP_URL_COUNT} entries")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    by_id = {r.get("route_id"): r for r in routes}
    for rid, path in zip(ROUTE_IDS, NEW_ROUTES.values()):
        if rid not in by_id:
            error(f"route registry missing {rid}")
            ok = False
        elif by_id[rid].get("path") != path:
            error(f"{rid}: path must be {path}")
            ok = False
    for rel in NEW_ROUTES:
        if not (ROOT / rel).is_file():
            error(f"missing page {rel}")
            ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    if "choose your entry point" not in lower:
        error("homepage missing Choose Your Entry Point section")
        ok = False
    for path in NEW_ROUTES.values():
        if path not in content:
            error(f"homepage missing link to {path}")
            ok = False
    return ok


def validate_page(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    if len(re.findall(r"<h1\b", content, re.I)) != 1:
        error(f"{rel}: expected exactly one H1")
        ok = False
    if 'rel="canonical"' not in lower:
        error(f"{rel}: missing canonical URL")
        ok = False
    if 'name="description"' not in lower:
        error(f"{rel}: missing meta description")
        ok = False
    if 'property="og:title"' not in lower or 'property="og:description"' not in lower:
        error(f"{rel}: missing Open Graph title/description")
        ok = False
    wc = visible_words(content)
    if wc < MIN_WORDS:
        error(f"{rel}: insufficient depth ({wc} words, need {MIN_WORDS})")
        ok = False
    for anchor in ANCHORS:
        if anchor not in content:
            error(f"{rel}: missing anchor {anchor}")
            ok = False
    for label in SECTION_LABELS:
        if label not in lower:
            error(f"{rel}: missing section {label!r}")
            ok = False
    if "/entry-points/" not in content and rel != "entry-points/index.html":
        error(f"{rel}: must link to /entry-points/")
        ok = False
    if rel != "entry-points/index.html" and 'href="/"' not in content and 'href="/"' not in content.replace(" ", ""):
        if 'href="/"' not in content:
            error(f"{rel}: must link to homepage")
            ok = False
    util_count = sum(1 for u in UTILITY_OR_PATHWAY if u in content)
    if util_count < 3:
        error(f"{rel}: must link to at least 3 utility or pathway routes")
        ok = False
    ref_count = sum(1 for r in REFERENCE_ROUTES if r in content)
    if ref_count < 5:
        error(f"{rel}: must link to at least 5 reference routes")
        ok = False
    if rel in REQUIRED_LINKS:
        for link in REQUIRED_LINKS[rel]:
            if link not in content:
                error(f"{rel}: missing required link {link}")
                ok = False
    if "<form" in lower or "<input" in lower:
        error(f"{rel}: forms/inputs forbidden")
        ok = False
    if re.search(r'<script\b(?![^>]*type=["\']application/ld\+json["\'])', content, re.I):
        error(f"{rel}: JavaScript forbidden")
        ok = False
    for claim in FORBIDDEN_CLAIMS:
        for line in content.splitlines():
            if line_has_unnegated_claim(line, claim):
                error(f"{rel}: forbidden claim {claim!r}")
                ok = False
                break
    if "page-end-reference-nav" not in content:
        error(f"{rel}: missing page-end reference navigation")
        ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-114" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-114 missing")
        ok = False
    if "validate_public_reference_strategic_entry_points_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 96 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
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
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
    ):
        error("publisher status must reflect Sprint 96 strategic entry points validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_strategic_entry_points_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0097" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0097 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0090" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0090 missing")
        ok = False
    if "Sprint 96 | COMPLETE | G96 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 96 row")
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
    if not validate_homepage():
        ok = False
    for rel in NEW_ROUTES:
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
