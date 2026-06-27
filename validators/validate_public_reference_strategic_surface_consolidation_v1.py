#!/usr/bin/env python3
"""Validate Sprint 99 — Public Reference Strategic Surface Consolidation v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
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
    validate_public_surface,
)

CONSOLIDATION_DOC = "PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_AUDIT_V1.md"
STANDARD_DOC = "PUBLIC_STRATEGIC_SURFACE_CONSOLIDATION_STANDARD_V1.md"
REPAIR_DOC = "PUBLIC_REFERENCE_STRATEGIC_SURFACE_REPAIR_LOG_V1.md"
CONSOLIDATION_JSON = "data/public-reference-strategic-surface-consolidation-v1.json"
CONSOLIDATION_SCHEMA = "data/public-reference-strategic-surface-consolidation-v1.schema.json"
SPRINT_DOC = "SPRINT_99_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_V1.md"
INDEX = "index.html"
EXPECTED = 58

ENTRY_PAGES = [
    "entry-points/index.html",
    "entry-points/human-readers/index.html",
    "entry-points/ai-agents/index.html",
    "entry-points/research-review/index.html",
    "entry-points/trust-safety/index.html",
    "entry-points/education-literacy/index.html",
]

NARRATIVE_PAGES = [
    "narrative/index.html",
    "narrative/evidence-before-verdict/index.html",
    "narrative/why-evidence-risk/index.html",
    "narrative/reference-before-detection/index.html",
    "narrative/non-verdict-trust/index.html",
]

READINESS_PAGES = [
    "acquisition-readiness/index.html",
    "acquisition-readiness/category-asset/index.html",
    "acquisition-readiness/public-reference-surface/index.html",
    "acquisition-readiness/governance-traceability/index.html",
    "acquisition-readiness/ai-retrieval-readiness/index.html",
    "acquisition-readiness/non-detector-moat/index.html",
]

STRATEGIC_PAGES = ENTRY_PAGES + NARRATIVE_PAGES + READINESS_PAGES

NARRATIVE_PATHS = [
    "/narrative/",
    "/narrative/evidence-before-verdict/",
    "/narrative/why-evidence-risk/",
    "/narrative/reference-before-detection/",
    "/narrative/non-verdict-trust/",
]

READINESS_PATHS = [
    "/acquisition-readiness/",
    "/acquisition-readiness/category-asset/",
    "/acquisition-readiness/public-reference-surface/",
    "/acquisition-readiness/governance-traceability/",
    "/acquisition-readiness/ai-retrieval-readiness/",
    "/acquisition-readiness/non-detector-moat/",
]

ENTRY_PATHS = [
    "/entry-points/",
    "/entry-points/human-readers/",
    "/entry-points/ai-agents/",
    "/entry-points/research-review/",
    "/entry-points/trust-safety/",
    "/entry-points/education-literacy/",
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
    "for sale",
    "asking price",
    "valuation",
    "term sheet",
    "broker representation",
    "sale offer",
    "acquisition terms available",
    "contact to buy",
    "make an offer",
    "purchase this domain",
    "price available",
    "listed for sale",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not)\s+[\w\s\-/]{0,50}",
    re.IGNORECASE,
)

NON_TX_SNIPPET = "public reference-readiness page"

EXTERNAL_OPS = [
    "github pages enablement",
    "cloudflare dns",
    "deploy to production",
    "custom domain launch",
]

SOURCE_LOCS = [
    CONSOLIDATION_DOC,
    AUDIT_DOC,
    STANDARD_DOC,
    REPAIR_DOC,
    CONSOLIDATION_JSON,
    CONSOLIDATION_SCHEMA,
    SPRINT_DOC,
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
        if claim == "valuation" and idx > 0 and lower[idx - 1] == "e":
            pos = idx + len(claim)
            continue
        prefix = lower[max(0, idx - 80) : idx]
        if not NEGATION_PATTERN.search(prefix + claim):
            return True
        pos = idx + len(claim)
    return False


def validate_artifacts() -> bool:
    ok = True
    for rel in [CONSOLIDATION_DOC, AUDIT_DOC, STANDARD_DOC, REPAIR_DOC, CONSOLIDATION_JSON, CONSOLIDATION_SCHEMA, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    data = load_json(CONSOLIDATION_JSON)
    if data.get("decision_ref") != "DEC-117":
        error("decision_ref must be DEC-117")
        ok = False
    if data.get("new_public_routes_added") is not False:
        error("new_public_routes_added must be false")
        ok = False
    if data.get("expected_sitemap_url_count_after") != EXPECTED:
        error("expected_sitemap_url_count_after must be 58")
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
        "pricing_statement_authorized",
        "transaction_page_authorized",
        "acquisition_term_document_authorized",
        "representative_mandate_authorized",
        "legal_representation_authorized",
        "financial_representation_authorized",
    ):
        if data.get(flag) is not False:
            error(f"{flag} must be false")
            ok = False
    for rel in [CONSOLIDATION_DOC, AUDIT_DOC, STANDARD_DOC, REPAIR_DOC, CONSOLIDATION_JSON, SPRINT_DOC]:
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
    data = load_json(CONSOLIDATION_JSON)
    if data.get("expected_sitemap_url_count_after") != 58:
        error("historical expected_sitemap_url_count_after must remain 58 for Sprint 99")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    return ok


def validate_homepage() -> bool:
    ok = True
    content = (ROOT / INDEX).read_text(encoding="utf-8")
    lower = content.lower()
    checks = [
        ("strategic surface map", "Strategic Surface Map"),
        ("/entry-points/", "/entry-points/"),
        ("/narrative/", "/narrative/"),
        ("/acquisition-readiness/", "/acquisition-readiness/"),
        ("enter hoax.ai", "Enter Hoax.ai"),
        ("understand the category", "Understand the Category"),
        ("inspect the public reference asset", "Inspect the Public Reference Asset"),
        ("human reader path", "Human Reader Path"),
        ("ai retrieval path", "AI Retrieval Path"),
        ("strategic review path", "Strategic Review Path"),
        ("non-transactional review surface", "non-transactional review surface"),
    ]
    for needle, label in checks:
        if needle not in lower:
            error(f"homepage missing {label}")
            ok = False
    return ok


def validate_strategic_page(rel: str) -> bool:
    ok = True
    content = (ROOT / rel).read_text(encoding="utf-8")
    lower = content.lower()
    if "hoax.ai strategic surface navigation" not in lower:
        error(f"{rel}: missing Hoax.ai Strategic Surface Navigation")
        ok = False
    if "strategic surface capsule" not in lower:
        error(f"{rel}: missing Strategic Surface Capsule")
        ok = False
    if "strategic next step" not in lower:
        error(f"{rel}: missing Strategic next step")
        ok = False
    if 'id="strategic-surface-navigation"' not in content:
        error(f"{rel}: missing strategic-surface-navigation anchor")
        ok = False
    if 'id="strategic-surface-capsule"' not in content:
        error(f"{rel}: missing strategic-surface-capsule anchor")
        ok = False
    if 'id="strategic-next-step"' not in content:
        error(f"{rel}: missing strategic-next-step anchor")
        ok = False

    if rel in ENTRY_PAGES:
        if "/narrative/" not in content or "/acquisition-readiness/" not in content:
            error(f"{rel}: entry point must link to narrative and readiness hubs")
            ok = False
        if sum(1 for p in NARRATIVE_PATHS if p in content) < 2:
            error(f"{rel}: entry point needs 2+ narrative links")
            ok = False
        if sum(1 for p in READINESS_PATHS if p in content) < 2:
            error(f"{rel}: entry point needs 2+ readiness links")
            ok = False
    if rel in NARRATIVE_PAGES:
        if "/entry-points/" not in content or "/acquisition-readiness/" not in content:
            error(f"{rel}: narrative must link to entry points and readiness hubs")
            ok = False
        if sum(1 for p in ENTRY_PATHS if p in content) < 2:
            error(f"{rel}: narrative needs 2+ entry-point links")
            ok = False
        if sum(1 for p in READINESS_PATHS if p in content) < 2:
            error(f"{rel}: narrative needs 2+ readiness links")
            ok = False
    if rel in READINESS_PAGES:
        if "/entry-points/" not in content or "/narrative/" not in content:
            error(f"{rel}: readiness must link to entry points and narrative hubs")
            ok = False
        if sum(1 for p in ENTRY_PATHS if p in content) < 2:
            error(f"{rel}: readiness needs 2+ entry-point links")
            ok = False
        if sum(1 for p in NARRATIVE_PATHS if p in content) < 2:
            error(f"{rel}: readiness needs 2+ narrative links")
            ok = False
        if NON_TX_SNIPPET not in lower:
            error(f"{rel}: missing non-transactional review boundary wording")
            ok = False
    return ok


def validate_public_html(rel: str) -> bool:
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
    return ok


def validate_governance() -> bool:
    ok = True
    if "DEC-117" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-117 missing")
        ok = False
    if "validate_public_reference_strategic_surface_consolidation_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 99 validator")
        ok = False
    policy = load_json("data/publisher-governance-policy.json")
    if policy.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,

    ):
        error("publisher status must reflect Sprint 99 consolidation validation")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS + ["validators/validate_public_reference_strategic_surface_consolidation_v1.py"]:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0100" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0100 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0093" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0093 missing")
        ok = False
    if "Sprint 99 | COMPLETE | G99 passed" not in (ROOT / "MASTER_EXECUTION_PLAN.md").read_text(encoding="utf-8"):
        error("master execution plan missing Sprint 99 row")
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
    for rel in STRATEGIC_PAGES:
        if not validate_strategic_page(rel):
            ok = False
    for rel in sorted(ALLOWED_PUBLIC_HTML):
        if not validate_public_html(rel):
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
