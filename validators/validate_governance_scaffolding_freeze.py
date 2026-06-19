#!/usr/bin/env python3
"""Validate Sprint 52 — Governance Scaffolding Freeze and Public Reference Production Reset v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ERRORS: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


def main() -> int:
    # 1. GOVERNANCE_SCAFFOLDING_FREEZE_AND_PUBLIC_PRODUCTION_MANDATE.md exists
    freeze_mandate = ROOT / "GOVERNANCE_SCAFFOLDING_FREEZE_AND_PUBLIC_PRODUCTION_MANDATE.md"
    check(freeze_mandate.exists(), "GOVERNANCE_SCAFFOLDING_FREEZE_AND_PUBLIC_PRODUCTION_MANDATE.md must exist")

    # 2. PUBLIC_REFERENCE_PRODUCTION_PLAN_V1.md exists
    production_plan_md = ROOT / "PUBLIC_REFERENCE_PRODUCTION_PLAN_V1.md"
    check(production_plan_md.exists(), "PUBLIC_REFERENCE_PRODUCTION_PLAN_V1.md must exist")

    # 3. data/governance-scaffolding-freeze-policy.json parses
    freeze_policy_path = ROOT / "data" / "governance-scaffolding-freeze-policy.json"
    freeze_policy = None
    if freeze_policy_path.exists():
        try:
            with freeze_policy_path.open() as f:
                freeze_policy = json.load(f)
        except Exception as e:
            check(False, f"data/governance-scaffolding-freeze-policy.json must parse as valid JSON: {e}")
    else:
        check(False, "data/governance-scaffolding-freeze-policy.json must exist")

    # 4. data/public-reference-production-plan-v1.json parses
    prod_plan_path = ROOT / "data" / "public-reference-production-plan-v1.json"
    prod_plan = None
    if prod_plan_path.exists():
        try:
            with prod_plan_path.open() as f:
                prod_plan = json.load(f)
        except Exception as e:
            check(False, f"data/public-reference-production-plan-v1.json must parse as valid JSON: {e}")
    else:
        check(False, "data/public-reference-production-plan-v1.json must exist")

    # 5. production threshold is 10
    if freeze_policy is not None:
        threshold = freeze_policy.get("production_threshold", {}).get("minimum_additional_public_reference_pages")
        check(threshold == 10, f"production_threshold.minimum_additional_public_reference_pages must be 10, got {threshold}")

    # 6. immediate next phase is public_reference_page_production
    if freeze_policy is not None:
        next_phase = freeze_policy.get("immediate_next_phase")
        check(
            next_phase == "public_reference_page_production",
            f"immediate_next_phase must be 'public_reference_page_production', got '{next_phase}'"
        )

    # 7. frozen work types include public route candidate registration authorization governance
    #    and governance validation of governance validation
    if freeze_policy is not None:
        frozen = freeze_policy.get("frozen_work_types", [])
        check(
            "public_route_candidate_registration_authorization_governance" in frozen,
            "frozen_work_types must include 'public_route_candidate_registration_authorization_governance'"
        )
        check(
            "governance_validation_of_governance_validation" in frozen,
            "frozen_work_types must include 'governance_validation_of_governance_validation'"
        )

    # 8. allowed work types include public reference page creation and route/sitemap expansion
    if freeze_policy is not None:
        allowed = freeze_policy.get("allowed_work_types", [])
        check(
            "public_reference_page_creation" in allowed,
            "allowed_work_types must include 'public_reference_page_creation'"
        )
        has_route_or_sitemap = any("route" in w or "sitemap" in w for w in allowed)
        check(
            has_route_or_sitemap,
            "allowed_work_types must include route or sitemap expansion items for real public reference pages"
        )

    # 9. production plan includes at least 10 page candidates
    if prod_plan is not None:
        candidates = prod_plan.get("page_candidates", [])
        check(len(candidates) >= 10, f"production plan must include at least 10 page_candidates, found {len(candidates)}")

    # 10. initial release batch includes exactly the 4 Sprint 53 pages
    required_batch = {
        "/reference/source-confidence/",
        "/reference/provenance-gap/",
        "/reference/not-assessable/",
        "/reference/output-boundary/",
    }
    if freeze_policy is not None:
        batch = set(freeze_policy.get("initial_release_batch", []))
        check(batch == required_batch, f"freeze policy initial_release_batch must be exactly {sorted(required_batch)}, got {sorted(batch)}")
    if prod_plan is not None:
        prod_batch = set(prod_plan.get("initial_release_batch", []))
        check(prod_batch == required_batch, f"production plan initial_release_batch must be exactly {sorted(required_batch)}, got {sorted(prod_batch)}")

    # 11. non-authorization rules preserve exclusions for engine, classifier, upload, scoring,
    #     API, analytics, DNS, Cloudflare, custom domain launch, monetization, public tool
    if freeze_policy is not None:
        non_auth = freeze_policy.get("non_authorization_rules", [])
        required_terms = [
            "engine", "classifier", "upload", "scoring", "api",
            "analytics", "dns", "cloudflare", "custom_domain", "monetization", "public_tool"
        ]
        for term in required_terms:
            found = any(term in rule for rule in non_auth)
            check(found, f"non_authorization_rules must include a rule containing '{term}'")

    # 12. validate_all.py includes this validator
    validate_all_path = ROOT / "validators" / "validate_all.py"
    if validate_all_path.exists():
        content = validate_all_path.read_text()
        check(
            "validate_governance_scaffolding_freeze" in content,
            "validators/validate_all.py must reference validate_governance_scaffolding_freeze"
        )
    else:
        check(False, "validators/validate_all.py must exist")

    # 13. DECISION_LOG.md includes DEC-070
    decision_log = ROOT / "DECISION_LOG.md"
    if decision_log.exists():
        content = decision_log.read_text()
        check("DEC-070" in content, "DECISION_LOG.md must include DEC-070")
    else:
        check(False, "DECISION_LOG.md must exist")

    # 14. ROADMAP.md marks next phase as Public Reference Production Batch 1
    roadmap = ROOT / "ROADMAP.md"
    if roadmap.exists():
        content = roadmap.read_text()
        check(
            "Public Reference Production Batch 1" in content or "Sprint 53" in content,
            "ROADMAP.md must mark next phase as Public Reference Production Batch 1 (Sprint 53)"
        )
        check("Sprint 52" in content, "ROADMAP.md must include Sprint 52 section")
    else:
        check(False, "ROADMAP.md must exist")

    # 15. MASTER_EXECUTION_PLAN.md records the freeze and production mandate
    master_plan = ROOT / "MASTER_EXECUTION_PLAN.md"
    if master_plan.exists():
        content = master_plan.read_text()
        check(
            "G52" in content or "Governance Scaffolding Freeze" in content,
            "MASTER_EXECUTION_PLAN.md must record the governance scaffolding freeze (G52)"
        )
    else:
        check(False, "MASTER_EXECUTION_PLAN.md must exist")

    # 16. CATEGORY_INTELLIGENCE_FACTORY_PLAN.md states governance protects production
    cifp = ROOT / "CATEGORY_INTELLIGENCE_FACTORY_PLAN.md"
    if cifp.exists():
        content = cifp.read_text()
        check(
            "protect production" in content.lower() or "governance must protect production" in content.lower(),
            "CATEGORY_INTELLIGENCE_FACTORY_PLAN.md must state that governance protects production rather than replacing it"
        )
    else:
        check(False, "CATEGORY_INTELLIGENCE_FACTORY_PLAN.md must exist")

    # 17. sitemap remains unchanged in Sprint 52 (at most 4 URLs)
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        sitemap_content = sitemap.read_text()
        url_count = sitemap_content.count("<loc>")
        check(url_count <= 4, f"sitemap.xml must have at most 4 URLs in Sprint 52, found {url_count}")

    # 18. route registry remains unchanged (at most 4 active routes)
    route_registry = ROOT / "data" / "route-registry.json"
    if route_registry.exists():
        with route_registry.open() as f:
            rr = json.load(f)
        routes = rr.get("routes", [])
        active_routes = [r for r in routes if r.get("status") == "active"]
        check(len(active_routes) <= 4, f"route registry must have at most 4 active routes in Sprint 52, found {len(active_routes)}")

    # 19. prototype files exist and are not deleted
    prototype_index = ROOT / "_internal_prototypes" / "evidence-posture-workbench" / "index.html"
    prototype_css = ROOT / "_internal_prototypes" / "evidence-posture-workbench" / "prototype.css"
    check(prototype_index.exists(), "_internal_prototypes/evidence-posture-workbench/index.html must exist (must not be deleted)")
    check(prototype_css.exists(), "_internal_prototypes/evidence-posture-workbench/prototype.css must exist (must not be deleted)")

    # 20. no Python cache files exist in the repository
    pycache_dirs = list(ROOT.rglob("__pycache__"))
    pyc_files = list(ROOT.rglob("*.pyc"))
    check(len(pycache_dirs) == 0, f"No __pycache__ directories should exist in repository: found {len(pycache_dirs)}")
    check(len(pyc_files) == 0, f"No .pyc files should exist in repository: found {len(pyc_files)}")

    # 21. this validator itself exists
    this_validator = ROOT / "validators" / "validate_governance_scaffolding_freeze.py"
    check(this_validator.exists(), "validators/validate_governance_scaffolding_freeze.py must exist")

    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}")
        return 1

    print("PASS: validate_governance_scaffolding_freeze.py — all Sprint 52 conditions verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
