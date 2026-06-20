# Output Language Guardrail Model v1

## 1. Guardrail Statement

**Any future Hoax.ai output may describe evidence posture, support limits, source caveats, provenance caveats, context caveats, traceability caveats, limitation caveats, interpretation-risk caveats, attribution-boundary caveats, and output-boundary caveats; it must not produce truth verdicts, fake/real labels, subject accusations, deception findings, legal judgments, scores, confidence percentages, or automated enforcement language.**

Hoax.ai must not merely prevent bad output. It must define the language by which evidence can be described without becoming accusation, verdict, score, or detector result.

## 2. Guardrail Status

Output Language Guardrail Model v1 is:

- **internal model only** — repository documentation and JSON, not a deployed system
- **non-operational** — no execution path, no rendering, no export pipeline
- **no output generator exists** — no automated language emission
- **no public engine exists** — Hoax.ai has no public engine and none is authorized by this guardrail
- **no classifier exists** — no categorical verdict labels beyond governed posture vocabulary
- **no score exists** — no numeric ranking or confidence percentage
- **no API exists** — no endpoints for output retrieval or submission
- **no public report system exists** — no user-facing report engine

**No score, no fake/real label, and no verdict system.**

## 3. Source Authority

This guardrail is derived from:

- **Evidence Posture Standard v1** — EPS-001 through EPS-014 and posture vocabulary
- **Evidence Posture Protocol v1 Draft** — EP-P01 through EP-P17 bounded output formation (EP-P17)
- **Engine Boundary Charter** — engine drift and non-operational constraints
- **Evidence Posture Engine Model v0** — evidence condition dimensions, boundary checks, permitted and prohibited output types
- **Output Boundary** — scope of governed statements
- **Evidence Limitation** — limitation-as-credibility infrastructure
- **Interpretation Risk** — restraint without accusation
- **Attribution Boundary** — artifact-only scope without subject transfer
- **Artifact–Subject Separation** — artifact condition is not subject guilt
- **Claim–Source Traceability** — claim strength relative to cited basis

## 4. Linguistic Primitives

Output Language Guardrail Model v1 defines twelve core primitives. Each primitive is a governed building block for **evidence posture language**, not a template for automated generation.

| Primitive | Definition | Function | Allowed use | Forbidden misuse | Standard | Protocol | Engine Model v0 |
|-----------|------------|----------|-------------|------------------|----------|----------|-----------------|
| evidence posture statement | Categorical posture description without verdict | Name artifact/claim condition under standard vocabulary | Supported, Qualified, Limited, Not Assessable, Out of Scope | fake/real, guilt, deception proof | EPS-005, EPS-006 | EP-P16 | posture_state |
| support limit | Boundary on how strongly language may claim support | Prevent overclaim from partial evidence | "supports a bounded reading", "does not establish" | truth certification, certainty inflation | EPS-012 | EP-P12 | evidence_limitation |
| caveat | Proportionate qualification attached to output | Preserve honesty under weak conditions | source, provenance, context, traceability, limitation, risk | caveat omission, headline certainty | EPS-003–004 | EP-P04–P06 | permitted_output_types |
| boundary reminder | Explicit restatement of output boundary | Block drift into verdict or subject transfer | "artifact condition does not support subject attribution" | moderation action, enforcement | EPS-006, EPS-014 | EP-P14–P15 | output_boundary_check |
| non-transfer rule | Prohibition on artifact-to-subject inference | Preserve artifact-subject separation | artifact-only scope language | subject guilt, responsibility | EPS-002, EPS-014 | EP-P14 | artifact_subject_separation_check |
| interpretation restraint | Narrow language under high interpretive risk | Prevent accusation from ambiguity | "interpretation risk requires restraint" | blame, motive, deception default | EPS-013 | EP-P13 | interpretation_risk_status |
| source basis qualifier | Source-relationship language without certification | Describe source condition in bounds | "source basis is limited", "requires qualification" | fraud label, verified true/false | EPS-003 | EP-P03–P04 | source_confidence |
| provenance qualifier | Chain/origin language without manipulation proof | Name provenance gap or continuity | "provenance condition limits interpretation" | manipulation proven, concealment proof | EPS-004 | EP-P05 | provenance_status |
| traceability qualifier | Claim-to-source mapping language | Govern claim strength | "claim-source relationship requires qualification" | deception default from weak trace | EPS-007 | EP-P07 | traceability_status |
| limitation qualifier | Envelope-edge language for partial evidence | Define responsible speech limits | "evidence limitation envelope applies" | falsehood from gap | EPS-012 | EP-P12 | limitation_status |
| attribution boundary qualifier | Scope lock to artifact review | Block subject-transfer overclaim | "does not transfer to subject attribution" | creator intent, guilt | EPS-014 | EP-P14 | attribution_boundary_status |
| output boundary constraint | Refusal of prohibited phrasing | Enforce standard language gates | refuse fake/real, scores, enforcement | detector result cards | EPS-006 | EP-P15, EP-P17 | output_boundary_check |

