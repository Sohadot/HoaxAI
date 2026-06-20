# Controlled Internal Prototype v0 — Hardening Coverage

Sprint 73 hardens the internal prototype without public exposure or operational product behavior.

## Fixture Coverage

- **10 synthetic fixtures** in `fixtures/synthetic-fixtures-v0.json`
- **5 base posture fixtures**: Supported, Qualified, Limited, Not Assessable, Out of Scope
- **5 edge-case fixtures**: attribution boundary, provenance gap, context collapse, claim drift, limitation-not-falsehood

All fixtures remain synthetic, neutral, case-neutral, and free of real-person, current-event, political, legal, medical, financial-advice, company-accusatory, and private-data content.

## Regression Checks

- `validation_harness.py` — fixture evaluation and posture coverage
- `guardrail_regression.py` — guardrail failure detection on synthetic negative vectors
- `traceability_harness.py` — traceability and interpretability audit validation
- `fixture_coverage_harness.py` — governed fixture coverage validation
- `regression_harness.py` — combined hardening validation entry point

## Coverage Governance (Sprint 75)

Ten synthetic fixtures are mapped against posture states, evidence dimensions, protocol steps, standard principles, boundary checks, caveat families, guardrail rules, forbidden transformations, traceability fields, and regression vectors. Coverage is a governance map, not a score. See `INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_V1.md`.

## Boundaries Preserved

- No public route, sitemap entry, or public link
- No upload, API, UI, JavaScript, scoring, or external data
- No verdict, fake/real label, or report export behavior
- Local-only, fixture-bound, governed internal architecture test

## Run Hardening Validation

`py -3 internal/prototypes/controlled-engine-v0/regression_harness.py`

Expected: `controlled internal prototype hardening validation passed`
