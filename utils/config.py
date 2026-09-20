from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(value: str | Path, base: Path = PROJECT_ROOT) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def configured_dataset_path(key: str, config_path: str | Path | None = None) -> Path:
    dataset_config_path = Path(config_path) if config_path else PROJECT_ROOT / "configs" / "dataset.yaml"
    config = load_yaml(dataset_config_path)
    if key not in config:
        raise KeyError(f"Missing dataset path '{key}' in {dataset_config_path}")
    return resolve_path(config[key])


def class_names(config: dict[str, Any]) -> dict[int, str]:
    return {int(key): str(value) for key, value in config["classes"].items()}
