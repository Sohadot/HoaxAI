# Public Reference Citation and Retrieval Hardening v1

## Citation and Retrieval Hardening Statement

Sprint 90 hardens Hoax.ai’s existing twenty-nine-URL public surface with **Cite This Reference** blocks, **Retrieval Capsule** blocks, stable anchor IDs, and reference summary lines. No new routes. No chatbot, generator, API, or verdict behavior.

**Decision:** DEC-108 | **Sprint:** 90 | **Gate:** G90

## Why Citation Safety Matters

Humans quote reference pages. Without citation guidance, definitional language can be misread as artifact assessment or truth certification.

## Why AI Retrieval Needs Stable Capsules

AI agents select pages by concept, answer, and boundary signals. Retrieval capsules provide static, labeled fields without JSON-LD or APIs.

## What Was Hardened

- Cite This Reference blocks on eleven pages
- Retrieval Capsule blocks on eleven pages
- Stable anchor IDs for deep linking
- Reference summary lines on ten utility/reference pages

## Pages Updated

Homepage plus ten public utility/reference routes.

## Cite This Reference Component

Page title, canonical URL, reference role, best used for, not suitable for, boundary reminder.

## Retrieval Capsule Component

Primary concept, page type, canonical answer, support type, related concepts, related utilities, boundary rule.

## Stable Anchor Strategy

Homepage: hero, public-utilities, reference-layer, reference-graph, source-confidence, reference-answer, cite-this-reference, retrieval-capsule, boundary.

Utility/reference pages: reference-answer, source-confidence, reference-path, cite-this-reference, retrieval-capsule, boundary, plus related-concepts or continue-with.

## Reference Summary Line Standard

One sentence after the page title summarizing the page without verdict, detection, upload, or score language.

## What This Does Not Authorize

Upload, scoring, verdict, detector claims, public API, automated reports, JavaScript, forms, chatbots, generators, or real-world case evaluation.

## Why This Is Not a Chatbot

No conversational interface or dynamic responses.

## Why This Is Not a Detector

Citation blocks explicitly negate artifact assessment and automated authenticity outputs.

## Future Citation/Retrieval Candidates

- Cross-page citation consistency audits (Sprint 91)
- Retrieval snippet alignment with capsules
