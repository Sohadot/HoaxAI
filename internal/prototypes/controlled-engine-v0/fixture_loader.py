"""Load and validate governed synthetic fixtures for Controlled Internal Prototype v0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROTOTYPE_ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = PROTOTYPE_ROOT / "fixtures" / "synthetic-fixtures-v0.json"

REQUIRED_FLAGS = {
    "synthetic": True,
    "real_person": False,
    "current_event": False,
    "political": False,
    "legal": False,
    "medical": False,
    "financial_advice": False,
    "company_accusatory": False,
    "private_data": False,
    "external_fact_check_target": False,
}


def _validate_fixture(fixture: dict[str, Any]) -> None:
    for key, expected in REQUIRED_FLAGS.items():
        if fixture.get(key) is not expected:
            raise ValueError(f"fixture {fixture.get('fixture_id')} failed policy flag {key}")
    if not fixture.get("fixture_id"):
        raise ValueError("fixture missing fixture_id")


def load_fixtures() -> list[dict[str, Any]]:
    """Load only the governed synthetic fixture file."""
    if not FIXTURE_PATH.is_file():
        raise FileNotFoundError(f"fixture file missing: {FIXTURE_PATH}")
    with FIXTURE_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    fixtures = data.get("fixtures", [])
    if len(fixtures) < 5:
        raise ValueError("fixture set must contain at least 5 fixtures")
    for fixture in fixtures:
        _validate_fixture(fixture)
    return fixtures
