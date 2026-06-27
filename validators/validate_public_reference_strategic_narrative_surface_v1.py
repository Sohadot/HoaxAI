#!/usr/bin/env python3
"""Validate Sprint 97 — Public Reference Strategic Narrative Surface v1."""

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
    validate_public_surface,
)

NARRATIVE_DOC = "PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_AUDIT_V1.md"
STANDARD_DOC = "PUBLIC_STRATEGIC_NARRATIVE_STANDARD_V1.md"
NARRATIVE_JSON = "data/public-reference-strategic-narrative-surface-v1.json"
NARRATIVE_SCHEMA = "data/public-reference-strategic-narrative-surface-v1.schema.json"
SPRINT_DOC = "SPRINT_97_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_V1.md"
INDEX = "index.html"
EXPECTED = 52
MIN_WORDS = 850

NEW_ROUTES = {
    "narrative/index.html": "/narrative/",
    "narrative/evidence-before-verdict/index.html": "/narrative/evidence-before-verdict/",
    "narrative/why-evidence-risk/index.html": "/narrative/why-evidence-risk/",
    "narrative/reference-before-detection/index.html": "/narrative/reference-before-detection/",
    "narrative/non-verdict-trust/index.html": "/narrative/non-verdict-trust/",
}

ROUTE_IDS = [f"ROUTE-{i:04d}" for i in range(48, 53)]

NARRATIVE_SIBLING_PATHS = [
    "/narrative/",
    "/narrative/evidence-before-verdict/",
    "/narrative/why-evidence-risk/",
    "/narrative/reference-before-detection/",
    "/narrative/non-verdict-trust/",
]

UTILITY_PATHWAY_OR_ENTRY = [
    "/manual-evidence-checklist/",
    "/evidence-posture-map/",
    "/evidence-risk-questions/",
    "/pathways/source-unclear/",
    "/pathways/provenance-weak/",
    "/pathways/context-missing/",
    "/pathways/claim-overextended/",
    "/pathways/traceability-incomplete/",
    "/pathways/posture-not-assessable/",
    "/entry-points/human-readers/",
    "/entry-points/ai-agents/",
    "/entry-points/research-review/",
    "/entry-points/trust-safety/",
    "/entry-points/education-literacy/",
]

REFERENCE_ROUTES = [
    "/evidence-risk/",
    "/provenance-risk/",
    "/context-collapse/",
    "/claim-drift/",
    "/traceability-gap/",
    "/source-ambiguity/",
    "/boundary-integrity/",
    "/evidence-weight/",
    "/interpretation-risk/",
    "/not-assessable-posture/",
    "/why-hoax-ai-is-not-a-detector/",
    "/source-confidence/",
    "/reference/evidence-posture/",
    "/standard/evidence-posture/",
]

ANCHORS = [
    'id="reference-summary"',
    'id="narrative-purpose"',
    'id="category-frame"',
    'id="strategic-thesis"',
    'id="reference-answer"',
    'id="source-confidence"',
    'id="cite-this-reference"',
    'id="retrieval-capsule"',
    'id="boundary"',
]

SECTION_LABELS = [
    "reference summary",
    "narrative purpose",
    "category frame",
    "strategic thesis",
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
    NARRATIVE_DOC,
    AUDIT_DOC,
    STANDARD_DOC,
    NARRATIVE_JSON,
    NARRATIVE_SCHEMA,
    SPRINT_DOC,
]

REQUIRED_LINKS = {
    "narrative/index.html": [
        "/entry-points/",
        "/manual-evidence-checklist/",
        "/evidence-risk/",
        "/claim-drift/",
        "/boundary-integrity/",
        "/why-hoax-ai-is-not-a-detector/",
        "/narrative/evidence-before-verdict/",
        "/narrative/why-evidence-risk/",
        "/narrative/reference-before-detection/",
        "/narrative/non-verdict-trust/",
    ],
    "narrative/evidence-before-verdict/index.html": [
        "/evidence-posture-map/",
        "/manual-evidence-checklist/",
        "/evidence-risk-questions/",
        "/boundary-integrity/",
        "/not-assessable-posture/",
        "/pathways/posture-not-assessable/",
    ],
    "narrative/why-evidence-risk/index.html": [
        "/evidence-risk/",
        "/source-ambiguity/",
        "/provenance-risk/",
        "/context-collapse/",
        "/claim-drift/",
        "/traceability-gap/",
        "/interpretation-risk/",
    ],
    "narrative/reference-before-detection/index.html": [
        "/why-hoax-ai-is-not-a-detector/",
        "/entry-points/ai-agents/",
        "/evidence-risk/",
        "/boundary-integrity/",
        "/not-assessable-posture/",
        "/narrative/non-verdict-trust/",
    ],
    "narrative/non-verdict-trust/index.html": [
        "/not-assessable-posture/",
        "/boundary-integrity/",
        "/evidence-weight/",
        "/source-confidence/",
        "/entry-points/research-review/",
        "/entry-points/trust-safety/",
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
    for rel in [NARRATIVE_DOC, AUDIT_DOC, STANDARD_DOC, NARRATIVE_JSON, NARRATIVE_SCHEMA, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(NARRATIVE_JSON)
    if data.get("decision_ref") != "DEC-115":
        error("decision_ref must be DEC-115")
        ok = False
    if sorted(data.get("public_routes_added", [])) != sorted(NEW_ROUTES.values()):
        error("public_routes_added must list exactly five new routes")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED:
        error("expected_sitemap_url_count_after must be 52")
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
    for rel in [NARRATIVE_DOC, AUDIT_DOC, STANDARD_DOC, NARRATIVE_JSON, SPRINT_DOC]:
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
    if "the strategic narrative" not in lower:
        error("homepage missing The Strategic Narrative section")
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
    own_path = NEW_ROUTES[rel]
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
    if "/entry-points/" not in content:
        error(f"{rel}: must link to /entry-points/")
        ok = False
    if 'href="/"' not in content:
        error(f"{rel}: must link to homepage")
        ok = False
    util_count = sum(1 for u in UTILITY_PATHWAY_OR_ENTRY if u in content)
    if util_count < 3:
        error(f"{rel}: must link to at least 3 utility, pathway, or entry-point routes")
        ok = False
    ref_count = sum(1 for r in REFERENCE_ROUTES if r in content)
    if ref_count < 5:
        error(f"{rel}: must link to at least 5 reference routes")
        ok = False
    sibling_count = sum(1 for s in NARRATIVE_SIBLING_PATHS if s in content and s != own_path)
    if sibling_count < 2:
        error(f"{rel}: must link to at least 2 sibling narrative routes")
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
    if "DEC-115" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-115 missing")
        ok = False
    if "validate_public_reference_strategic_narrative_surface_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 97 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,

    ):
        error("publisher status must reflect Sprint 97 strategic narrative surface validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_strategic_narrative_surface_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0098" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0098 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0091" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0091 missing")
        ok = False
    if "Sprint 97 | COMPLETE | G97 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 97 row")
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
