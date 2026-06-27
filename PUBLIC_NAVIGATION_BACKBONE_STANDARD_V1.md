# Public Navigation Backbone Standard v1

Sprint 110 — Public Reference Navigation Backbone Consolidation v1  
**Decision:** DEC-128

## Navigation Backbone Standard Statement

The public navigation backbone must remain a static, citation-safe route-group navigation layer across the 83-route public surface. Consolidation sprints inspect route counts, metadata, links, route-group connectivity, page-end navigation, AI retrieval navigation, boundaries, and prohibited drift without creating new routes or operational tools.

## Route-count requirements

- Sitemap must remain exactly 83 URLs unless an approved route sprint changes count.
- Route registry must remain exactly 83 entries.
- Public-file-registry must stay aligned if used.
- Visible public copy describing current release surface must not use stale 58/63/68/73/78 route counts.

## Homepage backbone requirements

The homepage must include a Navigation Backbone Snapshot with current public route count, navigation backbone role, major navigation layers, supported and unsupported uses, boundary statement, and non-transactional review boundary. The homepage must link visibly to `/system-map/` and `/strategic-review/`.

## System-map backbone requirements

`/system-map/` must include a Navigation Backbone section explaining how the map relates to the backbone, how route groups connect, why the map is structural and non-operational, human and AI use guidance, and why it is not a dashboard, graph tool, scorecard, rating system, report, pitch deck, sales page, or transaction surface. Required cross-links to homepage, system-map child routes, reviewer packet index, executive overview system page, strategic review depth, and external review reviewer map must be present.

## Cross-group navigation requirements

Major route groups must not remain isolated. Review layers, system map, utilities, concepts, pathways, strategic surfaces, and boundary references must remain reachable through grouped navigation — not exhaustive 83-link dumps on every page.

## Metadata requirements

Exactly one H1, canonical URL, title, meta description, Open Graph title, and Open Graph description on every public HTML page.

## Link requirements

No broken internal links among public HTML routes.

## Role clarity requirements

Navigation backbone must state it supports route-group understanding and structural review — not dashboards, graph tools, scorecards, rating systems, due-diligence rooms, pitch decks, sales pages, private data rooms, downloadable reports, or transaction surfaces.

## Non-verdict requirements

No verdict, detector, upload, or automated report capability claims.

## Non-transactional requirements

No pricing, transaction, acquisition term, representative mandate, legal, or financial representation claims.

## Dashboard prohibition

No dashboard behavior or dashboard framing as capability.

## Graph-tool prohibition

No graph-tool behavior or interactive graph framing as capability.

## Scorecard prohibition

No scorecard behavior.

## Rating-system prohibition

No rating-system behavior.

## Due-diligence-room prohibition

No due-diligence-room or private diligence-room access claims.

## Pitch-deck and sales-page prohibition

No pitch-deck or sales-page behavior.

## Private data-room and downloadable-report prohibition

No private data-room access or downloadable report behavior.

## Forbidden public HTML copy

Positive or promotional use of detector, verdict, upload, scoring, pricing, transaction, private data-room, downloadable report, pitch-deck, sales-page, scorecard, rating-system, dashboard, or graph-tool claims is prohibited. Safe negative boundary language is allowed.

## Validator protection

`validators/validate_public_reference_navigation_backbone_consolidation_v1.py` enforces this standard after visible production changes exist.
