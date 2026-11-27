import shutil
from pathlib import Path

import pytest
import yaml

from src.fhe_credit.experiments.artifacts import resolve_within
from src.fhe_credit.experiments.errors import ArtifactIntegrityError, ExperimentError
from src.fhe_credit.experiments.planning import build_plan


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


def test_plan_is_read_only_and_reports_synthetic_adapter(project):
    config = project / "configs/experiments/synthetic_executor_smoke.yaml"
    before = sorted(path.relative_to(project).as_posix() for path in project.rglob("*"))
    plan = build_plan(config, project)
    after = sorted(path.relative_to(project).as_posix() for path in project.rglob("*"))
    assert before == after
    assert plan["adapter_allowed"] is True
    assert plan["blockers"] == []
    assert plan["expected_artifacts"][-1] == "adapter_output.json"


def test_unknown_adapter_blocks_execution_plan(project):
    config_path = project / "configs/experiments/synthetic_executor_smoke.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    payload["execution"]["adapter"] = "unknown-adapter"
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    assert "adapter ausente ou não autorizado" in build_plan(config_path, project)["blockers"]


def test_symlink_input_escape_is_rejected(project, tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = project / "link.txt"
    link.symlink_to(outside)
    config_path = project / "configs/experiments/synthetic_executor_smoke.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    payload["input_artifacts"] = [{"path": "link.txt"}]
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError):
        build_plan(config_path, project)


def test_configuration_must_match_registered_path(project):
    copied = project / "configs/experiments/copied.yaml"
    shutil.copy(project / "configs/experiments/synthetic_executor_smoke.yaml", copied)
    with pytest.raises(ExperimentError, match="does not match"):
        build_plan(copied, project)
