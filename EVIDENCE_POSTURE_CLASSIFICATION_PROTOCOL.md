# Hoax.ai Evidence Posture Classification Protocol

**Version:** v1.0.0  
**Status:** governed_internal_protocol  
**Maturity:** not_public_tool  
**Decision:** DEC-019

## A. Purpose

This protocol defines the governed process for moving from artifact review to bounded evidence posture language.

It specifies the sequence for assigning an evidence posture state to an evidence artifact or evidence chain — using the adopted taxonomy and standard — without automating judgment or creating an active classifier.

The protocol governs how posture is assigned; it does not automate judgment.

## B. Non-Purpose

This protocol does **not**:

- determine truth or falsity;
- detect all synthetic media;
- certify authenticity;
- prove manipulation;
- prove fraud;
- establish guilt;
- accuse people or institutions;
- determine whether an event occurred;
- create an active public classifier;
- create a score;
- create an upload workflow;
- replace human, legal, forensic, journalistic, or institutional review.

## C. Governing Principle

**The protocol governs how posture is assigned; it does not automate judgment.**

**A protocol outcome is a bounded evidence-posture statement, not a verdict about truth, authenticity, people, institutions, or events.**

## D. Dependencies

This protocol depends on:

- `EVIDENCE_POSTURE_TAXONOMY.md`
- `data/evidence-posture-taxonomy.json`
- `EVIDENCE_POSTURE_STANDARD.md`
- `data/evidence-posture-standard.json`
- `GOVERNANCE_BOUNDARY.md`
- `CLAIM_POLICY.md`
- `data/category-language.json`
- `data/ontology-foundation.json`

## E. Protocol Scope

### Applies To

- evidence artifacts;
- evidence chains;
- claim records;
- source records;
- provenance signals;
- context signals;
- coherence signals;
- future bounded outputs.

### Does Not Apply To

- people as classification targets;
- institutions as classification targets;
- brands as classification targets;
- organizations as classification targets;
- events as subjects of judgment.

## F. Protocol Stages

### 1. Artifact Boundary Identification

**Goal:** Identify the discrete artifact or evidence chain being reviewed.

**Required checks:**

- Is there a discrete artifact?
- Is the artifact type known?
- Is the artifact distinct from the subject connected to it?
- Is the review scope bounded?

**Stop condition:** If no discrete artifact or evidence chain can be identified, use `not_assessable_posture`.

### 2. Subject Separation Check

**Goal:** Ensure the protocol does not transfer artifact risk to a person, institution, brand, organization, or event.

**Required checks:**

- Does the artifact depict, reference, or imply an identifiable subject?
- Is all output language bounded to the artifact?
- Does the output avoid intent, guilt, deception, misconduct, or involvement language?

**Stop condition:** If subject separation cannot be preserved, no posture output may be issued.

### 3. Source Record Review

**Goal:** Review whether the source record is visible, bounded, or missing.

**Required checks:**

- Is the source known?
- Is the publication path visible?
- Is the source appropriate to the claim?
- Is source confidence limited or sufficient?

### 4. Provenance Visibility Review

**Goal:** Assess origin, custody, publication path, or source-chain visibility.

**Required checks:**

- Is origin visible?
- Is chain of custody visible where relevant?
- Is publication path bounded?
- Are provenance gaps present?

### 5. Contextual Stability Review

**Goal:** Assess whether the surrounding context is stable enough for bounded interpretation.

**Required checks:**

- Is context missing?
- Is context ambiguous?
- Is context disputed?
- Is context stable enough for bounded reliance?

### 6. Forensic Coherence Review

**Goal:** Review internal, relational, temporal, visual, audio, metadata, or contextual coherence signals without turning them into conclusions.

**Required checks:**

- Are coherence signals internally consistent?
- Are there unresolved inconsistencies?
- Is further examination needed?
- Are coherence questions described as questions rather than proof?

### 7. Evidence Chain Continuity Review

**Goal:** Determine whether the artifact is supported by a stable chain of records.

**Required checks:**

- Are supporting records available?
- Is the chain partial?
- Is the chain broken?
- Are supporting records conflicting?

### 8. Corroboration Posture Review

**Goal:** Review whether additional supporting signals exist, are absent, partial, or conflicting.

**Required checks:**

