#!/usr/bin/env python3
"""Validate Hoax.ai first internal draft blueprint pack enforcement."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

POLICY_TOP = {
    "policy_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "structure_principle",
    "allowed_blueprint_pack_actions",
    "prohibited_blueprint_pack_actions",
    "eligible_candidate_readiness_states",
    "ineligible_candidate_readiness_states",
    "required_blueprint_fields",
    "required_status_values",
    "non_authorization_rules",
    "last_reviewed",
}

PACK_TOP = {
    "blueprint_pack_id",
    "name",
    "version",
    "status",
    "maturity",
    "governing_principle",
    "selected_candidates",
    "blueprints",
    "last_reviewed",
}

REGISTRY_TOP = {
    "registry_id",
    "name",
    "version",
    "status",
    "maturity",
    "blueprint_records",
    "last_reviewed",
}

REQUIRED_SOURCE_LOCATIONS = [
    "FIRST_INTERNAL_DRAFT_BLUEPRINT_PACK.md",
    "data/internal-draft-blueprint-pack-policy.json",
    "data/internal-draft-blueprint-pack-v1.json",
    "data/internal-draft-blueprint-registry.json",
    "validators/validate_internal_draft_blueprint_pack.py",
]

REQUIRED_BLUEPRINT_IDS = [f"DRAFT-BLUEPRINT-{i:04d}" for i in range(1, 5)]

REQUIRED_CANDIDATE_IDS = ["REF-CAND-0001", "REF-CAND-0002", "REF-CAND-0006", "REF-CAND-0007"]

EXCLUDED_CANDIDATE_IDS = ["REF-CAND-0008"]

BLUEPRINT_FIELDS = [
    "blueprint_id",
    "candidate_id",
    "candidate_name",
    "candidate_evaluation_ref",
    "blueprint_status",
    "draft_status",
    "route_status",
    "sitemap_status",
    "publication_status",
    "page_family",
    "page_type_ref",
    "template_ref",
    "reference_thesis",
    "reference_purpose",
    "definition_scope",
    "governance_boundary",
    "claim_scope",
    "source_scope",
    "semantic_seo_role",
    "section_contracts",
    "prohibited_misreadings",
    "forbidden_public_implications",
    "internal_link_plan",
    "structured_data_boundary",
    "interface_boundary",
    "security_privacy_boundary",
    "required_gates",
    "review_status",
    "non_authorization_statement",
    "notes",
]

ELIGIBLE_READINESS = {"draft_blueprint_candidate", "dependency_candidate"}

PROHIBITED_ACTIONS = [
    "draft_prose",
    "draft_files",
    "page_creation",
    "route_activation",
    "sitemap",
    "public_metadata",
    "public_navigation",
    "publication",
    "deployment",
    "dns",
    "cloudflare",
    "tool",
    "classifier",
    "upload",
    "scoring",
    "forms",
    "analytics",
    "external_factual",
]

NON_AUTHORIZATION_TERMS = [
    "drafts",
    "routes",
    "sitemap",
    "publishing",
    "deployment",
    "seo_expansion",
    "public_metadata",
]

FORBIDDEN_IMPLICATIONS = [
    "detector",
    "fake",
    "real",
    "upload",
    "scoring",
    "classifier",
    "tool",
    "service",
    "software",
    "api",
    "unsupported authority",
]

PUBLIC_METADATA_TERMS = [
    "public_title",
    "meta_description",
    "public_canonical",
    "og:title",
    "twitter:card",
    "schema.org",
    '"@type"',
]

REAL_ENTITY_TERMS = [
    "donald trump",
    "joe biden",
    "google",
    "microsoft",
    "openai",
    "elon musk",
    "ukraine",
    "election 2024",
]

NUMERIC_SCORE_PATTERN = re.compile(
    r"\b(score|grade|percent|percentage|\d+\s*%|seo_score|quality_score)\b",
    re.IGNORECASE,
)

BLUEPRINT_ID_PATTERN = re.compile(r"^DRAFT-BLUEPRINT-\d{4}$")
SECTION_ID_PATTERN = re.compile(r"^DRAFT-SECTION-\d{4}$")
DRAFT_GATE_PATTERN = re.compile(r"^DRAFT-GATE-\d{4}$")
PUB_GATE_PATTERN = re.compile(r"^PUB-GATE-\d{4}$")

from public_surface_checks import (
    ALLOWED_PUBLIC_HTML,
    ALLOWED_PUBLIC_ROOT_FILES,
    PUBLISHER_STATUSES_ALLOWED,
    PUBLISHER_STATUS_POST_PILOT,
    validate_no_extra_public_html,
    validate_pilot_public_surface,
    validate_pilot_route_registry,
    validate_pilot_sitemap,
)

PUBLIC_FILES = ALLOWED_PUBLIC_ROOT_FILES

DRAFT_PATH_CANDIDATES = [ROOT / "internal" / "drafts", ROOT / "governance" / "drafts"]

MAX_FIELD_WORDS = 80


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def word_count(text: str) -> int:
    return len(text.split())


def collect_strings(obj: object) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        out: list[str] = []
        for v in obj.values():
            out.extend(collect_strings(v))
        return out
    if isinstance(obj, list):
        out = []
        for item in obj:
            out.extend(collect_strings(item))
        return out
    return []


def json_has_numeric_scores(data: object) -> bool:
    text = json.dumps(data).lower()
    if NUMERIC_SCORE_PATTERN.search(text):
        if "no_numeric" in text.replace("-", "_"):
            return False
        return True
    return False


def validate_policy() -> bool:
    ok = True
    path = ROOT / "data" / "internal-draft-blueprint-pack-policy.json"
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        error(f"internal-draft-blueprint-pack-policy.json parse failed: {exc}")
        return False

    missing = POLICY_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-blueprint-pack-policy.json missing fields: {sorted(missing)}")
        ok = False

    if data.get("status") != "governed_internal_draft_blueprint_pack_policy":
        error("internal-draft-blueprint-pack-policy.json: invalid status")
        ok = False
    if data.get("maturity") != "blueprint_records_only_no_drafts_no_routes_no_publication":
        error("internal-draft-blueprint-pack-policy.json: invalid maturity")
        ok = False

    prohibited = " ".join(data.get("prohibited_blueprint_pack_actions", [])).lower()
    for term in PROHIBITED_ACTIONS:
        if term.replace("_", "") not in prohibited.replace("_", ""):
            error(f"internal-draft-blueprint-pack-policy.json: prohibited actions missing {term}")
            ok = False

    non_auth = " ".join(data.get("non_authorization_rules", [])).lower()
    for term in NON_AUTHORIZATION_TERMS:
        if term.replace("_", "") not in non_auth.replace("_", ""):
            error(f"internal-draft-blueprint-pack-policy.json: non_authorization_rules missing {term}")
            ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-blueprint-pack-policy.json: numeric scores prohibited")
        ok = False

    return ok


def validate_blueprint_pack() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "internal-draft-blueprint-pack-v1.json")
    evaluations = {
        e.get("candidate_id"): e
        for e in load_json(ROOT / "data" / "reference-candidate-evaluation-v1.json").get("evaluations", [])
    }
    section_ids = {
        c.get("section_contract_id")
        for c in load_json(ROOT / "data" / "internal-draft-section-contracts.json").get("section_contracts", [])
    }
    template_ids = {
        t.get("template_id")
        for t in load_json(ROOT / "data" / "internal-draft-template-registry.json").get("templates", [])
    }
    page_type_ids = {
        pt.get("page_type_id")
        for pt in load_json(ROOT / "data" / "reference-page-type-registry.json").get("page_types", [])
    }
    draft_gate_ids = {
        g.get("gate_id")
        for g in load_json(ROOT / "data" / "internal-draft-readiness-gates.json").get("gates", [])
    }
    pub_gate_ids = {
        g.get("gate_id")
        for g in load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    }

    missing = PACK_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-blueprint-pack-v1.json missing fields: {sorted(missing)}")
        ok = False

    blueprints = data.get("blueprints", [])
    if len(blueprints) != 4:
        error("internal-draft-blueprint-pack-v1.json: exactly 4 blueprint records required")
        ok = False

    ids = [b.get("blueprint_id") for b in blueprints]
    if set(ids) != set(REQUIRED_BLUEPRINT_IDS):
        error("internal-draft-blueprint-pack-v1.json: required blueprint IDs missing")
        ok = False

    selected = set(data.get("selected_candidates", []))
    if selected != set(REQUIRED_CANDIDATE_IDS):
        error("internal-draft-blueprint-pack-v1.json: selected candidates must be 0001, 0002, 0006, 0007")
        ok = False

    pack_blob = json.dumps(data).lower()
    for cid in EXCLUDED_CANDIDATE_IDS:
        if cid.lower() in pack_blob:
            error(f"internal-draft-blueprint-pack-v1.json: {cid} must not appear")
            ok = False

    for bp in blueprints:
        bid = bp.get("blueprint_id", "?")
        if not BLUEPRINT_ID_PATTERN.match(bid):
            error(f"blueprint pack: invalid blueprint_id {bid}")
            ok = False

        cid = bp.get("candidate_id", "")
        if cid not in evaluations:
            error(f"blueprint pack: {bid} references unevaluated candidate {cid}")
            ok = False
            continue

        readiness = evaluations[cid].get("readiness_state", "")
        if readiness not in ELIGIBLE_READINESS:
            error(f"blueprint pack: {bid} candidate {cid} readiness {readiness} not eligible")
            ok = False

        for field in BLUEPRINT_FIELDS:
            if field not in bp:
                error(f"blueprint pack: {bid} missing field {field}")
                ok = False

        for field, expected in [
            ("blueprint_status", "blueprint_created_internal"),
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
        ]:
            if bp.get(field) != expected:
                error(f"blueprint pack: {bid} {field} must be {expected}")
                ok = False

        expected_draft = (
            "internal_draft_created"
            if bid in ("DRAFT-BLUEPRINT-0001", "DRAFT-BLUEPRINT-0002")
            else "not_draft_created"
        )
        if bp.get("draft_status") != expected_draft:
            error(f"blueprint pack: {bid} draft_status must be {expected_draft}")
            ok = False

        if bp.get("page_type_ref") not in page_type_ids:
            error(f"blueprint pack: {bid} invalid page_type_ref")
            ok = False
        if bp.get("template_ref") not in template_ids:
            error(f"blueprint pack: {bid} invalid template_ref")
            ok = False

        for sid in bp.get("section_contracts", []):
            if sid not in section_ids:
                error(f"blueprint pack: {bid} invalid section contract {sid}")
                ok = False

        for gid in bp.get("required_gates", []):
            if not (DRAFT_GATE_PATTERN.match(gid) or PUB_GATE_PATTERN.match(gid)):
                error(f"blueprint pack: {bid} invalid gate {gid}")
                ok = False
            elif DRAFT_GATE_PATTERN.match(gid) and gid not in draft_gate_ids:
                error(f"blueprint pack: {bid} unknown draft gate {gid}")
                ok = False
            elif PUB_GATE_PATTERN.match(gid) and gid not in pub_gate_ids:
                error(f"blueprint pack: {bid} unknown publisher gate {gid}")
                ok = False

        stmt = bp.get("non_authorization_statement", "").lower()
        if "does not authorize" not in stmt:
            error(f"blueprint pack: {bid} missing non_authorization_statement")
            ok = False

        for text in collect_strings(bp):
            lower = text.lower()
            if word_count(text) > MAX_FIELD_WORDS:
                error(f"blueprint pack: {bid} field exceeds long-form prose limit")
                ok = False
            for term in PUBLIC_METADATA_TERMS:
                if term in lower and "no public" not in lower:
                    error(f"blueprint pack: {bid} contains public metadata term {term}")
                    ok = False
            for entity in REAL_ENTITY_TERMS:
                if entity in lower:
                    error(f"blueprint pack: {bid} contains real entity reference")
                    ok = False

        link_plan = bp.get("internal_link_plan", {})
        if link_plan.get("public_links_created") is True:
            error(f"blueprint pack: {bid} must not create public links")
            ok = False

    if json_has_numeric_scores(data):
        error("internal-draft-blueprint-pack-v1.json: numeric scores prohibited")
        ok = False

    return ok


def validate_blueprint_registry() -> bool:
    ok = True
    pack = load_json(ROOT / "data" / "internal-draft-blueprint-pack-v1.json")
    pack_by_id = {b.get("blueprint_id"): b for b in pack.get("blueprints", [])}

    data = load_json(ROOT / "data" / "internal-draft-blueprint-registry.json")
    missing = REGISTRY_TOP - set(data.keys())
    if missing:
        error(f"internal-draft-blueprint-registry.json missing fields: {sorted(missing)}")
        ok = False

    records = data.get("blueprint_records", [])
    if len(records) != 4:
        error("internal-draft-blueprint-registry.json: exactly 4 registry entries required")
        ok = False

    for entry in records:
        bid = entry.get("blueprint_id", "?")
        bp = pack_by_id.get(bid)
        if not bp:
            error(f"blueprint registry: {bid} not in pack")
            ok = False
            continue

        for field, expected in [
            ("blueprint_status", "blueprint_created_internal"),
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
        ]:
            if entry.get(field) != expected:
                error(f"blueprint registry: {bid} {field} must be {expected}")
                ok = False

        expected_draft = (
            "internal_draft_created"
            if bid in ("DRAFT-BLUEPRINT-0001", "DRAFT-BLUEPRINT-0002")
            else "not_draft_created"
        )
        if entry.get("draft_status") != expected_draft:
            error(f"blueprint registry: {bid} draft_status must be {expected_draft}")
            ok = False

        if bid in ("DRAFT-BLUEPRINT-0001", "DRAFT-BLUEPRINT-0002"):
            if bp.get("draft_status") != entry.get("draft_status"):
                error(f"blueprint registry: {bid} draft_status mismatch with pack")
                ok = False
        elif bp.get("draft_status") != entry.get("draft_status"):
            error(f"blueprint registry: {bid} draft_status mismatch with pack")
            ok = False

        if entry.get("candidate_id") != bp.get("candidate_id"):
            error(f"blueprint registry: {bid} candidate_id mismatch")
            ok = False

        if entry.get("blueprint_ref") != "data/internal-draft-blueprint-pack-v1.json":
            error(f"blueprint registry: {bid} blueprint_ref missing or wrong")
            ok = False

    return ok


def validate_candidate_registry() -> bool:
    ok = True
    registry = load_json(ROOT / "data" / "reference-page-candidate-registry.json")
    pack = load_json(ROOT / "data" / "internal-draft-blueprint-pack-v1.json")
    pack_candidates = {b.get("candidate_id") for b in pack.get("blueprints", [])}

    for entry in registry.get("candidates", []):
        cid = entry.get("candidate_id", "?")

        for field, expected in [
            ("route_status", "not_route_created"),
            ("sitemap_status", "not_sitemap_eligible"),
            ("publication_status", "publication_blocked"),
        ]:
            if entry.get(field) != expected:
                error(f"candidate registry: {cid} {field} must remain {expected}")
                ok = False

        draft_status = entry.get("draft_status", "")
        if draft_status not in ("not_draft_created", "internal_draft_created"):
            error(f"candidate registry: {cid} invalid draft_status {draft_status}")
            ok = False

        if cid in pack_candidates:
            if entry.get("internal_draft_blueprint_status") != "blueprint_created_internal":
                error(f"candidate registry: {cid} must have blueprint_created_internal status")
                ok = False
            if entry.get("internal_draft_blueprint_ref") != "data/internal-draft-blueprint-pack-v1.json":
                error(f"candidate registry: {cid} internal_draft_blueprint_ref missing or wrong")
                ok = False
            if entry.get("internal_draft_blueprint_pack_id") != "INT-DRAFT-BP-PACK-V1-001":
                error(f"candidate registry: {cid} internal_draft_blueprint_pack_id missing or wrong")
                ok = False
        elif cid == "REF-CAND-0008":
            status = entry.get("internal_draft_blueprint_status", "")
            if status in ("blueprint_created_internal", "blueprint_created"):
                error("candidate registry: REF-CAND-0008 must not have blueprint created")
                ok = False
            if entry.get("readiness_state") != "needs_boundary_refinement":
                error("candidate registry: REF-CAND-0008 must remain needs_boundary_refinement")
                ok = False
        else:
            bp_status = entry.get("internal_draft_blueprint_status", "")
            if bp_status == "blueprint_created_internal":
                error(f"candidate registry: {cid} must not be blueprint_created_internal")
                ok = False

    return ok


def validate_publisher_and_gates() -> bool:
    ok = True

    pub = load_json(ROOT / "data" / "publisher-governance-policy.json")
    status = pub.get("current_publisher_status", "")
    if status not in (
        "blocked_until_first_internal_draft_pack",
        "blocked_until_internal_draft_review_and_refinement",
        "blocked_until_public_route_readiness_gate",
        "blocked_until_first_controlled_public_reference_pilot",
        "blocked_until_public_reference_validation_and_live_surface_audit",
        "blocked_until_public_category_language_layer",
        "blocked_until_public_category_language_validation",
        "blocked_until_evidence_posture_workbench_governance",
        "blocked_until_evidence_posture_workbench_dry_run_harness",
        "blocked_until_workbench_specification_layer",
        "blocked_until_workbench_interface_blueprint_governance",
    ):
        error(
            f"publisher-governance-policy: current_publisher_status must be "
            f"blocked_until_first_internal_draft_pack, blocked_until_internal_draft_review_and_refinement, "
            f"blocked_until_public_route_readiness_gate, or blocked_until_first_controlled_public_reference_pilot, got {status}"
        )
        ok = False

    prohibited = " ".join(pub.get("prohibited_current_outputs", [])).lower()
    if "draft_pages" not in prohibited and "content_drafts" not in prohibited:
        error("publisher-governance-policy: actual drafts must remain prohibited")
        ok = False

    gates = load_json(ROOT / "data" / "publisher-quality-gates.json").get("gates", [])
    pack_gate = next((g for g in gates if g.get("gate_id") == "PUB-GATE-0020"), None)
    if not pack_gate:
        error("publisher-quality-gates: PUB-GATE-0020 missing")
        ok = False
    elif pack_gate.get("required_before_public_release") is not True or pack_gate.get("bypassable") is True:
        error("publisher-quality-gates: PUB-GATE-0020 must be required and not bypassable")
        ok = False
    else:
        notes = pack_gate.get("notes", "").lower()
        if "does not authorize" not in notes:
            error("publisher-quality-gates: PUB-GATE-0020 must not authorize outputs by itself")
            ok = False

    expansion = load_json(ROOT / "data" / "reference-expansion-gate.json")
    checks = " ".join(expansion.get("required_pre_release_checks", [])).lower()
    if "blueprint_pack" not in checks and "internal_draft_blueprint_pack" not in checks:
        error("reference-expansion-gate.json: must include blueprint pack pre-release check")
        ok = False

    return ok


def validate_route_sitemap_public_safety() -> bool:
    ok = True
    pack = load_json(ROOT / "data" / "internal-draft-blueprint-pack-v1.json")
    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])

    from public_surface_checks import validate_pilot_route_registry
    if not validate_pilot_route_registry(routes, error):
        ok = False

    from public_surface_checks import validate_candidate_paths_not_registered_except_pilot
    candidates = load_json(ROOT / "data" / "reference-candidate-pack-v1.json").get("candidates", [])
    if not validate_candidate_paths_not_registered_except_pilot(routes, candidates, error):
        ok = False

    from public_surface_checks import validate_pilot_sitemap
    try:
        if not validate_pilot_sitemap(routes, error):
            ok = False
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        ok = False

    for draft_dir in DRAFT_PATH_CANDIDATES:
        if draft_dir.exists():
            for item in draft_dir.rglob("*"):
                if item.is_file():
                    error(f"public safety: draft directory content at {item.relative_to(ROOT)}")
                    ok = False

    for html in ROOT.glob("**/*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel not in ALLOWED_PUBLIC_HTML:
            error(f"public safety: unexpected HTML file {rel}")
            ok = False

    return ok


def validate_cross_file() -> bool:
    ok = True
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    locations = {s.get("location") for s in sources}
    for loc in REQUIRED_SOURCE_LOCATIONS:
        if loc not in locations:
            error(f"source-registry.json: missing source for {loc}")
            ok = False

    content = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_internal_draft_blueprint_pack.py" not in content:
        error("validate_all.py: must include validate_internal_draft_blueprint_pack.py")
        ok = False

    return ok


def main() -> int:
    parse_paths = [
        "data/internal-draft-blueprint-pack-policy.json",
        "data/internal-draft-blueprint-pack-v1.json",
        "data/internal-draft-blueprint-registry.json",
        "data/internal-draft-template-registry.json",
        "data/internal-draft-section-contracts.json",
        "data/internal-draft-readiness-gates.json",
        "data/reference-candidate-evaluation-v1.json",
        "data/reference-page-candidate-registry.json",
        "data/publisher-governance-policy.json",
        "data/publisher-quality-gates.json",
        "data/reference-expansion-gate.json",
        "data/route-registry.json",
    ]
    for rel in parse_paths:
        try:
            load_json(ROOT / rel)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"{rel} parse failed: {exc}")
            return 1

    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap.xml parse failed: {exc}")
        return 1

    checks = [
        ("blueprint pack policy", validate_policy),
        ("blueprint pack", validate_blueprint_pack),
        ("blueprint registry", validate_blueprint_registry),
        ("candidate registry", validate_candidate_registry),
        ("publisher and gates", validate_publisher_and_gates),
        ("route sitemap public safety", validate_route_sitemap_public_safety),
        ("cross-file integration", validate_cross_file),
    ]

    all_ok = True
    for name, fn in checks:
        if not fn():
            all_ok = False

    if all_ok:
        print("PASS")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
