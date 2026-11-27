from pathlib import Path

from src.fhe_credit.experiments.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_lists_describes_validates_and_requires_execute(capsys):
    assert main(["--project-root", str(ROOT), "list"]) == 0
    assert "synthetic-executor-smoke" in capsys.readouterr().out
    assert main(["--project-root", str(ROOT), "describe", "--experiment-id", "synthetic-executor-smoke"]) == 0
    assert main(["--project-root", str(ROOT), "validate", "--config", "configs/experiments/synthetic_executor_smoke.yaml"]) == 0
    assert main(["--project-root", str(ROOT), "run", "--config", "configs/experiments/synthetic_executor_smoke.yaml"]) == 2
