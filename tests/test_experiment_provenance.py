from pathlib import Path

from src.fhe_credit.experiments.provenance import (
    effective_code_provenance,
    environment_metadata,
    persistent_machine_id,
)


def test_machine_id_is_stable_in_one_local_state_directory(tmp_path):
    assert persistent_machine_id(tmp_path / "state") == persistent_machine_id(tmp_path / "state")


def test_environment_canonical_representation_is_stable():
    first = environment_metadata()
    second = environment_metadata()
    assert first["environment_hash"] == second["environment_hash"]


def test_effective_code_hash_changes_for_authorized_source_change(tmp_path):
    source = tmp_path / "src/fhe_credit"
    source.mkdir(parents=True)
    file = source / "module.py"
    file.write_text("VALUE = 1\n", encoding="utf-8")
    configs = tmp_path / "configs"
    configs.mkdir()
    first = effective_code_provenance(tmp_path)
    file.write_text("VALUE = 2\n", encoding="utf-8")
    second = effective_code_provenance(tmp_path)
    assert first["effective_code_hash"] != second["effective_code_hash"]
