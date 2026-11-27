"""Central executor for explicitly authorized, registered low-risk adapters."""
from __future__ import annotations

import contextlib
import copy
import hashlib
from pathlib import Path
from typing import Any, Iterator

from ..configuration import config_hash, validate_config
from ..experiment_registry import load_experiment_registry
from ..run_manifest import (
    build_manifest, complete_run, create_run, generate_run_id, load_manifest, sha256_file,
    resume_run, transition_run, verify_artifact_hashes, write_json_atomic,
)
from .adapters import get_adapter
from .artifacts import read_json, resolve_within, run_directory
from .errors import (
    AdapterNotAllowedError, ArtifactIntegrityError, ConcurrentRunError,
    ExecutionAuthorizationError, ExperimentError, ResumeNotSupportedError,
)
from .planning import build_plan
from .provenance import effective_code_provenance, environment_metadata, persistent_machine_id


@contextlib.contextmanager
def run_lock(directory: Path) -> Iterator[None]:
    """Take a non-blocking local advisory lock for a single run directory."""
    try:
        import fcntl
    except ImportError as error:  # pragma: no cover - non-POSIX fallback
        raise ConcurrentRunError("exclusive run locking is unavailable on this platform") from error
    lock_path = directory / ".run.lock"
    with lock_path.open("a+", encoding="utf-8") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ConcurrentRunError("another execution or resume holds this Run ID") from error
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def plan_config(config_path: str | Path, project_root: str | Path = ".") -> dict[str, Any]:
    return build_plan(config_path, project_root)


def _provenance(root: Path, state_directory: Path) -> tuple[str, dict[str, Any], dict[str, Any]]:
    machine = persistent_machine_id(state_directory)
    environment = environment_metadata()
    code = effective_code_provenance(root)
    return machine, environment, code


def resolve_experiment_results_root(root: Path, plan: dict[str, Any]) -> Path:
    """Derive new-run storage from a registered experiment directory only."""
    directory = resolve_within(root, plan["experiment_directory"])
    if not directory.is_dir():
        raise ArtifactIntegrityError("registered experiment directory does not exist")
    return directory / "results" / "runs"


def locate_run_results_root(run_id: str, project_root: str | Path) -> Path:
    """Locate one Run ID across legacy and registered unit directories without guessing."""
    root = Path(project_root).resolve()
    registry_path = root / "experiments" / "registry.yaml"
    if not registry_path.is_file():
        registry_path = root / "configs" / "registry" / "experiments.yaml"
    candidates = [root / "results" / "runs"]
    for entry in load_experiment_registry(registry_path).values():
        directory = entry.get("experiment_directory")
        if directory:
            candidates.append(resolve_within(root, directory) / "results" / "runs")
    matches = [candidate for candidate in candidates if (candidate / run_id).is_dir()]
    if len(matches) != 1:
        raise ArtifactIntegrityError("Run ID not found or ambiguous across authorized result directories")
    return matches[0]


def execute_config(
    config_path: str | Path,
    *,
    project_root: str | Path = ".",
    results_root: str | Path | None = None,
    state_directory: str | Path | None = None,
    authorized: bool = False,
) -> dict[str, Any]:
    """Run only after an explicit caller authorization; never dispatches YAML code."""
    if not authorized:
        raise ExecutionAuthorizationError("execution requires explicit --execute authorization")
    root = Path(project_root).resolve()
    plan = build_plan(config_path, root)
    if plan["execution_mode"] != "execute":
        raise ExecutionAuthorizationError("configuration is not marked for explicit execute mode")
    if plan["blockers"]:
        raise ExperimentError("execution blocked: " + "; ".join(plan["blockers"]))
    adapter = get_adapter(plan["adapter"])
    if adapter is None:
        raise AdapterNotAllowedError("adapter is not registered")
    output_root = Path(results_root).resolve() if results_root else (
        resolve_experiment_results_root(root, plan) if plan.get("experiment_directory") else root / "results" / "runs"
    )
    local_state = Path(state_directory).resolve() if state_directory else root / "state"
    machine, environment, code = _provenance(root, local_state)
    input_hashes = {item["path"]: sha256_file(resolve_within(root, item["path"])) for item in plan["configuration"]["input_artifacts"]}
    dataset_hash = hashlib.sha256("".join(f"{path}:{digest}\n" for path, digest in sorted(input_hashes.items())).encode("utf-8")).hexdigest() if input_hashes else None
    run_id = generate_run_id()
    required = sorted(set(["effective_config.json", "environment.json", *plan["expected_artifacts"]]))
    manifest = build_manifest(
        run_id=run_id, experiment_id=plan["experiment_id"], configuration_id=plan["configuration_id"],
        config_hash=plan["config_hash"], seed=plan["configuration"]["parameters"].get("seed"),
        visibility=plan["publication"], machine_id_value=machine,
        hardware_fingerprint=environment["hardware"], environment_id="environment-" + environment["environment_hash"][:16],
        environment_hash=environment["environment_hash"], effective_code_hash=code["effective_code_hash"],
        effective_code_files=code["files"], dataset_hash=dataset_hash, input_artifact_hashes=input_hashes,
    )
    manifest["required_artifacts"] = required
    directory = create_run(output_root, manifest)
    write_json_atomic(directory / "effective_config.json", plan["configuration"])
    write_json_atomic(directory / "environment.json", environment)
    adapter_config = copy.deepcopy(plan["configuration"])
    adapter_config["_resolved_input_paths"] = {
        item.get("role", item["path"]): str(resolve_within(root, item["path"]))
        for item in plan["configuration"]["input_artifacts"]
    }
    with run_lock(directory):
        running = transition_run(directory, "RUNNING")
        try:
            adapter.run(adapter_config, directory)
            completed = complete_run(directory, running)
        except KeyboardInterrupt:
            transition_run(directory, "INTERRUPTED", reason="KeyboardInterrupt")
            raise
        except Exception as error:
            transition_run(directory, "FAILED", reason=type(error).__name__)
            raise ExperimentError("adapter execution failed; see manifest status for the sanitized error type") from error
    return {"run_id": run_id, "run_directory": str(directory), "manifest": completed}


