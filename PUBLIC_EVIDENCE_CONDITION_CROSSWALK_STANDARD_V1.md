# Public Evidence Condition Crosswalk Standard v1

**Decision:** DEC-133
**Sprint:** Sprint 115
**Status:** Active standard for the evidence-condition crosswalk surface

## Evidence Condition Crosswalk Standard Statement

This standard governs the public evidence-condition crosswalk page at `/evidence-conditions/crosswalk/` and any future crosswalk surface. Crosswalk layers may relate evidence conditions across the public reference system, but must not rank, score, verify, detect, adjudicate, or operationalize them.

## Required page structure

Every crosswalk page must include, in reading order:

1. Reference summary
2. Crosswalk purpose
3. How to read this crosswalk
4. Evidence condition recap
5. Condition × core concept relation
6. Condition × evidence-risk pathway relation
7. Condition × route-group relation
8. Condition × audience-path relation
9. Condition × boundary-language relation
10. Condition × confusion-prevention relation
11. Condition × AI retrieval instruction
12. What this crosswalk supports
13. What this crosswalk does not claim
14. Reference Answer
15. Source Confidence
16. Cite This Reference
17. Retrieval Capsule
18. Strategic reference value
19. Page-end reference navigation
20. Boundary reminder
21. Non-transactional review boundary

## Minimum depth requirement

Each crosswalk page must contain at least 1,400 visible words of unique reference content.

## Required reference components

Each crosswalk page must include canonical URL, title element, meta description, Open Graph title and description, exactly one H1, and stable anchor IDs for every required section.

## Relation language requirements

Allowed relation labels only:

- directly relevant
- contextually relevant
- boundary-sensitive
- retrieval-supporting
- confusion-preventing
- adjacent reference

Forbidden relation labels include: high risk, medium risk, low risk, severity, score, rating, confidence score, verified, detected, confirmed, false, true, manipulated, fraudulent, deceptive, authentic, inauthentic. These terms may appear only inside explicit negation or prohibition language.

## Human use requirements

Crosswalk pages must explain how human readers choose companion reading for a named condition without converting relations into workflow steps or case outcomes.

## AI retrieval use requirements

Crosswalk pages must instruct AI agents to cite condition pages for definitions and the crosswalk for relations, preserving negations and avoiding invented orderings.

## Internal link requirements

Each crosswalk page must link to the homepage, `/system-map/`, `/evidence-conditions/`, all five condition pages, and at least two route-group or audience-path pages.

## Citation/retrieval requirements

Each crosswalk page must include Reference Answer, Source Confidence, Cite This Reference, and Retrieval Capsule blocks with stable anchors.

## Non-verdict requirements

No crosswalk relation may imply truth status, manipulation findings, severity, or outcome. Conditions remain interpretive-limit vocabulary.

## Non-transactional requirements

Crosswalk pages must include the non-transactional review boundary and must not contain pricing, transaction, acquisition, mandate, or representation language.

## Prohibitions

- Detector-output prohibition: no crosswalk may present relations as detector outputs.
- Ranking prohibition: no severity ordering, weighting, or risk matrix between conditions.
- Dashboard prohibition: no dashboard behavior or dashboard framing.
- Graph-tool prohibition: no interactive graph or graph-tool behavior.
- Scorecard prohibition: no score-card framing of relations.
- Rating-system prohibition: no rating-system framing of relations.
- Due-diligence-room prohibition: no private review-room framing.
- Pitch-deck prohibition: no pitch-deck framing.
- Sales-page prohibition: no sales-page behavior.
- Private data-room prohibition: no private data-room claims.
- Downloadable report prohibition: no downloadable-report claims.
- Consulting-offer prohibition: no consulting offers.
- Service-funnel prohibition: no service funnels.

## Forbidden regression patterns

- Converting relation labels into numeric or ordinal values
- Presenting the crosswalk as a verification workflow
- Adding JavaScript, forms, input fields, or upload behavior
- Introducing real-world case examples or accusations

## Thin-page prevention rules

Crosswalk pages must not be link farms. Every relation section must include prose explaining what the relation means and how to read it safely. Pages below the minimum depth requirement fail validation.
