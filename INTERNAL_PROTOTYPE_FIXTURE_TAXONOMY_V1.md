# Internal Prototype Fixture Taxonomy v1

## Fixture Taxonomy Statement

Controlled Internal Prototype v0 synthetic fixtures are classified by governance purpose, not by volume. Taxonomy defines what each fixture class is allowed to test and what it must never represent.

## Base Posture Fixtures

Five fixtures (SYN-FIX-001 through SYN-FIX-005) establish one canonical synthetic case per posture state:

- Supported, Qualified, Limited, Not Assessable, Out of Scope

Each base fixture activates core evidence dimensions and expected caveats for its posture state.

## Boundary Edge Fixtures

Five fixtures (SYN-FIX-006 through SYN-FIX-010) stress specific boundary checks:

- attribution boundary (006)
- provenance gap (007)
- context collapse (008)
- claim drift (009)
- limitation-not-falsehood (010)

## Caveat-Trigger Fixtures

Fixtures trigger caveat families through expected_required_caveats metadata. Base and edge fixtures collectively activate source, provenance, context, drift, limitation, interpretation_risk, attribution_boundary, and output_boundary caveats.

## Guardrail-Negative Fixtures

Forbidden output expectations in fixture metadata define guardrail-negative test targets. Guardrail regression vectors supplement fixture-level guardrail coverage.

## Traceability Fixtures

All ten fixtures participate in traceability coverage through prototype_core execution and traceability_mapper linkage.

## Out-of-Scope Fixtures

SYN-FIX-005-OUT-OF-SCOPE tests scope boundary behavior with not_applicable_scope dimension values.

## Not-Assessable Fixtures

SYN-FIX-004 and SYN-FIX-010 test assessment-blocked conditions without verdict or falsehood language.

## Compound-Boundary Fixtures

No compound-boundary fixture exists yet. This is a documented gap for future authorized expansion.

## Future Candidate Fixture Classes

- FC-TRACEABILITY-CAVEAT-STUB
- FC-COMPOUND-SUPPORTED-QUALIFIED-BOUNDARY
- FC-QUALIFIED-MULTI-CAVEAT-COMPOUND
- FC-LIMITED-DRIFT-CONTEXT-COMPOUND
- FC-NOT-ASSESSABLE-TRACEABILITY-COLLAPSE
- FC-OUT-OF-SCOPE-SECONDARY-CATEGORY

## Forbidden Fixture Classes

The following fixture classes are permanently inadmissible:

- real-person accusation
- current event
- political claim
- legal dispute
- medical claim
- financial advice
- company fraud accusation
- private screenshot
- uploaded user file
- celebrity claim
- live URL
- external fact-check target
- copyrighted article reproduction
