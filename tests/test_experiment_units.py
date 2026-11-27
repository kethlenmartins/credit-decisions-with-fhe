from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat", reason="dependência opcional de notebooks")
NotebookClient = pytest.importorskip("nbclient", reason="dependência opcional de notebooks").NotebookClient

from src.fhe_credit.experiment_registry import load_experiment_registry
from src.fhe_credit.experiments.planning import build_plan


ROOT = Path(__file__).resolve().parents[1]


def test_active_registry_contains_historical_units_and_legacy_registry_redirects():
    active = load_experiment_registry(ROOT / "experiments/registry.yaml")
    compatibility = load_experiment_registry(ROOT / "configs/registry/experiments.yaml")
    assert "hist01-uci-plaintext-baseline" in active
    assert "historical-fhe-smoke-synthetic" in active
    assert "historical-fhe-uci-smoke" in active
    assert compatibility == active


def test_hist01_plan_resolves_its_local_experiment_unit():
    plan = build_plan(ROOT / "experiments/historical/HIST01_uci_plaintext_baseline/config.yaml", ROOT)
    assert plan["experiment_directory"] == "experiments/historical/HIST01_uci_plaintext_baseline"
    assert plan["adapter"] == "hist01-uci-plaintext-baseline-v1"


def test_historical_notebooks_are_valid_and_execute_without_experiment_run(monkeypatch):
    monkeypatch.delenv("HIST01_RUN_ID", raising=False)
    monkeypatch.delenv("HIST02_RUN_ID", raising=False)
    monkeypatch.delenv("HIST03_RUN_ID", raising=False)
    paths = [
        ROOT / "experiments/00_research_overview.ipynb",
        ROOT / "experiments/templates/experiment_template.ipynb",
        ROOT / "experiments/historical/HIST01_uci_plaintext_baseline/experiment.ipynb",
        ROOT / "experiments/historical/HIST02_fhe_synthetic_smoke/experiment.ipynb",
        ROOT / "experiments/historical/HIST03_fhe_uci_smoke/experiment.ipynb",
    ]
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(notebook, timeout=60, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
