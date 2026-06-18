#!/usr/bin/env python3
"""Validate Hoax.ai governed publisher control plane enforcement."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "quality_principle",
    "current_publisher_status",
    "allowed_current_outputs",
    "prohibited_current_outputs",
    "future_allowed_outputs_after_gates",
    "publisher_prohibitions",
    "required_release_gates",
    "human_approval_rule",
    "last_reviewed",
}

WORKFLOW_TOP = {"registry_id", "name", "version", "status", "maturity", "workflows", "last_reviewed"}

STATE_MACHINE_TOP = {
    "state_machine_id",
    "name",
    "version",
    "status",
    "maturity",
    "states",
    "allowed_transitions",
    "terminal_states",
    "blocked_transitions",
    "current_system_state",
    "last_reviewed",
}

GATES_TOP = {"gate_set_id", "name", "version", "status", "maturity", "gates", "last_reviewed"}

QUEUE_TOP = {"registry_id", "name", "version", "status", "maturity", "queues", "last_reviewed"}

REQUIRED_STATES = [
    "blocked",
    "proposed_internal",
    "candidate_registered",
    "blueprint_checked",
    "substance_required",
    "claim_mapping_required",
    "source_scope_required",
    "draft_allowed_internal",
    "draft_generated_internal",
    "validation_pending",
    "governance_review_required",
    "pull_request_ready",
    "release_candidate",
    "release_eligible",
    "public_release_blocked",
    "retired",
]

REQUIRED_GATE_IDS = [f"PUB-GATE-{i:04d}" for i in range(1, 16)]

REQUIRED_WORKFLOW_IDS = [f"PUB-WORKFLOW-{i:04d}" for i in range(1, 16)]

DRAFT_BLOCKED_FROM = "PUB-WORKFLOW-0008"

REQUIRED_SOURCE_LOCATIONS = [
    "GOVERNED_PUBLISHER_CONTROL_PLANE.md",
    "data/publisher-governance-policy.json",
    "data/publisher-workflow-registry.json",
    "data/publisher-state-machine.json",
    "data/publisher-quality-gates.json",
    "data/publisher-queue-registry.json",
    "validators/validate_publisher_control_plane.py",
    ".github/ISSUE_TEMPLATE/publisher-candidate.yml",
    ".cursor/rules/hoax-publisher.mdc",
]

PROHIBITED_CURRENT_OUTPUTS = [
    "public_page",
    "public_route",
    "draft_page",
    "sitemap",
    "seo_page",
    "deployment",
    "dns",
    "cloudflare",
    "form",
    "analytics",
    "classifier",
    "upload",
    "scoring",
    "monetization",
]

PUBLIC_FILES = {"index.html", "styles.css", "robots.txt", "sitemap.xml"}

WORKFLOW_ID_PATTERN = re.compile(r"^PUB-WORKFLOW-\d{4}$")
GATE_ID_PATTERN = re.compile(r"^PUB-GATE-\d{4}$")


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_publisher_policy() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-governance-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-governance-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"publisher-governance-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_publisher_policy":
        error("publisher-governance-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "publisher_blocked_until_dry_run_harness":
        error("publisher-governance-policy.json: invalid maturity")
        ok = False
    if data.get("current_publisher_status") != "blocked_until_publisher_dry_run_harness":
        error("publisher-governance-policy.json: publisher must be blocked until dry-run harness")
        ok = False

    allowed = " ".join(data.get("allowed_current_outputs", [])).lower()
    for term in ["policy", "workflow", "state_machine", "quality_gate", "queue", "validator", "audit"]:
        if term.replace("_", "") not in allowed.replace("_", ""):
            error(f"publisher-governance-policy.json: allowed_current_outputs missing {term}")
            ok = False

    prohibited = " ".join(data.get("prohibited_current_outputs", [])).lower()
    for term in PROHIBITED_CURRENT_OUTPUTS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"publisher-governance-policy.json: prohibited_current_outputs missing {term}")
            ok = False

    release = " ".join(data.get("required_release_gates", [])).lower()
    for term in ["content_quality", "claim", "route", "technical", "interface", "security",
                 "forbidden", "validate_all", "audit", "approval", "publisher"]:
        if term not in release:
            error(f"publisher-governance-policy.json: required_release_gates missing {term}")
            ok = False

    metrics = data.get("future_quality_metrics", [])
    for bad in ["score", "percent", "grade"]:
        combined = " ".join(metrics).lower()
        if bad in combined and "passed" not in combined:
            error(f"publisher-governance-policy.json: numeric quality metric prohibited: {bad}")
            ok = False

    return ok


def validate_workflow_registry() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-workflow-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-workflow-registry.json parse failed: {exc}")
        return False

    missing = WORKFLOW_TOP - set(data.keys())
    if missing:
        error(f"publisher-workflow-registry.json missing fields: {sorted(missing)}")
        ok = False

    workflows = data.get("workflows", [])
    ids: list[str] = []
    for wf in workflows:
        wid = wf.get("workflow_id", "")
        if not WORKFLOW_ID_PATTERN.match(wid):
            error(f"publisher-workflow-registry: invalid workflow_id {wid}")
            ok = False
        if wid in ids:
            error(f"publisher-workflow-registry: duplicate workflow_id {wid}")
            ok = False
        ids.append(wid)

        for field in ["workflow_id", "name", "status", "allowed_currently", "required_inputs",
                      "required_outputs", "blocked_until", "prohibited_behavior", "notes"]:
            if field not in wf:
                error(f"publisher-workflow-registry: {wid} missing {field}")
                ok = False

        combined = " ".join(str(wf.get(k, "")) for k in ["name", "notes", "prohibited_behavior"]).lower()
        if "publicly available" in combined or "publish now" in combined:
            error(f"publisher-workflow-registry: {wid} implies current public publishing")
            ok = False

    if set(ids) != set(REQUIRED_WORKFLOW_IDS):
        error(f"publisher-workflow-registry: expected workflows {REQUIRED_WORKFLOW_IDS}")
        ok = False

    draft_idx = REQUIRED_WORKFLOW_IDS.index(DRAFT_BLOCKED_FROM)
    for wid in REQUIRED_WORKFLOW_IDS[draft_idx:]:
        wf = next((w for w in workflows if w.get("workflow_id") == wid), None)
        if wf and wf.get("allowed_currently") is not False:
            error(f"publisher-workflow-registry: {wid} must have allowed_currently false")
            ok = False

    pub_release = next((w for w in workflows if w.get("workflow_id") == "PUB-WORKFLOW-0015"), None)
    if not pub_release or pub_release.get("status") != "blocked":
        error("publisher-workflow-registry: Public Release Gate must be blocked")
        ok = False

    return ok


def validate_state_machine() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-state-machine.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-state-machine.json parse failed: {exc}")
        return False

    missing = STATE_MACHINE_TOP - set(data.keys())
    if missing:
        error(f"publisher-state-machine.json missing fields: {sorted(missing)}")
        ok = False

    states = data.get("states", [])
    for state in REQUIRED_STATES:
        if state not in states:
            error(f"publisher-state-machine.json: missing state {state}")
            ok = False

    current = data.get("current_system_state", "")
    if current not in ("blocked", "blocked_until_publisher_dry_run_harness"):
        error(f"publisher-state-machine.json: invalid current_system_state {current}")
        ok = False

    if "public_release_blocked" not in states:
        error("publisher-state-machine.json: public_release_blocked state missing")
        ok = False

    blocked = data.get("blocked_transitions", [])
    direct_release = any(
        b.get("from") == "proposed_internal" and b.get("to") == "release_eligible"
        for b in blocked
    )
    if not direct_release:
        error("publisher-state-machine.json: must block proposed_internal to release_eligible")
        ok = False

    release_req = data.get("release_eligible_requires", [])
    if len(release_req) < 8:
        error("publisher-state-machine.json: release_eligible_requires too few gates")
        ok = False

    return ok


def validate_quality_gates() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-quality-gates.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-quality-gates.json parse failed: {exc}")
        return False

    missing = GATES_TOP - set(data.keys())
    if missing:
        error(f"publisher-quality-gates.json missing fields: {sorted(missing)}")
        ok = False

    gates = data.get("gates", [])
    ids = [g.get("gate_id") for g in gates]
    if set(ids) != set(REQUIRED_GATE_IDS):
        error(f"publisher-quality-gates.json: expected gates {REQUIRED_GATE_IDS}")
        ok = False

    for gate in gates:
        gid = gate.get("gate_id", "")
        if not GATE_ID_PATTERN.match(gid):
            error(f"publisher-quality-gates: invalid gate_id {gid}")
            ok = False
        if gate.get("required_before_public_release") is not True:
            error(f"publisher-quality-gates: {gid} must be required_before_public_release")
            ok = False
        if gate.get("bypassable") is True:
            error(f"publisher-quality-gates: {gid} must not be bypassable")
            ok = False

    cq = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0003"), None)
    if not cq or "blocked_until_sprint_14" in cq.get("status", "").lower():
        error("publisher-quality-gates: Content Quality Gate must be defined after Sprint 14")
        ok = False

    return ok


def validate_queue_registry() -> bool:
    ok = True
    path = ROOT / "data" / "publisher-queue-registry.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"publisher-queue-registry.json parse failed: {exc}")
        return False

    missing = QUEUE_TOP - set(data.keys())
    if missing:
        error(f"publisher-queue-registry.json missing fields: {sorted(missing)}")
        ok = False

    required_queues = {
        "publisher_intake_queue",
        "publisher_candidate_queue",
        "publisher_blocked_queue",
        "publisher_release_candidate_queue",
    }
    found = {q.get("queue_id") for q in data.get("queues", [])}
    if found != required_queues:
        error(f"publisher-queue-registry.json: expected queues {sorted(required_queues)}")
        ok = False

    for queue in data.get("queues", []):
        items = queue.get("items", [])
        if items:
            error(f"publisher-queue-registry: queue {queue.get('queue_id')} must be empty in Sprint 13B")
            ok = False

    return ok


def validate_publisher_issue_template() -> bool:
    ok = True
    path = ROOT / ".github" / "ISSUE_TEMPLATE" / "publisher-candidate.yml"
    if not path.exists():
        error("publisher-candidate.yml missing")
        return False

    content = path.read_text(encoding="utf-8").lower()
    for term in ["candidate purpose", "page family", "claim scope", "route impact", "sitemap impact",
                 "approval", "blocked", "content quality"]:
        if term not in content:
            error(f"publisher-candidate.yml: missing field context for '{term}'")
            ok = False

    for bad in ["deploy now", "enable pages", "publish directly", "expand sitemap now"]:
        if bad in content:
            error(f"publisher-candidate.yml: encourages prohibited action '{bad}'")
            ok = False

    return ok


def validate_cursor_publisher_rule() -> bool:
    ok = True
    path = ROOT / ".cursor" / "rules" / "hoax-publisher.mdc"
    if not path.exists():
        return True

    content = path.read_text(encoding="utf-8").lower()
    for required in ["blocked", "validate_all", "no draft", "no public route", "not a volume engine"]:
        if required not in content:
            error(f"hoax-publisher.mdc: missing '{required}'")
            ok = False

    for bad in ["publish now", "create draft pages in sprint 13b", "deploy to"]:
        if bad in content:
            error(f"hoax-publisher.mdc: permits publishing '{bad}'")
            ok = False

    return ok


def validate_expansion_gate_integration() -> bool:
    ok = True
    path = ROOT / "data" / "reference-expansion-gate.json"
    data = load_json(path)
    checks = " ".join(data.get("required_pre_release_checks", [])).lower()
    if "publisher" not in checks:
        error("reference-expansion-gate.json: must include publisher control pre-release check")
        ok = False

    rules = " ".join(data.get("release_eligibility_rules", [])).lower()
    if "publisher" not in rules:
        error("reference-expansion-gate.json: release rules must require publisher governance")
        ok = False

    return ok


def validate_repository_safety() -> bool:
    ok = True

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    if [r.get("route_id") for r in routes] != ["ROUTE-0001"]:
        error("route-registry: unexpected routes added")
        ok = False

    candidates = load_json(ROOT / "data" / "reference-page-candidate-registry.json").get("candidates", [])
    if candidates != []:
        error("reference-page-candidate-registry: must remain empty")
        ok = False

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in PUBLIC_FILES:
            error(f"unexpected HTML file: {rel}")
            ok = False

    draft_dirs = list(ROOT.glob("**/drafts/**")) + list(ROOT.glob("**/draft/**"))
    for d in draft_dirs:
        if d.is_dir() and any(d.iterdir()):
            error(f"content draft directory found: {d}")
            ok = False

    return ok


def validate_validate_all_integration() -> bool:
    ok = True
    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_publisher_control_plane.py" not in content:
        error("validate_all.py: must include validate_publisher_control_plane.py")
        ok = False
    return ok


def validate_source_registry() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry: missing publisher source {loc}")
            ok = False
    return ok


def validate_required_files() -> bool:
    ok = True
    for rel in [
        "GOVERNED_PUBLISHER_CONTROL_PLANE.md",
        "data/publisher-governance-policy.json",
        "data/publisher-workflow-registry.json",
        "data/publisher-state-machine.json",
        "data/publisher-quality-gates.json",
        "data/publisher-queue-registry.json",
        ".github/ISSUE_TEMPLATE/publisher-candidate.yml",
    ]:
        if not (ROOT / rel).exists():
            error(f"required publisher file missing: {rel}")
            ok = False
    return ok


def main() -> int:
    ok = True

    if not validate_required_files():
        ok = False
    if not validate_publisher_policy():
        ok = False
    if not validate_workflow_registry():
        ok = False
    if not validate_state_machine():
        ok = False
    if not validate_quality_gates():
        ok = False
    if not validate_queue_registry():
        ok = False
    if not validate_publisher_issue_template():
        ok = False
    if not validate_cursor_publisher_rule():
        ok = False
    if not validate_expansion_gate_integration():
        ok = False
    if not validate_repository_safety():
        ok = False
    if not validate_validate_all_integration():
        ok = False
    if not validate_source_registry():
        ok = False

    if ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
