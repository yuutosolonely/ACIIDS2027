"""Only temporary synthetic run attempts; never a research job."""
import json

import pytest

from cric_ed.run_record import run_attempt


def test_failure_retains_stage_request_and_partial_data(tmp_path):
    out = tmp_path / "synthetic"
    with pytest.raises(RuntimeError, match="synthetic failure"):
        with run_attempt(out, {"seed": 0, "source": "fixture"}) as attempt:
            attempt.phase("baseline:fake")
            (attempt.directory / "partial.txt").write_text("fixture evidence")
            raise RuntimeError("synthetic failure")
    partial = tmp_path / "synthetic.partial"
    record = json.loads((partial / "attempt.json").read_text())
    assert not out.exists()
    assert record["status"] == "failed" and record["stage"] == "baseline:fake"
    assert record["request"]["source"] == "fixture"
    assert record["error"]["type"] == "RuntimeError"
    assert (partial / "partial.txt").read_text() == "fixture evidence"
    before = (partial / "attempt.json").read_bytes()
    with pytest.raises(FileExistsError):
        with run_attempt(out, {}):
            pytest.fail("Must not reuse partial evidence")
    assert (partial / "attempt.json").read_bytes() == before


def test_interruption_is_recorded_and_reraised(tmp_path):
    out = tmp_path / "interrupt"
    with pytest.raises(KeyboardInterrupt):
        with run_attempt(out, {}) as attempt:
            attempt.phase("score:fake")
            raise KeyboardInterrupt()
    record = json.loads((tmp_path / "interrupt.partial/attempt.json").read_text())
    assert record["status"] == "interrupted"
    assert not out.exists()


def test_only_complete_attempts_are_finalized_and_never_overwritten(tmp_path):
    out = tmp_path / "success"
    with run_attempt(out, {"seed": 2}, required=("result.json",)) as attempt:
        (attempt.directory / "result.json").write_text("{}")
    record = json.loads((out / "attempt.json").read_text())
    assert record["status"] == "completed"
    assert not (tmp_path / "success.partial").exists()
    with pytest.raises(FileExistsError):
        with run_attempt(out, {}):
            pytest.fail("Must not overwrite results")


def test_missing_required_artifact_remains_failed(tmp_path):
    out = tmp_path / "incomplete"
    with pytest.raises(ValueError, match="artifact is absent"):
        with run_attempt(out, {}, required=("scores.npz",)):
            pass
    record = json.loads((tmp_path / "incomplete.partial/attempt.json").read_text())
    assert record["status"] == "failed" and record["stage"] == "finalize"
    assert not out.exists()
