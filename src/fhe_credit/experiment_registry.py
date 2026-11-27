"""Safe registry for stable scientific experiment identifiers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .configuration import (
    ConfigValidationError,
    IDENTIFIER_PATTERN,
    PUBLICATION_CLASSES,
    SCIENTIFIC_STATUSES,
    _validate_relative_path,
)


def load_experiment_registry(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load declarative experiment metadata without importing its executor."""
    source = Path(path).resolve()
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ConfigValidationError(f"invalid registry YAML: {error}") from error
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise ConfigValidationError("registry must use schema_version 1.0")
    if "registry_redirect" in data:
        redirect = Path(data["registry_redirect"])
        root = source.parents[2] if source.parts[-3:] == ("configs", "registry", "experiments.yaml") else source.parent
        if redirect.is_absolute() or ".." in redirect.parts:
            raise ConfigValidationError("registry redirect must be a safe relative path")
        return load_experiment_registry(root / redirect)
    entries = data.get("experiments")
    if not isinstance(entries, list):
        raise ConfigValidationError("registry.experiments must be a list")
    result: dict[str, dict[str, Any]] = {}
    required = {"experiment_id", "name", "scientific_question", "hypothesis", "dependencies", "configuration", "executor", "notebook", "status", "expected_artifacts", "visibility"}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ConfigValidationError(f"registry entry {index} must be a mapping")
        missing = sorted(required - set(entry))
        if missing:
            raise ConfigValidationError(f"registry entry {index} missing: {', '.join(missing)}")
        experiment_id = entry["experiment_id"]
        if not isinstance(experiment_id, str) or not IDENTIFIER_PATTERN.fullmatch(experiment_id):
            raise ConfigValidationError(f"invalid experiment_id in entry {index}")
        if experiment_id in result:
            raise ConfigValidationError(f"duplicate experiment_id: {experiment_id}")
        if entry["status"] not in SCIENTIFIC_STATUSES:
            raise ConfigValidationError(f"invalid status for {experiment_id}")
        if entry["visibility"] not in PUBLICATION_CLASSES:
            raise ConfigValidationError(f"invalid visibility for {experiment_id}")
        if not isinstance(entry["name"], str) or not isinstance(entry["scientific_question"], str):
            raise ConfigValidationError(f"name and scientific_question must be strings for {experiment_id}")
        if entry["hypothesis"] is not None and not isinstance(entry["hypothesis"], str):
            raise ConfigValidationError(f"hypothesis must be a string or null for {experiment_id}")
        if not isinstance(entry["dependencies"], list) or not isinstance(entry["expected_artifacts"], list):
            raise ConfigValidationError(f"dependencies and expected_artifacts must be lists for {experiment_id}")
        _validate_relative_path(entry["configuration"], f"registry[{experiment_id}].configuration")
        _validate_relative_path(entry["executor"], f"registry[{experiment_id}].executor")
        if entry["notebook"] is not None:
            _validate_relative_path(entry["notebook"], f"registry[{experiment_id}].notebook")
        if "experiment_directory" in entry:
            _validate_relative_path(entry["experiment_directory"], f"registry[{experiment_id}].experiment_directory")
        result[experiment_id] = entry
    return result
