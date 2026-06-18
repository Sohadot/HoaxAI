#!/usr/bin/env python3
"""Run all Hoax.ai repository validators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATORS = [
    ROOT / "validators" / "validate_factory_foundation.py",
    ROOT / "validators" / "validate_adversarial_enforcement.py",
    ROOT / "validators" / "validate_interface_governance.py",
    ROOT / "validators" / "validate_security_privacy_boundary.py",
    ROOT / "validators" / "validate_link_route_integrity.py",
    ROOT / "validators" / "validate_claim_source_traceability.py",
    ROOT / "validators" / "validate_technical_quality_gate.py",
    ROOT / "validators" / "validate_reference_page_blueprint.py",
    ROOT / "validators" / "validate_automation_governance.py",
    ROOT / "validators" / "validate_publisher_control_plane.py",
    ROOT / "validators" / "validate_content_quality_standard.py",
    ROOT / "validators" / "validate_structured_data_semantic_seo.py",
    ROOT / "validators" / "validate_publisher_dry_run.py",
    ROOT / "validators" / "validate_reference_candidate_pack.py",
    ROOT / "validators" / "validate_reference_candidate_evaluation.py",
    ROOT / "validators" / "validate_internal_draft_blueprint_governance.py",
    ROOT / "validators" / "validate_internal_draft_blueprint_pack.py",
    ROOT / "validators" / "validate_internal_draft_pack.py",
    ROOT / "validators" / "validate_internal_draft_review.py",
    ROOT / "validators" / "validate_public_route_readiness_gate.py",
    ROOT / "validators" / "validate_controlled_public_reference_pilot.py",
    ROOT / "validators" / "validate_public_reference_live_surface.py",
    ROOT / "validators" / "validate_public_category_language_layer.py",
    ROOT / "validators" / "validate_public_category_language_validation.py",
    ROOT / "validators" / "validate_evidence_posture_workbench_governance.py",
    ROOT / "validators" / "validate_evidence_posture_workbench_dry_run.py",
    ROOT / "validators" / "validate_evidence_posture_workbench_specification.py",
    ROOT / "validators" / "validate_evidence_posture_workbench_interface_blueprint.py",
    ROOT / "validators" / "validate_evidence_posture_workbench_interface_blueprint_validation.py",
]
MANIFEST_GENERATOR = ROOT / "validators" / "generate_build_manifest.py"


def run_step(label: str, command: list[str]) -> int:
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"ERROR: {label} failed with exit code {result.returncode}")
    return result.returncode


def main() -> int:
    exit_code = 0

    if not (ROOT / "BUILD_MANIFEST.json").exists() and MANIFEST_GENERATOR.exists():
        code = run_step(
            "generate_build_manifest.py (bootstrap)",
            [sys.executable, str(MANIFEST_GENERATOR)],
        )
        if code != 0:
            return code

    for validator in VALIDATORS:
        if not validator.exists():
            print(f"ERROR: validator missing: {validator}")
            exit_code = 1
            continue
        code = run_step(validator.name, [sys.executable, str(validator)])
        if code != 0:
            exit_code = code

    if exit_code != 0:
        return exit_code

    if not MANIFEST_GENERATOR.exists():
        print(f"ERROR: manifest generator missing: {MANIFEST_GENERATOR}")
        return 1

    code = run_step("generate_build_manifest.py", [sys.executable, str(MANIFEST_GENERATOR)])
    if code != 0:
        return code

    foundation = ROOT / "validators" / "validate_factory_foundation.py"
    code = run_step(
        "validate_factory_foundation.py (post-manifest)",
        [sys.executable, str(foundation)],
    )
    if code != 0:
        return code

    return 0


if __name__ == "__main__":
    sys.exit(main())
