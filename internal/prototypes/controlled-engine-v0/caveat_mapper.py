"""Map fixture conditions to required caveat family IDs."""

from __future__ import annotations

from typing import Any

CAVEAT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("source_caveat", ("source", "confidence", "basis")),
    ("provenance_caveat", ("provenance", "chain")),
    ("context_caveat", ("context", "collapse")),
    ("traceability_caveat", ("traceability", "chain")),
    ("drift_caveat", ("drift",)),
    ("limitation_caveat", ("limitation", "assessment_blocked")),
    ("interpretation_risk_caveat", ("interpretation", "risk")),
    ("attribution_boundary_caveat", ("attribution", "subject")),
    ("output_boundary_caveat", ("output", "scope", "boundary")),
]


def map_caveats(fixture: dict[str, Any]) -> list[str]:
    """Return internal caveat IDs expected from fixture conditions."""
    expected = set(fixture.get("expected_required_caveats", []))
    triggered: set[str] = set()
    blob = " ".join(
        str(fixture.get(k, ""))
        for k in (
            "source_confidence",
            "provenance_status",
            "context_status",
            "traceability_status",
            "chain_status",
            "drift_status",
            "limitation_status",
            "interpretation_risk_status",
            "attribution_boundary_status",
            "output_boundary_status",
        )
    ).lower()
    for caveat_id, markers in CAVEAT_RULES:
        if any(marker in blob for marker in markers):
            triggered.add(caveat_id)
    return sorted(expected | triggered)