## 5. Allowed Output Families

Allowed language families for future governed output (conceptual only):

- evidence posture statement
- support condition statement
- qualification statement
- source caveat
- provenance caveat
- context caveat
- traceability caveat
- claim drift caveat
- evidence limitation caveat
- interpretation risk caveat
- attribution boundary caveat
- output boundary caveat
- not assessable statement
- out of scope statement
- bounded next-reading suggestion

These families express **bounded output language** and **posture without verdict**.

## 6. Prohibited Output Families

Prohibited language families:

- fake/real verdict
- truth/falsity verdict
- lie/deception finding
- manipulation proof
- fraud accusation
- subject guilt
- responsibility assignment
- creator intent
- legal conclusion
- moderation/enforcement recommendation
- numeric score
- confidence percentage
- upload classification result
- automated result card
- public detector result

## 7. Output Certainty Without Scoring

Hoax.ai expresses strength of support through **evidence posture language**, not probability or rank:

| Expression | Meaning | Not equivalent to |
|------------|---------|-------------------|
| supports | Material conditions align for bounded posture reading | verified true |
| qualifies | Support exists with explicit conditions | partial score |
| limits | Language must remain narrow | low confidence % |
| does not establish | Insufficient for stronger posture | false |
| cannot assess | Prerequisites fail for posture | hidden judgment |
| remains bounded by | Output envelope active | verdict pending |
| requires caveat | Qualification mandatory | weakness score |
| does not transfer to subject attribution | Artifact-subject separation | innocence/guilt |

No score. No percentage. No fake/real label. No probability field.

## 8. Posture-State Linguistic Grammar

### Supported

- **May say:** "The available evidence supports a Supported posture reading under the current material."; bounded output language with standard-aligned phrasing.
- **Must not imply:** truth certification, subject guilt, deception absence, legal conclusion.
- **Required caveats:** source and provenance caveats when EPS-003 or EPS-004 conditions apply.
- **Allowed structures:** posture statement + support condition + optional caveat stack.
- **Prohibited structures:** "verified true", "authentic", "not manipulated", result-card framing.
- **Boundary reminder:** artifact-subject separation; output boundary discipline.
- **Category language:** evidence posture, bounded output language, posture without verdict.

### Qualified

- **May say:** "The available evidence supports a Qualified reading with explicit conditions."
- **Must not imply:** full support, score elevation, fake/real resolution.
- **Required caveats:** source basis qualifier, traceability qualifier when claim-source mapping is partial.
- **Allowed structures:** posture + qualification statement + caveat stack.
- **Prohibited structures:** headline certainty, confidence percentage, detector-style labels.
- **Boundary reminder:** qualification is not certification.

### Limited

- **May say:** "The available evidence supports only a Limited posture reading."
- **Must not imply:** falsehood, deception, manipulation proof from limitation alone.
- **Required caveats:** evidence limitation caveat, interpretation risk caveat when EPS-012/013 active.
- **Allowed structures:** limitation envelope + restrained posture language.
- **Prohibited structures:** "likely fake", "probably deceptive", numeric rank.

### Not Assessable

- **May say:** "The evidence condition is not assessable from the available material."
- **Must not imply:** hidden negative judgment, failure, guilt, fake default.
- **Required caveats:** not assessable statement per EPS-005; prerequisite failure named.
- **Allowed structures:** not assessable posture + limitation explanation.
- **Prohibited structures:** substituting Limited/Qualified to avoid institutional discomfort.

### Out of Scope

- **May say:** "This material is out of scope for evidence posture review under current boundaries."
- **Must not imply:** subject accusation, enforcement recommendation.
- **Required caveats:** output boundary caveat; scope boundary named.
- **Allowed structures:** out of scope statement + boundary reminder.
- **Prohibited structures:** moderation action language, legal conclusion.

## 9. Template Families (Conceptual, Non-Operational)

Each template is **conceptual and non-operational**. No template executes or renders.

- "The available evidence supports a [posture] reading."
- "The source basis is [condition], so the output must remain [bounded/qualified/limited]."
- "The provenance condition limits interpretation."
- "The claim-source relationship requires qualification."
- "The artifact condition does not support subject attribution."
- "The evidence condition is not assessable from the available material."
- "Interpretation risk is high; output language must remain restrained."

## 10. Required Caveat Rules

| Trigger condition | Required caveat |
|-------------------|---------------|
| source_confidence_low | source caveat |
| provenance_gap | provenance caveat |
| context_collapse | context caveat |
| weak_traceability | traceability caveat |
| claim_drift | drift caveat |
| evidence_limitation | limitation caveat |
| high_interpretation_risk | interpretation risk caveat |
| attribution_boundary_risk | subject-transfer caveat |
| output_boundary_risk | prohibited-language guardrail |

