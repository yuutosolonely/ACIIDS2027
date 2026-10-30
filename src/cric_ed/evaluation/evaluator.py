"""Evaluation harness for cell error detection.

Strictly isolates ground-truth labels and computes cell-level AUPRC,
budgeted metrics, and cluster-preserving bootstrap confidence intervals.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple
from cric_ed.models import CellScore

def compute_average_precision(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Average Precision (AUPRC) with tied scores grouped into one threshold.

    Higher score indicates higher suspicion of error. Tie handling matches
    scikit-learn's `average_precision_score`, so input order cannot change the value.
    Returns NaN when there are no positives (AUPRC is undefined).
    """
    if len(scores) != len(labels) or not scores:
        return float("nan")

    positives = sum(labels)
    if positives == 0:
        return float("nan")

    by_score: Dict[float, List[int]] = {}
    for s, y in zip(scores, labels):
        tally = by_score.setdefault(s, [0, 0])
        tally[0] += 1
        tally[1] += y

    ap = 0.0
    cum_n = 0
    cum_tp = 0
    for s in sorted(by_score, reverse=True):
        n, tp = by_score[s]
        cum_n += n
        cum_tp += tp
        if tp:
            ap += (cum_tp / cum_n) * (tp / positives)
    return float(ap)


def apply_coverage_penalty(scores: List[float], failed: List[bool]) -> List[float]:
    """Preregistered rule: failed or non-finite cells receive max finite score + 1.0."""
    finite = [s for s, f in zip(scores, failed) if not f and math.isfinite(s)]
    penalty = (max(finite) if finite else 0.0) + 1.0
    return [penalty if (f or not math.isfinite(s)) else s for s, f in zip(scores, failed)]


def cluster_bootstrap_auprc_ci(
    scores_by_row: Dict[int, List[float]],
    labels_by_row: Dict[int, List[int]],
    entity_to_rows: Dict[str, List[int]],
    n_bootstraps: int = 1000,
    seed: int = 42
) -> Tuple[float, float, float]:
    """Mean and 95% percentile CI of AUPRC under an entity-cluster bootstrap.

    Replicates without any positive cell are discarded (AUPRC undefined there);
    `last_valid_replicates` records how many were kept.
    """
    rng = random.Random(seed)
    unique_entities = list(entity_to_rows.keys())
    n_entities = len(unique_entities)

    if n_entities < 2:
        # Fallback if too few clusters
        flat_s = [s for r in scores_by_row.values() for s in r]
        flat_l = [l for r in labels_by_row.values() for l in r]
        base_ap = compute_average_precision(flat_s, flat_l)
        return base_ap, base_ap, base_ap

    boot_aps = []

    for _ in range(n_bootstraps):
        sampled_entities = [rng.choice(unique_entities) for _ in range(n_entities)]
        boot_scores = []
        boot_labels = []

        for ent in sampled_entities:
            for r in entity_to_rows[ent]:
                boot_scores.extend(scores_by_row.get(r, []))
                boot_labels.extend(labels_by_row.get(r, []))

        ap = compute_average_precision(boot_scores, boot_labels)
        if not math.isnan(ap):
            boot_aps.append(ap)

    cluster_bootstrap_auprc_ci.last_valid_replicates = len(boot_aps)
    if not boot_aps:
        return float("nan"), float("nan"), float("nan")
    boot_aps.sort()
    lower_idx = int(0.025 * len(boot_aps))
    upper_idx = int(0.975 * len(boot_aps))
    mean_ap = sum(boot_aps) / len(boot_aps)

    return mean_ap, boot_aps[lower_idx], boot_aps[min(upper_idx, len(boot_aps) - 1)]

def paired_bootstrap_delta(
    scores_a: Dict[int, List[float]],
    scores_b: Dict[int, List[float]],
    labels_by_row: Dict[int, List[int]],
    entity_to_rows: Dict[str, List[int]],
    n_bootstraps: int = 1000,
    seed: int = 42
) -> Dict[str, Any]:
    """Entity-cluster bootstrap of AUPRC(a) - AUPRC(b) on the same resampled cells."""
    rng = random.Random(seed)
    ents = list(entity_to_rows.keys())

    def flat(sc, rows):
        return [x for r in rows for x in sc.get(r, [])]

    all_rows = [r for e in ents for r in entity_to_rows[e]]
    lab = flat(labels_by_row, all_rows)
    point = (compute_average_precision(flat(scores_a, all_rows), lab)
             - compute_average_precision(flat(scores_b, all_rows), lab))
    deltas = []
    for _ in range(n_bootstraps):
        rows = [r for e in (rng.choice(ents) for _ in ents) for r in entity_to_rows[e]]
        lab = flat(labels_by_row, rows)
        d = (compute_average_precision(flat(scores_a, rows), lab)
             - compute_average_precision(flat(scores_b, rows), lab))
        if not math.isnan(d):
            deltas.append(d)
    deltas.sort()
    lo = deltas[int(0.025 * len(deltas))]
    hi = deltas[min(int(0.975 * len(deltas)), len(deltas) - 1)]
    return {"delta": round(point, 4), "ci95": [round(lo, 4), round(hi, 4)], "valid_replicates": len(deltas)}


