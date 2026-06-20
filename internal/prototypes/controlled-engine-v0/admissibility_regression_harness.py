"""Local admissibility regression harness for Controlled Internal Prototype v0."""

from __future__ import annotations

import sys
from pathlib import Path

PROTOTYPE_ROOT = Path(__file__).resolve().parent
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

from admissibility_regression_suite import (  # noqa: E402
    REGRESSION_DOMAINS,
    REQUIRED_FIXTURE_COUNT,
    REQUIRED_HARNESSES,
    run_admissibility_regression_suite,
)


def main() -> int:
    if len(REGRESSION_DOMAINS) < 10:
        return 1

    for harness in REQUIRED_HARNESSES:
        if not (PROTOTYPE_ROOT / harness).is_file():
            return 1

    result = run_admissibility_regression_suite(PROTOTYPE_ROOT)
    if result.get("fixture_count") != REQUIRED_FIXTURE_COUNT:
        return 1
    if result.get("regression_validation_status") != "pass":
        return 1
    if len(result.get("domain_results", [])) != len(REGRESSION_DOMAINS):
        return 1
    for domain in result.get("domain_results", []):
        if domain.get("regression_status") != "pass":
            return 1

    print("controlled internal admissibility regression validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
