"""Privacy-preserving local provenance for code, machine, and environment."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import uuid
from importlib import metadata
from pathlib import Path
from typing import Any


def _canonical_hash(payload: Any) -> str:
    value = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def persistent_machine_id(state_directory: str | Path) -> str:
    """Read or atomically create a local random UUID; no host/user/MAC data is used."""
    directory = Path(state_directory)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        directory.chmod(0o700)
    except OSError:
        pass
    path = directory / "machine_id"
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        if value.startswith("machine-") and len(value) == len("machine-") + 32:
            return value
        raise ValueError("local machine_id file has an invalid format")
    value = "machine-" + uuid.uuid4().hex
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(value + "\n")
        try:
            path.chmod(0o600)
        except OSError:
            pass
    except FileExistsError:
        return persistent_machine_id(directory)
    return value


def _cpu_model() -> str | None:
    path = Path("/proc/cpuinfo")
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lower().startswith("model name"):
            return line.split(":", 1)[1].strip()
    return None


def _physical_cores() -> int | None:
    path = Path("/proc/cpuinfo")
    if not path.exists():
        return None
    cores: set[tuple[str, str]] = set()
    physical = core = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines() + [""]:
        if not line.strip():
            if physical is not None and core is not None:
                cores.add((physical, core))
            physical = core = None
        elif line.startswith("physical id"):
            physical = line.split(":", 1)[1].strip()
        elif line.startswith("core id"):
            core = line.split(":", 1)[1].strip()
    return len(cores) or None


def _memory_bytes() -> int | None:
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (AttributeError, OSError, ValueError):
        return None
    return int(pages * page_size)


def environment_metadata() -> dict[str, Any]:
    """Collect selected reproducibility metadata, never arbitrary environment variables."""
    packages = sorted(
        ({"name": distribution.metadata["Name"].lower(), "version": distribution.version}
         for distribution in metadata.distributions() if distribution.metadata.get("Name")),
        key=lambda item: item["name"],
    )
    thread_variables = {key: os.environ[key] for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS") if key in os.environ}
    payload = {
        "python": {"version": platform.python_version(), "implementation": platform.python_implementation()},
        "platform": {"system": platform.system(), "release": platform.release(), "architecture": platform.machine()},
        "hardware": {"cpu_model": _cpu_model(), "logical_cores": os.cpu_count(), "physical_cores": _physical_cores(), "memory_bytes_installed": _memory_bytes()},
        "thread_configuration": thread_variables,
        "packages": packages,
    }
    payload["environment_hash"] = _canonical_hash(payload)
    return payload


def effective_code_provenance(project_root: str | Path) -> dict[str, Any]:
    """Hash only an explicit, safe subset of relevant source and configuration files."""
    root = Path(project_root).resolve()
    allowed = (root / "src" / "fhe_credit", root / "configs")
    direct = (root / "requirements-base.txt", root / "requirements-fhe.txt", root / "requirements-fhe-lock.txt")
    candidates: list[Path] = []
    for directory in allowed:
        if directory.exists():
            candidates.extend(path for path in directory.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    candidates.extend(path for path in direct if path.is_file())
    files = []
    for path in sorted({item.resolve() for item in candidates}):
        if not any(path == base or base in path.parents for base in allowed) and path not in direct:
            continue
        relative = path.relative_to(root).as_posix()
        files.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    payload = {"scope": "src/fhe_credit, configs and declared requirements files only; excludes datasets, results, keys, environments and files outside this scope.", "files": files}
    payload["effective_code_hash"] = _canonical_hash(payload)
    return payload
