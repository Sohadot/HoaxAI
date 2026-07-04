# Sprint 136 — Live Public Surface Parity Audit v1

**Status:** Complete — audit-only live parity audit  
**Date:** 2026-07-04

## Goal

Audit parity between the validated Sprint 135 repository release candidate and the deployed live public surface at `https://hoax.ai/`.

## Result

The live site is reachable and repository-aligned for route count, sitemap count, robots sitemap reference, and sampled route availability. The live sitemap contains 104 URLs and matches the repository sitemap route set.

Sprint 135 release-candidate language is not yet visible on the live homepage/system map. This is recorded as live deployment freshness lag, not a repository validation failure.

## Deliverables

- `LIVE_PUBLIC_SURFACE_PARITY_AUDIT_V1.md`
- `data/live-public-surface-parity-audit-v1.json`
- `data/live-public-surface-parity-audit-v1.schema.json`
- `validators/validate_live_public_surface_parity_audit_v1.py`
- CLAIM-0137 and PUB-GATE-0130 governance updates

## Non-Expansion Confirmation

- No new public routes
- No live status page
- No deployment page
- No release page
- No launch page
- No new DEC
- 60 live parity records inventoried
- 60 live parity scenarios tested

## Validation

- `py -3 validators/validate_live_public_surface_parity_audit_v1.py` — PASS
- `py -3 validators/validate_all.py` — PASS
- internal prototype harnesses — PASS
