# Controlled Internal Prototype v0 — Hardening Coverage

Sprint 73 hardens the internal prototype without public exposure or operational product behavior.

## Fixture Coverage

- **16 synthetic fixtures** in `fixtures/synthetic-fixtures-v0.json` (10 base + edge + 6 targeted expansion)
- **5 base posture fixtures**: Supported, Qualified, Limited, Not Assessable, Out of Scope
- **5 edge-case fixtures**: attribution boundary, provenance gap, context collapse, claim drift, limitation-not-falsehood
- **6 targeted expansion fixtures** (Sprint 76): traceability caveat, provenance/context compound, drift/limitation compound, attribution/output boundary, source/traceability/chain, not-assessable multi-reason

All fixtures remain synthetic, neutral, case-neutral, and free of real-person, current-event, political, legal, medical, financial-advice, company-accusatory, and private-data content.

## Regression Checks

- `validation_harness.py` — fixture evaluation and posture coverage
- `guardrail_regression.py` — guardrail failure detection on synthetic negative vectors
- `traceability_harness.py` — traceability and interpretability audit validation
- `fixture_coverage_harness.py` — governed fixture coverage validation
- `targeted_fixture_expansion_harness.py` — targeted gap-closure fixture validation (Sprint 76+)
- `compound_boundary_stress_analyzer.py` — compound boundary stress evaluation (Sprint 77+)
- `compound_boundary_stress_harness.py` — compound boundary stress validation (Sprint 77+)
- `guardrail_red_team_pack.py` — guardrail red-team vector definitions (Sprint 78+)
- `guardrail_red_team_harness.py` — guardrail red-team validation (Sprint 78+)
- `regression_harness.py` — combined hardening validation entry point

## Coverage Governance (Sprint 75)

Ten synthetic fixtures are mapped against posture states, evidence dimensions, protocol steps, standard principles, boundary checks, caveat families, guardrail rules, forbidden transformations, traceability fields, and regression vectors. Coverage is a governance map, not a score. See `INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_V1.md`.

## Compound Boundary Stress Coverage (Sprint 77)

Eight internal stress cases test compound boundary classes against existing 16 synthetic fixtures. Stress testing verifies collapse prevention (no verdict, score, fake/real label, accusation, or report-shape output). See `INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_V1.md` and `data/internal-prototype-compound-boundary-stress-test-v1.json`.

## Guardrail Red-Team Coverage (Sprint 78)

Sixteen internal red-team vectors pressure-test output-language guardrails against adversarial linguistic collapse (verdict, score, fake/real, accusation, certification, result-card, public-report shape). See `INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_V1.md` and `data/internal-prototype-guardrail-red-team-pack-v1.json`.

## Boundaries Preserved

- No public route, sitemap entry, or public link
- No upload, API, UI, JavaScript, scoring, or external data
- No verdict, fake/real label, or report export behavior
- Local-only, fixture-bound, governed internal architecture test

## Run Hardening Validation

`py -3 internal/prototypes/controlled-engine-v0/regression_harness.py`

Expected: `controlled internal prototype hardening validation passed`
