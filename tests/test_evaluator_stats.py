"""Software-only checks for evaluator statistics fixed on 2026-10-30."""

import math
import random

from cric_ed.evaluation.evaluator import apply_coverage_penalty, compute_average_precision, evaluate_cell_scores
from cric_ed.models import CellScore


def test_average_precision_ignores_order_within_ties():
    scores = [3.0, 2.0, 2.0, 2.0, 1.0, 1.0]
    labels = [1, 0, 1, 0, 1, 0]
    ref = compute_average_precision(scores, labels)
    rng = random.Random(0)
    for _ in range(20):
        idx = list(range(len(scores)))
        rng.shuffle(idx)
        assert math.isclose(compute_average_precision([scores[i] for i in idx], [labels[i] for i in idx]), ref)
    # Hand value (scikit-learn convention): 1/3 * (1 + 2/4 + 3/6)
    assert math.isclose(ref, (1 + 0.5 + 0.5) / 3)


def test_average_precision_undefined_without_positives():
    assert math.isnan(compute_average_precision([1.0, 2.0], [0, 0]))


def test_coverage_penalty_puts_failures_on_top():
    out = apply_coverage_penalty([0.5, float("nan"), 2.0, 1.0], [False, False, False, True])
    assert out == [0.5, 3.0, 2.0, 3.0]


def test_rare_valid_budget_is_exact_under_ties():
    # 20 cells, all tied: top 5% = 1 cell, so at most one of the rare cells can be flagged.
    cells = [CellScore(row_idx=r, col_idx=1, col_name="c", raw_value="v", score=1.0) for r in range(20)]
    gt = [[0, 1 if r == 0 else 0] for r in range(20)]
    rare = [[False, r >= 10] for r in range(20)]
    m = evaluate_cell_scores(cells, gt, [f"e{r}" for r in range(20)], [], rare_valid_mask=rare, n_bootstraps=50)
    assert m["rare_valid_fpr_at_k05"] == 0.0
