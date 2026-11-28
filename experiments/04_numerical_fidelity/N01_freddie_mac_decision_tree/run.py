"""Explicit runner for N01; execution is delegated to the registered adapter."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from fhe_credit.experiments.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["run", "--config", "experiments/04_numerical_fidelity/N01_freddie_mac_decision_tree/config.yaml", "--execute"]))
