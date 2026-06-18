# Hoax.ai Reference Page Blueprint

**Version:** v1.0.0  
**Status:** governed_internal_reference_blueprint  
**Maturity:** pre_reference_expansion_gate  
**Decision:** DEC-029

## A. Purpose

This blueprint defines the minimum requirements for future Hoax.ai reference pages.

## B. Non-Purpose

This blueprint does **not**:

- create new public pages;
- create new routes;
- create SEO expansion;
- create sitemap expansion;
- create deployment readiness;
- create DNS or Cloudflare work;
- create a public classifier;
- create a public tool;
- create upload functionality;
- create monetization;
- create external factual claims.

## C. Governing Principle

**A reference page is not a URL. It is a governed unit of reference value.**

**No reference expansion before blueprint, claim mapping, route eligibility, source scope, link integrity, and technical quality gates exist.**

## D. Reference Page Definition

A Hoax.ai reference page is a public page that explains a governed concept, term, posture state, dimension, standard element, protocol element, source/claim boundary, or reference framework in a way that is useful, bounded, internally linked, claim-traceable, technically valid, and non-thin.

## E. Prohibited Page Types

- thin SEO pages;
- keyword-only pages;
- placeholder pages;
- future-route teaser pages;
- tool-implying pages;
- upload-implying pages;
- fake/real detector pages;
- sensational examples;
- accusation-oriented pages;
- unsupported superiority claim pages;
- pages with public claims not mapped to evidence ledger;
- pages with external factual claims not source-supported;
- pages not listed in candidate registry before creation.

## F. Allowed Future Reference Page Families

These families are **future page types only — not active routes**:

1. Category Language Pages
2. Evidence Posture State Pages
3. Evidence Posture Dimension Pages
4. Standard Element Pages
5. Protocol Stage Pages
6. Output Boundary Pages
7. Governance Boundary Pages
8. Reference Framework Pages

These families are not routes yet. They require candidate registration and expansion gate approval before creation.

## G. Minimum Page Requirements

Every future reference page must have:

- registered candidate ID;
- approved page family;
- route candidate status;
- defined reference purpose;
- page thesis;
- target concept or governed entity;
- allowed claim scope;
- required claim mappings;
- source support scope;
- internal link obligations;
- outbound source policy where applicable;
- metadata requirements;
- canonical plan;
- sitemap eligibility plan;
- no active tool implication;
- no unsupported external factual claims;
- no subject accusation risk;
- no fake/real verdict language;
- no scoring language;
- accessibility and technical quality compliance.

## H. Required Page Sections

Every future reference page must include, where applicable:

1. Page Thesis
2. Definition / Scope
3. Governance Boundary
4. Relationship to Taxonomy / Standard / Protocol
5. Allowed Use
6. Prohibited Misreadings
7. Claim and Source Traceability
8. Internal Links
9. Last Reviewed

## I. Expansion Gate

A page candidate may move through these statuses only:

- proposed_internal
- blueprint_checked
- claim_mapping_required
- source_scope_required
- route_candidate
- validation_pending
- release_eligible
- blocked
- retired

Public release eligibility requires:

- candidate registry entry;
- route registry entry;
- claim-source map alignment;
- public claim map prepared;
- source registry alignment;
- link graph update;
- sitemap eligibility;
- technical quality validation;
- forbidden language validation;
- interface governance validation;
- security/privacy validation;
- content quality substance validation;
- publisher control plane validation;
- final audit.

## J. Sitemap Rule

No future page may be added to sitemap.xml unless:

- it exists as a public file;
- its route is active in route-registry;
- it is marked sitemap eligible;
- internal links are valid;
- claim/source traceability passes;
- technical quality passes.

## K. Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_reference_blueprint |
| Maturity | pre_reference_expansion_gate |

## Machine-Readable Sources

- Blueprint: `data/reference-page-blueprint.json`
- Page types: `data/reference-page-type-registry.json`
- Expansion gate: `data/reference-expansion-gate.json`
- Candidates: `data/reference-page-candidate-registry.json`
- Validator: `validators/validate_reference_page_blueprint.py`
