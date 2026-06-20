# Internal Prototype Output Admissibility Repair Policy v1

## Repair Policy Statement

Inadmissible internal outputs require structural repair, not cosmetic word substitution.

## Structural Repair Principle

Repair restores posture basis, protocol refs, standard refs, boundary checks, caveats, traceability refs, guardrail blocks, and forbidden-transformation blocks.

## Word Replacement Is Insufficient

Replacing a forbidden word while leaving missing caveats, boundaries, or traceability does not restore admissibility.

## Missing Caveat Repair

Restore triggered_caveats and caveat_trigger_refs through caveat_mapper integration.

## Missing Boundary Repair

Restore active_boundary_checks and boundary_check_refs through boundary_evaluator integration.

## Missing Traceability Repair

Restore trace_id and traceability_map through traceability_mapper integration.

## Missing Protocol/Standard Repair

Restore protocol_step_refs and standard_principle_refs through traceability mapping.

## Guardrail Repair

Clear guardrail_failure_flags, restore validation_status pass, and remove prohibited language from output candidate fields.

## Report-Shape Repair

Remove result-card and public-report shape language from output candidate fields; restore output boundary constraints.

## Public-Output-Risk Repair

Restore non_public_confirmation and remove public-action or moderation-action language from output candidate fields.

## Non-Admissible Cases

Results with persistent guardrail failure, report-shape output, or public-output risk remain inadmissible until structural repair completes.

## Future Repair Validator Requirements

Future sprints may add admissibility regression suites. Any expansion requires separate explicit sprint authorization.

Sprint 80 Admissibility Regression Suite v1 (DEC-098) implements unified regression checks for inadmissible output mutations and required repair re-run sequences.