Caveat omission is a guardrail failure mode.

## 11. Forbidden Term Controls

**Forbidden as output conclusions:** fake, real, lie, lied, deception, deceptive, fraud, fraudulent, manipulated, manipulation proven, guilty, responsible, intended to deceive, verified true, verified false, score, confidence percent, detection result.

**Allowed only as prohibited-language examples** (in guardrail documentation): fake, real, score, detector, upload, scan — when illustrating what outputs must refuse.

## 12. Boundary Transformation Rules

| Unsafe transformation | Why it violates Hoax.ai | Safe alternative | Validator-detectable terms |
|-----------------------|-------------------------|------------------|---------------------------|
| evidence limitation → falsehood | EPS-012; gap is not proof of false content | "evidence limitation envelope applies" | "therefore false", "proven untrue" |
| claim drift → deception | EPS-011; drift is structural, not intent proof | "claim drift caveat applies" | "deceptive intent", "lied" |
| provenance gap → manipulation | EPS-004; gap narrows language only | "provenance condition limits interpretation" | "manipulation proven", "concealed" |
| context collapse → motive | EPS-009; context loss ≠ misconduct | "context caveat applies" | "motive proven", "misconduct proof" |
| source weakness → fraud | EPS-003; source condition ≠ fraud label | "source basis requires qualification" | "fraudulent source", "fraud accusation" |
| interpretation risk → verdict | EPS-013; risk triggers restraint | "interpretation risk requires restraint" | "guilty", "responsible" |
| artifact condition → subject guilt | EPS-002, EPS-014 | "does not transfer to subject attribution" | "subject guilt", "creator intent" |
| evidence chain continuity → truth certification | EPS-010 | "continuity described; not truth certified" | "verified true", "certified authentic" |
| synthetic fragility → fake | EPS-008 | "synthetic fragility caveat; not fake label" | "fake", "not real" |
| confidence language → certification | EPS-003, EPS-006 | source caveat without numeric confidence | "confidence percent", "score:" |

## 13. Canonical Language Assets

Hoax.ai owns these category-defining phrases for **evidence posture language** and **non-verdict evidence framework** positioning:

- evidence posture
- bounded output language
- artifact-subject separation
- non-transfer language
- evidence limitation envelope
- interpretation restraint
- source-basis qualifier
- provenance caveat
- output boundary discipline
- posture without verdict
- evidence condition without accusation
- not assessable posture
- out of scope posture
- claim-source traceability
- attribution boundary

## 14. Future Engine Dependency

Any future engine model, prototype, report system, or interface must obey this guardrail before any output is rendered, displayed, exported, or stored. Engine Model v0 maps conditions; this guardrail maps **language**. Both are prerequisites for any future internal non-public prototype.

## 15. Failure Modes

- verdict leakage
- detector drift
- score drift
- caveat omission
- subject-transfer leakage
- synthetic-to-fake leakage
- limitation-to-falsehood leakage
- drift-to-deception leakage
- output certainty inflation
- public result-card framing

## 16. Future Prototype Gate

A future internal non-public prototype may be considered only after Output Language Guardrail Model v1 validation passes, Internal Non-Public Engine Prototype Charter validation passes (DEC-088), and a separate sprint explicitly authorizes controlled non-public prototyping.

## Internal Non-Public Engine Prototype Charter Dependency

Internal Non-Public Engine Prototype Charter (Sprint 70, DEC-088) defines prototype admissibility, fixture policy, environment boundaries, and execution limits before any prototype is authorized. Any future prototype must obey this charter in addition to Engine Model v0 and this guardrail. See `INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER.md` and `data/internal-non-public-engine-prototype-charter-v1.json`.

## Controlled Internal Prototype v0 Authorization Package Dependency

Controlled Internal Prototype v0 Authorization Package (Sprint 71, DEC-089) is the final authorization layer before Sprint 72 may consider implementation. It defines permitted future components, prohibited components, output boundaries, and disqualification conditions. See `CONTROLLED_INTERNAL_PROTOTYPE_V0_AUTHORIZATION_PACKAGE.md` and `data/controlled-internal-prototype-v0-authorization-package.json`.

No prototype, public route, sitemap entry, input system, output generator, classifier, scorer, API, JavaScript surface, or public tool behavior is authorized by this document.

---

*Sprint 69 — Output Language Guardrail Model v1*
*Updated Sprint 70 — Internal Non-Public Engine Prototype Charter dependency (DEC-088)*
*Updated Sprint 71 — Authorization Package dependency (DEC-089)*
*Decision: DEC-087*
*Date: 2026-06-20*
