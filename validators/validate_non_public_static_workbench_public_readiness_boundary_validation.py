#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Public-Readiness Boundary Governance Validation v1."""

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
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
    validate_public_surface,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
)

PROTO_DIR = ROOT / "_internal_prototypes" / "evidence-posture-workbench"
INDEX_PATH = PROTO_DIR / "index.html"
CSS_PATH = PROTO_DIR / "prototype.css"
LOCKED_FILES = [
    "_internal_prototypes/evidence-posture-workbench/index.html",
    "_internal_prototypes/evidence-posture-workbench/prototype.css",
]
ALLOWED_FILES = {"index.html", "prototype.css"}
MATURE = "validation_only_public_readiness_boundary_no_public_release_no_engine_no_classifier_no_route"
STATUS = "governed_non_public_static_workbench_public_readiness_boundary_validation"
POLICY_STATUS = "governed_non_public_static_workbench_public_readiness_boundary_validation_policy"
DIMENSIONS = [
    "Public-Readiness Boundary Policy Integrity",
    "Public-Readiness Definition Integrity",
    "Public-Readiness Non-Authorization Integrity",
    "Public-Readiness Prerequisite Gate Integrity",
    "Locked Baseline Dependency Integrity",
    "Change-Control Dependency Integrity",
    "Public Route Exclusion",
    "Sitemap Exclusion",
    "Public Navigation Exclusion",
    "Homepage Link Exclusion",
    "Reference Page Link Exclusion",
    "Language Page Link Exclusion",
    "Prototype Files Not Modified",
    "No Additional Prototype Files",
    "No JavaScript",
    "No Forms or Inputs",
    "No Upload Surface",
    "No Scoring Surface",
    "No Fake/Real Verdict Surface",
    "No Generated Output Surface",
    "No API/Network/Storage Behavior",
    "No Analytics",
    "No DNS/Cloudflare/Deployment Change",
    "No Public Workbench Authorization",
    "No Public Engine Authorization",
    "No Public Classifier Authorization",
    "No Public Tool Authorization",
    "No Monetization Authorization",
    "No Public Release Authorization",
    "No Custom Domain Launch Authorization",
    "Public Surface Four-URL Integrity",
    "Public Isolation Integrity",
    "Static Safety Integrity",
    "Non-Operational Boundary Integrity",
    "Publisher Gate Alignment",
    "Reference Expansion Gate Alignment",
    "Python Cache Exclusion",
    "Evidence Ledger / Claim Map Alignment",
    "Source Registry Alignment",
    "Build Manifest Regeneration",
]
PROHIBITED_ACTIONS = [
    "modifying prototype files",
    "new prototype files",
    "prototype expansion",
    "public route creation",
    "sitemap expansion",
    "public navigation link",
    "interface behavior",
    "javascript",
    "forms",
    "inputs",
    "upload",
    "scoring",
    "fake/real output",
    "generated output",
    "engine",
    "classifier",
    "detector",
    "api",
    "analytics",
    "storage",
    "network calls",
    "monetization",
    "dns",
    "cloudflare",
    "custom domain launch",
    "deployment changes",
    "external factual claims",
    "subject accusation",
    "public release authorization",
    "python cache file commit",
]
PREREQ_KEYS = [
    "locked_visual_baseline_required",
    "baseline_lock_validation_required",
    "change_control_required",
    "public_isolation_required",
    "static_safety_required",
    "route_governance_required_before_public_route",
    "sitemap_governance_required_before_sitemap_expansion",
    "navigation_governance_required_before_public_linking",
    "engine_governance_required_before_engine",
    "classifier_governance_required_before_classifier",
    "upload_governance_required_before_upload",
    "scoring_governance_required_before_scoring",
    "API_governance_required_before_API",
    "analytics_governance_required_before_analytics",
    "deployment_governance_required_before_deployment",
    "DNS_Cloudflare_governance_required_before_custom_domain",
]
BLOCKED_AUTH = [
    "no_public_workbench_authorized",
    "no_public_route_authorized",
    "no_sitemap_expansion_authorized",
    "no_public_navigation_authorized",
    "no_engine_authorized",
    "no_classifier_authorized",
    "no_upload_authorized",
    "no_scoring_authorized",
    "no_API_authorized",
    "no_analytics_authorized",
    "no_DNS_authorized",
    "no_Cloudflare_authorized",
    "no_custom_domain_launch_authorized",
    "no_deployment_authorized",
    "no_monetization_authorized",
    "no_public_tool_authorized",
    "no_public_release_authorized",
]
SOURCE_LOCS = [
    "NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE_VALIDATION_V1.md",
    "data/non-public-static-workbench-public-readiness-boundary-validation-policy.json",
    "data/non-public-static-workbench-public-readiness-boundary-validation-results-v1.json",
    "data/non-public-static-workbench-public-readiness-prerequisite-validation-v1.json",
    "data/non-public-static-workbench-public-readiness-non-authorization-validation-v1.json",
    "data/non-public-static-workbench-public-readiness-public-isolation-audit-v1.json",
    "data/non-public-static-workbench-public-readiness-static-safety-audit-v1.json",
    "validators/validate_non_public_static_workbench_public_readiness_boundary_validation.py",
]
SPRINT42_PARSE = [
    "data/non-public-static-workbench-public-readiness-boundary-policy.json",
    "data/non-public-static-workbench-public-readiness-non-authorization-rules-v1.json",
    "data/non-public-static-workbench-public-readiness-required-prerequisites-v1.json",
    "data/non-public-static-workbench-public-readiness-risk-boundary-v1.json",
    "data/non-public-static-workbench-public-readiness-route-blockers-v1.json",
    "data/non-public-static-workbench-public-readiness-boundary-audit-v1.json",
]
BASELINE_PARSE = [
    "data/non-public-static-workbench-visual-system-baseline-lock-validation-results-v1.json",
    "data/non-public-static-workbench-visual-system-baseline-lock-record-v1.json",
    "data/non-public-static-workbench-visual-system-change-control-v1.json",
]
FORBIDDEN_OVERALL = [
    "public_route_readiness",
    "workbench_readiness",
    "engine_readiness",
    "classifier_readiness",
    "tool_readiness",
    "deployment_readiness",
    "dns_readiness",
    "cloudflare_readiness",
    "custom_domain_readiness",
    "monetization_readiness",
    "public_release_readiness",
]
NUMERIC_SCORE_PATTERN = re.compile(
    r"\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b",
    re.I,
)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(rel: str) -> dict:
    with (ROOT / rel).open(encoding="utf-8") as fh:
        return json.load(fh)


