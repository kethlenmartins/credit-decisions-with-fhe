"""Utilities for structured, local experimental reports."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


def compare_outputs(clear: Any, simulated: Any, encrypted: Any) -> dict[str, Any]:
    """Compare paired outputs without assigning probability semantics to them."""
    clear_array = np.asarray(clear)
    simulated_array = np.asarray(simulated)
    encrypted_array = np.asarray(encrypted)
    if clear_array.shape != simulated_array.shape or clear_array.shape != encrypted_array.shape:
        raise ValueError("all outputs must have the same shape")
    return {
        "shape": list(clear_array.shape),
        "dtype_clear": str(clear_array.dtype),
        "dtype_simulated": str(simulated_array.dtype),
        "dtype_encrypted": str(encrypted_array.dtype),
        "clear_equals_simulated": bool(np.array_equal(clear_array, simulated_array)),
        "clear_equals_encrypted": bool(np.array_equal(clear_array, encrypted_array)),
        "simulated_equals_encrypted": bool(np.array_equal(simulated_array, encrypted_array)),
        "different_clear_simulated": int(np.count_nonzero(clear_array != simulated_array)),
        "different_clear_encrypted": int(np.count_nonzero(clear_array != encrypted_array)),
        "different_simulated_encrypted": int(np.count_nonzero(simulated_array != encrypted_array)),
    }


def write_report(output_dir: Path, stem: str, metadata: dict[str, Any], timings: dict[str, Any], comparison: dict[str, Any]) -> tuple[Path, Path]:
    """Persist JSON metadata and one-row CSV summary for a completed experiment."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {"metadata": metadata, "timings_seconds": timings, "comparison": comparison}
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    row = {**{f"metadata.{key}": value for key, value in metadata.items()}, **{f"timing.{key}": value for key, value in timings.items()}, **{f"comparison.{key}": value for key, value in comparison.items()}}
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    return json_path, csv_path
