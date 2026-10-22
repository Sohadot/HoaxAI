# Hoax.ai public survey — operational release checklist

This is the **public** survey mechanism only. Private investment analysis, valuation, raw response data and any internal Sohadot experiment files must never be committed here.

## Current readiness

- Static page: /survey/ (staged; do not add to navigation or sitemap until operational).
- API: Cloudflare Worker route /survey/api/* (same domain).
- Private response store: Cloudflare D1 (not a public JSON, GitHub Issue or commit).
- Abuse protection: Turnstile server-side Siteverify, origin validation, bounded inputs; **configure Cloudflare rate limits before launch**.
- The UI **fails closed** when the API, D1, or Turnstile is not configured. It does not claim a response was received unless the server returns success.
- No personal contact fields, uploads, accounts, public result endpoint or individual feedback display.

## Deployment prerequisites (not done by the pull request)

1. Verify current authoritative DNS/nameservers, GitHub Pages custom domain and TLS before any change. Domain owner coordination is required. A Cloudflare Worker route requires traffic for the host to flow through a Cloudflare-proxied DNS record. Do **not** change DNS or proxy/TLS mode solely to deploy this survey without an agreed rollback plan.
2. Confirm who administers the Cloudflare zone. Create a **private** D1 database named hoax-survey-private under the permitted Cloudflare account. Run the SQL in survey-api/schema.sql against it, e.g.:
   - npx wrangler d1 create hoax-survey-private
   - npx wrangler d1 execute hoax-survey-private --remote --file=./schema.sql (working directory: survey-api)
3. Register a Turnstile widget for hoax.ai and obtain its public site key + secret.
4. Copy survey-api/wrangler.toml.example to survey-api/wrangler.toml (ignored by Git; do not commit a filled copy). Insert real D1 ID and PUBLIC Turnstile site key. Keep the SECRET only as a Worker secret:
   - cd survey-api && npx wrangler secret put TURNSTILE_SECRET
   - Run deploy only after secrets are configured; wrangler secret setup may require a Worker first deploy depending on tooling. Follow the Cloudflare workflow without committing secrets.
5. Configure Cloudflare WAF / rate limiting for /survey/api/submit, including an abuse-response procedure. Challenge verification is not a substitute for a rate limit.
6. Deploy the Worker, then verify GET https://hoax.ai/survey/api/status returns ready=true with a public sitekey. Confirm POST with missing/wrong verification fails; test a legitimate survey response, verify it in private D1, and ensure no answers appear in GitHub.
7. Merge this PR only once endpoint, TLS, staged survey and accessibility smoke test all pass. Smoke-test at mobile width, keyboard-only, screen reader basics, abort/network retry, and submission duplicate ID handling.
8. Create distribution-specific URLs only after live validation: https://hoax.ai/survey/?ref=rick and ?ref=discord. Referral codes are untrusted distribution hints, **not** verified user identity or random sampling.
9. Keep a private dated go-live record and anonymized aggregate analysis separately; no economic valuation in the public repository.

## Data boundaries

- No name, email, identifier, uploads, or account fields are requested.
- The D1 table stores question choices, optional comment (500 characters max), rough distribution referral, server insertion time, and a random idempotency identifier. Application code does not store network IP or user agent. Cloudflare's infrastructure may process request metadata under its own policies.
- Respondents are asked not to include identifying data in free text. Review raw text privately and redact unexpected personal details before analysis.
- Limit access to D1 to authorized operators. Do not enable a public export/metrics endpoint.
- Retention target: 90 days. Run the DELETE documented in schema.sql at least monthly or implement an account-owned scheduled purge; record the purge. Do not claim automatic deletion until configured.
- The survey is a convenience sample, possibly selected from Rick's domain investor audience. It cannot establish general-market demand, current domain valuation, or causal impact of the build.

## Evaluation integrity

- Q1 must be answered and locked *before* linking to the main site; all remaining questions come after a self-reported visit.
- No pre-answer explanatory text, testimonials or sample answers on stage 1 beyond the name.
- Do not modify published questions after collecting responses without versioning the instrument and separating cohorts.
- Automated traffic and responses from AI models are not human survey observations.
- Do not report percentages without a denominator and recruitment context.
- The open-ended text and cohorts remain private; report aggregated results separately from project documentation.
- No direct URL to this form should be posted publicly while the backend is unconfigured.

## Repo validation

Run from repository root:
  node --test survey-api/test/worker.test.js

Or from survey-api:
  npm test