def has_all(container, required) -> bool:
    text = " ".join(str(x) for x in container).lower()
    return all(item.lower() in text or item.lower().replace("_", " ") in text for item in required)


def validate_doctrine() -> bool:
    ok = True
    text = (
        ROOT / "NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE_VALIDATION_V1.md"
    ).read_text(encoding="utf-8")
    required = [
        "Public-readiness boundary governance must be validated before public-readiness can be discussed operationally.",
        "A boundary for future public readiness is not permission to become public.",
        "Public-readiness boundary validation is a governance validation layer",
        "Sprint 42 public-readiness boundary governance",
        "maturity: validation_only_public_readiness_boundary_no_public_release_no_engine_no_classifier_no_route",
    ]
    for phrase in required:
        if phrase not in text:
            error(f"doctrine: missing {phrase}")
            ok = False
    for dim in DIMENSIONS:
        if dim not in text:
            error(f"doctrine: missing validation dimension {dim}")
            ok = False
    for term in [
        "public release approval",
        "public route approval",
        "workbench launch approval",
        "engine readiness",
        "classifier readiness",
        "deployment readiness",
        "sitemap expansion approval",
    ]:
        if term not in text.lower():
            error(f"doctrine: validation-is-not missing {term}")
            ok = False
    return ok


def validate_policy() -> bool:
    ok = True
    data = load_json("data/non-public-static-workbench-public-readiness-boundary-validation-policy.json")
    required = {
        "policy_id",
        "name",
        "version",
        "status",
        "maturity",
        "governing_principle",
        "identity_principle",
        "allowed_validation_actions",
        "prohibited_actions",
        "validation_scope",
        "correction_policy",
        "non_authorization_rules",
        "last_reviewed",
    }
    if not required.issubset(data):
        error("validation policy: missing top-level fields")
        ok = False
    if data.get("status") != POLICY_STATUS:
        error("validation policy: invalid status")
        ok = False
    if data.get("maturity") != MATURE:
        error("validation policy: invalid maturity")
        ok = False
    if not has_all(
        data.get("allowed_validation_actions", []),
        [
            "public-readiness boundary validation",
            "prerequisite validation",
            "non-authorization validation",
            "public isolation validation",
            "static safety validation",
            "publisher gate validation",
            "reference gate validation",
            "python cache exclusion validation",
            "validation only",
        ],
    ):
        error("validation policy: missing allowed validation actions")
        ok = False
    if not has_all(data.get("prohibited_actions", []), PROHIBITED_ACTIONS):
        error("validation policy: missing prohibited actions")
        ok = False
    if not has_all(
        data.get("validation_scope", []),
        [
            "Sprint 42 public-readiness boundary governance",
            "current prototype HTML",
            "current prototype CSS",
            "route registry exclusion",
            "sitemap exclusion",
            "public link exclusion",
            "publisher governance",
            "publisher gates",
            "reference expansion gate",
            "Python cache exclusion",
        ],
    ):
        error("validation policy: missing validation scope")
        ok = False
    correction = data.get("correction_policy", "").lower()
    for term in [
        "modify prototype files",
        "add files",
        "add routes",
        "add sitemap entries",
        "add public links",
        "add js",
        "add forms",
        "add inputs",
        "add upload",
        "add scoring",
        "add engine behavior",
        "add classifier behavior",
        "add api",
        "add analytics",
        "add deployment changes",
        "dns/cloudflare/custom domain",
        "commit python cache files",
    ]:
        if term not in correction:
            error(f"validation policy: correction policy missing {term}")
            ok = False
    blocked = " ".join(data.get("non_authorization_rules", {}).get("blocked", [])).lower()
    for term in [
        "public workbench",
        "public route",
        "sitemap expansion",
        "public navigation",
        "engine",
        "classifier",
        "upload",
        "scoring",
        "api",
        "analytics",
        "deployment",
        "dns",
        "cloudflare",
        "custom domain launch",
        "monetization",
        "public tool behavior",
        "prototype modification",
        "prototype expansion",
        "production readiness",
        "public release",
        "python cache commit",
    ]:
        if term not in blocked:
            error(f"validation policy: non-authorization missing {term}")
            ok = False
    if NUMERIC_SCORE_PATTERN.search(
        (ROOT / "data/non-public-static-workbench-public-readiness-boundary-validation-policy.json").read_text(
            encoding="utf-8"
        )
    ):
        error("validation policy: numeric score, grade, percentage, or SEO score found")
        ok = False
    return ok


