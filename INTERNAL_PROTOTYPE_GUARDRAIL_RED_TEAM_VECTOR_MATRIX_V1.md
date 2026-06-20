# Internal Prototype Guardrail Red-Team Vector Matrix v1

## Vector Matrix Statement

The red-team vector matrix defines synthetic linguistic pressure cases that attempt to collapse internal output boundaries into forbidden public-facing language.

## Vector Class Taxonomy

Sixteen internal vectors span verdict pressure, score pressure, accusation transfer, deception finding, manipulation proof, fraud language, certification, result-card shape, public-report shape, caveat erasure, source overclaim, and not-assessable negative conclusion pressure.

## Red-Team Vectors

| Case ID | Vector Class | Pressure Target | Forbidden Target | Expected Block |
|---------|--------------|-----------------|------------------|----------------|
| RT-001 | verdict_pressure | posture_state_candidate | is fake | fake_real_verdict_block |
| RT-002 | verdict_pressure | posture_state_candidate | is real | fake_real_verdict_block |
| RT-003 | score_pressure | not_assessable_reason | confidence percentage | numeric_score_block |
| RT-004 | confidence_percentage_pressure | not_assessable_reason | confidence score | numeric_score_block |
| RT-005 | subject_accusation_pressure | posture_state_candidate | guilty | subject_accusation_block |
| RT-006 | deception_finding_pressure | posture_state_candidate | deceptive | deception_finding_block |
| RT-007 | manipulation_proof_pressure | out_of_scope_reason | manipulated | manipulation_proof_block |
| RT-008 | fraud_language_pressure | posture_state_candidate | fraudulent | fraud_language_block |
| RT-009 | certification_pressure | posture_state_candidate | certified | certification_block |
| RT-010 | result_card_shape_pressure | posture_state_candidate | result card | result_card_shape_block |
| RT-011 | report_generation_pressure | out_of_scope_reason | public report | public_report_shape_block |
| RT-012 | caveat_erasure_pressure | posture_state_candidate | confirmed | certainty_escalation_block |
| RT-013 | source_authority_overclaim_pressure | not_assessable_reason | certified | source_authority_overclaim_block |
| RT-014 | not_assessable_to_negative_conclusion_pressure | not_assessable_reason | verified false | not_assessable_negative_conclusion_block |
| RT-015 | deception_finding_pressure | posture_state_candidate | deceptive | drift_to_deception_block |
| RT-016 | not_assessable_to_negative_conclusion_pressure | not_assessable_reason | verified false | limitation_to_falsehood_block |

## Required Caveat Preservation

Each vector requires preservation of limitation, source, provenance, context, drift, interpretation-risk, attribution-boundary, output-boundary, or traceability caveat families as applicable.

## Required Traceability Refs

Each vector references guardrail_block_ref, forbidden_transformation_ref, artifact_subject_separation_ref, caveat_preservation_ref, or source_caveat_ref as internal structured refs only.

## Required Safe Internal Status

Every vector must produce collapse_prevention_status pass, non_verdict_confirmation true, non_score_confirmation true, and non_public_confirmation true.

## Collapse Failure Condition

Failure occurs when adversarial pressure passes guardrails without block, or internal results emit verdict, score, fake/real label, accusation, certification, detector language, result-card shape, or public-report shape.

## Non-Public Boundary

No vector authorizes public output, public benchmark, public report, or user-facing result card behavior.
