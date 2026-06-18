#!/usr/bin/env python3
"""Validate Hoax.ai automation governance and CI quality gate enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AUTO_POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "approved_automation",
    "prohibited_automation",
    "ci_permission_rules",
    "workflow_trigger_rules",
    "agent_execution_rules",
    "deployment_block",
    "external_infrastructure_block",
    "validation_requirements",
    "last_reviewed",
}

CI_POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "required_workflows",
    "allowed_actions",
    "prohibited_actions",
    "required_commands",
    "prohibited_commands",
    "permissions_policy",
    "last_reviewed",
}

REQUIRED_FILES = [
    "AUTOMATION_GOVERNANCE.md",
    "AGENT_EXECUTION_RULES.md",
    ".github/workflows/quality-gate.yml",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/governance-task.yml",
    ".github/BRANCH_PROTECTION_RECOMMENDATION.md",
    "data/automation-governance-policy.json",
    "data/ci-quality-gate-policy.json",
]

REQUIRED_SOURCE_LOCATIONS = [
    "AUTOMATION_GOVERNANCE.md",
    "AGENT_EXECUTION_RULES.md",
    "data/automation-governance-policy.json",
    "data/ci-quality-gate-policy.json",
    "validators/validate_automation_governance.py",
    ".github/workflows/quality-gate.yml",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/governance-task.yml",
    ".github/BRANCH_PROTECTION_RECOMMENDATION.md",
    ".cursor/rules/hoax-governance.mdc",
]

PROHIBITED_AUTO_TERMS = [
    "deployment",
    "github_pages",
    "cloudflare",
    "dns",
    "secrets",
    "write_permission",
    "pull_request_target",
    "sitemap_expansion",
    "route_generation",
    "public_tool",
    "upload",
    "scoring",
    "analytics",
]

WORKFLOW_PROHIBITED = [
    "pull_request_target",
    "write-all",
    "pages:",
    "id-token:",
    "deployments:",
    "secrets.",
    "wrangler",
    "cloudflare",
    "vercel",
    "netlify",
    "firebase",
    "gcloud",
    "npm publish",
    "scp ",
    "ssh ",
    "ftp ",
    "rsync ",
]

from public_surface_checks import (
    ALLOWED_NON_PUBLIC_HTML,
    ALLOWED_PUBLIC_ROOT_FILES,
    PUBLISHER_STATUSES_ALLOWED,
    PUBLISHER_STATUS_POST_PILOT,
    validate_no_extra_public_html,
    validate_pilot_public_surface,
    validate_pilot_route_registry,
    validate_pilot_sitemap,
)

PUBLIC_FILES = ALLOWED_PUBLIC_ROOT_FILES


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_automation_policy() -> bool:
    ok = True
    path = ROOT / "data" / "automation-governance-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"automation-governance-policy.json parse failed: {exc}")
        return False

    missing = AUTO_POLICY_TOP - set(data.keys())
    if missing:
        error(f"automation-governance-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_automation_quality_gate":
        error("automation-governance-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "validation_only_no_deployment":
        error("automation-governance-policy.json: invalid maturity")
        ok = False

    prohibited = " ".join(data.get("prohibited_automation", [])).lower()
    for term in PROHIBITED_AUTO_TERMS:
        key = term.replace("_", "")
        if key not in prohibited.replace("_", ""):
            if term == "write_permission" and "write" in prohibited:
                continue
            if term == "route_generation" and "route" in prohibited:
                continue
            error(f"automation-governance-policy.json: prohibited_automation missing {term}")
            ok = False

    validation = " ".join(data.get("validation_requirements", [])).lower()
    if "validate_all" not in validation:
        error("automation-governance-policy.json: validation_requirements must require validate_all.py")
        ok = False

    return ok


def validate_ci_policy() -> bool:
    ok = True
    path = ROOT / "data" / "ci-quality-gate-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"ci-quality-gate-policy.json parse failed: {exc}")
        return False

    missing = CI_POLICY_TOP - set(data.keys())
    if missing:
        error(f"ci-quality-gate-policy.json missing fields: {sorted(missing)}")
        ok = False

    workflows = data.get("required_workflows", [])
    if ".github/workflows/quality-gate.yml" not in workflows:
        error("ci-quality-gate-policy.json: must require quality-gate.yml")
        ok = False

    commands = " ".join(data.get("required_commands", [])).lower()
    if "validate_all" not in commands:
        error("ci-quality-gate-policy.json: required_commands must include validate_all.py")
        ok = False

    perms = data.get("permissions_policy", {})
    if perms.get("contents") != "read":
        error("ci-quality-gate-policy.json: permissions_policy must require contents read")
        ok = False

    prohibited_cmds = " ".join(data.get("prohibited_commands", [])).lower()
    for cmd in ["deploy", "wrangler", "cloudflare", "vercel", "netlify"]:
        if cmd not in prohibited_cmds:
            error(f"ci-quality-gate-policy.json: prohibited_commands missing {cmd}")
            ok = False

    allowed = data.get("allowed_actions", [])
    for action in allowed:
        if not action.startswith("actions/"):
            error(f"ci-quality-gate-policy.json: unapproved action {action}")
            ok = False

    prohibited_actions = " ".join(data.get("prohibited_actions", [])).lower()
    if "pull_request_target" not in prohibited_actions:
        error("ci-quality-gate-policy.json: must prohibit pull_request_target")
        ok = False

    return ok


def validate_workflow() -> bool:
    ok = True
    path = ROOT / ".github" / "workflows" / "quality-gate.yml"
    if not path.exists():
        error("quality-gate.yml missing")
        return False

    content = path.read_text(encoding="utf-8")
    lower = content.lower()

    if "validate_all.py" not in content:
        error("quality-gate.yml: must run validate_all.py")
        ok = False

    if "contents: read" not in lower and "contents:read" not in lower.replace(" ", ""):
        error("quality-gate.yml: must set permissions contents read")
        ok = False

    for pattern in WORKFLOW_PROHIBITED:
        if pattern.lower() in lower:
            error(f"quality-gate.yml: prohibited pattern '{pattern}'")
            ok = False

    if re.search(r"\bdeploy\b", lower) and "validate" not in lower:
        error("quality-gate.yml: contains deploy command")
        ok = False

    deploy_lines = [ln for ln in content.splitlines() if re.search(r"\bdeploy\b", ln.lower())]
    for ln in deploy_lines:
        if "validate_all" not in ln and "py_compile" not in ln:
            error(f"quality-gate.yml: deploy-like command: {ln.strip()}")
            ok = False

    return ok


def validate_pr_template() -> bool:
    ok = True
    path = ROOT / ".github" / "pull_request_template.md"
    if not path.exists():
        error("pull_request_template.md missing")
        return False

    content = path.read_text(encoding="utf-8").lower()
    checks = [
        "validate_all.py",
        "pass",
        "dns",
        "cloudflare",
        "deployment",
        "classifier",
        "upload",
        "scoring",
        "route",
        "sitemap",
        "claim",
        "source",
    ]
    for check in checks:
        if check not in content:
            error(f"pull_request_template.md: missing checklist item related to '{check}'")
            ok = False

    return ok


def validate_governance_issue_template() -> bool:
    ok = True
    path = ROOT / ".github" / "ISSUE_TEMPLATE" / "governance-task.yml"
    if not path.exists():
        error("governance-task.yml missing")
        return False

    content = path.read_text(encoding="utf-8").lower()
    for field in ["sprint", "proposed change", "governance", "validator", "deployment", "acceptance"]:
        if field not in content:
            error(f"governance-task.yml: missing field context for '{field}'")
            ok = False

    if "enable pages" in content or "deploy now" in content:
        error("governance-task.yml: encourages deployment")
        ok = False

    return ok


def validate_cursor_rules() -> bool:
    ok = True
    path = ROOT / ".cursor" / "rules" / "hoax-governance.mdc"
    if not path.exists():
        return True

    content = path.read_text(encoding="utf-8").lower()
    for required in ["validate_all.py", "not a detector", "deployment", "classifier"]:
        if required not in content:
            error(f"hoax-governance.mdc: missing '{required}'")
            ok = False

    prohibited = ["upload your file", "scan now", "deploy to production", "enable github pages"]
    for phrase in prohibited:
        if phrase in content:
            error(f"hoax-governance.mdc: prohibited expansion language '{phrase}'")
            ok = False

    return ok


def validate_validate_all_integration() -> bool:
    ok = True
    path = ROOT / "validators" / "validate_all.py"
    content = path.read_text(encoding="utf-8")
    if "validate_automation_governance.py" not in content:
        error("validate_all.py: must include validate_automation_governance.py")
        ok = False
    return ok


def validate_source_registry() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing automation governance source {loc}")
            ok = False
    return ok


def validate_route_sitemap_safety() -> bool:
    ok = True
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    candidates = load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", [])
    if candidates:
        from candidate_registry_checks import validate_candidates_blocked_only

        if not validate_candidates_blocked_only(candidates, error):
            ok = False

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_NON_PUBLIC_HTML:
            error(f"unexpected public HTML: {rel}")
            ok = False

    return ok


def validate_required_files() -> bool:
    ok = True
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            error(f"required automation file missing: {rel}")
            ok = False
    return ok


def main() -> int:
    ok = True

    if not validate_required_files():
        ok = False
    if not validate_automation_policy():
        ok = False
    if not validate_ci_policy():
        ok = False
    if not validate_workflow():
        ok = False
    if not validate_pr_template():
        ok = False
    if not validate_governance_issue_template():
        ok = False
    if not validate_cursor_rules():
        ok = False
    if not validate_validate_all_integration():
        ok = False
    if not validate_source_registry():
        ok = False
    if not validate_route_sitemap_safety():
        ok = False

    if ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