def validate_results() -> bool:
    ok = True
    data = load_json("data/non-public-static-workbench-public-readiness-boundary-validation-results-v1.json")
    dims = data.get("validation_dimensions", [])
    names = [d.get("name") for d in dims]
    if names != DIMENSIONS:
        error("validation results: all 40 dimensions must exist in order")
        ok = False
    if any(d.get("result") != "pass" for d in dims):
        error("validation results: every dimension must pass")
        ok = False
    if data.get("overall_result") != "public_readiness_boundary_governance_validated":
        error("validation results: invalid overall_result")
        ok = False
    overall = data.get("overall_result", "").lower()
    for term in FORBIDDEN_OVERALL:
        if term in overall:
            error(f"validation results: overall_result implies {term}")
            ok = False
    if data.get("python_cache_result") != "python_cache_excluded":
        error("validation results: python_cache_result must be python_cache_excluded")
        ok = False
    return ok


def validate_prerequisite() -> bool:
    ok = True
    data = load_json("data/non-public-static-workbench-public-readiness-prerequisite-validation-v1.json")
    if data.get("status") != "non_public_static_workbench_public_readiness_prerequisites_validated":
        error("prerequisite validation: invalid status")
        ok = False
    if data.get("maturity") != "prerequisite_validation_only_no_public_release":
        error("prerequisite validation: invalid maturity")
        ok = False
    if data.get("overall_result") != "public_readiness_prerequisites_validated":
        error("prerequisite validation: invalid overall_result")
        ok = False
    results = data.get("prerequisite_results", {})
    for key in PREREQ_KEYS:
        if results.get(key) != "pass":
            error(f"prerequisite validation: missing or failing {key}")
            ok = False
    if data.get("missing_prerequisite_policy") != "missing_any_required_prerequisite_blocks_public_readiness_discussion":
        error("prerequisite validation: invalid missing_prerequisite_policy")
        ok = False
    return ok


