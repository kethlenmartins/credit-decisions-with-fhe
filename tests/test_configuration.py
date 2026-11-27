from pathlib import Path

import pytest

from src.fhe_credit.configuration import ConfigValidationError, config_hash, load_config, validate_config
from src.fhe_credit.experiment_registry import load_experiment_registry


ROOT = Path(__file__).resolve().parents[1]


def test_historical_configuration_loads_and_hashes_deterministically():
    config = load_config(ROOT / "configs/experiments/historical_fhe_smoke_synthetic.yaml")
    assert config["scientific_status"] == "HISTORICAL"
    assert config["execution"]["mode"] == "execute"
    assert config["execution"]["adapter"] == "legacy-report-import-v1"
    assert config_hash(config) == config_hash(config)


def test_configuration_rejects_unsafe_artifact_path():
    config = {
        "schema_version": "1.0", "experiment_id": "valid-experiment", "configuration_id": "valid-config",
        "description": "Synthetic validation configuration", "scientific_status": "EXPLORATORY",
        "dependencies": [], "parameters": {}, "input_artifacts": [{"path": "../secret.csv"}],
        "execution": {"mode": "analyze"}, "publication": "PRIVATE",
    }
    with pytest.raises(ConfigValidationError, match="inside the repository"):
        validate_config(config)


def test_registry_is_loadable_and_references_historical_entry():
    registry = load_experiment_registry(ROOT / "configs/registry/experiments.yaml")
    assert registry["historical-fhe-smoke-synthetic"]["status"] == "HISTORICAL"
