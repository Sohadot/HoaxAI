# Controlled Internal Prototype v0

Internal, non-public, local-only architecture test for Hoax.ai evidence-posture composition.

## Status

- This prototype is **internal and non-public**
- **No route** exists for this prototype
- **No sitemap entry** exists for this prototype
- **No upload**, API, UI, JavaScript, scoring, fake/real result, or public output exists
- **No public explanation** or report generator exists
- **No public benchmark** or coverage report exists
- The prototype uses **only governed synthetic fixtures**
- The prototype must **not** be used on real-world claims
- This is **only a controlled architecture test**

## Location

All files remain under `internal/prototypes/controlled-engine-v0/`.

## Usage

Run the local validation harness:

`py -3 internal/prototypes/controlled-engine-v0/validation_harness.py`

Run hardening regression (Sprint 73+):

`py -3 internal/prototypes/controlled-engine-v0/regression_harness.py`

Run internal traceability validation (Sprint 74+):

`py -3 internal/prototypes/controlled-engine-v0/traceability_harness.py`

Run internal fixture coverage validation (Sprint 75+):

`py -3 internal/prototypes/controlled-engine-v0/fixture_coverage_harness.py`

Run targeted fixture expansion validation (Sprint 76+):

`py -3 internal/prototypes/controlled-engine-v0/targeted_fixture_expansion_harness.py`

Run compound boundary stress validation (Sprint 77+):

`py -3 internal/prototypes/controlled-engine-v0/compound_boundary_stress_harness.py`

Run guardrail red-team validation (Sprint 78+):

`py -3 internal/prototypes/controlled-engine-v0/guardrail_red_team_harness.py`

Run output admissibility validation (Sprint 79+):

`py -3 internal/prototypes/controlled-engine-v0/output_admissibility_harness.py`

Run admissibility regression validation (Sprint 80+):

`py -3 internal/prototypes/controlled-engine-v0/admissibility_regression_harness.py`

Do not deploy, link publicly, or treat this as a product feature.