def validate_non_authorization() -> bool:
    ok = True
    data = load_json("data/non-public-static-workbench-public-readiness-non-authorization-validation-v1.json")
    if data.get("status") != "non_public_static_workbench_public_readiness_non_authorization_validated":
        error("non-authorization validation: invalid status")
        ok = False
    if data.get("maturity") != "non_authorization_validation_only_no_public_release":
        error("non-authorization validation: invalid maturity")
        ok = False
    if data.get("overall_result") != "public_readiness_non_authorization_validated":
        error("non-authorization validation: invalid overall_result")
        ok = False
    blocked = data.get("blocked_authorization_results", {})
    for key in BLOCKED_AUTH:
        if blocked.get(key) != "pass":
            error(f"non-authorization validation: missing or failing {key}")
            ok = False
    if data.get("public_release_boundary_result") != "public_release_remains_blocked":
        error("non-authorization validation: public_release_boundary_result must be public_release_remains_blocked")
        ok = False
    return ok


def validate_isolation_and_static_safety() -> bool:
    ok = True
    isolation = load_json("data/non-public-static-workbench-public-readiness-public-isolation-audit-v1.json")
    expected = {
        "internal_prototype_location": "_internal_prototypes/evidence-posture-workbench/",
        "route_registry_result": "not_registered_as_public_route",
        "sitemap_result": "not_in_sitemap",
        "homepage_link_result": "not_linked_from_homepage",
        "reference_page_link_result": "not_linked_from_reference_pages",
        "language_page_link_result": "not_linked_from_language_page",
        "public_navigation_result": "not_linked_from_public_navigation",
        "public_surface_result": "public_surface_unchanged_four_urls",
        "overall_outcome": "public_readiness_public_isolation_validated",
    }
    for key, value in expected.items():
        if isolation.get(key) != value:
            error(f"public isolation audit: {key} must be {value}")
            ok = False
    safety = load_json("data/non-public-static-workbench-public-readiness-static-safety-audit-v1.json")
    if safety.get("overall_outcome") != "public_readiness_static_safety_validated":
        error("static safety audit: invalid overall_outcome")
        ok = False
    for key, required in {
        "prototype_file_results": [
            "prototype_files_not_modified_in_sprint_43",
            "only_index_and_css_in_prototype_directory",
            "no_additional_prototype_files",
            "no_new_prototype_directories",
        ],
        "html_safety_results": [
            "no_script_tags",
            "no_forms",
            "no_inputs",
            "no_textarea",
            "no_file_inputs",
            "no_buttons",
            "no_upload_controls",
            "no_generated_output_regions",
            "no_external_scripts",
            "no_external_libraries",
        ],
        "css_safety_results": [
            "no_imports",
            "no_external_urls",
            "no_upload_dropzone_styling",
            "no_scoring_gauge_styling",
            "no_red_green_verdict_styling",
            "no_detector_scanner_naming",
            "visual_tokens_present",
            "evidence_field_classes_present",
            "chamber_boundary_classes_present",
            "provenance_shadow_classes_present",
            "output_envelope_classes_present",
            "responsive_rules_present",
        ],
        "capability_block_results": [
            "no_engine",
            "no_classifier",
            "no_detector",
            "no_upload",
            "no_scoring",
            "no_fake_real",
            "no_api",
            "no_analytics",
            "no_storage",
            "no_network_calls",
            "no_deployment_change",
            "no_DNS_change",
            "no_Cloudflare_change",
            "no_custom_domain_launch",
        ],
        "content_safety_results": [
            "no_real_people",
            "no_real_companies",
            "no_real_institutions",
            "no_real_brands",
            "no_current_events",
            "no_political_events",
            "no_accusations",
            "no_external_factual_claims",
            "no_generated_analysis",
            "no_verified_certified_claims",
        ],
        "python_cache_results": [
            "no_pycache_tracked",
            "no_pyc_staged",
            "no_python_cache_committed",
        ],
    }.items():
        if not set(required).issubset(set(safety.get(key, {}).keys())):
            error(f"static safety audit: missing {key}")
            ok = False
    return ok


