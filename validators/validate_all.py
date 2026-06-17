#!/usr/bin/env python3
"""Run all Hoax.ai repository validators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATORS = [
    ROOT / "validators" / "validate_factory_foundation.py",
]


def main() -> int:
    exit_code = 0
    for validator in VALIDATORS:
        if not validator.exists():
            print(f"ERROR: validator missing: {validator}")
            exit_code = 1
            continue
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            exit_code = result.returncode
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
