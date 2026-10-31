"""Candidate v2 invariants on synthetic data and fake models only.

Run in the existing .venv-tfm environment. The minimal setup environment skips this
module when its scientific dependencies are absent; no packages are downloaded.
"""
import importlib.util
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("scipy")

from cric_ed import conditional as c
from cric_ed.v2_contract import BASELINES, CONDITIONS, MODELS, SEEDS, TABLES

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate_analysis", ROOT / "experiments/tfm/analyze_v2.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class FakeModel:
    """Deterministic context-sensitive tail stub, with no fitted weights or downloads."""
    def tail(self, Xc, yc, Xq, yq, cat_idx):
        assert Xc.shape[1] == Xq.shape[1] == 1  # target column omitted
        return np.exp(-np.abs(yq - np.mean(yc)) / (np.std(yc) + 1))


def table():
    return pd.DataFrame({"x": [str(i) for i in range(60)],
                         "y": [str((i * 7) % 19) for i in range(60)]})


def test_nested_purification_is_invariant_to_outer_query_values():
    dirty = table()
    folds, bases = c.folds_and_bases(len(dirty), 5, 512, 0)
    heldout = set(folds[0].tolist())
    changed = dirty.copy()
    changed.iloc[folds[0], :] = "10000"
    logs = []
    raw_scores = []
    for frame in (dirty, changed):
        raw, _ = c.score_table(frame, list(frame), FakeModel(), "raw", 0)
        raw_scores.append(raw)
        log = c.RunLog()
        c.score_table(frame, list(frame), FakeModel(), "purify", 0, log=log)
        logs.append(log)
        inner = [r for r in log.contexts if r["stage"] == "pass1" and r["outer_fold"] == 0]
        assert inner
        for r in inner:
            for key in ("query_row_ids", "base_row_ids", "active_row_ids", "preprocessing_row_ids"):
                assert heldout.isdisjoint(r[key])
            assert set(r["query_row_ids"]).isdisjoint(r["active_row_ids"])
    # Reusing the old global matrix exposes a dependency on held-out target values.
    assert not np.allclose(raw_scores[0][bases[0]], raw_scores[1][bases[0]])
    removal = lambda log: [r["removed_row_ids"] for r in log.contexts
                           if r["stage"] == "final" and r["fold"] == 0]
    assert removal(logs[0]) == removal(logs[1])


def test_contexts_pair_arms_and_log_complete_membership():
    dirty = table()
    arms = {}
    for arm in ("raw", "random", "purify"):
        log = c.RunLog()
        c.score_table(dirty, list(dirty), FakeModel(), arm, 3, log=log)
        arms[arm] = [r for r in log.contexts if r["stage"] == "final"]
        for r in arms[arm]:
            assert set(r["query_row_ids"]).isdisjoint(r["active_row_ids"])
            assert set(r["active_row_ids"]) | set(r["removed_row_ids"]) == set(r["base_row_ids"])
    assert [r["base_row_ids"] for r in arms["raw"]] == [r["base_row_ids"] for r in arms["purify"]]
    assert [r["base_row_ids"] for r in arms["random"]] == [r["base_row_ids"] for r in arms["purify"]]
    assert [len(r["removed_row_ids"]) for r in arms["random"]] == [len(r["removed_row_ids"]) for r in arms["purify"]]


def test_global_pass1_and_clean_inputs_are_rejected_before_model_calls():
    dirty = table()
    with pytest.raises(ValueError, match="External pass1"):
        c.score_table(dirty, list(dirty), object(), "purify", 0, pass1=np.zeros((60, 2)))
    for arm in ("raw", "random", "purify", "leaky"):
        with pytest.raises(ValueError, match="only.*oracle"):
            c.score_table(dirty, list(dirty), object(), arm, 0, clean=dirty)


def test_timing_includes_preprocessing(monkeypatch):
    clock = [0.0]
    original = c.Encoder
    class TimedEncoder(original):
        def __init__(self, *args):
            clock[0] += 10.0
            super().__init__(*args)
    monkeypatch.setattr(c, "Encoder", TimedEncoder)
    monkeypatch.setattr(c.time, "perf_counter", lambda: clock[0])
    log = c.RunLog()
    c.score_table(table(), ["x", "y"], FakeModel(), "raw", 0, log=log)
    assert log.seconds[("raw", 0)] == 10.0


