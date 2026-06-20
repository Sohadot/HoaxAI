# Controlled Prototype v0 Validation Plan

## Validation Plan Statement

This plan defines required validation checks before any Controlled Internal Prototype v0 implementation may be committed in Sprint 72. Sprint 71 does not authorize implementation or execution.

## Pre-Implementation Checks

Before Sprint 72 implementation begins:

- Sprint 71 authorization package validation must PASS
- DEC-089 must be active in DECISION_LOG.md
- Implementation contract must be accepted as governing
- Prototype charter, admissibility model, and fixture policy must remain valid
- Engine Model v0 and Output Language Guardrail Model v1 must remain valid
- Publisher status must reflect implementation-sprint authorization only after Sprint 72 governance updates
- `validate_all.py` must PASS on main before implementation branch work begins

## File-Scope Checks

- All new files must remain under authorized non-public internal path (e.g. `internal/prototypes/controlled-engine-v0/`)
- No files in public routes, sitemap, route registry, or forbidden paths
- No executable prototype code in Sprint 71
- Locked prototype files under `_internal_prototypes/evidence-posture-workbench/` must remain unmodified unless separately governed

## Fixture Checks

- Fixtures must be synthetic and governed
- No real-person fixture
- No current-event fixture
- No political, legal, medical, or company-accusatory fixture
- No uploaded user files or private screenshots
- No external fact-check targets
- Fixture metadata must include fixture_id, synthetic flag, case_neutral, non_personal, non_accusatory

## Output Checks

- Output structures limited to permitted internal objects only
- No fake/real result, truth/falsity result, score, or confidence percentage
- No accusation, subject guilt, deception finding, manipulation proof, or fraud claim
- No legal conclusion, moderation action, public result card, or downloadable report

## Guardrail Checks

- Output Language Guardrail Model v1 rules must be applied
- Posture-state language rules must be enforced
- Required caveats must not be omitted
- Boundary transformation rules must be respected

## Prohibited-Language Checks

- Forbidden term controls from guardrail model must block detector, verdict, and score language
- Prohibited language blocker must flag fake/real, truth/falsity, and accusation leakage

## Public Exposure Checks

- No public link to prototype
- No crawler exposure
- No public navigation reference
- No demo or marketing framing on public pages

## Route/Sitemap Checks

- Sitemap must remain exactly 19 URLs
- Route registry must not gain new public routes
- No prototype path registered as public route

## External Data Checks

- No external API calls
- No live web lookup
- No URL submission ingestion
- No account or private data ingestion

## Traceability and Interpretability Checks

- Every result must carry a deterministic `trace_id`
- Every posture candidate must expose protocol, standard, boundary, caveat, and guardrail refs
- Traceability must remain structured internal data only
- No natural-language report generation or public explanation rendering

## Fixture Coverage Checks

- Fixture coverage must be measured against governed coverage dimensions
- Coverage statuses are qualitative governance labels, not scores
- Future fixtures must reference named coverage gaps
- No fixture may be added for volume alone

## Prototype Rollback Checks

If disqualification triggers:

- Remove or revert violating files
- Restore sitemap and route registry if altered
- Re-run `validate_all.py` until PASS
- Document rollback in sprint audit

## Required PASS State Before Commit

Sprint 72 may commit implementation only when:

- all prototype-specific validators PASS
- `validate_all.py` PASS
- DECISION_LOG chronology validator PASS
- no Python cache files staged
- no unrelated untracked files remain
- prototype files not modified unless separately governed
- working tree contains only intended Sprint 72 scope

---

*Sprint 71 — Controlled Prototype v0 Validation Plan*  
*Decision: DEC-089*
