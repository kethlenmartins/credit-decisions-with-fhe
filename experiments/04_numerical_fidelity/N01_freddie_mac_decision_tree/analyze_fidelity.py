"""Derived N01-A analysis; reads a completed private run and writes private analysis only."""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from scipy.stats import kendalltau, spearmanr
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score


def frequencies(values):
    unique, counts = np.unique(values, return_counts=True)
    return [{"value": float(value), "count": int(count)} for value, count in zip(unique, counts)]


def predictive(y, scores):
    return {"roc_auc": float(roc_auc_score(y, scores)), "average_precision": float(average_precision_score(y, scores)), "brier": float(brier_score_loss(y, scores)), "log_loss": float(log_loss(y, scores, labels=[0, 1])), "variance": float(np.var(scores)), "distinct_probabilities": int(len(np.unique(scores)))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    from concrete.ml.sklearn import DecisionTreeClassifier

    data = np.load(args.run_directory / "prepared_dataset.npz")
    model = joblib.load(args.run_directory / "sklearn_model.joblib")
    x, y = data["X_test"][:10_000], data["y_test"][:10_000]
    calibration = data["X_train"][np.random.default_rng(42).choice(len(data["X_train"]), 1000, replace=False)]
    reference = model.predict_proba(x)[:, 1]
    leaf_ids = model.apply(x)
    output = {"source_run_id": args.run_directory.name, "n": len(y), "prevalence": float(y.mean()), "reference": {"metrics": predictive(y, reference), "probability_frequencies": frequencies(reference), "leaf_distribution": {str(key): int(value) for key, value in zip(*np.unique(leaf_ids, return_counts=True))}, "leaf_values": [float(model.tree_.value[node, 0, 1] / model.tree_.value[node, 0].sum()) for node in range(model.tree_.node_count) if model.tree_.children_left[node] == model.tree_.children_right[node]]}, "quantized": {}}
    pair_mask = np.triu(np.ones((len(x), len(x)), dtype=bool), 1)
    ref_order = np.sign(reference[:, None] - reference[None, :])
    ordered = (ref_order != 0) & pair_mask
    for bits in range(3, 13):
        try:
            concrete = DecisionTreeClassifier.from_sklearn_model(model, X=calibration, n_bits=bits)
            scores = concrete.predict_proba(x, fhe="disable")[:, 1]
            delta, quant_order = scores - reference, np.sign(scores[:, None] - scores[None, :])
            output["quantized"][str(bits)] = {"status": "COMPLETED", "metrics": predictive(y, scores), "probability_frequencies": frequencies(scores), "mae": float(np.mean(abs(delta))), "rmse": float(np.sqrt(np.mean(delta**2))), "max_absolute_error": float(np.max(abs(delta))), "mean_signed_error": float(np.mean(delta)), "spearman": None if len(np.unique(scores)) < 2 else float(spearmanr(reference, scores).statistic), "kendall_tau_b": None if len(np.unique(scores)) < 2 else float(kendalltau(reference, scores).statistic), "tied_pair_proportion": float((quant_order[pair_mask] == 0).mean()), "reference_ordered_to_tied_proportion": float(((quant_order == 0) & ordered).sum() / ordered.sum()), "inversion_proportion": float(((ref_order * quant_order < 0) & ordered).sum() / ordered.sum())}
        except Exception as error:
            output["quantized"][str(bits)] = {"status": "FAILED", "error_type": type(error).__name__}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
