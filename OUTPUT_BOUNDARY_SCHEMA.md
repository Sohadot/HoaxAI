# Hoax.ai Output Boundary Schema

**Version:** v1.0.0  
**Status:** governed_internal_schema  
**Maturity:** not_public_tool  
**Decision:** DEC-020

## A. Purpose

This schema defines the controlled shape of future evidence-posture outputs.

It specifies what a future Hoax.ai output is allowed to contain, how it must be bounded, and what it must never imply. It is the output contract between the Evidence Posture Classification Protocol and any future engine or tool.

Before the system can produce outputs, the system must govern what an output is allowed to say.

## B. Non-Purpose

This schema does **not**:

- create an active tool;
- create a classifier;
- create a scoring system;
- create upload functionality;
- determine truth or falsity;
- certify authenticity;
- detect all synthetic media;
- prove fraud;
- establish guilt;
- accuse people or institutions;
- determine whether an event occurred;
- replace human, legal, forensic, journalistic, or institutional review.

## C. Governing Principle

**Before the system can produce outputs, the system must govern what an output is allowed to say.**

**An output is a bounded evidence-posture statement about an artifact or evidence chain, not a verdict about truth, authenticity, people, institutions, brands, organizations, or events.**

A future engine may only speak through the output boundary schema.

## D. Dependencies

This schema depends on:

- `EVIDENCE_POSTURE_TAXONOMY.md`
- `data/evidence-posture-taxonomy.json`
- `EVIDENCE_POSTURE_STANDARD.md`
- `data/evidence-posture-standard.json`
- `EVIDENCE_POSTURE_CLASSIFICATION_PROTOCOL.md`
- `data/evidence-posture-protocol.json`
- `GOVERNANCE_BOUNDARY.md`
- `CLAIM_POLICY.md`
- `data/category-language.json`
- `data/ontology-foundation.json`

## E. Required Output Fields

### 1. output_id

A unique identifier for a future output instance.

### 2. schema_version

The output boundary schema version.

### 3. protocol_version

The Evidence Posture Classification Protocol version used.

### 4. taxonomy_version

The Evidence Posture Taxonomy version used.

### 5. standard_version

The Evidence Posture Standard version used.

### 6. artifact_scope

A bounded description of the artifact or evidence chain being reviewed.

### 7. artifact_type

The artifact type: image, video, audio, document, screenshot, source record, claim record, media object, or evidence chain.

### 8. posture_state

One allowed taxonomy state only:

- `documented_posture`
- `partially_supported_posture`
- `provenance_limited_posture`
- `contextually_unstable_posture`
- `coherence_questioned_posture`
- `high_risk_evidence_posture`
- `not_assessable_posture`
- `planned_not_claimed_posture`

### 9. posture_reason_summary

A concise explanation of why the posture state was selected, bounded to evidence posture only.

### 10. dimension_findings

A structured list mapping findings to the nine standard/taxonomy dimensions.

### 11. limiting_factors

A list of missing, weak, unstable, or unresolved factors.

### 12. subject_boundary_statement

A required statement that the posture applies to the artifact or evidence chain, not to any connected person, institution, brand, organization, or event.

### 13. prohibited_interpretations

A required list of what the output must not be read to mean.

### 14. confidence_boundary

A qualitative boundary statement explaining the limits of reliance. This must not be a numeric score.

### 15. recommended_next_checks

Optional bounded next checks. These must not imply accusation or certainty.

### 16. source_record_refs

Optional references to source records when available.

### 17. claim_record_refs

Optional references to claim records when available.

### 18. output_status

One of:

- `draft_internal`
- `governed_internal`
- `public_allowed_after_gate`
- `retired`
- `blocked`

### 19. generated_by

The system, protocol, or manual process that created the output.

### 20. last_reviewed

Review date.

## F. Required Boundary Statements

Every future output must include:

- artifact focus;
- posture state;
- reason summary;
- limitation statement;
- subject-separation boundary;
- prohibited interpretations;
- confidence boundary;
- no truth verdict;
- no fake/real binary;
- no accusation.

## G. Prohibited Output Fields

The following must never appear as output fields:

- truth_score
- lie_score
- guilt_score
- fraud_score
- authenticity_score
- deception_score
- subject_risk_score
- person_score
- institution_score
- fake_real_result
- deepfake_detected
- verdict
- accusation
- legal_conclusion
- guilt_finding

No numeric scores unless a later scoring standard is separately adopted and validated.

## H. Prohibited Output Language

- "This is fake."
- "This is real."
- "This proves fraud."
- "This proves deception."
- "The person is lying."
- "The institution is guilty."
- "This confirms the event did not happen."
- "Deepfake detected."
- "Truth score."
- "Lie score."
- "Authenticity certified."
- "Guaranteed detection."
- "Verified truth."
- "Hoax confirmed."

## I. Allowed Output Language Examples

Bounded examples only — no real people, institutions, brands, or events:

- "The artifact has a provenance-limited posture because the available source chain is incomplete."
- "The evidence chain is partially supported within the available context."
- "The available information is not sufficient for a responsible posture classification."
- "This posture applies to the artifact, not to any connected subject."
- "The output should not be interpreted as a truth verdict, authenticity certification, or accusation."

## J. Minimum Output Template

Future template — **not an active public tool or service**:

```
Artifact scope:
Posture state:
Reason summary:
Limiting factors:
Subject boundary:
Prohibited interpretations:
Confidence boundary:
Recommended next checks:
```

## K. Output Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_schema |
| Maturity | not_public_tool |

## Machine-Readable Source

Canonical machine-readable schema: `data/output-boundary-schema.json`

## Related Governance

- DEC-017 — Evidence Posture Taxonomy v1
- DEC-018 — Evidence Posture Standard v1
- DEC-019 — Evidence Posture Classification Protocol v1
- DEC-020 — Output Boundary Schema v1

## Protocol Relationship

Future protocol outputs must conform to this schema. The protocol defines how posture is assigned; the output boundary schema defines what the resulting statement is allowed to say.
