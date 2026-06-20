"""Check prohibited output families for Controlled Internal Prototype v0."""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PATTERNS = [
    re.compile(r"\bfake\b", re.I),
    re.compile(r"\breal\b", re.I),
    re.compile(r"verified\s+(true|false)", re.I),
    re.compile(r"\bscore\b", re.I),
    re.compile(r"confidence\s+percentage", re.I),
    re.compile(r"\bdeceptive\b", re.I),
    re.compile(r"\bfraud\b", re.I),
    re.compile(r"\bguilty\b", re.I),
    re.compile(r"manipulation\s+proof", re.I),
    re.compile(r"legal\s+conclusion", re.I),
    re.compile(r"moderation\s+action", re.I),
    re.compile(r"detection\s+result", re.I),
    re.compile(r"result\s+card", re.I),
]

PROHIBITED_FAMILIES = [
    "fake/real verdict",
    "truth/falsity verdict",
    "deception finding",
    "manipulation proof",
    "fraud accusation",
    "subject guilt",
    "responsibility assignment",
    "legal conclusion",
    "moderation action",
    "numeric score",
    "confidence percentage",
    "upload classification result",
    "automated result card",
    "detector-style language",
]


def scan_text_for_prohibited(text: str) -> list[str]:
    """Return prohibited language blocks detected in text."""
    blocks: list[str] = []
    for pattern in PROHIBITED_PATTERNS:
        if pattern.search(text):
            blocks.append(pattern.pattern)
    return blocks


def verify_internal_structure(candidate: dict[str, Any]) -> dict[str, Any]:
    """Verify candidate internal structures contain no prohibited output families."""
    output_fields = (
        candidate.get("posture_state_candidate"),
        candidate.get("not_assessable_reason"),
        candidate.get("out_of_scope_reason"),
    )
    serialized = " ".join(str(v) for v in output_fields if v is not None)
    blocks = scan_text_for_prohibited(serialized)
    for family in PROHIBITED_FAMILIES:
        if family.lower() in serialized.lower():
            blocks.append(family)
    return {
        "prohibited_language_blocks": sorted(set(blocks)),
        "guardrail_failure_flags": sorted(set(blocks)),
        "passed": len(blocks) == 0,
    }
