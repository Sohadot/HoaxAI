# Internal Prototype Regression Case Matrix v1

## Regression Matrix Statement

This matrix binds prior sprint harness coverage into unified regression case groups with required negative mutations, expected failure status, and pass conditions. It is internal governance only; it does not authorize public output or reporting.

## Regression Case Groups

| Regression domain | Existing harness coverage | Required negative mutation | Expected failure status | Required pass condition | Non-public confirmation |
|---|---|---|---|---|---|
| missing posture basis | output_admissibility_harness.py | remove posture_basis from admissible result | inadmissible_missing_basis | mutation fails admissibility; baseline fixtures pass | no public output |
| missing caveat | output_admissibility_harness.py | clear triggered_caveats and caveat_trigger_refs | inadmissible_missing_caveat | mutation fails; caveats preserved on fixtures | no public output |
| missing traceability refs | traceability_harness.py | remove trace_id and traceability_map | inadmissible_traceability_gap | mutation fails; all fixtures retain traceability | no public output |
| missing boundary check | output_admissibility_harness.py | clear active_boundary_checks and boundary_check_refs | inadmissible_boundary_collapse | mutation fails; boundary checks intact on fixtures | no public output |
| missing guardrail block | guardrail_red_team_harness.py | set guardrail_blocked validation_status | inadmissible_guardrail_failure | mutation fails; guardrails pass on fixtures | no public output |
| forbidden phrase leakage | guardrail_regression.py | inject prohibited phrase into output candidate | inadmissible_guardrail_failure | mutation fails; guardrail regression passes | no public output |
| score leakage | output_admissibility_harness.py | inject confidence score stub | inadmissible_guardrail_failure | mutation fails; no_score_confirmation preserved | no score output |
| verdict leakage | output_admissibility_harness.py | clear no_verdict_confirmation | inadmissible_guardrail_failure | mutation fails; no_verdict_confirmation preserved | no verdict output |
| accusation transfer | output_admissibility_harness.py | inject fraud accusation stub | inadmissible_guardrail_failure | mutation fails; accusation markers blocked | no accusation output |
| report-shape output | output_admissibility_harness.py | inject public report generation stub | inadmissible_report_shape | mutation fails; no report shape on fixtures | no public report |
| result-card-shape output | output_admissibility_harness.py | inject result card envelope stub | inadmissible_report_shape | mutation fails; no result-card shape on fixtures | no result card |
| fixture metadata loss | fixture_coverage_harness.py | simulate missing fixture_id metadata | fixture_inventory_regression fail | inventory check detects metadata loss | internal-only |
| fixture count drift | validation_harness.py | compare fixture count to required 16 | fixture_inventory_regression fail | count remains exactly 16 | no new fixtures |
| public route drift | admissibility_regression_suite.py | verify sitemap and route registry unchanged | non_public_boundary_regression fail | sitemap 19 URLs; registry 19 entries | no public route |
| network import drift | admissibility_regression_suite.py | scan prototype modules for network imports | non_public_boundary_regression fail | no requests/urllib/httpx/aiohttp/socket imports | no network behavior |
| user input drift | admissibility_regression_suite.py | scan prototype modules for input/CLI patterns | non_public_boundary_regression fail | no input/argparse/click/typer usage | no user input |
