# Live Public Surface Parity Audit v1

**Sprint:** Sprint 136  
**Status:** Audit-only live parity audit  
**Live target:** `https://hoax.ai/`

## Audit Purpose

Sprint 136 audits parity between the validated Sprint 135 repository release candidate and the deployed Hoax.ai live public surface. It checks whether humans, crawlers, and AI agents see the same 104-route governed public reference system that the repository validates.

Governing sentence: Live surface parity means Hoax.ai’s deployed public site matches the validated 104-route release candidate in repository structure, sitemap, metadata, navigation, boundaries, and public interpretation without stale deployment, route drift, launch drift, marketing drift, commercial drift, detector drift, proof drift, verdict drift, or governance inflation.

## Live Fetch Summary

- Live base URL checked: `https://hoax.ai/`
- Live fetch completed: yes
- Live access issue found: no
- Live sitemap URL count observed: 104
- Repository sitemap URL count observed: 104
- Core sampled live routes returned HTTP 200
- Sprint 135 release-candidate anchor visible live: no

## Audit Outcome

The deployed live surface is reachable, indexable, and sitemap-aligned with the repository 104-route surface. The live sitemap matches repository count and route set, robots references the live sitemap, and core route samples respond successfully.

However, the Sprint 135 release-candidate language is not yet visible on the live homepage/system map. Sprint 136 records this as a live deployment freshness issue, not a repository validation defect. No repository route, registry, sitemap, or metadata repair was required.

## Walkthrough Summary

| Metric | Result |
| --- | --- |
| Live parity records | 60 |
| Safe records | 59 |
| Unsafe records | 1 |
| Scenarios | 60 |
| Passed | 55 |
| Failed | 5 |
| Live sitemap URLs | 104 |
| New DEC created | No |

## Failed Scenarios

The failed scenarios are deployment-freshness scenarios tied to Sprint 135 not being live-visible yet:

- Release-candidate language remains discoverable.
- Live public surface does not show stale deployment from before Sprint 135 on homepage.
- Live public surface does not show stale deployment from before Sprint 135 on system map.
- Live public surface does not show stale deployment from before Sprint 135 on Sprint 135-patched pages.
- The deployed Hoax.ai surface matches the validated repository release candidate sufficiently to treat Sprint 135 as live-visible.

## Repairs Applied

No repository repairs were applied. The observed issue is live deployment freshness, not a repository defect.

## Decision Outcome

No new DEC was required. The sprint records a concrete live parity observation without adding governance for future deployment or monitoring.

## Boundary Confirmation

Sprint 136 did not introduce any new route, live status page, deployment page, release page, launch page, announcement page, press page, marketing page, SEO expansion route, discovery route, crawler guide route, AI discovery route, start-here page, onboarding page, guide page, navigation page, workflow page, user-journey page, orientation page, tool, API, dashboard, form, upload, generated-answer system, consulting page, service page, lead-generation page, monetization page, pricing page, subscription page, support/sponsorship/donation page, paid report, private access page, sales page, buyer page, acquisition page, offer page, transaction page, pitch deck, due-diligence room, downloadable report, contact-to-buy surface, contact-for-service surface, legal representation, financial representation, investment claim, authority claim, proof claim, verification claim, detector behavior, score claim, verdict support, or case conclusion.