def validate_prototype_files() -> bool:
    ok = True
    if not INDEX_PATH.is_file() or not CSS_PATH.is_file():
        error("prototype index and css must exist")
        return False
    files = {p.name for p in PROTO_DIR.iterdir() if p.is_file()}
    if files != ALLOWED_FILES:
        error("prototype directory must contain only index.html and prototype.css")
        ok = False
    diff = subprocess.run(
        ["git", "diff", "--name-only", "--", *LOCKED_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", *LOCKED_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    if diff or staged:
        error("prototype files must not be modified or staged in Sprint 43")
        ok = False
    html = INDEX_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    lower_html = html.lower()
    if html.count("<h1") != 1:
        error("prototype html: expected exactly one H1")
        ok = False
    if "Evidence Posture Workbench — Static Prototype" not in html and "Evidence Posture Workbench - Static Prototype" not in html:
        if "Evidence Posture Workbench" not in html or "Static Prototype" not in html:
            error("prototype html: H1 must be Evidence Posture Workbench — Static Prototype")
            ok = False
    for forbidden in [
        "<script",
        "<form",
        "<input",
        "<textarea",
        'type="file"',
        "<button",
        "upload control",
        "generated output",
        "fake/real",
        "probability",
        "detector",
        "scanner",
    ]:
        if forbidden in lower_html:
            error(f"prototype html: forbidden {forbidden}")
            ok = False
    if 'href="prototype.css"' not in lower_html:
        error("prototype html: must link only to prototype.css")
        ok = False
    for phrase in [
        "Internal static prototype",
        "Non-public web surface",
        "Evidence Chamber",
        "Governed Evidence Field",
        "boundary rail",
        "provenance shadow",
        "missing context",
        "Not Assessable",
        "Refusal Gate",
        "Output Envelope",
        "Verification Path",
    ]:
        if phrase.lower() not in lower_html:
            error(f"prototype html: missing required language {phrase}")
            ok = False
    for zone in [
        "zone-boundary-header",
        "zone-artifact-context",
        "zone-provenance-context",
        "zone-missing-information",
        "zone-state-routing",
        "zone-refusal-boundary",
        "zone-output-envelope",
        "zone-verification-questions",
    ]:
        if zone not in html:
            error(f"prototype html: missing {zone}")
            ok = False
    lower_css = css.lower()
    for forbidden in ["@import", "url(", "dropzone", "gauge", "verdict", "fake", "real", "detector", "scanner"]:
        if forbidden in lower_css:
            error(f"prototype css: forbidden {forbidden}")
            ok = False
    for phrase in [
        "--background-field",
        "--chamber-surface",
        "--boundary-accent",
        "--provenance-shadow",
        "evidence-field",
        "evidence-chamber",
        "boundary-rail",
        "output-envelope",
        "@media",
    ]:
        if phrase.lower() not in lower_css:
            error(f"prototype css: missing {phrase}")
            ok = False
    return ok


def validate_public_safety() -> bool:
    ok = True
    routes = load_json("data/route-registry.json").get("routes", [])
    if not validate_public_surface(routes, error, PUBLIC_SITEMAP_URL_COUNT):
        ok = False
    route_text = json.dumps(routes).lower()
    if "internal_prototypes" in route_text or "evidence-posture-workbench" in route_text:
        error("route-registry: prototype must not be registered")
        ok = False
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [el.text.strip().lower() for el in tree.findall(".//{*}loc") if el.text]
    if len(locs) != 4:
        error("sitemap.xml must remain exactly 4 URLs")
        ok = False
    if any("internal_prototypes" in loc or "evidence-posture-workbench" in loc for loc in locs):
        error("sitemap.xml must not include prototype")
        ok = False
    link_pattern = re.compile(r"internal_prototypes|evidence-posture-workbench", re.I)
    for rel in [
        "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "language/index.html",
    ]:
        if link_pattern.search((ROOT / rel).read_text(encoding="utf-8")):
            error(f"{rel}: must not link to prototype")
            ok = False
    if (ROOT / ".nojekyll").exists():
        error(".nojekyll must not exist")
        ok = False
    return ok


def validate_governance_and_registry() -> bool:
    ok = True
    pub = load_json("data/publisher-governance-policy.json")
    if pub.get("current_publisher_status") not in (
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
        PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    ):
        error("publisher status must be blocked until public route eligibility governance")
        ok = False
    gates = load_json("data/publisher-quality-gates.json").get("gates", [])
    gate = next(
        (
            g
            for g in gates
            if g.get("name")
            == "Non-Public Static Workbench Public-Readiness Boundary Governance Validation Gate"
        ),
        None,
    )
    if not gate:
        error("public-readiness boundary validation gate missing")
        ok = False
    else:
        for field in [
            "required_before_public_route_eligibility_governance",
            "required_before_any_public_route",
            "required_before_any_interface_prototype_expansion",
            "required_before_engine_governance",
        ]:
            if gate.get(field) is not True:
                error(f"public-readiness boundary validation gate: {field} must be true")
                ok = False
        if gate.get("bypassable") is not False:
            error("public-readiness boundary validation gate must not be bypassable")
            ok = False
        notes = gate.get("notes", "").lower()
        for term in [
            "public engine",
            "public classifier",
            "public tool",
            "public route",
            "sitemap",
            "navigation",
            "upload",
            "scoring",
            "api",
            "forms",
            "analytics",
            "deployment",
            "dns",
            "cloudflare",
            "custom domain launch",
            "public release",
        ]:
            if term not in notes:
                error(f"public-readiness boundary validation gate notes missing {term}")
                ok = False
    exp = load_json("data/reference-expansion-gate.json")
    checks = " ".join(exp.get("required_pre_release_checks", [])).lower()
    rules = " ".join(exp.get("release_eligibility_rules", [])).lower()
    if "public_readiness_boundary_governance_validation" not in checks:
        error("reference gate missing public-readiness boundary governance validation")
        ok = False
    if "no_public_engine_eligibility_by_public_readiness_boundary_validation_alone" not in rules:
        error("reference gate must block engine eligibility by boundary validation alone")
        ok = False
    if "no_public_route_eligibility_by_boundary_validation_alone" not in rules:
        error("reference gate must block route eligibility by boundary validation alone")
        ok = False
    locs = {s.get("location") for s in load_json("data/source-registry.json").get("sources", [])}
    for loc in SOURCE_LOCS:
        if loc not in locs:
            error(f"source registry missing {loc}")
            ok = False
    ledger = load_json("data/evidence-ledger.json").get("claims", [])
    if not any(c.get("claim_id") == "CLAIM-0049" for c in ledger):
        error("CLAIM-0049 missing from evidence ledger")
        ok = False
    if not any(c.get("claim_id") == "CLAIM-0049" for c in load_json("data/claim-source-map.json").get("claim_source_links", [])):
        error("CLAIM-0049 missing from claim-source-map")
        ok = False
    validate_all = (ROOT / "validators" / "validate_all.py").read_text(encoding="utf-8")
    if "validate_non_public_static_workbench_public_readiness_boundary_validation.py" not in validate_all:
        error("validate_all.py must include sprint 43 validator")
        ok = False
    if "DEC-061" not in (ROOT / "DECISION_LOG.md").read_text(encoding="utf-8"):
        error("DEC-061 missing from DECISION_LOG.md")
        ok = False
    audit = load_json("data/non-public-static-workbench-public-readiness-boundary-audit-v1.json")
    if audit.get("overall_outcome") != "non_public_static_workbench_public_readiness_boundary_governance_validated":
        error("Sprint 42 boundary audit must show governance validated")
        ok = False
    return ok


def validate_python_cache() -> bool:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=False
    ).stdout.splitlines()
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True, check=False
    ).stdout.splitlines()
    for rel in tracked + staged:
        low = rel.lower().replace("\\", "/")
        if "__pycache__/" in low or low.endswith((".pyc", ".pyo", ".pyd")) or ".pytest_cache/" in low:
            error(f"python cache tracked or staged: {rel}")
            return False
    return True


