# Hoax.ai Evidence Ledger Policy

## Purpose

The evidence ledger is Hoax.ai's internal claim registry.

It makes trust inspectable by recording what Hoax.ai claims, how each claim is categorized, what evidence posture supports it, and where support can be found.

The ledger does not certify truth.

It disciplines claims.

## Claim ID Format

Each ledger entry uses a sequential claim identifier:

```
CLAIM-0001
CLAIM-0002
CLAIM-0003
```

IDs are permanent. Retired claims retain their ID with `retired` evidence posture.

## Claim Categories

| Category | Definition |
|----------|------------|
| `conceptual_thesis` | Strategic framing, category positioning, or interpretive thesis statements |
| `operational_claim` | Statements about what Hoax.ai has built, deployed, or established |
| `governance_claim` | Statements about governance boundaries, policies, or decision records |
| `external_factual_claim` | Statements about external facts requiring source support |
| `future_capability_claim` | Statements about planned layers not yet built or deployed |

## Evidence Posture Values

| Posture | Meaning |
|---------|---------|
| `conceptual` | Interpretive or thesis-level framing; not a factual assertion about existence |
| `repository_supported` | Supported by traceable repository evidence |
| `source_supported` | Supported by cited external source per SOURCE_POLICY.md |
| `planned_not_claimed` | Future capability acknowledged as planned, not existing |
| `needs_review` | Claim requires re-examination before publication or reliance |
| `retired` | Claim withdrawn or superseded; not active |

## Required Fields

Every ledger entry must include:

| Field | Description |
|-------|-------------|
| `claim_id` | Sequential identifier (CLAIM-0001 format) |
| `claim_text` | The claim as stated |
| `claim_type` | One of the five claim categories |
| `evidence_posture` | One of the six evidence posture values |
| `support_location` | Repository path, decision ID, or source reference |
| `source_type` | Type of support: repository, decision_log, governance_file, public_surface, external_source, conceptual, none |
| `status` | `active`, `needs_review`, or `retired` |
| `last_reviewed` | Date of last review (ISO 8601: YYYY-MM-DD) |
| `notes` | Context, boundaries, or review comments |

## Ledger File

The canonical ledger file is:

```
data/evidence-ledger.json
```

The ledger begins small and grows only as claims are added with appropriate evidence posture.

## Prohibited Ledger Uses

The evidence ledger must not be used for:

- truth certification;
- legal verification;
- subject accusation;
- claiming future layers as existing;
- unsupported external factual claims.

The ledger records claim discipline. It does not issue verdicts.

## Review Discipline

- New claims require categorization and evidence posture before activation.
- Operational claims require `repository_supported` posture or `needs_review` status.
- External factual claims require `source_supported` posture or must not be added.
- Future capability claims require `planned_not_claimed` posture.
- Claims that violate GOVERNANCE_BOUNDARY.md or CLAIM_POLICY.md must not be added.

## Relationship to Self-Application

The evidence ledger is the operational instrument of the Self-Application Doctrine.

Hoax.ai subjects its own claims to the evidence discipline it applies to the category by recording, categorizing, and posturing every foundational claim before expansion.

## Governing Rule

**A site can claim trust. A governed asset must make trust inspectable.**
