# Hoax.ai Reference Candidate Evaluation and Prioritization

**Version:** v1.0.0  
**Status:** governed_internal_candidate_evaluation  
**Maturity:** evaluation_only_no_drafts_no_routes_no_publication  
**Decision:** DEC-036

## A. Purpose

This document governs how existing reference candidates are evaluated and prioritized before any draft, route, sitemap, or public page work.

## B. Non-Purpose

Candidate evaluation does **not**:

- create public pages;
- create draft pages;
- create internal draft files;
- create route files;
- activate routes;
- expand sitemap.xml;
- create public metadata;
- create SEO expansion;
- create public navigation links;
- create public classifier functionality;
- create a public tool;
- create upload functionality;
- create scoring;
- create forms;
- create analytics;
- deploy anything;
- enable DNS or Cloudflare;
- authorize publication.

## C. Governing Principle

**Evaluation ranks readiness. It does not grant publication permission.**

**A prioritized candidate is still not a page.**

## D. Evaluation Definition

Candidate evaluation is a governed internal review that determines whether a candidate is foundational, dependent, blocked, ready for a future draft blueprint, or deferred, based on substance readiness, governance clarity, claim/source scope, semantic SEO role, internal dependency value, boundary safety, and future drafting suitability.

## E. Priority Is Not

Priority is not:

- a numeric score;
- a quality score;
- an SEO score;
- a publication right;
- a route approval;
- a sitemap approval;
- a draft approval;
- a market-demand ranking;
- a keyword-volume ranking.

## F. Required Evaluation Dimensions

Each candidate is evaluated across:

1. Foundation Value
2. Governance Clarity
3. Claim/Source Scope Clarity
4. Semantic SEO Safety
5. Internal Link Dependency
6. Content Substance Readiness
7. Publisher Safety
8. Route Risk
9. Draft Blueprint Suitability
10. Blocking Issues

## G. Priority Bands

Qualitative bands only:

- priority_foundational
- priority_high_dependency
- priority_ready_for_draft_blueprint
- priority_needs_boundary_refinement
- priority_needs_claim_scope_refinement
- priority_defer
- priority_blocked

No band authorizes drafts or publication. `priority_ready_for_draft_blueprint` means future Internal Draft Blueprint consideration only.

## H. Readiness States

- evaluation_complete
- draft_blueprint_candidate
- needs_boundary_refinement
- needs_claim_source_refinement
- needs_semantic_seo_refinement
- dependency_candidate
- deferred
- blocked

No readiness state may be release_eligible, route_eligible, sitemap_eligible, draft_created, or publication_allowed.

## I. Sprint 18 Evaluation Summary

Eight candidates evaluated (REF-CAND-0001–0008). Foundational: Evidence Posture, Artifact–Subject Separation. High dependency: Claim and Source Traceability, Output Boundary, Source Confidence. Ready for draft blueprint consideration: Provenance Gap, Not Assessable Posture. Boundary refinement: Synthetic Fragility.

## J. Candidate Status After Sprint 18

Candidates remain internal_only, not_route_created, not_sitemap_eligible, not_draft_created, publication_blocked. Publisher remains blocked from drafts and publication. Future Internal Draft Blueprint may be considered.

## K. Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_candidate_evaluation |
| Maturity | evaluation_only_no_drafts_no_routes_no_publication |

## Machine-Readable Sources

- Policy: `data/reference-candidate-evaluation-policy.json`
- Evaluations: `data/reference-candidate-evaluation-v1.json`
- Priority bands: `data/reference-candidate-priority-bands.json`
- Dependencies: `data/reference-candidate-dependency-map.json`
- Validator: `validators/validate_reference_candidate_evaluation.py`
