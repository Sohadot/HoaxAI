#!/usr/bin/env python3
"""Generate BUILD_MANIFEST.json for Hoax.ai repository integrity metadata."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "BUILD_MANIFEST.json"

GOVERNANCE_FILES = [
    "ADVERSARIAL_ENFORCEMENT_HARNESS.md",
    "INTERFACE_EMBODIMENT_GOVERNANCE.md",
    "INTERFACE_THESIS.md",
    "SECURITY_PRIVACY_BOUNDARY.md",
    "LINK_ROUTE_INTEGRITY_POLICY.md",
    "CLAIM_SOURCE_TRACEABILITY_POLICY.md",
    "TECHNICAL_QUALITY_GATE.md",
    "REFERENCE_PAGE_BLUEPRINT.md",
    "AUTOMATION_GOVERNANCE.md",
    "AGENT_EXECUTION_RULES.md",
    "GOVERNED_PUBLISHER_CONTROL_PLANE.md",
    "CONTENT_QUALITY_REFERENCE_SUBSTANCE_STANDARD.md",
    "INTERNAL_ENGINE_MODEL.md",
    "OUTPUT_BOUNDARY_SCHEMA.md",
    "EVIDENCE_POSTURE_CLASSIFICATION_PROTOCOL.md",
    "EVIDENCE_POSTURE_STANDARD.md",
    "EVIDENCE_POSTURE_TAXONOMY.md",
    "GOVERNANCE_BOUNDARY.md",
    "CLAIM_POLICY.md",
    "DECISION_LOG.md",
    "ROADMAP.md",
    "MASTER_EXECUTION_PLAN.md",
    "CATEGORY_INTELLIGENCE_FACTORY_PLAN.md",
]

DATA_FILES = [
    "data/evidence-ledger.json",
    "data/route-registry.json",
    "data/category-language.json",
    "data/ontology-foundation.json",
    "data/source-registry.json",
    "data/evidence-posture-taxonomy.json",
    "data/evidence-posture-standard.json",
    "data/evidence-posture-protocol.json",
    "data/output-boundary-schema.json",
    "data/internal-engine-model.json",
    "data/internal-engine-fixtures.json",
    "data/forbidden-language-policy.json",
    "data/adversarial-validation-cases.json",
    "data/interface-grammar.json",
    "data/interface-component-registry.json",
    "data/interface-surface-map.json",
    "data/security-privacy-boundary.json",
    "data/interaction-permission-registry.json",
    "data/external-dependency-registry.json",
    "data/link-route-integrity-policy.json",
    "data/internal-link-graph.json",
    "data/claim-source-traceability-policy.json",
    "data/claim-source-map.json",
    "data/public-claim-map.json",
    "data/technical-quality-gate.json",
    "data/public-file-registry.json",
    "data/html-metadata-registry.json",
    "data/reference-page-blueprint.json",
    "data/reference-page-type-registry.json",
    "data/reference-expansion-gate.json",
    "data/reference-page-candidate-registry.json",
    "data/automation-governance-policy.json",
    "data/ci-quality-gate-policy.json",
    "data/publisher-governance-policy.json",
    "data/publisher-workflow-registry.json",
    "data/publisher-state-machine.json",
    "data/publisher-quality-gates.json",
    "data/publisher-queue-registry.json",
    "data/content-quality-standard.json",
    "data/reference-substance-rules.json",
    "data/thin-content-failure-patterns.json",
    "data/reference-section-requirements.json",
]

VALIDATORS = [
    "validators/validate_all.py",
    "validators/validate_factory_foundation.py",
    "validators/validate_adversarial_enforcement.py",
    "validators/validate_interface_governance.py",
    "validators/validate_security_privacy_boundary.py",
    "validators/validate_link_route_integrity.py",
    "validators/validate_claim_source_traceability.py",
    "validators/validate_technical_quality_gate.py",
    "validators/validate_reference_page_blueprint.py",
    "validators/validate_automation_governance.py",
    "validators/validate_publisher_control_plane.py",
    "validators/validate_content_quality_standard.py",
    "validators/generate_build_manifest.py",
]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit_sha() -> tuple[str | None, str | None]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip(), None
        return None, result.stderr.strip() or "git rev-parse failed"
    except OSError as exc:
        return None, str(exc)


def main() -> int:
    commit_sha, commit_note = git_commit_sha()

    routes = load_json(ROOT / "data" / "route-registry.json").get("routes", [])
    category_terms = load_json(ROOT / "data" / "category-language.json").get("terms", [])
    ontology_classes = load_json(ROOT / "data" / "ontology-foundation.json").get("classes", [])
    sources = load_json(ROOT / "data" / "source-registry.json").get("sources", [])
    claims = load_json(ROOT / "data" / "evidence-ledger.json").get("claims", [])

    taxonomy = load_json(ROOT / "data" / "evidence-posture-taxonomy.json")
    standard = load_json(ROOT / "data" / "evidence-posture-standard.json")
    protocol = load_json(ROOT / "data" / "evidence-posture-protocol.json")
    output_schema = load_json(ROOT / "data" / "output-boundary-schema.json")
    engine_model = load_json(ROOT / "data" / "internal-engine-model.json")

    sitemap_count = 0
    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        content = sitemap_path.read_text(encoding="utf-8")
        sitemap_count = content.count("<loc>")

    tracked_paths = GOVERNANCE_FILES + DATA_FILES + VALIDATORS + ["index.html", "sitemap.xml"]
    file_hashes: dict[str, str | None] = {}
    for rel in tracked_paths:
        file_hashes[rel] = sha256_file(ROOT / rel)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit_sha": commit_sha,
        "commit_sha_note": commit_note,
        "validator_entrypoint": "validators/validate_all.py",
        "validator_status": "pending_until_validate_all",
        "route_count": len(routes),
        "sitemap_url_count": sitemap_count,
        "category_term_count": len(category_terms),
        "ontology_class_count": len(ontology_classes),
        "source_count": len(sources),
        "evidence_claim_count": len(claims),
        "taxonomy_version": taxonomy.get("version"),
        "standard_version": standard.get("version"),
        "protocol_version": protocol.get("version"),
        "output_schema_version": output_schema.get("version"),
        "engine_model_version": engine_model.get("version"),
        "governance_files": GOVERNANCE_FILES,
        "data_files": DATA_FILES,
        "validators": VALIDATORS,
        "file_hashes": file_hashes,
        "deployment_status": "external_deployment_deferred",
        "notes": "Internal repository integrity metadata. Not public certification.",
    }

    with MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    print(f"Generated {MANIFEST_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
