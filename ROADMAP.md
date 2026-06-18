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

**Status:** COMPLETE — 2026-06-17  
**Goal:** Govern how Hoax.ai's interface may visually express evidence posture without implying detection authority, scoring, upload, or active classifier capability.

### Deliverables

- INTERFACE_EMBODIMENT_GOVERNANCE.md
- data/interface-grammar.json
- data/interface-component-registry.json
- data/interface-surface-map.json
- validators/validate_interface_governance.py
- SPRINT_8_INTERFACE_EMBODIMENT_GOVERNANCE_AUDIT.md
- DEC-023 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Interface Governance Scope

- 10 registered interface components (IFC-0001 through IFC-0010)
- Root thesis surface mapped to ROUTE-0001
- Prohibited visual metaphors and interface promises defined
- No engine, classifier, score, upload workflow, public route, or tool created

### Gate

External deployment remains deferred (Sprint 1C). Interface governance is not_public_tool.

---

## Sprint 9 — Security and Privacy Boundary v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define and enforce the zero-data, static-first, no-interaction security posture before any future tool, form, upload, analytics, API, or external dependency exists.

### Deliverables

- SECURITY_PRIVACY_BOUNDARY.md
- data/security-privacy-boundary.json
- data/interaction-permission-registry.json
- data/external-dependency-registry.json
- validators/validate_security_privacy_boundary.py
- SPRINT_9_SECURITY_PRIVACY_BOUNDARY_AUDIT.md
- DEC-024 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Security/Privacy Scope

- 10 interaction permissions (PERMISSION-0001 allowed; PERMISSION-0002–0010 blocked)
- Zero-data static foundation maturity
- External dependency registry (first-party local only)
- No form, upload, analytics, cookie, API, or public tool created

### Gate

External deployment remains deferred (Sprint 1C). Security boundary is zero_data_static_foundation.

---

## Sprint 10 — Link and Route Integrity Hardening v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Enforce route, sitemap, canonical, and internal link discipline before reference expansion or SEO work.

### Deliverables

- LINK_ROUTE_INTEGRITY_POLICY.md
- data/link-route-integrity-policy.json
- data/internal-link-graph.json
- validators/validate_link_route_integrity.py
- SPRINT_10_LINK_ROUTE_INTEGRITY_AUDIT.md
- DEC-025 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Route/Link Scope

- Single public route ROUTE-0001 (/) with sitemap and canonical alignment
- Internal link graph mapped to index.html
- No new routes, SEO expansion, or deployment created

### Gate

External deployment remains deferred (Sprint 1C). Route integrity is pre_expansion_hardening.

---

## Sprint 11 — Claim and Source Traceability Hardening v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Enforce strict traceability between claims, sources, support locations, public statements, and internal governance evidence.

### Deliverables

- CLAIM_SOURCE_TRACEABILITY_POLICY.md
- data/claim-source-traceability-policy.json
- data/claim-source-map.json
- data/public-claim-map.json
- validators/validate_claim_source_traceability.py
- SPRINT_11_CLAIM_SOURCE_TRACEABILITY_AUDIT.md
- DEC-026 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Traceability Scope

- 15 evidence ledger claims mapped (CLAIM-0001 through CLAIM-0015)
- 6 homepage public claims mapped (PUB-CLAIM-0001 through PUB-CLAIM-0006)
- No external factual claims introduced
- No new routes or SEO expansion

### Gate

External deployment remains deferred (Sprint 1C). Traceability is pre_reference_expansion_hardening.

---

## Sprint 12 — Technical Quality Gate Hardening v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Enforce static public-surface technical quality across HTML, metadata, robots, sitemap, accessibility, dependencies, performance posture, and static security before reference expansion.

### Deliverables

- TECHNICAL_QUALITY_GATE.md
- data/technical-quality-gate.json
- data/public-file-registry.json
- data/html-metadata-registry.json
- validators/validate_technical_quality_gate.py
- SPRINT_12_TECHNICAL_QUALITY_GATE_AUDIT.md
- DEC-027 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Technical Quality Scope

