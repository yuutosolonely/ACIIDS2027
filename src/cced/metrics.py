"""Evaluation-only metrics. These are the only functions that read error masks."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score


def auprc(scores: np.ndarray, errors: np.ndarray) -> float:
    y = errors.ravel().astype(int)
    if y.sum() == 0:
        return float("nan")
    return float(average_precision_score(y, scores.ravel()))


def r_precision(scores: np.ndarray, errors: np.ndarray) -> float:
    """Precision (= recall = F1) when the audit budget equals the number of errors."""
    y = errors.ravel()
    k = int(y.sum())
    if k == 0:
        return float("nan")
    top = np.argsort(-scores.ravel(), kind="stable")[:k]
    return float(y[top].mean())


def precision_at(scores, errors, frac):
    y = errors.ravel()
    k = max(1, int(round(frac * y.size)))
    top = np.argsort(-scores.ravel(), kind="stable")[:k]
    return float(y[top].mean())


def rare_valid_alarm_rate(scores, errors, rare_mask, frac=None):
    """Share of rare-but-correct cells that fall inside the top-k audit budget.

    k defaults to the number of true errors. `rare_mask` marks cells whose *clean*
    value is rare in its column; it is computed by the harness from clean data.
    """
    y = errors.ravel()
    k = int(y.sum()) if frac is None else max(1, int(round(frac * y.size)))
    flagged = np.zeros(y.size, dtype=bool)
    flagged[np.argsort(-scores.ravel(), kind="stable")[:k]] = True
    rv = rare_mask.ravel() & ~y
    return float(flagged[rv].mean()) if rv.any() else float("nan")


def rare_valid_mask(clean_cols: np.ndarray, max_share: float = 0.01) -> np.ndarray:
    """Cells whose clean value occurs in at most `max_share` of rows (and not unique-ID-like)."""
    n, d = clean_cols.shape
    m = np.zeros((n, d), dtype=bool)
    for j in range(d):
        vals, inv, cnt = np.unique(clean_cols[:, j], return_inverse=True, return_counts=True)
        if len(vals) > 0.5 * n:  # near-unique columns: rarity is uninformative
            continue
        m[:, j] = (cnt[inv] / n) <= max_share
    return m


def bootstrap_rows(fn, scores_list, errors, reps=200, seed=0):
    """Row-cluster bootstrap: resample rows (all their cells together)."""
    rng = np.random.default_rng(seed)
    n = errors.shape[0]
    out = []
    for _ in range(reps):
        idx = rng.integers(0, n, n)
        out.append([fn(s[idx], errors[idx]) for s in scores_list])
    return np.array(out)


def summarize(scores, errors, rare_mask=None) -> dict:
    out = {
        "auprc": auprc(scores, errors),
        "r_precision": r_precision(scores, errors),
        "p_at_1pct": precision_at(scores, errors, 0.01),
        "p_at_5pct": precision_at(scores, errors, 0.05),
        "prevalence": float(errors.mean()),
    }
    if rare_mask is not None:
        out["rare_valid_alarm"] = rare_valid_alarm_rate(scores, errors, rare_mask)
    return out
