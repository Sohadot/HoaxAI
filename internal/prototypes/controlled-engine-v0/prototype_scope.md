# Controlled Internal Prototype v0 — Scope

## Purpose

Test whether Evidence Posture Engine Model v0, Output Language Guardrail Model v1, Internal Non-Public Engine Prototype Charter, and Controlled Internal Prototype v0 Authorization Package can be composed into internal structured posture candidates, boundary checks, caveat triggers, and guardrail flags without verdicts, scores, or public outputs.

## Allowed Local-Only Behavior

- Load governed repository JSON models from fixed paths
- Load governed synthetic fixtures from `fixtures/synthetic-fixtures-v0.json`
- Map protocol steps EP-P01 through EP-P17 as internal structures
- Evaluate boundary checks as booleans/flags
- Map caveat family IDs
- Run output guardrail checks on internal structures
- Attach internal traceability and interpretability fields
- Analyze governed fixture coverage as internal structured objects
- Run deterministic in-memory validation harness

## Prohibited Behavior

- Public routes, sitemap entries, or public links
- Upload, forms, user input, CLI arguments
- Network calls, external APIs, live web lookup
- Scoring, fake/real labels, verdicts, accusations
- Natural-language reports, result cards, exports
- Public explanations, rendered interpretability, or report-shape narratives
- Public benchmarks, coverage reports, or performance rankings
- Deployment, analytics, JavaScript public behavior

## Source Authority Stack

- Evidence Posture Standard v1
- Evidence Posture Protocol v1 Draft
- Engine Boundary Charter
- Evidence Posture Engine Model v0
- Output Language Guardrail Model v1
- Internal Non-Public Engine Prototype Charter
- Internal Prototype Admissibility Model
- Internal Prototype Fixture Policy
- Controlled Internal Prototype v0 Authorization Package

## File Boundaries

All implementation files remain under `internal/prototypes/controlled-engine-v0/`.

## Fixture Boundaries

Synthetic fixtures only. No real-person, current-event, political, legal, medical, financial-advice, company-accusatory, or private-data fixtures.

## Output Boundaries

Internal structured objects only: posture_state_candidate, active_boundary_checks, triggered_caveats, prohibited_language_blocks, required_output_constraints, not_assessable_reason, out_of_scope_reason, guardrail_failure_flags, validation_status.

## Validator Requirements

Sprint 72 includes `validators/validate_controlled_internal_prototype_v0_implementation.py` and local `validation_harness.py`.

Sprint 73 adds ten synthetic fixtures, `guardrail_regression.py`, `regression_harness.py`, and `HARDENING_COVERAGE.md`.

Sprint 74 adds `traceability_mapper.py`, `interpretability_auditor.py`, `traceability_harness.py`, and internal traceability documentation.

Sprint 75 adds `fixture_coverage_analyzer.py`, `fixture_coverage_harness.py`, and Internal Prototype Fixture Coverage Matrix v1 governance documents.

## Future Removal/Rollback Rule

Any disqualifying drift requires rollback before commit. Public exposure fails the prototype boundary.
