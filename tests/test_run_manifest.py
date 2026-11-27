import json

import pytest

from src.fhe_credit.run_manifest import (
    ManifestValidationError,
    build_manifest,
    complete_run,
    create_run,
    generate_run_id,
    resume_run,
    sha256_file,
    transition_run,
    validate_manifest,
    verify_artifact_hashes,
    write_json_atomic,
)


def test_run_ids_are_unique():
    assert generate_run_id() != generate_run_id()


def test_run_directory_prevents_overwrite_and_writes_manifest(tmp_path):
    manifest = build_manifest(
        run_id="run-synthetic-one", experiment_id="synthetic-test", configuration_id="synthetic-config",
        config_hash="a" * 64, seed=42,
    )
    directory = create_run(tmp_path, manifest)
    assert json.loads((directory / "manifest.json").read_text(encoding="utf-8"))["status"] == "CREATED"
    with pytest.raises(FileExistsError):
        create_run(tmp_path, manifest)


def test_completed_run_requires_and_hashes_required_artifacts(tmp_path):
    manifest = build_manifest(
        run_id="run-synthetic-complete", experiment_id="synthetic-test", configuration_id="synthetic-config",
        config_hash="b" * 64,
    )
    manifest["required_artifacts"] = ["metric.json"]
    directory = create_run(tmp_path, manifest)
    manifest = transition_run(directory, "RUNNING")
    with pytest.raises(ManifestValidationError, match="required artifact"):
        complete_run(directory, manifest)
    write_json_atomic(directory / "metric.json", {"metric": 1})
    completed = complete_run(directory, manifest)
    assert completed["status"] == "COMPLETED"
    assert completed["artifact_hashes"]["metric.json"] == sha256_file(directory / "metric.json")
    validate_manifest(completed)
    assert verify_artifact_hashes(directory, completed) is True
    (directory / "metric.json").write_text('{"metric": 2}\n', encoding="utf-8")
    assert verify_artifact_hashes(directory, completed) is False


def test_interrupted_run_resumes_with_same_id_and_new_attempt(tmp_path):
    manifest = build_manifest(
        run_id="run-synthetic-resume", experiment_id="synthetic-test", configuration_id="synthetic-config",
        config_hash="c" * 64,
    )
    directory = create_run(tmp_path, manifest)
    transition_run(directory, "RUNNING")
    interrupted = transition_run(directory, "INTERRUPTED", reason="synthetic interruption")
    resumed = resume_run(directory)
    assert resumed["run_id"] == interrupted["run_id"]
    assert resumed["status"] == "RUNNING"
    assert len(resumed["attempts"]) == len(interrupted["attempts"]) + 1
