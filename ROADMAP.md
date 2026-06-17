# Hoax.ai Roadmap

## Operating Goal

Turn Hoax.ai from a premium AI-era domain into a governed category asset.

The asset should not become a generic website, AI detector, or fact-checking blog.

It should become evidence-risk reference infrastructure for the synthetic media age.

---

## Sprint 0 — Foundation Governance

**Status:** COMPLETE — 2026-06-17  
**Goal:** Establish Hoax.ai as a governed asset before public interface, tools, or SEO expansion.

### Deliverables

- README.md
- CATEGORY_THESIS.md
- GOVERNANCE_BOUNDARY.md
- CLAIM_POLICY.md
- SOURCE_POLICY.md
- INTERFACE_THESIS.md
- BUYER_LOGIC.md
- MONETIZATION_BOUNDARY.md
- DECISION_LOG.md
- ROADMAP.md

### Prohibited

- No public pages yet.
- No tool yet.
- No SEO expansion yet.
- No unsupported claims.
- No fake/real verdict language.

---

## Sprint 0A — Governance Foundation Audit

**Status:** COMPLETE — 2026-06-17  
**Goal:** Verify consistency, alignment, and governance boundary enforcement across all Sprint 0 files.

### Deliverables

- SPRINT_0A_AUDIT.md

---

## Sprint 0B — Naming Convention Normalization

**Status:** COMPLETE — 2026-06-17  
**Goal:** Normalize all governance filenames to UPPERCASE_WITH_UNDERSCORES.md.

### Deliverables

- SPRINT_0B_NAMING_AUDIT.md

---

## Sprint 1 — Public Thesis Surface

**Status:** COMPLETE — 2026-06-17  
**Goal:** Create the first visible GitHub public surface.

### Deliverables

- index.html
- styles.css
- robots.txt
- sitemap.xml

### Homepage Communicated

- Hoax.ai is not a truth machine.
- Hoax.ai classifies evidence posture.
- The AI era creates synthetic fragility.
- Trust begins with evidence structure.
- A taxonomy, standard, reference layer, and bounded classifier are under development.

---

## Sprint 1A — Artifact–Subject Separation

**Status:** COMPLETE — 2026-06-17  
**Goal:** Separate classification of evidence artifacts from connected subjects across governance and public surface.

### Deliverables

- DEC-012 appended to DECISION_LOG.md
- Artifact–Subject Separation Doctrine in GOVERNANCE_BOUNDARY.md
- CLAIM_POLICY.md and index.html updated
- SPRINT_1A_ARTIFACT_SUBJECT_SEPARATION_AUDIT.md

---

## Sprint 1B — Sovereign Integrity and Self-Application Foundation

**Status:** COMPLETE — 2026-06-17  
**Goal:** Establish the sovereign integrity architecture that makes Hoax.ai a governed Category Intelligence Factory.

### Deliverables

- SELF_APPLICATION.md
- EVIDENCE_LEDGER_POLICY.md
- data/evidence-ledger.json
- SOVEREIGN_REFERENCE_INTEGRITY_STANDARD.md
- CATEGORY_INTELLIGENCE_FACTORY_PLAN.md
- MASTER_EXECUTION_PLAN.md
- SPRINT_1B_SOVEREIGN_INTEGRITY_AUDIT.md
- DEC-013, DEC-014, DEC-015 appended to DECISION_LOG.md
- README.md and ROADMAP.md updated

### Gate

Ontology, standard, protocol, classifier, and reference pages **cannot proceed** until Sprint 1B passes validation.

---

## Sprint 1C — Public Deployment and Surface Validation

**Status:** BLOCKED — 2026-06-17  
**Goal:** Validate the GitHub Pages public surface and repository readiness before ontology, standard, protocol, classifier, or reference expansion.

### Deliverables

- SPRINT_1C_PUBLIC_DEPLOYMENT_AUDIT.md
- Public surface file validation (index.html, styles.css, robots.txt, sitemap.xml)
- Repository integrity validation
- DEC-016 (deferred until GitHub Pages deployment confirmed)

### Blocker

GitHub Pages is not enabled (`has_pages: false`). Public surface returns HTTP 404 at `https://sohadot.github.io/Hoax/`.

### Remediation

Enable GitHub Pages: branch `main`, folder `/` (root). Re-validate load, then close sprint and append DEC-016.