- 4 public files registered (index.html, styles.css, robots.txt, sitemap.xml)
- HTML metadata registry for ROUTE-0001
- 16 evidence ledger claims (CLAIM-0016 added)
- No public pages added
- No public routes added
- No SEO expansion

### Gate

External deployment remains deferred (Sprint 1C). Technical quality is pre_expansion_static_quality_gate.

### Next Phase

**Sprint 13 — Reference Page Blueprint and Expansion Gate v1**

Public classifier remains blocked. External deployment remains blocked.

---

## Sprint 13 — Reference Page Blueprint and Expansion Gate v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define the governed blueprint and expansion gate for reference pages before any reference layer publication, SEO growth, or route addition.

### Deliverables

- REFERENCE_PAGE_BLUEPRINT.md
- data/reference-page-blueprint.json
- data/reference-page-type-registry.json
- data/reference-expansion-gate.json
- data/reference-page-candidate-registry.json
- validators/validate_reference_page_blueprint.py
- SPRINT_13_REFERENCE_PAGE_BLUEPRINT_AUDIT.md
- DEC-029 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Blueprint Scope

- 8 future page types registered (REF-TYPE-0001 through REF-TYPE-0008)
- Empty candidate registry (no candidates added)
- 17 evidence ledger claims (CLAIM-0017 added)
- No public pages added
- No public routes added
- No sitemap expansion

### Gate

External deployment remains deferred (Sprint 1C). Blueprint is pre_reference_expansion_gate.

### Next Phase

**Sprint 14 — Content Quality and Reference Substance Standard v1**

Public classifier remains blocked. External deployment remains blocked. DNS, Cloudflare, and custom domain work remain in later deployment gates (DEPLOY-G1 through DEPLOY-G3).

---

## Sprint 13A — Automation Governance and CI Quality Gate v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Enforce automated validation, CI quality gates, agent execution rules, and repository workflow boundaries before reference content expansion.

### Deliverables

- AUTOMATION_GOVERNANCE.md
- AGENT_EXECUTION_RULES.md
- data/automation-governance-policy.json
- data/ci-quality-gate-policy.json
- validators/validate_automation_governance.py
- .github/workflows/quality-gate.yml
- .github/pull_request_template.md
- .github/ISSUE_TEMPLATE/config.yml
- .github/ISSUE_TEMPLATE/governance-task.yml
- .github/BRANCH_PROTECTION_RECOMMENDATION.md
- .cursor/rules/hoax-governance.mdc
- SPRINT_13A_AUTOMATION_GOVERNANCE_AUDIT.md
- DEC-030 appended to DECISION_LOG.md
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Automation Scope

- Validation-only CI workflow (contents: read, no secrets, no deployment)
- 18 evidence ledger claims (CLAIM-0018 added)
- No public pages, routes, or sitemap expansion
- DEPLOY-G1 through DEPLOY-G3 remain not passed

### Gate

External deployment remains deferred (Sprint 1C). Automation maturity is validation_only_no_deployment.

### Next Phase

**Sprint 14 — Content Quality and Reference Substance Standard v1**

Public classifier remains blocked. External deployment remains blocked.

---

## Sprint 13B — Governed Publisher Control Plane v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define publisher control infrastructure so future automation may produce governed reference candidates only — without publishing, drafting, routing, or sitemap expansion.

### Deliverables

- GOVERNED_PUBLISHER_CONTROL_PLANE.md
- data/publisher-governance-policy.json
- data/publisher-workflow-registry.json
- data/publisher-state-machine.json
- data/publisher-quality-gates.json
- data/publisher-queue-registry.json
- validators/validate_publisher_control_plane.py
- .github/ISSUE_TEMPLATE/publisher-candidate.yml
- .cursor/rules/hoax-publisher.mdc
- SPRINT_13B_GOVERNED_PUBLISHER_CONTROL_AUDIT.md
- DEC-031 appended to DECISION_LOG.md
- data/reference-expansion-gate.json updated
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Publisher Scope

