"""Map fixture fields to EP-P01 through EP-P17 protocol concepts."""

from __future__ import annotations

from typing import Any

PROTOCOL_FIELD_MAP = {
    "EP-P01": "artifact_condition",
    "EP-P02": "claim_condition",
    "EP-P03": "source_basis",
    "EP-P04": "source_confidence",
    "EP-P05": "provenance_status",
    "EP-P06": "context_status",
    "EP-P07": "traceability_status",
    "EP-P08": "chain_status",
    "EP-P09": "artifact_condition",
    "EP-P10": "context_status",
    "EP-P11": "drift_status",
    "EP-P12": "limitation_status",
    "EP-P13": "interpretation_risk_status",
    "EP-P14": "attribution_boundary_status",
    "EP-P15": "output_boundary_status",
    "EP-P16": "expected_allowed_posture_states",
    "EP-P17": "forbidden_output_expectations",
}


def map_protocol_steps(fixture: dict[str, Any]) -> dict[str, Any]:
    """Return internal protocol-step mapping without verdict language."""
    mapping: dict[str, Any] = {}
    for step_id, field in PROTOCOL_FIELD_MAP.items():
        mapping[step_id] = {
            "field": field,
            "value": fixture.get(field),
            "mapped": True,
        }
    return mapping
