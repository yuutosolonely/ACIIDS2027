"""Strict protocol software fixtures; no weights, labels or benchmark files."""
import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("scipy")

from cric_ed.strict_scorer import StrictConfig, context_plan, score_diagnostic, score_variants


class FakeModel:
    def tail(self, Xc, yc, Xq, yq, cat_idx):
        assert Xc.shape[1] == Xq.shape[1] == 2
        return np.exp(-np.abs(yq - yc.mean()) / (yc.std() + 1))

    def class_proba(self, Xc, yc, Xq, cat_idx):
        assert Xc.shape[1] == Xq.shape[1] == 2
        classes, counts = np.unique(yc, return_counts=True)
        return classes, np.tile(counts / counts.sum(), (len(Xq), 1))


def fixture():
    return (pd.DataFrame({"x": [str(i) for i in range(60)],
                          "y": [str(i % 13) for i in range(60)],
                          "c": ["a" if i % 3 else "b" for i in range(60)]}),
            np.array(["entity" + str(i // 6) for i in range(60)]))


def test_all_training_stages_exclude_heldout_groups():
    dirty, groups = fixture()
    result = score_variants(dirty, list(dirty), groups, FakeModel(), 0)
    plans = context_plan(groups, StrictConfig(), 0)
    for record in result["log"].contexts:
        assert set(record["query_groups"]).isdisjoint(record["context_groups"])
        assert record["active_row_ids"] == record["preprocessing_row_ids"]
        assert set(record["query_row_ids"]).isdisjoint(record["typing_row_ids"])
        if record["stage"] == "pass1":
            heldout = plans[record["outer_fold"]][1]
            for key in ("query_row_ids", "active_row_ids", "preprocessing_row_ids", "typing_row_ids"):
                assert set(heldout).isdisjoint(record[key])


def test_heldout_mutation_cannot_change_trimming_or_fitted_encoder():
    dirty, groups = fixture()
    query = context_plan(groups, StrictConfig(), 4)[0][1]
    changed = dirty.copy()
    changed.iloc[query, 0] = "99999"
    changed.iloc[query, 2] = "heldout_only_value"
    original = score_variants(dirty, list(dirty), groups, FakeModel(), 4)
    mutated = score_variants(changed, list(changed), groups, FakeModel(), 4)
    def signatures(result):
        return [(r["arm"], r["column"], r["active_row_ids"], r["encoder_sha256"])
                for r in result["log"].contexts if r["stage"] == "final" and r["outer_fold"] == 0]
    assert signatures(original) == signatures(mutated)


def test_paired_removal_and_shared_compute_are_recorded():
    dirty, groups = fixture()
    result = score_variants(dirty, list(dirty), groups, FakeModel(), 1)
    final = [r for r in result["log"].contexts if r["stage"] == "final"]
    for f in range(5):
        for col in dirty:
            records = {r["arm"]: r for r in final if r["fold"] == f and r["column"] == col}
            assert records["raw"]["base_row_ids"] == records["random"]["base_row_ids"] == records["purify"]["base_row_ids"]
            assert len(records["random"]["active_row_ids"]) == len(records["purify"]["active_row_ids"])
    assert result["log"].model_calls["shared_pass1"] > 0
    assert set(result["log"].model_calls["incremental"]) == {"raw", "random", "purify"}
    assert result["log"].seconds["total"] >= result["log"].seconds["shared_pass1"]


def test_diagnostic_entry_is_explicit_and_dirty_api_has_no_clean_input():
    dirty, groups = fixture()
    raw = score_variants(dirty, list(dirty), groups, FakeModel(), 2, arms=("raw",))["scores"]["raw"]
    oracle, _ = score_diagnostic(dirty, list(dirty), groups, FakeModel(), 2, "oracle", clean=dirty.copy())
    assert np.allclose(raw, oracle)
    _, leaky = score_diagnostic(dirty, list(dirty), groups, FakeModel(), 2, "leaky")
    assert all(set(r["query_row_ids"]) & set(r["active_row_ids"]) for r in leaky.contexts)
    with pytest.raises(TypeError):
        score_variants(dirty, list(dirty), groups, FakeModel(), 2, clean=dirty)
    with pytest.raises(ValueError):
        score_diagnostic(dirty, list(dirty), groups, FakeModel(), 2, "raw")


def test_unsupported_columns_stay_in_output_universe():
    dirty, groups = fixture()
    dirty["c"] = ["unique" + str(i) for i in range(len(dirty))]
    result = score_variants(dirty, list(dirty), groups, FakeModel(), 2, arms=("raw",))
    assert result["scores"]["raw"].shape == dirty.shape
    assert not result["supported"][:, 2].any()
    assert (result["scores"]["raw"][:, 2] == 0).all()


def test_too_few_groups_fail_instead_of_silently_switching_to_rows():
    dirty, _ = fixture()
    with pytest.raises(ValueError, match="group"):
        score_variants(dirty, list(dirty), ["one"] * len(dirty), FakeModel(), 0)