def test_analysis_has_no_cross_dataset_hypothesis_verdict():
    assert not hasattr(analysis, "decide")
    assert not hasattr(analysis, "holm")


def test_bootstrap_keeps_all_seeds_in_each_valid_replicate(monkeypatch):
    # Seed-specific masks mimic injected corruption; zero-positive seeds may not be omitted.
    monkeypatch.setattr(analysis, "B", 200)
    runs = []
    for i in range(2):
        E = np.zeros((4, 1), bool)
        E[i] = True
        runs.append(({}, {"errors": E, "a": np.arange(4.0).reshape(4, 1),
                          "b": np.arange(4.0)[::-1].reshape(4, 1)}))
    r = analysis.paired_delta(runs, "a", "b")
    assert 0 < r["valid"] < 200


def synthetic_run(meta_seed=0, condition="real"):
    E = np.array([[True, False], [False, False]])
    meta = {"status": "completed", "rows": 2, "cells": 4, "errors": 1, "row_ids": [0, 1], "seed": meta_seed,
            "eligible_columns": ["x", "y"], "condition": condition,
            "column_specs": [{"name": col, "kind": "numeric"} for col in ("x", "y")]}
    arrays = {"errors": E, "clean_values": np.array([["a", "b"], ["c", "d"]])}
    for b in BASELINES:
        arrays[f"baseline__{b}"] = np.zeros(E.shape)
    for m in MODELS:
        for a in ("raw", "random", "purify", "oracle") + (("leaky", "raw_leo") if condition == "real" else ()):
            arrays[f"{m}__{a}"] = np.zeros(E.shape)
            arrays[f"{m}__{a}__nan_cells"] = np.zeros(E.shape, bool)
    return meta, arrays


def test_analysis_rejects_missing_scores_denominator_and_failure_masks():
    meta, arrs = synthetic_run()
    analysis.validate_arrays(meta, arrs)
    key = "tabpfn-v2__purify"
    with pytest.raises(ValueError, match="scores"):
        analysis.validate_arrays(meta, {k: v for k, v in arrs.items() if k != key})
    with pytest.raises(ValueError, match="failure mask"):
        analysis.validate_arrays(meta, {k: v for k, v in arrs.items() if k != key + "__nan_cells"})
    with pytest.raises(ValueError, match="denominator"):
        analysis.validate_arrays({**meta, "cells": 3}, arrs)


def test_loader_requires_complete_matching_runs_and_seed_alignment(tmp_path):
    import json
    expected = {"prereg_sha256": "p", "source_snapshot_sha256": "s", "code_sha256": {"a": "b"}}
    for t in TABLES:
        for condition in CONDITIONS:
            for seed in SEEDS:
                d = tmp_path / f"{t}__{condition}__s{seed}"
                d.mkdir()
                meta, arrs = synthetic_run(seed, condition)
                meta.update(table=t, role="confirmatory", models=list(MODELS), failures=[], **expected)
                (d / "meta.json").write_text(json.dumps(meta))
                (d / "attempt.json").write_text(json.dumps({"status": "completed", "request": meta}))
                np.savez(d / "scores.npz", **arrs)
    units = analysis.load(tmp_path, expected)
    assert len(units) == 12 and all(len(v) == 5 for v in units.values())
    target = tmp_path / f"{TABLES[0]}__real__s0/meta.json"
    good = json.loads(target.read_text())
    target.write_text(json.dumps({**good, "row_ids": [1, 0]}))
    with pytest.raises(ValueError, match="alignment"):
        analysis.load(tmp_path, expected)
    target.write_text(json.dumps(good))
    # A partial failure is retained and blocks analysis, rather than silently disappearing.
    (tmp_path / "hospital__real__s0.partial").mkdir()
    with pytest.raises(ValueError, match="partial"):
        analysis.load(tmp_path, expected)