### Gate

Ontology, standard, protocol, classifier, and reference pages **cannot proceed** until Sprint 1C passes validation.

External deployment remains deferred. Repository validation may pass while external exposure remains blocked.

---

## Sprint 1D — Category Factory Enforcement Layer v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Convert governance from strategic documentation into enforceable repository structure.

### Deliverables

- data/route-registry.json
- data/category-language.json
- data/ontology-foundation.json
- data/source-registry.json
- validators/validate_factory_foundation.py
- validators/validate_all.py
- SPRINT_1D_FACTORY_ENFORCEMENT_AUDIT.md
- DEC-016 appended to DECISION_LOG.md

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Gate

Sprint 2 (ontology) **cannot proceed** until:

- route registry exists
- category language registry exists
- ontology foundation exists
- source registry exists
- validate_all.py passes

External deployment remains deferred until deployment readiness gate (Sprint 1C).

---

## Sprint 2 — Evidence Posture Taxonomy v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define the first governed Evidence Posture Taxonomy for evidence artifacts and evidence chains.

### Deliverables

- EVIDENCE_POSTURE_TAXONOMY.md
- data/evidence-posture-taxonomy.json
- SPRINT_2_EVIDENCE_POSTURE_TAXONOMY_AUDIT.md
- DEC-017 appended to DECISION_LOG.md
- Validator extended for taxonomy checks

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Taxonomy Scope

- 9 posture dimensions (DIM-0001 through DIM-0009)
- 8 posture states (STATE-0001 through STATE-0008)
- No classifier, score, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Taxonomy is internal/governed until public route governance permits publication.

---

## Sprint 3 — Evidence Posture Standard v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define the first evidence posture standard mapping taxonomy states to bounded sufficiency rules.

### Deliverables

- EVIDENCE_POSTURE_STANDARD.md
- data/evidence-posture-standard.json
- SPRINT_3_EVIDENCE_POSTURE_STANDARD_AUDIT.md
- DEC-018 appended to DECISION_LOG.md
- Validator extended for standard checks

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Standard Scope

- 9 standard dimensions (STD-DIM-0001 through STD-DIM-0009) mapped to taxonomy
- 8 sufficiency rules (STD-RULE-0001 through STD-RULE-0008) mapped to taxonomy states
- No protocol, classifier, score, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Standard is internal/governed until public route governance permits publication.

---

## Sprint 4 — Evidence Posture Classification Protocol v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define the governed sequence for assigning evidence posture states to artifacts and evidence chains.

### Deliverables

- EVIDENCE_POSTURE_CLASSIFICATION_PROTOCOL.md
- data/evidence-posture-protocol.json
- SPRINT_4_EVIDENCE_POSTURE_PROTOCOL_AUDIT.md
- DEC-019 appended to DECISION_LOG.md
- Validator extended for protocol checks

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Protocol Scope

- 12 protocol stages (PROTO-STAGE-0001 through PROTO-STAGE-0012)
- 8 state selection rules (PROTO-RULE-0001 through PROTO-RULE-0008)
- Maps to taxonomy and standard
- No classifier, engine, score, upload workflow, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Protocol is internal/governed with maturity not_public_tool.

---

## Sprint 5 — Output Boundary Schema v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define the governed output contract for protocol-compliant evidence posture statements.

### Deliverables

- OUTPUT_BOUNDARY_SCHEMA.md
- data/output-boundary-schema.json
- SPRINT_5_OUTPUT_BOUNDARY_SCHEMA_AUDIT.md
- DEC-020 appended to DECISION_LOG.md
- Protocol updated with output schema dependency
- Validator extended for schema checks

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Schema Scope

- 20 required output fields (OUT-FIELD-0001 through OUT-FIELD-0020)
- 8 allowed posture states mapped to taxonomy
- Prohibited output fields and language defined
- No engine, classifier, score, upload workflow, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Schema is internal/governed with maturity not_public_tool.

---

## Sprint 6 — Internal Engine Model v0

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define the permitted internal logic architecture for a future evidence-posture engine without creating a public tool or upload workflow.

### Deliverables

- INTERNAL_ENGINE_MODEL.md
- data/internal-engine-model.json
- data/internal-engine-fixtures.json
- SPRINT_6_INTERNAL_ENGINE_MODEL_AUDIT.md
- DEC-021 appended to DECISION_LOG.md
- Validator extended for engine model and fixtures

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Engine Model Scope

