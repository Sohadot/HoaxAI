#!/usr/bin/env python3
"""Validate Sprint 59 — Hoax.ai Evidence Posture Standard v1 public authority layer."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
)

STANDARD_PATH = "standard/evidence-posture/index.html"
STANDARD_URL = "https://hoax.ai/standard/evidence-posture/"
STANDARD_ROUTE = "/standard/evidence-posture/"

REQUIRED_SECTIONS = [
    "Standard Statement",
    "Scope",
    "Governing Principles",
    "Evidence Posture States",
    "Evidence Support Conditions",
    "Allowed Output Language",
    "Prohibited Output Language",
    "Relationship to Reference Layer",
    "Standard Matrix",
    "Boundary Rules",
    "Institutional Usefulness",
    "Standard Versioning",
    "Hoax.ai Boundary",
    "Related Reference Pages",
]

EPS_IDS = [f"EPS-{i:03d}" for i in range(1, 15)]

POSTURE_STATES = [
    "Supported",
    "Qualified",
    "Limited",
    "Not Assessable",
    "Out of Scope",
]

REFERENCE_LINKS = [
    "/reference/evidence-posture/",
    "/reference/artifact-subject-separation/",
    "/reference/source-confidence/",
    "/reference/provenance-gap/",
    "/reference/not-assessable/",
    "/reference/output-boundary/",
    "/reference/synthetic-fragility/",
    "/reference/evidence-chain/",
    "/reference/context-collapse/",
    "/reference/claim-source-traceability/",
    "/reference/attribution-boundary/",
    "/reference/claim-drift/",
    "/reference/evidence-limitation/",
    "/reference/interpretation-risk/",
]

ALLOWED_EXAMPLES = [
    "The available evidence supports a limited posture.",
    "The source basis is not sufficient for a stronger conclusion.",
    "The evidence condition is not assessable from the available material.",
]

PROHIBITED_EXAMPLES = [
    "This is fake.",
    "This is real.",
    "This proves deception.",
    "The subject is responsible.",
]

BOUNDARY_PHRASES = [
    "artifact-subject separation",
    "output boundary",
    "evidence limitation",
    "interpretation risk",
    "claim-source traceability",
    "attribution boundary",
]

NOT_TOOL_PHRASES = [
    "public reference standard",
    "not a fake/real detector",
    "not a truth engine",
    "not a scoring system",
    "not an upload workflow",
    "not an api",
    "not a public classifier",
    "not a legal judgment system",
    "not an accusation system",
]

FORBIDDEN_PATTERNS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script[^>]+src=",
    r"upload your",
    r"scan now",
    r"scoring interface",
    r"classifier interface",
    r"detector interface",
    r"scanner interface",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_59_EVIDENCE_POSTURE_STANDARD_V1_AUDIT.md",
    "validators/validate_evidence_posture_standard_v1_public.py",
]

MIN_WORDS = 2500


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    return re.sub(r"<[^>]+>", " ", text)


def visible_word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html)))


def validate_standard_page() -> bool:
    ok = True
    path = ROOT / STANDARD_PATH
    if not path.is_file():
        error(f"missing {STANDARD_PATH}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    if text.count("<h1") != 1:
        error("standard page must have exactly one H1")
        ok = False
    if STANDARD_URL not in text:
        error("standard page missing canonical URL")
        ok = False
    if "<title>" not in text or 'name="description"' not in text:
        error("standard page missing title or meta description")
        ok = False
    for section in REQUIRED_SECTIONS:
        if section not in text:
            error(f"standard page missing section: {section}")
            ok = False
    for eps in EPS_IDS:
        if eps not in text:
            error(f"standard page missing {eps}")
            ok = False
    for state in POSTURE_STATES:
        if state not in text:
            error(f"standard page missing posture state: {state}")
            ok = False
    for link in REFERENCE_LINKS:
        if link not in text:
            error(f"standard page missing link to {link}")
            ok = False
    for phrase in ALLOWED_EXAMPLES:
        if phrase.lower() not in lower:
            error(f"standard page missing allowed example: {phrase}")
            ok = False
    for phrase in PROHIBITED_EXAMPLES:
        if phrase.lower() not in lower:
            error(f"standard page missing prohibited example: {phrase}")
            ok = False
    for phrase in BOUNDARY_PHRASES:
        if phrase not in lower:
            error(f"standard page missing boundary phrase: {phrase}")
            ok = False
    for phrase in NOT_TOOL_PHRASES:
        if phrase not in lower:
            error(f"standard page missing positioning phrase: {phrase}")
            ok = False
    wc = visible_word_count(text)
    if wc < MIN_WORDS:
        error(f"standard page insufficient depth ({wc} words, need {MIN_WORDS})")
        ok = False
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.I):
            error(f"standard page forbidden pattern: {pat}")
            ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    standard_routes = [r for r in routes if r.get("path") == STANDARD_ROUTE]
    if len(standard_routes) != 1:
        error("route registry must include exactly one standard route at /standard/evidence-posture/")
        ok = False
    elif standard_routes[0].get("route_id") != "ROUTE-0017":
        error("standard route must be ROUTE-0017")
        ok = False
    extra_standard = [r for r in routes if r.get("path", "").startswith("/standard/") and r.get("path") != STANDARD_ROUTE]
    if extra_standard:
        error("no additional standard routes beyond /standard/evidence-posture/")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
        ok = False
    if STANDARD_URL not in locs:
        error("sitemap missing standard URL")
        ok = False
    pat = re.compile(
        r"internal_prototypes|evidence-posture-workbench|/workbench/|/tool/|/classifier/|/detector/|/upload/|/score/",
        re.I,
    )
    if pat.search((ROOT / STANDARD_PATH).read_text(encoding="utf-8")):
        error("standard page prototype or blocked route leak")
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
    if "DEC-077" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-077 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_59_EVIDENCE_POSTURE_STANDARD_V1_AUDIT.md").is_file():
        error("Sprint 59 audit missing")
        ok = False
    if "validate_evidence_posture_standard_v1_public.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 59 validator")
        ok = False
    policy = json.loads((ROOT / "data/publisher-governance-policy.json").read_text(encoding="utf-8"))
    if policy.get("current_publisher_status") not in (
        "blocked_until_evidence_posture_standard_v1_validation",
        "blocked_until_evidence_posture_protocol_v1_draft_validation",
        "blocked_until_public_interface_thesis_evidence_field_validation",
        "blocked_until_evidence_field_static_interface_embodiment_v1_validation",
        "blocked_until_evidence_field_visual_system_accessibility_hardening_validation",
        "blocked_until_controlled_domain_connection_decision",
        "blocked_until_engine_boundary_and_public_reference_seo_authority_map_validation",
        "blocked_until_evidence_posture_engine_model_v0_validation",
        "blocked_until_output_language_guardrail_model_v1_validation",
        "blocked_until_internal_non_public_engine_prototype_charter_validation",
        "blocked_until_controlled_internal_prototype_v0_implementation_sprint",
        "blocked_until_controlled_internal_prototype_v0_validation",
        "blocked_until_controlled_internal_prototype_v0_hardening_validation",
        "blocked_until_internal_prototype_traceability_interpretability_audit_validation",
        "blocked_until_internal_prototype_fixture_coverage_matrix_validation",
        "blocked_until_targeted_synthetic_fixture_expansion_v1_validation",
        "blocked_until_internal_prototype_compound_boundary_stress_test_validation",
        "blocked_until_internal_prototype_guardrail_red_team_pack_validation",
        "blocked_until_public_reference_route_expansion_validation",
        "blocked_until_public_utility_interface_embodiment_validation",
        "blocked_until_public_reference_authority_internal_linking_validation",
        "blocked_until_public_reference_source_confidence_layer_validation",
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
        "blocked_until_public_reference_executive_overview_surface_validation",
        "blocked_until_public_reference_executive_overview_integrity_audit_validation",
        "blocked_until_public_reference_strategic_review_index_validation",
        "blocked_until_public_reference_strategic_review_index_integrity_audit_validation",
        "blocked_until_public_reference_system_map_surface_validation",        PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,

    ):
        error("publisher status must be blocked_until_evidence_posture_standard_v1_validation or protocol v1 draft validation")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0063" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0063 missing")
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
    ok = all(fn() for fn in [validate_standard_page, validate_surface, validate_governance, validate_cache])
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
