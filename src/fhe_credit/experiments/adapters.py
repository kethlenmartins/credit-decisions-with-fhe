"""Explicitly registered, dependency-light adapters. No YAML-driven imports occur here."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from ..run_manifest import write_json_atomic


class Adapter(Protocol):
    identifier: str
    supports_computational_resume: bool

    def run(self, config: dict[str, Any], output_directory: Path) -> list[str]: ...


@dataclass(frozen=True)
class SyntheticDecisionStabilityAdapter:
    """Infrastructure-only deterministic perturbation check; it has no FHE semantics."""

    identifier: str = "synthetic-decision-stability-v1"
    supports_computational_resume: bool = False

    def run(self, config: dict[str, Any], output_directory: Path) -> list[str]:
        parameters = config["parameters"]
        seed = parameters.get("seed")
        threshold = parameters.get("threshold")
        sample_size = parameters.get("sample_size")
        if not isinstance(seed, int) or not isinstance(threshold, (int, float)) or not isinstance(sample_size, int):
            raise ValueError("synthetic adapter requires integer seed/sample_size and numeric threshold")
        if not 0 < float(threshold) < 1 or not 1 <= sample_size <= 10_000:
            raise ValueError("synthetic adapter parameters are out of the allowed infrastructure range")
        rng = random.Random(seed)
        baseline = [round(rng.uniform(0.01, 0.99), 8) for _ in range(sample_size)]
        perturbed = [round(min(1.0, max(0.0, value + rng.uniform(-0.015, 0.015))), 8) for value in baseline]
        errors = [abs(left - right) for left, right in zip(baseline, perturbed)]
        classes_equal = [(left <= threshold) == (right <= threshold) for left, right in zip(baseline, perturbed)]
        metrics = {
            "scope": "synthetic infrastructure validation only; not credit, FHE, CKKS, TFHE, or policy evidence",
            "sample_size": sample_size,
            "threshold_illustrative": float(threshold),
            "mae": sum(errors) / len(errors),
            "rmse": math.sqrt(sum(error * error for error in errors) / len(errors)),
            "max_absolute_error": max(errors),
            "class_agreement": sum(classes_equal) / len(classes_equal),
        }
        write_json_atomic(output_directory / "metrics.json", metrics)
        write_json_atomic(output_directory / "adapter_output.json", {"baseline": baseline, "perturbed": perturbed, "note": "synthetic vectors for executor validation only"})
        return ["metrics.json", "adapter_output.json"]


@dataclass(frozen=True)
class HistoricalUciPlaintextBaselineAdapter:
    """Faithful isolated implementation of the historical 01_baseline.py behavior."""

    identifier: str = "hist01-uci-plaintext-baseline-v1"
    supports_computational_resume: bool = False

    def run(self, config: dict[str, Any], output_directory: Path) -> list[str]:
        import hashlib

        import pandas as pd
        from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
        from sklearn.model_selection import train_test_split
        from sklearn.tree import DecisionTreeClassifier

        from ..policies import cutoff

        parameters = config["parameters"]
        resolved_inputs = config.get("_resolved_input_paths", {})
        features = pd.read_csv(resolved_inputs.get("features", Path(parameters["data_root"]) / parameters["features_file"]))
        target = pd.read_csv(resolved_inputs.get("target", Path(parameters["data_root"]) / parameters["target_file"])).iloc[:, 0].astype(int)
        selected = features.select_dtypes(include="number").drop(columns=parameters["drop_columns"], errors="ignore")
        split = parameters["split"]
        seed = parameters["seed"]
        X_train, X_hold, y_train, y_hold = train_test_split(selected, target, test_size=split["first_test_size"], stratify=target, random_state=seed)
        X_val, X_test, y_val, y_test = train_test_split(X_hold, y_hold, test_size=split["second_test_size"], stratify=y_hold, random_state=seed)
        model_parameters = parameters["model"]
        model = DecisionTreeClassifier(max_depth=model_parameters["max_depth"], min_samples_leaf=model_parameters["min_samples_leaf"], random_state=model_parameters["random_state"])
        model.fit(X_train, y_train)
        scores = model.predict_proba(X_test)[:, 1]
        threshold = parameters["policy"]["threshold"]
        metrics = {
            "scope": "historical UCI plaintext baseline; not Freddie Mac, FHE, or production underwriting",
            "n_train": len(X_train), "n_validation": len(X_val), "n_test": len(X_test),
            "roc_auc": roc_auc_score(y_test, scores), "average_precision": average_precision_score(y_test, scores),
            "brier": brier_score_loss(y_test, scores), "approval_rate_at_0.2": float(cutoff(scores, threshold).mean()),
        }
        split_hash = lambda index: hashlib.sha256(",".join(map(str, index.tolist())).encode("utf-8")).hexdigest()
        split_summary = {"feature_names": list(selected.columns), "feature_count": len(selected.columns), "train_index_hash": split_hash(X_train.index), "validation_index_hash": split_hash(X_val.index), "test_index_hash": split_hash(X_test.index), "model_parameters": model.get_params(), "seed": seed, "historical_script": "experiments/01_baseline.py"}
        predictions = pd.DataFrame({"y_true": y_test.to_numpy(), "score": scores, "approved_at_0_2": cutoff(scores, threshold)})
        write_json_atomic(output_directory / "metrics.json", metrics)
        write_json_atomic(output_directory / "split_summary.json", split_summary)
        predictions.to_csv(output_directory / "predictions.csv", index=False)
        return ["metrics.json", "split_summary.json", "predictions.csv"]


@dataclass(frozen=True)
class LegacyReportImportAdapter:
    """Import a legacy JSON report without running its historical experiment."""

    identifier: str = "legacy-report-import-v1"
    supports_computational_resume: bool = False

    def run(self, config: dict[str, Any], output_directory: Path) -> list[str]:
        import hashlib
        import json

        source = Path(config["_resolved_input_paths"]["legacy_report"])
        raw = source.read_bytes()
        report = json.loads(raw.decode("utf-8"))
        write_json_atomic(output_directory / "imported_report.json", report)
        write_json_atomic(output_directory / "import_record.json", {
            "kind": "legacy_artifact_import",
            "source_path": str(config["input_artifacts"][0]["path"]),
            "imported_sha256": hashlib.sha256(raw).hexdigest(),
            "hash_semantics": "calculated during import; not recorded by the historical execution",
            "available_metadata": sorted(report.keys()) if isinstance(report, dict) else [],
            "missing_metadata": config["parameters"]["known_missing_metadata"],
            "provenance_limitations": config["parameters"]["provenance_limitations"],
        })
        return ["imported_report.json", "import_record.json"]


ADAPTERS: dict[str, Adapter] = {
    SyntheticDecisionStabilityAdapter.identifier: SyntheticDecisionStabilityAdapter(),
    HistoricalUciPlaintextBaselineAdapter.identifier: HistoricalUciPlaintextBaselineAdapter(),
    LegacyReportImportAdapter.identifier: LegacyReportImportAdapter(),
}


def get_adapter(identifier: str) -> Adapter | None:
    return ADAPTERS.get(identifier)
