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
    ROOT / "validators" / "validate_non_public_static_workbench_prototype_governance.py",
    ROOT / "validators" / "validate_non_public_static_workbench_prototype_v1.py",
    ROOT / "validators" / "validate_non_public_static_workbench_prototype_validation.py",
    ROOT / "validators" / "validate_non_public_static_workbench_prototype_refinement.py",
    ROOT / "validators" / "validate_non_public_static_workbench_prototype_refinement_validation.py",
    ROOT / "validators" / "validate_non_public_static_workbench_visual_system_hardening.py",
    ROOT / "validators" / "validate_non_public_static_workbench_visual_system_hardening_validation.py",
    ROOT / "validators" / "validate_non_public_static_workbench_visual_system_baseline_lock.py",
    ROOT / "validators" / "validate_non_public_static_workbench_visual_system_baseline_lock_validation.py",
    ROOT / "validators" / "validate_non_public_static_workbench_public_readiness_boundary_governance.py",
    ROOT / "validators" / "validate_non_public_static_workbench_public_readiness_boundary_validation.py",
    ROOT / "validators" / "validate_public_route_eligibility_governance.py",
    ROOT / "validators" / "validate_public_route_eligibility_governance_validation.py",
    ROOT / "validators" / "validate_public_route_candidate_assessment_governance.py",
    ROOT / "validators" / "validate_public_route_candidate_assessment_governance_validation.py",
    ROOT / "validators" / "validate_public_route_candidate_registry_governance.py",
    ROOT / "validators" / "validate_public_route_candidate_registry_governance_validation.py",
    ROOT / "validators" / "validate_public_route_candidate_registration_governance.py",
    ROOT / "validators" / "validate_public_route_candidate_registration_governance_validation.py",
    ROOT / "validators" / "validate_governance_scaffolding_freeze.py",
    ROOT / "validators" / "validate_public_reference_production_batch_1.py",
    ROOT / "validators" / "validate_public_reference_batch_1_depth_seo_inevitability.py",
    ROOT / "validators" / "validate_public_reference_production_batch_2.py",
    ROOT / "validators" / "validate_public_reference_batch_2_depth_seo_inevitability.py",
    ROOT / "validators" / "validate_decision_log_chronology.py",
    ROOT / "validators" / "validate_public_reference_production_batch_3.py",
    ROOT / "validators" / "validate_public_reference_batch_3_depth_standard_readiness.py",
    ROOT / "validators" / "validate_evidence_posture_standard_v1_public.py",
    ROOT / "validators" / "validate_standard_integration_protocol_readiness.py",
    ROOT / "validators" / "validate_evidence_posture_protocol_v1_draft.py",
    ROOT / "validators" / "validate_protocol_integration_standard_alignment_interface_readiness.py",
    ROOT / "validators" / "validate_public_interface_thesis_evidence_field.py",
    ROOT / "validators" / "validate_evidence_field_static_interface_embodiment_v1.py",
    ROOT / "validators" / "validate_evidence_field_visual_system_accessibility_hardening.py",
    ROOT / "validators" / "validate_evidence_field_interface_trust_audit_launch_readiness.py",
    ROOT / "validators" / "validate_engine_boundary_charter.py",
    ROOT / "validators" / "validate_public_reference_seo_authority_map.py",
    ROOT / "validators" / "validate_evidence_posture_engine_model_v0.py",
    ROOT / "validators" / "validate_output_language_guardrail_model_v1.py",
    ROOT / "validators" / "validate_internal_non_public_engine_prototype_charter.py",
    ROOT / "validators" / "validate_controlled_internal_prototype_v0_authorization_package.py",
    ROOT / "validators" / "validate_controlled_internal_prototype_v0_implementation.py",
    ROOT / "validators" / "validate_controlled_internal_prototype_v0_hardening.py",
    ROOT / "validators" / "validate_internal_prototype_traceability_interpretability_audit_v1.py",
    ROOT / "validators" / "validate_internal_prototype_fixture_coverage_matrix_v1.py",
    ROOT / "validators" / "validate_targeted_synthetic_fixture_expansion_v1.py",
    ROOT / "validators" / "validate_internal_prototype_compound_boundary_stress_test_v1.py",
    ROOT / "validators" / "validate_internal_prototype_guardrail_red_team_pack_v1.py",
    ROOT / "validators" / "validate_internal_prototype_output_admissibility_contract_v1.py",
    ROOT / "validators" / "validate_internal_prototype_admissibility_regression_suite_v1.py",
    ROOT / "validators" / "validate_internal_prototype_release_blocker_board_v1.py",
    ROOT / "validators" / "validate_public_exposure_prerequisite_map_v1.py",
    ROOT / "validators" / "validate_public_copy_boundary_framework_v1.py",
    ROOT / "validators" / "validate_public_evidence_risk_utility_surface_v1.py",
    ROOT / "validators" / "validate_public_reference_route_expansion_v1.py",
    ROOT / "validators" / "validate_public_reference_authority_internal_linking_v1.py",
    ROOT / "validators" / "validate_public_reference_source_confidence_layer_v1.py",
    ROOT / "validators" / "validate_public_reference_answer_surface_v1.py",
    ROOT / "validators" / "validate_public_reference_citation_retrieval_hardening_v1.py",
    ROOT / "validators" / "validate_public_reference_quality_consolidation_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_depth_expansion_v1.py",
    ROOT / "validators" / "validate_public_reference_pathway_pages_v1.py",
    ROOT / "validators" / "validate_public_reference_navigation_ia_consolidation_v1.py",
    ROOT / "validators" / "validate_public_reference_surface_authority_review_v1.py",
    ROOT / "validators" / "validate_public_reference_strategic_entry_points_v1.py",
    ROOT / "validators" / "validate_public_reference_strategic_narrative_surface_v1.py",
    ROOT / "validators" / "validate_public_reference_acquisition_readiness_surface_v1.py",
    ROOT / "validators" / "validate_public_reference_strategic_surface_consolidation_v1.py",
    ROOT / "validators" / "validate_public_reference_release_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_external_review_readiness_v1.py",
    ROOT / "validators" / "validate_public_reference_reviewer_packet_v1.py",
    ROOT / "validators" / "validate_public_reference_review_packet_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_executive_overview_surface_v1.py",
    ROOT / "validators" / "validate_public_reference_executive_overview_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_strategic_review_index_v1.py",
    ROOT / "validators" / "validate_public_reference_strategic_review_index_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_system_map_surface_v1.py",
    ROOT / "validators" / "validate_public_reference_system_map_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_navigation_backbone_consolidation_v1.py",
    ROOT / "validators" / "validate_public_reference_navigation_backbone_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_route_group_deepening_v1.py",
    ROOT / "validators" / "validate_public_reference_audience_path_expansion_v1.py",
    ROOT / "validators" / "validate_public_reference_evidence_condition_library_v1.py",
    ROOT / "validators" / "validate_public_reference_evidence_condition_crosswalk_v1.py",
    ROOT / "validators" / "validate_public_reference_100_route_surface_integrity_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_reading_sequences_v1.py",
    ROOT / "validators" / "validate_public_reference_retrieval_index_v1.py",
    ROOT / "validators" / "validate_public_reference_retrieval_walkthrough_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_citation_orientation_v1.py",
    ROOT / "validators" / "validate_public_reference_citation_walkthrough_audit_v1.py",
    ROOT / "validators" / "validate_public_reference_source_use_orientation_v1.py",
    ROOT / "validators" / "validate_public_reference_source_use_walkthrough_audit_v1.py",
]
MANIFEST_GENERATOR = ROOT / "validators" / "generate_build_manifest.py"


def run_step(label: str, command: list[str]) -> int:
    import os
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(command, cwd=ROOT, check=False, env=env)
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
