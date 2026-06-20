# Internal Prototype Interpretability Audit v1

## 1. Interpretability Audit Statement

The controlled internal prototype must be internally interpretable without becoming an output generator.

## 2. Interpretability Dimensions

- posture interpretability
- protocol-step interpretability
- standard-principle interpretability
- boundary-check interpretability
- caveat-trigger interpretability
- guardrail interpretability
- forbidden-transformation interpretability
- fixture-policy interpretability
- scope interpretability

## 3. Required Internal Explanation Fields

- `trace_id`
- `fixture_id`
- `posture_basis`
- `protocol_step_refs`
- `standard_principle_refs`
- `evidence_condition_refs`
- `boundary_check_refs`
- `caveat_trigger_refs`
- `guardrail_rule_refs`
- `forbidden_transformation_refs`
- `limitation_reason_refs`
- `out_of_scope_reason_refs`
- `no_verdict_confirmation`
- `no_score_confirmation`
- `no_subject_accusation_confirmation`
- `non_public_confirmation`

## 4. Non-Narrative Explanation Rule

The audit permits structured interpretability objects only. It does not permit natural-language report generation, public explanation rendering, or user-facing summaries.

## 5. Interpretability Quality Tests

- every fixture has `trace_id`
- every posture candidate has basis
- every caveat has trigger
- every boundary check has condition source
- every guardrail block has prohibited family
- every not-assessable result has reason
- every out-of-scope result has reason
- every result confirms no verdict, no score, no subject accusation, and non-public status

## 6. Interpretability Failure Modes

- unexplained posture
- orphan caveat
- orphan boundary check
- missing guardrail source
- hidden verdict implication
- score implication
- subject-transfer leakage
- trace without source authority
- explanation becoming report
- report-shape drift

## Future Coverage Linkage

Internal Prototype Fixture Coverage Matrix v1 (Sprint 75, DEC-093) verifies that required interpretability fields remain covered across all synthetic fixtures without generating public explanations.
