# Internal Prototype Admissibility Regression Suite v1

## 1. Regression Suite Statement

Internal Prototype Admissibility Regression Suite v1 protects the controlled internal prototype from regressions across fixture coverage, traceability, compound boundary stress, guardrail red-team pressure, and output admissibility. Admissibility is not complete until regression prevents it from silently degrading.

## 2. Scope

- internal-only
- non-public
- no new fixtures
- no public benchmark
- no public report
- no public route
- no sitemap entry
- no public explanation layer
- no score
- no result card
- no output generation
- no user input behavior
- no external data

## 3. Regression Domains

- fixture_inventory_regression
- fixture_coverage_regression
- traceability_regression
- compound_boundary_regression
- guardrail_red_team_regression
- output_admissibility_regression
- forbidden_language_regression
- non_public_boundary_regression
- no_score_no_verdict_regression
- no_report_shape_regression

## 4. Required Regression Guarantees

The suite must guarantee:

- fixture count remains 16
- no fixtures lose required metadata
- every fixture remains synthetic and policy-safe
- all traceability fields remain present
- compound boundary stress cases remain protected
- guardrail red-team vectors remain blocked
- output admissibility rejects malformed or collapsed outputs
- forbidden output shapes remain rejected
- public output behavior remains absent
- no score/verdict/fake-real/report-shape output emerges

## 5. Regression Failure Meaning

A regression failure blocks publication, public exposure, output behavior, and future sprint continuation until repaired.

## 6. Non-Public Boundary

Passing the regression suite does not authorize public release. It only preserves internal validation continuity.
