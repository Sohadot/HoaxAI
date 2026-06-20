# Internal Prototype Future Fixture Admission Criteria

## Fixture Admission Statement

A future synthetic fixture is admissible only if it closes a named coverage gap and preserves synthetic, neutral, non-public, non-accusatory, non-current-event constraints.

Volume alone is never sufficient justification.

## Required Justification for Every Future Fixture

Each proposed fixture must document:

- why the fixture is needed
- which named gap it closes
- why existing fixtures cannot cover the gap
- why the fixture remains synthetic and non-public

## Required Coverage Gap Reference

Every future fixture proposal must cite an entry from coverage_gaps in `data/internal-prototype-fixture-coverage-matrix-v1.json` or a future-candidate ID from the taxonomy.

## Required Policy Flags

All fixtures must satisfy Internal Prototype Fixture Policy flags:

- synthetic: true
- real_person: false
- current_event: false
- political: false
- legal: false
- medical: false
- financial_advice: false
- company_accusatory: false
- private_data: false
- external_fact_check_target: false

## Required Expected Posture State

Each fixture must declare expected_allowed_posture_states aligned with Evidence Posture Standard v1 posture vocabulary.

## Required Expected Caveats

Each fixture must declare expected_required_caveats that match activated boundary checks.

## Required Boundary Activation

When a fixture targets a boundary gap, it must declare which boundary check(s) it activates and how.

## Required Forbidden Transformation Target When Applicable

When a fixture tests guardrail behavior, it must declare forbidden_output_expectations without producing prohibited language in fixture narrative fields.

## Required Traceability Fields

Each fixture must be traceable through prototype_core and traceability_mapper to protocol steps, standard principles, boundary checks, and caveat triggers.

## Disqualifying Fixture Criteria

A fixture is disqualified if it:

- references a real person, company, or current event
- requires external data or live URL
- implies verdict, score, or fake/real label as expected output
- exists only to increase fixture count
- violates fixture policy flags
- requires public exposure to be meaningful

## Reviewer Checklist

- [ ] Named coverage gap reference documented
- [ ] Policy flags verified
- [ ] Expected posture state declared
- [ ] Expected caveats declared
- [ ] Boundary activation documented
- [ ] Forbidden transformation target documented when applicable
- [ ] Traceability linkage verified
- [ ] No public route or benchmark implied
- [ ] No real-world case material used

## Future Validator Requirements

Future fixture expansion sprints must:

- update coverage matrix JSON with revised coverage statuses
- run fixture_coverage_harness.py
- run traceability_harness.py and regression_harness.py
- pass validate_all.py
- preserve sitemap at exactly 19 URLs

## Governing Rule

A future fixture is admissible only if it closes a named gap and preserves synthetic, neutral, non-public, non-accusatory, non-current-event constraints.
