# Hoax.ai Internal Draft Blueprint Governance

**Version:** v1.0.0  
**Status:** governed_internal_draft_blueprint_governance  
**Maturity:** blueprint_governance_only_no_drafts_no_routes_no_publication  
**Decision:** DEC-037

## A. Purpose

This document governs the structure and admissibility of future internal drafts before any draft content may be created.

## B. Non-Purpose

Internal draft blueprint governance does **not**:

- create internal draft files;
- create public pages;
- create route files;
- activate routes;
- expand sitemap.xml;
- create public metadata;
- create public navigation links;
- create SEO expansion;
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

**A draft blueprint is not content. It is the contract content must satisfy before it can exist.**

**The first draft must be permitted by structure before it is written by language.**

## D. Internal Draft Definition

An internal draft is a non-public, non-route, non-sitemap, non-indexable, governance-bound working artifact that may later be created only after candidate evaluation, draft blueprint approval, claim/source scope, section contracts, semantic SEO boundaries, and validation gates are satisfied.

## E. Draft Blueprint Definition

A draft blueprint is a structured pre-draft contract that defines the required sections, claim boundaries, source scope, semantic SEO role, prohibited implications, internal link plan, review status, gate dependencies, and non-public status for a future internal draft.

## F. Draft Blueprint Is Not

A draft blueprint is not:

- a page;
- a draft;
- a route;
- a sitemap entry;
- a public URL;
- public metadata;
- publication approval;
- SEO expansion;
- proof of truth;
- source verification;
- route eligibility;
- deployment readiness.

## G. Required Future Draft Blueprint Fields

Every future draft blueprint must include:

- blueprint_id
- candidate_id
- candidate_name
- candidate_evaluation_ref
- blueprint_status
- draft_status
- route_status
- sitemap_status
- publication_status
- page_family
- page_type_ref
- reference_thesis
- reference_purpose
- definition_scope
- governance_boundary
- claim_scope
- source_scope
- semantic_seo_role
- section_contracts
- prohibited_misreadings
- forbidden_public_implications
- internal_link_plan
- structured_data_boundary
- interface_boundary
- security_privacy_boundary
- required_gates
- review_status
- non_authorization_statement
- notes

## H. Required Future Draft Sections

Every future internal draft must be governed by these section contracts:

1. Draft Thesis
2. Definition and Scope
3. Governance Boundary
4. Relationship to Hoax.ai System
5. Semantic SEO Role
6. Claim and Source Traceability
7. Prohibited Misreadings
8. Internal Link Plan
9. Structured Data Boundary
10. Review Status

Conditional sections:

- Taxonomy Relationship
- Standard Relationship
- Protocol Relationship
- Output Boundary Relationship
- Candidate Dependency Notes
- Source Scope Notes
- Publisher Notes

## I. Draft State Rules

Allowed draft blueprint states:

- blueprint_not_created
- blueprint_required
- blueprint_created_internal
- blueprint_validation_pending
- blueprint_validated
- ready_for_future_internal_draft_pack
- blocked_needs_candidate_refinement
- blocked_needs_claim_scope
- blocked_needs_source_scope
- blocked_needs_boundary_refinement
- retired

Prohibited states:

- draft_created
- public_page_created
- route_active
- sitemap_eligible
- publication_allowed
- release_eligible
- deployed

## J. Future Draft Location Rule

No actual draft location is created in Sprint 19.

If future internal drafts are later allowed, they must be stored only in a clearly non-public internal path such as `internal/drafts/` or `governance/drafts/`. Sprint 19 does not create any draft directory.

## K. Draft Prohibitions

Future internal drafts must never:

- imply Hoax.ai is a truth machine;
- imply active detector capability;
- imply public classifier availability;
- imply upload workflow;
- imply scoring;
- imply fake/real verdicts;
- imply subject guilt;
- invent sources;
- invent citations;
- use unsupported external factual claims;
- create clickbait SEO;
- create public service/product/software claims;
- bypass validate_all.py.

## L. Candidate Eligibility for Future Blueprint

Only evaluated candidates with readiness_state `draft_blueprint_candidate` or `dependency_candidate` may be considered for a future draft blueprint pack.

Candidates with `needs_boundary_refinement` must not receive a draft blueprint until refinement passes.

## M. Publisher Status After Sprint 19

After this sprint:

- internal draft blueprint governance exists;
- publisher remains blocked from actual drafts;
- future First Internal Draft Blueprint Pack may be considered;
- no draft generation is authorized;
- no public release is authorized.

## N. Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_draft_blueprint_governance |
| Maturity | blueprint_governance_only_no_drafts_no_routes_no_publication |

## Machine-Readable Sources

- Policy: `data/internal-draft-blueprint-policy.json`
- Templates: `data/internal-draft-template-registry.json`
- Section contracts: `data/internal-draft-section-contracts.json`
- State machine: `data/internal-draft-state-machine.json`
- Readiness gates: `data/internal-draft-readiness-gates.json`
- Validator: `validators/validate_internal_draft_blueprint_governance.py`
