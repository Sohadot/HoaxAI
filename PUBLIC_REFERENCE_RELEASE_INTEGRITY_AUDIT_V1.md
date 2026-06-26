# Public Reference Release Integrity Audit v1

Sprint 100 — Public Reference Release Integrity Audit v1  
**Decision:** DEC-118  
**Date:** 2026-06-26

## Audit statement

Hoax.ai completed a full release-integrity audit across all 58 public routes. The homepage received a Public Release Integrity Snapshot as visible production contact. No additional metadata, link, component, boundary, or route-count defects were found on inspection.

## Inspection scope

- 58 routes in `data/route-registry.json`
- 58 URLs in `sitemap.xml`
- 58 public HTML route files on disk
- Metadata: H1, canonical, meta description, Open Graph title/description
- Internal route links (`href` values starting with `/`)
- Stale route-count language in public HTML
- Strategic surface components from Sprint 99
- Acquisition-readiness non-transactional boundaries
- `data/public-file-registry.json` alignment for public route HTML files

## Results

| Check | Result |
|-------|--------|
| Homepage Public Release Integrity Snapshot | Added |
| Full 58-route inspection | Completed |
| Route-count mismatch | None |
| Metadata defects | None |
| Broken internal route links | None |
| Component drift | None |
| Boundary drift | None |
| Stale route-count language in public HTML | None |
| New public routes | None |
| Sitemap URL count | 58 (unchanged) |
| Route registry entries | 58 (unchanged) |
| Public-file-registry route HTML alignment | All 58 route files tracked; registry also includes `styles.css`, `sitemap.xml`, `robots.txt` as non-route support files |
| Additional visible repairs | None beyond homepage snapshot |
| total_repairs_made | 1 |

## 58-Route Release Inventory

Route groups and counts (from `data/route-registry.json`):

| Route group | Count |
|-------------|------:|
| Homepage | 1 |
| Public Utilities | 4 |
| Core Reference Concepts | 6 |
| Deep Reference Concepts | 6 |
| Evidence-Risk Pathways | 6 |
| Strategic Entry Points | 6 |
| Strategic Narrative | 5 |
| Strategic Readiness | 6 |
| Boundary / Standard / Governance / Support References | 18 |
| **Total** | **58** |

### Homepage (1)

- `/` — Hoax.ai

### Public Utilities (4)

- `/manual-evidence-checklist/` — Manual Evidence Checklist
- `/evidence-posture-map/` — Evidence Posture Map
- `/synthetic-examples/` — Synthetic Evidence-Risk Examples
- `/evidence-risk-questions/` — Evidence-Risk Questions

### Core Reference Concepts (6)

- `/evidence-risk/` — Evidence Risk
- `/provenance-risk/` — Provenance Risk
- `/context-collapse/` — Context Collapse
- `/claim-drift/` — Claim Drift
- `/traceability-gap/` — Traceability Gap
- `/why-hoax-ai-is-not-a-detector/` — Why Hoax.ai Is Not a Detector

### Deep Reference Concepts (6)

- `/source-ambiguity/` — Source Ambiguity
- `/artifact-claim-gap/` — Artifact-Claim Gap
- `/boundary-integrity/` — Boundary Integrity
- `/evidence-weight/` — Evidence Weight
- `/interpretation-risk/` — Interpretation Risk
- `/not-assessable-posture/` — Not-Assessable Posture

### Evidence-Risk Pathways (6)

- `/pathways/source-unclear/` — When the Source Is Unclear
- `/pathways/provenance-weak/` — When Provenance Is Weak
- `/pathways/context-missing/` — When Context Is Missing
- `/pathways/claim-overextended/` — When the Claim Goes Beyond the Artifact
- `/pathways/traceability-incomplete/` — When Traceability Is Incomplete
- `/pathways/posture-not-assessable/` — When Evidence Is Not Assessable

### Strategic Entry Points (6)

- `/entry-points/` — Hoax.ai Entry Points
- `/entry-points/human-readers/` — For Human Readers
- `/entry-points/ai-agents/` — For AI Agents
- `/entry-points/research-review/` — For Research and Review
- `/entry-points/trust-safety/` — For Trust and Safety Teams
- `/entry-points/education-literacy/` — For Education and Literacy

### Strategic Narrative (5)

- `/narrative/` — Hoax.ai Strategic Narrative
- `/narrative/evidence-before-verdict/` — Evidence Before Verdict
- `/narrative/why-evidence-risk/` — Why Evidence Risk Matters
- `/narrative/reference-before-detection/` — Reference Before Detection
- `/narrative/non-verdict-trust/` — Non-Verdict Trust

### Strategic Readiness (6)

- `/acquisition-readiness/` — Hoax.ai Acquisition Readiness
- `/acquisition-readiness/category-asset/` — Category Asset Readiness
- `/acquisition-readiness/public-reference-surface/` — Public Reference Surface Readiness
- `/acquisition-readiness/governance-traceability/` — Governance Traceability Readiness
- `/acquisition-readiness/ai-retrieval-readiness/` — AI Retrieval Readiness
- `/acquisition-readiness/non-detector-moat/` — Non-Detector Moat

### Boundary / Standard / Governance / Support References (18)

- `/language/` — Hoax.ai Category Language
- `/interface/evidence-field/` — Hoax.ai Evidence Field Interface Thesis
- `/protocol/evidence-posture/` — Hoax.ai Evidence Posture Protocol v1 Draft
- `/standard/evidence-posture/` — Hoax.ai Evidence Posture Standard v1
- `/reference/evidence-posture/` — Evidence Posture
- `/reference/artifact-subject-separation/` — Artifact–Subject Separation
- `/reference/source-confidence/` — Source Confidence
- `/reference/provenance-gap/` — Provenance Gap
- `/reference/not-assessable/` — Not Assessable
- `/reference/output-boundary/` — Output Boundary
- `/reference/synthetic-fragility/` — Synthetic Fragility
- `/reference/evidence-chain/` — Evidence Chain
- `/reference/context-collapse/` — Context Collapse
- `/reference/claim-source-traceability/` — Claim–Source Traceability
- `/reference/attribution-boundary/` — Attribution Boundary
- `/reference/claim-drift/` — Claim Drift
- `/reference/evidence-limitation/` — Evidence Limitation
- `/reference/interpretation-risk/` — Interpretation Risk

## Public-file-registry scope

`data/public-file-registry.json` tracks public route HTML files plus non-route support assets (`styles.css`, `sitemap.xml`, `robots.txt`). All 58 route HTML files are registered. Governance documents and validator code are out of scope for public-file-registry route tracking.

## Boundary preservation

- Non-verdict boundary preserved across inspected pages
- Non-transactional review boundary preserved on acquisition-readiness pages and homepage snapshot
- No upload, score, verdict, detector claim, public API, automated report, JavaScript, forms, chatbot, generator, pricing statement, transaction page, acquisition term document, representative mandate, legal representation, or financial representation introduced

## Validator

`validators/validate_public_reference_release_integrity_audit_v1.py` — PASS required  
`validators/validate_all.py` — PASS required
