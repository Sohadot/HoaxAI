#!/usr/bin/env python3
"""Validate Hoax.ai Category Intelligence Factory foundation registries and public surface."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent

EVIDENCE_POSTURES = {
    "conceptual",
    "repository_supported",
    "source_supported",
    "planned_not_claimed",
    "needs_review",
    "retired",
}

CLAIM_TYPES = {
    "conceptual_thesis",
    "operational_claim",
    "governance_claim",
    "external_factual_claim",
    "future_capability_claim",
}

LEDGER_REQUIRED = {
    "claim_id",
    "claim_text",
    "claim_type",
    "evidence_posture",
    "support_location",
    "source_type",
    "status",
    "last_reviewed",
    "notes",
}

ROUTE_REQUIRED = {
    "route_id",
    "path",
    "title",
    "route_type",
    "status",
    "index_policy",
    "canonical_url",
    "sitemap_included",
    "internal_linking_required",
    "public_surface",
    "deployment_status",
    "notes",
}

TERM_REQUIRED = {
    "term_id",
    "term",
    "canonical_status",
    "definition",
    "layer",
    "public_use_allowed",
    "related_terms",
    "prohibited_misreadings",
    "notes",
}

CLASS_REQUIRED = {
    "class_id",
    "class_name",
    "category",
    "definition",
    "allowed_use",
    "prohibited_use",
    "related_terms",
    "status",
    "notes",
}

SOURCE_REQUIRED = {
    "source_id",
    "source_title",
    "source_type",
    "location",
    "supports",
    "reliability_posture",
    "status",
    "notes",
}

CATEGORY_PROHIBITED = [
    "truth machine",
    "fake/real detector",
    "detects all",
    "guaranteed detection",
    "certifies truth",
    "proves guilt",
    "accuses",
    "fraud by association",
]

INDEX_FORBIDDEN = [
    "upload",
    "submit",
    "<form",
    "truth score",
    "first in the world",
    "scan your",
    "scan now",
    "deepfake detector",
    "try our detector",
    "active classifier",
    "live tool",
]

INDEX_CONDITIONAL = ["detect", "check", "verdict", "fake", "real", "scan", "analyze"]

NEGATION_PATTERN = re.compile(
    r"(?:does not|do not|not a|not an|never|no |cannot|can't|without)\s+[\w\s]{0,30}",
    re.IGNORECASE,
)

ID_PATTERNS = {
    "CLAIM": re.compile(r"^CLAIM-\d{4}$"),
    "ROUTE": re.compile(r"^ROUTE-\d{4}$"),
    "TERM": re.compile(r"^TERM-\d{4}$"),
    "CLASS": re.compile(r"^CLASS-\d{4}$"),
    "SOURCE": re.compile(r"^SOURCE-\d{4}$"),
}


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_unique_ids(items: list[dict], key: str, prefix: str, label: str) -> bool:
    ok = True
    seen: set[str] = set()
    pattern = ID_PATTERNS[prefix]
    for item in items:
        item_id = item.get(key, "")
        if not pattern.match(item_id):
            error(f"{label}: invalid ID format '{item_id}'")
            ok = False
        if item_id in seen:
            error(f"{label}: duplicate ID '{item_id}'")
            ok = False
        seen.add(item_id)
    return ok


def validate_required_fields(items: list[dict], required: set[str], label: str) -> bool:
    ok = True
    for item in items:
        item_id = item.get(next(iter(required), "id"), item.get("claim_id", "?"))
        missing = required - set(item.keys())
        if missing:
            error(f"{label} '{item_id}': missing fields {sorted(missing)}")
            ok = False
    return ok


def validate_evidence_ledger() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "evidence-ledger.json")
    claims = data.get("claims", [])
    ok &= validate_unique_ids(claims, "claim_id", "CLAIM", "evidence-ledger")
    ok &= validate_required_fields(claims, LEDGER_REQUIRED, "evidence-ledger")

    for claim in claims:
        cid = claim["claim_id"]
        posture = claim.get("evidence_posture")
        if posture not in EVIDENCE_POSTURES:
            error(f"evidence-ledger '{cid}': invalid evidence_posture '{posture}'")
            ok = False
        ctype = claim.get("claim_type")
        if ctype not in CLAIM_TYPES:
            error(f"evidence-ledger '{cid}': invalid claim_type '{ctype}'")
            ok = False
        if ctype == "future_capability_claim" and posture not in {
            "planned_not_claimed",
            "conceptual",
            "retired",
        }:
            error(
                f"evidence-ledger '{cid}': future capability must not be marked as existing"
            )
            ok = False
        if posture == "planned_not_claimed" and ctype not in {
            "future_capability_claim",
            "conceptual_thesis",
        }:
            error(
                f"evidence-ledger '{cid}': planned_not_claimed used on non-future claim"
            )
            ok = False
    return ok


def path_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if not path.endswith("/") and "." not in Path(path).name:
        path = path + "/"
    return path if path != "" else "/"


def validate_route_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "route-registry.json")
    routes = data.get("routes", [])
    ok &= validate_unique_ids(routes, "route_id", "ROUTE", "route-registry")
    ok &= validate_required_fields(routes, ROUTE_REQUIRED, "route-registry")

    paths = {r["path"] for r in routes}
    if "/" not in paths:
        error("route-registry: route / must exist")
        ok = False

    sitemap_paths: set[str] = set()
    registry_sitemap_paths: set[str] = set()

    for route in routes:
        if route.get("sitemap_included"):
            registry_sitemap_paths.add(route["path"])

    sitemap_file = ROOT / "sitemap.xml"
    if sitemap_file.exists():
        tree = ElementTree.parse(sitemap_file)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for loc in tree.findall(".//sm:loc", ns):
            if loc.text:
                sitemap_paths.add(path_from_url(loc.text.strip()))

        for sp in sorted(sitemap_paths):
            if sp not in paths:
                error(f"sitemap.xml: URL path '{sp}' not in route-registry.json")
                ok = False

        for rp in sorted(registry_sitemap_paths):
            if rp not in sitemap_paths:
                error(
                    f"route-registry: sitemap_included path '{rp}' missing from sitemap.xml"
                )
                ok = False

    deferred = [
        r for r in routes if r.get("deployment_status") == "external_deployment_deferred"
    ]
    if not deferred:
        error("route-registry: external_deployment_deferred status expected for deferred routes")
        ok = False

    return ok


def validate_category_language() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "category-language.json")
    terms = data.get("terms", [])
    ok &= validate_unique_ids(terms, "term_id", "TERM", "category-language")
    ok &= validate_required_fields(terms, TERM_REQUIRED, "category-language")

    for term in terms:
        tid = term["term_id"]
        definition = term.get("definition", "").lower()
        for phrase in CATEGORY_PROHIBITED:
            if phrase in definition:
                error(
                    f"category-language '{tid}': prohibited product language '{phrase}' in definition"
                )
                ok = False
    return ok


def validate_ontology_foundation() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "ontology-foundation.json")
    classes = data.get("classes", [])
    ok &= validate_unique_ids(classes, "class_id", "CLASS", "ontology-foundation")
    ok &= validate_required_fields(classes, CLASS_REQUIRED, "ontology-foundation")

    subject = None
    posture_class = None
    for cls in classes:
        if cls.get("class_name") == "SubjectReference":
            subject = cls
        if cls.get("class_name") == "EvidencePostureClassification":
            posture_class = cls

    if subject is None:
        error("ontology-foundation: SubjectReference class missing")
        ok = False
    else:
        combined = " ".join(
            [
                subject.get("definition", ""),
                subject.get("prohibited_use", ""),
                subject.get("notes", ""),
            ]
        ).lower()
        boundary_markers = [
            "artifact–subject separation",
            "artifact-subject separation",
            "not a classification target",
            "not evidence about people",
        ]
        if not any(marker in combined for marker in boundary_markers):
            error(
                "ontology-foundation: SubjectReference missing artifact–subject boundary language"
            )
            ok = False

    if posture_class is None:
        error("ontology-foundation: EvidencePostureClassification class missing")
        ok = False
    else:
        combined = " ".join(
            [
                posture_class.get("definition", ""),
                posture_class.get("prohibited_use", ""),
                posture_class.get("status", ""),
                posture_class.get("notes", ""),
            ]
        ).lower()
        if "active tool" in combined and "not" not in combined.split("active tool")[0][-20:]:
            pass
        active_markers = ["active tool", "live scoring", "currently deployed", "operational tool"]
        for marker in active_markers:
            if marker in combined and "not" not in combined:
                # allow if marker only in prohibited_use negation context
                if marker in posture_class.get("prohibited_use", "").lower():
                    continue
                error(
                    f"ontology-foundation: EvidencePostureClassification described as active tool ('{marker}')"
                )
                ok = False
        if posture_class.get("status") != "planned_not_deployed":
            error(
                "ontology-foundation: EvidencePostureClassification must be planned_not_deployed"
            )
            ok = False

    for cls in classes:
        prohibited = cls.get("prohibited_use", "").lower()
        definition = cls.get("definition", "").lower()
        for phrase in [
            "classify people",
            "classify institutions",
            "classify the person",
            "subject accusation target",
            "guilt assessment of",
        ]:
            if phrase in definition and cls.get("class_name") != "SubjectReference":
                error(
                    f"ontology-foundation '{cls['class_id']}': class describes people/institutions as classification targets"
                )
                ok = False
    return ok


def validate_source_registry() -> bool:
    ok = True
    data = load_json(ROOT / "data" / "source-registry.json")
    sources = data.get("sources", [])
    ok &= validate_unique_ids(sources, "source_id", "SOURCE", "source-registry")
    ok &= validate_required_fields(sources, SOURCE_REQUIRED, "source-registry")

    for source in sources:
        sid = source["source_id"]
        location = source.get("location", "")
        stype = source.get("source_type", "")
        if stype.startswith("internal"):
            if not (ROOT / location).exists():
                error(f"source-registry '{sid}': internal source file missing '{location}'")
                ok = False
        if stype == "external_web":
            error(f"source-registry '{sid}': unsupported external factual source in Sprint 1D")
            ok = False
    return ok


def line_has_unnegated_term(line: str, term: str) -> bool:
    lower = line.lower()
    if term not in lower:
        return False

    line_negations = [
        "does not",
        "do not",
        "not a ",
        "not an ",
        "no absolute",
        "not absolute",
        "never the ",
        "not on connected",
        "not to any person",
        "planned,",
        "under development",
    ]
    if any(neg in lower for neg in line_negations):
        return False

    idx = 0
    while True:
        pos = lower.find(term, idx)
        if pos == -1:
            return False
        prefix = lower[max(0, pos - 50) : pos]
        if not NEGATION_PATTERN.search(prefix + term):
            return True
        idx = pos + len(term)
    return False


def validate_public_surface() -> bool:
    ok = True
    index_path = ROOT / "index.html"
    if not index_path.exists():
        error("public surface: index.html missing")
        return False

    content = index_path.read_text(encoding="utf-8")
    lower = content.lower()

    h1_count = len(re.findall(r"<h1\b", content, re.IGNORECASE))
    if h1_count != 1:
        error(f"public surface: expected exactly one H1, found {h1_count}")
        ok = False

    for phrase in INDEX_FORBIDDEN:
        if phrase in lower:
            error(f"public surface: forbidden phrase '{phrase}' in index.html")
            ok = False

    for line in content.splitlines():
        line_lower = line.lower()
        for term in INDEX_CONDITIONAL:
            if term in line_lower and line_has_unnegated_term(line, term):
                error(
                    f"public surface: '{term}' in index.html may imply live tool without clear negation"
                )
                ok = False

    artifact_markers = [
        "evidence artifact",
        "artifact–subject",
        "artifact-subject",
        "not on connected subjects",
        "not a statement about people",
    ]
    if not any(marker in lower for marker in artifact_markers):
        error("public surface: artifact–subject separation language not visible")
        ok = False

    return ok


def validate_json_files() -> bool:
    ok = True
    for rel in [
        "data/evidence-ledger.json",
        "data/route-registry.json",
        "data/category-language.json",
        "data/ontology-foundation.json",
        "data/source-registry.json",
    ]:
        path = ROOT / rel
        try:
            load_json(path)
        except (json.JSONDecodeError, OSError) as exc:
            error(f"JSON parse failed for {rel}: {exc}")
            ok = False
    return ok


def main() -> int:
    checks = [
        ("JSON validity", validate_json_files),
        ("Evidence ledger", validate_evidence_ledger),
        ("Route registry", validate_route_registry),
        ("Category language", validate_category_language),
        ("Ontology foundation", validate_ontology_foundation),
        ("Source registry", validate_source_registry),
        ("Public surface", validate_public_surface),
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