def evaluate_cell_scores(
    cell_scores: List[CellScore],
    ground_truth_errors: List[List[int]],
    entity_ids: List[str],
    numeric_col_indices: Sequence[int],
    rare_valid_mask: Optional[List[List[bool]]] = None,
    n_bootstraps: int = 1000
) -> Dict[str, Any]:
    """Evaluate full cell predictions against isolated ground truth."""
    eligible = [cs for cs in cell_scores if cs.is_eligible]
    penalised = apply_coverage_penalty([cs.score for cs in eligible],
                                       [bool(cs.failure_status) for cs in eligible])
    eligible_scores: List[float] = []
    eligible_labels: List[int] = []

    num_scores: List[float] = []
    num_labels: List[int] = []

    cat_scores: List[float] = []
    cat_labels: List[int] = []

    scores_by_row: Dict[int, List[float]] = {}
    labels_by_row: Dict[int, List[int]] = {}
    entity_to_rows: Dict[str, List[int]] = {}

    for r, ent in enumerate(entity_ids):
        entity_to_rows.setdefault(ent, []).append(r)
        scores_by_row[r] = []
        labels_by_row[r] = []

    rare_valid_positions: List[int] = []

    for cs, score in zip(eligible, penalised):
        true_label = ground_truth_errors[cs.row_idx][cs.col_idx]

        eligible_scores.append(score)
        eligible_labels.append(true_label)

        scores_by_row[cs.row_idx].append(score)
        labels_by_row[cs.row_idx].append(true_label)

        if cs.col_idx in numeric_col_indices:
            num_scores.append(score)
            num_labels.append(true_label)
        else:
            cat_scores.append(score)
            cat_labels.append(true_label)

        if rare_valid_mask and rare_valid_mask[cs.row_idx][cs.col_idx]:
            rare_valid_positions.append(len(eligible_scores) - 1)

    # 1. Primary AUPRC
    overall_auprc = compute_average_precision(eligible_scores, eligible_labels)
    numeric_auprc = compute_average_precision(num_scores, num_labels)
    categorical_auprc = compute_average_precision(cat_scores, cat_labels)

    # 2. Cluster Bootstrap CI
    mean_ap, ci_lower, ci_upper = cluster_bootstrap_auprc_ci(
        scores_by_row, labels_by_row, entity_to_rows, n_bootstraps=n_bootstraps
    )
    valid_replicates = cluster_bootstrap_auprc_ci.last_valid_replicates

    # 3. Budgeted Metrics (k = 1%, 5%, 10% of eligible cells)
    total_eligible = len(eligible_scores)
    budgets = {
        "k_01": max(int(0.01 * total_eligible), 1),
        "k_05": max(int(0.05 * total_eligible), 1),
        "k_10": max(int(0.10 * total_eligible), 1)
    }

    budgeted_results = {}
    positives = sum(eligible_labels)
    # Deterministic budget ranking: score descending, then cell order.
    sorted_idx = sorted(range(total_eligible), key=lambda i: (-eligible_scores[i], i))

    for b_key, b_size in budgets.items():
        top_k = sorted_idx[:b_size]
        tp = sum(eligible_labels[i] for i in top_k)
        prec = tp / b_size if b_size else 0.0
        rec = tp / positives if positives else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        budgeted_results[b_key] = {
            "budget": b_size,
            "true_positives": tp,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4)
        }

    # 4. Rare-valid false positive alarm rate (fraction of rare-valid cells in top 5% audit budget)
    # Membership in the exact top-k set, so ties at the boundary cannot enlarge the budget.
    rare_valid_fpr = 0.0
    if rare_valid_positions and total_eligible > 0:
        top5 = set(sorted_idx[:budgets["k_05"]])
        rare_valid_fpr = sum(1 for i in rare_valid_positions if i in top5) / len(rare_valid_positions)

    return {
        "eligible_cells": total_eligible,
        "true_error_positives": positives,
        "overall_auprc": round(overall_auprc, 4),
        "numeric_auprc": round(numeric_auprc, 4),
        "categorical_auprc": round(categorical_auprc, 4),
        "auprc_95_ci": [round(ci_lower, 4), round(ci_upper, 4)],
        "bootstrap": {"unit": "entity", "requested": n_bootstraps, "valid_replicates": valid_replicates},
        "failed_cells_penalised": sum(1 for cs in eligible if cs.failure_status),
        "budgeted_metrics": budgeted_results,
        "rare_valid_fpr_at_k05": round(rare_valid_fpr, 4)
    }
