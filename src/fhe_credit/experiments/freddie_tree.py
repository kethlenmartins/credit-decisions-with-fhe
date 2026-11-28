"""N01 exploratory Freddie Mac decision-tree experiment; never writes outside one Run ID."""
from __future__ import annotations

import json
import math
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..run_manifest import write_json_atomic

ORIG_FEATURES = {"credit_score": 0, "original_cltv": 8, "original_dti": 9, "original_upb": 10, "original_ltv": 11, "original_loan_term": 21, "number_of_borrowers": 22}
LOAN_ID, FIRST_PAYMENT = 19, 1
PERF_LOAN_ID, PERF_PERIOD, PERF_DELINQUENCY, PERF_ZERO = 0, 1, 3, 8


def _month(value: str) -> int | None:
    value = value.strip()
    if len(value) != 6 or not value.isdigit(): return None
    year, month = int(value[:4]), int(value[4:])
    return year * 12 + month - 1 if 1 <= month <= 12 else None


def _load_vintage(path: Path, year: int, horizon: int, features: list[str], missing_codes: set[int], log) -> tuple[pd.DataFrame, dict[str, int]]:
    """Build one loan-level target, excluding censoring and ambiguous termination."""
    with zipfile.ZipFile(path) as archive:
        orig_name = next(name for name in archive.namelist() if "orig" in name.lower())
        perf_name = next(name for name in archive.namelist() if "perf" in name.lower())
        loans: dict[str, dict[str, Any]] = {}
        log(f"vintage={year} phase=origination_read_started")
        with archive.open(orig_name) as stream:
            for raw in stream:
                fields = raw.decode("latin-1").rstrip("\r\n").split("|")
                if len(fields) < 23: continue
                reference = _month(fields[FIRST_PAYMENT])
                if reference is None: continue
                values = []
                for name in features:
                    try: value = float(fields[ORIG_FEATURES[name]].strip())
                    except ValueError: value = np.nan
                    if value in missing_codes: value = np.nan
                    values.append(value)
                loans[fields[LOAN_ID]] = {"reference": reference, "values": values, "last": None, "event": None, "zero": None, "zero_code": None}
        log(f"vintage={year} phase=performance_read_started")
        with archive.open(perf_name) as stream:
            for raw in stream:
                fields = raw.decode("latin-1").rstrip("\r\n").split("|")
                if len(fields) < 9 or fields[PERF_LOAN_ID] not in loans: continue
                row, period = loans[fields[PERF_LOAN_ID]], _month(fields[PERF_PERIOD])
                if period is None: continue
                row["last"] = period if row["last"] is None else max(row["last"], period)
                status = fields[PERF_DELINQUENCY].strip()
                if status.isdigit() and int(status) >= 3 and (row["event"] is None or period < row["event"]): row["event"] = period
                code = fields[PERF_ZERO].strip()
                if code and (row["zero"] is None or period < row["zero"]): row["zero"], row["zero_code"] = period, code
    log(f"vintage={year} phase=target_construction_started")
    accepted, counts = [], Counter()
    for loan_id, row in loans.items():
        end = row["reference"] + horizon
        if row["event"] is not None and row["event"] <= end and (row["zero"] is None or row["event"] <= row["zero"]): target = 1
        elif row["zero"] is not None and row["zero"] <= end:
            if row["zero_code"] == "01": target = 0
            elif row["zero_code"] in {"02", "03", "09", "96"}: counts["excluded_termination_or_censoring"] += 1; continue
            else: counts["excluded_unknown_zero_code"] += 1; continue
        elif row["last"] is not None and row["last"] >= end: target = 0
        else: counts["excluded_insufficient_follow_up"] += 1; continue
        accepted.append([loan_id, target, *row["values"]]); counts["eligible"] += 1
    frame = pd.DataFrame(accepted, columns=["loan_id", "target", *features])
    counts["origination_records"] = len(loans); counts["positive"] = int(frame.target.sum()) if len(frame) else 0
    log(f"vintage={year} phase=target_construction_completed eligible={len(frame)} positives={counts['positive']}")
    return frame, dict(counts)


