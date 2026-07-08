# Sprint 140 — Claim Drift Reference Deepening

**Date:** 2026-07-08  
**Type:** Production deepening (category reference)  
**Decision:** None — no new governing rule required

## Scope

- Deepen existing `/claim-drift/` only
- No new route, sitemap change, audit sprint, or DEC

## Goal

Make Claim Drift a reusable category concept: when a claim exceeds what evidence can support — including when the artifact is real.

## Production change

- Strengthened definition, drift chain, common patterns, reader questions, fictional examples, and boundary section
- Updated Reference Answer, Source Confidence, Cite This Reference, and Retrieval Capsule alignment
- Reader bridge from fake/real entry question to evidence-limit question (bounded, non-verdict)

## Acceptance

- `validators/validate_all.py` — PASS
- Route count unchanged (63)
