"""Regression harness for Controlled Internal Prototype v0 hardening."""

from __future__ import annotations

import sys
from pathlib import Path

PROTOTYPE_ROOT = Path(__file__).resolve().parent
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

from admissibility_regression_harness import main as run_admissibility_regression_validation  # noqa: E402
from compound_boundary_stress_harness import main as run_stress_validation  # noqa: E402
from fixture_coverage_harness import main as run_coverage_validation  # noqa: E402
from guardrail_red_team_harness import main as run_red_team_validation  # noqa: E402
from guardrail_regression import run_guardrail_regression  # noqa: E402
from output_admissibility_harness import main as run_admissibility_validation  # noqa: E402
from targeted_fixture_expansion_harness import main as run_expansion_validation  # noqa: E402
from traceability_harness import main as run_traceability_validation  # noqa: E402
from validation_harness import main as run_fixture_validation  # noqa: E402


def main() -> int:
    if run_fixture_validation() != 0:
        return 1
    if run_traceability_validation() != 0:
        return 1
    if run_coverage_validation() != 0:
        return 1
    if run_expansion_validation() != 0:
        return 1
    if run_stress_validation() != 0:
        return 1
    if run_red_team_validation() != 0:
        return 1
    if run_admissibility_validation() != 0:
        return 1
    if run_admissibility_regression_validation() != 0:
        return 1
    if not run_guardrail_regression():
        return 1
    print("controlled internal prototype hardening validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
