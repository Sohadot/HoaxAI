# Internal Prototype Coverage Gap Analysis v1

## Gap Analysis Statement

This document identifies coverage strengths, weaknesses, and named gaps in Controlled Internal Prototype v0 synthetic fixture coverage. It does not authorize public exposure, public reporting, or real-world case testing.

## Current Coverage Strengths

- All five posture states have at least one governed fixture
- All thirteen evidence condition dimensions are activated
- All seventeen protocol steps have direct or indirect fixture linkage
- All nine boundary checks have fixture activation
- Traceability fields are fully covered through Sprint 74 infrastructure
- Fixture policy flags are enforced across all ten fixtures
- Guardrail regression vectors validate prohibited synthetic output shapes

## Current Coverage Weaknesses

- traceability_caveat family has no dedicated fixture
- compound boundary interactions are untested
- out-of-scope variety is limited to one fixture
- not-assessable variety is limited to two similar fixtures
- EP-P17 forbidden-output activation is partial
- GL-DETECTOR-STYLE-BLOCK lacks dedicated negative vector

## Posture Gaps

Not Assessable and Out of Scope have partial variety coverage. Future fixtures must close named variants without expanding into real-world cases.

## Boundary Interaction Gaps

No fixture tests simultaneous activation of multiple boundary stress conditions (e.g., drift plus context collapse plus provenance gap).

## Caveat Gaps

traceability_caveat is the only caveat family without direct fixture activation.

## Guardrail Gaps

source_weakness_to_fraud, risk_to_verdict, and confidence_to_certification are partially covered. GL-DETECTOR-STYLE-BLOCK needs a dedicated regression or fixture target.

## Traceability Gaps

No traceability field gaps remain at the structural level. Future work may require traceability under compound boundary conditions.

## Regression Gaps

Guardrail regression has four vectors. Detector-style and upload-classification negative vectors are not yet present.

## Future Fixture Candidates

Each candidate must reference a named gap from coverage_gaps in the coverage matrix JSON:

- FC-TRACEABILITY-CAVEAT-STUB
- FC-COMPOUND-SUPPORTED-QUALIFIED-BOUNDARY
- FC-LIMITED-DRIFT-CONTEXT-COMPOUND
- FC-NOT-ASSESSABLE-TRACEABILITY-COLLAPSE
- FC-OUT-OF-SCOPE-SECONDARY-CATEGORY

## Non-Admissible Fixture Ideas

- Real-person social media screenshot evaluation
- Current-event news article fact-check
- Political claim verification
- Company fraud investigation stub
- Live URL ingestion test
- User upload classification test

## Sprint 76 Readiness Conditions

Sprint 76 (Targeted Synthetic Fixture Expansion v1) may proceed only when:

- Sprint 75 validation passes
- Named gaps are selected from coverage_gaps
- Future fixture admission criteria are satisfied for each candidate
- No public route, benchmark, report, or operational capability is introduced
