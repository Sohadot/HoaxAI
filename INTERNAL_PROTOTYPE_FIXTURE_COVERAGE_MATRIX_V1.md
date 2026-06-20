# Internal Prototype Fixture Coverage Matrix v1

## 1. Coverage Matrix Statement

Internal Prototype Fixture Coverage Matrix v1 maps synthetic fixtures against governed evidence-posture architecture. It identifies which posture states, evidence dimensions, protocol steps, standard principles, boundary checks, caveat families, guardrail rules, forbidden transformations, traceability fields, and fixture-policy constraints are covered, partially covered, or not yet covered.

Coverage is a governance map, not a score. Status labels are qualitative and non-performance.

## 2. Coverage Scope

- internal coverage only
- no public benchmark
- no model score
- no performance ranking
- no public report
- no real-world evaluation
- no user-facing result
- no external data
- no route
- no sitemap entry

## 3. Coverage Status Vocabulary

| Status | Meaning |
|--------|---------|
| Covered | At least one governed synthetic fixture or regression vector directly activates the dimension |
| Partially Covered | Indirect, shallow, or single-variant activation exists |
| Gap | No governed activation yet |
| Not Applicable | Dimension does not apply to current fixture scope |
| Future Candidate | Named gap with admissible future fixture class defined |

These statuses are qualitative governance labels, not scores and not performance metrics.

## 4. Current Fixture Inventory

| Attribute | Value |
|-----------|-------|
| Total fixtures | 10 |
| Base posture fixtures | 5 (SYN-FIX-001 through SYN-FIX-005) |
| Edge-case boundary fixtures | 5 (SYN-FIX-006 through SYN-FIX-010) |
| Environment | local-only, non-public |
| Data class | synthetic only |
| Real-person/current-event/private-data fixtures | none |

## 5. Coverage Dimensions

- posture_state_coverage
- evidence_condition_dimension_coverage
- protocol_step_coverage
- standard_principle_coverage
- boundary_check_coverage
- caveat_family_coverage
- guardrail_rule_coverage
- forbidden_transformation_coverage
- traceability_field_coverage
- fixture_policy_coverage
- regression_vector_coverage

## 6. Posture-State Coverage

| Posture State | Fixture IDs | Status | Missing Conditions | Future Candidates |
|---------------|-------------|--------|--------------------|---------------------|
| Supported | SYN-FIX-001-SUPPORTED | Covered | compound boundary interaction | FC-COMPOUND-SUPPORTED-QUALIFIED-BOUNDARY |
| Qualified | SYN-FIX-002, 006, 007 | Covered | multi-caveat compound | FC-QUALIFIED-MULTI-CAVEAT-COMPOUND |
| Limited | SYN-FIX-003, 008, 009 | Covered | simultaneous drift and context collapse | FC-LIMITED-DRIFT-CONTEXT-COMPOUND |
| Not Assessable | SYN-FIX-004, 010 | Partially Covered | traceability collapse variant | FC-NOT-ASSESSABLE-TRACEABILITY-COLLAPSE |
| Out of Scope | SYN-FIX-005 | Partially Covered | secondary category variant | FC-OUT-OF-SCOPE-SECONDARY-CATEGORY |

Under-coverage risk is moderate for Not Assessable and Out of Scope due to limited variety.

## 7. Evidence Condition Dimension Coverage

All thirteen evidence condition dimensions are covered by at least one fixture:

- artifact_condition, claim_condition, source_basis, source_confidence
- provenance_status, context_status, traceability_status, chain_status
- drift_status, limitation_status, interpretation_risk_status
- attribution_boundary_status, output_boundary_status

Out-of-scope fixture marks several dimensions as not_applicable_scope, which is expected boundary behavior.

## 8. Protocol and Standard Coverage

Protocol steps EP-P01 through EP-P16 have direct or indirect fixture activation. EP-P17 (forbidden output expectations) is partially covered because not all forbidden output families have dedicated fixture negative vectors.

Standard principles EPS-001 through EPS-013 are covered. EPS-014 is partially covered through attribution and output boundary fixtures only.

## 9. Boundary and Caveat Coverage

All nine boundary checks have fixture activation. Caveat families are covered except traceability_caveat, which remains a gap. Output_boundary_caveat is partially covered through a single out-of-scope fixture.

## 10. Guardrail and Forbidden Transformation Coverage

| Forbidden Transformation | Coverage | Primary Activation |
|--------------------------|----------|-------------------|
| limitation_to_falsehood | Covered | SYN-FIX-010 |
| drift_to_deception | Covered | SYN-FIX-009 |
| gap_to_manipulation | Covered | SYN-FIX-007 |
| risk_to_verdict | Partially Covered | SYN-FIX-004, 010 |
| artifact_to_subject_guilt | Covered | SYN-FIX-006 |
| synthetic_to_fake | Covered | guardrail regression vector |
| source_weakness_to_fraud | Partially Covered | SYN-FIX-003 |
| context_collapse_to_motive | Covered | SYN-FIX-008 |
| confidence_to_certification | Partially Covered | SYN-FIX-002, 007 |

## 11. Traceability Coverage

All required traceability fields are covered through prototype_core and traceability_mapper integration validated by traceability_harness.

## 12. Gap Analysis

- traceability_caveat family lacks dedicated fixture
- compound boundary interactions are absent
- out-of-scope and not-assessable variety is limited
- EP-P17 and GL-DETECTOR-STYLE-BLOCK coverage is partial
- output boundary stress beyond single fixture is partial

## 13. Future Coverage Rule

No future fixture may be added merely to increase count. Each future fixture must close a named coverage gap, activate a specific boundary or caveat, test a forbidden transformation, or validate a specific traceability requirement.
