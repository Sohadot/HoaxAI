# Public Route Candidate Registry Governance v1

## A. Purpose

This document defines how future public route candidates may be recorded in a governed registry before assessment, eligibility validation, route creation, sitemap inclusion, navigation inclusion, deployment, or release.

## B. Non-Purpose

This sprint does not:

- register an actual candidate;
- instantiate a candidate record;
- assess a candidate;
- select a candidate route;
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

A candidate registry governs how candidates may be recorded. It does not create, assess, approve, or publish candidates.

A registry entry is not a route. A registered candidate is not an assessed candidate. A governed registry is not launch permission.

## D. Candidate Registry Definition

A public route candidate registry is a governed internal record system for future route ideas that may be considered for assessment only after the candidate entry satisfies required identity, purpose, non-purpose, route type, claim boundary, source boundary, public-surface risk, prototype exposure risk, sitemap intention, navigation intention, operational implication, and non-authorization fields.

## E. Candidate Registry Is Not

A candidate registry is not:

- public route creation;
- public route approval;
- candidate assessment;
- candidate validation;
- sitemap inclusion;
- public navigation inclusion;
- public workbench launch;
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

## F. Registry Entry Requirement

A future candidate registry entry must include:

1. candidate_id
2. candidate_name
3. proposed_route_path
4. proposed_route_title
5. candidate_class
6. route_type
7. public_purpose
8. explicit_non_purpose
9. claim_boundary
10. source_boundary
11. structured_data_boundary
12. sitemap_intention
13. navigation_intention
14. internal_linking_intention
15. public_surface_risk
16. operational_implication_risk
17. internal_prototype_exposure_risk
18. artifact_subject_separation_posture
19. evidence_posture_boundary
20. anti_detector_language_posture
21. privacy_security_posture
22. accessibility_baseline
23. deployment_DNS_boundary
24. monetization_boundary
25. public_release_boundary
26. assessment_required
27. current_candidate_state
28. required_next_gate
29. non_authorization_statement
30. date_recorded

Sprint 48 defines these requirements only. It does not create a real entry.

## G. Registry Candidate States

- registry_not_created
- registry_governance_defined
- registry_governance_validated
- entry_not_allowed
- entry_required_governance
- entry_template_defined
- entry_ready_for_future_recording
- candidate_recorded
- candidate_record_requires_assessment
- candidate_under_assessment
- candidate_assessment_validated
- eligible_for_route_creation_sprint
- blocked_for_missing_required_fields
- blocked_for_public_surface_risk
- blocked_for_operational_implication
- blocked_for_internal_prototype_exposure
- blocked_for_sitemap_or_navigation_gap
- blocked_for_engine_classifier_upload_scoring_implication
- blocked_for_public_release_implication

No state may create a route. No state may add a sitemap entry. No state may add public navigation. No state may authorize public release.

## H. Registry Entry Classes

1. Reference Route Candidate Entry
2. Governance Route Candidate Entry
3. Language Route Candidate Entry
4. Methodology Route Candidate Entry
5. Static Explanatory Route Candidate Entry
6. Public Workbench Route Candidate Entry
7. Diagnostic Route Candidate Entry
8. Tool Route Candidate Entry
9. Engine Route Candidate Entry
10. Upload Route Candidate Entry
11. API Route Candidate Entry

Reference, governance, language, methodology, and static explanatory candidate entries may be recordable only after registry validation.

Public workbench, diagnostic, tool, engine, upload, API, classifier, scoring, analytics, monetization, deployment, and DNS/custom-domain candidates remain blocked by default unless separate governance exists.

Sprint 48 records no candidate entry.

## I. Registry Zero-State

Sprint 48 creates registry governance only. It does not create a populated registry, does not register candidate entries, does not create candidate IDs, does not create candidate pages, and does not select any route path for assessment.

## J. Internal Prototype Boundary

The internal static prototype is not a registry entry by default. It must not be recorded as a public route candidate, exposed, routed, indexed, linked, copied into a public page, or used as the basis for a public workbench without separate public workbench governance, privacy/security review, route readiness validation, sitemap governance, navigation governance, deployment governance, and custom-domain governance.

## K. Future Candidate Registration Requirement

A future candidate registration sprint must:

1. reference this registry governance;
2. pass registry governance validation;
3. create a candidate entry using the approved template;
4. avoid public route creation;
5. avoid sitemap expansion;
6. avoid public navigation;
7. avoid prototype exposure;
8. avoid engine/classifier/upload/scoring implication;
9. preserve public-release blocking;
10. pass a dedicated registry-entry validator.

## L. Maturity

- version: v1.0.0
- status: public_route_candidate_registry_governance_created
- maturity: registry_governance_only_no_candidate_registered_no_candidate_assessed_no_route_no_sitemap_no_public_release_no_engine_no_classifier
