"""Constrained local artifact access used by executor operations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ArtifactIntegrityError


def resolve_within(root: str | Path, candidate: str | Path) -> Path:
    """Resolve a path and reject absolute, traversal, and symlink escapes."""
    base = Path(root).resolve()
    raw = Path(candidate)
    if raw.is_absolute() or ".." in raw.parts:
        raise ArtifactIntegrityError("path must be relative and remain in its authorized directory")
    resolved = (base / raw).resolve()
    if resolved != base and base not in resolved.parents:
        raise ArtifactIntegrityError("resolved path escapes its authorized directory")
    return resolved


def run_directory(results_root: str | Path, run_id: str) -> Path:
    if not run_id.startswith("run-") or Path(run_id).name != run_id:
        raise ArtifactIntegrityError("invalid run_id")
    directory = resolve_within(results_root, run_id)
    if not directory.is_dir():
        raise ArtifactIntegrityError("run directory does not exist")
    return directory


def read_json(path: str | Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactIntegrityError(f"cannot read JSON artifact: {error}") from error
    if not isinstance(payload, dict):
        raise ArtifactIntegrityError("JSON artifact must contain an object")
    return payload
