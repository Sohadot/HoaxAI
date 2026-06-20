# Controlled Prototype v0 Disqualification Matrix

| Disqualifying condition | Why it violates Hoax.ai | Trigger examples | Required response | Validator target |
|-------------------------|-------------------------|------------------|-------------------|------------------|
| public route leakage | Public routes convert governance into product exposure | New `/tool/` page registered; prototype HTML in public path | Remove route; revert registry; fail validation | no_public_route_validator |
| sitemap leakage | Sitemap expansion implies launch readiness | Prototype URL added to sitemap.xml | Restore 19-URL sitemap; fail validation | no_sitemap_change_validator |
| upload implication | Upload implies operational input system | Upload form, file input, drag-drop zone | Remove UI; fail validation | no_upload_validator |
| user-input implication | User input implies public tool behavior | Text field for claim submission; URL paste box | Remove input; fail validation | no_upload_validator |
| fake/real leakage | Violates evidence-posture non-verdict doctrine | "fake", "real", "authentic", "inauthentic" in output | Block output; fail guardrail | forbidden_language_validator |
| score leakage | Scoring implies detector or grading product | Numeric score, percentage, grade, confidence meter | Remove score fields; fail validation | no_score_validator |
| subject accusation leakage | Violates artifact-subject separation | Subject named as deceptive; guilt attributed to person | Block output; fail guardrail | output_guardrail_validator |
| real-person fixture | Real cases create accusation and liability risk | Celebrity name; named executive; politician | Remove fixture; fail fixture policy | fixture_policy_validator |
| current-event fixture | Current events create news-cycle exploitation | Active scandal headline; breaking news claim | Remove fixture; fail fixture policy | fixture_policy_validator |
| external API call | External data breaks fixture-bound local-only boundary | HTTP client to fact-check API; web fetch | Remove code; fail validation | no_external_api_validator |
| live web lookup | Live lookup implies operational verification engine | URL fetch; search integration | Remove connector; fail validation | no_external_api_validator |
| output generator drift | Output generator becomes public report system | Rendered verdict card; formatted accusation report | Remove renderer; fail validation | output_guardrail_validator |
| public demo drift | Demo implies product availability | "Try it" page; interactive public prototype | Remove demo; fail public exposure checks | no_public_link_validator |
| marketing/demo framing | Marketing converts governance into product pitch | "Detect hoaxes now"; product landing copy | Remove copy; fail validation | public_exposure_checks |
| report-export drift | Export implies shareable verdict product | PDF report; share link; downloadable result | Remove exporter; fail validation | output_guardrail_validator |
| API endpoint drift | API implies operational backend | REST endpoint; webhook; server handler | Remove endpoint; fail validation | no_public_route_validator |

---

*Sprint 71 — Controlled Prototype v0 Disqualification Matrix*  
*Decision: DEC-089*