- 9 allowed input fields (ENG-IN-0001 through ENG-IN-0009)
- 10 processing layers (ENG-LAYER-0001 through ENG-LAYER-0010)
- Maps to taxonomy, standard, protocol, and output boundary schema
- Output status limited to draft_internal and governed_internal
- No engine, classifier, score, upload workflow, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Engine model is internal/governed with maturity not_public_tool.

---

## Sprint 7 — Adversarial Enforcement Harness v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Create an adversarial enforcement layer that proves Hoax.ai rejects invalid claims, routes, outputs, forbidden language, dependency drift, and ungoverned expansion.

### Deliverables

- ADVERSARIAL_ENFORCEMENT_HARNESS.md
- data/forbidden-language-policy.json
- data/adversarial-validation-cases.json
- validators/validate_adversarial_enforcement.py
- validators/generate_build_manifest.py
- BUILD_MANIFEST.json
- SPRINT_7_ADVERSARIAL_ENFORCEMENT_AUDIT.md
- DEC-022 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Enforcement Scope

- 20 adversarial validation cases (ADV-CASE-0001 through ADV-CASE-0020)
- Context-aware forbidden language policy
- Build manifest with SHA-256 file hashes
- No engine, classifier, score, upload workflow, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Enforcement harness is internal_only_not_public_tool.

---

## Sprint 8 — Interface Embodiment Governance v1

**Status:** READY — G7 passed  
**Goal:** Govern interface embodiment alignment with evidence-structure thesis without creating a public classifier or tool.

### Deliverables

- interface embodiment governance (future — not in current scope)
- visual system alignment checks
- no public classifier page
- no upload workflow

### Required Principle

Interface governance must follow interface thesis and governance boundary. Public classifier remains blocked.

---

## Sprint 8 — Reference Layer v1

**Status:** BLOCKED — requires reference governance gates  
**Goal:** Add a small number of strong reference pages.

### Candidate Pages

- /evidence-posture/
- /synthetic-fragility/
- /source-confidence/
- /provenance-gap/
- /synthetic-media-risk/
- /deception-patterns/
- /methodology/
- /standard/

### Rule

No thin pages.

Every page must be reference-grade, internally linked, source-disciplined, and aligned with the governance boundary.

---

## Sprint 6 — Source Registry

**Goal:** Establish source discipline and claim traceability.

### Deliverables

- SOURCE_REGISTRY.md or data/source-registry.json
- source categories
- claim mapping
- review status
- citation policy

---

## Sprint 7 — Interface Embodiment

**Goal:** Develop the visual system that embodies evidence posture.

### Interface Direction

The interface should show evidence layers:

- claim;
- source;
- provenance;
- media;
- context;
- identity;
- pattern;
- posture.

### Prohibited

- fake scanning effects;
- cyber-gaming visuals;
- fake certainty meters;
- sensational red alerts;
- decorative animations without conceptual function.

---

## Sprint 8 — GitHub Public Completion

**Goal:** Make the GitHub version complete and visible before custom domain connection.

### Requirements

- homepage live;
- governance files present;
- sitemap present;
- robots present;
- internal links working;
- no broken links;
- no thin pages;
- no false claims;
- mobile-stable;
- accessible;
- performance-safe.

---

## Sprint 9 — DNS and Cloudflare Layer

**Goal:** Connect Hoax.ai after the GitHub public foundation is ready.

### Infrastructure Rule

GitHub is the first public build layer.

Cloudflare nameservers are added later as DNS, performance, and security infrastructure.

### DNS Direction

The domain owner retains ownership.

After the GitHub build is complete and visible, Cloudflare nameservers can be provided for domain-level DNS management.

GitHub Pages connection may use the appropriate A and CNAME records through the active DNS provider.

Do not request DNS changes before the public foundation is ready.

---

## Long-Term Roadmap

Future layers may include:

- Evidence Risk Briefs;
- Brand Impersonation Risk Intake;
- Synthetic Media Trust Reports;
- Evidence Posture API;
- Reference Licensing;
- Enterprise Workflows;
- Strategic Acquisition Positioning.

---

## Governing Roadmap Sentence

**Build category infrastructure before building scale.**
