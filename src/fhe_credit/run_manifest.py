"""Immutable-per-run manifest utilities for reproducible experimental infrastructure."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST_SCHEMA_VERSION = "1.0"
RUN_STATES = frozenset({"CREATED", "RUNNING", "COMPLETED", "FAILED", "INTERRUPTED"})
TERMINAL_STATES = frozenset({"COMPLETED", "FAILED", "INTERRUPTED"})
VISIBILITIES = frozenset({"PRIVATE", "REVIEW_REQUIRED", "PUBLIC_APPROVED"})


class ManifestValidationError(ValueError):
    """Raised when a manifest would not be portable or internally consistent."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def generate_run_id() -> str:
    """Generate a sortable, globally unique identifier without host information."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"run-{stamp}-{uuid.uuid4().hex}"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_value(arguments: list[str]) -> str | None:
    try:
        result = subprocess.run(["git", *arguments], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def code_provenance() -> dict[str, Any]:
    commit = _git_value(["rev-parse", "HEAD"])
    dirty = _git_value(["status", "--porcelain"])
    unavailable: dict[str, str] = {}
    if commit is None:
        unavailable["git_commit"] = "Git commit indisponível no diretório de execução."
    if dirty is None:
        unavailable["git_dirty"] = "Estado Git indisponível no diretório de execução."
    unavailable["effective_code_hash"] = (
        "Não capturado nesta etapa; um commit não representa alterações locais. "
        "Etapa futura deve gerar snapshot filtrado e hash do código efetivo."
    )
    return {"git_commit": commit, "git_dirty": None if dirty is None else bool(dirty), "unavailable": unavailable}


def machine_id() -> str:
    """Return a non-personal platform fingerprint; hostname and account are excluded."""
    descriptor = "|".join((platform.system(), platform.release(), platform.machine(), platform.python_implementation()))
    return "machine-" + hashlib.sha256(descriptor.encode("utf-8")).hexdigest()[:16]


def build_manifest(
    *,
    run_id: str,
    experiment_id: str,
    configuration_id: str,
    config_hash: str,
    seed: int | None = None,
    parent_run_id: str | None = None,
    visibility: str = "PRIVATE",
    machine_id_value: str | None = None,
    hardware_fingerprint: dict[str, Any] | None = None,
    environment_id: str | None = None,
    environment_hash: str | None = None,
    effective_code_hash: str | None = None,
    effective_code_files: list[dict[str, str]] | None = None,
    dataset_hash: str | None = None,
    input_artifact_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    if visibility not in VISIBILITIES:
        raise ManifestValidationError("visibility is not allowed")
    provenance = code_provenance()
    unavailable = {
        **provenance["unavailable"],
        "dataset_hash": "Não aplicável ou indisponível antes da execução.",
        "model_hash": "Não aplicável ou indisponível antes da execução.",
        "environment_hash": "Não disponível para esta execução.",
    }
    if environment_hash is not None:
        unavailable.pop("environment_hash", None)
    if effective_code_hash is not None:
        unavailable.pop("effective_code_hash", None)
    if dataset_hash is not None:
        unavailable.pop("dataset_hash", None)
    created = utc_now()
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "configuration_id": configuration_id,
        "machine_id": machine_id_value or machine_id(),
        "hardware_fingerprint": hardware_fingerprint or {},
        "environment_id": environment_id or "environment-unavailable",
        "parent_run_id": parent_run_id,
        "git_commit": provenance["git_commit"],
        "git_dirty": provenance["git_dirty"],
        "config_hash": config_hash,
        "dataset_hash": dataset_hash,
        "input_artifact_hashes": input_artifact_hashes or {},
        "model_hash": None,
        "environment_hash": environment_hash,
        "effective_code_hash": effective_code_hash,
        "effective_code_files": effective_code_files or [],
        "seed": seed,
        "started_at": None,
        "finished_at": None,
        "status": "CREATED",
        "artifact_hashes": {},
        "required_artifacts": [],
        "visibility": visibility,
        "unavailable_fields": unavailable,
        "attempts": [{"number": 1, "status": "CREATED", "at": created}],
    }
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema_version", "run_id", "experiment_id", "configuration_id", "machine_id", "hardware_fingerprint", "environment_id",
        "parent_run_id", "git_commit", "git_dirty", "config_hash", "dataset_hash", "model_hash",
        "environment_hash", "effective_code_hash", "effective_code_files", "input_artifact_hashes", "seed", "started_at", "finished_at", "status", "artifact_hashes",
        "required_artifacts", "visibility", "unavailable_fields", "attempts",
    }
    if not isinstance(manifest, dict) or required - set(manifest):
        raise ManifestValidationError("manifest is missing required fields")
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise ManifestValidationError("unsupported manifest schema_version")
    if manifest["status"] not in RUN_STATES:
        raise ManifestValidationError("invalid manifest status")
    if manifest["visibility"] not in VISIBILITIES:
        raise ManifestValidationError("invalid manifest visibility")
    if not isinstance(manifest["artifact_hashes"], dict) or not isinstance(manifest["required_artifacts"], list):
        raise ManifestValidationError("artifact fields have invalid types")
    if not isinstance(manifest["unavailable_fields"], dict) or not isinstance(manifest["attempts"], list):
        raise ManifestValidationError("traceability fields have invalid types")
    if not isinstance(manifest["run_id"], str) or not manifest["run_id"].startswith("run-"):
        raise ManifestValidationError("run_id must use the run- prefix")
    if not isinstance(manifest["config_hash"], str) or len(manifest["config_hash"]) != 64:
        raise ManifestValidationError("config_hash must be a SHA-256 hexadecimal digest")
    if any(not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts for name in manifest["required_artifacts"]):
        raise ManifestValidationError("required artifact paths must be safe relative paths")
    if any(not isinstance(digest, str) or len(digest) != 64 for digest in manifest["artifact_hashes"].values()):
        raise ManifestValidationError("artifact hashes must be SHA-256 hexadecimal digests")
    if not isinstance(manifest["hardware_fingerprint"], dict) or not isinstance(manifest["effective_code_files"], list):
        raise ManifestValidationError("provenance fields have invalid types")
    if not isinstance(manifest["input_artifact_hashes"], dict):
        raise ManifestValidationError("input artifact hashes have invalid type")
    if manifest["status"] == "COMPLETED":
        absent = set(manifest["required_artifacts"]) - set(manifest["artifact_hashes"])
        if absent:
            raise ManifestValidationError("completed manifest has unhashed required artifacts")
        if not manifest["finished_at"]:
            raise ManifestValidationError("completed manifest requires finished_at")
    return manifest


def write_json_atomic(path: str | Path, payload: dict[str, Any]) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent, delete=False) as stream:
        json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, destination)
    return destination


def create_run_directory(results_root: str | Path, run_id: str) -> Path:
    root = Path(results_root).resolve()
    if Path(run_id).name != run_id:
        raise ManifestValidationError("run_id cannot contain a path")
    run_directory = root / run_id
    try:
        run_directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise FileExistsError(f"run directory already exists: {run_directory}") from error
    return run_directory


def create_run(results_root: str | Path, manifest: dict[str, Any]) -> Path:
    """Create an independent run directory and its initial manifest atomically enough for local use."""
    validate_manifest(manifest)
    run_directory = create_run_directory(results_root, manifest["run_id"])
    write_json_atomic(run_directory / "manifest.json", manifest)
    write_json_atomic(run_directory / "status.json", {"status": "CREATED", "updated_at": utc_now()})
    return run_directory


def load_manifest(run_directory: str | Path) -> dict[str, Any]:
    """Load and validate the persisted manifest for one existing run."""
    path = Path(run_directory) / "manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestValidationError(f"cannot load manifest: {error}") from error
    return validate_manifest(manifest)


def transition_run(run_directory: str | Path, status: str, *, reason: str | None = None) -> dict[str, Any]:
    """Persist a non-completed state transition while retaining the same Run ID."""
    if status not in {"RUNNING", "FAILED", "INTERRUPTED"}:
        raise ManifestValidationError("transition_run only accepts RUNNING, FAILED or INTERRUPTED")
    directory = Path(run_directory)
    manifest = load_manifest(directory)
    if manifest["status"] == "COMPLETED":
        raise ManifestValidationError("a completed run is immutable")
    timestamp = utc_now()
    event: dict[str, Any] = {"number": len(manifest["attempts"]) + 1, "status": status, "at": timestamp}
    if reason:
        event["reason"] = reason
    updated = {**manifest, "status": status, "attempts": [*manifest["attempts"], event]}
    if status == "RUNNING" and updated["started_at"] is None:
        updated["started_at"] = timestamp
    if status == "RUNNING":
        updated["finished_at"] = None
    if status in TERMINAL_STATES:
        updated["finished_at"] = timestamp
    validate_manifest(updated)
    write_json_atomic(directory / "manifest.json", updated)
    write_json_atomic(directory / "status.json", {"status": status, "updated_at": timestamp})
    return updated


def resume_run(run_directory: str | Path) -> dict[str, Any]:
    """Resume only an interrupted or failed run, retaining its Run ID and attempt history."""
    manifest = load_manifest(run_directory)
    if manifest["status"] not in {"FAILED", "INTERRUPTED"}:
        raise ManifestValidationError("only FAILED or INTERRUPTED runs can be resumed")
    return transition_run(run_directory, "RUNNING", reason="resumed")


def verify_artifact_hashes(run_directory: str | Path, manifest: dict[str, Any] | None = None) -> bool:
    """Verify every recorded artifact hash without executing experimental code."""
    directory = Path(run_directory).resolve()
    manifest = load_manifest(directory) if manifest is None else validate_manifest(manifest)
    for relative_name, expected_hash in manifest["artifact_hashes"].items():
        artifact = (directory / relative_name).resolve()
        if directory not in artifact.parents or not artifact.is_file() or sha256_file(artifact) != expected_hash:
            return False
    return True


def complete_run(run_directory: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Mark completion only after every declared required artifact exists and is hashed."""
    directory = Path(run_directory).resolve()
    if manifest["status"] != "RUNNING":
        raise ManifestValidationError("only a RUNNING run can be completed")
    hashes: dict[str, str] = {}
    for relative_name in manifest["required_artifacts"]:
        artifact = (directory / relative_name).resolve()
        if directory not in artifact.parents or not artifact.is_file():
            raise ManifestValidationError(f"required artifact missing or unsafe: {relative_name}")
        hashes[relative_name] = sha256_file(artifact)
    updated = {**manifest, "artifact_hashes": hashes, "status": "COMPLETED", "finished_at": utc_now()}
    updated["attempts"] = [*manifest["attempts"], {"number": len(manifest["attempts"]) + 1, "status": "COMPLETED", "at": updated["finished_at"]}]
    validate_manifest(updated)
    write_json_atomic(directory / "manifest.json", updated)
    write_json_atomic(directory / "status.json", {"status": "COMPLETED", "updated_at": updated["finished_at"]})
    return updated
