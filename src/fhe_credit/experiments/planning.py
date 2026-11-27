"""Read-only resolution of configuration, registry entry, and allowed adapter."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..configuration import ConfigValidationError, config_hash, load_config
from ..experiment_registry import load_experiment_registry
from .adapters import get_adapter
from .artifacts import resolve_within
from .errors import AdapterNotAllowedError, ArtifactIntegrityError, ExperimentError


def _project_path(root: Path, path: str | Path, category: str) -> Path:
    resolved = Path(path).resolve()
    allowed_roots = [(root / category).resolve(), (root / "experiments").resolve()]
    if not any(resolved == allowed or allowed in resolved.parents for allowed in allowed_roots):
        raise ArtifactIntegrityError("configuration path is outside authorized configs or experiments directories")
    return resolved


def build_plan(config_path: str | Path, project_root: str | Path) -> dict[str, Any]:
    """Resolve one plan without creating a run or importing cryptographic libraries."""
    root = Path(project_root).resolve()
    source = _project_path(root, config_path, "configs")
    config = load_config(source)
    registry_path = root / "experiments" / "registry.yaml"
    if not registry_path.is_file():
        registry_path = root / "configs" / "registry" / "experiments.yaml"
    registry = load_experiment_registry(registry_path)
    entry = registry.get(config["experiment_id"])
    if entry is None:
        raise ExperimentError("experiment_id is absent from the allowed registry")
    expected_config = resolve_within(root, entry["configuration"])
    if source != expected_config:
        raise ExperimentError("configuration path does not match the registered experiment")
    adapter_id = config["execution"].get("adapter")
    adapter = get_adapter(adapter_id) if isinstance(adapter_id, str) else None
    blockers: list[str] = []
    if adapter is None:
        blockers.append("adapter ausente ou não autorizado")
    inputs = []
    for artifact in config["input_artifacts"]:
        resolved = resolve_within(root, artifact["path"])
        exists = resolved.is_file()
        inputs.append({"path": artifact["path"], "exists": exists})
        if artifact.get("required", True) and not exists:
            blockers.append(f"artefato de entrada ausente: {artifact['path']}")
    executor_path = resolve_within(root, entry["executor"])
    if not executor_path.is_file():
        blockers.append("executor registrado ausente")
    return {
        "experiment_id": config["experiment_id"],
        "configuration_id": config["configuration_id"],
        "configuration": config,
        "config_hash": config_hash(config),
        "adapter": adapter_id,
        "adapter_allowed": adapter is not None,
        "dependencies": config["dependencies"],
        "input_artifacts": inputs,
        "expected_artifacts": entry["expected_artifacts"],
        "environment_required": "ambiente Python compatível com as dependências declaradas; detalhes efetivos são registrados no manifesto",
        "publication": config["publication"],
        "blockers": blockers,
        "execution_mode": config["execution"]["mode"],
        "supports_computational_resume": bool(adapter and adapter.supports_computational_resume),
        "experiment_directory": entry.get("experiment_directory"),
    }