def test_unfrozen_runner_refuses_before_reading_data_or_creating_run(tmp_path, monkeypatch):
    module_spec = importlib.util.spec_from_file_location("candidate_runner", ROOT / "experiments/tfm/run_v2.py")
    runner = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(runner)
    monkeypatch.setattr(runner, "REPO", tmp_path)
    def forbidden(*args, **kwargs):
        raise AssertionError("An unfrozen run must not access benchmark data")
    monkeypatch.setattr(runner, "get_table", forbidden)
    out = tmp_path / "runs"
    with pytest.raises(ValueError, match="not frozen"):
        runner.run("hospital", "real", 0, list(MODELS), out)
    assert not out.exists()


def test_invalid_analysis_does_not_create_result_directory(tmp_path, monkeypatch):
    out = tmp_path / "results"
    monkeypatch.setattr(analysis, "REPO", tmp_path)
    monkeypatch.setattr(analysis.sys, "argv", ["analyze_v2.py", "--runs", str(tmp_path / "runs"), "--out", str(out)])
    with pytest.raises(ValueError, match="not frozen"):
        analysis.main()
    assert not out.exists()


def _synthetic_runner(monkeypatch, tmp_path):
    module_spec = importlib.util.spec_from_file_location("fixture_runner", ROOT / "experiments/tfm/run_v2.py")
    runner = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(runner)
    monkeypatch.setattr(runner, "REPO", tmp_path)
    monkeypatch.setattr(runner, "sha", lambda _: "fixture-source")
    monkeypatch.setattr(runner, "git_state", lambda: {"commit": "fixture", "dirty_files": 1})
    return runner


def test_runner_journals_runtime_failure_before_data_access(tmp_path, monkeypatch):
    import json
    runner = _synthetic_runner(monkeypatch, tmp_path)
    def mismatch(_):
        raise ValueError("synthetic runtime mismatch")
    def forbidden(*args, **kwargs):
        pytest.fail("A runtime mismatch must stop before input/data access")
    monkeypatch.setattr(runner, "verify_environment", mismatch)
    monkeypatch.setattr(runner, "verify_local_inputs", forbidden)
    monkeypatch.setattr(runner, "get_table", forbidden)
    out = tmp_path / "runs"
    with pytest.raises(ValueError, match="runtime mismatch"):
        runner.run("movies_1", "real", 0, ["lgbm"], out)
    partial = out / "movies_1__real__s0.partial"
    record = json.loads((partial / "attempt.json").read_text())
    assert record["status"] == "failed" and record["stage"] == "verify_environment"
    assert record["request"]["role"] == "development"
    assert not (out / "movies_1__real__s0").exists()


def test_runner_completes_only_synthetic_artifacts_with_runtime_provenance(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    runner = _synthetic_runner(monkeypatch, tmp_path)
    dirty = table()
    fake_table = SimpleNamespace(dirty=dirty, clean=dirty.copy(), eligible=list(dirty),
                                 errors=np.zeros(dirty.shape, bool), meta={})
    monkeypatch.setattr(runner, "get_table", lambda *args: fake_table)
    monkeypatch.setattr(runner, "verify_environment", lambda _: {"synthetic": "1.0"})
    monkeypatch.setattr(runner, "verify_local_inputs", lambda *args: {"clf": "fake", "reg": "fake"})
    monkeypatch.setattr(runner, "BASELINES", {"fixture": lambda *args, **kwargs: np.zeros(dirty.shape)})
    monkeypatch.setattr(runner, "LGBMModel", lambda seed: FakeModel())
    def forbidden(*args, **kwargs):
        pytest.fail("Synthetic runner must not construct a real TFM")
    monkeypatch.setattr(runner, "TabPFNModel", forbidden)
    out = tmp_path / "runs"
    runner.run("movies_1", "real", 0, ["lgbm"], out)
    done = out / "movies_1__real__s0"
    meta = json.loads((done / "meta.json").read_text())
    attempt = json.loads((done / "attempt.json").read_text())
    assert meta["status"] == attempt["status"] == "completed"
    assert meta["runtime_versions"] == {"synthetic": "1.0"}
    assert not (out / "movies_1__real__s0.partial").exists()
    assert (done / "contexts.jsonl").stat().st_size > 0
