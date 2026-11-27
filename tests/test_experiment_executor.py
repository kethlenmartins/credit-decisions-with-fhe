import json
import shutil
from pathlib import Path

import pytest
import yaml

from src.fhe_credit.experiments import adapters
from src.fhe_credit.experiments.errors import (
    ArtifactIntegrityError,
    ExecutionAuthorizationError,
    ExperimentError,
    ResumeNotSupportedError,
)
from src.fhe_credit.experiments.executor import (
    analyze_run,
    execute_config,
    resume_config,
    run_lock,
    verify_run,
)
from src.fhe_credit.experiments.artifacts import run_directory


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path):
    shutil.copytree(ROOT / "configs", tmp_path / "configs")
    (tmp_path / "experiments").mkdir()
    shutil.copy(ROOT / "experiments/registry.yaml", tmp_path / "experiments/registry.yaml")
    adapter_path = tmp_path / "src/fhe_credit/experiments/adapters.py"
    adapter_path.parent.mkdir(parents=True)
    adapter_path.write_text("# registry path placeholder\n", encoding="utf-8")
    return tmp_path


def execute(project, tmp_path):
    return execute_config(
        project / "configs/experiments/synthetic_executor_smoke.yaml",
        project_root=project, results_root=tmp_path / "runs", state_directory=tmp_path / "state", authorized=True,
    )


def test_execution_requires_explicit_authorization(project, tmp_path):
    with pytest.raises(ExecutionAuthorizationError):
        execute_config(project / "configs/experiments/synthetic_executor_smoke.yaml", project_root=project, authorized=False)


def test_synthetic_execution_persists_complete_verifiable_run(project, tmp_path):
    result = execute(project, tmp_path)
    directory = Path(result["run_directory"])
    assert result["manifest"]["status"] == "COMPLETED"
    assert (directory / "effective_config.json").is_file()
    assert (directory / "environment.json").is_file()
    assert json.loads((directory / "metrics.json").read_text(encoding="utf-8"))["scope"].startswith("synthetic")
    assert verify_run(result["run_id"], results_root=tmp_path / "runs")["valid"] is True


def test_analyze_is_read_only_and_detects_tampering(project, tmp_path):
    result = execute(project, tmp_path)
    directory = Path(result["run_directory"])
    before = (directory / "manifest.json").read_bytes()
    analysis = analyze_run(result["run_id"], results_root=tmp_path / "runs")
    assert analysis["artifact_hashes_valid"] is True
    assert (directory / "manifest.json").read_bytes() == before
    (directory / "metrics.json").write_text('{"tampered": true}\n', encoding="utf-8")
    assert analyze_run(result["run_id"], results_root=tmp_path / "runs")["artifact_hashes_valid"] is False


def test_run_directory_rejects_unsafe_identifier(tmp_path):
    with pytest.raises(ArtifactIntegrityError):
        run_directory(tmp_path, "run-../escape")


def test_failed_adapter_records_failed_status_and_resume_can_be_real(project, tmp_path, monkeypatch):
    config_path = project / "configs/experiments/synthetic_executor_smoke.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["execution"]["adapter"] = "test-resumable"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    class FailsThenCompletes:
        identifier = "test-resumable"
        supports_computational_resume = True

        def __init__(self): self.calls = 0

        def run(self, config, output_directory):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("synthetic failure")
            (output_directory / "metrics.json").write_text("{}\n", encoding="utf-8")
            (output_directory / "adapter_output.json").write_text("{}\n", encoding="utf-8")
            return ["metrics.json", "adapter_output.json"]

    adapter = FailsThenCompletes()
    monkeypatch.setitem(adapters.ADAPTERS, adapter.identifier, adapter)
    with pytest.raises(ExperimentError):
        execute_config(config_path, project_root=project, results_root=tmp_path / "runs", state_directory=tmp_path / "state", authorized=True)
    directory = next((tmp_path / "runs").iterdir())
    failed = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    assert failed["status"] == "FAILED"
    completed = resume_config(failed["run_id"], project_root=project, results_root=tmp_path / "runs", authorized=True)
    assert completed["status"] == "COMPLETED"


def test_lock_prevents_concurrent_access(project, tmp_path):
    result = execute(project, tmp_path)
    directory = Path(result["run_directory"])
    with run_lock(directory):
        with pytest.raises(Exception, match="holds this Run ID"):
            with run_lock(directory):
                pass


def test_unknown_adapter_is_rejected_at_execution(project, tmp_path):
    config_path = project / "configs/experiments/synthetic_executor_smoke.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    payload["execution"]["adapter"] = "unknown-adapter"
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ExperimentError, match="blocked"):
        execute_config(config_path, project_root=project, results_root=tmp_path / "runs", authorized=True)


def test_keyboard_interrupt_is_recorded_without_exposing_error(project, tmp_path, monkeypatch):
    config_path = project / "configs/experiments/synthetic_executor_smoke.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    payload["execution"]["adapter"] = "test-interrupt"
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    class InterruptingAdapter:
        identifier = "test-interrupt"
        supports_computational_resume = False

        def run(self, config, output_directory):
            raise KeyboardInterrupt()

    monkeypatch.setitem(adapters.ADAPTERS, "test-interrupt", InterruptingAdapter())
    with pytest.raises(KeyboardInterrupt):
        execute_config(config_path, project_root=project, results_root=tmp_path / "runs", state_directory=tmp_path / "state", authorized=True)
    directory = next((tmp_path / "runs").iterdir())
    assert json.loads((directory / "manifest.json").read_text(encoding="utf-8"))["status"] == "INTERRUPTED"


def test_non_resumable_adapter_rejects_computational_resume(project, tmp_path, monkeypatch):
    config_path = project / "configs/experiments/synthetic_executor_smoke.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    payload["execution"]["adapter"] = "test-no-resume"
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    class FailingAdapter:
        identifier = "test-no-resume"
        supports_computational_resume = False

        def run(self, config, output_directory):
            raise RuntimeError("synthetic failure")

    monkeypatch.setitem(adapters.ADAPTERS, "test-no-resume", FailingAdapter())
    with pytest.raises(ExperimentError):
        execute_config(config_path, project_root=project, results_root=tmp_path / "runs", state_directory=tmp_path / "state", authorized=True)
    run_id = json.loads((next((tmp_path / "runs").iterdir()) / "manifest.json").read_text(encoding="utf-8"))["run_id"]
    with pytest.raises(ResumeNotSupportedError):
        resume_config(run_id, project_root=project, results_root=tmp_path / "runs", authorized=True)
