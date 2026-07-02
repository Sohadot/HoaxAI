#!/usr/bin/env python3
"""Validate Sprint 123 — Public Reference Source Use Walkthrough Audit v1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from public_surface_checks import PUBLIC_SITEMAP_URL_COUNT  # noqa: E402

AUDIT_MD = "PUBLIC_REFERENCE_SOURCE_USE_WALKTHROUGH_AUDIT_V1.md"
SPRINT = "SPRINT_123_PUBLIC_REFERENCE_SOURCE_USE_WALKTHROUGH_AUDIT_V1.md"
JSON_PATH = "data/public-reference-source-use-walkthrough-audit-v1.json"
SCHEMA_PATH = "data/public-reference-source-use-walkthrough-audit-v1.schema.json"
PAGE = "source-use-orientation/index.html"
PAGE_ROUTE = "/source-use-orientation/"

REQUIRED_SCENARIO_FIELDS = [
    "scenario_id",
    "source_interpretation_intent",
    "expected_reference_destination",
    "actual_reference_destination",
    "supporting_routes",
    "result",
    "observed_issue",
    "repair_applied",
    "boundary_check",
    "ai_source_interpretation_note",
]

UNSAFE_TERMS = [
    "source index",
    "source database",
    "source directory",
    "source authority page",
    "proof claim",
    "verification claim",
    "certification claim",
    "endorsement claim",
    "detector evidence",
    "score basis",
    "case conclusion",
    "best source",
    "approved source",
    "trusted source certification",
    "citation generator",
    "generated citation",
    "search box",
    "dashboard",
    "graph tool",
    "scorecard",
    "rating system",
    "downloadable report",
    "sales page",
    "consulting offer",
    "service funnel",
    "due diligence",
    "legal representation",
    "financial representation",
]

NEGATION_PATTERN = re.compile(
    r"(?:must not|does not|do not|not a|not an|no |without|forbidden|prohibited|is not|are not|cannot)\s+[\w\s\-/]{0,120}",
    re.IGNORECASE,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def unnegated(text: str, term: str) -> bool:
    lower = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).lower()
    pos = 0
    while True:
        idx = lower.find(term, pos)
        if idx < 0:
            return False
        prefix = lower[max(0, idx - 160):idx]
        if NEGATION_PATTERN.search(prefix + term) or "what this page does not claim" in lower:
            pos = idx + len(term)
            continue
        if term == "sales page" and "sales-page" in lower[max(0, idx - 4): idx + 12]:
            pos = idx + len(term)
            continue
        return True


def validate_artifacts() -> bool:
    ok = True
    for rel in (AUDIT_MD, SPRINT, JSON_PATH, SCHEMA_PATH):
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            ok = False
    return ok


def validate_audit_json() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    load_json(SCHEMA_PATH)
    expected = {
        "audit_only": True,
        "production_route_added": False,
        "public_route_count_before": 104,
        "public_route_count_after": 104,
        "sitemap_url_count_expected": 104,
        "primary_route_under_audit": PAGE_ROUTE,
        "route_registry_changed": False,
        "public_file_registry_changed": False,
        "no_new_routes": True,
        "new_decision_created": False,
        "boundary_regressions_found": False,
        "proof_drift_found": False,
        "verification_drift_found": False,
        "authority_claim_drift_found": False,
        "endorsement_drift_found": False,
        "source_certification_drift_found": False,
        "detector_evidence_drift_found": False,
        "score_basis_drift_found": False,
        "case_conclusion_drift_found": False,
        "legal_or_academic_source_drift_found": False,
        "transaction_or_sales_drift_found": False,
    }
    for k, v in expected.items():
        if data.get(k) != v:
            error(f"{JSON_PATH}: {k} must be {v!r}")
            ok = False
    scenarios = data.get("walkthrough_scenarios", [])
    if len(scenarios) < 20:
        error(f"{JSON_PATH}: must include at least 20 scenarios")
        ok = False
    if data.get("total_scenarios") != len(scenarios):
        error(f"{JSON_PATH}: total_scenarios mismatch")
        ok = False
    passed = sum(1 for s in scenarios if s.get("result") == "pass")
    failed = sum(1 for s in scenarios if s.get("result") == "fail")
    if data.get("scenarios_passed") != passed or data.get("scenarios_failed") != failed:
        error(f"{JSON_PATH}: pass/fail counts mismatch")
        ok = False
    for sc in scenarios:
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in sc:
                error(f"{sc.get('scenario_id', '?')}: missing field {field}")
                ok = False
        if sc.get("result") not in ("pass", "fail"):
            error(f"{sc.get('scenario_id')}: invalid result")
            ok = False
        if sc.get("result") == "fail" and not (sc.get("repair_applied") or sc.get("deferred_reason")):
            error(f"{sc.get('scenario_id')}: failed scenario needs repair_applied or deferred_reason")
            ok = False
    return ok


def validate_no_expansion() -> bool:
    ok = True
    data = load_json(JSON_PATH)
    if data.get("production_route_added") is not False:
        error("audit JSON must declare production_route_added false for Sprint 123")
        ok = False
    if data.get("public_route_count_after") != 104:
        error("audit JSON public_route_count_after must remain 104 for Sprint 123")
        ok = False
    if data.get("sitemap_url_count_expected") != 104:
        error("audit JSON sitemap_url_count_expected must remain 104 for Sprint 123")
        ok = False
    reg = load_json("data/route-registry.json").get("routes", [])
    if len(reg) != 104:
        error(f"route registry must have exactly 104 entries, found {len(reg)}")
        ok = False
    r104 = next((r for r in reg if r.get("route_id") == "ROUTE-0104"), None)
    if r104 is None or r104.get("path") != PAGE_ROUTE:
        error("ROUTE-0104 must remain present for audited source-use-orientation route")
        ok = False
    files = load_json("data/public-file-registry.json").get("files", [])
    if any(f.get("public_file_id") == "PUB-FILE-0105" for f in files):
        error("PUB-FILE-0105 must not exist after Sprint 123 audit-only sprint")
        ok = False
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = sitemap.findall("sm:url", ns) or sitemap.findall("url")
    if len(urls) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must have {PUBLIC_SITEMAP_URL_COUNT} URLs, found {len(urls)}")
        ok = False
    return ok


def validate_source_use_orientation_links() -> bool:
    ok = True
    if not (ROOT / PAGE).is_file():
        error(f"{PAGE} missing")
        return False
    html = (ROOT / PAGE).read_text(encoding="utf-8")
    for rel in (
        "index.html",
        "system-map/index.html",
        "reading-sequences/index.html",
        "retrieval-index/index.html",
        "citation-orientation/index.html",
    ):
        if PAGE_ROUTE not in (ROOT / rel).read_text(encoding="utf-8"):
            error(f"{rel} must link to {PAGE_ROUTE}")
            ok = False
    for anchor in (
        "#sources-as-reference-support",
        "#source-confidence-blocks",
        "#evidence-ledger-traceability",
        "#claim-source-relationship",
    ):
        if f'href="{anchor}"' not in html:
            error(f"source-use-orientation how-to-use missing self-block anchor {anchor}")
            ok = False
    ri = (ROOT / "retrieval-index/index.html").read_text(encoding="utf-8")
    if "/source-use-orientation/#reference-answer" not in ri:
        error("retrieval-index missing source-use-orientation block anchor hardening")
        ok = False
    co = (ROOT / "citation-orientation/index.html").read_text(encoding="utf-8")
    if "/source-use-orientation/#source-use-citation-orientation" not in co:
        error("citation-orientation missing source-use-citation-orientation hardening link")
        ok = False
    for bad in ("<script", "<form", "<input", "<textarea", "<select"):
        if bad in html.lower():
            error(f"{PAGE}: prohibited element {bad}")
            ok = False
    return ok


def validate_terms_and_decision() -> bool:
    ok = True
    dlog = (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8")
    data = load_json(JSON_PATH)
    if data.get("new_decision_created"):
        if "DEC-139" not in dlog:
            error("DEC-139 required when new_decision_created is true")
            ok = False
        if PAGE_ROUTE not in dlog:
            error("DEC-139 must govern visible production issue on source-use-orientation route")
            ok = False
    elif re.search(r"\bDEC-139\b", dlog):
        error("DEC-139 present but audit declares no new decision was required")
        ok = False
    for rel in (SPRINT,):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for term in UNSAFE_TERMS:
            if unnegated(text, term):
                error(f"{rel}: unnegated unsafe term {term!r}")
                ok = False
    for rel in (PAGE, "retrieval-index/index.html", "citation-orientation/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for term in UNSAFE_TERMS:
            if unnegated(text, term):
                error(f"{rel}: unnegated unsafe term {term!r}")
                ok = False
    return ok


def validate_governance_wiring() -> bool:
    ok = True
    if not any(c.get("claim_id") == "CLAIM-0124" for c in load_json("data/evidence-ledger.json").get("claims", [])):
        error("CLAIM-0124 missing")
        ok = False
    if not any(g.get("gate_id") == "PUB-GATE-0117" for g in load_json("data/publisher-quality-gates.json").get("gates", [])):
        error("PUB-GATE-0117 missing")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for rel in (
        AUDIT_MD,
        SPRINT,
        JSON_PATH,
        SCHEMA_PATH,
        "validators/validate_public_reference_source_use_walkthrough_audit_v1.py",
    ):
        if rel not in locs:
            error(f"source-registry missing {rel}")
            ok = False
    if "validate_public_reference_source_use_walkthrough_audit_v1.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py missing Sprint 123 validator")
        ok = False
    names = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    names += subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True
    ).stdout.splitlines()
    for rel in names:
        if "__pycache__" in rel or rel.endswith(".pyc"):
            error(f"python cache tracked or staged: {rel}")
            ok = False
    return ok


def main() -> int:
    ok = True
    for fn in (
        validate_artifacts,
        validate_audit_json,
        validate_no_expansion,
        validate_source_use_orientation_links,
        validate_terms_and_decision,
        validate_governance_wiring,
    ):
        if not fn():
            ok = False
    if not ok:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