def analyze_run(run_id: str, *, results_root: str | Path = "results/runs") -> dict[str, Any]:
    """Read existing artifacts and hashes without writing or triggering computation."""
    directory = run_directory(results_root, run_id)
    manifest = load_manifest(directory)
    metrics_path = directory / "metrics.json"
    metrics = read_json(metrics_path) if metrics_path.is_file() else None
    available = sorted(path.name for path in directory.iterdir() if path.name != ".run.lock")
    missing = [name for name in manifest["required_artifacts"] if not (directory / name).is_file()]
    return {
        "run_id": run_id, "status": manifest["status"], "manifest": manifest,
        "effective_config": read_json(directory / "effective_config.json") if (directory / "effective_config.json").is_file() else None,
        "metrics": metrics, "available_artifacts": available, "missing_artifacts": missing,
        "artifact_hashes_valid": verify_artifact_hashes(directory, manifest),
    }


def status_run(run_id: str, *, results_root: str | Path = "results/runs") -> dict[str, Any]:
    directory = run_directory(results_root, run_id)
    manifest = load_manifest(directory)
    return {"run_id": run_id, "status": manifest["status"], "attempts": manifest["attempts"]}


def verify_run(run_id: str, *, results_root: str | Path = "results/runs") -> dict[str, Any]:
    directory = run_directory(results_root, run_id)
    manifest = load_manifest(directory)
    return {"run_id": run_id, "valid": verify_artifact_hashes(directory, manifest), "status": manifest["status"]}


def resume_config(
    run_id: str, *, project_root: str | Path = ".", results_root: str | Path = "results/runs", authorized: bool = False,
) -> dict[str, Any]:
    """Resume only adapters that declare real support; administrative state changes are separate."""
    if not authorized:
        raise ExecutionAuthorizationError("resume requires explicit --execute authorization")
    directory = run_directory(results_root, run_id)
    with run_lock(directory):
        manifest = load_manifest(directory)
        if manifest["status"] == "COMPLETED":
            raise ResumeNotSupportedError("completed runs cannot be resumed")
        if not verify_artifact_hashes(directory, manifest):
            raise ArtifactIntegrityError("recorded artifacts failed integrity verification")
        config = validate_config(read_json(directory / "effective_config.json"))
        if config_hash(config) != manifest["config_hash"]:
            raise ArtifactIntegrityError("effective configuration does not match manifest hash")
        adapter = get_adapter(config["execution"].get("adapter", ""))
        if adapter is None:
            raise AdapterNotAllowedError("stored adapter is not registered")
        if not adapter.supports_computational_resume:
            raise ResumeNotSupportedError("adapter does not declare computational resume support")
        root = Path(project_root).resolve()
        code = effective_code_provenance(root)
        if code["effective_code_hash"] != manifest["effective_code_hash"]:
            raise ArtifactIntegrityError("effective code hash changed; resume is unsafe")
        environment = environment_metadata()
        if environment["environment_hash"] != manifest["environment_hash"]:
            raise ArtifactIntegrityError("environment hash changed; resume is unsafe")
        running = resume_run(directory)
        try:
            adapter.run(config, directory)
            return complete_run(directory, running)
        except KeyboardInterrupt:
            transition_run(directory, "INTERRUPTED", reason="KeyboardInterrupt")
            raise
        except Exception as error:
            transition_run(directory, "FAILED", reason=type(error).__name__)
            raise ExperimentError("adapter resume failed") from error
