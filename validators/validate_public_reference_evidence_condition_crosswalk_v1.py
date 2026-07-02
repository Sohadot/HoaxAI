#!/usr/bin/env python3
"""Validate Sprint 115 — Public Reference Evidence Condition Crosswalk v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (  # noqa: E402
    ALLOWED_PUBLIC_HTML,
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
)

INDEX_DOC = "PUBLIC_REFERENCE_EVIDENCE_CONDITION_CROSSWALK_V1.md"
AUDIT_DOC = "PUBLIC_REFERENCE_EVIDENCE_CONDITION_CROSSWALK_AUDIT_V1.md"
STANDARD_DOC = "PUBLIC_EVIDENCE_CONDITION_CROSSWALK_STANDARD_V1.md"
INDEX_JSON = "data/public-reference-evidence-condition-crosswalk-v1.json"
INDEX_SCHEMA = "data/public-reference-evidence-condition-crosswalk-v1.schema.json"
SPRINT_DOC = "SPRINT_115_PUBLIC_REFERENCE_EVIDENCE_CONDITION_CROSSWALK_V1.md"
INDEX = "index.html"
MAP_HUB = "system-map/index.html"
HUB = "evidence-conditions/index.html"
CROSSWALK_PAGE = "evidence-conditions/crosswalk/index.html"
CROSSWALK_PATH = "/evidence-conditions/crosswalk/"
MIN_WORDS = 1400

CONDITION_PATHS = [
    "/evidence-conditions/source-uncertainty/",
    "/evidence-conditions/provenance-discontinuity/",
    "/evidence-conditions/context-loss/",
    "/evidence-conditions/claim-evidence-misalignment/",
    "/evidence-conditions/traceability-break/",
]

ROUTE_GROUP_PAGES = [
    "route-groups/core-concepts/index.html",
    "route-groups/evidence-risk-pathways/index.html",
    "route-groups/boundary-and-support-references/index.html",
]

AUDIENCE_PATH_PAGES = [
    "audience-paths/research-reviewers/index.html",
    "audience-paths/trust-safety-readers/index.html",
    "audience-paths/education-literacy/index.html",
    "audience-paths/ai-agents/index.html",
]

REQUIRED_SECTIONS = [
    "Reference summary",
    "Crosswalk purpose",
    "How to read this crosswalk",
    "Evidence condition recap",
    "Condition × core concept relation",
    "Condition × evidence-risk pathway relation",
    "Condition × route-group relation",
    "Condition × audience-path relation",
    "Condition × boundary-language relation",
    "Condition × confusion-prevention relation",
    "Condition × AI retrieval instruction",
    "What this crosswalk supports",
    "What this crosswalk does not claim",
    "Reference Answer",
    "Source Confidence",
    "Cite This Reference",
    "Retrieval Capsule",
    "Strategic reference value",
    "Boundary reminder",
    "Non-transactional review boundary",
]

REQUIRED_ANCHORS = [
    "reference-summary",
    "crosswalk-purpose",
    "how-to-read",
    "condition-recap",
    "condition-core-concepts",
    "condition-pathways",
    "condition-route-groups",
    "condition-audience-paths",
    "condition-boundary-language",
    "condition-confusion-prevention",
    "condition-ai-retrieval",
    "what-supports",
    "does-not-claim",
    "reference-answer",
    "source-confidence",
    "cite-this-reference",
    "retrieval-capsule",
    "strategic-reference-value",
    "boundary",
    "non-transactional-boundary",
]

ALLOWED_RELATION_LABELS = [
    "directly relevant",
    "contextually relevant",
    "boundary-sensitive",
    "retrieval-supporting",
    "confusion-preventing",
    "adjacent reference",
]

# Forbidden relation/verdict terms; allowed only inside explicit negation or
# prohibition language on the crosswalk page.
FORBIDDEN_RELATION_TERMS = [
    "high risk",
    "medium risk",
    "low risk",
    "severity",
    "confidence score",
    "verified",
    "detected",
    "confirmed",
    "manipulated",
    "fraudulent",
    "deceptive",
    "authentic",
    "inauthentic",
]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without|not|prohibition|prohibited|forbidden)"
    r"\s+[\w\s\-/,]{0,80}",
    re.IGNORECASE,
)

REQUIRED_COMPONENTS = [
    "reference_summary",
    "crosswalk_purpose",
    "how_to_read_this_crosswalk",
    "evidence_condition_recap",
    "condition_core_concept_relation",
    "condition_evidence_risk_pathway_relation",
    "condition_route_group_relation",
    "condition_audience_path_relation",
    "condition_boundary_language_relation",
    "condition_confusion_prevention_relation",
    "condition_ai_retrieval_instruction",
    "what_this_crosswalk_supports",
    "what_this_crosswalk_does_not_claim",
    "reference_answer",
    "source_confidence",
    "cite_this_reference",
    "retrieval_capsule",
    "strategic_reference_value",
    "page_end_reference_navigation",
    "boundary_reminder",
    "non_transactional_review_boundary",
]

SOURCE_LOCS = [INDEX_DOC, AUDIT_DOC, STANDARD_DOC, INDEX_JSON, INDEX_SCHEMA, SPRINT_DOC]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def visible_words(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def term_has_unnegated_use(html: str, term: str) -> bool:
    lower = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).lower()
    pos = 0
    while True:
        idx = lower.find(term, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 140): idx]
        if NEGATION_PATTERN.search(prefix + term):
            pos = idx + len(term)
            continue
        return True


def validate_docs() -> bool:
    ok = True
    for rel in [INDEX_DOC, AUDIT_DOC, STANDARD_DOC, SPRINT_DOC]:
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            ok = False
    doc = (ROOT / INDEX_DOC).read_text(encoding="utf-8")
    for needle in (
        "Evidence Condition Crosswalk Statement",
        "DEC-133",
        CROSSWALK_PATH,
        "does not rank, score, verify, detect, or adjudicate",
    ):
        if needle not in doc:
            error(f"{INDEX_DOC}: missing {needle!r}")
            ok = False
    std = (ROOT / STANDARD_DOC).read_text(encoding="utf-8")
    for needle in (
        "Evidence Condition Crosswalk Standard Statement",
        "Required page structure",
        "Minimum depth requirement",
        "Relation language requirements",
        "Thin-page prevention rules",
    ):
        if needle not in std:
            error(f"{STANDARD_DOC}: missing {needle!r}")
            ok = False
    return ok


def validate_data_json() -> bool:
    ok = True
    try:
        data = load_json(INDEX_JSON)
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{INDEX_JSON} unreadable: {exc}")
        return False
    try:
        load_json(INDEX_SCHEMA)
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{INDEX_SCHEMA} unreadable: {exc}")
        ok = False
    if data.get("decision_ref") != "DEC-133":
        error("decision_ref must be DEC-133")
        ok = False
    if data.get("sprint") != "Sprint 115":
        error("sprint must be Sprint 115")
        ok = False
    if data.get("status") != "public_reference_evidence_condition_crosswalk":
        error("status must be public_reference_evidence_condition_crosswalk")
        ok = False
    if data.get("public_routes_added") != [CROSSWALK_PATH]:
        error("public_routes_added must list exactly the crosswalk route")
        ok = False
    if data.get("expected_sitemap_url_count_after") != 100:
        error("expected_sitemap_url_count_after must be 100")
        ok = False
    if data.get("expected_route_registry_count_after") != 100:
        error("expected_route_registry_count_after must be 100")
        ok = False
    if sorted(data.get("conditions_related", [])) != sorted(CONDITION_PATHS):
        error("conditions_related must list exactly the five condition routes")
        ok = False
    if data.get("minimum_visible_words", 0) < MIN_WORDS:
        error(f"minimum_visible_words must be at least {MIN_WORDS}")
        ok = False
    if sorted(data.get("allowed_relation_labels", [])) != sorted(ALLOWED_RELATION_LABELS):
        error("allowed_relation_labels must match the six non-ranking labels")
        ok = False
    missing = [c for c in REQUIRED_COMPONENTS if c not in data.get("required_components", [])]
    if missing:
        error(f"required_components missing: {missing}")
        ok = False
    for flag in ("non_ranking", "non_verdict", "non_transactional_review_surface"):
        if data.get(flag) is not True:
            error(f"{flag} must be true")
            ok = False
    for key, value in data.items():
        if key.endswith("_authorized") and value is not False:
            error(f"{key} must be false")
            ok = False
    return ok


def validate_registries() -> bool:
    ok = True
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {len(locs)}")
        ok = False
    if f"https://hoax.ai{CROSSWALK_PATH}" not in locs:
        error("sitemap missing crosswalk URL")
        ok = False
    routes = load_json("data/route-registry.json").get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must have {PUBLIC_SITEMAP_URL_COUNT} entries, found {len(routes)}")
        ok = False
    entry = next((r for r in routes if r.get("route_id") == "ROUTE-0100"), None)
    if entry is None:
        error("route registry missing ROUTE-0100")
        ok = False
    elif entry.get("path") != CROSSWALK_PATH:
        error("ROUTE-0100 path must be the crosswalk route")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    files = load_json("data/public-file-registry.json").get("public_files", [])
    entry = next((f for f in files if f.get("file_id") == "PUB-FILE-0100"), None)
    if entry is None:
        error("public-file-registry missing PUB-FILE-0100")
        ok = False
    elif entry.get("path") != CROSSWALK_PAGE:
        error("PUB-FILE-0100 path must be the crosswalk page")
        ok = False
    return ok


def validate_navigation() -> bool:
    ok = True
    home = (ROOT / INDEX).read_text(encoding="utf-8")
    if CROSSWALK_PATH not in home:
        error("homepage must link to the crosswalk")
        ok = False
    if f"Current public route count: {PUBLIC_SITEMAP_URL_COUNT}" not in home:
        error(f"homepage snapshot must include Current public route count: {PUBLIC_SITEMAP_URL_COUNT}")
        ok = False
    hub = (ROOT / HUB).read_text(encoding="utf-8")
    if CROSSWALK_PATH not in hub:
        error("evidence-conditions hub must link to the crosswalk")
        ok = False
    system_map = (ROOT / MAP_HUB).read_text(encoding="utf-8")
    if "Evidence Condition Library Layer" not in system_map:
        error("/system-map/ must include Evidence Condition Library Layer")
        ok = False
    if CROSSWALK_PATH not in system_map:
        error("/system-map/ must link to the crosswalk")
        ok = False
    for rel in ROUTE_GROUP_PAGES + AUDIENCE_PATH_PAGES:
        if CROSSWALK_PATH not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel} must link to the crosswalk")
            ok = False
    return ok


def validate_crosswalk_page() -> bool:
    ok = True
    page = ROOT / CROSSWALK_PAGE
    if not page.is_file():
        error(f"{CROSSWALK_PAGE} missing")
        return False
    content = page.read_text(encoding="utf-8")
    if len(re.findall(r"<h1[ >]", content)) != 1:
        error(f"{CROSSWALK_PAGE}: expected exactly one H1")
        ok = False
    lower = content.lower()
    for field in ('rel="canonical"', "<title>", 'name="description"', "og:title", "og:description"):
        if field.lower() not in lower:
            error(f"{CROSSWALK_PAGE}: missing {field}")
            ok = False
    if f'href="https://hoax.ai{CROSSWALK_PATH}"' not in content:
        error(f"{CROSSWALK_PAGE}: canonical URL must be the crosswalk route")
        ok = False
    if visible_words(content) < MIN_WORDS:
        error(f"{CROSSWALK_PAGE}: fewer than {MIN_WORDS} visible words")
        ok = False
    for section in REQUIRED_SECTIONS:
        if section not in content:
            error(f"{CROSSWALK_PAGE}: missing section {section!r}")
            ok = False
    for anchor in REQUIRED_ANCHORS:
        if f'id="{anchor}"' not in content:
            error(f"{CROSSWALK_PAGE}: missing anchor {anchor}")
            ok = False
    for label in ALLOWED_RELATION_LABELS:
        if label not in lower:
            error(f"{CROSSWALK_PAGE}: missing relation label {label!r}")
            ok = False
    for term in FORBIDDEN_RELATION_TERMS:
        if term_has_unnegated_use(content, term):
            error(f"{CROSSWALK_PAGE}: forbidden relation term {term!r} used outside negation")
            ok = False
    for path in CONDITION_PATHS + ["/evidence-conditions/", "/system-map/", 'href="/"']:
        needle = path if path.startswith("href=") else f'href="{path}"'
        if needle not in content:
            error(f"{CROSSWALK_PAGE}: missing link {path}")
            ok = False
    group_links = sum(1 for p in ("/route-groups/", "/audience-paths/") if p in content)
    if group_links < 2:
        error(f"{CROSSWALK_PAGE}: must link to route-group and audience-path pages")
        ok = False
    for pattern, label in (
        ("<script", "JavaScript"),
        ("<form", "form"),
        ("<input", "input field"),
        ("<textarea", "textarea"),
        ("<select", "select"),
        ("<button", "button"),
    ):
        if pattern in lower:
            error(f"{CROSSWALK_PAGE}: contains {label}")
            ok = False
    return ok


def validate_governance() -> bool:
    ok = True
    log = (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8")
    if "DEC-133" not in log:
        error("DEC-133 missing")
        ok = False
    if log.find("DEC-132") > log.find("DEC-133"):
        error("DECISION_LOG chronology invalid: DEC-133 must follow DEC-132")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0116" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0116 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0109" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0109 missing")
        ok = False
    if "validate_public_reference_evidence_condition_crosswalk_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include the Sprint 115 validator")
        ok = False
    return ok


def validate_hygiene() -> bool:
    ok = True
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll exists")
        ok = False
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    names += subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        if "__pycache__" in rel or rel.endswith(".pyc"):
            error(f"python cache file tracked or staged: {rel}")
            ok = False
    return ok


def main() -> int:
    ok = True
    for check in (
        validate_docs,
        validate_data_json,
        validate_registries,
        validate_navigation,
        validate_crosswalk_page,
        validate_governance,
        validate_hygiene,
    ):
        if not check():
            ok = False
    if not ok:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
