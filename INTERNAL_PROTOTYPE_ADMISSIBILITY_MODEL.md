# Internal Prototype Admissibility Model

## Admissibility Statement

A future Hoax.ai internal prototype is **admissible** only when it satisfies every precondition in this model. Admissibility is not authorization. A file may be technically possible to create but not admissible unless it obeys the standard, protocol, engine boundary, engine model, output guardrail, fixture policy, and public-exposure boundary.

## Permission vs Admissibility

| Concept | Meaning |
|---------|---------|
| **Permission** | Explicit sprint authorization to build or run a controlled internal prototype |
| **Admissibility** | Technical and governance preconditions that must be true before permission may even be considered |

Sprint 70 defines admissibility. Sprint 70 does **not** grant permission.

## Required Preconditions

Before any future prototype may be considered admissible:

1. Evidence Posture Standard v1 validation passes
2. Evidence Posture Protocol v1 Draft validation passes
3. Engine Boundary Charter validation passes
4. Evidence Posture Engine Model v0 validation passes
5. Output Language Guardrail Model v1 validation passes
6. Internal Non-Public Engine Prototype Charter validation passes
7. Internal Prototype Fixture Policy validation passes
8. Sitemap remains exactly 19 URLs
9. No public route exists for the prototype
10. A prototype-specific validator exists before implementation

## Disqualifying Conditions

Any of the following disqualifies a prototype immediately:

- public route registration
- sitemap entry
- homepage or reference-layer link to prototype
- upload interface or form
- API endpoint exposure
- public JavaScript behavior
- score or confidence percentage output
- fake/real or truth/falsity result
- subject guilt or deception finding
- external API ingestion for fact-checking
- real-person accusation fixtures
- active news event fixtures
- deployment to public asset pipeline

## Fixture Admissibility

Fixtures must satisfy `INTERNAL_PROTOTYPE_FIXTURE_POLICY.md`. Non-synthetic, accusatory, current-event, or private-data fixtures are inadmissible.

## Output Admissibility

Output may only use bounded structure types defined in the prototype charter output boundary. Any verdict, score, result card, or shareable report output is inadmissible.

## Environment Admissibility

Prototype environment must be local-only or non-public test directory. No deployment, analytics, crawler exposure, or external API calls.

## Public-Exposure Disqualification

Any path to public discovery — route, sitemap, link, demo URL, SEO-indexable page — disqualifies the prototype regardless of internal intent.

## External-Data Disqualification

Live web lookup, external fact-check targets, uploaded user files, account data, and private message ingestion disqualify the prototype.

## Prototype-to-Product Drift Prevention

The prototype must not be framed as product, detector, scanner, upload tool, or public report engine. Documentation, filenames, and output structures must preserve non-operational, non-public status.

## Future Sprint 71 Readiness Conditions

Sprint 71 may consider Controlled Internal Prototype v0 Authorization Package only if:

- DEC-088 charter validation passes
- this admissibility model is registered in source registry
- fixture policy is registered
- publisher status reflects charter validation complete
- separate explicit DEC authorizes prototype v0
- prototype-specific validator is written before any implementation file

---

*Sprint 70 — Internal Prototype Admissibility Model*
*Decision: DEC-088*
