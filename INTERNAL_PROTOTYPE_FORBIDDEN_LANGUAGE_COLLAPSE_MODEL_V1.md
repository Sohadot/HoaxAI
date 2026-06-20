# Internal Prototype Forbidden Language Collapse Model v1

## Forbidden Language Collapse Statement

Forbidden language collapse occurs when adversarial linguistic pressure transforms evidence-posture internal structures into verdict, score, accusation, certification, detector, result-card, or public-report language.

## Collapse Definition

Collapse is any internal or would-be public output that crosses from posture, limitation, and caveat language into forbidden transformation families defined by Output Language Guardrail Model v1.

## Collapse Classes

- verdict collapse (fake/real, verified true/false)
- score collapse (confidence score, percentage)
- accusation collapse (guilty, subject guilt transfer)
- deception collapse (deceptive finding)
- manipulation collapse (manipulated, manipulation proof)
- fraud collapse (fraudulent)
- certification collapse (certified, proven, confirmed)
- result-card collapse
- public-report collapse
- legal conclusion collapse (illegal, liable)

## Transformation Pressure Map

| Pressure | Forbidden Target | Guardrail Block |
|----------|------------------|-----------------|
| verdict_pressure | is fake / is real | fake_real_verdict_block |
| score_pressure | confidence score / percentage | numeric_score_block |
| subject_accusation | guilty | subject_accusation_block |
| deception_finding | deceptive | deception_finding_block |
| manipulation_proof | manipulated | manipulation_proof_block |
| fraud_language | fraudulent | fraud_language_block |
| certification | certified / proven / confirmed | certification_block |
| result_card_shape | result card | result_card_shape_block |
| report_generation | public report | public_report_shape_block |

## Forbidden Phrase Map

Guardrails block: is fake, is real, verified true, verified false, confidence score, detection result, fraudulent, guilty, deceptive, manipulated, proven, certified, confirmed, illegal, liable, result card, public report.

## Allowed Replacement Language

Posture states (Supported, Qualified, Limited, Not Assessable, Out of Scope), limitation caveats, source caveats, provenance caveats, interpretation-risk caveats, and attribution-boundary caveats.

## Guardrail Preservation Rules

- block forbidden transformation before output emission
- preserve posture language over verdict language
- preserve uncertainty over certainty escalation
- preserve artifact-subject separation

## Caveat Preservation Rules

Red-team vectors must not erase limitation, source, provenance, drift, interpretation-risk, attribution-boundary, or output-boundary caveats under pressure.

## Traceability Preservation Rules

Each blocked vector must retain internal traceability refs linking pressure class to guardrail block and forbidden transformation family.

## Stress Failure Modes

- guardrail passes adversarial payload
- internal result emits forbidden phrase as conclusion
- caveat erasure under certainty pressure
- not-assessable becomes negative conclusion

## Required Response to Collapse

Any collapse failure requires guardrail strengthening and sprint rollback before commit. No public exposure is permitted.
