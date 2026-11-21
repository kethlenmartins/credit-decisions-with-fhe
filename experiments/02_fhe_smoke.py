"""Run one real FHE tree inference and persist its paired comparison locally."""
from __future__ import annotations

import platform
import sys
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np

from src.fhe_credit.experiment_results import compare_outputs, write_report

SEED = 42
N_BITS = 3


def cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def main() -> None:
    try:
        from concrete.ml.sklearn import DecisionTreeClassifier
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Concrete ML não está instalado. Use o ambiente .venv-fhe documentado antes de executar este experimento."
        ) from error

    rng = np.random.default_rng(SEED)
    features = rng.integers(0, 8, size=(100, 2)).astype(np.float32)
    target = (features[:, 0] + features[:, 1] > 7).astype(int)
    sample = features[:2]
    model = DecisionTreeClassifier(n_bits=N_BITS, max_depth=2, random_state=SEED)

    started = time.perf_counter()
    model.fit(features, target)
    training_seconds = time.perf_counter() - started
    started = time.perf_counter()
    model.compile(features)
    compilation_seconds = time.perf_counter() - started
    started = time.perf_counter()
    clear = model.predict(sample, fhe="disable")
    clear_seconds = time.perf_counter() - started
    started = time.perf_counter()
    simulated = model.predict(sample, fhe="simulate")
    simulation_seconds = time.perf_counter() - started
    # This stable estimator API exposes the complete encrypted round trip only.
    started = time.perf_counter()
    encrypted = model.predict(sample, fhe="execute")
    encrypted_total_seconds = time.perf_counter() - started

    comparison = compare_outputs(clear, simulated, encrypted)
    metadata = {
        "experiment": "02_fhe_smoke", "seed": SEED, "n_bits": N_BITS,
        "n_train_observations": int(len(features)), "n_inference_observations": int(len(sample)),
        "batch_size": int(len(sample)),
        "output_semantics": "class labels from predict; not probabilities or calibrated PD",
        "python_version": platform.python_version(), "platform": platform.platform(),
        "architecture": platform.machine(), "cpu_model": cpu_model(), "concrete_ml_version": version("concrete-ml"),
        "numpy_version": version("numpy"), "scikit_learn_version": version("scikit-learn"),
        "interpreter": sys.executable,
    }
    timings = {
        "training": training_seconds, "compilation": compilation_seconds,
        "quantized_clear_prediction": clear_seconds, "fhe_simulation_prediction": simulation_seconds,
        "fhe_execute_total_prediction": encrypted_total_seconds,
        "key_generation": "não mensurado: API de alto nível",
        "encryption": "não mensurado: API de alto nível",
        "homomorphic_evaluation": "não mensurado: API de alto nível",
        "decryption": "não mensurado: API de alto nível",
    }
    json_path, csv_path = write_report(Path("results"), "02_fhe_smoke", metadata, timings, comparison)
    print("FHE execute completed")
    print(comparison)
    print(f"Saved {json_path} and {csv_path}")


if __name__ == "__main__":
    main()
