# Hoax.ai

**Truth is no longer the first layer. Evidence is.**

Hoax.ai helps people read evidence risk in the synthetic media age — without issuing verdicts, scores, uploads, or fake/real labels.

**Live site:** [https://hoax.ai/](https://hoax.ai/)

## What Hoax.ai Is

A governed public evidence-risk reference system with manual utilities and category definitions. Hoax.ai classifies evidence posture, synthetic risk signals, source confidence, contextual gaps, and provenance weaknesses — it does not issue careless truth verdicts or accuse individuals or institutions.

The core question is not *Is this true?* but *What is the condition of the evidence?*

## Public Utilities

Manual, non-verdict reference tools:

- [Manual Evidence Checklist](https://hoax.ai/manual-evidence-checklist/)
- [Evidence Posture Map](https://hoax.ai/evidence-posture-map/)
- [Synthetic Examples](https://hoax.ai/synthetic-examples/)
- [Evidence-Risk Questions](https://hoax.ai/evidence-risk-questions/)

## Core Reference Routes

- [Evidence Risk](https://hoax.ai/evidence-risk/)
- [Provenance Risk](https://hoax.ai/provenance-risk/)
- [Context Collapse](https://hoax.ai/context-collapse/)
- [Claim Drift](https://hoax.ai/claim-drift/)
- [Traceability Gap](https://hoax.ai/traceability-gap/)
- [Why Hoax.ai Is Not a Detector](https://hoax.ai/why-hoax-ai-is-not-a-detector/)

## Standard and Protocol

- [Evidence Posture Standard v1](https://hoax.ai/standard/evidence-posture/)
- [Evidence Posture Classification Protocol v1](https://hoax.ai/protocol/evidence-posture/)
- [Evidence Field interface](https://hoax.ai/interface/evidence-field/)

## Sovereign Integrity

Hoax.ai does not ask for trust by assertion. It makes trust inspectable.

- [Self-Application Doctrine](SELF_APPLICATION.md)
- [Evidence Ledger](data/evidence-ledger.json) per [EVIDENCE_LEDGER_POLICY.md](EVIDENCE_LEDGER_POLICY.md)
- [Sovereign Reference Integrity Standard](SOVEREIGN_REFERENCE_INTEGRITY_STANDARD.md)
- Machine-readable registries validated by `validators/validate_all.py`

## Current Status

| Item | Status |
|------|--------|
| Public domain | **Live** at [hoax.ai](https://hoax.ai/) |
| Indexable public routes | **63** (rebalanced Sprint 138, DEC-139) |
| Hosting | GitHub Pages + custom domain |
| Repository | [github.com/Sohadot/HoaxAI](https://github.com/Sohadot/HoaxAI) |

Sprint history: [CHANGELOG.md](CHANGELOG.md). Decisions: [DECISION_LOG.md](DECISION_LOG.md).

## Boundaries

Hoax.ai is **not** a truth machine, political fact-checking site, automated authenticity detector, upload tool, scoring system, or public report generator.

**Classify the evidence. Do not perform the verdict.**

## Public Reference Graph

The public surface connects utilities, concept references, pathways, evidence conditions, standard, and protocol through governed internal linking. Each page includes **Source Confidence**, **Reference Answer**, **Cite This Reference**, and **Retrieval Capsule** blocks for citation-safe use by humans and AI agents — without JSON-LD APIs, generators, or verdict behavior.

For quiet orientation to the reference asset (not acquisition language), see [About This Reference](https://hoax.ai/about-this-reference/).

## Repository

```bash
py -3 validators/validate_all.py
```

Governance, sprint history, and archived pre-rebalance pages live in the repository. The indexable public surface teaches evidence and category substance first.
