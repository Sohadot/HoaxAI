"""Release blocker board for Controlled Internal Prototype v0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BOARD_REL = "data/internal-prototype-release-blocker-board-v1.json"
REQUIRED_BLOCKER_COUNT = 20

REQUIRED_BLOCKER_CATEGORIES = [
    "public_route_blocker",
    "public_output_blocker",
    "public_report_blocker",
    "benchmark_blocker",
    "input_system_blocker",
    "upload_blocker",
    "scoring_blocker",
    "API_blocker",
    "external_data_blocker",
    "legal_risk_blocker",
    "real_world_case_blocker",
    "privacy_blocker",
    "claim_overreach_blocker",
    "evidence_authority_blocker",
    "output_admissibility_blocker",
    "guardrail_blocker",
    "traceability_blocker",
    "regression_blocker",
    "governance_blocker",
    "monetization_blocker",
]

AUTHORIZATION_FLAGS = [
    "release_authorized",
    "public_route_authorized",
    "public_benchmark_authorized",
    "public_report_authorized",
    "output_generator_authorized",
    "input_system_authorized",
    "upload_authorized",
    "scoring_authorized",
    "api_authorized",
    "javascript_authorized",
    "monetization_authorized",
]

CLEARED_STATUSES = frozenset({"cleared", "resolved_public", "public_authorized"})


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_release_blocker_board(root: Path | None = None) -> dict[str, Any]:
    """Load release blocker board JSON from repository data."""
    board_path = (root or _repo_root()) / BOARD_REL
    with board_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def evaluate_release_blocker_board(root: Path | None = None) -> dict[str, Any]:
    """Verify release blockers remain unresolved and public authorization remains false."""
    board = load_release_blocker_board(root)
    blockers = board.get("blockers", [])
    failures: list[str] = []

    if board.get("board_id") != "internal-prototype-release-blocker-board-v1":
        failures.append("board_id_mismatch")
    if len(blockers) < REQUIRED_BLOCKER_COUNT:
        failures.append("blocker_count_drift")

    categories = board.get("blocker_categories", [])
    for category in REQUIRED_BLOCKER_CATEGORIES:
        if category not in categories:
            failures.append(f"missing_category_{category}")

    for flag in AUTHORIZATION_FLAGS:
        if board.get(flag) is not False:
            failures.append(f"{flag}_not_false")

    clearance_doc = board.get("clearance_criteria", "")
    if clearance_doc != "INTERNAL_PROTOTYPE_RELEASE_BLOCKER_CLEARANCE_CRITERIA_V1.md":
        failures.append("clearance_criteria_mismatch")
    if "does not clear" not in str(board.get("non_release_statement", "")).lower():
        failures.append("non_release_statement_missing")

    unresolved = 0
    for blocker in blockers:
        status = str(blocker.get("current_status", "")).lower()
        if status in CLEARED_STATUSES or blocker.get("public_exposure_allowed") is True:
            failures.append(f"blocker_cleared_{blocker.get('blocker_id', 'unknown')}")
        if status == "unresolved":
            unresolved += 1
        clearance_sprint = str(blocker.get("authorized_clearance_sprint", "")).lower()
        if "future" not in clearance_sprint and "explicit" not in clearance_sprint:
            failures.append(f"clearance_sprint_not_explicit_{blocker.get('blocker_id', 'unknown')}")

    if unresolved < REQUIRED_BLOCKER_COUNT:
        failures.append("unresolved_blocker_drift")

    return {
        "board_id": board.get("board_id"),
        "blocker_count": len(blockers),
        "unresolved_blocker_count": unresolved,
        "blocker_board_validation_status": "pass" if not failures else "fail",
        "validation_failures": failures,
        "release_authorized": False,
        "public_exposure_allowed": False,
        "non_public_confirmation": True,
    }
