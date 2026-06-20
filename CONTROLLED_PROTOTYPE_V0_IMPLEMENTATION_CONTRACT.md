# Controlled Prototype v0 Implementation Contract

## Contract Statement

Sprint 72 may only implement what this contract permits. **Anything not explicitly allowed remains prohibited.**

This contract is a future Sprint 72 scope boundary. Sprint 71 does not authorize implementation.

## Source Authority

Future implementation must obey:

- Evidence Posture Standard v1
- Evidence Posture Protocol v1 Draft
- Engine Boundary Charter
- Evidence Posture Engine Model v0
- Output Language Guardrail Model v1
- Internal Non-Public Engine Prototype Charter
- Internal Prototype Admissibility Model
- Internal Prototype Fixture Policy
- Controlled Internal Prototype v0 Authorization Package
- Public Reference SEO Authority Map v1

## Future Implementation Scope

Future Sprint 72 may implement only:

- local-only internal prototype files under the authorized internal path
- fixture-bound parsing of governed synthetic fixtures
- protocol-step mapping
- evidence condition mapping
- posture-state candidate mapping
- boundary-check evaluation
- caveat-trigger mapping
- output guardrail application checks
- schema validation
- forbidden-output blocking
- non-public validation harness
- audit log stubs

## Future File Boundaries

Future files must remain under `internal/prototypes/controlled-engine-v0/` or an equivalently non-public governed path approved in Sprint 72.

Forbidden locations include public routes, sitemap, route registry, `/engine/`, `/tool/`, `/scanner/`, `/api/`, `/dashboard/`, `/upload/`, `/score/`, and public asset directories.

## Future Component Boundaries

Only permitted future component categories from the authorization package may be implemented. Prohibited components include detectors, classifiers, upload handlers, score calculators, API endpoints, public UI, result card renderers, report exporters, external fact checkers, live web connectors, analytics trackers, and user account connectors.

## Future Fixture Boundaries

Fixtures must be synthetic, neutral, case-neutral, non-personal, non-current-event, non-political, non-legal, non-medical, non-financial-advice, non-company-accusatory, and free of private personal data and real-person accusations. Real-person fixtures, current-event fixtures, and external fact-check targets are prohibited.

## Future Output Boundaries

Output may only be internal structured objects: posture_state_candidate, active_boundary_checks, triggered_caveats, prohibited_language_blocks, required_output_constraints, not_assessable_reason, out_of_scope_reason, guardrail_failure_flags.

Prohibited outputs include fake/real result, truth/falsity result, score, confidence percentage, accusation, subject guilt, deception finding, manipulation proof, fraud claim, legal conclusion, moderation action, public result card, and downloadable report.

## Future Validator Requirements

Sprint 72 must ship validators before or with implementation covering: no public route, fixture policy, output guardrail, forbidden language, no sitemap change, no public link, no external API, no upload, no score, and no JavaScript public behavior.

## Disallowed Implementation Behavior

Future implementation must not:

- create public routes or sitemap entries
- accept user input or uploads
- call external APIs or perform live web lookup
- emit verdict, score, fake/real, or accusation language
- render public result cards or export reports
- deploy, expose crawlers, or add analytics
- use JavaScript on public surfaces
- drift into demo, marketing, or product behavior

## No Public Exposure Rule

The prototype must remain non-public, non-routed, non-indexed, and unlinked from public navigation.

## No Route/Sitemap Rule

Sitemap must remain exactly 19 URLs. No new public route may be registered.

## No External Data Rule

No live web lookup, external API ingestion, account data ingestion, or external fact-checking targets.

## No Verdict/Scoring Rule

No scores, confidence percentages, fake/real labels, truth/falsity results, or subject guilt findings.

## Removal/Rollback Rule

If any disqualification condition is triggered, implementation must be rolled back or removed before commit. Validators must fail until violation is remediated.

## Sprint 72 Readiness Conditions

Sprint 72 may proceed only if:

- Sprint 71 authorization package validation passes
- DEC-089 is active
- this contract is accepted as governing
- prototype-specific validators are written before or with implementation
- sitemap remains 19 URLs
- prototype files under `_internal_prototypes/evidence-posture-workbench/` remain unmodified unless separately governed
- separate explicit Sprint 72 authorization is given

---

*Sprint 71 — Controlled Prototype v0 Implementation Contract*  
*Decision: DEC-089*
