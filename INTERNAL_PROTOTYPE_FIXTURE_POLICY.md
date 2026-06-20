# Internal Prototype Fixture Policy

## Fixture Policy Statement

Future Hoax.ai internal prototype fixtures must be **synthetic, neutral, and governance-safe**. Fixtures exist to test protocol sequencing, posture mapping, boundary checks, and guardrail application — not to simulate real-world accusations, news events, or fact-check targets.

## Permitted Fixture Classes

- synthetic artifact descriptions with no real subject
- neutral claim text with no political or legal accusation
- governed source-basis stubs with no external verification
- provenance gap scenarios without manipulation proof
- context-collapse scenarios without motive inference
- claim-drift scenarios without deception default
- evidence-limitation envelopes without falsehood substitution
- interpretation-risk scenarios without blame language
- not-assessable prerequisite-failure scenarios
- out-of-scope boundary scenarios

## Prohibited Fixture Classes

- real person accusation
- active news event
- political claim
- celebrity claim
- company fraud claim
- medical misinformation case
- legal dispute
- public scandal
- private screenshots
- personal messages
- uploaded user files
- copyrighted article reproduction
- external fact-check target

## Synthetic Fixture Requirements

Every admissible fixture must:

- be labeled synthetic in fixture metadata
- avoid real names, institutions, or identifiable subjects unless explicitly governed in a future sprint
- avoid current-event references
- avoid verdict-implying language in fixture source material
- map to a governed protocol step or evidence condition dimension only

## No Real-Person Accusation Rule

Fixtures must not name or imply guilt, deception, fraud, or manipulation against any real person or institution.

## No Current-Event Exploitation Rule

Fixtures must not reference active news cycles, ongoing scandals, or time-sensitive public disputes.

## No Public Scandal Rule

Fixtures must not reproduce or simulate public scandal narratives for detector-style testing.

## No Uploaded/Private Material Rule

Fixtures must not include private screenshots, personal messages, user uploads, or copyrighted third-party content.

## No External Fact-Checking Target Rule

Fixtures must not point at live URLs, external articles, or third-party fact-check subjects for verification testing.

## Fixture Metadata Requirements

Each future fixture must carry metadata:

- fixture_id
- synthetic: true
- case_neutral: true
- non_personal: true
- non_accusatory: true
- protocol_step_ref (optional)
- evidence_condition_ref (optional)
- prohibited_output_check: true

## Future Fixture Validator Requirements

Before any prototype uses fixtures, a fixture validator must confirm:

- fixture class is permitted
- metadata is complete
- no prohibited fixture type matches
- no real-person or current-event patterns detected
- fixture output expectations remain non-verdict

---

*Sprint 70 — Internal Prototype Fixture Policy*
*Decision: DEC-088*
