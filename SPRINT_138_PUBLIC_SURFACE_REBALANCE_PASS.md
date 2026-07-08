# Sprint 138 — Public Surface Rebalance Pass

**Date:** 2026-07-08  
**Type:** Production corrective sprint (not audit-only)  
**Decision:** DEC-139 — Public Surface Rebalance and Audit Sprint Freeze

## Trigger

Existing live production surface at `https://hoax.ai/`, README drift, sitemap composition dominated by self-referential routes, and external framing friction from acquisition/review readiness pages indexed as public category surface.

## Objectives

1. Clean README — concise thesis, live routes, standard, protocol, utilities, boundaries, current status
2. Move sprint history to `CHANGELOG.md`
3. Remove self-referential strategic/review/acquisition routes from indexable public surface
4. Add quiet consolidated orientation at `/about-this-reference/`
5. Keep category-teaching routes (concepts, utilities, pathways, standard, protocol, evidence conditions)
6. Acceptance validation only — no new audit-only sprint chain

## Production changes

| Area | Change |
|------|--------|
| Public routes | 104 → **63** |
| Removed | 42 self-referential routes (entry-points, narrative, acquisition-readiness, external-review, reviewer-packet, executive-overview, strategic-review, system-map) |
| Added | `/about-this-reference/` |
| README | Rewritten; sprint wall removed |
| CHANGELOG | Created with sprint history |
| Homepage | Strategic/review/acquisition sections removed; public surface summary added |
| Archive | `docs/archive/public-surface-pre-rebalance/ARCHIVE_MANIFEST.md` |
| Governance | DEC-139 appended; audit sprint freeze rule active |

## Acceptance

- `validators/validate_public_surface_rebalance_pass_v1.py` — PASS
- `validators/validate_all.py` — PASS

## Boundary

This sprint does not delete governance. It relocates self-description off the indexable public surface and freezes sequential audit-only sprints unless tied to production contact per DEC-139.
