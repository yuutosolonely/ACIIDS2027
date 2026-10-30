"""Software-only synthetic checks; no datasets, checkpoints or model imports."""
import copy
import hashlib
import json

import pytest

from cric_ed.v2_contract import (
    CONDITIONS, MODELS, PREREG, REQUIRED_FREEZE_FILES, SEEDS, SOURCE_FILES, TABLES,
    validate_run_grid, validate_run_metadata, verify_environment, verify_freeze,
)


def _freeze(root):
    files = {}
    for rel in REQUIRED_FREEZE_FILES:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("synthetic freeze fixture: " + rel, encoding="utf-8")
        files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    (root / "prereg/PREREGISTRATION_V2.sha256").write_text(files[PREREG])
    lock = root / "prereg/PREREGISTRATION_V2.freeze.json"
    lock.write_text(json.dumps({"schema_version": 1, "files_sha256": files}))
    return files


def test_freeze_requires_analysis_and_detects_changed_source(tmp_path):
    _freeze(tmp_path)
    identity = verify_freeze(tmp_path)
    assert set(identity["code_sha256"]) == set(SOURCE_FILES)
    (tmp_path / "experiments/tfm/analyze_v2.py").write_text("changed synthetic analysis")
    with pytest.raises(ValueError, match="Frozen file differs"):
        verify_freeze(tmp_path)


def test_protocol_hash_alone_does_not_freeze_pipeline(tmp_path):
    _freeze(tmp_path)
    (tmp_path / "prereg/PREREGISTRATION_V2.freeze.json").unlink()
    with pytest.raises(ValueError, match="not frozen"):
        verify_freeze(tmp_path)


def test_freeze_rejects_missing_analysis_and_disagreeing_protocol(tmp_path):
    files = _freeze(tmp_path)
    lock = tmp_path / "prereg/PREREGISTRATION_V2.freeze.json"
    del files["experiments/tfm/analyze_v2.py"]
    lock.write_text(json.dumps({"schema_version": 1, "files_sha256": files}))
    with pytest.raises(ValueError, match="omits required"):
        verify_freeze(tmp_path)
    _freeze(tmp_path)
    (tmp_path / "prereg/PREREGISTRATION_V2.sha256").write_text("0" * 64)
    with pytest.raises(ValueError, match="disagree"):
        verify_freeze(tmp_path)


def test_freeze_rejects_path_outside_repository(tmp_path):
    files = _freeze(tmp_path)
    files["../outside"] = "0" * 64
    (tmp_path / "prereg/PREREGISTRATION_V2.freeze.json").write_text(
        json.dumps({"schema_version": 1, "files_sha256": files}))
    with pytest.raises(ValueError, match="escapes"):
        verify_freeze(tmp_path)


def test_grid_rejects_missing_duplicate_and_unexpected_seeds():
    grid = [(t, c, s) for t in TABLES for c in CONDITIONS for s in SEEDS]
    validate_run_grid(grid)
    for bad in (grid[:-1], grid + [grid[0]], grid[:-1] + [(TABLES[-1], CONDITIONS[-1], 9)]):
        with pytest.raises(ValueError):
            validate_run_grid(bad)


def test_metadata_requires_same_frozen_snapshot_and_both_models():
    expected = {"prereg_sha256": "p", "source_snapshot_sha256": "s", "code_sha256": {"analysis": "a"},
                "checkpoint_sha256": {"clf": "c", "reg": "r"}}
    meta = {"status": "completed", "table": TABLES[0], "condition": "real", "seed": 0, "role": "confirmatory",
            "models": list(MODELS), "failures": [], **expected}
    assert validate_run_metadata(meta, expected) == (TABLES[0], "real", 0)
    for key, val in (("source_snapshot_sha256", "other"), ("code_sha256", {}),
                     ("seed", True), ("role", "development"), ("models", [MODELS[0]]),
                     ("models", [MODELS[0], MODELS[0]]), ("failures", None), ("checkpoint_sha256", {})):
        bad = copy.deepcopy(meta)
        bad[key] = val
        with pytest.raises(ValueError):
            validate_run_metadata(bad, expected)


def test_runtime_verification_requires_core_pins_and_matches_installed_metadata(tmp_path):
    env = tmp_path / "experiments/tfm_env_freeze.txt"
    env.parent.mkdir()
    packages = ["torch", "tabpfn", "lightgbm", "numpy", "pandas", "scipy", "scikit-learn"]
    env.write_text("\n".join(p + "==1.0" for p in packages if p != "torch"))
    with pytest.raises(ValueError, match="omits core.*torch"):
        verify_environment(tmp_path, lambda _: "1.0")
    env.write_text("\n".join(p + "==1.0" for p in packages))
    assert verify_environment(tmp_path, lambda _: "1.0") == {p: "1.0" for p in packages}
    with pytest.raises(ValueError, match="differs from pinned"):
        verify_environment(tmp_path, lambda _: "2.0")
    env.write_text("torch>=1.0")
    with pytest.raises(ValueError, match="exact.*pins"):
        verify_environment(tmp_path, lambda _: "1.0")
