"""Local release blocker board harness for Controlled Internal Prototype v0."""

from __future__ import annotations

import sys
from pathlib import Path

PROTOTYPE_ROOT = Path(__file__).resolve().parent
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

from release_blocker_board import REQUIRED_BLOCKER_COUNT, evaluate_release_blocker_board  # noqa: E402


def main() -> int:
    result = evaluate_release_blocker_board()
    if result.get("blocker_count", 0) < REQUIRED_BLOCKER_COUNT:
        return 1
    if result.get("unresolved_blocker_count", 0) < REQUIRED_BLOCKER_COUNT:
        return 1
    if result.get("blocker_board_validation_status") != "pass":
        return 1
    if result.get("release_authorized") is not False:
        return 1
    if result.get("public_exposure_allowed") is not False:
        return 1

    print("controlled internal release blocker board validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
