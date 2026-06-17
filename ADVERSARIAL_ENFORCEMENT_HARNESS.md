# Hoax.ai Adversarial Enforcement Harness

**Version:** v1.0.0  
**Status:** governed_internal_enforcement  
**Maturity:** internal_only_not_public_tool  
**Decision:** DEC-022

## A. Purpose

This harness validates not only correct structure but the rejection of prohibited structures.

It proves that Hoax.ai rejects invalid claims, invalid routes, invalid outputs, forbidden public language, dependency drift, and ungoverned expansion — making governance structurally enforceable rather than merely documented.

**Do not merely describe governance. Make violations fail.**

**Unclassified ambiguity fails closed.**

## B. Non-Purpose

This harness does **not**:

- create a public tool;
- create a classifier;
- create scoring;
- create upload functionality;
- create public routes;
- create SEO expansion;
- create external deployment readiness;
- classify real evidence.

## C. Governing Principle

**Do not merely describe governance. Make violations fail.**

**Unclassified ambiguity fails closed.**

## D. Enforcement Domains

Enforcement applies across:

| Domain | Scope |
|--------|-------|
| Claims | Evidence ledger claim structure and posture alignment |
| Routes | Route registry required fields and canonical URLs |
| Sitemap | Sitemap URLs must match route registry |
| Internal links | Registry alignment (future expansion) |
| Taxonomy states | Posture states must exist in taxonomy |
| Standard rules | Standard rules must map to taxonomy states |
| Protocol rules | Protocol rules must map to taxonomy and standard |
| Output schema | Output fields, boundaries, and prohibited content |
| Internal engine model | No scoring, upload, or classifier fields |
| Source registry | Internal source files must exist |
| Public language | Context-aware forbidden term enforcement |
| Future capability claims | Planned capabilities must not read as live |
| Build manifest | Repository integrity metadata recorded |

## E. Required Failure Classes

The harness must reject:

- unregistered route in sitemap
- sitemap URL missing from route registry
- posture state not in taxonomy
- standard rule not mapped to taxonomy
- protocol rule not mapped to taxonomy or standard
- output field outside schema
- output missing subject boundary
- output containing fake/real verdict
- output containing numeric score
- output implying subject accusation
- public page implying active tool
- future capability described as live
- unsupported "first in the world" claim
- external factual claim without source support
- forbidden language outside allowed context

## F. Pass Meaning

**Passing means:** the repository enforces current governance boundaries.

**Passing does not mean:**

- Hoax.ai is ready for external deployment;
- a public classifier exists;
- an engine exists;
- evidence can be classified publicly;
- claims are externally verified beyond their registered posture.

## G. Maturity

| Field | Value |
|-------|-------|
| Version | v1.0.0 |
| Status | governed_internal_enforcement |
| Maturity | internal_only_not_public_tool |

## Machine-Readable Sources

- Forbidden language policy: `data/forbidden-language-policy.json`
- Adversarial cases: `data/adversarial-validation-cases.json`
- Adversarial validator: `validators/validate_adversarial_enforcement.py`
- Build manifest generator: `validators/generate_build_manifest.py`
- Build manifest: `BUILD_MANIFEST.json`

## Related Governance

- DEC-022
- `validators/validate_all.py` orchestrates factory foundation, adversarial enforcement, and manifest generation
