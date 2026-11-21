"""One fixed UCI observation through a compiled Concrete ML decision tree."""
from pathlib import Path
import platform
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as FloatDecisionTreeClassifier

from concrete.ml.sklearn import DecisionTreeClassifier
from src.fhe_credit.experiment_results import compare_outputs, write_report


def cpu_model():
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def main():
    X = pd.read_csv("data/raw/features.csv").select_dtypes(include="number").drop(columns=["ID"], errors="ignore")
    y = pd.read_csv("data/raw/target.csv").iloc[:, 0].astype(int)
    X_train, X_hold, y_train, y_hold = train_test_split(X, y, test_size=0.4, stratify=y, random_state=42)
    _, X_test, _, _ = train_test_split(X_hold, y_hold, test_size=0.5, stratify=y_hold, random_state=42)
    train = X_train.to_numpy(dtype=np.float32)
    sample = X_test.iloc[:1].to_numpy(dtype=np.float32)

    float_model = FloatDecisionTreeClassifier(max_depth=3, min_samples_leaf=100, random_state=42).fit(X_train, y_train)
    model = DecisionTreeClassifier(n_bits=3, max_depth=3, min_samples_leaf=100, random_state=42)
    started = time.perf_counter(); model.fit(train, y_train); training = time.perf_counter() - started
    started = time.perf_counter(); model.compile(train); compilation = time.perf_counter() - started
    started = time.perf_counter(); clear = model.predict(sample, fhe="disable"); clear_time = time.perf_counter() - started
    started = time.perf_counter(); simulated = model.predict(sample, fhe="simulate"); simulation_time = time.perf_counter() - started
    started = time.perf_counter(); encrypted = model.predict(sample, fhe="execute"); execute_time = time.perf_counter() - started
    comparison = compare_outputs(clear, simulated, encrypted)
    metadata = {
        "experiment": "03_fhe_uci_smoke", "seed": 42, "n_bits": 3,
        "n_train_observations": len(train), "n_validation_observations": 6000,
        "n_test_observations": 6000, "n_inference_observations": 1,
        "architecture": platform.machine(), "cpu_model": cpu_model(),
        "output_semantics": "class labels only; not probabilities or calibrated PD",
        "float_class_for_same_observation": int(float_model.predict(sample)[0]),
        "quantized_clear_class_for_same_observation": int(clear[0]),
    }
    timings = {"training": training, "compilation": compilation, "quantized_clear_prediction": clear_time, "fhe_simulation_prediction": simulation_time, "fhe_execute_total_prediction": execute_time, "key_generation": "não mensurado: API de alto nível", "encryption": "não mensurado: API de alto nível", "homomorphic_evaluation": "não mensurado: API de alto nível", "decryption": "não mensurado: API de alto nível"}
    paths = write_report(Path("results"), "03_fhe_uci_smoke", metadata, timings, comparison)
    print({"comparison": comparison, "float_class": metadata["float_class_for_same_observation"], "files": [str(path) for path in paths]})


if __name__ == "__main__":
    main()
