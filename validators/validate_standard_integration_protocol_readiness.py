#!/usr/bin/env python3
"""Validate Sprint 60 — Standard Integration, Cross-Linking, and Protocol Readiness."""

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

STANDARD_PATH = "standard/evidence-posture/index.html"
STANDARD_LINK = "/standard/evidence-posture/"
PROTOCOL_DOC = "STANDARD_TO_PROTOCOL_READINESS.md"

REFERENCE_INTEGRATION = {
    "reference/evidence-posture/index.html": {
        "eps": "EPS-001",
        "phrase": "Evidence Posture contributes",
    },
    "reference/artifact-subject-separation/index.html": {
        "eps": "EPS-002",
        "phrase": "Artifact–Subject Separation contributes",
    },
    "reference/source-confidence/index.html": {
        "eps": "EPS-003",
        "phrase": "Source Confidence contributes",
    },
    "reference/provenance-gap/index.html": {
        "eps": "EPS-004",
        "phrase": "Provenance Gap contributes",
    },
    "reference/not-assessable/index.html": {
        "eps": "EPS-005",
        "phrase": "Not Assessable contributes",
    },
    "reference/output-boundary/index.html": {
        "eps": "EPS-006",
        "phrase": "Output Boundary contributes",
    },
    "reference/claim-source-traceability/index.html": {
        "eps": "EPS-007",
        "phrase": "Claim–Source Traceability contributes",
    },
    "reference/synthetic-fragility/index.html": {
        "eps": "EPS-008",
        "phrase": "Synthetic Fragility contributes",
    },
    "reference/context-collapse/index.html": {
        "eps": "EPS-009",
        "phrase": "Context Collapse contributes",
    },
    "reference/evidence-chain/index.html": {
        "eps": "EPS-010",
        "phrase": "Evidence Chain contributes",
    },
    "reference/claim-drift/index.html": {
        "eps": "EPS-011",
        "phrase": "Claim Drift contributes",
    },
    "reference/evidence-limitation/index.html": {
        "eps": "EPS-012",
        "phrase": "Evidence Limitation contributes",
    },
    "reference/interpretation-risk/index.html": {
        "eps": "EPS-013",
        "phrase": "Interpretation Risk contributes",
    },
    "reference/attribution-boundary/index.html": {
        "eps": "EPS-014",
        "phrase": "Attribution Boundary contributes",
    },
}

STANDARD_SECTIONS = [
    "Reference Layer Dependencies",
    "How to Read This Standard",
    "Protocol Readiness",
    "Not an Operational Engine",
    "Future Protocol Boundary",
]

FORBIDDEN_PATTERNS = [
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<button\b",
    r"<script[^>]+src=",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    "SPRINT_60_STANDARD_INTEGRATION_PROTOCOL_READINESS_AUDIT.md",
    "validators/validate_standard_integration_protocol_readiness.py",
    "STANDARD_TO_PROTOCOL_READINESS.md",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def validate_reference_integration() -> bool:
    ok = True
    for rel, spec in REFERENCE_INTEGRATION.items():
        path = ROOT / rel
        if not path.is_file():
            error(f"missing reference page {rel}")
            ok = False
            continue
        text = path.read_text(encoding="utf-8")
        if STANDARD_LINK not in text:
            error(f"{rel}: must link to Evidence Posture Standard v1")
            ok = False
        if "Standard Relationship" not in text:
            error(f"{rel}: missing Standard Relationship section")
            ok = False
        if spec["eps"] not in text:
            error(f"{rel}: must reference {spec['eps']}")
            ok = False
        if spec["phrase"] not in text:
            error(f"{rel}: missing concept-specific standard relationship phrase")
            ok = False
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, text, re.I):
                error(f"{rel}: forbidden pattern {pat}")
                ok = False
    for rel in ("index.html", "language/index.html"):
        if STANDARD_LINK not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel}: must link to standard")
            ok = False
    return ok


def validate_standard_page() -> bool:
    ok = True
    path = ROOT / STANDARD_PATH
    if not path.is_file():
        error(f"missing {STANDARD_PATH}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    for section in STANDARD_SECTIONS:
        if section not in text:
            error(f"standard page missing section: {section}")
            ok = False
    if "authority layer" not in lower:
        error("standard page must state it is the authority layer")
        ok = False
    if "future protocol" not in lower:
        error("standard page must mention future protocol")
        ok = False
    if "does not create a public protocol" not in lower and "does not create" not in lower:
        error("standard page must state no public protocol is created")
        ok = False
    for rel in REFERENCE_INTEGRATION:
        parts = rel.split("/")
        href = f"/{parts[0]}/{parts[1]}/"
        if href not in text:
            error(f"standard page missing link to {href}")
            ok = False
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    if pat.search(text):
        error("standard page must not link to prototypes")
        ok = False
    return ok


def validate_protocol_doc() -> bool:
    ok = True
    path = ROOT / PROTOCOL_DOC
    if not path.is_file():
        error(f"missing {PROTOCOL_DOC}")
        return False
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    for phrase in [
        "no public protocol route is created",
        "no engine",
        "no classifier",
        "no upload",
        "no scoring",
        "no api",
        "no analytics",
        "no forms",
        "public tool behavior",
    ]:
        if phrase not in lower:
            error(f"{PROTOCOL_DOC}: missing phrase '{phrase}'")
            ok = False
    if "/protocol/" in text and "no public protocol route" not in lower:
        error(f"{PROTOCOL_DOC}: must clarify /protocol/ is not created")
        ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    decision_log = (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8")
    protocol_routes = [r for r in routes if "/protocol/" in r.get("path", "")]
    if "DEC-079" in decision_log:
        if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
            error(f"route registry must contain {PUBLIC_SITEMAP_URL_COUNT} routes after Sprint 61")
            ok = False
        if len(protocol_routes) != 1 or protocol_routes[0].get("path") != "/protocol/evidence-posture/":
            error("Sprint 61 must retain exactly one protocol route at /protocol/evidence-posture/")
            ok = False
        if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
            ok = False
    else:
        if len(routes) != 17:
            error("route registry must remain 17 routes at Sprint 60 completion")
            ok = False
        if protocol_routes:
            error("no public protocol route may be created at Sprint 60")
            ok = False
        if not validate_public_surface(routes, error, 17):
            ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    expected = PUBLIC_SITEMAP_URL_COUNT if "DEC-079" in decision_log else 17
    if len(locs) != expected:
        error(f"sitemap must contain exactly {expected} URLs for Sprint 60/61 snapshot")
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
    if "DEC-078" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-078 missing from DECISION_LOG.md")
        ok = False
    if not (ROOT / "SPRINT_60_STANDARD_INTEGRATION_PROTOCOL_READINESS_AUDIT.md").is_file():
        error("Sprint 60 audit missing")
        ok = False
    if "validate_standard_integration_protocol_readiness.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 60 validator")
        ok = False
    pub = json.loads((ROOT / "data/publisher-governance-policy.json").read_text(encoding="utf-8"))
    if pub.get("current_publisher_status") not in (
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
    ):
        error("publisher status must be blocked_until_evidence_posture_standard_v1_validation, protocol v1 draft validation, interface thesis validation, static embodiment v1 validation, visual system hardening validation, or controlled domain connection decision")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
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
            validate_reference_integration,
            validate_standard_page,
            validate_protocol_doc,
            validate_surface,
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
