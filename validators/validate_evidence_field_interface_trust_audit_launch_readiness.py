#!/usr/bin/env python3
"""Validate Sprint 66 — Evidence Field Interface Trust Audit and Launch Readiness."""

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

TRUST_AUDIT = "EVIDENCE_FIELD_INTERFACE_TRUST_AUDIT.md"
LAUNCH_CHECKLIST = "PUBLIC_LAUNCH_READINESS_CHECKLIST.md"
SPRINT_AUDIT = "SPRINT_66_EVIDENCE_FIELD_INTERFACE_TRUST_AUDIT_LAUNCH_READINESS_AUDIT.md"
INTERFACE_PATH = "interface/evidence-field/index.html"
STANDARD_PATH = "standard/evidence-posture/index.html"
PROTOCOL_PATH = "protocol/evidence-posture/index.html"
HOMEPAGE_PATH = "index.html"
INTERFACE_ROUTE = "/interface/evidence-field/"

INTERFACE_REJECT = [
    "detector dashboard",
    "upload-centered",
    "traffic-light",
    "confidence meter",
    "result-card",
    "fake/real",
]

INTERFACE_FORBIDDEN = [
    r"<script\b",
    r"<form\b",
    r"<input\b",
    r"<textarea\b",
    r"<select\b",
    r"<button\b",
    r"\b\d{1,3}\s*%",
    r"confidence percentage",
]

FORBIDDEN_UNTRACKED = [
    "SPRINT_66_PUBLIC_REFERENCE_SEO",
]

LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]

SOURCE_LOCS = [
    TRUST_AUDIT,
    LAUNCH_CHECKLIST,
    SPRINT_AUDIT,
    "validators/validate_evidence_field_interface_trust_audit_launch_readiness.py",
]


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def validate_documents() -> bool:
    ok = True
    for name in (TRUST_AUDIT, LAUNCH_CHECKLIST, SPRINT_AUDIT):
        if not (ROOT / name).is_file():
            error(f"missing {name}")
            ok = False
    trust = (ROOT / TRUST_AUDIT).read_text(encoding="utf-8") if (ROOT / TRUST_AUDIT).is_file() else ""
    checklist = (ROOT / LAUNCH_CHECKLIST).read_text(encoding="utf-8") if (ROOT / LAUNCH_CHECKLIST).is_file() else ""
    lower_check = checklist.lower()
    if "19" not in checklist and "nineteen" not in lower_check:
        error("launch checklist must document 19 URLs")
        ok = False
    if "not changed in sprint 66" not in lower_check and "not changed in Sprint 66" not in checklist:
        error("launch checklist must state DNS was not changed in Sprint 66")
        ok = False
    if "custom domain" not in lower_check or "not launched" not in lower_check:
        error("launch checklist must state custom domain was not launched in Sprint 66")
        ok = False
    if "engine" not in lower_check or "blocked" not in lower_check:
        error("launch checklist must state engine/tool remains blocked")
        ok = False
    if "controlled domain connection" not in lower_check or "explicit" not in lower_check:
        error("launch checklist must require separate explicit controlled domain connection decision")
        ok = False
    if "evidence-field" not in trust.lower() and "evidence field" not in trust.lower():
        error("trust audit must document evidence-field framing")
        ok = False
    if "detector" not in trust.lower():
        error("trust audit must document detector-dashboard rejection")
        ok = False
    return ok


def validate_pages() -> bool:
    ok = True
    for rel in (HOMEPAGE_PATH, STANDARD_PATH, PROTOCOL_PATH, INTERFACE_PATH):
        if not (ROOT / rel).is_file():
            error(f"missing {rel}")
            ok = False
    iface = (ROOT / INTERFACE_PATH).read_text(encoding="utf-8")
    iface_lower = iface.lower()
    if "Non-Operational" not in iface and "non-operational" not in iface_lower:
        error("interface page missing non-operational status")
        ok = False
    for phrase in INTERFACE_REJECT:
        if phrase not in iface_lower:
            error(f"interface page must reject or address: {phrase}")
            ok = False
    for pat in INTERFACE_FORBIDDEN:
        if re.search(pat, iface, re.I):
            error(f"interface page forbidden pattern: {pat}")
            ok = False
    standard = (ROOT / STANDARD_PATH).read_text(encoding="utf-8").lower()
    if "not an operational engine" not in standard and "not an operational engine or classifier" not in standard:
        if "not operate an engine" not in standard or "classifier" not in standard:
            error("standard page must state it is not an operational engine or classifier")
            ok = False
    protocol = (ROOT / PROTOCOL_PATH).read_text(encoding="utf-8").lower()
    if "not executable automation" not in protocol and "public engine behavior" not in protocol:
        if "does not operate an engine" not in protocol:
            error("protocol page must state it is not executable automation or public engine behavior")
            ok = False
    pat = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for rel in (HOMEPAGE_PATH, STANDARD_PATH, PROTOCOL_PATH, INTERFACE_PATH):
        if pat.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel} prototype leak")
            ok = False
    return ok


def validate_surface() -> bool:
    ok = True
    routes = json.loads((ROOT / "data/route-registry.json").read_text(encoding="utf-8")).get("routes", [])
    if len(routes) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"route registry must contain exactly {PUBLIC_SITEMAP_URL_COUNT} routes")
        ok = False
    extra = [r for r in routes if r.get("path", "").startswith("/interface/") and r.get("path") != INTERFACE_ROUTE]
    if extra:
        error("no additional interface routes beyond /interface/evidence-field/")
        ok = False
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    locs = [e.text.strip() for e in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc") if e.text]
    if len(locs) != PUBLIC_SITEMAP_URL_COUNT:
        error(f"sitemap must contain exactly {PUBLIC_SITEMAP_URL_COUNT} URLs")
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
    if "DEC-084" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-084 missing from DECISION_LOG.md")
        ok = False
    if "validate_evidence_field_interface_trust_audit_launch_readiness.py" not in (
        ROOT / "validators/validate_all.py"
    ).read_text(encoding="utf-8"):
        error("validate_all.py must include Sprint 66 validator")
        ok = False
    locs = {s.get("location") for s in json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8")).get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    if not any(c.get("claim_id") == "CLAIM-0068" for c in json.loads((ROOT / "data/evidence-ledger.json").read_text(encoding="utf-8")).get("claims", [])):
        error("CLAIM-0068 missing")
        ok = False
    return ok


def validate_worktree() -> bool:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    ).stdout
    for line in out.splitlines():
        if line.startswith("??"):
            path = line[3:].strip()
            if any(f in path for f in FORBIDDEN_UNTRACKED):
                error(f"unrelated untracked file present: {path}")
                return False
    return True


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
            validate_documents,
            validate_pages,
            validate_surface,
            validate_governance,
            validate_worktree,
            validate_cache,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
