"""Safe loading and validation for versioned experimental YAML configurations."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "1.0"
SCIENTIFIC_STATUSES = frozenset({"HISTORICAL", "EXPLORATORY", "PRELIMINARY", "CONFIRMED"})
PUBLICATION_CLASSES = frozenset({"PRIVATE", "REVIEW_REQUIRED", "PUBLIC_APPROVED"})
EXECUTION_MODES = frozenset({"analyze", "execute"})
IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")
REQUIRED_FIELDS = frozenset({
    "schema_version", "experiment_id", "configuration_id", "description",
    "scientific_status", "dependencies", "parameters", "input_artifacts",
    "execution", "publication",
})


class ConfigValidationError(ValueError):
    """Raised when a configuration is structurally unsafe or incomplete."""


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigValidationError(f"{field} must be a mapping")
    return value


def _validate_identifier(value: Any, field: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise ConfigValidationError(f"{field} must match {IDENTIFIER_PATTERN.pattern}")


def _validate_relative_path(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConfigValidationError(f"{field} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ConfigValidationError(f"{field} must stay inside the repository")


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate data only; this function never executes configuration content."""
    config = _require_mapping(config, "configuration")
    missing = sorted(REQUIRED_FIELDS - set(config))
    if missing:
        raise ConfigValidationError(f"missing required fields: {', '.join(missing)}")
    if config["schema_version"] != SCHEMA_VERSION:
        raise ConfigValidationError(f"unsupported schema_version: {config['schema_version']!r}")
    _validate_identifier(config["experiment_id"], "experiment_id")
    _validate_identifier(config["configuration_id"], "configuration_id")
    if not isinstance(config["description"], str) or not config["description"].strip():
        raise ConfigValidationError("description must be a non-empty string")
    if config["scientific_status"] not in SCIENTIFIC_STATUSES:
        raise ConfigValidationError("scientific_status is not allowed")
    if not isinstance(config["dependencies"], list) or not all(isinstance(item, str) for item in config["dependencies"]):
        raise ConfigValidationError("dependencies must be a list of strings")
    _require_mapping(config["parameters"], "parameters")
    if not isinstance(config["input_artifacts"], list):
        raise ConfigValidationError("input_artifacts must be a list")
    for index, artifact in enumerate(config["input_artifacts"]):
        artifact = _require_mapping(artifact, f"input_artifacts[{index}]")
        if "path" not in artifact:
            raise ConfigValidationError(f"input_artifacts[{index}].path is required")
        _validate_relative_path(artifact["path"], f"input_artifacts[{index}].path")
    execution = _require_mapping(config["execution"], "execution")
    if execution.get("mode") not in EXECUTION_MODES:
        raise ConfigValidationError("execution.mode must be analyze or execute")
    if "executor" in execution:
        _validate_relative_path(execution["executor"], "execution.executor")
    if "adapter" in execution and (not isinstance(execution["adapter"], str) or not execution["adapter"].strip()):
        raise ConfigValidationError("execution.adapter must be a non-empty string")
    if config["publication"] not in PUBLICATION_CLASSES:
        raise ConfigValidationError("publication is not allowed")
    return config


def load_config(path: str | Path) -> dict[str, Any]:
    """Safely parse and validate one YAML configuration file."""
    source = Path(path)
    if source.suffix not in {".yaml", ".yml"}:
        raise ConfigValidationError("configuration must be a YAML file")
    try:
        parsed = yaml.safe_load(source.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ConfigValidationError(f"invalid YAML: {error}") from error
    return validate_config(parsed)


def config_hash(config: dict[str, Any]) -> str:
    """Hash canonical validated configuration data, independent of YAML layout."""
    validated = validate_config(config)
    canonical = json.dumps(validated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