def main() -> int:
    for rel in (
        [
            "data/non-public-static-workbench-public-readiness-boundary-validation-policy.json",
            "data/non-public-static-workbench-public-readiness-boundary-validation-results-v1.json",
            "data/non-public-static-workbench-public-readiness-prerequisite-validation-v1.json",
            "data/non-public-static-workbench-public-readiness-non-authorization-validation-v1.json",
            "data/non-public-static-workbench-public-readiness-public-isolation-audit-v1.json",
            "data/non-public-static-workbench-public-readiness-static-safety-audit-v1.json",
        ]
        + SPRINT42_PARSE
        + BASELINE_PARSE
        + [
            "data/publisher-governance-policy.json",
            "data/publisher-quality-gates.json",
            "data/reference-expansion-gate.json",
            "data/route-registry.json",
        ]
    ):
        try:
            load_json(rel)
        except Exception as exc:
            error(f"{rel} parse failed: {exc}")
            return 1
    for rel in [
        "sitemap.xml",
        "index.html",
        "reference/evidence-posture/index.html",
        "reference/artifact-subject-separation/index.html",
        "language/index.html",
        *LOCKED_FILES,
    ]:
        if not (ROOT / rel).is_file():
            error(f"{rel} missing")
            return 1
    try:
        ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as exc:
        error(f"sitemap parse failed: {exc}")
        return 1
    ok = all(
        fn()
        for fn in [
            validate_doctrine,
            validate_policy,
            validate_results,
            validate_prerequisite,
            validate_non_authorization,
            validate_isolation_and_static_safety,
            validate_prototype_files,
            validate_public_safety,
            validate_governance_and_registry,
            validate_python_cache,
        ]
    )
    if ok:
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
