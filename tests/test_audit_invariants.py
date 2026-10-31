"""Software-only invariants added by the 2026-10-30 audit (not research evidence).

They check determinism, paired context construction across trimming arms, the
leave-entity-out context boundary and that detectors never read label files.
"""

import shutil
from pathlib import Path

import pytest

from cric_ed.detectors.baseline_classical import RobustCoordinateDevianceDetector
from cric_ed.detectors.cric_scorer import CRICDetector
from cric_ed.loader import load_dirty_benchmark_table

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "toy_mixed"
NUMERIC = {"feature_a", "feature_b", "num_target"}


def _table(path=FIXTURE / "dirty.csv"):
    return load_dirty_benchmark_table(path, entity_col="entity_id", numeric_cols=NUMERIC,
                                      primary_key_cols={"entity_id"})


@pytest.mark.parametrize("mode", ["none", "matched_random", "influence"])
def test_repeated_scoring_is_deterministic(mode):
    det = CRICDetector(context_size=30, trimming_mode=mode, seed=42)
    table = _table()
    first = [c.score for c in det.score_table(table)]
    second = [c.score for c in det.score_table(table)]
    assert first == second


def test_trimming_arms_share_base_contexts():
    table = _table()
    logs = {}
    for mode in ("none", "matched_random", "influence"):
        det = CRICDetector(context_size=30, trimming_mode=mode, seed=42)
        det.context_log = []
        det.score_table(table)
        logs[mode] = [(q, j, base) for q, j, base, _ in det.context_log]
    assert logs["none"] == logs["matched_random"] == logs["influence"]
    assert len(logs["none"]) == 400


def test_context_excludes_query_entity():
    table = _table()
    det = CRICDetector(context_size=30, trimming_mode="influence", seed=7)
    det.context_log = []
    det.score_table(table)
    for q, _, base, active in det.context_log:
        assert q not in base
        assert all(table.entity_ids[c] != table.entity_ids[q] for c in base)
        assert set(active) <= set(base)


def test_detectors_do_not_read_label_files(tmp_path):
    """Scores from a directory holding only dirty.csv equal scores next to clean/errors files."""
    shutil.copy(FIXTURE / "dirty.csv", tmp_path / "dirty.csv")
    isolated, original = _table(tmp_path / "dirty.csv"), _table()
    for det in (CRICDetector(seed=3), RobustCoordinateDevianceDetector()):
        a = [c.score for c in det.score_table(original)]
        b = [c.score for c in det.score_table(isolated)]
        assert a == b
