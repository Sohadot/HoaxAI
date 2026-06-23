# Public AI Retrieval Capsule Standard v1

## Retrieval Capsule Statement

The **Retrieval Capsule** is static HTML text that helps AI agents extract governed reference fields.

## Required Fields

Primary concept, page type, canonical answer, support type, related concepts, related utilities, boundary rule.

## Primary Concept Rules

Matches the page’s governed concept name.

## Page Type Rules

Homepage overview, public utility, or public reference concept/boundary.

## Canonical Answer Rules

Two to four sentences aligned with the Reference Answer block short answer.

## Support Type Rules

Matches Source Confidence support types where applicable.

## Related Concept Rules

Internal links to complementary reference routes.

## Boundary Rule

Single sentence negating verdict, detector, upload, and score behavior.

## Why This Is Not JSON-LD

Capsules are visible governed prose, not schema.org FAQ or structured verdict data.

## Why This Is Not an API

No endpoints, no JavaScript fetch, no dynamic generation.

## AI Retrieval Quality Checklist

- Retrieval Capsule heading present
- All seven fields present
- Canonical answer matches Reference Answer intent
- Boundary rule present
- No forbidden n-grams
- No JSON-LD