def _error(left: np.ndarray, right: np.ndarray) -> dict[str, Any]:
    delta = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    result = {"n": int(delta.size), "mae": float(np.mean(abs(delta))), "rmse": float(np.sqrt(np.mean(delta ** 2))), "max_absolute_error": float(np.max(abs(delta))), "mean_signed_error": float(np.mean(delta)), "percentiles_absolute_error": {str(p): float(np.percentile(abs(delta), p)) for p in (50,90,95,99)}}
    result["spearman"] = float(pd.Series(left).corr(pd.Series(right), method="spearman")) if len(np.unique(left)) > 1 and len(np.unique(right)) > 1 else None
    return result


def run_n01(config: dict[str, Any], output: Path) -> list[str]:
    import joblib
    from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
    from sklearn.tree import DecisionTreeClassifier
    from concrete.ml.sklearn import DecisionTreeClassifier as ConcreteTree

    log_path = output / "progress.log"
    def log(message: str) -> None:
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {message}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n"); stream.flush()
    p, resolved = config["parameters"], config["_resolved_input_paths"]
    features, horizon, seed = p["features"], p["horizon_months"], p["seed"]
    frames, summaries = {}, {}
    for year in [2015, 2016, 2017, 2019, 2021]:
        frame, summary = _load_vintage(Path(resolved[f"sample_{year}"]), year, horizon, features, set(p["missing_codes"]), log)
        frames[year], summaries[str(year)] = frame, summary
    train = pd.concat([frames[y] for y in p["training_vintages"]], ignore_index=True)
    val, test = frames[2019], frames[2021]
    log("phase=preprocessing_started")
    medians = train[features].median().to_dict()
    for frame in (train, val, test): frame.loc[:, features] = frame[features].fillna(medians).clip(lower=train[features].quantile(.001), upper=train[features].quantile(.999), axis=1)
    X_train, y_train = train[features].to_numpy(np.float32), train.target.to_numpy(int)
    X_val, y_val = val[features].to_numpy(np.float32), val.target.to_numpy(int)
    X_test, y_test = test[features].to_numpy(np.float32), test.target.to_numpy(int)
    np.savez_compressed(output / "prepared_dataset.npz", X_train=X_train, y_train=y_train, X_validation=X_val, y_validation=y_val, X_test=X_test, y_test=y_test)
    log("phase=preprocessing_completed prepared_dataset_persisted=true")
    log("phase=sklearn_training_started")
    started = time.perf_counter(); float_model = DecisionTreeClassifier(**p["model"]).fit(X_train, y_train); train_seconds = time.perf_counter()-started
    joblib.dump(float_model, output / "sklearn_model.joblib")
    log("phase=sklearn_training_completed model_persisted=true")
    started=time.perf_counter(); p_ref=float_model.predict_proba(X_test)[:,1]; ref_seconds=time.perf_counter()-started
    metrics = {"scope":"EXPLORATORY; target and feature set are provisional; no production or causal claim", "predictive": {"roc_auc":float(roc_auc_score(y_test,p_ref)),"average_precision":float(average_precision_score(y_test,p_ref)),"brier":float(brier_score_loss(y_test,p_ref)),"log_loss":float(log_loss(y_test,p_ref,labels=[0,1]) )}, "timings_seconds":{"sklearn_training":train_seconds,"sklearn_test_inference":ref_seconds}}
    paired_n=min(p["paired_evaluation_size"],len(X_test)); paired=np.arange(paired_n)
    calibration=X_train[np.random.default_rng(seed).choice(len(X_train),min(p["calibration_sample_size"],len(X_train)),replace=False)]
    fidelity={"reference_semantics":"sklearn predict_proba[:, 1]", "quantized":{}}
    concrete3=None
    for bits in p["quantization_bits"]:
        try:
            log(f"phase=quantized_inference_started n_bits={bits}")
            model=ConcreteTree.from_sklearn_model(float_model, X=calibration, n_bits=bits)
            started=time.perf_counter(); q=model.predict_proba(X_test[paired],fhe="disable")[:,1]; elapsed=time.perf_counter()-started
            fidelity["quantized"][str(bits)]={"status":"COMPLETED","output_semantics":"Concrete ML predict_proba[:, 1], fhe=disable","error_quant_minus_reference":_error(q,p_ref[paired]),"distinct_probabilities":int(len(np.unique(q))),"inference_seconds":elapsed,"class_agreement":float(np.mean((q>=.5)==(p_ref[paired]>=.5)))}
            if bits==p["fhe_bits"]: concrete3=model
            log(f"phase=quantized_inference_completed n_bits={bits}")
        except Exception as exc: fidelity["quantized"][str(bits)]={"status":"FAILED","error_type":type(exc).__name__}
    if concrete3 is None: raise RuntimeError("requested FHE bit-width did not create a Concrete ML model")
    log(f"phase=compilation_started n_bits={p['fhe_bits']}")
    started=time.perf_counter(); concrete3.compile(calibration); compilation=time.perf_counter()-started
    log("phase=compilation_completed")
    log("phase=simulation_started")
    sim=concrete3.predict_proba(X_test[paired],fhe="simulate")[:,1]
    q3=concrete3.predict_proba(X_test[paired],fhe="disable")[:,1]
    fidelity["simulation"]={"status":"COMPLETED","n":paired_n,"error_sim_minus_quant":_error(sim,q3),"error_sim_minus_reference":_error(sim,p_ref[paired]),"class_agreement_quant":float(np.mean((sim>=.5)==(q3>=.5)))}
    log("phase=simulation_completed")
    fhe_n=min(p["fhe_sample_size"],len(X_test)); selected=np.arange(fhe_n)
    log(f"phase=fhe_execute_started n={fhe_n}")
    started=time.perf_counter(); fhe=concrete3.predict_proba(X_test[selected],fhe="execute")[:,1]; fhe_seconds=time.perf_counter()-started
    fidelity["fhe_execute"]={"status":"COMPLETED","n":fhe_n,"selection":"primeiras observações na ordem do arquivo sample_2021 após filtros; não selecionadas por concordância","error_fhe_minus_quant":_error(fhe,q3[selected]),"error_fhe_minus_reference":_error(fhe,p_ref[selected]),"class_agreement_quant":float(np.mean((fhe>=.5)==(q3[selected]>=.5))),"total_seconds":fhe_seconds,"key_generation":"not isolated by high-level API"}
    tree={"depth":int(float_model.get_depth()),"node_count":int(float_model.tree_.node_count),"leaf_count":int(float_model.get_n_leaves()),"leaf_probabilities":sorted(float(x) for x in float_model.tree_.value[:,0,1]/float_model.tree_.value[:,0].sum(axis=1))}
    summary={"target":"delinquency >= 90 days within 12 months from First Payment Date","target_scenario":"S01: zero-balance 01 negative; 02/03/09/96 and insufficient follow-up excluded","features":features,"splits":{"train":p["training_vintages"],"validation":p["validation_vintages"],"test":p["test_vintages"]},"per_vintage":summaries,"n_train":len(train),"n_validation":len(val),"n_test":len(test),"prevalence":{"train":float(y_train.mean()),"validation":float(y_val.mean()),"test":float(y_test.mean())},"imputation":"median and 0.1%/99.9% clipping fit on training only","missing_codes":p["missing_codes"]}
    metrics["timings_seconds"]["concrete_compilation"] = compilation
    write_json_atomic(output/"metrics.json",metrics); write_json_atomic(output/"fidelity.json",fidelity); write_json_atomic(output/"dataset_summary.json",summary); write_json_atomic(output/"tree_summary.json",tree)
    log("phase=fhe_execute_completed run_artifacts_persisted=true")
    return ["metrics.json","fidelity.json","dataset_summary.json","tree_summary.json","prepared_dataset.npz","sklearn_model.joblib","progress.log"]
