# Hoax.ai Governed Publisher Control Plane

**Version:** v1.0.0  
**Status:** governed_internal_publisher_control_plane  
**Maturity:** publisher_blocked_until_quality_standard  
**Decision:** DEC-031

## A. Purpose

The publisher control plane defines how future automated or semi-automated content production may create governed reference candidates without bypassing gates.

## B. Non-Purpose

The publisher control plane does **not**:

- publish content now;
- create public pages now;
- create draft pages now;
- create routes now;
- expand sitemap now;
- generate SEO pages now;
- deploy anything;
- enable DNS or Cloudflare;
- create a public classifier;
- create upload, scoring, forms, analytics, APIs, or monetization.

## C. Governing Principle

**Automation may produce candidates. Governance decides what becomes public.**

**The publisher must not generate volume. It must generate governed reference value.**

## D. Publisher Role

The publisher is a controlled pipeline that may later transform approved reference candidates into internal drafts or pull requests only after content quality, claim/source, route/link, technical, interface, security/privacy, forbidden language, and expansion gates are satisfied.

## E. Publisher Current Status

| Field | Value |
|-------|-------|
| current_status | blocked_until_internal_draft_blueprint |

**Reason:** Reference Candidate Evaluation (Sprint 18) completed for eight internal candidates. Publisher remains blocked from drafts, public pages, routes, and publication until a future Internal Draft Blueprint sprint and explicit approval.

## F. Publisher Workflow Stages

Future stages:

1. topic_intake
2. candidate_registration
3. page_family_assignment
4. claim_scope_definition
5. source_scope_definition
6. outline_from_blueprint
7. substance_gate_check
8. internal_draft_generation
9. claim_mapping
10. route_candidate_review
11. technical_validation
12. governance_review
13. pull_request_preparation
14. release_candidate_review
15. public_release_gate

## G. Publisher State Machine

Allowed states:

- blocked
- proposed_internal
- candidate_registered
- blueprint_checked
- substance_required
- claim_mapping_required
- source_scope_required
- draft_allowed_internal
- draft_generated_internal
- validation_pending
- governance_review_required
- pull_request_ready
- release_candidate
- release_eligible
- public_release_blocked
- retired

## H. Publisher Prohibitions

The publisher must never:

- publish directly to live domain;
- add sitemap entries without release eligibility;
- add route-registry active routes without gate approval;
- invent sources;
- invent external claims;
- write fake citations;
- create content from unsupported current events;
- create keyword-only pages;
- create generic AI commentary;
- create fake/real detector pages;
- create accusation-oriented pages;
- create tool-promise pages;
- create public upload/scoring/classifier language;
- bypass `validators/validate_all.py`;
- bypass human/governance approval.

## I. Publisher Output Rule

**Allowed future outputs** after later gates:

- candidate registry entries;
- draft outlines;
- internal draft pages only if later approved;
- pull requests for review;
- audit records;
- manifest updates.

**Current Sprint 13B output:**

- publisher policy only;
- publisher workflow registry;
- publisher state machine;
- publisher quality gates;
- publisher queue registry;
- publisher validator;
- no content drafts.

## J. Human/Governance Approval Rule

No publisher output becomes public unless:

- candidate approved;
- content quality standard passes;
- claim/source mapping passes;
- route/link integrity passes;
- technical quality passes;
- interface governance passes;
- security/privacy passes;
- forbidden language passes;
- `validators/validate_all.py` passes;
- audit file exists;
- user approval or explicit sprint instruction exists.

## K. Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_publisher_control_plane |
| Maturity | publisher_blocked_until_quality_standard |

## Publisher Publishing Philosophy

The Hoax.ai publisher is not a volume engine. It is a governed reference production system.

The publisher does not produce pages. It produces release-eligible reference units.

SEO is a consequence of governed reference value, not a substitute for it.

A future publisher output must satisfy seven publishing contracts before it may become public:

### 1. Reference Substance Contract

The candidate must carry governed reference substance: purpose, definition, scope, boundary, system relationship, claim traceability, source scope, internal link logic, prohibited misreadings, review posture, and technical quality.

### 2. Claim/Source Integrity Contract

The candidate must not contain unsupported external factual claims, invented citations, broad source overreach, or unmapped public claims. Every material claim must be traceable to the evidence ledger, claim-source map, source registry, and support location where applicable.

### 3. Semantic SEO Discipline Contract

The candidate must use SEO as semantic clarification, not keyword inflation. Title, meta description, H1, headings, slug, internal links, canonical, and structured data must express the governed concept accurately without implying active tool capability, fake/real detection, scoring, upload, or unsupported authority.

### 4. Route and Sitemap Eligibility Contract

The candidate must not become a route until route-registry status, canonical policy, link graph, sitemap eligibility, and reference expansion gate requirements are satisfied.

### 5. Boundary Safety Contract

The candidate must not imply truth certification, fake/real verdicts, deepfake detection, public classifier availability, upload workflow, scoring, subject accusation, fraud determination, or event verification.

### 6. Technical Quality Contract

The candidate must pass static technical quality checks: HTML structure, metadata, accessibility, local dependencies, static security, no external scripts, no forms, no analytics, no tracking, no API calls, and no unresolved placeholders.

### 7. Governance Approval Contract

The candidate must not become public without `validate_all.py` PASS, audit record, manifest update, required registry updates, and explicit user/governance approval.

## Publisher SEO Rule

The publisher may prepare SEO metadata only after the reference thesis, page family, claim scope, source scope, and route purpose are defined. SEO metadata must never create a claim that the page body, evidence ledger, and source map do not support.

## Publisher Prohibited SEO Patterns

- keyword stuffing;
- search-volume-first page creation;
- generic AI explainer pages;
- repeated thesis pages with different keywords;
- programmatic route inflation;
- location/category combinations without governed need;
- pages created only for sitemap volume;
- fake/real detector keyword capture;
- deepfake detector keyword capture;
- tool-implying titles;
- clickbait metadata;
- unsupported superiority claims;
- schema markup that overclaims product, software, tool, service, or detector status.

## Publisher Future Quality Metrics

Do not use numeric SEO scores, quality scores, percentages, or grades.

Use governed pass/fail gates:

- reference_substance_passed
- claim_source_traceability_passed
- semantic_seo_boundary_passed
- route_link_integrity_passed
- technical_quality_passed
- interface_boundary_passed
- security_privacy_passed
- forbidden_language_passed
- governance_approval_required

## Machine-Readable Sources

- Policy: `data/publisher-governance-policy.json`
- Workflows: `data/publisher-workflow-registry.json`
- State machine: `data/publisher-state-machine.json`
- Quality gates: `data/publisher-quality-gates.json`
- Queues: `data/publisher-queue-registry.json`
- Validator: `validators/validate_publisher_control_plane.py`
