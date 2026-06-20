"""Load governed internal JSON models for Controlled Internal Prototype v0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROTOTYPE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROTOTYPE_ROOT.parents[2]

MODEL_PATHS = {
    "engine_model": REPO_ROOT / "data" / "evidence-posture-engine-model-v0.json",
    "guardrail_model": REPO_ROOT / "data" / "output-language-guardrail-model-v1.json",
    "prototype_charter": REPO_ROOT / "data" / "internal-non-public-engine-prototype-charter-v1.json",
    "authorization_package": REPO_ROOT
    / "data"
    / "controlled-internal-prototype-v0-authorization-package.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_models() -> dict[str, Any]:
    """Load only fixed governed repository model paths."""
    models: dict[str, Any] = {}
    for key, path in MODEL_PATHS.items():
        if not path.is_file():
            raise FileNotFoundError(f"governed model missing: {path}")
        models[key] = _load_json(path)
    return models
