# Public Reference Production Plan v1

## Purpose

This plan defines the production schedule and quality requirements for the next batch of real public reference pages on Hoax.ai.

Sprint 52 freezes meta-governance scaffolding and resets the project toward public reference production. This plan prepares the first 10 page candidates and defines their purpose, route paths, internal linking strategy, source/claim posture, metadata requirements, validation requirements, and release order.

Sprint 52 does not create these pages. Sprint 53 creates the first release batch.

## Production Threshold

Before any new meta-governance layer may be proposed:

- Minimum additional public reference pages: **10**
- Current public reference pages: 3 (evidence-posture, artifact-subject-separation, language)
- Pages needed: 10 additional governed reference pages

## Page Candidates

### Batch 1 — Initial Release (Sprint 53)

#### Page 1: /reference/source-confidence/

**Purpose:** Explain what it means for a source to carry confidence weight in evidence posture analysis.

**Route path:** `/reference/source-confidence/`

**Page purpose:** A reference page that defines source confidence as an evidence posture dimension — how source origin, verifiability, history, and corroborating signals affect the confidence weight applied during evidence posture assessment. Not a scoring interface. Not a tool.

**Relation to existing pages:** Extends Evidence Posture (/reference/evidence-posture/) and supports the claim/source discipline framework.

**Internal link strategy:**
- Link from: /reference/evidence-posture/, /reference/artifact-subject-separation/
- Link to: /reference/provenance-gap/ (when created)

**Source/claim posture:** Repository-supported governance claims only. No external factual claims unless ledger-registered and traceable.

**Metadata requirements:** Title, meta description, canonical URL, H1 exactly matching route purpose.

**Validation:** Must pass validate_all.py including content quality, route integrity, claim source traceability, and technical quality gates.

---

#### Page 2: /reference/provenance-gap/

**Purpose:** Define what happens when origin, chain of custody, or creation context cannot be established for an artifact.

**Route path:** `/reference/provenance-gap/`

**Page purpose:** A reference page that defines provenance gap as an evidence posture condition — when an artifact's origin, creation context, or transmission chain cannot be confirmed, this is not an absence of truth but a confirmed gap in the evidence available for posture assessment.

**Relation to existing pages:** Extends Evidence Posture. Connects to source-confidence and not-assessable.

**Internal link strategy:**
- Link from: /reference/evidence-posture/, /reference/source-confidence/
- Link to: /reference/not-assessable/, /reference/evidence-chain/

**Source/claim posture:** Repository-supported governance claims only.

**Metadata requirements:** Title, meta description, canonical URL, H1.

**Validation:** validate_all.py PASS.

---

#### Page 3: /reference/not-assessable/

**Purpose:** Define the not-assessable evidence posture state and explain why it is a governed classification, not a failure.

**Route path:** `/reference/not-assessable/`

**Page purpose:** A reference page that defines the not-assessable posture state as a governed outcome — when evidence conditions are insufficient for classification, the correct output is not-assessable, not a guess. This page explains the governance rationale, the triggering conditions, and the boundary between not-assessable and other posture states.

**Relation to existing pages:** Extends Evidence Posture. Connects to provenance-gap and output-boundary.

**Internal link strategy:**
- Link from: /reference/evidence-posture/, /reference/provenance-gap/
- Link to: /reference/output-boundary/

**Source/claim posture:** Repository-supported governance claims only.

**Metadata requirements:** Title, meta description, canonical URL, H1.

**Validation:** validate_all.py PASS.

---

#### Page 4: /reference/output-boundary/

**Purpose:** Define the scope and limits of Hoax.ai evidence posture outputs.

**Route path:** `/reference/output-boundary/`

**Page purpose:** A reference page that defines the output boundary as a governed constraint — what Hoax.ai's evidence posture outputs may say and what they may not say. No final verdicts. No subject accusations. No certainty claims. The output boundary is a feature that protects both the asset and its users from misuse.

