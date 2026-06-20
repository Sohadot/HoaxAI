"""Guardrail regression checks for Controlled Internal Prototype v0 hardening."""

from __future__ import annotations

from typing import Any

from output_guardrail_checker import verify_internal_structure

# Synthetic internal test vectors only — not real-world claims or outputs.
NEGATIVE_VECTORS: list[dict[str, Any]] = [
    {"posture_state_candidate": "Supported", "not_assessable_reason": None, "out_of_scope_reason": None},
    {
        "posture_state_candidate": "artifact shows verdict_label_stub",
        "not_assessable_reason": None,
        "out_of_scope_reason": None,
    },
    {
        "posture_state_candidate": "Qualified",
        "not_assessable_reason": "numeric_grade_stub",
        "out_of_scope_reason": None,
    },
    {
        "posture_state_candidate": "Limited",
        "not_assessable_reason": None,
        "out_of_scope_reason": "subject_transfer_stub",
    },
]

BLOCKED_INDEXES = {1, 2, 3}


def run_guardrail_regression() -> bool:
    """Return True when guardrail correctly blocks prohibited synthetic vectors."""
    for index, vector in enumerate(NEGATIVE_VECTORS):
        result = verify_internal_structure(vector)
        should_pass = index not in BLOCKED_INDEXES
        if result["passed"] != should_pass:
            return False
    return True
