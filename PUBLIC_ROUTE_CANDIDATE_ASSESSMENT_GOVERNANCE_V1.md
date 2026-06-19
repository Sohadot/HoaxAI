# Public Route Candidate Assessment Governance v1

## A. Purpose

This document defines how future public route candidates may be assessed before any route-specific eligibility decision or route creation sprint.

## B. Non-Purpose

This sprint does not:

- assess a specific public route candidate;
- create a route candidate page;
- create a public route;
- approve a public route;
- add a sitemap URL;
- add public navigation;
- expose the internal prototype;
- modify the internal prototype;
- create a public workbench;
- create an engine;
- create a classifier;
- create a detector;
- create upload functionality;
- create scoring;
- create fake/real outputs;
- create forms;
- create user inputs;
- create analytics;
- create an API;
- create monetization;
- modify DNS or Cloudflare;
- launch the Hoax.ai custom domain;
- authorize deployment;
- authorize public release.

## C. Governing Principle

Route candidate assessment governance defines how future candidates are assessed. It does not assess, approve, create, or publish a route.

A candidate is not a route. An assessed candidate is not a created route. A validated candidate is not a public release.

## D. Candidate Assessment Definition

Public route candidate assessment is a governed pre-creation evaluation process that reviews a future route idea against purpose, non-purpose, route type, claim boundary, source posture, public-surface risk, sitemap implications, navigation implications, internal prototype exposure risk, operational implication, accessibility requirements, SEO/structured data boundary, security/privacy posture, and public-release non-authorization.

## E. Candidate Assessment Is Not

Assessment is not:

- route creation;
- route approval;
- route publication;
- sitemap inclusion;
- public navigation inclusion;
- workbench launch;
- engine readiness;
- classifier readiness;
- tool readiness;
- upload readiness;
- scoring readiness;
- API readiness;
- analytics readiness;
- deployment readiness;
- DNS readiness;
- Cloudflare readiness;
- custom domain readiness;
- monetization readiness;
- public release readiness.

## F. Assessment Inputs

A future candidate assessment must define:

1. Proposed route path
2. Proposed route title
3. Route type
4. Public purpose
5. Explicit non-purpose
6. Claim boundary
7. Source boundary
8. Structured data boundary
9. Sitemap intention
10. Navigation intention
11. Internal linking intention
12. Public-surface risk
13. Operational implication risk
14. Internal prototype exposure risk
15. Artifact-subject separation posture
16. Evidence posture boundary
17. Anti-detector language posture
18. Privacy/security posture
19. Accessibility baseline
20. Deployment/DNS boundary
21. Monetization boundary
22. Public-release boundary

## G. Assessment Outcomes

Possible assessment outcomes:

- not_assessed
- assessment_required
- candidate_assessment_ready
- candidate_under_assessment
- candidate_assessment_validated
- eligible_for_route_creation_sprint
- blocked_for_public_surface_risk
- blocked_for_operational_implication
- blocked_for_internal_prototype_exposure
- blocked_for_claim_or_source_gap
- blocked_for_sitemap_or_navigation_gap
- blocked_for_engine_classifier_upload_scoring_implication
- blocked_for_deployment_or_DNS_implication
- blocked_for_public_release_implication

No outcome may create a route. Even candidate_assessment_validated may only permit a future route creation sprint if all later gates agree.

## H. Candidate Classes

1. Reference Route Candidate
2. Governance Route Candidate
3. Language Route Candidate
4. Methodology Route Candidate
5. Static Explanatory Route Candidate
6. Public Workbench Route Candidate
7. Diagnostic Route Candidate
8. Tool Route Candidate
9. Engine Route Candidate
10. Upload Route Candidate
11. API Route Candidate

Reference, governance, language, methodology, and static explanatory route candidates may be assessable after governance.

Public workbench, diagnostic, tool, engine, upload, and API route candidates remain blocked until separate governance exists.

No candidate is assessed in Sprint 46.

## I. Prohibited Candidate Defaults

These candidate types are blocked by default until separate governance exists:

- public workbench;
- diagnostic route;
- tool route;
- engine route;
- classifier route;
- upload route;
- scoring route;
- API route;
- analytics route;
- monetization route;
- deployment route;
- DNS/custom-domain route.

## J. Internal Prototype Boundary

The internal static prototype is not a public route candidate by default. It must not be exposed, routed, indexed, linked, copied into a public page, or used as the basis for a public workbench without separate public workbench governance, privacy/security review, route readiness validation, sitemap governance, navigation governance, and deployment governance.

## K. Route Candidate Record Requirement

No candidate may be assessed without a route candidate assessment record. The record must define purpose, non-purpose, route type, claim boundary, source posture, public-surface risk, sitemap intention, navigation intention, internal prototype exposure risk, operational implication risk, and non-authorization status.

## L. Maturity

- version: v1.0.0
- status: public_route_candidate_assessment_governance_created
- maturity: candidate_assessment_governance_only_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier
