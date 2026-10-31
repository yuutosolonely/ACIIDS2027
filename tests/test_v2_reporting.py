"""Software fixtures only: group exclusion and descriptive reporting contracts."""
import importlib.util
import json
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("scipy")

from cric_ed import conditional as c
from cric_ed.benchmark import Table, entity_groups
from cric_ed.v2_contract import BASELINES, CONDITIONS, MODELS, TABLES

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reporting", ROOT / "experiments/tfm/analyze_v2.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def test_group_folds_and_scoring_never_include_query_entity():
    groups = np.repeat(np.arange(10), 6)
    frame = pd.DataFrame({"x": np.arange(60).astype(str), "y": (np.arange(60) % 13).astype(str)})
    folds, bases = c.folds_and_bases(60, 5, 20, 8, groups)
    assert sorted(np.concatenate(folds)) == list(range(60))
    for query, base in zip(folds, bases):
        assert set(groups[query]).isdisjoint(groups[base])
        assert len(base) == 20
    class Fake:
        def tail(self, Xc, yc, Xq, yq, cat_idx):
            return np.full(len(yq), 0.5)
    log = c.RunLog()
    c.score_table(frame, list(frame), Fake(), "raw_leo", 8, groups=groups, log=log)
    assert not log.failures
    for record in log.contexts:
        assert set(groups[record["query_row_ids"]]).isdisjoint(groups[record["active_row_ids"]])


@pytest.mark.parametrize("arm,groups", [
    ("raw_leo", None), ("raw", np.arange(10)), ("purify", np.arange(10)),
    ("raw_leo", np.arange(9)), ("raw_leo", np.zeros(10)),
    ("raw_leo", np.zeros((10, 1))), ("raw_leo", np.full(10, np.nan)),
])
def test_raw_leo_invalid_arguments_fail_before_model_calls(arm, groups):
    frame = pd.DataFrame({"x": np.arange(10).astype(str), "y": np.arange(10).astype(str)})
    with pytest.raises(ValueError):
        c.score_table(frame, list(frame), object(), arm, 0, groups=groups)


def test_entity_keys_use_observed_values_only():
    dirty = pd.DataFrame({"flight": ["a", "a", "b", "bad-key"]})
    clean = pd.DataFrame({"flight": ["a", "a", "b", "b"]})
    groups = entity_groups(Table("flights", dirty, clean, ["flight"]))
    assert groups[0] == groups[1] and groups[2] != groups[3]


def fake_run(table="movies_1", condition="real", seed=0):
    errors = np.array([[1, 0], [0, 1], [0, 0], [1, 0]], dtype=bool)
    meta = {"table": table, "condition": condition, "seed": seed, "rows": 4,
            "cells": 8, "errors": 3, "row_ids": list(range(4)), "eligible_columns": ["x", "y"],
            "column_specs": [{"name": "x", "kind": "numeric"}, {"name": "y", "kind": "categorical"}],
            "models": list(MODELS), "failures": [], "role": "development", "status": "completed",
            "code_sha256": {"fixture": "source"}, "checkpoint_sha256": {"fixture": "weights"},
            "timing_sec": {}, "wall_clock_sec": 100}
    arrays = {"errors": errors, "clean_values": np.full(errors.shape, "fixture")}
    for baseline in BASELINES:
        arrays["baseline__" + baseline] = np.ones(errors.shape)
    for model in MODELS:
        arms = ["raw", "random", "purify", "oracle"]
        if condition == "real":
            arms += ["leaky"] + (["raw_leo"] if table == "hospital" else [])
        for arm in arms:
            arrays[f"{model}__{arm}"] = errors.astype(float) if arm == "purify" else np.zeros(errors.shape)
            arrays[f"{model}__{arm}__nan_cells"] = np.zeros(errors.shape, bool)
            meta["timing_sec"][f"{model}__{arm}"] = 10.0
        meta["timing_sec"][f"{model}__pass1_nested"] = 7.0
    return meta, arrays


def test_per_table_fake_analysis_writes_csv_latex_and_figures(tmp_path, monkeypatch):
    monkeypatch.setattr(analysis, "B", 30)
    units = {(table, condition): [fake_run(table, condition, seed) for seed in (0, 1)]
             for table in ("movies_1", "hospital") for condition in CONDITIONS}
    result = analysis.analyze(units, development=True)
    # Exercise actual strict JSON serialization, including NumPy count scalars.
    json.dumps(analysis._json_safe(result), allow_nan=False)
    assert "hypotheses" not in result
    effect = result["units"]["movies_1|real"]["paired"]["purify_minus_random"]
    assert effect["delta"] == pytest.approx(1 - 3 / 8)
    assert effect["category"] == "primary"
    assert result["units"]["movies_1|inj-random"]["paired"]["purify_minus_random"]["category"] == "mechanism_probe"
    assert result["macro_descriptive"]["real|purify_minus_random"]["n_tables"] == 2
    costs = result["units"]["movies_1|real"]["cost_seconds_seed_mean"]
    assert costs["tabpfn-v2__purify_final"] == 3
    assert costs["tabpfn-v2__random_matched_total"] == 17
    assert "tabpfn-v2_raw_leo_minus_raw" in result["units"]["hospital|real"]["paired"]
    assert "tabpfn-v2_leaky_minus_raw" in result["units"]["movies_1|real"]["paired"]
    assert len(result["units"]["movies_1|real"]["seed_metrics"]) == 2
    assert result["units"]["movies_1|real"]["metrics"]["baseline__VF"]["supported_cells"] == 8
    assert result["units"]["movies_1|real"]["metrics"]["baseline__RobustZ"]["supported_cells"] == 4
    analysis.write_tables(result, tmp_path)
    analysis.write_figures(result, tmp_path)
    for name in ("metrics", "paired_deltas", "costs", "macro_descriptive"):
        assert (tmp_path / (name + ".csv")).stat().st_size > 10
        assert "\\begin{tabular}" in (tmp_path / (name + ".tex")).read_text()
    assert (tmp_path / "primary_deltas.pdf").stat().st_size > 100
    assert (tmp_path / "mechanism_deltas.png").stat().st_size > 100


def test_keyed_real_analysis_requires_leo_arrays():
    meta, arrays = fake_run("hospital")
    analysis.validate_arrays(meta, arrays)
    arrays.pop("lgbm__raw_leo")
    with pytest.raises(ValueError, match="raw_leo"):
        analysis.validate_arrays(meta, arrays)


def test_development_loader_cannot_bypass_confirmatory_freeze(tmp_path):
    meta, arrays = fake_run()
    expected = {k: meta[k] for k in ("code_sha256", "checkpoint_sha256")}
    for table in TABLES:
        with pytest.raises(ValueError, match="movies_1"):
            analysis.validate_development_metadata({**meta, "table": table}, expected)
    for condition in CONDITIONS:
        meta, arrays = fake_run(condition=condition)
        path = tmp_path / f"movies_1__{condition}__s0"
        path.mkdir()
        (path / "meta.json").write_text(json.dumps(meta))
        (path / "attempt.json").write_text(json.dumps({"status": "completed", "request": meta}))
        np.savez(path / "scores.npz", **arrays)
    assert len(analysis.load(tmp_path, expected, development=True)) == 3
    path = tmp_path / "movies_1__real__s0/meta.json"
    meta = json.loads(path.read_text())
    path.write_text(json.dumps({**meta, "table": "hospital"}))
    with pytest.raises(ValueError, match="movies_1"):
        analysis.load(tmp_path, expected, development=True)


def test_bootstrap_uses_same_rows_across_seeds(monkeypatch):
    monkeypatch.setattr(analysis, "B", 10)
    # Opposite seed effects must cancel in every paired replicate, not merely on average.
    meta, arrays = fake_run()
    a = arrays["errors"].astype(float)
    runs = [(meta, {"errors": arrays["errors"], "a": a, "b": -a}),
            (meta, {"errors": arrays["errors"], "a": -a, "b": a})]
    effect = analysis.paired_delta(runs, "a", "b")
    assert effect["delta"] == 0 and effect["ci95"] == [0, 0]


def test_nonfinite_nested_predictions_are_reported_before_penalty():
    class Nonfinite:
        def tail(self, Xc, yc, Xq, yq, cat_idx):
            return np.full(len(yq), np.nan)
    frame = pd.DataFrame({"x": np.arange(50).astype(str), "y": (np.arange(50) * 2).astype(str)})
    log = c.RunLog()
    scores, _ = c.score_table(frame, list(frame), Nonfinite(), "purify", 0, log=log)
    assert any(e["stage"] == "pass1" and e["nonfinite_cells"] > 0 for e in log.failures)
    assert any(e["stage"] == "final" and e["nonfinite_cells"] > 0 for e in log.failures)
    assert scores.shape == (50, 2) and np.isfinite(c.apply_penalty(scores)).all()