**Relation to existing pages:** Extends Evidence Posture and Artifact-Subject Separation. Connects to the Output Boundary Schema.

**Internal link strategy:**
- Link from: /reference/evidence-posture/, /reference/artifact-subject-separation/, /reference/not-assessable/
- Link to: /reference/classification-boundary/

**Source/claim posture:** Repository-supported governance claims. May reference Output Boundary Schema as a ledger-registered source.

**Metadata requirements:** Title, meta description, canonical URL, H1.

**Validation:** validate_all.py PASS.

---

### Batch 2 — Next Release (Sprint 54 or later)

#### Page 5: /reference/synthetic-fragility/

**Purpose:** Explain the structural characteristics that make synthetic media artifacts detectable through provenance and context.

**Route path:** `/reference/synthetic-fragility/`

---

#### Page 6: /reference/evidence-chain/

**Purpose:** Define how evidence posture reasoning connects artifact, context, source, and provenance into a chain.

**Route path:** `/reference/evidence-chain/`

---

#### Page 7: /reference/context-collapse/

**Purpose:** Define what happens to evidence posture when an artifact is separated from its original context.

**Route path:** `/reference/context-collapse/`

---

#### Page 8: /reference/claim-source-traceability/

**Purpose:** Explain why every material claim in a reference context must be traceable to a ledger-registered source.

**Route path:** `/reference/claim-source-traceability/`

---

#### Page 9: /reference/evidence-limitation/

**Purpose:** Define the bounded nature of evidence posture assessment and why limitations are structural features.

**Route path:** `/reference/evidence-limitation/`

---

#### Page 10: /reference/classification-boundary/

**Purpose:** Define what Hoax.ai classifies and what it does not classify.

**Route path:** `/reference/classification-boundary/`

---

## Internal Link Requirements

Every new reference page must:

- Be reachable from at least one existing public page
- Link to at least one other reference page where thematically relevant
- Not be orphaned (zero inbound links)

## Route and Sitemap Requirements

Every new reference page must:

1. Have a route registry entry before any public surface exposure
2. Be included in sitemap.xml only after route validation passes
3. Have canonical URL defined in metadata

## Page Quality Requirements

Every new reference page must satisfy:

- Content quality standard (CONTENT_QUALITY_REFERENCE_SUBSTANCE_STANDARD.md)
- Reference substance standard (at minimum 500 words of governed substance)
- No thin content, no placeholder content, no keyword stuffing
- One H1 exactly matching the route concept
- Title tag, meta description, canonical link
- No verdict language, no tool language, no upload/scoring implications
- No subject accusation language
- Artifact-subject separation preserved

## Prohibited Capabilities

No reference page may:

- Imply tool, classifier, upload, scoring, or API capability
- Issue truth verdicts about subjects, events, or institutions
- Promise detection capability
- Include forms, inputs, or interactive elements
- Include analytics or external scripts
- Be deployed without validate_all.py passing

## Release Order

| Order | Page | Sprint |
|-------|------|--------|
| 1 | /reference/source-confidence/ | Sprint 53 |
| 2 | /reference/provenance-gap/ | Sprint 53 |
| 3 | /reference/not-assessable/ | Sprint 53 |
| 4 | /reference/output-boundary/ | Sprint 53 |
| 5 | /reference/synthetic-fragility/ | Sprint 54+ |
| 6 | /reference/evidence-chain/ | Sprint 54+ |
| 7 | /reference/context-collapse/ | Sprint 54+ |
| 8 | /reference/claim-source-traceability/ | Sprint 54+ |
| 9 | /reference/evidence-limitation/ | Sprint 54+ |
| 10 | /reference/classification-boundary/ | Sprint 54+ |

---

*Sprint 52 — Governance Scaffolding Freeze and Public Reference Production Reset v1*
*Decision: DEC-070*
*Date: 2026-06-19*