- Is there corroboration?
- Is corroboration independent?
- Is corroboration partial?
- Is corroboration conflicting?

### 9. Standard Mapping

**Goal:** Map the reviewed conditions to the Evidence Posture Standard.

**Required checks:**

- Which standard dimensions are sufficient?
- Which are limited?
- Which are weak?
- Which are not assessable?
- Which posture sufficiency rule is satisfied?

### 10. Posture State Selection

**Goal:** Select one bounded posture state from the taxonomy.

**Allowed states only:**

- `documented_posture`
- `partially_supported_posture`
- `provenance_limited_posture`
- `contextually_unstable_posture`
- `coherence_questioned_posture`
- `high_risk_evidence_posture`
- `not_assessable_posture`
- `planned_not_claimed_posture`

**Rules:**

- Do not invent new posture states.
- Do not use fake/real language.
- Do not use truth/falsity language.
- Do not use subject accusation language.
- If multiple states appear possible, choose the most bounded responsible state.
- If required information is missing, prefer `not_assessable_posture` over speculative output.

### 11. Output Boundary Composition

**Goal:** Create a bounded evidence-posture statement.

Every future output must include:

- artifact focus;
- posture state;
- reason summary;
- limitation statement;
- subject-separation boundary;
- no truth verdict;
- no fake/real binary;
- no accusation;
- recommended next checks if appropriate.

### 12. Final Governance Check

**Goal:** Ensure the output complies with governance before use.

**Required checks:**

- Does it stay within artifact posture?
- Does it avoid subject judgment?
- Does it avoid unsupported certainty?
- Does it avoid planned capability as existing service?
- Does it follow taxonomy and standard?
- Does it avoid public tool implication if used before an engine exists?

## G. State Selection Rules

State selection follows Sprint 3 standard sufficiency rules (STD-RULE-0001 through STD-RULE-0008). The protocol may select a state only when the corresponding standard rule's required conditions are satisfied. Rules are not loosened or contradicted.

| State | When Selectable |
|-------|-----------------|
| documented_posture | Artifact identified, source bounded, provenance visible, context stable, no major coherence gap |
| partially_supported_posture | Supporting signals exist with unresolved dimension gaps |
| provenance_limited_posture | Provenance visibility insufficient for stronger posture |
| contextually_unstable_posture | Context missing, disputed, or unstable |
| coherence_questioned_posture | Coherence signals require further examination |
| high_risk_evidence_posture | Multiple dimensions contain unresolved risk signals |
| not_assessable_posture | Information insufficient for responsible classification |
| planned_not_claimed_posture | Referenced capability is planned, not active |

## H. Stop Conditions

The protocol must stop or return no posture output if:

- no discrete artifact or evidence chain exists;
- subject separation cannot be preserved;
- available information is insufficient and not_assessable language is not safe;
- output would imply accusation;
- output would imply truth verdict;
- output would imply fake/real binary;
- output would claim future capability as active;
- required taxonomy or standard mapping is missing.

## I. Minimum Protocol Output Shape

Future output shape — **not an active public tool**:

| Field | Purpose |
|-------|---------|
| artifact_scope | Bounded description of artifact or evidence chain reviewed |
| posture_state | Selected taxonomy state label |
| posture_reason_summary | Brief bounded reason for state selection |
| limiting_factors | Unresolved dimensions or gaps |
| subject_boundary_statement | Explicit artifact–subject separation |
| prohibited_interpretations | What the output must not be read as |
| recommended_next_checks | Bounded verification steps if appropriate |
| confidence_boundary | Uncertainty and limitation framing |
| protocol_version | Protocol version reference |

## J. Prohibited Protocol Outputs

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

## K. Protocol Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_protocol |
| Maturity | not_public_tool |

This protocol is not an active classifier, scoring system, upload workflow, or public service.

## Machine-Readable Source

Canonical machine-readable protocol: `data/evidence-posture-protocol.json`

## Related Governance

- DEC-017 — Evidence Posture Taxonomy v1
- DEC-018 — Evidence Posture Standard v1
- DEC-019 — Evidence Posture Classification Protocol v1

## Output Boundary Schema Dependency

Future protocol outputs must conform to `OUTPUT_BOUNDARY_SCHEMA.md` and `data/output-boundary-schema.json`. The protocol defines how posture is assigned; the output boundary schema defines what the resulting statement is allowed to say.
