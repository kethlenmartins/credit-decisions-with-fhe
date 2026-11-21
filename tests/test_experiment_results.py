import json

import pytest

from src.fhe_credit.experiment_results import compare_outputs, write_report


def test_compare_outputs_reports_paired_equality():
    result = compare_outputs([0, 1], [0, 1], [0, 0])
    assert result["clear_equals_simulated"] is True
    assert result["clear_equals_encrypted"] is False
    assert result["different_clear_encrypted"] == 1


def test_compare_outputs_rejects_different_shapes():
    with pytest.raises(ValueError, match="same shape"):
        compare_outputs([0], [0, 1], [0])


def test_write_report_persists_json_and_csv(tmp_path):
    json_path, csv_path = write_report(
        tmp_path, "smoke", {"n_bits": 3}, {"compile": 0.1}, {"clear_equals_encrypted": True}
    )
    assert json.loads(json_path.read_text(encoding="utf-8"))["metadata"]["n_bits"] == 3
    assert "comparison.clear_equals_encrypted" in csv_path.read_text(encoding="utf-8")
