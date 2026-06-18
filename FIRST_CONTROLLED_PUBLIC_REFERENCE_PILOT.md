# Hoax.ai First Controlled Public Reference Pilot

**Version:** v1.0.0  
**Status:** first_controlled_public_reference_pilot  
**Maturity:** two_public_reference_pages_only_no_engine_no_classifier_no_tool  
**Decision:** DEC-042

## A. Purpose

Sprint 24 creates the first two controlled public reference pages for Hoax.ai.

## B. Non-Purpose

This pilot does **not** create a public classifier, public engine, public tool, upload workflow, scoring, fake/real outputs, forms, analytics, API, monetization, DNS/Cloudflare changes, custom domain launch, broader page expansion, or unrestricted publication.

## C. Governing Principle

**A controlled public reference page teaches the language. It does not operate the engine.**

**The first public routes must make Hoax.ai's category legible before any public classifier exists.**

## D. Pilot Scope

| Path | Concept |
|------|---------|
| `/reference/evidence-posture/` | Evidence Posture |
| `/reference/artifact-subject-separation/` | Artifact–Subject Separation |

## E. Why These Two Pages

**Evidence Posture:** The central category term of Hoax.ai. It defines the condition of the evidence before verdict, belief, action, publication, escalation, or institutional response.

**Artifact–Subject Separation:** The governing boundary that prevents a statement about an evidence artifact from becoming a statement about a person, institution, brand, event, or connected subject.

## F. Controlled Public Page Definition

A controlled public reference page is a public HTML route that explains a governed Hoax.ai concept under strict boundary, claim/source, metadata, link, accessibility, and non-tool constraints. It may educate the public. It may not operate as a classifier, detector, upload tool, scoring system, or verdict engine.

## G. Public Route Status

For the two pages only:

- route_status: controlled_public_reference_route_created
- sitemap_status: sitemap_included_controlled_reference_pilot
- public_metadata_status: controlled_public_metadata_created
- public_navigation_status: linked_from_homepage_reference_section
- publication_status: controlled_public_reference_pilot
- deployment_status: repository_public_preview_only

## H. Maturity

- version: v1.0.0
- status: first_controlled_public_reference_pilot
- maturity: two_public_reference_pages_only_no_engine_no_classifier_no_tool

## Machine-Readable Sources

- Policy: `data/controlled-public-reference-pilot-policy.json`
- Record: `data/controlled-public-reference-pilot-v1.json`
- Validator: `validators/validate_controlled_public_reference_pilot.py`