- 15 publisher workflows registered (PUB-WORKFLOW-0001–0015), all blocked
- 14 publisher quality gates (PUB-GATE-0001–0014)
- Empty publisher queues and empty candidate registry
- 19 evidence ledger claims (CLAIM-0019 added)
- Publisher blocked until content quality standard (Sprint 14)
- No content drafts, public pages, routes, or sitemap expansion

### Gate

External deployment remains deferred (Sprint 1C). Publisher maturity is publisher_blocked_until_quality_standard.

### Next Phase

**Sprint 14 — Content Quality and Reference Substance Standard v1**

Public classifier remains blocked. External deployment remains blocked.

---

## Sprint 14 — Content Quality and Reference Substance Standard v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define minimum governed substance requirements for future reference pages before public, route, or sitemap eligibility.

### Deliverables

- CONTENT_QUALITY_REFERENCE_SUBSTANCE_STANDARD.md
- data/content-quality-standard.json
- data/reference-substance-rules.json
- data/thin-content-failure-patterns.json
- data/reference-section-requirements.json
- validators/validate_content_quality_standard.py
- SPRINT_14_CONTENT_QUALITY_REFERENCE_SUBSTANCE_AUDIT.md
- DEC-032 appended to DECISION_LOG.md
- data/reference-expansion-gate.json updated
- data/publisher-quality-gates.json updated
- data/publisher-governance-policy.json updated (blocked_until_publisher_dry_run_harness)
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Substance Scope

- 16 substance rules (SUBSTANCE-RULE-0001–0016)
- 14 thin-content failure patterns (THIN-PATTERN-0001–0014)
- 16 section requirements (9 required, 7 conditional)
- 20 evidence ledger claims (CLAIM-0020 added)
- Publisher PUB-GATE-0003 standard defined; publisher blocked until dry-run harness
- No public pages, draft pages, routes, or sitemap expansion

### Gate

External deployment remains deferred (Sprint 1C). Maturity is pre_reference_publication_standard.

### Next Phase

**Sprint 16 — Publisher Dry-Run Harness v1**

Public classifier remains blocked. External deployment remains blocked. Publisher remains blocked until future dry-run harness.

---

## Sprint 15 — Structured Data and Semantic SEO Governance v1

**Status:** COMPLETE — 2026-06-17  
**Goal:** Define how Hoax.ai may use metadata, structured data, titles, descriptions, canonical signals, and future page SEO without implying active tool capability, detector status, or unsupported authority.

### Deliverables

- STRUCTURED_DATA_SEMANTIC_SEO_GOVERNANCE.md
- data/semantic-seo-governance.json
- data/structured-data-policy.json
- data/schema-type-registry.json
- data/metadata-pattern-registry.json
- data/seo-prohibited-patterns.json
- validators/validate_structured_data_semantic_seo.py
- SPRINT_15_STRUCTURED_DATA_SEMANTIC_SEO_AUDIT.md
- DEC-033 appended to DECISION_LOG.md
- data/reference-expansion-gate.json updated
- data/publisher-quality-gates.json updated (PUB-GATE-0015)
- validators/validate_all.py updated

### Validation

`python validators/validate_all.py` — PASS required for sprint closure.

### Semantic SEO Scope

- 15 schema types registered (SCHEMA-TYPE-0001–0015)
- 12 metadata patterns registered
- 14 SEO prohibited patterns (SEO-PATTERN-0001–0014)
- 21 evidence ledger claims (CLAIM-0021 added)
- Publisher PUB-GATE-0015 standard defined; publisher blocked until dry-run harness
- No public pages, draft pages, routes, sitemap expansion, or JSON-LD overclaiming

### Gate

External deployment remains deferred (Sprint 1C). Maturity is pre_reference_publication_seo_governance.

### Next Phase

**Sprint 16 — Publisher Dry-Run Harness v1**

Public classifier remains blocked. External deployment remains blocked. Publisher remains blocked until future dry-run harness.

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
